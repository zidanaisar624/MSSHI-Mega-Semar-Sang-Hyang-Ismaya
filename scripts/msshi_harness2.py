#!/usr/bin/env python3
"""MSSHI Harness²: isolated core installation, deterministic demo, and review-only plans."""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

SOURCE_COMMIT = "6868817518876de8fd170c6a8354daca273b6191"
LICENSE_SHA256 = "3ddf9be5c28fe27dad143a5dc76eea25222ad1dd68934a047064e56ed2fa40c5"
UPSTREAM = "https://github.com/google-research/harness2"
OWNER = {"owner": "MSSHI Harness2 isolated demo runtime", "schema": 1}
COMPONENTS = ("system prompt", "guardrails", "memory", "tool guidance", "subagents", "skills", "scripts", "plugins")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def atomic(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def root_home(value=None):
    default = Path("D:/HermesData") if os.name == "nt" and Path("D:/HermesData").is_dir() else Path.home() / ".hermes"
    home = Path(value or os.environ.get("MSSHI_HERMES_HOME") or os.environ.get("HERMES_HOME") or default).expanduser().absolute()
    if home.parent.name.lower() == "profiles":
        home = home.parent.parent
    if any(p.lower() in {"profiles", "configs", ".git"} for p in home.parts):
        raise ValueError("The shared runtime must stay outside profile and config directories")
    if any((p / ".git").exists() for p in (home, *home.parents)):
        raise ValueError("The private runtime must stay outside source repositories")
    no_links(home)
    return home.resolve()


def paths(home):
    folder = Path(home) / "msshi-private" / "harness2-runtime"
    python = folder / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    return folder, python


def no_links(path):
    for part in (Path(path), *Path(path).parents):
        if part.exists() and (part.is_symlink() or getattr(part.lstat(), "st_file_attributes", 0) & 0x400):
            raise ValueError(f"Symlink/junction path is not allowed: {part}")


def environment(folder, output=None, *, install=False):
    """Allowlist; never inherit keys, cloud sessions, proxies, or user agent homes."""
    system = Path(os.environ.get("SYSTEMROOT", r"C:\Windows"))
    child_home = Path(folder) / "child-home"
    temporary = Path(folder) / "tmp"
    env = {
        "PATH": str(Path(folder) / "venv" / ("Scripts" if os.name == "nt" else "bin")) + os.pathsep + (str(system / "System32") if os.name == "nt" else "/usr/bin:/bin"),
        "HOME": str(child_home), "USERPROFILE": str(child_home),
        "APPDATA": str(child_home / "AppData" / "Roaming"),
        "LOCALAPPDATA": str(child_home / "AppData" / "Local"),
        "TEMP": str(temporary), "TMP": str(temporary), "TMPDIR": str(temporary),
        "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1", "PYTHONHASHSEED": "0",
        "PIP_CONFIG_FILE": os.devnull, "PIP_DISABLE_PIP_VERSION_CHECK": "1", "PIP_NO_INPUT": "1",
        "PIP_CACHE_DIR": str(Path(folder) / "pip-cache"),
    }
    if os.name == "nt":
        env.update(SYSTEMROOT=str(system), WINDIR=str(system), COMSPEC=str(system / "System32" / "cmd.exe"))
    if install:
        env["PIP_INDEX_URL"] = "https://pypi.org/simple"
    if output is not None:
        env["HARNESS2_RUNS_DIR"] = str(Path(output) / "runs")
    return env


def owned_run(command, env, timeout, *, cwd=None, stdout=None, stderr=None):
    """Own descendants, including venv redirectors. Adapted from MSSHI's MIT TimesFM helper."""
    process = handle = kernel = None
    if os.name == "nt":
        from ctypes import wintypes
        class Basic(ctypes.Structure):
            _fields_ = [("process_time", ctypes.c_int64), ("job_time", ctypes.c_int64), ("flags", wintypes.DWORD), ("min_ws", ctypes.c_size_t), ("max_ws", ctypes.c_size_t), ("active_limit", wintypes.DWORD), ("affinity", ctypes.c_size_t), ("priority", wintypes.DWORD), ("scheduling", wintypes.DWORD)]
        class Counters(ctypes.Structure):
            _fields_ = [(str(i), ctypes.c_ulonglong) for i in range(6)]
        class Extended(ctypes.Structure):
            _fields_ = [("basic", Basic), ("io", Counters), ("process_mem", ctypes.c_size_t), ("job_mem", ctypes.c_size_t), ("peak_process", ctypes.c_size_t), ("peak_job", ctypes.c_size_t)]
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CreateJobObjectW.restype = wintypes.HANDLE
        kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.CreateJobObjectW(None, None)
        info = Extended()
        info.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not handle or not kernel.SetInformationJobObject(handle, 9, ctypes.byref(info), ctypes.sizeof(info)):
            if handle:
                kernel.CloseHandle(handle)
            raise OSError("Cannot establish Harness2 child-process ownership")
    try:
        process = subprocess.Popen(command, env=env, cwd=cwd, stdout=stdout, stderr=stderr, stdin=subprocess.DEVNULL, start_new_session=os.name != "nt", creationflags=0x08000004 if os.name == "nt" else 0)
        if handle:
            if not kernel.AssignProcessToJobObject(handle, process._handle):
                raise OSError("Cannot assign Harness2 worker to job")
            resume = ctypes.WinDLL("ntdll").NtResumeProcess
            resume.argtypes = [ctypes.c_void_p]
            resume.restype = ctypes.c_long
            if resume(process._handle):
                raise OSError("Cannot resume owned Harness2 worker")
        code = process.wait(timeout=timeout)
        if code:
            raise subprocess.CalledProcessError(code, command)
    finally:
        if handle:
            kernel.CloseHandle(handle)
        elif process is not None and os.name != "nt":
            import signal
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if process is not None and process.poll() is None:
            process.kill()
            process.wait(timeout=10)


def capture(command, env, folder, timeout=60):
    with tempfile.TemporaryFile(dir=Path(folder) / "tmp") as log:
        owned_run(command, env, timeout, cwd=folder, stdout=log, stderr=subprocess.STDOUT)
        log.seek(0)
        return log.read().decode("utf-8").strip()


def package_files(folder):
    if os.name == "nt":
        return Path(folder) / "venv" / "Lib" / "site-packages" / "harness2"
    return Path(folder) / "venv" / "lib" / "python3.12" / "site-packages" / "harness2"


def inventory(folder):
    return [{"path": p.relative_to(folder).as_posix(), "bytes": p.stat().st_size, "sha256": digest(p)} for p in sorted(Path(folder).rglob("*")) if p.is_file() and "__pycache__" not in p.parts]


def status(home, verify=False):
    folder, python = paths(home)
    no_links(folder)
    marker = folder / "INSTALLATION.json"
    state = read(marker) if marker.is_file() else {}
    files = state.get("package_files", [])
    ready = python.is_file() and (folder / "OWNER.json").is_file() and read(folder / "OWNER.json") == OWNER and state.get("source_commit") == SOURCE_COMMIT and state.get("license_sha256") == LICENSE_SHA256 and bool(files)
    if ready:
        for item in files:
            relative = Path(item["path"])
            if relative.anchor or ".." in relative.parts:
                raise ValueError("Invalid installed manifest path")
            p = package_files(folder) / relative
            no_links(p)
            if not p.is_file() or p.stat().st_size != item["bytes"] or (verify and digest(p) != item["sha256"]):
                ready = False
                break
    return {"ready": ready, "scope": "deterministic local demo only", "runtime": str(folder), "python": str(python), "source_commit": SOURCE_COMMIT, "license": "Apache-2.0", "package_hashes_verified_now": bool(ready and verify), "benchmarks_enabled": False, "auto_promotion": False, "new_model_or_api_dependencies": False, "last_demo": state.get("last_demo")}


def install(home, source=None):
    if sys.version_info[:2] != (3, 12):
        raise ValueError("Run the installer with Python 3.12")
    folder, python = paths(home)
    no_links(folder)
    folder.mkdir(parents=True, exist_ok=True)
    identity = folder / "OWNER.json"
    if identity.is_file():
        if read(identity) != OWNER:
            raise ValueError("Runtime ownership mismatch")
    elif any(folder.iterdir()):
        raise ValueError("Existing unowned runtime; refusing to modify it")
    else:
        atomic(identity, OWNER)
    if status(home, True)["ready"]:
        return status(home, True)
    for name in ("tmp", "child-home"):
        (folder / name).mkdir(exist_ok=True)
    env = environment(folder, install=True)
    source = Path(source or Path(home) / "msshi-private" / "v3.1-sources" / "harness2").expanduser().resolve()
    no_links(source)
    if not (source / "pyproject.toml").is_file():
        raise ValueError("Supply --source pointing to the reviewed pinned Harness2 checkout")
    git = shutil.which("git")
    if not git:
        raise ValueError("git is required to verify and snapshot the pinned source")
    command = [git, "-c", "core.fsmonitor=false", "-C", str(source)]
    if capture(command + ["rev-parse", "HEAD"], env, folder) != SOURCE_COMMIT:
        raise ValueError("Harness2 source commit mismatch")
    # Build only committed bytes, never ignored credentials or local setup.py additions.
    lock = folder / "install.lock"
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.close(descriptor)
    try:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        archive = folder / f"source-{stamp}.zip"
        with archive.open("xb") as output:
            owned_run(command + ["archive", "--format=zip", SOURCE_COMMIT], env, 60, cwd=folder, stdout=output)
        build = folder / f"build-{stamp}"
        build.mkdir()
        with zipfile.ZipFile(archive) as zipped:
            for member in zipped.infolist():
                relative = Path(member.filename)
                if relative.is_absolute() or ".." in relative.parts or stat.S_ISLNK(member.external_attr >> 16):
                    raise ValueError("Unsafe path in pinned source archive")
            zipped.extractall(build)
        # The upstream clone may use CRLF; the archive preserves canonical Git bytes.
        if digest(build / "LICENSE") != LICENSE_SHA256:
            raise ValueError("Canonical upstream license hash mismatch")
        if not python.is_file():
            owned_run([sys.executable, "-I", "-B", "-m", "venv", str(folder / "venv")], env, 120, cwd=folder)
        owned_run([str(python), "-I", "-B", "-m", "pip", "install", "--only-binary=:all:", "--disable-pip-version-check", "--index-url", "https://pypi.org/simple", "setuptools==80.9.0", "wheel==0.45.1"], env, 300, cwd=folder)
        owned_run([str(python), "-I", "-B", "-m", "pip", "install", "--no-deps", "--no-build-isolation", "--no-compile", "--disable-pip-version-check", str(build)], env, 300, cwd=folder)
        packages = json.loads(capture([str(python), "-I", "-B", "-c", "import importlib.metadata as m,json,sys; print(json.dumps({'python':sys.version,'packages':{d.metadata['Name']:d.version for d in m.distributions()}}))"], env, folder))
        atomic(folder / "INSTALLATION.json", {"schema": 1, "source_url": UPSTREAM, "source_commit": SOURCE_COMMIT, "source_checkout": str(source), "source_archive": str(archive), "source_archive_sha256": digest(archive), "license": "Apache-2.0", "license_sha256": LICENSE_SHA256, "installed_utc": datetime.now(timezone.utc).isoformat(), "runtime": packages, "package_files": inventory(package_files(folder)), "last_demo": None, "limitations": "Upstream targets Linux. Only the deterministic demo is adapted for Windows; no model-backed benchmark readiness is claimed."})
    finally:
        lock.unlink(missing_ok=True)
    return status(home, True)


def safe_output(folder, requested=None):
    base = Path(folder) / "demo-runs"
    no_links(base)
    name = datetime.now(timezone.utc).strftime("demo-%Y%m%dT%H%M%S%fZ")
    output = Path(requested).expanduser().absolute() if requested else base / name
    no_links(output)
    if output.parent.resolve() != base.resolve() or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,47}", output.name):
        raise ValueError(f"Demo output must be a new direct child of {base} with a simple name <=48 characters")
    if output.exists():
        raise FileExistsError(f"Demo output already exists: {output}")
    return output


