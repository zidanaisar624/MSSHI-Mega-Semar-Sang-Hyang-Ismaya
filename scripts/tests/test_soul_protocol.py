"""SOUL-only protocol updates retain private persona bytes and never activate models."""
from pathlib import Path
import json
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import msshi_soul_protocol as soul


class SoulProtocolTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / 'HermesClient'
        self.prefix = b'\xef\xbb\xbf# Private persona\r\nKeep spelling, voice and all personal references.\r\n'
        self.config = b'model:\r\n  default: current/main\r\n  provider: unchanged\r\ndelegation:\r\n  model: current/helper\r\n'
        self.secret = b'EXISTING_KEY="fixture-not-real"\r\n'
        for name in ('shikaku', 'kiki-chii'):
            folder = self.home / 'profiles' / name
            folder.mkdir(parents=True)
            (folder / 'SOUL.md').write_bytes(self.prefix)
            (folder / 'config.yaml').write_bytes(self.config)
            (folder / '.env').write_bytes(self.secret)

    def test_preview_writes_nothing(self):
        result = soul.apply_protocol(self.home, ['shikaku', 'kiki-chii'])
        self.assertEqual(result['status'], 'preview')
        self.assertFalse((self.home / 'msshi-runtime').exists())
        self.assertEqual((self.home / 'profiles/shikaku/SOUL.md').read_bytes(), self.prefix)

    def test_apply_preserves_private_prefix_config_and_env_and_is_idempotent(self):
        result = soul.apply_protocol(self.home, ['shikaku', 'kiki-chii'], apply=True)
        self.assertTrue(result['applied'])
        self.assertTrue(result['non_selected_protected_files_preserved'])
        for name in ('shikaku', 'kiki-chii'):
            folder = self.home / 'profiles' / name
            text = (folder / 'SOUL.md').read_bytes()
            self.assertTrue(text.startswith(self.prefix))
            self.assertEqual(text.count(soul.COMMON[0]), 1)
            self.assertEqual(text.count(soul.markers(name)[1][0]), 1)
            self.assertEqual((folder / 'config.yaml').read_bytes(), self.config)
            self.assertEqual((folder / '.env').read_bytes(), self.secret)
        second = soul.apply_protocol(self.home, ['shikaku', 'kiki-chii'], apply=True)
        self.assertEqual(second['status'], 'already_current')
        self.assertEqual(len(list((self.home/'msshi-runtime/soul-receipts').glob('*/receipt.json'))), 1)
        receipt = json.loads(Path(result['receipt']).read_text(encoding='utf-8'))
        self.assertNotIn('fixture-not-real', json.dumps(receipt))

    def test_matching_rollback_restores_exact_original_soul(self):
        result = soul.apply_protocol(self.home, ['shikaku'], apply=True)
        preview = soul.rollback(self.home, Path(result['receipt']))
        self.assertEqual(len(preview['would_restore']), 1)
        self.assertNotEqual((self.home/'profiles/shikaku/SOUL.md').read_bytes(), self.prefix)
        rolled = soul.rollback(self.home, Path(result['receipt']), apply=True)
        self.assertFalse(rolled['conflicts'])
        self.assertEqual((self.home/'profiles/shikaku/SOUL.md').read_bytes(), self.prefix)

    def test_refresh_changes_only_managed_ranges_and_keeps_custom_suffix(self):
        template = (soul.ROOT/'configs/personas/shikaku.md').read_bytes()
        first = soul.render(self.prefix, template, 'shikaku') + b'\r\nPrivate project appendix.\r\n'
        updated = template.replace(b'## Nama dan sapaan pengguna', b'## Nama dan sapaan pengguna revisi')
        second = soul.render(first, updated, 'shikaku')
        self.assertTrue(second.startswith(self.prefix))
        self.assertTrue(second.endswith(b'\r\nPrivate project appendix.\r\n'))
        self.assertEqual(second.count(soul.COMMON[0]), 1)
        self.assertIn(b'pengguna revisi', second)

    def test_rollback_preserves_later_user_edit(self):
        result = soul.apply_protocol(self.home, ['shikaku'], apply=True)
        target = self.home/'profiles/shikaku/SOUL.md'
        edited = target.read_bytes() + b'\r\nUser clarification.\r\n'
        target.write_bytes(edited)
        rolled = soul.rollback(self.home, Path(result['receipt']), apply=True)
        self.assertEqual(rolled['conflicts'], [str(target)])
        self.assertEqual(target.read_bytes(), edited)

    def test_incomplete_managed_block_refuses_entire_plan(self):
        target = self.home/'profiles/kiki-chii/SOUL.md'
        target.write_bytes(self.prefix + soul.COMMON[0])
        with self.assertRaises(ValueError):
            soul.apply_protocol(self.home, ['shikaku', 'kiki-chii'], apply=True)
        self.assertEqual((self.home/'profiles/shikaku/SOUL.md').read_bytes(), self.prefix)
        self.assertFalse((self.home/'msshi-runtime').exists())

    def test_link_refusal_and_receipt_path_confinement(self):
        original = Path.is_symlink
        target = self.home/'profiles/shikaku/SOUL.md'
        with patch.object(Path, 'is_symlink', lambda path: path == target or original(path)):
            with self.assertRaises(ValueError):
                soul.apply_protocol(self.home, ['shikaku'], apply=True)
        outside = Path(self.temp.name)/'receipt.json'
        outside.write_text('{}')
        with self.assertRaises(ValueError):
            soul.rollback(self.home, outside, apply=True)

    def test_receipt_cannot_restore_config_or_other_files(self):
        result = soul.apply_protocol(self.home, ['shikaku'], apply=True)
        receipt = Path(result['receipt'])
        data = json.loads(receipt.read_text())
        data['entries'][0]['path'] = str(self.home/'profiles/shikaku/config.yaml')
        receipt.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            soul.rollback(self.home, receipt, apply=True)
        self.assertEqual((self.home/'profiles/shikaku/config.yaml').read_bytes(), self.config)

    def test_all_public_templates_ask_generic_user_identity(self):
        for name in soul.PROFILES:
            data = (soul.ROOT/'configs/personas'/(name+'.md')).read_bytes()
            self.assertIsNotNone(soul.span(data, *soul.COMMON))
            self.assertIn(b'Identitas pembuat proyek', data)
            self.assertNotIn(b'Muhammad Zidan Aisar', data)
        for name in ('shikaku', 'kiki-chii'):
            data = (soul.ROOT/'configs/personas'/(name+'.md')).read_text(encoding='utf-8')
            self.assertIn('minta izin terpisah', data)
            self.assertIn('model/provider yang benar-benar', data)
            self.assertNotIn('Fable 5.2', data)


if __name__ == '__main__':
    unittest.main()
