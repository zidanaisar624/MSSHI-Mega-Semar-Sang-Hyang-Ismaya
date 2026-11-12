"""MSSHI TimesFM 2.5: explicit isolated CPU setup and offline, bounded forecasts."""
from __future__ import annotations
import argparse
import ctypes
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import venv

sys.dont_write_bytecode = True
SOURCE_COMMIT = "e51928e27119cb17bebc005be2696b75e0a9e688"
MODEL_ID = "google/timesfm-2.5-200m-pytorch"
MODEL_REVISION = "1d952420fba87f3c6dee4f240de0f1a0fbc790e3"
WEIGHTS_SHA256 = "2f776efe6245e42b24bc4153ffdf61810140210e4bd3b01fb21f7aa779ab6ce8"
WEIGHTS_BYTES = 925181104
TORCH = "2.8.0+cpu"

def root_home(value=None):
    p = Path(value or os.environ.get("MSSHI_HERMES_HOME") or os.environ.get("HERMES_HOME") or ("D:/HermesData" if os.name == "nt" and Path("D:/HermesData").exists() else Path.home()/".hermes")).expanduser().absolute()
    return p.parent.parent if p.parent.name.lower() == "profiles" else p

def checked(p):
    p = Path(os.path.abspath(p))
    for q in (p, *p.parents):
        if q.exists() and (q.is_symlink() or getattr(q.lstat(), "st_file_attributes", 0) & 0x400):
            raise ValueError(f"Refusing symlink/junction destination: {q}")
    return p

def digest(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""): h.update(block)
    return h.hexdigest()

def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))

def acquire_lock(path):
    """Recover a lock after shutdown only when its recorded process is gone."""
    path=checked(path)
    try: return os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError:
        before=path.read_bytes()
        try: pid=int(before.decode("ascii"))
        except (ValueError,UnicodeError): raise ValueError(f"Unverifiable lock; inspect manually: {path}")
        if pid<=0: raise ValueError("Invalid lock owner")
        if os.name=="nt":
            import ctypes
            kernel=ctypes.WinDLL("kernel32",use_last_error=True)
            kernel.OpenProcess.restype=ctypes.c_void_p
            handle=kernel.OpenProcess(0x1000,False,pid)
            if handle:
                kernel.CloseHandle(ctypes.c_void_p(handle))
                raise ValueError(f"TimesFM process {pid} is still active")
            if ctypes.get_last_error()!=87: raise ValueError(f"Cannot verify lock owner {pid}")
        else:
            try: os.kill(pid,0)
            except ProcessLookupError: pass
            else: raise ValueError(f"TimesFM process {pid} is still active")
        if path.read_bytes()!=before: raise ValueError("Lock changed during recovery")
        path.unlink()
        return os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY)

def encode(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+"\n").encode()

def write_new(p, obj):
    p=checked(p); p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("xb") as stream: stream.write(encode(obj))

def atomic(p, obj):
    p=checked(p); p.parent.mkdir(parents=True, exist_ok=True)
    fd, name=tempfile.mkstemp(dir=p.parent, prefix=".timesfm-")
    try:
        with os.fdopen(fd,"wb") as stream: stream.write(encode(obj))
        os.replace(name,p)
    finally:
        Path(name).unlink(missing_ok=True)

def paths(home):
    folder=checked(home/"msshi-private"/"timesfm-runtime")
    python=folder/"venv"/("Scripts/python.exe" if os.name=="nt" else "bin/python")
    return folder, python