def demo(home, output=None):
    state = status(home, True)
    if not state["ready"]:
        raise ValueError("Harness2 demo runtime is not ready; run install first")
    folder, python = paths(home)
    destination = safe_output(folder, output)
    destination.parent.mkdir(exist_ok=True)
    destination.mkdir()
    worker = Path(__file__).with_name("msshi_harness2_worker.py").resolve()
    if not worker.is_file():
        raise ValueError("Missing standalone demo worker")
    begin = time.monotonic()
    with (destination / "worker.log").open("x", encoding="utf-8") as log:
        owned_run([str(python), "-I", "-B", str(worker), "--output", str(destination)], environment(folder, destination), 120, cwd=destination, stdout=log, stderr=subprocess.STDOUT)
    proof = read(destination / "MSSHI_DEMO_PROOF.json")
    if not proof.get("success"):
        raise ValueError(f"Demo did not pass; inspect {destination / 'worker.log'}")
    proof.update(output=str(destination), source_commit=SOURCE_COMMIT, elapsed_seconds=round(time.monotonic() - begin, 3), wrapper_sha256=digest(Path(__file__)), worker_sha256=digest(worker), installed_package_hashes_verified=True)
    atomic(destination / "MSSHI_DEMO_PROOF.json", proof)
    installation = read(folder / "INSTALLATION.json")
    installation["last_demo"] = proof
    atomic(folder / "INSTALLATION.json", installation)
    return proof


