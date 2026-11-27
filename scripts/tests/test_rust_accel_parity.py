"""Verify MSSHI Rust hot-path accelerator bridge, fallback parity, and <=40% ratio guardrail."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import msshi_rust_accel as rust_accel
import msshi_skill_index as skill_index
import msshi_update as update_mod
import secret_scan


class RustAccelParityTests(unittest.TestCase):
    def test_rust_surface_stays_well_under_40_percent_cap(self):
        py_js_files = [
            p
            for p in (ROOT / "scripts").rglob("*")
            if p.is_file()
            and p.suffix.lower() in {".py", ".cjs", ".js"}
            and "tests" not in p.parts
            and "__pycache__" not in p.parts
        ]
        rs_files = list((ROOT / "crates").rglob("*.rs")) if (ROOT / "crates").is_dir() else []
        self.assertGreaterEqual(len(rs_files), 1)
        ratio = len(rs_files) / (len(py_js_files) + len(rs_files))
        self.assertLessEqual(ratio, 0.40, f"Rust module ratio {ratio:.2%} exceeded 40% ceiling")

    def test_python_fallback_works_identically_when_rust_disabled(self):
        prev = os.environ.get("MSSHI_DISABLE_RUST_ACCEL")
        os.environ["MSSHI_DISABLE_RUST_ACCEL"] = "1"
        try:
            self.assertIsNone(rust_accel.resolve_accel_binary())
            with TemporaryDirectory() as tmp:
                base = Path(tmp)
                sdir = base / "skills" / "demo-skill"
                sdir.mkdir(parents=True)
                (sdir / "SKILL.md").write_text(
                    "---\nname: demo-skill\ndescription: Fast demo\n---\n# Demo\n",
                    encoding="utf-8",
                )
                inv = update_mod.inventory(sdir)
                self.assertIn("SKILL.md", inv)
                scan = skill_index.scan_profile_skills(base / "skills", write_cache=False)
                self.assertEqual(scan["skill_count"], 1)
                self.assertEqual(scan["skills"][0]["name"], "demo-skill")
                rep = secret_scan.scan_repository(base, allow_rust=False)
                self.assertEqual(rep["status"], "PASS")
        finally:
            if prev is None:
                os.environ.pop("MSSHI_DISABLE_RUST_ACCEL", None)
            else:
                os.environ["MSSHI_DISABLE_RUST_ACCEL"] = prev

    def test_differential_parity_when_rust_binary_present(self):
        prev = os.environ.pop("MSSHI_DISABLE_RUST_ACCEL", None)
        try:
            binary = rust_accel.resolve_accel_binary()
            if binary is None:
                # Acceptable on machines without Cargo; CI rust-accel.yml runs with binary built
                self.assertTrue((ROOT / "crates" / "msshi-rust-accel" / "Cargo.toml").is_file())
                return
            with TemporaryDirectory() as tmp:
                base = Path(tmp)
                for slug in ("alpha-skill", "beta-skill"):
                    sd = base / "skills" / slug
                    (sd / "references").mkdir(parents=True)
                    (sd / "SKILL.md").write_text(
                        f"---\nname: {slug}\ndescription: Desc for {slug}\n---\n# Body\n",
                        encoding="utf-8",
                    )
                # 1. Inventory parity
                rust_inv = rust_accel.try_inventory(base / "skills")
                os.environ["MSSHI_DISABLE_RUST_ACCEL"] = "1"
                py_inv = update_mod.inventory(base / "skills")
                os.environ.pop("MSSHI_DISABLE_RUST_ACCEL", None)
                self.assertEqual(rust_inv, py_inv)

                # 2. Skill frontmatter scan parity
                os.environ["MSSHI_DISABLE_RUST_ACCEL"] = "1"
                py_scan = skill_index.scan_profile_skills(base / "skills", write_cache=False)
                os.environ.pop("MSSHI_DISABLE_RUST_ACCEL", None)
                rust_scan = skill_index.scan_profile_skills(base / "skills", write_cache=False)
                self.assertEqual(rust_scan["skills"], py_scan["skills"])
                self.assertEqual(rust_scan["excluded_dirs_skipped"], py_scan["excluded_dirs_skipped"])

                # 3. Secret scan parity
                py_sec = secret_scan.scan_repository(base, allow_rust=False)
                rust_sec = rust_accel.try_secret_scan(base)
                self.assertIsNotNone(rust_sec)
                self.assertEqual(rust_sec["status"], py_sec["status"])
                self.assertEqual(rust_sec["findings_count"], py_sec["findings_count"])
        finally:
            if prev is not None:
                os.environ["MSSHI_DISABLE_RUST_ACCEL"] = prev


if __name__ == "__main__":
    unittest.main()