def environment(folder, offline=True):
    env=os.environ.copy()
    for key in ("PYTHONHOME","PYTHONPATH","PIP_TARGET","PIP_PREFIX","PIP_USER"):
        env.pop(key,None)
    env.update(PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1", CUDA_VISIBLE_DEVICES="", OMP_NUM_THREADS="2", MKL_NUM_THREADS="2", HF_HUB_DISABLE_TELEMETRY="1", HF_HUB_DISABLE_XET="1", HF_HOME=str(folder/"hf-cache"))
    if offline: env.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
    else: env.pop("HF_HUB_OFFLINE",None)
    return env

def owned_run(command, env, timeout):
    """Own the entire worker tree, including Windows venv redirector children."""
    process=None; handle=None; kernel=None
    if os.name=="nt":
        from ctypes import wintypes
        class Basic(ctypes.Structure):
            _fields_=[("process_time",ctypes.c_int64),("job_time",ctypes.c_int64),("flags",wintypes.DWORD),("min_ws",ctypes.c_size_t),("max_ws",ctypes.c_size_t),("active_limit",wintypes.DWORD),("affinity",ctypes.c_size_t),("priority",wintypes.DWORD),("scheduling",wintypes.DWORD)]
        class Counters(ctypes.Structure):
            _fields_=[(str(i),ctypes.c_ulonglong) for i in range(6)]
        class Extended(ctypes.Structure):
            _fields_=[("basic",Basic),("io",Counters),("process_mem",ctypes.c_size_t),("job_mem",ctypes.c_size_t),("peak_process",ctypes.c_size_t),("peak_job",ctypes.c_size_t)]
        kernel=ctypes.WinDLL("kernel32",use_last_error=True)
        kernel.CreateJobObjectW.restype=wintypes.HANDLE
        kernel.CreateJobObjectW.argtypes=[ctypes.c_void_p,wintypes.LPCWSTR]
        kernel.SetInformationJobObject.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD]
        kernel.AssignProcessToJobObject.argtypes=[wintypes.HANDLE,wintypes.HANDLE]
        kernel.CloseHandle.argtypes=[wintypes.HANDLE]
        handle=kernel.CreateJobObjectW(None,None)
        info=Extended(); info.basic.flags=0x2000
        if not handle or not kernel.SetInformationJobObject(handle,9,ctypes.byref(info),ctypes.sizeof(info)):
            if handle: kernel.CloseHandle(handle)
            raise OSError("Cannot establish TimesFM child-process ownership")
    try:
        process=subprocess.Popen(command,env=env,start_new_session=os.name!="nt",creationflags=0x08000004 if os.name=="nt" else 0)
        if handle:
            if not kernel.AssignProcessToJobObject(handle,process._handle): raise OSError("Cannot assign TimesFM worker to job")
            resume=ctypes.WinDLL("ntdll").NtResumeProcess
            resume.argtypes=[ctypes.c_void_p]; resume.restype=ctypes.c_long
            if resume(process._handle): raise OSError("Cannot resume owned TimesFM worker")
        result=process.wait(timeout=timeout)
        if result: raise subprocess.CalledProcessError(result,command)
    finally:
        if handle: kernel.CloseHandle(handle)
        elif process is not None and os.name!="nt":
            import signal
            try: os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError: pass
        if process is not None and process.poll() is None:
            process.kill(); process.wait(timeout=10)

def memory_budget():
    if os.name!="nt": return {"checked":False,"reason":"Windows commit preflight is not available on this platform"}
    from ctypes import wintypes
    class Memory(ctypes.Structure):
        _fields_=[("length",wintypes.DWORD),("load",wintypes.DWORD),*[(key,ctypes.c_ulonglong) for key in ("total_phys","avail_phys","total_commit","avail_commit","total_virtual","avail_virtual","avail_extended")]]
    info=Memory(); info.length=ctypes.sizeof(info)
    if not ctypes.WinDLL("kernel32",use_last_error=True).GlobalMemoryStatusEx(ctypes.byref(info)): raise OSError("Cannot check available memory")
    if info.avail_commit<2560*1024*1024: raise ValueError("TimesFM requires at least 2.5 GiB available system commit before model loading; close unused applications and retry")
    return {"checked":True,"available_physical_bytes":info.avail_phys,"available_commit_bytes":info.avail_commit,"note":"Preflight only; not a hard memory quota. Windows may page when physical memory is low."}

def status(home, verify=False):
    folder,python=paths(home); marker=folder/"INSTALLATION.json"
    state=read(marker) if marker.is_file() else {}
    model=folder/"model"/"model.safetensors"
    matching=state.get("source_commit")==SOURCE_COMMIT and state.get("model_revision")==MODEL_REVISION and state.get("weights_sha256")==WEIGHTS_SHA256
    ready=python.is_file() and model.is_file() and model.stat().st_size==WEIGHTS_BYTES and matching
    if verify and ready: ready=digest(model)==WEIGHTS_SHA256
    return {"ready":ready,"runtime":str(folder),"python":str(python),"model_id":MODEL_ID,"model_revision":MODEL_REVISION,"source_commit":SOURCE_COMMIT,"offline_forecast":True,"device":"cpu","starts_on_boot":False,"model_weights_license":"Apache-2.0","api_credits_used":0,"weights_hash_verified_now":bool(verify and ready),"last_test":state.get("last_test")}

