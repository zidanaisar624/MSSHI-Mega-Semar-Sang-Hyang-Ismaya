"""Offline Academic installation and application-routing regression tests."""
import argparse
import contextlib
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
import install_msshi as installer
import msshi_academic as academic
import msshi_hermes_profiles as hp
import msshi_runtime as runtime
sys.path.insert(0, str(ROOT / 'skills/cli-anything-universal-bridge/scripts'))
import msshi_bridge_runtime as bridge
import setup_cli_anything_hermes as connect


class AcademicInstallTests(unittest.TestCase):
    def test_project_is_native_and_does_not_adopt_personal_vault(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp) / 'HermesData'
            self.assertEqual(academic.project_path(home), home / 'workspace/academic')
            with self.assertRaises(ValueError):
                academic.project_path(home, Path(tmp) / 'HermesProject')

    def test_profile_and_notes_preserved_after_reinstall(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp) / 'HermesData'
            values = {'preferred_name': 'Nama Pilihan', 'academic_level': 'S2', 'academic_topic': 'Topik contoh'}
            first = academic.install_project(home, 'academic-mahasiswa', ROOT, values)
            project = Path(first['project'])
            profile = project / '00_PROFIL_AKADEMIK_PENGGUNA.md'
            self.assertIn('Nama Pilihan', profile.read_text(encoding='utf-8'))
            self.assertIn('S2', profile.read_text(encoding='utf-8'))
            custom = b'# Catatan yang sudah ditulis pengguna\r\n'
            profile.write_bytes(custom)
            second = academic.install_project(home, 'academic-mahasiswa', ROOT, {'preferred_name': 'Beda'})
            self.assertEqual(profile.read_bytes(), custom)
            self.assertFalse(second['created'])
            self.assertFalse((project / '.obsidian').exists())
            self.assertFalse((project / '1. Private').exists())

    def test_fresh_native_install_uses_academic_without_changing_model(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp) / 'HermesData'
            home.mkdir()
            original = b'# exact user config\r\nmodel:\r\n  provider: user-selected\r\n  default: user-chosen\r\n'
            (home / 'config.yaml').write_bytes(original)
            with patch.dict(os.environ, {'HERMES_HOME': str(home), 'MSSHI_IGNORE_REGISTRY_HERMES_HOME': '1', 'MSSHI_NO_PDF': '1'}), contextlib.redirect_stdout(io.StringIO()):
                code = installer.main(['--platform', 'hermes', '--target-dir', str(home / 'profiles'), '--preferred-name', 'Rani', '--academic-level', 'S1', '--apply'])
            self.assertEqual(code, 0)
            self.assertEqual(hp.load_yaml_mapping((home / 'config.yaml').read_bytes())['model'], hp.load_yaml_mapping(original)['model'])
            self.assertIn('Koordinator ide', (home / 'SOUL.md').read_text(encoding='utf-8'))
            self.assertEqual(json.loads((home / academic.MARKER).read_text())['preset'], 'academic-mahasiswa')
            for role in ('shizuka', 'val', 'kiki-chii', 'shikaku'):
                self.assertTrue((home / 'profiles' / role / 'SOUL.md').is_file())
            self.assertIn('Rani', (home / 'workspace/academic/00_PROFIL_AKADEMIK_PENGGUNA.md').read_text(encoding='utf-8'))

    def test_existing_muza_mode_is_not_changed_by_unattended_setup(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp) / 'HermesData'
            academic.record_active(home, 'muza-preset', ROOT)
            self.assertEqual(academic.existing_mode(home), 'muza-preset')
            self.assertEqual(academic.existing_mode(home, {'setup_mode': 'academic-mahasiswa'}), 'muza-preset')

    def test_model_or_credentials_not_part_of_public_profile_inputs(self):
        parser = argparse.ArgumentParser()
        academic.add_arguments(parser)
        values = academic.setup_profile(parser.parse_args([]), 'academic-mahasiswa')
        self.assertEqual(set(values), set(academic.PROFILE_FIELDS))
        self.assertFalse({'model', 'provider', 'api_key'}.intersection(values))


