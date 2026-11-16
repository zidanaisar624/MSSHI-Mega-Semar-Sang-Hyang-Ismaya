"""Automatic manual delivery remains offline, checked and reversible."""
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import msshi_manuals as manuals


class ManualDelivery(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.dest = self.root / 'downloads'
        self.payload = b'%PDF-1.4\nfixture only\n'
        relative = 'docs/manuals/v3.1.1/guide.pdf'
        pdf = self.source / relative
        pdf.parent.mkdir(parents=True)
        pdf.write_bytes(self.payload)
        self.entry = {'version': 'latest', 'maps_to': 'v3.1.1', 'filename': 'guide.pdf',
                      'rel_path': relative, 'sha256': hashlib.sha256(self.payload).hexdigest(), 'pages': 1}
        (self.source / manuals.CATALOG_REL).write_text(json.dumps(
            {'latest_version': 'v3.1.1', 'manuals': [self.entry, {**self.entry, 'version':'v3.1.1'}]}))
        self.args = SimpleNamespace(no_pdf=False, pdf_dest=self.dest)

    def test_automatic_without_interactive_prompt(self):
        with patch.dict(os.environ, {'MSSHI_NO_PDF': '0'}), \
             patch('builtins.input', side_effect=AssertionError('unexpected prompt')):
            result = manuals.prompt_manual_download(self.args, self.source)
        self.assertEqual(result['status'], 'saved')
        self.assertEqual((self.dest / 'guide.pdf').read_bytes(), self.payload)

    def test_opt_out(self):
        with patch.dict(os.environ, {'MSSHI_NO_PDF': '1'}):
            self.assertIsNone(manuals.prompt_manual_download(self.args, self.source))
        self.assertFalse(self.dest.exists())

    def test_changed_document_backed_up_identical_not_rewritten(self):
        manuals.save_manual(self.entry, self.dest, self.source)
        target = self.dest / 'guide.pdf'
        target.write_bytes(b'%PDF-private notes')
        result = manuals.save_manual(self.entry, self.dest, self.source)
        self.assertEqual(Path(result['previous_backup']).read_bytes(), b'%PDF-private notes')
        self.assertEqual(manuals.save_manual(self.entry, self.dest, self.source)['status'], 'already_present')

    def test_checksum_and_traversal_rejected(self):
        for entry in ({**self.entry, 'sha256': '0'*64},
                      {**self.entry, 'rel_path': '../private.pdf'},
                      {**self.entry, 'filename': '../guide.pdf'}):
            with self.assertRaises(ValueError): manuals.save_manual(entry, self.dest, self.source)

    def test_version_alias(self):
        self.assertEqual(manuals.resolve_manual(manuals.load_catalog(self.source), '3.1.1')['version'], 'v3.1.1')


if __name__ == '__main__': unittest.main()
