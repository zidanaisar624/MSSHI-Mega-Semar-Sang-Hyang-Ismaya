"""Native YAML must remain complete when optional YAML libraries are absent."""
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import msshi_hermes_profiles as hp
import msshi_interaction as interaction

NATIVE = b'''model:
  provider: chosen-provider
  default: chosen-main
plugins:
  enabled:
  - msshi-auto-trim
  - msshi-interaction
  disabled: []
moa:
  enabled: true
  presets:
    chosen:
      reference_models:
      - model: chosen-review-1
        provider: chosen-provider
      - model: chosen-review-2
        provider: chosen-provider
      aggregator:
        model: chosen-integrator
        provider: chosen-provider
after_council:
- one
- two
'''

class IndentlessSequences(unittest.TestCase):
    def setUp(self):
        self.no_yaml = patch.dict(sys.modules, {'yaml': None, 'ruamel': None, 'ruamel.yaml': None})
        self.no_yaml.start()
        self.addCleanup(self.no_yaml.stop)

    def test_native_plugin_and_council_sequences_keep_following_keys(self):
        cfg = hp.load_yaml_mapping(NATIVE)
        self.assertEqual(cfg['plugins']['enabled'], ['msshi-auto-trim', 'msshi-interaction'])
        refs = cfg['moa']['presets']['chosen']['reference_models']
        self.assertEqual(len(refs), 2)
        self.assertEqual(refs[1]['provider'], 'chosen-provider')
        self.assertEqual(cfg['after_council'], ['one', 'two'])

    def test_plugin_only_edit_preserves_council_and_all_other_bytes(self):
        original = NATIVE.replace(b'  - msshi-interaction\n', b'')
        before = hp.load_yaml_mapping(original)
        plugins = dict(before['plugins'])
        plugins['enabled'] = plugins['enabled'] + ['msshi-interaction']
        rendered = hp._replace_yaml_section_bytes(original, 'plugins', plugins)
        after = hp.load_yaml_mapping(rendered)
        self.assertEqual(after, {**before, 'plugins': plugins})
        self.assertEqual(original.split(b'moa:', 1)[1], rendered.split(b'moa:', 1)[1])
        self.assertEqual(original.split(b'plugins:', 1)[0], rendered.split(b'plugins:', 1)[0])

    def test_empty_indentless_list_then_following_mapping(self):
        cfg = hp.load_yaml_mapping('outer:\n  list:\n  -\n  - item\n  next: yes\ntail: end\n')
        self.assertEqual(cfg['outer']['list'], [None, 'item'])
        self.assertEqual(cfg['outer']['next'], 'yes')
        self.assertEqual(cfg['tail'], 'end')

    def test_empty_value_is_null_while_explicit_empty_mapping_stays_mapping(self):
        cfg = hp.load_yaml_mapping('unset:\nempty: {}\ncompression:\n  optional_value:\n  enabled: true\n')
        self.assertIsNone(cfg['unset'])
        self.assertEqual(cfg['empty'], {})
        self.assertIsNone(cfg['compression']['optional_value'])
        self.assertTrue(cfg['compression']['enabled'])

    def test_native_provision_is_idempotent_without_yaml_dependency(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp)
            folder = home / 'profiles' / 'kiki-chii'
            folder.mkdir(parents=True)
            path = folder / 'config.yaml'
            path.write_bytes(NATIVE)
            first = interaction.install(home, ROOT, ['kiki-chii'], apply=True)
            self.assertTrue(first['applied'])
            self.assertEqual(path.read_bytes(), NATIVE)
            second = interaction.install(home, ROOT, ['kiki-chii'], apply=True)
            self.assertFalse(second['applied'])
            self.assertEqual(second['files_planned'], 0)

if __name__ == '__main__':
    unittest.main()
