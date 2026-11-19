"""Inspect/provision the local interaction plugin without running any model."""
from __future__ import annotations
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
PROFILES=('yukino','shizuka','val','kiki-chii','shikaku')
PLUGIN='msshi-interaction'

def _sha(data):return hashlib.sha256(data).hexdigest()

def _plugin(source):
    file=source/'hermes_plugins'/PLUGIN/'__init__.py'
    spec=importlib.util.spec_from_file_location('msshi_interaction_controller',file)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def _helpers(source):
    path=source/'scripts/msshi_hermes_profiles.py'
    spec=importlib.util.spec_from_file_location('msshi_interaction_profiles',path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

def install(home,source=ROOT,profiles=None,apply=False):
    """Only plugin files and plugins: change; explicit disable/custom edits survive."""
    runtime=_plugin(Path(source));home=runtime._ordinary(home);source=runtime._ordinary(source)
    hp=_helpers(source)
    rolemap=hp.team_role_profiles(home)
    selected=list(dict.fromkeys(profiles or rolemap.values()))
    allowed=set(rolemap.values())
    if any(p not in allowed for p in selected):raise ValueError('Choose the actual five role profiles only')
    plans=[];rows=[]
    package=source/'hermes_plugins'/PLUGIN
    owned_names=('__init__.py','plugin.yaml')
    for profile in selected:
        folder=home if profile=='default' else home/'profiles'/profile
        conf=runtime._ordinary(folder/'config.yaml')
        if not conf.is_file():
            rows.append({'profile':profile,'status':'DEFERRED_UNTIL_NATIVE_CONFIG','changed':False});continue
        original=conf.read_bytes();before=hp.load_yaml_mapping(original);after=deepcopy(before)
        plugins=after.setdefault('plugins',{})
        disabled=plugins.get('disabled') or []
        enabled=plugins.get('enabled') or []
        if PLUGIN in disabled or (isinstance(enabled,dict) and enabled.get(PLUGIN) is False):
            rows.append({'profile':profile,'status':'PRESERVED_EXPLICIT_DISABLE','changed':False});continue
        owned_path=runtime._ordinary(folder/'msshi-runtime/interaction-install.json')
        owned=json.loads(owned_path.read_bytes()) if owned_path.is_file() else {}
        if owned and owned.get('managed_by')!=PLUGIN:raise ValueError('Unrecognized interaction ownership record')
        fileplans=[];fingerprints={};conflict=False
        for name in owned_names:
            target=runtime._ordinary(folder/'plugins'/PLUGIN/name)
            new=(package/name).read_bytes();old=target.read_bytes() if target.is_file() else None
            expected=owned.get('files',{}).get(name)
            if old is not None and old!=new and (expected is None or _sha(old)!=expected):conflict=True
            if old!=new:fileplans.append((target,old,new))
            fingerprints[name]=_sha(new)
        if conflict:
            rows.append({'profile':profile,'status':'PRESERVED_CUSTOM_PLUGIN_CONFLICT','changed':False});continue
        if isinstance(enabled,list):
            if PLUGIN not in enabled:enabled.append(PLUGIN)
        elif isinstance(enabled,dict):enabled[PLUGIN]=True
        else:raise ValueError('Unknown native plugin enabled shape')
        plugins['enabled']=enabled
        rendered=original if before.get('plugins')==after['plugins'] else hp._replace_yaml_section_bytes(original,'plugins',after['plugins'])
        if hp.load_yaml_mapping(rendered)!=after:raise ValueError('Plugin-only config edit did not round trip')
        for key in set(before)|set(after):
            if key!='plugins' and before.get(key)!=after.get(key):raise ValueError('Protected config changed')
        if rendered!=original:fileplans.append((conf,original,rendered))
        record=(json.dumps({'schema':1,'managed_by':PLUGIN,'files':fingerprints},indent=2)+'\n').encode()
        old=owned_path.read_bytes() if owned_path.is_file() else None
        if old!=record:fileplans.append((owned_path,old,record))
        plans+=fileplans;rows.append({'profile':profile,'status':'PLUGIN_STAGED_FOR_NATIVE_RELOAD','changed':bool(fileplans)})
    result={'applied':False,'profiles':rows,'files_planned':len(plans),'model_provider_fields_untouched':True,
            'model_calls':0,'receipt':None,'host_requirement':'>=0.23.1','note':'Reload native plugin schema; provider/Council execution remains untested.'}
    if apply and plans:
        tx=hp.ProfileTransaction(home)
        try:
            for path,old,new in plans:
                if (path.read_bytes() if path.is_file() else None)!=old:raise ValueError('Concurrent file change')
                tx.write(path,new,0o600)
            result['receipt']=tx.commit();result['applied']=True
        except Exception:
            tx.rollback();raise
    return result

def status(home,source=ROOT):
    runtime=_plugin(Path(source));home=runtime._ordinary(home);hp=_helpers(Path(source))
    result=[]
    for role,profile in hp.team_role_profiles(home).items():
        folder=home if profile=='default' else home/'profiles'/profile
        path=runtime._ordinary(folder/'config.yaml')
        cfg=hp.load_yaml_mapping(path.read_bytes()) if path.is_file() else {}
        enabled=(cfg.get('plugins') or {}).get('enabled') or []
        disabled=(cfg.get('plugins') or {}).get('disabled') or []
        entry=((cfg.get('plugins') or {}).get('entries') or {}).get(PLUGIN,{})
        opts=entry.get('settings') or entry.get('config') or {}
        refs,agg,readiness,shared=runtime.council_binding(cfg,bool(opts.get('use_current_main_for_council')))
        result.append({'role':role,'profile':profile,'type':1 if role in runtime.T1 else 2,
            'plugin_present':(folder/'plugins'/PLUGIN/'plugin.yaml').is_file(),
            'plugin_enabled':PLUGIN in enabled and PLUGIN not in disabled,
            'council_readiness':readiness if role in runtime.T2 else 'NOT_USED_TYPE_1',
            'reference_count':len(refs) if role in runtime.T2 else 0,
            'advisor_config_present':bool((cfg.get('delegation') or {}).get('model')) if role in runtime.T1 else False,
            'advisor_readiness':('CONFIGURED_NOT_PROVIDER_TESTED' if (cfg.get('delegation') or {}).get('model') else 'NEEDS_ADVISOR_CONFIG') if role in runtime.T1 else 'NOT_USED_TYPE_2',
            'same_engine_logical_roles':shared,'provider_execution_tested':False})
    return {'profiles':result,'model_calls':0,'note':'Local registration/configuration evidence only; not a live Council or Advisor test.'}

def install_existing(home,source=ROOT,apply=False):
    """Provision only an already-created five-role native team, never create bots."""
    home=Path(home);source=Path(source);hp=_helpers(source)
    rolemap=hp.team_role_profiles(home);live=hp.live_named_profiles(home)
    if not all((profile=='default' and (home/'config.yaml').is_file()) or
               (profile in live and (live[profile]/'config.yaml').is_file()) for profile in rolemap.values()):
        return {'applied':False,'status':'DEFERRED_UNTIL_FIVE_NATIVE_PROFILES','model_calls':0,
                'note':'No bots or model/provider settings created. Complete native host setup first.'}
    return install(home,source,list(rolemap.values()),apply)

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--home',type=Path,default=Path(os.environ.get('HERMES_HOME',Path.home()/'.hermes')))
    p.add_argument('--source',type=Path,default=ROOT)
    p.add_argument('--status',action='store_true')
    p.add_argument('--install',action='store_true')
    p.add_argument('--apply',action='store_true')
    p.add_argument('--profiles',nargs='+',choices=['default',*PROFILES])
    p.add_argument('--protocol',action='store_true')
    args=p.parse_args(argv)
    if args.protocol:
        result={'type_1':'Main -> Advisor -> Main approval/execution; no Council',
          'type_2':'Initial plan -> Council round 1 -> Main audit -> Council round 2 -> Main approval/execution; no separate subagent',
          'ambiguity':'Direct request asks User; forwarded request asks sender, then User only if needed',
          'sources':'Aggregator requests sources; Main brokers approved tools and evidence',
          'fast_chat':'No Advisor/Council calls for brief or unconfirmed requests'}
    elif args.install:result=install(args.home,args.source,args.profiles,args.apply)
    else:result=status(args.home,args.source)
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
