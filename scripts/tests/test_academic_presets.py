"""Validate portable Academic manifests and their lightweight public resources."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
ROLES = {"yukino", "shizuka", "val", "kiki-chii", "shikaku"}
HEAVY = {"cadcraft", "solidcraft", "materialcraft", "texturecraft", "obs", "strix", "rea-forensics"}


class AcademicPresetManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "configs/academic_presets.json").read_text(encoding="utf-8"))
        cls.policy = json.loads((ROOT / "configs/academic_app_policy.json").read_text(encoding="utf-8"))

    def test_separate_modes_and_new_install_default(self):
        self.assertEqual(self.data["schema_version"], 1)
        self.assertEqual(self.data["default_new_install"], "academic-mahasiswa")
        self.assertEqual(set(self.data["presets"]), {"academic-mahasiswa", "academic-dosen"})
        for preset in self.data["presets"].values():
            self.assertEqual(preset["existing_install_policy"], "explicit-choice-preserve-existing")
            self.assertEqual(preset["model_provider_policy"], "user-configured-preserve-existing")

    def test_every_selected_skill_is_existing_bundle(self):
        for slug, preset in self.data["presets"].items():
            self.assertEqual(set(preset["roles"]), ROLES)
            for role, skills in preset["roles"].items():
                self.assertEqual(len(skills), len(set(skills)), (slug, role))
                self.assertIn("cli-anything-universal-bridge", skills)
                for skill in skills:
                    self.assertTrue((ROOT / "skills" / skill / "SKILL.md").is_file(), (slug, role, skill))

    def test_independent_personas_and_name_contract(self):
        for slug, preset in self.data["presets"].items():
            self.assertEqual(set(preset["persona_files"]), ROLES)
            self.assertEqual(preset["display_names"]["shikaku"], "Sir. Robot")
            for role, value in preset["persona_files"].items():
                self.assertEqual(value, f"configs/personas/{slug}/{role}.md")
                text = (ROOT / value).read_text(encoding="utf-8")
                self.assertNotIn(chr(0), text)
                self.assertIn("MSSHI USER ADDRESS BEGIN", text)
                self.assertIn("MSSHI USER ADDRESS END", text)
                self.assertIn("S1/S2/S3", text)
                self.assertIn("Shizuka", text)

    def test_no_default_heavy_app_routes_or_startup(self):
        self.assertFalse(self.policy["auto_open_on_boot"])
        self.assertTrue(self.policy["require_task_ticket"])
        for group in ("artcraft", "non_artcraft"):
            for routes in self.policy[group].values():
                self.assertFalse(HEAVY.intersection(routes))
        self.assertEqual(set(self.policy["optional_installed_only"]), HEAVY)

    def test_public_manifest_has_no_account_or_model_configuration(self):
        forbidden = {"api_key", "api_keys", "model", "models", "provider", "providers", "base_url", "oauth_client_id", "vault_path"}
        def walk(value):
            if isinstance(value, dict):
                self.assertFalse(forbidden.intersection(value))
                for item in value.values():
                    walk(item)
            elif isinstance(value, list):
                for item in value:
                    walk(item)
        walk(self.data)
        walk(self.policy)

    def test_templates_are_portable_and_include_progress_contract(self):
        folder = ROOT / "templates/academic"
        self.assertEqual(len(list(folder.glob("*.md"))), 5)
        text = (folder / "01_STATUS_RISET_DAN_AKTIVITAS.md").read_text(encoding="utf-8")
        for section in ("1. Sedang Fokus Apa Sekarang", "2. Apa yang Sudah Diselesaikan", "3. Target Selanjutnya"):
            self.assertIn(section, text)
        profile = (folder / "00_PROFIL_AKADEMIK_PENGGUNA.md").read_text(encoding="utf-8")
        self.assertIn("Nama/sapaan pilihan", profile)
        for file in folder.glob("*.md"):
            text = file.read_text(encoding="utf-8")
            self.assertNotIn("vault_path", text)
            self.assertNotIn("buka-np", text)
            self.assertNotIn(chr(0), text)

    def test_unverified_plugins_are_not_claimed_installed(self):
        for preset in self.data["presets"].values():
            for plugin in preset["optional_plugins"]:
                self.assertTrue(plugin["status"].startswith("optional-"))
                self.assertFalse(plugin["auto_install"])
                self.assertTrue(plugin["purpose"])


if __name__ == "__main__":
    unittest.main()