def install(home):
    folder,python=paths(home); folder.mkdir(parents=True,exist_ok=True)
    identity=folder/"OWNER.json"
    expected={"owner":"MSSHI TimesFM isolated runtime","schema":1}
    if identity.exists():
        if read(identity)!=expected: raise ValueError("Runtime ownership mismatch")
    elif any(folder.iterdir()): raise ValueError("Existing unowned runtime; refusing to modify")
    else: atomic(identity,expected)
    existing=status(home,True)
    if existing["ready"]: return existing
    lock=folder/"install.lock"
    fd=acquire_lock(lock)
    try:
        os.write(fd,str(os.getpid()).encode()); os.close(fd)
        if not python.exists(): venv.EnvBuilder(with_pip=True).create(folder/"venv")
        env=environment(folder,False)
        owned_run([str(python),"-m","pip","install","--disable-pip-version-check",f"torch=={TORCH}","--index-url","https://download.pytorch.org/whl/cpu"],env,1200)
        owned_run([str(python),"-m","pip","install","--disable-pip-version-check",f"https://github.com/google-research/timesfm/archive/{SOURCE_COMMIT}.zip"],env,600)
        owned_run([str(python),str(Path(__file__).resolve()),"--hermes-home",str(home),"_download"],env,1200)
        model=folder/"model"/"model.safetensors"
        if model.stat().st_size!=WEIGHTS_BYTES or digest(model)!=WEIGHTS_SHA256: raise ValueError("TimesFM model checksum mismatch")
        freeze=subprocess.run([str(python),"-m","pip","freeze"],capture_output=True,text=True,env=env,check=True).stdout
        atomic(folder/"INSTALLATION.json",{"schema":1,"source_commit":SOURCE_COMMIT,"model_id":MODEL_ID,"model_revision":MODEL_REVISION,"weights_sha256":WEIGHTS_SHA256,"weights_bytes":WEIGHTS_BYTES,"torch":TORCH,"installed_utc":datetime.now(timezone.utc).isoformat(),"packages":freeze.splitlines(),"license":"Apache-2.0","last_test":None})
    finally: lock.unlink(missing_ok=True)
    return status(home,True)

def download(home):
    from huggingface_hub import hf_hub_download
    folder,_=paths(home); dest=folder/"model"; dest.mkdir(exist_ok=True)
    for name in ("config.json","README.md","model.safetensors"):
        hf_hub_download(MODEL_ID,name,revision=MODEL_REVISION,local_dir=dest,token=False)

def data_from_input(p):
    p=Path(p)
    if p.stat().st_size>1024*1024: raise ValueError("Input JSON exceeds 1 MiB")
    obj=read(p)
    series=obj.get("series") if isinstance(obj,dict) else obj
    if not isinstance(series,list) or not 1<=len(series)<=4: raise ValueError("Expected 1 to 4 series in {series:[[numbers], ...]}")
    for values in series:
        if not isinstance(values,list) or not 32<=len(values)<=1024: raise ValueError("Each series must contain 32..1024 equally spaced observations")
        if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or abs(v)>1e20 for v in values): raise ValueError("Only finite numeric observations with abs(value)<=1e20 are accepted")
    return series

