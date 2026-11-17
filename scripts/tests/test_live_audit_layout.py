"""Read-only live-mode audit must work even before optional evidence exists."""
import contextlib
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import check_release_v31 as auditor

class LiveAudit(unittest.TestCase):
    def test_missing_optional_runtime_does_not_crash_live_audit(self):
        with TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            checks,ready,services=auditor.audit(ROOT,Path(tmp),package_only=False)
        self.assertIn('context_career-ops_live_scope_and_copies',checks)
        self.assertIsInstance(ready,dict)

    def test_fresh_default_yukino_expected_scope(self):
        with TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            home=Path(tmp)
            (home/'msshi-runtime').mkdir()
            roles={name:name for name in ('yukino','shizuka','val','kiki-chii','shikaku')}
            roles['yukino']='default'
            (home/'msshi-runtime/team-layout.json').write_text(json.dumps({'schema':1,'default_bot':'yukino','roles':roles}))
            checks,_,_=auditor.audit(ROOT,home,package_only=False)
        expected=checks['context_career-ops_live_scope_and_copies']['evidence']['expected_profiles']
        self.assertIn('default',expected)
        self.assertNotIn('yukino',expected)

if __name__=='__main__':unittest.main()
