"""Synthetic-only tests for local active-model key inheritance."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import msshi_hermes_profiles as hp


class ModelEnvironmentSeedTests(unittest.TestCase):
    def test_only_active_standard_provider_key_is_copied_locally(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp)
            (home / 'config.yaml').write_text('model:\n  provider: openai\n  default: user-choice\n')
            (home / '.env').write_text('OPENAI_API_KEY=fixture-allowed\nANTHROPIC_API_KEY=fixture-not-active\nGMAIL_PASSWORD=fixture-private\nDISCORD_BOT_TOKEN=fixture-private\nGOOGLE_CLIENT_ID=fixture-private\nUNKNOWN_PERSONAL_TOKEN=fixture-private\nHERMES_HOME=do-not-copy\n')
            result = hp.clone_safe_env_text(home / '.env')
            self.assertEqual(result, 'OPENAI_API_KEY=fixture-allowed\n')

    def test_custom_active_key_env_reference_is_respected(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp)
            (home / 'config.yaml').write_text('model:\n  provider: custom:research-model\n  default: selected\ncustom_providers:\n  - name: Research Model\n    base_url: https://example.invalid/v1\n    key_env: USER_MODEL_TOKEN\n')
            (home / '.env').write_text('export USER_MODEL_TOKEN="fixture-only"\nUNRELATED_TOKEN=fixture-private\nGMAIL_TOKEN=fixture-private\n')
            self.assertEqual(hp.clone_safe_env_text(home / '.env'), 'export USER_MODEL_TOKEN="fixture-only"\n')

    def test_personal_account_keys_remain_blocked_even_if_misconfigured_as_model(self):
        cfg = {'model': {'provider': 'custom:my-model'}, 'custom_providers': [{'name': 'My Model', 'key_env': 'GMAIL_TOKEN'}]}
        self.assertNotIn('GMAIL_TOKEN', hp.model_env_keys(cfg))

    def test_missing_configuration_copies_no_arbitrary_secrets(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / '.env'
            path.write_text('SOME_PRIVATE_KEY=fixture-private\n')
            self.assertEqual(hp.clone_safe_env_text(path), hp._PLACEHOLDER_ENV)

    def test_active_explicit_env_substitution_is_supported(self):
        cfg = {'model': {'provider': 'named'}, 'providers': {'named': {'api_key': '${USER_CHOSEN_LLM_KEY}'}}}
        self.assertEqual(hp.model_env_keys(cfg), {'USER_CHOSEN_LLM_KEY'})

    def test_enrolled_empty_profile_gets_only_active_key_after_host_configuration(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp)
            profile = home / 'profiles/val'
            profile.mkdir(parents=True)
            (profile / 'SOUL.md').write_text('# User persona\n')
            (profile / '.env').write_text(hp._PLACEHOLDER_ENV)
            hp.record_pending_bots(home, [{'bot_id': 'val', 'label': 'Val'}], 'academic-mahasiswa')
            (home / 'config.yaml').write_text('model:\n  provider: openai\n  default: chosen\n')
            (home / '.env').write_text('OPENAI_API_KEY=fixture-key\nGMAIL_TOKEN=fixture-private\n')
            hp.sync_pending_profile_configs(home)
            self.assertEqual((profile / '.env').read_text(), 'OPENAI_API_KEY=fixture-key\n')
            (profile / '.env').write_text('# User customized empty file\n')
            hp.sync_pending_profile_configs(home)
            self.assertEqual((profile / '.env').read_text(), '# User customized empty file\n')


if __name__ == '__main__':
    unittest.main()
