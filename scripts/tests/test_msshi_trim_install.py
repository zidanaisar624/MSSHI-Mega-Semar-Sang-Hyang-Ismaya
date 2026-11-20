"""Synthetic, offline MSSHITrim installation and integrity regressions."""
import hashlib
import importlib.util
import io
from contextlib import redirect_stdout
import json
from pathlib import Path
import sys
import tarfile
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import zipfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import msshi_trim_setup as trim
import msshi_hermes_profiles as hp
import msshi_llmtrim as wrapper


class TrimInstall(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory(prefix='msshi-trim-offline-')
        self.addCleanup(self.tmp.cleanup)
        self.home=Path(self.tmp.name)
        self.fake=b'fixture local binary; never executed'
        self.binary=self.home/'tools/llmtrim/llmtrim.exe'
        self.original=(b'# Keep user header\r\nmodel:\r\n  provider: user-choice\r\n'
          b'  default: user-model\r\nproviders:\r\n  user-choice:\r\n'
          b'    api_key: DUMMY_NOT_A_SECRET\r\n'
          b'delegation:\r\n  backend: default\r\n  model: user-child\r\n')

    def profile(self,name='default',config=None):
        folder=self.home if name=='default' else self.home/'profiles'/name
        folder.mkdir(parents=True,exist_ok=True)
        if config is not None:
            (folder/'config.yaml').write_bytes(config)
        else:
            (folder/'SOUL.md').write_text('Generic role',encoding='utf-8')
        return folder

    def verified(self):
        self.binary.parent.mkdir(parents=True,exist_ok=True)
        self.binary.write_bytes(self.fake)
        return patch.object(trim,'binary_plan',return_value=(self.binary,{},
            {'status':'verified_existing','version':trim.VERSION,'downloaded':False}))

    def test_archive_checksum_failure_never_extracts(self):
        with self.assertRaisesRegex(ValueError,'checksum'):
            trim.extract_binary(b'invalid archive','release.zip','0'*64)

    def test_extracts_one_zip_member_without_writing_archive_paths(self):
        data=io.BytesIO()
        with zipfile.ZipFile(data,'w') as z:
            z.writestr('docs/notes.txt','unused')
            z.writestr('../../llmtrim.exe',self.fake)
        payload=data.getvalue()
        self.assertEqual(self.fake,trim.extract_binary(payload,'release.zip',trim.sha(payload)))
        self.assertFalse(self.binary.exists())

    def test_duplicate_binary_or_tar_symlink_rejected(self):
        data=io.BytesIO()
        with zipfile.ZipFile(data,'w') as z:
            z.writestr('one/llmtrim.exe',b'one')
            z.writestr('two/llmtrim.exe',b'two')
        with self.assertRaisesRegex(ValueError,'exactly one'):
            trim.extract_binary(data.getvalue(),'release.zip',trim.sha(data.getvalue()))
        data=io.BytesIO()
        with tarfile.open(fileobj=data,mode='w:gz') as z:
            row=tarfile.TarInfo('llmtrim');row.type=tarfile.SYMTYPE;row.linkname='/elsewhere'
            z.addfile(row)
        with self.assertRaisesRegex(ValueError,'member'):
            trim.extract_binary(data.getvalue(),'release.tar.gz',trim.sha(data.getvalue()))

    def test_preview_never_downloads_or_writes(self):
        self.profile(config=self.original)
        with patch.object(trim,'host_target',return_value=('windows','x86_64')), patch.object(trim,'fetch_archive') as fetch:
            result=trim.install(self.home,apply=False,allow_download=True)
            fetch.assert_not_called()
        self.assertFalse(result['applied'])
        self.assertEqual('pending_binary_download',result['binary']['status'])
        self.assertFalse((self.home/'plugins').exists())
        self.assertEqual(self.original,(self.home/'config.yaml').read_bytes())

    def test_apply_enables_all_and_preserves_nonplugin_bytes(self):
        for name in ['default','yukino','shizuka','val','kiki-chii','shikaku']:
            self.profile(name,self.original)
        with self.verified():
            result=trim.install(self.home,apply=True)
        self.assertTrue(result['applied'])
        self.assertEqual(6,len(result['profiles']))
        self.assertTrue(Path(result['receipt']).is_file())
        for folder in trim.profile_dirs(self.home).values():
            raw=(folder/'config.yaml').read_bytes()
            self.assertTrue(raw.startswith(self.original))
            cfg=hp.load_yaml_mapping(raw)
            self.assertEqual([trim.PLUGIN],cfg['plugins']['enabled'])
            self.assertEqual('user-model',cfg['model']['default'])
            self.assertEqual('DUMMY_NOT_A_SECRET',cfg['providers']['user-choice']['api_key'])
            self.assertTrue((folder/'plugins'/trim.PLUGIN/'json-only.toml').is_file())
        desktop_ui=self.home/'desktop-plugins'/trim.PLUGIN/'plugin.js'
        self.assertTrue(desktop_ui.is_file())
        self.assertIn('MSSHITrim',desktop_ui.read_text(encoding='utf-8'))
        self.assertIn('registerSettingsPage',desktop_ui.read_text(encoding='utf-8'))

    def test_existing_disabled_preserved_unless_explicit_force(self):
        raw=self.original+b'plugins:\r\n  disabled: [msshi-auto-trim]\r\n'
        self.profile(config=raw)
        with self.verified():
            result=trim.install(self.home,apply=True)
            self.assertEqual('preserved_explicit_disable',result['profiles'][0]['status'])
            self.assertEqual(raw,(self.home/'config.yaml').read_bytes())
            self.assertFalse((self.home/'plugins').exists())
            forced=trim.install(self.home,apply=True,force_enable=True)
        self.assertTrue(forced['applied'])
        cfg=hp.load_yaml_mapping((self.home/'config.yaml').read_bytes())
        self.assertEqual([],cfg['plugins']['disabled'])

    def test_custom_plugin_edits_remain_untouched(self):
        self.profile(config=self.original)
        path=self.home/'plugins'/trim.PLUGIN/'__init__.py'
        path.parent.mkdir(parents=True);path.write_bytes(b'# user custom hook')
        with self.verified():
            result=trim.install(self.home,apply=True)
        self.assertEqual('preserved_custom_plugin_files',result['profiles'][0]['status'])
        self.assertEqual(b'# user custom hook',path.read_bytes())
        self.assertEqual(self.original,(self.home/'config.yaml').read_bytes())

    def test_existing_custom_binary_preserved(self):
        self.binary.parent.mkdir(parents=True);self.binary.write_bytes(b'user build')
        with patch.object(trim,'fetch_archive') as fetch:
            binary,changes,result=trim.binary_plan(self.home,allow_download=True,target=('windows','x86_64'))
        fetch.assert_not_called()
        self.assertIsNone(binary)
        self.assertEqual({},changes)
        self.assertEqual('pending_existing_unverified_binary_preserved',result['status'])
        self.assertEqual(b'user build',self.binary.read_bytes())

    def test_stage_before_hermes_and_enable_after_config_exists(self):
        self.profile()
        with self.verified():
            first=trim.install(self.home,apply=True)
            self.assertEqual('deferred_until_native_config',first['profiles'][0]['status'])
            self.assertFalse((self.home/'config.yaml').exists())
            (self.home/'config.yaml').write_bytes(self.original)
            second=trim.install(self.home,apply=True)
        self.assertEqual('enabled',second['profiles'][0]['status'])

    def test_second_install_is_idempotent_and_rollback_keeps_later_edit(self):
        self.profile(config=self.original)
        with self.verified():
            first=trim.install(self.home,apply=True)
            second=trim.install(self.home,apply=True)
        self.assertEqual(0,second['files_planned'])
        cfg=self.home/'config.yaml';changed=cfg.read_bytes()+b'# later edit\r\n';cfg.write_bytes(changed)
        result=hp.rollback_profile_receipt(Path(first['receipt']),expected_home=self.home)
        self.assertTrue(result['conflicts'])
        self.assertEqual(changed,cfg.read_bytes())

    def test_local_binary_manifest_checks_bytes_before_probe(self):
        self.binary.parent.mkdir(parents=True);self.binary.write_bytes(self.fake)
        marker=self.binary.with_name('msshi-provenance.json')
        asset,digest=trim.ASSETS[('windows','x86_64')]
        marker.write_bytes(trim.encode({'managed_by':trim.OWNER,'archive_sha256':digest,'binary_sha256':trim.sha(self.fake)}))
        with patch.object(trim,'probe') as probe, patch.object(trim,'fetch_archive') as fetch:
            binary,changes,result=trim.binary_plan(self.home,allow_download=True,target=('windows','x86_64'))
            self.assertEqual(self.binary,binary);probe.assert_called_once();fetch.assert_not_called()
            self.binary.write_bytes(self.fake+b'changed')
            rejected=trim.binary_plan(self.home,allow_download=True,target=('windows','x86_64'))
        self.assertIsNone(rejected[0])

    def test_status_reads_only_safe_metadata_and_never_runs_a_binary(self):
        self.profile(config=self.original)
        with self.verified():
            trim.install(self.home,apply=True)
        output=io.StringIO()
        with patch.object(wrapper.subprocess,'run') as run, redirect_stdout(output):
            self.assertEqual(0,wrapper.main(['--home',str(self.home),'--status']))
            run.assert_not_called()
        report=json.loads(output.getvalue())
        self.assertEqual('MSSHITrim',report['display_name'])
        self.assertTrue(report['plugin_enabled'])
        self.assertTrue(report['runtime_present'])
        self.assertFalse(report['runtime_hash_matches_installer_record'])
        self.assertNotIn('DUMMY_NOT_A_SECRET',output.getvalue())


if __name__=='__main__':
    unittest.main()
