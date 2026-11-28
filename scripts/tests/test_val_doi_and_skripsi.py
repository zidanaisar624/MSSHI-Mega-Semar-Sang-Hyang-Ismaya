"""Offline unit tests for Val's 2-Layer DOI Research Engine, Searching Paper, and Auto-Template v1.2."""
from __future__ import annotations

import ctypes
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
VAL_SCRIPTS = ROOT / "skills" / "val-doi-research" / "scripts"
TMPL_DIR = ROOT / "skills" / "muza-skripsi-template"
TMPL_SCRIPTS = TMPL_DIR / "scripts"

for _p in reversed((VAL_SCRIPTS, TMPL_SCRIPTS)):
    if _p.is_dir() and str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import doi_engine as de  # noqa: E402
import search_paper_engine as spe  # noqa: E402

try:
    import build_template as bt  # noqa: E402
    from docx import Document  # noqa: E402
    HAS_DOCX = True
except ImportError:  # pragma: no cover
    bt = None
    Document = None
    HAS_DOCX = False


def _stub_fetcher(calls: list[str]):
    def _fn(url: str, headers: dict, timeout: int) -> de.HttpResult:
        calls.append(url)
        if "sci-hub" in url.lower():
            raise AssertionError("Piracy domain must never be contacted!")
        if "api.openalex.org/works/doi:10.1038/nature14539" in url:
            return de.HttpResult(status=200, data={
                "id": "https://openalex.org/W2963403868",
                "doi": "https://doi.org/10.1038/nature14539",
                "display_name": "Deep learning",
                "publication_year": 2015,
                "type": "article",
                "language": "en",
                "cited_by_count": 68000,
                "authorships": [
                    {"author": {"display_name": "Yann LeCun", "orcid": "https://orcid.org/0000-0002-1234-5678"}},
                    {"author": {"display_name": "Yoshua Bengio"}},
                    {"author": {"display_name": "Geoffrey Hinton"}},
                ],
                "primary_location": {"source": {"display_name": "Nature", "issn_l": "0028-0836"}},
                "biblio": {"volume": "521", "issue": "7553", "first_page": "436", "last_page": "444"},
                "open_access": {"is_oa": False, "oa_status": "closed"},
                "abstract_inverted_index": {"Deep": [0], "learning": [1], "achieves": [2], "99.2%": [3], "accuracy.": [4]},
            })
        if "api.openalex.org/works?" in url and "is_oa%3Atrue" in url:
            return de.HttpResult(status=200, data={"results": [{
                "display_name": "Deep learning",
                "authorships": [{"author": {"display_name": "Yann LeCun"}}],
                "best_oa_location": {"pdf_url": "https://hal.science/hal-04206682/document", "version": "submittedVersion"},
            }]})
        if "api.elsevier.com/content/abstract/doi/" in url:
            return de.HttpResult(status=200, headers={"x-ratelimit-remaining": "9997"}, data={
                "abstracts-retrieval-response": {"coredata": {"dc:title": "Deep learning", "citedby-count": "71500"}}
            })
        if "api.elsevier.com/content/article/entitlement/doi/" in url:
            return de.HttpResult(status=200, data={"entitlement-response": {"document-entitlement": {"entitled": "false"}}})
        return de.HttpResult(status=404, error="stubbed")
    return _fn


