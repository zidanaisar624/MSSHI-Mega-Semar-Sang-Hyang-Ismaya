"""Offline role selection for curated skills, dream planning and voice planning.

Never run dream, model synthesis, external processes, downloads or network calls.
"""
from __future__ import annotations

import ast
import inspect
import io
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import msshi_hermes_profiles as hp
import msshi_integrations as integrations


class IntegrationProfileLayoutTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        for name in ("download",):
            guard = patch.object(integrations, name, side_effect=AssertionError("No network in fixture"))
            guard.start()
            self.addCleanup(guard.stop)
        process = patch.object(integrations.subprocess, "run", side_effect=AssertionError("No processes in fixture"))
        process.start()
        self.addCleanup(process.stop)

    def home(self, layout, *, aliases=False):
        home = self.base / (layout + ("-aliases" if aliases else ""))
        home.mkdir()
        hp.record_team_layout(home, layout)
        expected = {}
        cfg = b"# private configuration\r\nmodel:\r\n  default: keep/model\r\n  provider: keep-provider\r\ndelegation:\r\n  backend: private-advanced\r\n  model: keep/child\r\n"
        (home / "config.yaml").write_bytes(cfg)
        for role, actual in hp.team_role_profiles(home).items():
            if aliases and actual != "default":
                actual = {"shizuka": "shizuka-hiratsuka", "shikaku": "nyenyenye-ya-gw-coder"}.get(actual, actual)
            folder = home if actual == "default" else home / "profiles" / actual
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "SOUL.md").write_text("Private persona " + role, encoding="utf-8")
            (folder / "config.yaml").write_bytes(cfg)
            expected[role] = folder
        return home, expected

    def source_cache(self):
        sources = {}
        for slug in integrations.SOURCE_SPEC:
            folder = self.base / "fixture-sources" / slug
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "LICENSE").write_text("Fixture license", encoding="utf-8")
            sources[slug] = folder
        for source, names in (("caveman", ("caveman",)), ("anthropic-skills", integrations.DOCS),
                              ("hyperframes", integrations.HYPER)):
            for name in names:
                skill = sources[source] / "skills" / name
                skill.mkdir(parents=True)
                (skill / "SKILL.md").write_text(f"---\nname: {name}\ndescription: Fixture\n---\nFixture instructions\n", encoding="utf-8")
        ui = sources["ui-ux-pro-max"]
        for relative, content in ((".claude/skills/ui-ux-pro-max/SKILL.md", "---\nname: ui-ux-pro-max\n---\n# UI/UX Pro Max - Design Intelligence\n"),
                                  ("src/ui-ux-pro-max/templates/base/quick-reference.md", "Fixture quick reference")):
            file = ui / relative
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(content, encoding="utf-8")
        return sources

    def test_actual_default_and_legacy_named_layout_select_all_five_roles(self):
        for layout in ("yukino", "keep-hermes"):
            home, expected = self.home(layout)
            self.assertEqual(dict(integrations.profiles(home)), expected)
            self.assertEqual(dict(integrations.profiles(expected["shikaku"])), expected)
            self.assertEqual(len(expected), 5)
            if layout == "yukino":
                self.assertEqual(expected["yukino"], home)

    def test_legacy_aliases_remain_usable_and_hidden_profiles_are_skipped(self):
        home, expected = self.home("keep-hermes", aliases=True)
        self.assertEqual(dict(integrations.profiles(home)), expected)
        deleted = home / "profiles/.deleted/val"
        deleted.parent.mkdir()
        deleted.write_text("deleted\n", encoding="utf-8")
        self.assertNotIn("val", dict(integrations.profiles(home)))
        self.assertEqual(dict(integrations.profiles(expected["shikaku"]))["shizuka"], expected["shizuka"])

    def test_default_yukino_does_not_select_a_legacy_named_duplicate(self):
        home, expected = self.home("yukino")
        legacy = home / "profiles/yukino"
        legacy.mkdir()
        (legacy / "SOUL.md").write_text("Preserved private legacy persona", encoding="utf-8")
        marker = home / "profiles/.deleted/yukino"
        marker.parent.mkdir()
        marker.write_text("deleted\n", encoding="utf-8")
        self.assertEqual(dict(integrations.profiles(home)), expected)
        self.assertEqual(len(list(integrations.profiles(home))), 5)
        self.assertTrue((legacy / "SOUL.md").is_file())

    def test_cli_named_home_is_normalized_before_voice_status(self):
        home, expected = self.home("keep-hermes")
        with patch.object(integrations, "voice_status", return_value={"fixture": True}) as status, \
             patch("sys.stdout", new_callable=io.StringIO):
            result = integrations.main(["voice", "--home", str(expected["shikaku"]), "--status"])
        self.assertEqual(result, 0)
        status.assert_called_once_with(home)

    def test_curated_skill_plan_targets_yukino_and_four_specialists_in_both_layouts(self):
        sources = self.source_cache()
        for layout in ("yukino", "keep-hermes"):
            home, expected = self.home(layout)
            plan = {}
            def capture(_home, proposed, _label):
                plan.update(proposed)
                return {"changed_files": len(proposed), "rollback_receipt": "fixture-not-applied"}
            with patch.object(integrations, "materialize", side_effect=lambda _home, slug: sources[slug]), \
                 patch.object(integrations, "apply_files", side_effect=capture):
                result = integrations.install(home)
            self.assertEqual(set(result["roles"]), set(expected))
            for role, folder in expected.items():
                self.assertIn(folder / "skills/caveman/SKILL.md", plan, role)
                self.assertIn(folder / "skills/anthropic-pdf/SKILL.md", plan, role)
                self.assertNotIn(folder / "config.yaml", plan)

    def test_voice_configuration_plan_uses_shared_role_homes_without_synthesis(self):
        for layout in ("yukino", "keep-hermes"):
            home, expected = self.home(layout)
            plan = {}
            def capture(_home, proposed, _label):
                plan.update(proposed)
                return {"changed_files": len(proposed), "rollback_receipt": "fixture-not-applied"}
            with patch.object(integrations, "voice_status", return_value={"synthesis_verified": True}), \
                 patch.object(integrations, "apply_files", side_effect=capture):
                result = integrations.voice_enable(home)
            self.assertEqual(result["profiles"], 5)
            for role, folder in expected.items():
                original = (folder / "config.yaml").read_bytes()
                revised = hp.load_yaml_mapping(plan[folder / "config.yaml"])
                self.assertEqual(revised["model"], hp.load_yaml_mapping(original)["model"])
                self.assertEqual(revised["delegation"]["backend"], "private-advanced")
                self.assertIn(f"--role {role}", revised["tts"]["providers"]["omnivoice"]["command"])
                self.assertIn(folder / "skills/msshi-voice-persona/SKILL.md", plan)
                self.assertEqual((folder / "config.yaml").read_bytes(), original)

    def test_dream_reads_the_shared_profile_selector_without_executing_dream(self):
        tree = ast.parse(inspect.getsource(integrations.dream))
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
        self.assertTrue(any(isinstance(call.func, ast.Name) and call.func.id == "profiles" for call in calls))
        for layout in ("yukino", "keep-hermes"):
            home, expected = self.home(layout)
            # Inspect only the same pure selection that the dream loop consumes.
            self.assertEqual(dict(integrations.profiles(home)), expected)
            self.assertFalse((home / "msshi-private/integrations/dream").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
