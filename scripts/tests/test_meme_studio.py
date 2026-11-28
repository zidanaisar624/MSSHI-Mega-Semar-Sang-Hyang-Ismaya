"""Offline unit tests for Kiki-Chii's Rp0 Meme Studio Suite & Antigravity Meshy exclusion."""
from __future__ import annotations

import importlib.util
import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "skills" / "meme-studio-suite" / "scripts" / "msshi_meme_studio.py"


def _load_helper():
    spec = importlib.util.spec_from_file_location("msshi_meme_studio", HELPER)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class MemeStudioSuiteTests(unittest.TestCase):
    def test_memegen_escape_and_url_generation_zero_network(self):
        mod = _load_helper()
        self.assertEqual(mod.escape_memegen(""), "_")
        self.assertEqual(mod.escape_memegen("Why - is_this? 100% #1 / \"ok\""), "Why_--_is__this~q_100~p_~h1_~s_''ok''")
        url = mod.build_memegen_url("drake", ["Write docs", "Refactor at 2 AM"])
        self.assertEqual(url, "https://api.memegen.link/images/drake/Write_docs/Refactor_at_2_AM.png")

    def test_offline_templates_and_ab_rating_html(self):
        mod = _load_helper()
        coding = mod.search_templates("programmer")
        self.assertGreaterEqual(len(coding), 5)
        self.assertTrue(any(r["id"] == "vim-exit" for r in coding))
        self.assertEqual(mod.composite_score({"concept": 10, "quality": 10, "meme_fit": 10, "consistency": 10, "speed": 10, "cost": 10}), 10.0)
        with tempfile.TemporaryDirectory() as tmp:
            out_html = Path(tmp) / "ab.html"
            mod.generate_ab_html(
                "Meme Check",
                [{"label": "A", "image": "a.png", "pattern": "Ironic Contrast"}],
                out_html,
            )
            text = out_html.read_text(encoding="utf-8")
            self.assertIn("Rubrik 6 Dimensi", text)
            self.assertIn("Ironic Contrast", text)

    def test_template_count_unicode_url_and_caption_lint(self):
        mod = _load_helper()
        self.assertEqual(len({row["id"] for row in mod.search_templates()}), 28)
        self.assertTrue(mod.search_templates("table-unflip"))
        self.assertIn("caf%C3%A9", mod.build_memegen_url("drake", ["café"]))
        self.assertTrue(mod.caption_lint(["satu dua tiga empat lima enam tujuh"]))
        self.assertFalse(mod.caption_lint(["Revisi selesai"]))

    def test_local_board_paths_and_human_scores(self):
        mod = _load_helper()
        legacy = mod.parse_candidate(r"A:D:\contoh\a.png:Kontras")
        self.assertEqual(legacy["image"], r"D:\contoh\a.png")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image = root / "gambar #1.png"
            image.touch()
            board = root / "hasil" / "pilih.html"
            with redirect_stdout(StringIO()):
                self.assertEqual(mod.main(["ab-rate-html", "--entry", "A:1", str(image), "A & B",
                                           "--output", str(board)]), 0)
            text = board.read_text(encoding="utf-8")
            self.assertIn('src="../gambar%20%231.png"', text)
            self.assertIn("A &amp; B", text)
            self.assertIn("Belum dinilai", text)
            self.assertEqual(text.count("value=''"), 6)
            with self.assertRaises(ValueError):
                mod.local_image_link("https://example.org/meme.png", board)
            with self.assertRaises(ValueError):
                mod.composite_score({"cost": 10})

    def test_kiki_chii_meme_suite_and_antigravity_no_meshy_policy(self):
        matrix = json.loads((ROOT / "configs" / "bot_role_and_skill_matrix.json").read_text(encoding="utf-8-sig"))
        academic = json.loads((ROOT / "configs" / "academic_presets.json").read_text(encoding="utf-8-sig"))

        # Meshy must NOT be in antigravity external_skills (personal API key/tasks paid)
        ag_ext = matrix.get("antigravity", {}).get("external_skills", [])
        self.assertNotIn("meshy-3d-generation", ag_ext)

        # meme-studio-suite belongs to kiki-chii across muza-preset and academic presets
        bots = {b["id"]: b for b in matrix["bots"]}
        self.assertIn("meme-studio-suite", bots["kiki-chii"]["required_skills"])
        for other in ("yukino", "shizuka", "val", "shikaku"):
            self.assertNotIn("meme-studio-suite", bots[other]["required_skills"])
        for preset_id in ("academic-mahasiswa", "academic-dosen"):
            roles = academic["presets"][preset_id]["roles"]
            self.assertIn("meme-studio-suite", roles["kiki-chii"])

        # meme-studio-suite SKILL.md strictly skips Visa CLI, paid Exa, fal.ai, StableUpload
        s_txt = (ROOT / "skills" / "meme-studio-suite" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("SKIP TOTAL", s_txt)


if __name__ == "__main__":
    unittest.main()