def plan(goal):
    return {"proposal_only": True, "goal": goal, "method": "Propose-Probe-Compose with fixed model weights", "editable_components_in_isolated_copy_only": list(COMPONENTS), "roles": {"Val": "define evaluation questions, held-out cases, evidence and uncertainty", "Coder": "prepare isolated candidate copies, reproducible probes and rollback diff", "Shizuka": "receive the review summary through existing authorized coordination"}, "steps": ["Record the baseline and a narrow hypothesis before proposing edits", "Propose candidate changes only in a separate task workspace", "Probe against identical tasks; keep held-out evaluation separate and prevent answer/rubric leakage", "Compose a candidate using observed contrasts; report failures, costs and uncertainty", "Present the diff, evidence, rollback and remaining risks for human review"], "promotion": "No automatic promotion into Hermes configuration, persona, SOUL, memory, skills or plugins", "benchmark_execution": "Excluded from this wrapper; requires a separate explicit setup and authorization", "api_calls_made": 0}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hermes-home")
    subs = parser.add_subparsers(dest="action", required=True)
    p = subs.add_parser("status"); p.add_argument("--verify", action="store_true")
    p = subs.add_parser("install"); p.add_argument("--source")
    p = subs.add_parser("demo"); p.add_argument("--output")
    p = subs.add_parser("plan"); p.add_argument("--goal", default="Evaluate a narrow harness improvement without changing live Hermes")
    args = parser.parse_args(argv)
    home = root_home(args.hermes_home)
    if args.action == "status":
        result = status(home, args.verify)
    elif args.action == "install":
        result = install(home, args.source)
    elif args.action == "demo":
        result = demo(home, args.output)
    else:
        result = plan(args.goal)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(f"Harness2 error: {exc}", file=sys.stderr)
        raise SystemExit(1)
