import json
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
import msshi_forge as forge
import msshi_hermes_profiles as hp


class ForgeTests(unittest.TestCase):
    def test_preview_and_create_without_inheriting_or_launching(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp)
            original = b'model:\n  provider: synthetic\n  default: fixture\n  base_url: https://private.invalid/api\n'
            (home/'config.yaml').write_bytes(original)
            (home/'.env').write_bytes(b'OPENAI_API_KEY=fixture-secret\n')
            design = {'id':'community-planner', 'name':'Community Planner', 'purpose':'Plan meeting agendas',
                      'gap':'Persistent project responsibilities', 'skills':['prep-for-meetings'],
                      'reviews':{'default':'Existing role supports research; planner handles agendas.'}}
            self.assertEqual(forge.provision(home, design)['status'], 'PLAN_ONLY')
            self.assertFalse((home/'profiles').exists())
            with patch.object(forge.trim,'install',return_value={'profiles':[], 'binary':{'status':'pending_binary'}, 'receipt':None}) as install:
                created = forge.provision(home, design, apply=True)
            self.assertEqual(created['status'], 'CREATED_PENDING_USER_MODEL')
            self.assertFalse(install.call_args.kwargs['allow_download'])
            folder = home/'profiles/community-planner'
            self.assertNotIn('model', hp.load_yaml_mapping(folder/'config.yaml'))
            self.assertEqual((folder/'.env').read_bytes(), hp._PLACEHOLDER_ENV.encode())
            self.assertEqual((home/'config.yaml').read_bytes(), original)
            self.assertTrue((folder/'skills/prep-for-meetings/SKILL.md').is_file())
            with self.assertRaises(ValueError):forge.provision(home, design, apply=True)
            with self.assertRaises(ValueError):forge.provision(home, {**design, 'id':'other', 'provider':'synthetic'})

if __name__ == '__main__':
    unittest.main()
