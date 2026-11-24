"""Metadata-only tests: never fetch source, weights, or providers."""
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import msshi_sources as sources

class UpstreamPins(unittest.TestCase):
    def test_all_git_sources_have_real_revision_shape(self):
        data=json.loads((ROOT/'configs/upstreams.json').read_text(encoding='utf-8-sig'))
        rows=[row for row in data['entries'] if row['source_type']=='git']
        self.assertEqual(len(rows),67)
        self.assertTrue(all(sources.COMMIT.fullmatch(row.get('revision','')) for row in rows))

    def manifest(self, folder, revision):
        p=Path(folder)/'sources.json'
        row={'id':'model','source_type':'model-card','source':'https://huggingface.co/owner/model','pack':'core'}
        if revision: row['revision']=revision
        p.write_text(json.dumps({'schema_version':1,'entries':[row]}))
        return p

    def test_model_card_uses_commit_when_available(self):
        with TemporaryDirectory() as tmp:
            pin='a'*40
            self.assertIn('/raw/'+pin+'/',sources.upstream_entries(self.manifest(tmp,pin))['model'][1])

    def test_model_card_rejects_path_in_revision(self):
        with TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): sources.upstream_entries(self.manifest(tmp,'../../private'))

    def test_unpinned_card_remains_explicit_metadata_main(self):
        with TemporaryDirectory() as tmp:
            self.assertIn('/raw/main/',sources.upstream_entries(self.manifest(tmp,None))['model'][1])

if __name__=='__main__':unittest.main()
