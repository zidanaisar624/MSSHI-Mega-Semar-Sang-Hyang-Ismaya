"""Doctor diagnostics/repairs never call a provider, network, or desktop app."""
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import msshi_doctor as doctor
import msshi_hermes_profiles as hp
from msshi_update import inventory
from msshi_cli import fingerprint

class DoctorReadiness(unittest.TestCase):
    def fixture(self, root):
        def put(name, value='fixture'):
            p=root/name;p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(value,encoding='utf-8')
        put('VERSION.json',json.dumps({'version':'3.1.2','bundled_skills':1,'core_skills':1,'integration_wrappers':0}))
        put('configs/bot_role_and_skill_matrix.json',json.dumps({'skills':[{'slug':'muza-skripsi-template','status':'bundled'}],'shared_foundation':{'jev_model_routing':False}}))
        put('configs/manifests/skill_activation_matrix.json',json.dumps({'app_connection_policy':{'jev_model_routing':False}}))
        for name in ['SKILL.md','scripts/build_template.py','scripts/campus_lookup.py','scripts/extract_guideline.py','references/spec_schema.md','assets/example_spec.json',*[f'assets/presets/preset_{x}.json' for x in ['informatika_ilkom','kuantitatif','kualitatif','rnd','ptk']]]:
            put('skills/muza-skripsi-template/'+name)
        for name in ['MuZA_Search.ipynb','MuZA_Skripsi_Builder.ipynb']:
            put('notebooks/skripsi/'+name)
        put('MULAI_SKRIPSI_DRAG_AND_DROP.bat')

    def diagnose_fixture(self, root, *, deps=True):
        with patch.object(doctor,'ROOT',root),patch.object(doctor,'inject_adaptive_pylibs',return_value=[]),patch.object(doctor,'has_module',return_value=deps),patch.object(doctor,'_native_health',return_value={'status':'NOT_INSTALLED','profiles':[],'provider_execution_tested':False}):
            return doctor.diagnose()

    def test_complete_source_without_native_install_is_not_reported_broken(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root);result=self.diagnose_fixture(root)
            self.assertEqual(result['status'],'HEALTHY')
            self.assertEqual(result['native']['status'],'NOT_INSTALLED')
            self.assertEqual(result['exit_code'],0)

    def test_missing_metadata_is_actionable_without_traceback(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root);(root/'VERSION.json').unlink()
            result=self.diagnose_fixture(root)
            self.assertEqual(result['exit_code'],1)
            self.assertIn('MISSING_METADATA',{i['code'] for i in result['issues']})

    def test_corrupt_json_is_actionable_and_does_not_echo_contents(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root);(root/'VERSION.json').write_text('{private_endpoint: https://secret.invalid',encoding='utf-8')
            result=self.diagnose_fixture(root)
            self.assertIn('INVALID_METADATA',{i['code'] for i in result['issues']})
            self.assertNotIn('secret.invalid',json.dumps(result))

    def test_optional_dependencies_are_warnings_with_commands(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root);result=self.diagnose_fixture(root,deps=False)
            self.assertEqual(result['exit_code'],2)
            self.assertEqual(result['core_status'],'HEALTHY')
            self.assertTrue(any('python-docx' in i['suggested_command'] for i in result['issues']))

    def test_native_config_missing_plugin_and_council_exposes_no_private_values(self):
        with TemporaryDirectory() as tmp:
            home=Path(tmp)/'hermes';folder=home/'profiles/val';folder.mkdir(parents=True)
            cfg={'model':{'default':'private-choice','provider':'private-provider','base_url':'https://private-endpoint.invalid/v1','api_key':'private-key'},'plugins':{'enabled':[]}}
            (folder/'config.yaml').write_text(hp.dump_yaml(cfg),encoding='utf-8')
            (folder/'SOUL.md').write_text('Val research role',encoding='utf-8')
            before={p:p.read_bytes() for p in home.rglob('*') if p.is_file()}
            issues=[]
            with patch.dict(os.environ,{'HERMES_HOME':str(home),'MSSHI_IGNORE_REGISTRY_HERMES_HOME':'1'}),patch('urllib.request.urlopen',side_effect=AssertionError('network forbidden')),patch('subprocess.run',side_effect=AssertionError('process forbidden')):
                result=doctor._native_health(issues)
            self.assertIn('PLUGIN_SETUP_REQUIRED',{i['code'] for i in issues})
            self.assertIn('NEEDS_COUNCIL_CONFIG',{i['code'] for i in issues})
            text=json.dumps([result,issues])
            for secret in ['private-choice','private-provider','private-endpoint.invalid','private-key']:
                self.assertNotIn(secret,text)
            self.assertEqual(before,{p:p.read_bytes() for p in home.rglob('*') if p.is_file()})

    def test_readonly_json_exit_code_matches_report(self):
        report={'exit_code':2,'status':'NEEDS_ATTENTION','issues':[]}
        output=io.StringIO()
        with patch.object(doctor,'diagnose',return_value=report),redirect_stdout(output):
            code=doctor.main(['--json'])
        self.assertEqual(code,2)
        self.assertEqual(json.loads(output.getvalue())['status'],'NEEDS_ATTENTION')

    def test_fix_restores_missing_proven_owned_plugin_with_receipt(self):
        with TemporaryDirectory() as tmp:
            home=Path(tmp)/'hermes';folder=home/'profiles/val';folder.mkdir(parents=True)
            cfg=b'model:\n  default: keep\n  base_url: https://private.invalid\n'
            (folder/'config.yaml').write_bytes(cfg)
            (folder/'SOUL.md').write_text('keep soul',encoding='utf-8')
            incoming=(ROOT/'hermes_plugins/msshi-interaction/plugin.yaml').read_bytes()
            record=folder/'msshi-runtime/interaction-install.json';record.parent.mkdir()
            record.write_text(json.dumps({'managed_by':'msshi-interaction','files':{'plugin.yaml':sha256(incoming).hexdigest()}}),encoding='utf-8')
            with patch.dict(os.environ,{'HERMES_HOME':str(home),'MSSHI_HOME':str(Path(tmp)/'msshi'),'MSSHI_IGNORE_REGISTRY_HERMES_HOME':'1'}),patch('urllib.request.urlopen',side_effect=AssertionError('network forbidden')),patch('subprocess.run',side_effect=AssertionError('process forbidden')):
                result=doctor.repair_owned_files()
            self.assertTrue(result['applied']);self.assertEqual(result['files_restored'],1)
            self.assertTrue(Path(result['receipt']).is_file())
            self.assertEqual((folder/'config.yaml').read_bytes(),cfg)
            self.assertEqual((folder/'plugins/msshi-interaction/plugin.yaml').read_bytes(),incoming)

    def test_fix_preserves_unowned_missing_and_custom_plugin_files(self):
        with TemporaryDirectory() as tmp:
            home=Path(tmp)/'hermes';folder=home/'profiles/val/plugins/msshi-interaction';folder.mkdir(parents=True)
            custom=folder/'plugin.yaml';custom.write_text('custom edit',encoding='utf-8')
            with patch.dict(os.environ,{'HERMES_HOME':str(home),'MSSHI_HOME':str(Path(tmp)/'msshi'),'MSSHI_IGNORE_REGISTRY_HERMES_HOME':'1'}):
                result=doctor.repair_owned_files()
            self.assertFalse(result['applied']);self.assertEqual(custom.read_text(encoding='utf-8'),'custom edit')
            self.assertFalse((folder/'__init__.py').exists())

    def test_fix_restores_only_missing_files_of_fingerprint_owned_skill(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)/'repo';source=root/'skills/demo';source.mkdir(parents=True)
            (source/'SKILL.md').write_text('managed instruction',encoding='utf-8')
            (source/'extra.txt').write_text('extra',encoding='utf-8')
            home=Path(tmp)/'hermes';home.mkdir();msshi=Path(tmp)/'msshi';msshi.mkdir()
            target=home/'profiles/val/skills';skill=target/'demo';skill.mkdir(parents=True)
            (skill/'SKILL.md').write_text('managed instruction',encoding='utf-8')
            (msshi/'state.json').write_text(json.dumps({'targets':{str(target):{'demo':fingerprint(inventory(source))}}}),encoding='utf-8')
            with patch.object(doctor,'ROOT',root),patch.dict(os.environ,{'HERMES_HOME':str(home),'MSSHI_HOME':str(msshi),'MSSHI_IGNORE_REGISTRY_HERMES_HOME':'1'}):
                result=doctor.repair_owned_files()
            self.assertEqual(result['files_restored'],1)
            self.assertEqual((skill/'extra.txt').read_text(encoding='utf-8'),'extra')

if __name__=='__main__':
    unittest.main()
