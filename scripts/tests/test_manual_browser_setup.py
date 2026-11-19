"""Local fixtures: browser intent only, no browser/account/network/plugin installation."""
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import msshi_browser_preferences as browser
import msshi_cli as cli


class BrowserPreferences(unittest.TestCase):
    def test_save_is_idempotent_and_does_not_touch_configs_or_credentials(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp)
            originals = {'config.yaml': b'model:\n  provider: keep\n  default: keep-model\n',
                         '.env': b'DUMMY_KEEP=not-a-real-key\n', 'auth.json': b'{"keep":"credential fixture"}'}
            for name, data in originals.items(): (home / name).write_bytes(data)
            result = browser.select(home, 'chrome', 'Work profile', 'Campus account')
            self.assertTrue(result['changed'])
            self.assertFalse(result['cookies_copied'])
            self.assertEqual(result['logged_in'], 'not_verified')
            self.assertEqual(result['network_requests'], 0)
            first = (home / browser.RELATIVE).read_bytes()
            again = browser.select(home, 'chrome', 'Work profile', 'Campus account')
            self.assertFalse(again['changed'])
            self.assertEqual((home / browser.RELATIVE).read_bytes(), first)
            for name, data in originals.items(): self.assertEqual((home / name).read_bytes(), data)

    def test_changed_choice_has_an_exact_backup(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp)
            browser.select(home, 'edge', 'School', '')
            before = (home / browser.RELATIVE).read_bytes()
            result = browser.select(home, 'firefox', 'Research', '')
            receipt = Path(result['receipt'])
            data = json.loads(receipt.read_text())
            self.assertEqual((receipt.parent / data['backup']).read_bytes(), before)
            self.assertEqual(data['before_sha256'], hashlib.sha256(before).hexdigest())
            self.assertFalse(data['credentials_read_or_written'])

    def test_invalid_label_and_invalid_browser_write_nothing(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp)
            for choice, profile in [('chrome', 'two\nlines'), ('chrome', 'api_key=do-not-enter'), ('steel', '')]:
                with self.assertRaises(ValueError): browser.select(home, choice, profile)
            self.assertFalse((home / browser.RELATIVE).exists())

    def test_rollback_restores_exact_bytes_and_preserves_later_edits(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp)
            browser.select(home, 'chrome', 'Own', '')
            original = (home / browser.RELATIVE).read_bytes()
            change = browser.select(home, 'firefox', 'Research', '')
            receipt = Path(change['receipt'])
            self.assertEqual(browser.rollback(home, receipt)['status'], 'rollback_preview')
            self.assertEqual(browser.current(home)['browser'], 'firefox')
            self.assertEqual(browser.rollback(home, receipt, True)['status'], 'restored')
            self.assertEqual((home / browser.RELATIVE).read_bytes(), original)
            change = browser.select(home, 'edge', '', '')
            user_edit = b'{"custom":"keep"}'
            (home / browser.RELATIVE).write_bytes(user_edit)
            self.assertEqual(browser.rollback(home, Path(change['receipt']), True)['status'], 'conflict_preserved')
            self.assertEqual((home / browser.RELATIVE).read_bytes(), user_edit)

    def test_concurrent_edit_is_not_overwritten(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp)
            browser.select(home, 'chrome', '', '')
            original_atomic = browser.atomic
            changed = b'{"user":"concurrent edit"}'
            def intercept(path, data):
                original_atomic(path, data)
                if path.name == 'receipt.json': (home / browser.RELATIVE).write_bytes(changed)
            with patch.object(browser, 'atomic', side_effect=intercept):
                with self.assertRaises(ValueError): browser.select(home, 'edge', '', '')
            self.assertEqual((home / browser.RELATIVE).read_bytes(), changed)

    def test_status_is_read_only_when_not_chosen(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp)
            self.assertEqual(browser.current(home)['status'], 'not_selected')
            self.assertEqual(list(home.iterdir()), [])

    def test_legacy_browser_install_is_noop(self):
        with TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()) as output:
            home = Path(tmp)
            self.assertEqual(browser.main(['--home', str(home), '--install', '--account-transfer', '--approved']), 0)
            self.assertEqual(list(home.iterdir()), [])
        self.assertEqual(json.loads(output.getvalue())['status'], 'legacy_steel_action_retired')


class WizardBrowser(unittest.TestCase):
    def args(self, **extra):
        return SimpleNamespace(connect_services=None, setup_browser=None, browser_profile_label='', browser_account_label='', **extra)

    def test_unattended_legacy_service_flag_does_not_install_or_prompt(self):
        with TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()), \
             patch('msshi_service_connections.install', side_effect=AssertionError('No service installation')), \
             patch.object(cli, '_prompt_choice', side_effect=AssertionError('No inherited-console prompt')):
            home = Path(tmp)
            args = self.args(); args.connect_services = 'share-oauth'
            result = cli._setup_service_connections(args, 'hermes', home, 'id', True)
            self.assertFalse(result['external_services_installed'])
            self.assertEqual(result['status'], 'not_selected')
            self.assertEqual(list(home.iterdir()), [])

    def test_interactive_chrome_saves_only_explicit_labels(self):
        with TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()), \
             patch.object(cli, '_prompt_choice', side_effect=['1', 'Work', 'Campus']), \
             patch('subprocess.Popen', side_effect=AssertionError('No browser process')):
            home = Path(tmp)
            result = cli._setup_service_connections(self.args(), 'hermes', home, 'id', False)
            self.assertEqual((result['browser'], result['profile_label'], result['account_label']), ('chrome', 'Work', 'Campus'))
            self.assertFalse(result['cookies_copied'])
            self.assertFalse(result['external_services_installed'])

    def test_unattended_explicit_browser_and_labels(self):
        with TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
            home = Path(tmp); args = self.args()
            args.setup_browser = 'edge'; args.browser_profile_label = 'Personal'; args.browser_account_label = 'Own account'
            result = cli._setup_service_connections(args, 'hermes', home, 'id', True)
            self.assertEqual(result['browser'], 'edge')
            self.assertEqual(result['logged_in'], 'not_verified')

    def test_cli_retired_services_never_run_service_script(self):
        with TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()) as output, \
             patch.object(cli, 'data_root', return_value=Path(tmp)), \
             patch.object(cli, 'active_script', return_value=None), \
             patch('subprocess.call', side_effect=AssertionError('No service subprocess')):
            self.assertEqual(cli.main(['services', 'install', '--share-oauth']), 0)
        self.assertEqual(json.loads(output.getvalue())['status'], 'manual_user_setup')

    def test_migrate_does_not_refresh_steel(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp)
            (home / 'config.yaml').write_text('model:\n  provider: preserve\n  default: preserve\nplugins:\n  enabled: [msshi-steel-policy]\n')
            with patch.object(cli.hermes_profiles, 'sync_pending_profile_configs', return_value={}), \
                 patch('subprocess.call', return_value=0) as process:
                self.assertEqual(cli.migrate_runtime(ROOT, home), 0)
                self.assertEqual(process.call_count, 1)
                self.assertIn('msshi_runtime.py', process.call_args.args[0][4])


if __name__ == '__main__': unittest.main()