class ValDoiAndSkripsiTests(unittest.TestCase):
    def test_piracy_guard_green_oa_and_layer2_elsevier_masking(self):
        calls: list[str] = []
        with tempfile.TemporaryDirectory() as tmp:
            cfg = de.load_config(state_dir=tmp, use_cache=False, elsevier_api_key="SECRET_ELS_KEY_12345")
            eng = de.ResearchEngine(cfg, fetcher=_stub_fetcher(calls))
            rec = eng.resolve("http://sci-hub.box/10.1038/nature14539", use_layer2=True)
            self.assertTrue(rec.found)
            self.assertEqual(rec.doi, "10.1038/nature14539")
            self.assertFalse(any("sci-hub" in c.lower() for c in calls))
            self.assertEqual(rec.best_pdf_url, "https://hal.science/hal-04206682/document")
            self.assertEqual(rec.publisher_access["elsevier"]["quota_remaining"], "9997")
            self.assertNotIn("SECRET_ELS_KEY_12345", json.dumps(cfg.masked_status()))

    def test_search_paper_engine_kpts_stemmer_and_bm25_offline(self):
        self.assertEqual(spe.stem_id_light("mengembangkan"), "kembang")
        scores = spe.score_bm25_lite("deteksi berita hoaks indobert", ["Deteksi berita hoaks dengan IndoBERT", "Resep masakan nusantara"])
        self.assertGreater(scores[0], scores[1])

    @unittest.skipUnless(HAS_DOCX, "python-docx not installed in current Python environment")
    def test_four_citation_styles_zero_placeholders_and_docx_injection(self):
        authors = [de.Author(given=f"First{i}", family=f"Last{i}") for i in range(1, 23)]
        rec = de.PaperRecord(query="10.1/x", doi="10.1/x", title="Twenty Two Authors Study", authors=authors, year=2026, venue="Nature", found=True)
        bt_apa = "".join(t for t, _ in bt.format_reference_segments(rec.to_ris_record(), "APA 7th", 1))
        self.assertIn(". . . Last22, F.", bt_apa)
        self.assertNotIn("Last20", bt_apa)
        no_au = {"title": "Standar Akademik Nasional", "year": "2026", "journal": "Kemdiktisaintek", "doi": "10.1/san"}
        for st in ("APA 7th", "IEEE", "Harvard", "Vancouver"):
            s_out = "".join(t for t, _ in bt.format_reference_segments(no_au, st, 1))
            self.assertNotIn("Anonim", s_out)
            self.assertNotIn("Untitled", s_out)

        calls: list[str] = []
        with tempfile.TemporaryDirectory() as tmp:
            cfg = de.load_config(state_dir=tmp, use_cache=False)
            eng = de.ResearchEngine(cfg, fetcher=_stub_fetcher(calls))
            resolved = eng.resolve("10.1038/nature14539")
            b_sum = de.export_bundle([resolved], os.path.join(tmp, "b"), style="APA 7th", make_zip=True, engine=eng)
            spec = json.loads((TMPL_DIR / "assets" / "example_spec.json").read_text(encoding="utf-8"))
            out_docx = os.path.join(tmp, "Test_Skripsi.docx")
            res = bt.build_from_spec(spec, out_docx, muza_zip=b_sum["zip_path"], preset="informatika_ilkom", auto_online=False)
            self.assertEqual(res["bab2_injected"], 1)
            self.assertEqual(res["refs_injected"], 1)
            doc = Document(out_docx)
            txt = "\\n".join(p.text for p in doc.paragraphs)
            self.assertIn("LeCun, Y., Bengio, Y., & Hinton, G.", txt)
            self.assertNotIn("Anonim", txt)

        if os.name == "nt":
            class PMC(ctypes.Structure):
                _fields_ = [("cb", ctypes.c_ulong), ("pf", ctypes.c_ulong), ("pws", ctypes.c_size_t),
                            ("ws", ctypes.c_size_t), ("qpp", ctypes.c_size_t), ("qp", ctypes.c_size_t),
                            ("qnp", ctypes.c_size_t), ("qn", ctypes.c_size_t), ("pfu", ctypes.c_size_t), ("ppfu", ctypes.c_size_t)]
            pmc = PMC(); pmc.cb = ctypes.sizeof(PMC)
            gp = ctypes.windll.kernel32.GetCurrentProcess; gp.restype = ctypes.c_void_p
            gm = ctypes.windll.psapi.GetProcessMemoryInfo
            gm.argtypes = [ctypes.c_void_p, ctypes.POINTER(PMC), ctypes.c_ulong]; gm.restype = ctypes.c_int
            gm(gp(), ctypes.byref(pmc), pmc.cb)
            self.assertLessEqual(pmc.ws / (1024 * 1024), 160.0)


if __name__ == "__main__":
    unittest.main()