class AcademicRouteTests(unittest.TestCase):
    def make_home(self, tmp):
        home = Path(tmp) / 'HermesData'
        academic.record_active(home, 'academic-mahasiswa', ROOT)
        hp.record_team_layout(home, 'yukino')
        return home

    def test_policy_actually_scopes_default_and_named_profiles(self):
        with TemporaryDirectory() as tmp:
            home = self.make_home(tmp)
            self.assertTrue(bridge.target_allowed('default', 'whatsapp-web', home))
            self.assertTrue(bridge.target_allowed('val', 'wordcraft', home))
            self.assertTrue(bridge.target_allowed('kiki-chii', 'deckcraft', home / 'profiles/kiki-chii'))
            for target in ('blender', 'obs', 'cadcraft', 'solidcraft', 'mcp:gitlab'):
                self.assertFalse(bridge.target_allowed('kiki-chii', target, home))
            self.assertFalse(bridge.target_allowed('shikaku', 'lightcraft', home))

    def test_muza_routes_remain_unchanged(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp)
            academic.record_active(home, 'muza-preset', ROOT)
            self.assertTrue(bridge.target_allowed('kiki-chii', 'cadcraft', home))
            self.assertFalse(bridge.target_allowed('val', 'cadcraft', home))

    def test_heavy_optional_requires_installed_binary_and_explicit_selection(self):
        with TemporaryDirectory() as tmp:
            home = self.make_home(tmp)
            with patch.object(bridge, 'optional_executable', return_value=None):
                self.assertFalse(bridge.target_allowed('kiki-chii', 'blender', home, allow_installed_optional=True))
            with patch.object(bridge, 'optional_executable', return_value='test-binary'):
                self.assertTrue(bridge.target_allowed('kiki-chii', 'blender', home, allow_installed_optional=True))
                self.assertFalse(bridge.target_allowed('kiki-chii', 'blender', home))

    def test_auto_reconnect_does_not_register_available_heavy_apps(self):
        with TemporaryDirectory() as tmp:
            home = self.make_home(tmp)
            profile = home / 'profiles/kiki-chii'
            dest = profile / 'msshi-bridge/connections.json'
            candidates = {'deckcraft': {'route': 'native-cli', 'readiness': 'available'},
                          'blender': {'route': 'native-cli', 'readiness': 'available'}}
            with patch.object(bridge, 'optional_executable', return_value='test-binary'):
                _, data, _ = connect.planned_registration(dest, candidates, [], 'auto-reconnect', None, profile_home=profile)
            self.assertEqual(json.loads(data)['targets'], ['deckcraft'])

    def test_explicit_heavy_selection_is_persisted_only_after_installed_detection(self):
        with TemporaryDirectory() as tmp:
            home = self.make_home(tmp)
            profile = home / 'profiles/kiki-chii'
            state = home / 'msshi-runtime'
            route = state / 'profiles/kiki-chii/routes.json'
            route.parent.mkdir(parents=True)
            route.write_text(json.dumps({'schema': 3, 'targets': {}}))
            (state / 'policy.json').write_text('{}')
            binary = home / 'blender.exe'
            binary.write_bytes(b'fixture; never executed')
            dest = profile / 'msshi-bridge/connections.json'
            dest.parent.mkdir(parents=True)
            candidates = {'blender': {'route': 'native-cli', 'readiness': 'blocked_by_specialization'}}
            with patch.object(connect.hub, 'optional_executable', return_value=str(binary)):
                _, data, result = connect.planned_registration(dest, candidates, [], 'select', ['blender'], profile_home=profile)
                self.assertEqual(result['academic_optional_opt_ins'], ['blender'])
                self.assertFalse(bridge.target_allowed('kiki-chii', 'blender', home))
                connect.write_synchronized_registry(dest, data, profile)
            with patch.object(bridge, 'optional_executable', return_value=str(binary)):
                self.assertTrue(bridge.target_allowed('kiki-chii', 'blender', home))
            with patch.object(bridge, 'optional_executable', return_value=None):
                self.assertFalse(bridge.target_allowed('kiki-chii', 'blender', home))

    def test_runtime_route_inventory_obeys_academic_and_preserves_provider(self):
        with TemporaryDirectory() as tmp:
            home = self.make_home(tmp)
            cfg = {'model': {'provider': 'mine', 'default': 'mine'}}
            with patch.object(runtime, 'bridge_policy', return_value=bridge), patch.object(runtime, 'executable', return_value=None), patch.object(bridge, 'artcraft_executable', return_value=None):
                row = runtime.native_routes(home, 'kiki-chii', cfg)
            self.assertEqual(row['specialization_policy'], 'academic-v1')
            self.assertIn('deckcraft', row['targets'])
            self.assertNotIn('blender', row['targets'])
            self.assertNotIn('cadcraft', row['targets'])
            self.assertEqual(cfg['model'], {'provider': 'mine', 'default': 'mine'})


if __name__ == '__main__':
    unittest.main()
