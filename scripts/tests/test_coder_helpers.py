"""Offline KAT configuration regressions. No inference or network requests."""
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import msshi_coder_helpers as kat


class CoderHelpers(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.profile = self.home / 'profiles/shikaku'
        self.profile.mkdir(parents=True)
        self.config = b'model:\n  provider: original\n  default: unchanged\ndelegation:\n  backend: msshi-team\n  model: existing-helper\nplugins:\n  enabled: [msshi-team-routing]\n  disabled: []\n'
        (self.profile / 'config.yaml').write_bytes(self.config)
        (self.profile / 'SOUL.md').write_bytes(b'private original persona')
        plugin = self.profile / 'plugins/msshi-team-routing/plugin.yaml'
        plugin.parent.mkdir(parents=True)
        plugin.write_text('name: msshi-team-routing\n')

    def test_missing_endpoint_stays_disabled(self):
        result = kat.configure(self.home, activate=True)
        self.assertEqual(result['status'], 'needs_endpoint')
        self.assertFalse(result['enabled'])

    def test_key_missing_stays_disabled(self):
        with patch.dict(os.environ, {}, clear=True):
            result = kat.configure(self.home, preset='streamlake-payg', activate=True,
                                   accept_documented_model=True)
        self.assertEqual(result['status'], 'needs_api_key')
        self.assertFalse(result['enabled'])
        self.assertEqual(result['source_variant'], 'pro-2.5')
        self.assertNotEqual(result['requested_model'], result['model'])

    def test_metadata_exact_match_enables_scoped_helper_only(self):
        with patch.dict(os.environ, {kat.ENV_NAME: 'fixture-secret'}), \
             patch.object(kat, 'model_catalog', return_value={'ok': True, 'ids': [kat.MODEL, 'other']}):
            result = kat.configure(self.home, base_url='https://fixture.invalid/v1',
                                   probe=True, activate=True)
        self.assertTrue(result['enabled'])
        self.assertEqual(result['validated_model_catalog'], [kat.MODEL])
        self.assertEqual((self.profile / 'config.yaml').read_bytes(), self.config)
        self.assertEqual((self.profile / 'SOUL.md').read_bytes(), b'private original persona')
        self.assertFalse(result['inference_tested'])

    def test_catalog_mismatch_never_falls_back(self):
        with patch.dict(os.environ, {kat.ENV_NAME: 'fixture-secret'}), \
             patch.object(kat, 'model_catalog', return_value={'ok': True, 'ids': ['other']}):
            result = kat.configure(self.home, base_url='https://fixture.invalid/v1',
                                   probe=True, activate=True)
        self.assertEqual(result['status'], 'needs_model_catalog')
        self.assertFalse(result['enabled'])

    def test_missing_native_plugin_blocks_enable(self):
        (self.profile / 'plugins/msshi-team-routing/plugin.yaml').unlink()
        with patch.dict(os.environ, {kat.ENV_NAME: 'fixture-secret'}):
            result = kat.configure(self.home, preset='streamlake-payg', activate=True,
                                   accept_documented_model=True)
        self.assertEqual(result['status'], 'needs_native_team_routing')
        self.assertFalse(result['enabled'])

    def test_explicit_plugin_disable_blocks_enable(self):
        (self.profile / 'config.yaml').write_bytes(self.config.replace(
            b'disabled: []', b'disabled: [msshi-team-routing]'))
        with patch.dict(os.environ, {kat.ENV_NAME: 'fixture-secret'}):
            result = kat.configure(self.home, preset='streamlake-payg', activate=True,
                                   accept_documented_model=True)
        self.assertEqual(result['status'], 'needs_native_team_routing')
        self.assertFalse(result['enabled'])

    def test_status_does_not_expose_unexpected_secret_fields(self):
        path = kat.state_path(self.home)
        kat.atomic(path, kat.encode({'enabled': False, 'api_key': 'secret',
                                    'authorization': 'secret', 'profile': 'shikaku'}))
        text = json.dumps(kat.status(self.home))
        self.assertNotIn('secret', text)
        self.assertNotIn('authorization', text)

    def test_endpoint_security(self):
        for value in ('http://example.com/v1', 'https://key:secret@example.com/v1',
                      'https://example.com/v1?api_key=secret', 'file:///tmp/key'):
            with self.assertRaises(ValueError): kat.endpoint(value)
        self.assertEqual(kat.endpoint('http://localhost:8000/v1/'), 'http://localhost:8000/v1')

    def test_existing_state_backed_up_disable_preserves_config(self):
        kat.configure(self.home)
        kat.wizard(self.home, 'skip')
        self.assertFalse(kat.status(self.home)['enabled'])
        self.assertEqual((self.profile / 'config.yaml').read_bytes(), self.config)

    def test_noninteractive_selection_does_not_download(self):
        with patch.object(sys.stdin, 'isatty', return_value=False), \
             patch.object(kat, 'model_catalog', side_effect=AssertionError('network')):
            self.assertEqual(kat.wizard(self.home, 'cloud')['status'], 'needs_endpoint')


if __name__ == '__main__':
    unittest.main()
