"""Unit and end-to-end tests for adaptive Hermes profile auto-provisioning (before, during, and after Hermes)."""
from __future__ import annotations

import builtins
import io
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import install_msshi  # noqa: E402
import msshi_browser_policy  # noqa: E402
import msshi_cli  # noqa: E402
import msshi_hermes_profiles as hermes_profiles  # noqa: E402
import msshi_runtime  # noqa: E402
import msshi_service_connections  # noqa: E402


class HermesProfileSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        # Integration fixtures never deliver to real Downloads or ask for endpoint secrets.
        no_pdf = patch.dict(os.environ, {"MSSHI_NO_PDF": "1"})
        no_pdf.start()
        self.addCleanup(no_pdf.stop)
        def offline_kat_wizard(home, mode="cloud", **_):
            from msshi_coder_helpers import configure, status
            if not (home / "profiles/shikaku/config.yaml").is_file():
                return status(home)  # Pre-Hermes setup defers private endpoint configuration.
            return configure(home, probe=False, activate=False)
        wizard = patch("msshi_coder_helpers.wizard", side_effect=offline_kat_wizard)
        wizard.start()
        self.addCleanup(wizard.stop)
    def test_pure_python_yaml_roundtrip_without_pyyaml(self) -> None:
        sample = (
            "model:\n"
            "  default: upstage/solar-mini4:free\n"
            "  provider: \"custom:my-local\"\n"
            "  base_url: https://inference-api.nousresearch.com/v1\n"
            "providers:\n"
            "  nous:\n"
            "    api_mode: chat_completions\n"
            "custom_providers:\n"
            "  - name: My Local\n"
            "    base_url: http://127.0.0.1:8080/v1\n"
            "gateway:\n"
            "  multiplex_profiles: true\n"
        )
        real_import = builtins.__import__

        def block_yaml(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "yaml" or name.startswith("ruamel"):
                raise ImportError(name)
            return real_import(name, globals, locals, fromlist, level)

        with patch("builtins.__import__", side_effect=block_yaml):
            parsed = hermes_profiles.load_yaml_mapping(sample)
            seed = hermes_profiles.launch_model_seed(parsed)
            dumped = hermes_profiles.dump_yaml(seed)
            reparsed = hermes_profiles.load_yaml_mapping(dumped)

        self.assertEqual(seed["model"]["default"], "upstage/solar-mini4:free")
        self.assertNotIn("gateway", seed)
        self.assertEqual(len(seed.get("custom_providers", [])), 1)
        self.assertEqual(reparsed["model"]["base_url"], "https://inference-api.nousresearch.com/v1")

    def test_adaptive_c_vs_d_resolution(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            local = root / "localappdata"
            user = root / "userhome"
            d_drive = root / "drive_d"
            d_drive.mkdir()
            env_with_d = {
                "LOCALAPPDATA": str(local),
                "USERPROFILE": str(user),
                "HOME": str(user),
                "MSSHI_IGNORE_REGISTRY_HERMES_HOME": "1",
                "MSSHI_WINDOWS_D_DRIVE": str(d_drive),
            }
            resolved_d = hermes_profiles.resolve_hermes_home(env=env_with_d)
            if os.name == "nt":
                self.assertEqual(resolved_d, (d_drive / "HermesData").absolute())

            env_c_only = {
                "LOCALAPPDATA": str(local),
                "USERPROFILE": str(user),
                "HOME": str(user),
                "MSSHI_IGNORE_REGISTRY_HERMES_HOME": "1",
                "MSSHI_WINDOWS_D_DRIVE": "",
            }
            resolved_c = hermes_profiles.resolve_hermes_home(env=env_c_only)
            expected_c = (local / "hermes").absolute() if os.name == "nt" else (user / ".hermes").absolute()
            self.assertEqual(resolved_c, expected_c)

    def test_before_during_and_after_hermes_flows(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            msshi_home = root / "msshi-data"
            hermes_home = root / "hermes-home"
            msshi_home.mkdir()

            base_env = {
                "MSSHI_HOME": str(msshi_home),
                "HERMES_HOME": str(hermes_home),
                "MSSHI_IGNORE_REGISTRY_HERMES_HOME": "1",
            }

            # 1. BEFORE Hermes is opened/initialized (no config.yaml / .env yet)
            # Fresh MuZA uses the real default as Yukino plus four named specialists.
            with patch.dict(os.environ, base_env, clear=False), patch("sys.stdout", new_callable=io.StringIO):
                code = msshi_cli.main(["setup", "--mode", "muza-preset", "--platform", "hermes", "--yes"])
            self.assertEqual(code, 0)

            self.assertFalse((hermes_home / "profiles" / "yukino").exists())
            yukino_meta = hermes_profiles.load_yaml_mapping(hermes_home / "profile.yaml")
            self.assertEqual(yukino_meta["display_name"], "Yukino Yukinoshita")
            self.assertTrue((hermes_home / "SOUL.md").exists())
            self.assertTrue((hermes_home / ".no-bundled-skills").exists())
            self.assertTrue((hermes_home / "skills/cli-anything-universal-bridge/SKILL.md").is_file())
            self.assertFalse((hermes_home / "config.yaml").exists())

            for bot_id in ("yukino", "shizuka", "val", "kiki-chii", "shikaku"):
                pdir = hermes_home if bot_id == "yukino" else hermes_home / "profiles" / bot_id
                self.assertTrue((pdir / "profile.yaml").is_file(), f"Missing profile.yaml for {bot_id}")
                self.assertTrue((pdir / "SOUL.md").is_file(), f"Missing SOUL.md for {bot_id}")
                self.assertTrue((pdir / "AGENTS.md").is_file(), f"Missing AGENTS.md for {bot_id}")
                self.assertTrue((pdir / ".no-bundled-skills").is_file())
                self.assertTrue((pdir / "memories").is_dir())
                self.assertTrue((pdir / "sessions").is_dir())
                self.assertTrue((pdir / "skills" / "cli-anything-universal-bridge" / "SKILL.md").is_file())
                self.assertFalse((pdir / "config.yaml").exists())

            self.assertTrue((hermes_home / "msshi-runtime" / "pending-bots.json").is_file())

            # Now simulate user opening Hermes later and configuring their model + .env (with channel secrets)
            default_cfg_text = (
                "model:\n"
                "  default: upstage/solar-mini4:free\n"
                "  provider: nous\n"
                "providers:\n"
                "  nous:\n"
                "    api_mode: chat_completions\n"
                "gateway:\n"
                "  multiplex_profiles: true\n"
            )
            default_cfg = hermes_home / "config.yaml"
            default_cfg.write_text(default_cfg_text, encoding="utf-8")
            (hermes_home / ".env").write_text(
                "OPENROUTER_API_KEY=sk-test-keep\n"
                "TELEGRAM_BOT_TOKEN=secret-tg-strip\n"
                "DISCORD_BOT_TOKEN=secret-dc-strip\n"
                "EMAIL_PASSWORD=secret-mail-strip\n",
                encoding="utf-8",
            )

            # User deletes 'val' in Hermes before migrating: backfill MUST respect .deleted tombstone!
            deleted_dir = hermes_home / "profiles" / ".deleted"
            deleted_dir.mkdir(parents=True, exist_ok=True)
            (deleted_dir / "val").write_text("", encoding="utf-8")

            with patch.dict(os.environ, base_env, clear=False), patch("sys.stdout", new_callable=io.StringIO):
                rc = msshi_cli.migrate_runtime(ROOT, hermes_home)
            self.assertEqual(rc, 0)

            default_after = hermes_profiles.load_yaml_mapping(default_cfg)
            self.assertEqual(default_after["model"]["default"], "upstage/solar-mini4:free")
            self.assertEqual(default_after["model"]["provider"], "nous")
            self.assertEqual(default_after["providers"]["nous"]["api_mode"], "chat_completions")
            self.assertTrue((hermes_home / "msshi-runtime" / "last-migration.json").is_file())
            self.assertFalse((hermes_home / "profiles" / "val" / "config.yaml").exists())

            for bot_id in ("shizuka", "kiki-chii", "shikaku"):
                pdir = hermes_home / "profiles" / bot_id
                cfg = hermes_profiles.load_yaml_mapping(pdir / "config.yaml")
                self.assertEqual(cfg.get("model", {}).get("default"), "upstage/solar-mini4:free")
                self.assertIn("providers", cfg)
                self.assertNotIn("gateway", cfg)
                env_text = (pdir / ".env").read_text(encoding="utf-8")
                # Existing per-profile .env bytes are preserved, even for a user placeholder.
                self.assertEqual(env_text, hermes_profiles._PLACEHOLDER_ENV)
                self.assertNotIn("TELEGRAM_BOT_TOKEN", env_text)
                self.assertNotIn("DISCORD_BOT_TOKEN", env_text)
                self.assertNotIn("EMAIL_PASSWORD", env_text)

            # 2. WHILE Hermes is open + AFTER Hermes opened:
            # Custom bot config & live state.db must stay untouched, while interactive custom display_name ("Sir. Robot") applies.
            shikaku_cfg = hermes_home / "profiles" / "shikaku" / "config.yaml"
            custom_cfg_text = "model:\n  default: custom/already-chosen\n  provider: openai\n"
            shikaku_cfg.write_text(custom_cfg_text, encoding="utf-8")
            shikaku_db = hermes_home / "profiles" / "shikaku" / "state.db"
            shikaku_db.write_bytes(b"SQLite format 3\x00sentinel")
            shikaku_soul = hermes_home / "profiles" / "shikaku" / "SOUL.md"
            shikaku_soul.write_text("# Custom User Soul\n", encoding="utf-8")

            # Clear stale tombstone by running setup again (user explicitly reinstalling MuZA team)
            interactive_inputs = "\n".join([
                "4",          # mode: muza-preset
                "hermes",     # platform
                "",           # default <hermes_home>\profiles
                "y",          # custom display names
                "",           # yukino
                "",           # shizuka
                "",           # val
                "",           # kiki-chii
                "Sir. Robot", # shikaku custom display name
                "y",          # confirm apply
                "1",          # [1/4] Skills: keep bundled skills (REA OFF)
                "1",          # [2/4] Plugin: stage fail-open msshi-auto-trim, KAT skip
                "1",          # [3/4] Koneksi Services: per-profile GitLab/Tinyfish MCP
                "1",          # [4/4] Bot -> Apps: auto-reconnect all bots
            ]) + "\n"
            with patch.dict(os.environ, base_env, clear=False), \
                 patch("sys.stdin", io.StringIO(interactive_inputs)), \
                 patch("sys.stdout", new_callable=io.StringIO):
                code2 = msshi_cli.main(["setup", "--no-pdf"])
            self.assertEqual(code2, 0)

            shikaku_after = hermes_profiles.load_yaml_mapping(shikaku_cfg)
            self.assertEqual(shikaku_after["model"], {"default": "custom/already-chosen", "provider": "openai"})
            self.assertIn("gitlab", shikaku_after.get("mcp_servers", {}))
            self.assertIn("tinyfish", shikaku_after.get("mcp_servers", {}))
            self.assertNotIn("brightdata", shikaku_after.get("mcp_servers", {}))
            self.assertTrue((hermes_home / "profiles" / "shikaku" / "plugins" / "msshi-auto-trim" / "plugin.yaml").is_file())
            self.assertEqual(shikaku_db.read_bytes(), b"SQLite format 3\x00sentinel")
            self.assertEqual(shikaku_soul.read_text(encoding="utf-8"), "# Custom User Soul\n")
            shikaku_meta = hermes_profiles.load_yaml_mapping(hermes_home / "profiles" / "shikaku" / "profile.yaml")
            self.assertEqual(shikaku_meta["display_name"], "Sir. Robot")
            self.assertEqual(shikaku_meta["ui_meta"]["hermes-bots"]["title"], "Sir. Robot")
            self.assertTrue((hermes_home / "profiles" / "val" / "config.yaml").is_file())
            self.assertFalse(any(p.name.startswith(".val.") for p in (hermes_home / "profiles").iterdir()))

            for bot_id in ("yukino", "shizuka", "val", "kiki-chii", "shikaku"):
                bot_root = hermes_home if bot_id == "yukino" else hermes_home / "profiles" / bot_id
                conn_file = bot_root / "msshi-bridge" / "connections.json"
                self.assertTrue(conn_file.is_file(), f"Missing connections.json for {bot_id}")
                conn_doc = json.loads(conn_file.read_text(encoding="utf-8"))
                self.assertFalse(conn_doc.get("auto_open_on_boot", True))
                self.assertIn("targets", conn_doc)

            report_file = msshi_home / "reports" / "last-setup-report.json"
            self.assertTrue(report_file.is_file())
            report_doc = json.loads(report_file.read_text(encoding="utf-8"))
            self.assertEqual(report_doc["default_bot"], "yukino")
            self.assertFalse(report_doc["provider_model_mutated"])
            self.assertFalse(report_doc["skills"]["rea_enabled"])
            self.assertTrue(report_doc["plugins"]["auto_trim"]["staged"])
            self.assertEqual(report_doc["services"]["status"], "installed")
            self.assertFalse(report_doc["services"]["brightdata_enabled"])
            self.assertEqual(len(report_doc["bot_app_connections"]["bots"]), 5)

            # 3. Custom-bots mode (mode 2) auto-sets Hermes profiles cleanly
            custom_stdin = "1\ncustom-alpha\nCustom Alpha\nTester\n1\n"
            with patch.dict(os.environ, base_env, clear=False), \
                 patch("sys.stdin", io.StringIO(custom_stdin)), \
                 patch("sys.stdout", new_callable=io.StringIO):
                code_custom = msshi_cli.main([
                    "setup", "--mode", "custom-bots", "--platform", "hermes", "--no-pdf", "--yes",
                ])
            self.assertEqual(code_custom, 0)
            self.assertTrue((hermes_home / "profiles" / "custom-alpha" / "profile.yaml").is_file())
            self.assertTrue((hermes_home / "profiles" / "custom-alpha" / "config.yaml").is_file())
            custom_meta = hermes_profiles.load_yaml_mapping(hermes_home / "profiles" / "custom-alpha" / "profile.yaml")
            self.assertEqual(custom_meta["display_name"], "Custom Alpha")

            # 4. Portable --target-dir isolation check
            portable = root / "portable-team"
            with patch.dict(os.environ, base_env, clear=False), patch("sys.stdout", new_callable=io.StringIO):
                install_msshi.main(["--mode", "muza-preset", "--platform", "hermes", "--target-dir", str(portable), "--apply"])
            self.assertTrue((portable / "shikaku" / "SOUL.md").is_file())
            self.assertFalse((portable / "shikaku" / "profile.yaml").exists())

    def test_runtime_yaml_module_pure_python_fallback_when_ruamel_missing(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            hermes_home = root / "hermes-home"
            hermes_home.mkdir()
            (hermes_home / "config.yaml").write_text(
                "model:\n  default: upstage/solar-mini4:free\n  provider: nous\n",
                encoding="utf-8",
            )
            env = {
                "HERMES_HOME": str(hermes_home),
                "MSSHI_IGNORE_REGISTRY_HERMES_HOME": "1",
                "MSSHI_WINDOWS_D_DRIVE": "",
            }
            real_import = builtins.__import__

            def block_yaml(name, globals=None, locals=None, fromlist=(), level=0):
                if name == "yaml" or name.startswith("ruamel"):
                    raise ImportError(name)
                return real_import(name, globals, locals, fromlist, level)

            with patch.dict(os.environ, env, clear=False), patch("builtins.__import__", side_effect=block_yaml):
                yaml_cls = msshi_runtime.yaml_module()
                self.assertIs(yaml_cls, hermes_profiles.PureYamlCompat)
                updated, changed = msshi_runtime.config_update(
                    b"model:\n  default: upstage/solar-mini4:free\nmcp_servers:\n  gdrive:\n    url: https://example.test\n"
                )
                self.assertIn("gdrive", changed)
                parsed = msshi_runtime.yaml_read(updated)
                self.assertEqual(parsed["model"]["default"], "upstage/solar-mini4:free")
                self.assertNotIn("gdrive", parsed.get("mcp_servers", {}))

    def test_pre_hermes_status_helpers_without_config_yaml(self) -> None:
        with TemporaryDirectory() as tmp:
            empty_hermes = Path(tmp) / "empty-hermes"
            empty_hermes.mkdir()
            svc = msshi_service_connections.status(empty_hermes)
            steel = msshi_browser_policy.status(empty_hermes)
            self.assertTrue(bool(svc))
            self.assertFalse(any(row["config_present"] for row in svc.values()))
            self.assertFalse(steel["config_present"])

    def test_setup_wizard_steps_cli_and_interactive_per_bot_mapping(self) -> None:
        _, _, packs = install_msshi.read_matrix(ROOT / msshi_cli.MATRIX)
        extra_pack = "business" if "business" in packs else next(iter(packs))
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            msshi_home = root / "msshi-data"
            hermes_home = root / "hermes-home"
            msshi_home.mkdir()
            base_env = {
                "MSSHI_HOME": str(msshi_home),
                "HERMES_HOME": str(hermes_home),
                "MSSHI_IGNORE_REGISTRY_HERMES_HOME": "1",
            }

            # Case A: Pre-Hermes unattended setup with explicit 4-step CLI options
            with patch.dict(os.environ, base_env, clear=False), patch("sys.stdout", new_callable=io.StringIO):
                code = msshi_cli.main([
                    "setup",
                    "--mode", "muza-preset",
                    "--platform", "hermes",
                    "--extra-packs", extra_pack,
                    "--with-rea",
                    "--kat-mode", "light",
                    "--connect-services", "per-profile",
                    "--connect-apps", "select",
                    "--connect-bots", "shikaku",
                    "--connect-targets", "antigravity,perplexity",
                    "--yes",
                ])
            self.assertEqual(code, 0)
            for slug in packs[extra_pack]:
                self.assertTrue((hermes_home / "profiles" / "shikaku" / "skills" / slug / "SKILL.md").is_file())
            self.assertTrue((hermes_home / "profiles" / "shikaku" / "skills" / "rea" / "SKILL.md").is_file())
            shikaku_conn = json.loads(
                (hermes_home / "profiles" / "shikaku" / "msshi-bridge" / "connections.json").read_text(encoding="utf-8")
            )
            self.assertEqual(shikaku_conn["targets"], ["antigravity", "perplexity"])
            self.assertFalse(shikaku_conn["auto_open_on_boot"])

            report_a = json.loads((msshi_home / "reports" / "last-setup-report.json").read_text(encoding="utf-8"))
            self.assertTrue(report_a["skills"]["rea_enabled"])
            self.assertIn(extra_pack, report_a["skills"]["extra_packs"])
            self.assertEqual(report_a["plugins"]["kat"]["profile"], "shikaku")
            self.assertFalse(report_a["plugins"]["kat"]["enabled"])
            self.assertFalse(report_a["plugins"]["kat"]["main_model_changed"])
            self.assertEqual(report_a["services"]["status"], "deferred_pre_hermes")
            self.assertEqual(list(report_a["bot_app_connections"]["bots"]), ["shikaku"])
            self.assertEqual(report_a["bot_app_connections"]["bots"]["shikaku"]["status"], "connected")

            # Case B: Post-Hermes interactive extra skills + dreaming + per-profile MCP + manual bot -> apps ("3")
            (hermes_home / "config.yaml").write_text(
                "model:\n  default: custom/post-hermes\n  provider: openrouter\n",
                encoding="utf-8",
            )
            with patch.dict(os.environ, base_env, clear=False), patch("sys.stdout", new_callable=io.StringIO):
                self.assertEqual(msshi_cli.migrate_runtime(ROOT, hermes_home), 0)

            interactive_manual = "\n".join([
                "4",          # mode: muza-preset
                "hermes",     # platform
                "",           # default <hermes_home>\profiles
                "n",          # skip custom display names
                "y",          # confirm apply
                "2",          # [1/4] Skills: add extra pack/skill
                extra_pack,   # extra pack name
                "",           # no extra individual slugs
                "yukino",     # apply extra pack only to yukino
                "3",          # [2/4] Plugin: auto-trim + dreaming + omnivoice check
                "1",          # [3/4] Koneksi Services: per-profile MCP
                "3",          # [4/4] Bot -> Apps: manual per-bot mapping
                "yukino,shikaku",  # selected bots for manual mapping
                "perplexity", # yukino -> perplexity
                "skip",       # shikaku -> skip manual mapping
            ]) + "\n"
            fake_dream = {"mode": "deterministic proposals only", "llm_calls": 0, "profiles": [{"role": "yukino", "exit": 0}]}
            with patch.dict(os.environ, base_env, clear=False), \
                 patch("msshi_integrations.dream", return_value=fake_dream), \
                 patch("sys.stdin", io.StringIO(interactive_manual)), \
                 patch("sys.stdout", new_callable=io.StringIO):
                code_b = msshi_cli.main(["setup", "--no-pdf"])
            self.assertEqual(code_b, 0)

            report_b = json.loads((msshi_home / "reports" / "last-setup-report.json").read_text(encoding="utf-8"))
            self.assertEqual(list(report_b["skills"]["applied_targets"]), ["yukino"])
            for slug in packs[extra_pack]:
                self.assertTrue((hermes_home / "skills" / slug / "SKILL.md").is_file())
            self.assertTrue((hermes_home / "plugins" / "msshi-auto-trim" / "plugin.yaml").is_file())
            self.assertTrue(report_b["plugins"]["auto_trim"]["staged"])
            self.assertEqual(report_b["plugins"]["dreaming"]["status"], "ok")
            self.assertEqual(report_b["services"]["status"], "installed")
            self.assertEqual(report_b["bot_app_connections"]["mode"], "manual-per-bot")
            self.assertEqual(report_b["bot_app_connections"]["bots"]["yukino"]["status"], "connected")
            self.assertEqual(
                report_b["bot_app_connections"]["bots"]["yukino"]["connections_file"],
                str(hermes_home / "msshi-bridge/connections.json"),
            )
            self.assertIn("perplexity", report_b["bot_app_connections"]["bots"]["yukino"]["targets"])
            self.assertEqual(list(report_b["bot_app_connections"]["bots"]), ["yukino"])
            yukino_cfg = hermes_profiles.load_yaml_mapping(hermes_home / "config.yaml")
            self.assertEqual(yukino_cfg["model"], {"default": "custom/post-hermes", "provider": "openrouter"})
            self.assertIn("gitlab", yukino_cfg.get("mcp_servers", {}))

    def test_named_yukino_preserves_neutral_stock_root_custom_soul_and_legacy(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            msshi_home = root / "msshi-data"
            hermes_home = root / "hermes-home"
            msshi_home.mkdir()
            hermes_home.mkdir()
            (hermes_home / "config.yaml").write_text(
                "model:\n  default: upstage/solar-mini4:free\n  provider: nous\n",
                encoding="utf-8",
            )
            stock_soul = (
                hermes_profiles.STOCK_HERMES_SOUL_PREFIX
                + " Be direct: skip filler phrases and answer directly.\n"
            )
            (hermes_home / "SOUL.md").write_text(stock_soul, encoding="utf-8")

            # Simulate pre-existing legacy profiles/yukino with user session DB
            legacy_yukino = hermes_home / "profiles" / "yukino"
            legacy_yukino.mkdir(parents=True)
            legacy_db = legacy_yukino / "state.db"
            legacy_db.write_bytes(b"SQLite format 3\x00legacy")

            base_env = {
                "MSSHI_HOME": str(msshi_home),
                "HERMES_HOME": str(hermes_home),
                "MSSHI_IGNORE_REGISTRY_HERMES_HOME": "1",
            }
            with patch.dict(os.environ, base_env, clear=False), patch("sys.stdout", new_callable=io.StringIO):
                code = msshi_cli.main(["setup", "--mode", "muza-preset", "--platform", "hermes", "--yes"])
            self.assertEqual(code, 0)

            self.assertFalse((hermes_home / "profile.yaml").exists())
            meta = hermes_profiles.load_yaml_mapping(legacy_yukino / "profile.yaml")
            self.assertEqual(meta["display_name"], "Yukino Yukinoshita")
            self.assertEqual(meta["ui_meta"]["hermes-bots"]["title"], "Yukino Yukinoshita")
            self.assertEqual((hermes_home / "SOUL.md").read_text(encoding="utf-8"), stock_soul)
            self.assertIn("Yukino", (legacy_yukino / "SOUL.md").read_text(encoding="utf-8"))
            self.assertFalse((hermes_home / "backups").exists())
            self.assertEqual(legacy_db.read_bytes(), b"SQLite format 3\x00legacy")

            # Custom user SOUL.md and custom display_name on default must never be overwritten without explicit update
            custom_soul = "# My Custom Default Bot Soul\nKeep everything intact.\n"
            (hermes_home / "SOUL.md").write_text(custom_soul, encoding="utf-8")
            with patch.dict(os.environ, base_env, clear=False), patch("sys.stdout", new_callable=io.StringIO):
                code2 = msshi_cli.main(["setup", "--mode", "muza-preset", "--platform", "hermes", "--yes"])
            self.assertEqual(code2, 0)
            self.assertEqual((hermes_home / "SOUL.md").read_text(encoding="utf-8"), custom_soul)

            # Opt-out (--default-bot keep-hermes) keeps vanilla Hermes default untouched on clean root
            hermes_optout = root / "hermes-optout"
            hermes_optout.mkdir()
            (hermes_optout / "config.yaml").write_text("model:\n  default: test/model\n", encoding="utf-8")
            (hermes_optout / "SOUL.md").write_text(stock_soul, encoding="utf-8")
            env_optout = {**base_env, "HERMES_HOME": str(hermes_optout)}
            with patch.dict(os.environ, env_optout, clear=False), patch("sys.stdout", new_callable=io.StringIO):
                code3 = msshi_cli.main([
                    "setup", "--mode", "muza-preset", "--platform", "hermes",
                    "--default-bot", "keep-hermes", "--yes",
                ])
            self.assertEqual(code3, 0)
            self.assertFalse((hermes_optout / "profile.yaml").exists())
            self.assertEqual((hermes_optout / "SOUL.md").read_text(encoding="utf-8"), stock_soul)
            self.assertTrue((hermes_optout / "profiles" / "yukino" / "profile.yaml").is_file())

    def test_existing_settings_preserved_across_yes_and_reinstall(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            msshi_home = root / "msshi-data"
            hermes_home = root / "hermes-home"
            msshi_home.mkdir()
            hermes_home.mkdir()
            (hermes_home / "config.yaml").write_text(
                "model:\n  default: custom/keep-model\n  provider: openai\n",
                encoding="utf-8",
            )
            base_env = {
                "MSSHI_HOME": str(msshi_home),
                "HERMES_HOME": str(hermes_home),
                "MSSHI_IGNORE_REGISTRY_HERMES_HOME": "1",
            }
            with patch.dict(os.environ, base_env, clear=False), patch("sys.stdout", new_callable=io.StringIO):
                code1 = msshi_cli.main([
                    "setup", "--mode", "muza-preset", "--platform", "hermes",
                    "--kat-mode", "light", "--stage-auto-trim",
                    "--connect-apps", "auto-reconnect", "--yes",
                ])
            self.assertEqual(code1, 0)
            self.assertTrue((hermes_home / "plugins" / "msshi-auto-trim" / "plugin.yaml").is_file())
            self.assertTrue((hermes_home / "profiles" / "shikaku" / "plugins" / "msshi-auto-trim" / "plugin.yaml").is_file())

            # Re-running with plain --yes (like re-running install.ps1 -Yes) MUST preserve existing KAT, auto-trim, and app connections
            with patch.dict(os.environ, base_env, clear=False), patch("sys.stdout", new_callable=io.StringIO):
                code2 = msshi_cli.main([
                    "setup", "--mode", "muza-preset", "--platform", "hermes", "--yes",
                ])
            self.assertEqual(code2, 0)
            report = json.loads((msshi_home / "reports" / "last-setup-report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["plugins"]["kat"]["profile"], "shikaku")
            self.assertFalse(report["plugins"]["kat"]["enabled"])
            self.assertFalse(report["plugins"]["kat"]["main_model_changed"])
            self.assertTrue(report["plugins"]["auto_trim"]["staged"])
            self.assertEqual(set(report["plugins"]["auto_trim"]["profiles"]), {"yukino", "shizuka", "val", "kiki-chii", "shikaku"})
            self.assertIn("shikaku", report["bot_app_connections"]["existing_connected_bots"])
            self.assertIn("yukino", report["bot_app_connections"]["existing_connected_bots"])


if __name__ == "__main__":
    unittest.main()