def worker(home, args):
    import numpy as np
    import torch
    import timesfm
    folder,_=paths(home)
    torch.set_num_threads(2); torch.set_num_interop_threads(1)
    inputs=data_from_input(args.input)
    memory=memory_budget()
    begin=time.monotonic()
    model=timesfm.TimesFM_2p5_200M_torch(torch_compile=False)
    model.load_checkpoint(str(folder/"model"/"model.safetensors"),torch_compile=False)
    context=int(math.ceil(max(map(len,inputs))/32)*32)
    model.compile(timesfm.ForecastConfig(max_context=context,max_horizon=128,per_core_batch_size=1,normalize_inputs=True,use_continuous_quantile_head=True,force_flip_invariance=False,infer_is_positive=False,fix_quantile_crossing=True))
    point,quantiles=model.forecast(horizon=args.horizon,inputs=[np.asarray(values,dtype=np.float32) for values in inputs])
    if not np.isfinite(point).all() or not np.isfinite(quantiles).all(): raise ValueError("Model returned non-finite output")
    result={"model_id":MODEL_ID,"model_revision":MODEL_REVISION,"source_commit":SOURCE_COMMIT,"device":"cpu","horizon":args.horizon,"input_lengths":list(map(len,inputs)),"point_forecast":point.tolist(),"quantiles":quantiles.tolist(),"quantile_channels":["mean","p10","p20","p30","p40","p50","p60","p70","p80","p90"],"elapsed_seconds":round(time.monotonic()-begin,3),"memory_preflight":memory,"api_credits_used":0,"limitations":"Experimental forecast; validate with chronological holdout and naive/seasonal baselines. Not a guarantee or financial advice."}
    write_new(args.output,result)

def forecast(home,args):
    state=status(home)
    if not state["ready"]: raise ValueError("TimesFM runtime not ready; run install explicitly first")
    data_from_input(args.input)
    output=checked(args.output)
    if output.exists(): raise FileExistsError(f"Output already exists: {output}")
    folder,python=paths(home); lock=folder/"forecast.lock"
    fd=acquire_lock(lock)
    try:
        os.write(fd,str(os.getpid()).encode()); os.close(fd)
        owned_run([str(python),str(Path(__file__).resolve()),"--hermes-home",str(home),"_worker","--input",str(Path(args.input).absolute()),"--output",str(output),"--horizon",str(args.horizon)],environment(folder),300)
    finally: lock.unlink(missing_ok=True)
    return {"success":True,"output":str(output),"model_id":MODEL_ID,"api_credits_used":0}

def smoke(home):
    folder,_=paths(home); proof=folder/"verification"; proof.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    inp=proof/f"synthetic-{stamp}.json"; out=proof/f"forecast-{stamp}.json"
    values=[10+0.02*i+math.sin(i*2*math.pi/12) for i in range(64)]
    write_new(inp,{"series":[values]})
    args=argparse.Namespace(input=str(inp),output=str(out),horizon=4)
    forecast(home,args); data=read(out)
    good=len(data["point_forecast"])==1 and len(data["point_forecast"][0])==4 and len(data["quantiles"][0])==4
    audit={"success":good,"input":str(inp),"output":str(out),"input_sha256":digest(inp),"output_sha256":digest(out),"elapsed_seconds":data["elapsed_seconds"],"synthetic_only":True,"api_credits_used":0,"tested_utc":datetime.now(timezone.utc).isoformat()}
    state=read(folder/"INSTALLATION.json"); state["last_test"]=audit; atomic(folder/"INSTALLATION.json",state)
    atomic(home/"msshi-private"/"v3-timesfm-audit.json",audit)
    return audit

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hermes-home")
    subs=parser.add_subparsers(dest="action",required=True)
    p=subs.add_parser("status"); p.add_argument("--verify",action="store_true")
    subs.add_parser("install"); subs.add_parser("smoke"); subs.add_parser("_download")
    for action in ("forecast","_worker"):
        p=subs.add_parser(action); p.add_argument("--input",required=True); p.add_argument("--output",required=True); p.add_argument("--horizon",type=int,default=12,choices=range(1,129),metavar="1..128")
    args=parser.parse_args(argv); home=root_home(args.hermes_home)
    if args.action=="status": result=status(home,args.verify)
    elif args.action=="install": result=install(home)
    elif args.action=="smoke": result=smoke(home)
    elif args.action=="forecast": result=forecast(home,args)
    elif args.action=="_download": download(home); return 0
    else: worker(home,args); return 0
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0

if __name__=="__main__":
    try: raise SystemExit(main())
    except (ValueError,OSError,subprocess.SubprocessError) as exc:
        print(f"TimesFM error: {exc}",file=sys.stderr); raise SystemExit(1)
