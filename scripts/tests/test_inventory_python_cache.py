"""Compiled Python caches must not disguise skill ownership or user edits."""
from __future__ import annotations

import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import msshi_update as updater


class PythonCacheInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory(prefix='msshi-cache-fixture-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / 'source'
        self.baseline = self.root / 'baseline'
        self.installed = self.root / 'installed'
        for root, content in ((self.source,'new'), (self.baseline,'old')):
            root.mkdir()
            (root/'VERSION.json').write_text(json.dumps({'version':content}),encoding='utf-8')
            self.skill(root/'skills/example',content)
        self.installed.mkdir()
        self.skill(self.installed/'example','old')

    @staticmethod
    def skill(folder,content):
        (folder/'scripts').mkdir(parents=True)
        (folder/'SKILL.md').write_text('# Example\n',encoding='utf-8')
        (folder/'scripts/main.py').write_text(content,encoding='utf-8')

    @staticmethod
    def cache(folder,content):
        (folder/'scripts/__pycache__').mkdir(parents=True,exist_ok=True)
        (folder/'scripts/__pycache__/main.cpython-314.pyc').write_bytes(content)
        (folder/'legacy.pyo').write_bytes(content)
        (folder/'legacy.pyc').write_bytes(content)

    def args(self,apply=False):
        return SimpleNamespace(source=self.source, baseline=self.baseline, skills_dir=self.installed,
                               skills=None, mode='auto' if apply else 'check', apply=apply, replace_custom=False)

    def test_different_compiled_caches_do_not_create_customization_and_update_is_clean(self):
        self.cache(self.baseline/'skills/example',b'old interpreter')
        self.cache(self.installed/'example',b'new interpreter')
        self.cache(self.source/'skills/example',b'build interpreter')
        self.assertEqual(updater.inventory(self.baseline/'skills/example'),updater.inventory(self.installed/'example'))
        self.assertEqual(updater.run(self.args())['skills'][0]['status'],'update_available')
        result=updater.run(self.args(True))
        self.assertEqual(result['skills'][0]['status'],'updated')
        self.assertEqual((self.installed/'example/scripts/main.py').read_text(),'new')
        self.assertFalse(list((self.installed/'example').rglob('__pycache__')))
        self.assertFalse(list((self.installed/'example').rglob('*.pyc')))
        self.assertFalse(list((self.installed/'example').rglob('*.pyo')))
        self.assertEqual((Path(result['backup'])/'example/scripts/main.py').read_text(),'old')

    def test_real_user_edits_are_still_review_required_and_preserved(self):
        self.cache(self.installed/'example',b'disposable cache')
        custom=self.installed/'example/scripts/main.py'
        custom.write_text('user implementation',encoding='utf-8')
        self.assertEqual(updater.run(self.args(True))['skills'][0]['status'],'different_needs_baseline_or_review')
        self.assertEqual(custom.read_text(),'user implementation')

    def test_ignored_cache_path_still_passes_link_validation(self):
        self.cache(self.source/'skills/example',b'cache')
        original=updater.validate_path
        def refuse_cache(path):
            if path.name=='__pycache__':
                raise ValueError('fixture linked cache')
            original(path)
        with patch.object(updater,'validate_path',side_effect=refuse_cache):
            with self.assertRaisesRegex(ValueError,'linked cache'):
                updater.inventory(self.source/'skills/example')


if __name__=='__main__':
    unittest.main()
