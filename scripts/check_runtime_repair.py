"""Offline regressions for MuZA roles, truthful baselines, and native route guards."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import msshi_runtime as runtime

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

BRIDGE = ROOT / 'skills/cli-anything-universal-bridge/scripts'
bridge = load('repair_bridge_fixture', BRIDGE / 'setup_cli_anything_hermes.py')
hub = bridge.hub
runtime._BRIDGE_POLICY = hub

def capture(fn, *args, **kwargs):
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        result = fn(*args, **kwargs)
    return result, stream.getvalue()

def refused(fn, *args, **kwargs):
    try:
        capture(fn, *args, **kwargs)
    except ValueError:
        return
    raise AssertionError('Expected refusal: ' + fn.__name__)

def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))

passed = []
expected = {
    'default':set(), 'yukino':set(), 'shizuka':set(),
    'val':{'pdfcraft','gridcraft','wordcraft','deckcraft'},
    'shikaku':{'craftanything','figcraft'},
    'kiki-chii':{'anicraft','filmcraft','effectcraft','soundcraft','photocraft','lightcraft','designcraft',
                'figcraft','vectorcraft','cadcraft','solidcraft','materialcraft','texturecraft'},
}
assert set(hub.ARTCRAFT) == set.union(*expected.values())
assert expected['shikaku'] & expected['kiki-chii'] == {'figcraft'}
assert not expected['val'] & (expected['shikaku'] | expected['kiki-chii'])
for profile, names in expected.items():
    assert {name for name in hub.ARTCRAFT if hub.target_allowed(profile,name)} == names
for profile in expected:
    assert not any(hub.target_allowed(profile,name) for name in ('gimp','libreoffice','solvecraft','gdrive','gdrive-web'))
    assert not any(hub.target_allowed(profile,'cli:'+name) for name in ('gimp','libreoffice','solvecraft','gdrive-web'))
    assert {name for name in hub.ARTCRAFT if hub.target_allowed(profile,'cli:'+name)} == expected[profile]
assert not hub.target_allowed('kiki-chii','blender-cli') and not hub.target_allowed('val','cli:blender')
assert bridge.allowed_id('anicraft')
assert read(ROOT/'configs/muza_app_policy.json')['artcraft'] == {key:list(value) for key,value in hub.MUZA_ARTCRAFT.items()}
passed.append('strict ArtCraft 4/2/13; figcraft only shared; coordinators and forbidden tools excluded')

with TemporaryDirectory(prefix='msshi-runtime-repair-', dir=ROOT.parent) as temporary:
    scratch=Path(temporary);home=scratch/'Hermes';apps=scratch/'ArtCraft Apps'
    for target in hub.ARTCRAFT:
        folder='craft-anything' if target=='craftanything' else target
        binary=apps/folder/(folder+('-cli.exe' if os.name=='nt' else '-cli'))
        binary.parent.mkdir(parents=True,exist_ok=True);binary.write_text('fixture only; never execute',encoding='utf-8')
    originals={}
    for profile in expected:
        directory=home if profile=='default' else home/'profiles'/profile
        directory.mkdir(parents=True,exist_ok=True)
        (directory/'config.yaml').write_text('model:\n  provider: fixture\n  model: keep-model\ndisplay_name: Original label\n',encoding='utf-8')
        (directory/'SOUL.md').write_text('# Private fixture '+profile+'\n',encoding='utf-8')
        (directory/'skills/cli-anything-universal-bridge/scripts').mkdir(parents=True)
        for name in ('config.yaml','SOUL.md'):originals[directory/name]=(directory/name).read_bytes()
    environment={'HERMES_HOME':str(home),'MSSHI_ARTCRAFT_ROOT':str(apps),'MSSHI_IGNORE_REGISTRY_HERMES_HOME':'1','MSSHI_WINDOWS_D_DRIVE':''}
    with patch.dict(os.environ,environment),patch.object(runtime,'executable',return_value=None), \
         patch.object(runtime.hermes_profiles,'sync_pending_profile_configs',return_value={'seeded_configs':[],'seeded_envs':[]}):
        for profile,names in expected.items():
            routes=runtime.native_routes(home,profile,{})
            assert set(routes['targets']) & set(hub.ARTCRAFT)==names
            assert all(routes['targets'][name]['readiness']=='available' for name in names)
            assert all(str(apps) in routes['targets'][name]['executable'] for name in names)
            assert routes['targets']['gdrive']['readiness']==routes['targets']['gdrive-web']['readiness']=='disabled'
        capture(runtime.migrate,home)
        assert all(path.read_bytes()==contents for path,contents in originals.items())
        migration=read(home/'msshi-runtime/last-migration.json')
        assert migration['preservation_baseline']['schema_version']==2
        assert runtime.preservation_report(home,migration)['provider_model_preserved']
        _,text=capture(runtime.status,home);status=json.loads(text)
        assert status['readiness']=='READY' and status['result']=='PASS_SUCCESS'
        passed.append('fixture migration discovers native binaries without MCP, preserves config/SOUL bytes and records verified schema2 baseline')

        root_config=home/'config.yaml'
        root_config.write_text(root_config.read_text().replace('Original label','Changed UI label'),encoding='utf-8')
        (home/'SOUL.md').write_text('# User-edited fixture SOUL\n',encoding='utf-8')
        state=runtime.preservation_report(home,migration)
        assert state['provider_model_preserved'] and state['config_changed_outside_llm'] and state['soul_changed_since_baseline']
        before_files={str(path):path.read_bytes() for path in originals}
        _,text=capture(runtime.rebaseline,home)
        preview=json.loads(text);assert not preview['current_llm_acceptance_required']
        refused(runtime.rebaseline,home,True)
        capture(runtime.rebaseline,home,True,preview['snapshot'])
        assert all(Path(path).read_bytes()==value for path,value in before_files.items())
        assert not runtime.preservation_report(home,read(home/'msshi-runtime/last-migration.json'))['soul_changed_since_baseline']
        passed.append('UI/SOUL edits do not masquerade as provider changes; preview/apply refresh is byte-preserving')

        root_config.write_text(root_config.read_text().replace('keep-model','intended-new-model'),encoding='utf-8')
        _,text=capture(runtime.rebaseline,home);preview=json.loads(text)
        assert preview['current_llm_acceptance_required'] and preview['preservation_before']['state']=='LLM_SETTINGS_CHANGED'
        before_migration=(home/'msshi-runtime/last-migration.json').read_bytes()
        refused(runtime.rebaseline,home,True,preview['snapshot'])
        assert (home/'msshi-runtime/last-migration.json').read_bytes()==before_migration
        root_config.write_text(root_config.read_text()+'ui_only: edited-after-preview\n',encoding='utf-8')
        refused(runtime.rebaseline,home,True,preview['snapshot'],True,'Authorized current model')
        _,text=capture(runtime.rebaseline,home);fresh=json.loads(text)
        before=root_config.read_bytes()
        capture(runtime.rebaseline,home,True,fresh['snapshot'],True,'User selected these current model settings')
        assert root_config.read_bytes()==before
        updated=read(home/'msshi-runtime/last-migration.json')
        assert updated['baseline_acceptance']['method']=='explicit_current_configuration_acceptance'
        assert updated['baseline_acceptance']['historical_external_edits_verified'] is False
        assert runtime.preservation_report(home,updated)['provider_model_preserved']
        passed.append('changed LLM settings require explicit acceptance and fresh snapshot; no forced history claim or config mutation')

        legacy={'protected_config_hashes':{str(path):runtime.legacy_protected(path.read_bytes()) for path in originals if path.name=='config.yaml'}}
        assert runtime.preservation_report(home,legacy)['provider_model_preserved']
        root_config.write_text(root_config.read_text().replace('Changed UI label','Legacy UI edit'),encoding='utf-8')
        legacy_state=runtime.preservation_report(home,legacy)
        assert not legacy_state['provider_model_preserved'] and legacy_state['state']=='LEGACY_BASELINE_REVIEW_REQUIRED'
        passed.append('legacy stale metadata is reported as review-required, not invented proof of a provider change')

        refused(runtime.ticket,home,'val','vectorcraft','Forbidden role fixture','direct',120)
        fake_id='a'*32
        for argument in ('mcp','serve','--connect','--connect=anything','--serve'):
            refused(runtime.run_target,home,'kiki-chii',fake_id,'lightcraft',[argument],10)
        refused(runtime.run_target,home,'shikaku',fake_id,'craftanything',['setup','--client','hermes'],10)
        refused(runtime.run_target,home,'val',fake_id,'vectorcraft',['--help'],10)
        passed.append('ticket/run reject cross-role apps, MCP/serve/connect and Craft Anything client setup before launch')

        coder=home/'profiles/shikaku';registry=coder/'msshi-bridge/connections.json'
        registry.write_text(json.dumps({'schema_version':1,'targets':list(hub.ARTCRAFT)}),encoding='utf-8')
        candidates={key:{'route':'native-cli','readiness':'available'} for key in hub.ARTCRAFT}
        _,data,report=bridge.planned_registration(registry,candidates,[],'auto-reconnect',None,profile_home=coder)
        assert set(json.loads(data)['targets'])==expected['shikaku']
        assert json.loads(data)['schema_version']==3 and json.loads(data)['execution']=='msshi-runtime-ticket'
        assert set(report['removed_by_specialization'])==set(hub.ARTCRAFT)-expected['shikaku']
        refused(bridge.planned_registration,registry,candidates,[],'select',['vectorcraft'],profile_home=coder)
        bridge.write_synchronized_registry(registry,data,coder)
        assert set(bridge.read_registry(registry))==expected['shikaku']
        passed.append('legacy registry accepts anicraft, reconciles leaked targets, writes schema3 and refuses explicit cross-role selection')

        def args(**overrides):
            values=dict(hermes_home=home,profile='shikaku',state_dir=None,mode=None,targets=None,query=None,open=None,
                        command_args=[],run=None,dry_run=False,catalog=False,status=False,add=None,remove=None,json=True,ticket=None)
            return SimpleNamespace(**(values|overrides))
        capture(bridge.run,args(remove='figcraft'))
        route_path=home/'msshi-runtime/profiles/shikaku/routes.json'
        assert read(route_path)['targets']['figcraft']['readiness']=='disabled_by_user'
        capture(runtime.migrate,home)
        assert read(route_path)['targets']['figcraft']['readiness']=='disabled_by_user'
        capture(bridge.run,args(add='figcraft'))
        assert read(route_path)['targets']['figcraft']['readiness']=='available'
        assert 'figcraft' in bridge.read_registry(registry)
        passed.append('connect remove/add synchronizes runtime registry and explicit user disable survives migration')

        original_route=route_path.read_bytes()
        real_write=bridge.write_registry
        def fail_registry(path,data):
            if path==registry:raise OSError('fixture write failure')
            return real_write(path,data)
        try:
            with patch.object(bridge,'write_registry',side_effect=fail_registry):
                bridge.write_synchronized_registry(registry,bridge.registry_bytes({'craftanything'}),coder)
        except OSError:pass
        else:raise AssertionError('Expected registry failure')
        assert route_path.read_bytes()==original_route
        passed.append('registry write failure restores prior runtime routes')

    standalone=subprocess.run([sys.executable,'-B','-X','utf8',str(BRIDGE/'msshi_runtime.py'),'rebaseline','--help'],
                              env={**os.environ,**environment},capture_output=True,text=True)
    assert standalone.returncode==0,standalone.stderr
    passed.append('copied standalone runtime resolves its sibling profile helper and rebaseline parser')

print(json.dumps({'passed':passed,'count':len(passed),'live_profiles_modified':False,
                  'model_or_service_calls':0,'app_processes_started':0},ensure_ascii=False,indent=2))
