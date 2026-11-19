"""A historical migration must not re-enable later-disconnected services."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import msshi_runtime as runtime

class ServiceChoices(unittest.TestCase):
    def test_current_disabled_remote_flags_override_historical_enabled(self):
        now=b'model:\n  default: chosen\n  provider: chosen\nmcp_servers:\n  tinyfish:\n    url: https://example.invalid/mcp\n    enabled: false\n    lazy: true\nplugins:\n  enabled: [custom-plugin]\n  disabled: [tinyfish]\n'
        old=b'mcp_servers:\n  tinyfish:\n    enabled: true\n    lazy: false\nplugins:\n  enabled: [tinyfish]\n'
        updated,_=runtime.config_update(now,old)
        self.assertEqual(updated,now)

    def test_removed_remote_plugin_is_not_reintroduced_during_trim_migration(self):
        now=b'model:\n  default: chosen\n  provider: chosen\nplugins:\n  enabled: [custom-plugin]\n'
        old=b'plugins:\n  enabled: [tinyfish]\n'
        updated,_=runtime.config_update(now,old,auto_trim_binary=Path('C:/fixture/llmtrim.exe'))
        d=runtime.yaml_read(updated)
        self.assertNotIn('tinyfish',d['plugins']['enabled'])
        self.assertEqual(d['model'],runtime.yaml_read(now)['model'])

if __name__=='__main__':unittest.main()
