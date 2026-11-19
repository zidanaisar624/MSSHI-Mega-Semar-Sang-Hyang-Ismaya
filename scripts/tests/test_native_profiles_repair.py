"""Offline fixtures: native identities, safe receipts, role transport and plugin routing.
No test starts Hermes, a server, a desktop app or a model turn.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import msshi_hermes_profiles as hp
import install_msshi

NAMES = ("yukino", "shizuka", "val", "kiki-chii", "shikaku")


class NativeProfilesRepairTests(unittest.TestCase):
    def setUp(self):
        self.pdf_env = patch.dict(os.environ, {"MSSHI_NO_PDF": "1"})
        self.pdf_env.start()
        self.addCleanup(self.pdf_env.stop)
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / "HermesData"
        self.home.mkdir()
        self.root_cfg = b"# user comment\r\nmodel:\r\n  default: current/root\r\n  provider: databyte\r\nproviders:\r\n  databyte:\r\n    base_url: https://example.invalid/v1\r\n"
        (self.home / "config.yaml").write_bytes(self.root_cfg)
        (self.home / "SOUL.md").write_bytes(b"Neutral Hermes custom soul\r\n")
        (self.home / ".env").write_bytes(b"PRIVATE_API_KEY=fixture-only\nHERMES_HOME=wrong\nTELEGRAM_BOT_TOKEN=do-not-copy\n")

    def existing(self, name, *, deleted=False):
        folder = self.home / "profiles" / name
        folder.mkdir(parents=True)
        (folder / "config.yaml").write_bytes((f"# exact {name}\r\nmodel:\r\n  default: current/{name}\r\n  provider: databyte\r\ndelegation:\r\n  model: child/{name}\r\n  provider: existing\r\n  reasoning_effort: high\r\n").encode())
        (folder / "SOUL.md").write_bytes((f"My custom {name} soul\r\n").encode())
        (folder / ".env").write_bytes((f"# custom empty secret placeholder {name}\r\n").encode())
        (folder / "AGENTS.md").write_bytes(b"\xef\xbb\xbf# My policy\r\nPreserve custom bytes.\r\n")
        (folder / "profile.yaml").write_text(hp.dump_yaml({"display_name": "Sir. Robot" if name == "shikaku" else name.title(),
            "ui_meta": {"hermes-bots": {"title": "Sir. Robot" if name == "shikaku" else name.title(), "sectionId": "mine", "image": "keep.png"}},
            "_ui_meta_revisions": {"hermes-bots": 7}}), encoding="utf-8")
        if deleted:
            marker = folder.parent / ".deleted" / name
            marker.parent.mkdir(exist_ok=True)
            marker.write_bytes(b"original tombstone\r\n")
        return folder

    def sync(self, name, tx=None, copies=None, copy_fn=None):
        return hp.sync_hermes_profile(self.home, name, name.title(), "New template never overwrite", "Initial guidance",
            copies or [], transaction=tx, copy_fn=copy_fn)

    def test_five_named_preserve_existing_identity_and_current_routes(self):
        originals = {}
        for name in NAMES:
            folder = self.existing(name, deleted=name == "yukino")
            originals[name] = {file: (folder / file).read_bytes() for file in ("SOUL.md", "config.yaml", ".env")}
        other = self.home / "profiles/.deleted/unselected"
        other.write_bytes(b"not selected")
        root_soul = (self.home / "SOUL.md").read_bytes()
        for name in NAMES:
            self.sync(name)
        self.assertEqual(set(hp.live_named_profiles(self.home)), set(NAMES))
        self.assertTrue(other.exists())
        self.assertEqual((self.home / "config.yaml").read_bytes(), self.root_cfg)
        self.assertEqual((self.home / "SOUL.md").read_bytes(), root_soul)
        for name in NAMES:
            for file, content in originals[name].items():
                self.assertEqual((self.home / "profiles" / name / file).read_bytes(), content)
        coder_meta = hp.load_yaml_mapping(self.home / "profiles/shikaku/profile.yaml")
        self.assertEqual(coder_meta["display_name"], "Sir. Robot")
        self.assertEqual(coder_meta["ui_meta"]["hermes-bots"]["image"], "keep.png")

    def test_explicit_neutral_metadata_restore_and_rollback(self):
        folder = self.existing("yukino", deleted=True)
        root_meta = {"display_name": "Yukino Yukinoshita", "description": "Yukino ideation", "ui_meta": {"hermes-bots":
            {"title": "Yukino Yukinoshita", "sectionId": "custom", "image": "my-image.png"}}, "_ui_meta_revisions": {"hermes-bots": 12}}
        meta = self.home / "profile.yaml"
        meta.write_text(hp.dump_yaml(root_meta), encoding="utf-8")
        before = meta.read_bytes()
        original_agents = (folder / "AGENTS.md").read_bytes()
        marker = folder.parent / ".deleted/yukino"
        tx = hp.ProfileTransaction(self.home)
        hp.restore_neutral_default(self.home, transaction=tx)
        self.sync("yukino", tx)
        receipt = tx.commit()
        after = hp.load_yaml_mapping(meta)
        self.assertEqual(after["display_name"], "Hermes")
        self.assertEqual(after["ui_meta"]["hermes-bots"]["title"], "Hermes")
        self.assertEqual(after["ui_meta"]["hermes-bots"]["sectionId"], "custom")
        self.assertEqual(after["_ui_meta_revisions"]["hermes-bots"], 13)
        result = hp.rollback_profile_receipt(Path(receipt), expected_home=self.home)
        self.assertEqual(result["conflicts"], [])
        self.assertEqual(meta.read_bytes(), before)
        self.assertEqual((folder / "AGENTS.md").read_bytes(), original_agents)
        self.assertEqual(marker.read_bytes(), b"original tombstone\r\n")

    def test_idempotent_custom_context_and_no_credit_calls(self):
        folder = self.existing("yukino")
        prefix = (folder / "AGENTS.md").read_bytes()
        with patch.object(hp.subprocess, "run") as process:
            first = self.sync("yukino")
            second = self.sync("yukino")
            process.assert_not_called()
        self.assertTrue(first["receipt"])
        self.assertIsNone(second["receipt"])
        data = (folder / "AGENTS.md").read_bytes()
        self.assertTrue(data.startswith(prefix))
        self.assertEqual(data.count(hp._POLICY_START.encode()), 1)
        self.assertIn(b"I don't need to do anything here.", data)

    def test_new_profile_seed_is_current_root_only_and_rollback_quarantines(self):
        result = self.sync("val")
        folder = self.home / "profiles/val"
        config = hp.load_yaml_mapping(folder / "config.yaml")
        self.assertEqual(config["model"]["default"], "current/root")
        self.assertEqual(config["model"]["provider"], "databyte")
        env = (folder / ".env").read_text()
        self.assertNotIn("PRIVATE_API_KEY=fixture-only", env)
        self.assertNotIn("HERMES_HOME", env)
        self.assertNotIn("TELEGRAM_", env)
        result = hp.rollback_profile_receipt(Path(result["receipt"]))
        self.assertEqual(result["conflicts"], [])
        self.assertFalse(folder.exists())
        self.assertTrue((Path(result["receipt"]).parent / "quarantine").is_dir())

    def test_rollback_does_not_overwrite_later_user_edit(self):
        folder = self.existing("yukino")
        result = self.sync("yukino")
        agents = folder / "AGENTS.md"
        agents.write_bytes(agents.read_bytes() + b"\nNew user note")
        rollback = hp.rollback_profile_receipt(Path(result["receipt"]))
        self.assertIn(str(agents), rollback["conflicts"])
        self.assertTrue(agents.read_bytes().endswith(b"New user note"))

    def test_failed_partial_copy_rolls_back_existing_metadata_and_new_tree(self):
        folder = self.existing("val")
        before = (folder / "AGENTS.md").read_bytes()
        src = self.home / "fixture-src"
        src.mkdir()
        def fail(source, target):
            target.mkdir(parents=True)
            (target / "partial").write_text("partial")
            raise OSError("fixture interrupted copy")
        with self.assertRaises(OSError):
            self.sync("val", copies=[(src, folder / "skills/fixture")], copy_fn=fail)
        self.assertEqual((folder / "AGENTS.md").read_bytes(), before)
        self.assertFalse((folder / "skills/fixture").exists())

    def test_native_target_validation_with_mock_transport(self):
        self.existing("yukino")
        val = self.existing("val")
        coder = self.existing("shikaku", deleted=True)
        calls = []
        def mock_message(target, message):
            path = hp.validate_named_profile_target(self.home, "yukino", target)
            calls.append((path.name, message))
            return {"status": "queued", "api_calls": 0}
        self.assertEqual(mock_message("val", "Need cited evidence")["api_calls"], 0)
        self.assertEqual(calls, [(val.name, "Need cited evidence")])
        for invalid in ("shikaku", "missing", "yukino"):
            with self.assertRaises(ValueError):
                mock_message(invalid, "no dispatch")
        self.assertEqual(len(calls), 1)

    def test_default_mapping_preserves_custom_soul_config_and_preview_has_zero_writes(self):
        target = self.home / "profiles"
        with contextlib.redirect_stdout(io.StringIO()), patch.dict(os.environ, {"MSSHI_IGNORE_REGISTRY_HERMES_HOME": "1"}):
            result = install_msshi.main(["--platform", "hermes", "--mode", "muza-preset", "--target-dir", str(target), "--dry-run"])
        self.assertEqual(result, 0)
        self.assertFalse(target.exists())
        self.assertEqual((self.home / "config.yaml").read_bytes(), self.root_cfg)
        original_soul = (self.home / "SOUL.md").read_bytes()
        result = hp.sync_hermes_profile(self.home, "yukino", "Yukino", "soul", "agents", [], as_default=True)
        self.assertTrue(result["custom_soul_preserved"])
        self.assertEqual(result["bot_id"], "default")
        self.assertEqual((self.home / "config.yaml").read_bytes(), self.root_cfg)
        self.assertEqual((self.home / "SOUL.md").read_bytes(), original_soul)

    def test_auto_layout_fresh_existing_and_receipted_alias_switch(self):
        self.assertEqual(hp.resolve_default_bot(self.home), "keep-hermes")
        fresh = self.home / "isolated-new-home"
        self.assertEqual(hp.resolve_default_bot(fresh), "yukino")
        legacy = self.existing("yukino")
        (legacy / "state.db").write_bytes(b"history sentinel")
        (self.home / "active_profile").write_bytes(b"yukino\n")
        tx = hp.ProfileTransaction(self.home)
        hp.record_team_layout(self.home, "yukino", transaction=tx)
        hp.hide_legacy_named_yukino(self.home, transaction=tx)
        receipt = tx.commit()
        self.assertEqual(hp.team_role_profiles(self.home)["yukino"], "default")
        self.assertEqual(hp.resolve_default_bot(self.home), "yukino")
        self.assertNotIn("yukino", hp.live_named_profiles(self.home))
        self.assertEqual((legacy / "state.db").read_bytes(), b"history sentinel")
        self.assertEqual((self.home / "active_profile").read_bytes(), b"default\n")
        self.assertEqual(hp.rollback_profile_receipt(Path(receipt))["conflicts"], [])
        self.assertIn("yukino", hp.live_named_profiles(self.home))
        self.assertEqual((self.home / "active_profile").read_bytes(), b"yukino\n")

    def test_stock_root_becomes_yukino_without_moving_any_model_and_rolls_back(self):
        stock = hp.STOCK_HERMES_SOUL + "\n"
        (self.home / "SOUL.md").write_text(stock, encoding="utf-8")
        self.assertEqual(hp.resolve_default_bot(self.home), "yukino")
        result = hp.sync_hermes_profile(self.home, "yukino", "Yukino", "Yukino template", "policy", [], as_default=True)
        self.assertTrue(result["stock_soul_replaced"])
        self.assertEqual((self.home / "SOUL.md").read_text(), "Yukino template\n")
        self.assertEqual((self.home / "config.yaml").read_bytes(), self.root_cfg)
        self.assertFalse((self.home / "profiles/yukino").exists())
        self.assertEqual(hp.rollback_profile_receipt(Path(result["receipt"]))["conflicts"], [])
        self.assertEqual((self.home / "SOUL.md").read_text(encoding="utf-8"), stock)

    def test_stock_prefix_is_not_permission_to_replace_custom_persona(self):
        soul = hp.STOCK_HERMES_SOUL + "\nMy own added rule.\n"
        (self.home / "SOUL.md").write_text(soul, encoding="utf-8")
        self.assertFalse(hp.is_stock_hermes_soul(self.home / "SOUL.md"))
        self.assertEqual(hp.resolve_default_bot(self.home), "keep-hermes")

    def test_pre_hermes_five_real_bots_activate_when_user_adds_config(self):
        fresh = self.home / "fresh-isolated"
        tx = hp.ProfileTransaction(fresh)
        for name in NAMES:
            hp.sync_hermes_profile(fresh, name, name, f"Public {name}", "policy", [],
                                  as_default=name == "yukino", transaction=tx)
        hp.record_team_layout(fresh, "yukino", transaction=tx)
        hp.install_team_routing_plugin(fresh, ROOT, transaction=tx)
        tx.commit()
        self.assertEqual(set(hp.live_named_profiles(fresh)), set(NAMES) - {"yukino"})
        self.assertFalse((fresh / "config.yaml").exists())
        user_config = b"# current user route\r\nmodel:\r\n  default: chosen/model\r\n  provider: chosen-provider\r\ndelegation:\r\n  model: chosen/child\r\n  provider: chosen-child-provider\r\n"
        (fresh / "config.yaml").write_bytes(user_config)
        result = hp.sync_pending_profile_configs(fresh)
        self.assertEqual(set(result["seeded_configs"]), set(NAMES) - {"yukino"})
        self.assertEqual(set(result["team_routing"]), {"default", "shizuka", "val", "kiki-chii", "shikaku"})
        for profile, row in result["team_routing"].items():
            self.assertTrue(row["active"], profile)
            pdir = fresh if profile == "default" else fresh / "profiles" / profile
            cfg = hp.load_yaml_mapping(pdir / "config.yaml")
            self.assertEqual(cfg["model"], {"default": "chosen/model", "provider": "chosen-provider"})
            self.assertEqual(cfg["delegation"]["backend"], "msshi-team")
        root_cfg = hp.load_yaml_mapping(fresh / "config.yaml")
        self.assertEqual(root_cfg["delegation"]["model"], "chosen/child")
        self.assertEqual(root_cfg["delegation"]["provider"], "chosen-child-provider")
        self.assertIn(b"# current user route\r\nmodel:\r\n  default: chosen/model", (fresh / "config.yaml").read_bytes())
        self.assertIsNone(hp.sync_pending_profile_configs(fresh)["team_routing_receipt"])

    def test_plugin_activation_preserves_primary_and_custom_backend_values(self):
        folder = self.existing("shikaku")
        cfg = folder / "config.yaml"
        with cfg.open("ab") as handle:
            handle.write(b"plugins:\n  enabled: [existing-plugin]\n")
        old = hp.load_yaml_mapping(cfg)
        result = hp.install_team_routing_plugin(self.home, ROOT)
        new = hp.load_yaml_mapping(cfg)
        self.assertEqual(new["model"], old["model"])
        self.assertEqual(new["delegation"]["model"], old["delegation"]["model"])
        self.assertEqual(new["delegation"]["provider"], old["delegation"]["provider"])
        self.assertEqual(new["delegation"]["backend"], "msshi-team")
        self.assertEqual(new["plugins"]["enabled"], ["existing-plugin", "msshi-team-routing"])
        self.assertIn(b"# exact shikaku\r\nmodel:\r\n  default: current/shikaku", cfg.read_bytes())
        self.assertTrue(result["new_session_prompt_required"])
        self.assertEqual(hp.install_team_routing_plugin(self.home, ROOT)["receipt"], None)
        hp.rollback_profile_receipt(Path(result["receipt"]))
        self.assertEqual(hp.load_yaml_mapping(cfg), old)
        # An advanced user backend is retained exactly, while the prompt plugin may load.
        custom = dict(old)
        custom["delegation"]["backend"] = "my-custom"
        cfg.write_text(hp.dump_yaml(custom), encoding="utf-8")
        result = hp.install_team_routing_plugin(self.home, ROOT)
        self.assertEqual(hp.load_yaml_mapping(cfg)["delegation"]["backend"], "my-custom")
        self.assertEqual(result["profiles"]["shikaku"]["backend"], "custom_backend_preserved")

    def test_explicit_default_backend_is_preserved_across_repeated_sync(self):
        for name in ('shizuka', 'val'):
            folder = self.existing(name)
            config = hp.load_yaml_mapping(folder / 'config.yaml')
            config['delegation']['backend'] = 'default'
            config['plugins'] = {'enabled': ['advanced-delegation'] if name == 'shizuka' else []}
            (folder / 'config.yaml').write_text(hp.dump_yaml(config), encoding='utf-8')
            before = config['delegation'].copy()
            first = hp.install_team_routing_plugin(self.home, ROOT)
            self.assertEqual(hp.load_yaml_mapping(folder / 'config.yaml')['delegation'], before)
            self.assertFalse(first['profiles'][name]['named_profile_delegate_backend_selected'])
            hp.sync_pending_profile_configs(self.home)
            self.assertEqual(hp.load_yaml_mapping(folder / 'config.yaml')['delegation'], before)
            if name == 'shizuka':
                self.assertIn('advanced-delegation', hp.load_yaml_mapping(folder / 'config.yaml')['plugins']['enabled'])


class TeamRoutingPluginTests(unittest.TestCase):
    def setUp(self):
        self.pdf_env = patch.dict(os.environ, {"MSSHI_NO_PDF": "1"})
        self.pdf_env.start()
        self.addCleanup(self.pdf_env.stop)
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        for name in NAMES:
            path = self.home / "profiles" / name
            path.mkdir(parents=True)
            (path / "SOUL.md").write_text(name)
        provider_module = types.ModuleType("agent.delegation_provider")
        provider_module.DelegationProvider = type("DelegationProvider", (), {})
        provider_module.DelegationRouteError = type("DelegationRouteError", (ValueError,), {})
        constants = types.ModuleType("hermes_constants")
        constants.get_default_hermes_root = lambda: self.home
        constants.get_hermes_home = lambda: self.home / "profiles/yukino"
        constants.named_profile_is_live = lambda path: path.is_dir() and (path / "SOUL.md").is_file() and not (path.parent / ".deleted" / path.name).exists()
        self.constants = constants
        self.modules = patch.dict(sys.modules, {"agent.delegation_provider": provider_module, "hermes_constants": constants})
        self.modules.start()
        self.addCleanup(self.modules.stop)
        spec = importlib.util.spec_from_file_location("fixture_msshi_team", ROOT / "hermes_plugins/msshi-team-routing/__init__.py")
        self.plugin = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.plugin)

    def test_registration_schema_route_and_deleted_target_rejection(self):
        registrations = {}
        class Context:
            def register_delegation_provider(self, provider): registrations["provider"] = provider
            def register_system_prompt_section(self, name, callback, **kwargs): registrations["prompt"] = callback
        self.plugin.register(Context())
        backend = registrations["provider"]
        self.assertEqual(backend.name, "msshi-team")
        schema = backend.task_parameters({})
        self.assertNotIn("yukino", schema["profile"]["enum"])
        self.assertEqual(backend.route_task({"profile": "val"}, {}), {"profile": "val", "label": "MSSHI val"})
        existing = {"model": "do-not-change", "provider": "private-provider", "reasoning_effort": "high", "fallback_providers": ["keep"], "service_tier": "fast"}
        self.assertEqual(backend.route_task({}, existing), {key: value for key, value in existing.items() if key != "service_tier"})
        marker = self.home / "profiles/.deleted/val"
        marker.parent.mkdir()
        marker.write_text("deleted")
        with self.assertRaises(ValueError):
            backend.route_task({"profile": "val"}, existing)
        prompt = registrations["prompt"]({"profile_name": "yukino"})
        self.assertIn("delegate only needed portions", prompt)
        self.assertIn("I don't need to do anything here.", prompt)
        self.assertIn("neutral general assistant", registrations["prompt"]({"profile_name": "default"}))
        neutral = registrations["prompt"]({"profile_name": "default"})
        self.assertIn("hand off only relevant bounded portions", neutral)
        self.assertIn("message_agent", neutral)
        self.assertIn("credit-consuming", neutral)

    def test_kat_disabled_for_non_coder_and_requires_private_validated_model(self):
        private = self.home / "msshi-private/coder/kat.json"
        private.parent.mkdir(parents=True)
        data = {"schema": 1, "enabled": True, "profile": "shikaku", "provider": "custom", "model": "kat-allowed", "base_url": "https://example.invalid/v1", "api_key_env": "FIXTURE_KAT_KEY", "validated_model_catalog": ["kat-allowed"]}
        private.write_text(json.dumps(data))
        with patch.dict(os.environ, {"FIXTURE_KAT_KEY": "fixture-only"}):
            self.assertNotIn("execution", self.plugin.MSSHITeamRouting().task_parameters({}))
            self.constants.get_hermes_home = lambda: self.home / "profiles/shikaku"
            backend = self.plugin.MSSHITeamRouting()
            self.assertIn("execution", backend.task_parameters({}))
            route = backend.route_task({"execution": "kat"}, {})
            self.assertEqual(route["model"], "kat-allowed")
            self.assertNotIn("profile", route)
            with self.assertRaises(ValueError):
                backend.route_task({"profile": "val", "execution": "kat"}, {})
            data["validated_model_catalog"] = []
            private.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                backend.route_task({"execution": "kat"}, {})

    def test_default_yukino_schema_routes_both_ways_and_preserves_legacy_layout(self):
        hp.record_team_layout(self.home, "yukino")
        self.constants.get_hermes_home = lambda: self.home
        root_backend = self.plugin.MSSHITeamRouting()
        self.assertEqual(set(root_backend.task_parameters({})["profile"]["enum"]), set(NAMES) - {"yukino"})
        self.assertIn("native role yukino (actual profile default)", self.plugin.role_policy({"profile_name": "default"}))
        self.constants.get_hermes_home = lambda: self.home / "profiles/val"
        val_backend = self.plugin.MSSHITeamRouting()
        self.assertIn("default", val_backend.task_parameters({})["profile"]["enum"])
        self.assertNotIn("yukino", val_backend.task_parameters({})["profile"]["enum"])
        self.assertEqual(val_backend.route_task({"profile": "default"}, {}), {"profile": "default", "label": "MSSHI default"})
        with self.assertRaises(ValueError):
            val_backend.route_task({"profile": "yukino"}, {})
        hp.record_team_layout(self.home, "keep-hermes")
        self.assertIn("yukino", val_backend.task_parameters({})["profile"]["enum"])
        self.assertNotIn("default", val_backend.task_parameters({})["profile"]["enum"])

    def test_every_role_routes_only_to_other_real_teammates_in_each_layout(self):
        for layout in ("yukino", "keep-hermes"):
            hp.record_team_layout(self.home, layout)
            actual_roles = hp.team_role_profiles(self.home)
            for actual in actual_roles.values():
                self.constants.get_hermes_home = lambda active=actual: self.home if active == "default" else self.home / "profiles" / active
                backend = self.plugin.MSSHITeamRouting()
                offered = backend.task_parameters({})["profile"]["enum"]
                self.assertEqual(set(offered), set(actual_roles.values()) - {actual})
                for target in offered:
                    self.assertEqual(backend.route_task({"profile": target}, {})["profile"], target)
                with self.assertRaises(ValueError):
                    backend.route_task({"profile": actual}, {})
                self.assertLess(len(self.plugin.role_policy({"profile_name": actual})), 2600)

    def test_kat_private_coder_env_fallback_does_not_modify_process(self):
        self.constants.get_hermes_home = lambda: self.home / "profiles/shikaku"
        # A provider registered before setup must pick up readiness on a NEW schema build.
        backend = self.plugin.MSSHITeamRouting()
        self.assertNotIn("execution", backend.task_parameters({}))
        private = self.home / "msshi-private/coder/kat.json"
        private.parent.mkdir(parents=True)
        private.write_text(json.dumps({"schema": 1, "enabled": True, "profile": "shikaku", "provider": "custom",
            "model": "kat-private", "base_url": "https://example.invalid/v1", "api_key_env": "FIXTURE_PRIVATE_KAT",
            "validated_model_catalog": ["kat-private"]}))
        (self.home / "profiles/shikaku/.env").write_text('FIXTURE_PRIVATE_KAT="fixture-only"\nOTHER_SECRET=ignore\n')
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("FIXTURE_PRIVATE_KAT", None)
            self.assertIn("execution", backend.task_parameters({}))
            route = backend.route_task({"execution": "kat"}, {})
            self.assertEqual(route["api_key"], "fixture-only")
            self.assertNotIn("FIXTURE_PRIVATE_KAT", os.environ)
            self.assertNotIn("OTHER_SECRET", os.environ)


if __name__ == "__main__":
    unittest.main(verbosity=2)
