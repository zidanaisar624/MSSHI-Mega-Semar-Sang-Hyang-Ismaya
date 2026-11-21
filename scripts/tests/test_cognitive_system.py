"""Offline unit tests for the MSSHI 4-Mission + 4-Pillar Closed-Loop Cognitive Operating System."""
from __future__ import annotations

from contextlib import contextmanager
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import msshi_hermes_profiles as hp
import msshi_system as sysmod


@contextmanager
def _team_routing_module(home: Path):
    """Load hermes_plugins/msshi-team-routing/__init__.py with stubbed Hermes core modules."""
    agent_mod = types.ModuleType("agent")
    dp_mod = types.ModuleType("agent.delegation_provider")

    class _DelegationProvider:
        pass

    class _DelegationRouteError(ValueError):
        pass

    dp_mod.DelegationProvider = _DelegationProvider
    dp_mod.DelegationRouteError = _DelegationRouteError
    hc_mod = types.ModuleType("hermes_constants")
    hc_mod.get_hermes_home = lambda: home
    hc_mod.get_default_hermes_root = lambda: home
    hc_mod.named_profile_is_live = lambda p: Path(p).is_dir()

    saved = {
        name: sys.modules.get(name)
        for name in ("agent", "agent.delegation_provider", "hermes_constants", "msshi_team_routing_test")
    }
    try:
        sys.modules["agent"] = agent_mod
        sys.modules["agent.delegation_provider"] = dp_mod
        sys.modules["hermes_constants"] = hc_mod
        plugin_path = ROOT / "hermes_plugins" / "msshi-team-routing" / "__init__.py"
        spec = importlib.util.spec_from_file_location("msshi_team_routing_test", plugin_path)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        yield mod
    finally:
        for name, prev in saved.items():
            if prev is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = prev


class CognitiveSystemTests(unittest.TestCase):
    def test_harness2_and_timesfm_parity_across_all_presets(self):
        matrix = json.loads((ROOT / "configs" / "bot_role_and_skill_matrix.json").read_text(encoding="utf-8-sig"))
        academic = json.loads((ROOT / "configs" / "academic_presets.json").read_text(encoding="utf-8-sig"))

        for bot in matrix["bots"]:
            self.assertIn("harness2", bot["required_skills"], f"harness2 missing on {bot['id']} in muza-preset")
        val_muza = next(b for b in matrix["bots"] if b["id"] == "val")
        self.assertIn("timesfm-forecasting", val_muza["required_skills"])

        for preset_id in ("academic-mahasiswa", "academic-dosen"):
            roles = academic["presets"][preset_id]["roles"]
            for role, skills in roles.items():
                self.assertIn("harness2", skills, f"harness2 missing on {role} in {preset_id}")
            self.assertIn("timesfm-forecasting", roles["val"], f"timesfm-forecasting missing on val in {preset_id}")
            self.assertIn("symbolic-equation", roles["val"], f"symbolic-equation missing on val in {preset_id}")

    def test_skripsi_and_journal_skills_belong_exclusively_to_val_and_shizuka_and_fit_hermes_limit(self):
        # Hermes enforces MAX_DESCRIPTION_LENGTH = 1024 on SKILL.md frontmatter
        sm = (ROOT / "skills" / "muza-skripsi-template" / "SKILL.md").read_text(encoding="utf-8-sig")
        fm = sm.split("---")[1]
        desc = fm.split("description:", 1)[1].strip()
        self.assertLessEqual(len(desc), 1024, f"muza-skripsi-template description exceeds 1024 chars: {len(desc)}")

        matrix = json.loads((ROOT / "configs" / "bot_role_and_skill_matrix.json").read_text(encoding="utf-8-sig"))
        academic = json.loads((ROOT / "configs" / "academic_presets.json").read_text(encoding="utf-8-sig"))
        exclusive = ("muza-skripsi-template", "literature-review", "deep-research")

        muza_roles = {b["id"]: set(b.get("required_skills", [])) for b in matrix["bots"]}
        for bot_id in ("yukino", "kiki-chii", "shikaku"):
            for slug in exclusive:
                self.assertNotIn(slug, muza_roles[bot_id], f"{slug} must not be on {bot_id} in muza-preset")
        for bot_id in ("val", "shizuka"):
            for slug in exclusive:
                self.assertIn(slug, muza_roles[bot_id], f"{slug} must be on {bot_id} in muza-preset")

        for preset_id in ("academic-mahasiswa", "academic-dosen"):
            roles = {r: set(sk) for r, sk in academic["presets"][preset_id]["roles"].items()}
            for bot_id in ("yukino", "kiki-chii", "shikaku"):
                for slug in exclusive:
                    self.assertNotIn(slug, roles[bot_id], f"{slug} must not be on {bot_id} in {preset_id}")
            self.assertIn("muza-skripsi-template", roles["val"])
            self.assertIn("muza-skripsi-template", roles["shizuka"])
            self.assertIn("literature-review", roles["val"])
            self.assertIn("literature-review", roles["shizuka"])

    def test_cognitive_manifest_has_4_missions_and_is_model_user_agnostic(self):
        manifest_path = ROOT / "configs" / "msshi_cognitive_system.json"
        self.assertTrue(manifest_path.is_file())
        data = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        self.assertEqual(data["schema_version"], 1)
        self.assertTrue((ROOT / data["documentation"]).is_file())
        mission_ids = [m["id"] for m in data["core_missions"]]
        self.assertEqual(
            mission_ids,
            [
                "1_belajar_jadi_guru",
                "2_tugas_skripsi_tesis_disertasi",
                "3_konten_kreasi",
                "4_coding",
                "5_teman_curhat_dan_daily_scheduling",
            ],
        )
        p = data["principles"]
        self.assertTrue(p["model_agnostic"])
        self.assertTrue(p["user_agnostic"])
        self.assertFalse(p["provider_model_mutation"])
        self.assertFalse(p["auto_open_on_boot"])
        self.assertFalse(p["background_model_calls"])
        self.assertTrue(p["human_approval_required_for_promotion"])
        self.assertFalse(p["jev_model_routing"])
        for pillar in ("token_efficiency", "continuous_learning", "research_and_prediction", "governance_and_routing"):
            self.assertIn(pillar, data["pillars"])

    def test_zero_orphan_coverage_for_all_skills_plugins_upstreams_and_connections(self):
        cov = sysmod.coverage_audit(ROOT)
        self.assertTrue(cov["zero_orphan_system"], f"Found orphans in cognitive system: {cov}")
        self.assertEqual(cov["bundled_skills_mapped"], cov["bundled_skills_total"])
        self.assertGreaterEqual(cov["bundled_skills_total"], 69)
        self.assertEqual(cov["unmapped_bundled_skills"], [])
        self.assertEqual(cov["optional_skills_mapped"], cov["optional_skills_total"])
        self.assertEqual(cov["unmapped_optional_skills"], [])
        self.assertEqual(cov["repo_plugins_mapped"], cov["repo_plugins_total"])
        self.assertGreaterEqual(cov["repo_plugins_total"], 4)
        self.assertEqual(cov["unmapped_repo_plugins"], [])
        self.assertEqual(cov["upstream_sources_governed"], cov["upstream_sources_total"])
        self.assertGreaterEqual(cov["upstream_sources_total"], 53)
        self.assertEqual(cov["unmapped_upstreams"], [])
        self.assertEqual(cov["connection_planes_governed"], 6)
        self.assertTrue(cov["all_connections_auto_open_false"])

    def test_system_status_offline_mock_zero_llm_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "hermes-home"
            home.mkdir(parents=True)
            cfg = (
                "plugins:\n"
                "  enabled:\n"
                "    - msshi-auto-trim\n"
                "    - msshi-team-routing\n"
                "    - msshi-interaction\n"
                "  disabled: []\n"
            )
            (home / "config.yaml").write_text(cfg, encoding="utf-8")
            (home / "tools" / "llmtrim").mkdir(parents=True)
            (home / "tools" / "llmtrim" / "llmtrim.exe").write_bytes(b"stub")
            (home / "msshi-private" / "harness2-runtime").mkdir(parents=True)
            (home / "msshi-private" / "harness2-runtime" / "INSTALLATION.json").write_text('{"schema": 1}', encoding="utf-8")

            for bot in ("yukino", "shizuka", "val", "kiki-chii", "shikaku"):
                pdir = home / "profiles" / bot
                (pdir / "skills" / "harness2").mkdir(parents=True)
                (pdir / "skills" / "harness2" / "SKILL.md").write_text("# harness2\n", encoding="utf-8")
                (pdir / "skills" / "caveman").mkdir(parents=True)
                (pdir / "skills" / "caveman" / "SKILL.md").write_text("# caveman\n", encoding="utf-8")
                (pdir / "config.yaml").write_text(cfg, encoding="utf-8")
            (home / "profiles" / "val" / "skills" / "timesfm-forecasting").mkdir(parents=True)
            (home / "profiles" / "val" / "skills" / "timesfm-forecasting" / "SKILL.md").write_text("# timesfm\n", encoding="utf-8")
            (home / "profiles" / "shikaku" / "skills" / "grim-prompter").mkdir(parents=True)
            (home / "profiles" / "shikaku" / "skills" / "grim-prompter" / "SKILL.md").write_text("# grim\n", encoding="utf-8")
            (home / "profiles" / "shikaku" / "skills" / "claude-bughunter").mkdir(parents=True)
            (home / "profiles" / "shikaku" / "skills" / "claude-bughunter" / "SKILL.md").write_text("# bughunter\n", encoding="utf-8")

            report = sysmod.system_status(home, source_root=ROOT)
            self.assertEqual(len(report["core_missions"]), 5)
            self.assertEqual(report["guardrails"]["model_calls"], 0)
            self.assertEqual(report["guardrails"]["network_requests"], 0)
            self.assertFalse(report["guardrails"]["provider_model_mutated"])
            self.assertTrue(all(report["preset_parity"]["harness2_all_bots"].values()))
            self.assertTrue(all(report["preset_parity"]["timesfm_on_val"].values()))
            self.assertEqual(report["pillars"]["1_token_efficiency"]["msshi_trim"]["enabled_count"], 6)
            self.assertTrue(report["pillars"]["2_continuous_learning"]["harness2_runtime_ready"])
            self.assertEqual(len(report["pillars"]["2_continuous_learning"]["harness2_skill_profiles"]), 5)
            self.assertEqual(report["pillars"]["3_research_and_prediction"]["timesfm_skill_profiles"], ["val"])
            self.assertEqual(report["pillars"]["3_research_and_prediction"]["coder_security_profiles"]["grim_prompter"], ["shikaku"])
            self.assertEqual(report["pillars"]["3_research_and_prediction"]["coder_security_profiles"]["claude_bughunter"], ["shikaku"])

    def test_route_task_all_4_core_missions_and_gating(self):
        # Mission 1: Belajar (Jadi Guru)
        learn = sysmod.route_task("Ajari saya kalkulus dan statistika dari nol sebagai guru tutor")
        self.assertEqual(learn["core_mission"], "1_belajar_jadi_guru")
        self.assertEqual(learn["lead_bot"], "shizuka")
        self.assertIn("parenting-6d-gad-mdd", learn["recommended_skills"])
        self.assertEqual(learn["model_calls"], 0)

        short_learn = sysmod.route_task("Ajari saya dasar Python")
        self.assertNotEqual(short_learn["interaction_mode"], "fast_main_only")

        # Mission 2: Tugas, Skripsi, Tesis, Disertasi (Riset & Prediksi)
        pred = sysmod.route_task("Prediksi tren penjualan 12 bulan dengan TimesFM dan backtesting")
        self.assertEqual(pred["core_mission"], "2_tugas_skripsi_tesis_disertasi")
        self.assertEqual(pred["lead_bot"], "val")
        self.assertIn("timesfm-forecasting", pred["recommended_skills"])
        self.assertFalse(pred["wake_all_bots"])
        self.assertEqual(pred["model_calls"], 0)

        pred_low = sysmod.route_task("Prediksi tren penjualan 12 bulan dengan backtesting", low_ram=True)
        self.assertEqual(pred_low["interaction_mode"], "sequential_single_inference_low_ram")

        res = sysmod.route_task("Riset literatur tesis dan disertasi tentang novelty serta sitasi DOI")
        self.assertEqual(res["core_mission"], "2_tugas_skripsi_tesis_disertasi")
        self.assertEqual(res["lead_bot"], "val")
        self.assertIn("deep-research", res["recommended_skills"])

        # Mission 3: Konten Kreasi
        creative = sysmod.route_task("Buat konsep dan storyboard konten kreasi video YouTube dan slide presentasi")
        self.assertEqual(creative["core_mission"], "3_konten_kreasi")
        self.assertEqual(creative["lead_bot"], "kiki-chii")

        # Mission 4: Coding & Security
        sec = sysmod.route_task("Lakukan threat model STRIDE dan audit keamanan OWASP SSRF pada API kami")
        self.assertEqual(sec["core_mission"], "4_coding")
        self.assertEqual(sec["lead_bot"], "shikaku")
        self.assertIn("grim-prompter", sec["recommended_skills"])
        self.assertIn("claude-bughunter", sec["recommended_skills"])

        code = sysmod.route_task("Refactor backend Python API dan tambahkan unit test TDD")
        self.assertEqual(code["core_mission"], "4_coding")
        self.assertEqual(code["lead_bot"], "shikaku")
        self.assertIn("mattpocock-engineering", code["recommended_skills"])

        # Mission 5: Teman Curhat & Daily Basis (Scheduling)
        daily = sysmod.route_task("Aku capek hari ini, mau curhat sebentar dan atur jadwal harian besok")
        self.assertEqual(daily["core_mission"], "5_teman_curhat_dan_daily_scheduling")
        self.assertEqual(daily["lead_bot"], "yukino")
        self.assertEqual(daily["interaction_mode"], "fast_main_only")
        self.assertEqual(daily["optional_support_bots"], [])
        self.assertFalse(daily["wake_all_bots"])
        self.assertIn("parenting-6d-gad-mdd", daily["recommended_skills"])
        self.assertIn("focus-my-energy", daily["recommended_skills"])

        # Brief chat gating
        brief = sysmod.route_task("Halo apa kabar?")
        self.assertEqual(brief["interaction_mode"], "fast_main_only")
        self.assertEqual(brief["optional_support_bots"], [])

        with self.assertRaises(ValueError):
            sysmod.route_task("   ")

    def test_plan_cycle_supports_learning_and_prediction_with_human_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "hermes-home"
            home.mkdir()
            plan_pred = sysmod.plan_cycle(home, "Bandingkan TimesFM 2.5 vs seasonal-naive", domain="prediction")
            self.assertEqual(len(plan_pred["phases"]), 4)
            self.assertEqual(plan_pred["routing"]["lead_bot"], "val")
            self.assertEqual(plan_pred["guardrails"]["model_calls"], 0)
            self.assertFalse(plan_pred["guardrails"]["auto_promotion"])
            self.assertTrue(plan_pred["guardrails"]["human_approval_required"])

            plan_learn = sysmod.plan_cycle(home, "Kuasai materi regresi linier sebagai guru", domain="learning")
            self.assertEqual(plan_learn["routing"]["lead_bot"], "shizuka")
            self.assertEqual(plan_learn["guardrails"]["model_calls"], 0)

    def test_team_routing_role_policy_includes_4_missions_and_cognitive_loop_under_2600_chars(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "hermes-home"
            home.mkdir()
            for layout in ("keep-hermes", "yukino"):
                hp.record_team_layout(home, layout)
                with _team_routing_module(home) as mod:
                    for actual in ("default", "yukino", "shizuka", "val", "kiki-chii", "shikaku"):
                        policy = mod.role_policy({"profile_name": actual})
                        self.assertLess(len(policy), 2600, f"role_policy too long for {layout}/{actual}: {len(policy)}")
                        for token in (
                            "Tutor/Guru",
                            "Skripsi/Tesis/Disertasi",
                            "Content creation",
                            "imagination-studio",
                            "Coding",
                            "Daily companion/curhat",
                            "MSSHITrim",
                            "caveman",
                            "msshi find",
                            "timesfm-forecasting",
                            "grim-prompter",
                            "claude-bughunter",
                            "msshi dream",
                            "harness2",
                            "never auto-promote",
                        ):
                            self.assertIn(token, policy)

    def test_optional_imagination_studio_collaborates_with_filmmaker_and_stays_opt_in(self):
        import msshi_imagination_studio as studio_mod
        import msshi_optional as opt_mod

        # Optional wrapper exists, public_default is False, description <= 1024 chars, NOTICE retains attribution
        opt_dir = ROOT / "optional" / "imagination-studio"
        self.assertFalse((ROOT / "skills" / "imagination-studio").exists())
        sm = (opt_dir / "SKILL.md").read_text(encoding="utf-8-sig")
        desc = sm.split("---")[1].split("description:", 1)[1].strip()
        self.assertLessEqual(len(desc), 1024)
        notice = (opt_dir / "NOTICE").read_text(encoding="utf-8-sig")
        self.assertIn("Keys (drowzeys)", notice)
        self.assertIn("Sam Wasserman", notice)

        # Filmmaker SKILL.md references Stage E Imagination Studio collaboration
        fm = (ROOT / "skills" / "filmmaking-videography-photography-s2" / "SKILL.md").read_text(encoding="utf-8-sig")
        self.assertIn("Stage E: Optional Imagination Studio", fm)
        self.assertIn("msshi studio status --probe", fm)

        # setup_targets scopes imagination-studio strictly to kiki-chii on presets
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sels = [root / bot / "skills" for bot in ("yukino", "shizuka", "val", "kiki-chii", "shikaku")]
            for preset in ("muza-preset", "academic-mahasiswa", "academic-dosen"):
                targets = opt_mod.setup_targets(preset, sels, name="imagination-studio", source=ROOT)
                self.assertEqual(targets, [root / "kiki-chii" / "skills"])

            # Offline status check makes 0 network/model calls and detects collaboration readiness
            home = root / "hermes"
            (home / "profiles" / "kiki-chii" / "skills" / "filmmaking-videography-photography-s2").mkdir(parents=True)
            (home / "profiles" / "kiki-chii" / "skills" / "filmmaking-videography-photography-s2" / "SKILL.md").write_text("# fm\n", encoding="utf-8")
            st_off = studio_mod.studio_status(home, probe=False)
            self.assertFalse(st_off["kiki_chii"]["optional_wrapper_enabled"])
            self.assertFalse(st_off["kiki_chii"]["collaboration_ready"])
            self.assertEqual(st_off["guardrails"]["network_requests"], 0)
            self.assertEqual(st_off["guardrails"]["model_calls"], 0)

            (home / "profiles" / "kiki-chii" / "skills" / "imagination-studio").mkdir(parents=True)
            (home / "profiles" / "kiki-chii" / "skills" / "imagination-studio" / "SKILL.md").write_text("# studio\n", encoding="utf-8")
            st_on = studio_mod.studio_status(home, probe=False)
            self.assertTrue(st_on["kiki_chii"]["optional_wrapper_enabled"])
            self.assertTrue(st_on["kiki_chii"]["collaboration_ready"])

        # Non-loopback URL is rejected strictly
        with self.assertRaises(ValueError):
            studio_mod.studio_status(url="https://example.com:7870", probe=False)

        # Plan produces 5-phase Filmmaker x Imagination Studio handoff
        plan = studio_mod.plan_collaboration("Film pendek cyber-noir 60 detik", fmt="short")
        self.assertEqual(plan["lead_bot"], "kiki-chii")
        self.assertEqual(plan["aspect_ratio"], "9:16")
        self.assertEqual(len(plan["phases"]), 5)
        self.assertEqual(plan["guardrails"]["model_calls"], 0)

        # Router maps Imagination Studio / Slate prompts to Kiki-Chii (Mission 3)
        routed = sysmod.route_task("Buat Slate shot list dan render klip di Imagination Studio")
        self.assertEqual(routed["core_mission"], "3_konten_kreasi")
        self.assertEqual(routed["lead_bot"], "kiki-chii")

    def test_spacewise_and_sharewise_installed_across_all_bots_and_presets(self):
        matrix = json.loads((ROOT / "configs" / "bot_role_and_skill_matrix.json").read_text(encoding="utf-8-sig"))
        academic = json.loads((ROOT / "configs" / "academic_presets.json").read_text(encoding="utf-8-sig"))

        for slug in ("spacewise", "sharewise"):
            # Skill folder + <=1024-char description + MIT LICENSE.upstream
            sm = (ROOT / "skills" / slug / "SKILL.md").read_text(encoding="utf-8-sig")
            desc = sm.split("---")[1].split("description:", 1)[1].strip()
            self.assertLessEqual(len(desc), 1024)
            self.assertTrue((ROOT / "skills" / slug / "LICENSE.upstream").is_file())
            # Native Hermes plugin folder + MIT LICENSE + plugin.yaml
            pdir = ROOT / "hermes_plugins" / slug
            self.assertTrue((pdir / "plugin.yaml").is_file())
            self.assertTrue((pdir / "__init__.py").is_file())
            self.assertTrue((pdir / "LICENSE").is_file())
            # Present on ALL bots in muza-preset, core pack, academic-mahasiswa, and academic-dosen
            self.assertIn(slug, matrix["packs"]["core"])
            for bot in matrix["bots"]:
                self.assertIn(slug, bot["required_skills"], f"{slug} missing on {bot['id']} in muza-preset")
            for preset_id in ("academic-mahasiswa", "academic-dosen"):
                for role, skills in academic["presets"][preset_id]["roles"].items():
                    self.assertIn(slug, skills, f"{slug} missing on {role} in {preset_id}")

        # Atomic plugin installer enables both plugins without mutating provider/model
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "hermes-home"
            home.mkdir()
            base_cfg = "model: keep-me\nprovider: keep-provider\nplugins:\n  enabled:\n    - msshi-auto-trim\n  disabled: []\n"
            (home / "config.yaml").write_text(base_cfg, encoding="utf-8")
            for bot in ("yukino", "shizuka", "val", "kiki-chii", "shikaku"):
                pdir = home / "profiles" / bot
                pdir.mkdir(parents=True)
                (pdir / "config.yaml").write_text(base_cfg, encoding="utf-8")
            res = hp.install_wise_plugins(home, ROOT)
            self.assertTrue(res["installed"])
            self.assertEqual(res["network_or_llm_calls"], 0)
            for name in ("default", "yukino", "shizuka", "val", "kiki-chii", "shikaku"):
                p = home if name == "default" else home / "profiles" / name
                self.assertTrue((p / "plugins" / "spacewise" / "plugin.yaml").is_file())
                self.assertTrue((p / "plugins" / "sharewise" / "plugin.yaml").is_file())
                cfg = hp.load_yaml_mapping(p / "config.yaml")
                self.assertEqual(cfg["model"], "keep-me")
                self.assertEqual(cfg["provider"], "keep-provider")
                self.assertIn("spacewise", cfg["plugins"]["enabled"])
                self.assertIn("sharewise", cfg["plugins"]["enabled"])

    def test_ossu_computer_science_connected_as_open_university_not_skill(self):
        import msshi_context_sources as cs_mod
        import msshi_ossu as ossu_mod

        self.assertIn("ossu-computer-science", cs_mod.PINNED)
        # OSSU is an open-source CS university curriculum, NOT a bot skill
        self.assertFalse((ROOT / "skills" / "ossu-computer-science").exists())

        matrix = json.loads((ROOT / "configs" / "bot_role_and_skill_matrix.json").read_text(encoding="utf-8-sig"))
        academic = json.loads((ROOT / "configs" / "academic_presets.json").read_text(encoding="utf-8-sig"))
        cog = json.loads((ROOT / "configs" / "msshi_cognitive_system.json").read_text(encoding="utf-8-sig"))
        self.assertNotIn("ossu-computer-science", {row["slug"] for row in matrix["skills"]})
        for bot in matrix["bots"]:
            self.assertNotIn("ossu-computer-science", bot["required_skills"])
        for preset_id in ("academic-mahasiswa", "academic-dosen"):
            self.assertIn("ossu-computer-science", academic["presets"][preset_id].get("connected_curricula", []))
            for role, skills in academic["presets"][preset_id]["roles"].items():
                self.assertNotIn("ossu-computer-science", skills, f"ossu must not be a skill on {role} in {preset_id}")

        conn = cog["connections_and_bridges_registry"]["ossu_open_cs_university"]
        self.assertIs(conn["is_bot_skill"], False)
        self.assertIs(conn["auto_open_on_boot"], False)
        self.assertEqual(conn["portal_url"], "https://cs.ossu.dev")

        sample_readme = (
            "# Curriculum\n"
            "## Intro CS\n"
            "`computation`\n"
            "Courses | Duration | Effort | Prerequisites\n"
            ":-- | :--: | :--: | :--:\n"
            "[Intro CS Python](coursepages/intro-cs/README.md) | 14 weeks | 6-10 hours/week | algebra\n"
            "## Core CS\n"
            "### Core systems\n"
            "`operating systems`\n"
            "Courses | Duration | Effort | Prerequisites\n"
            ":-- | :--: | :--: | :--:\n"
            "[Nand to Tetris](https://www.nand2tetris.org/) | 6 weeks | 7-13 hours/week | C\n"
        )
        parsed = ossu_mod.parse_curriculum(sample_readme)
        self.assertEqual(parsed["total_tracks"], 2)
        self.assertEqual(parsed["total_courses"], 2)
        self.assertEqual(parsed["courses"][0]["track_slug"], "intro-cs")
        self.assertTrue(parsed["courses"][0]["is_local_coursepage"])
        self.assertEqual(parsed["courses"][1]["track_slug"], "core-systems")

        portal = ossu_mod.open_target(ROOT, "portal", launch_browser=False)
        self.assertEqual(portal["url"], "https://cs.ossu.dev")
        self.assertFalse(portal["browser_opened"])

        routed = sysmod.route_task("Saya mahasiswa mau belajar kurikulum OSSU Computer Science dari nol")
        self.assertEqual(routed["core_mission"], "1_belajar_jadi_guru")
        self.assertEqual(routed["lead_bot"], "shizuka")
        self.assertTrue(any("msshi ossu" in item for item in routed["plugins_and_tools"]))

    def test_beginner_learning_mode_chalk_learnloop_codecoach_and_routing(self):
        import msshi_learn as learn_mod

        # belajar-pemula bundled across ALL 5 bots and BOTH Academic presets
        sm = (ROOT / "skills" / "belajar-pemula" / "SKILL.md").read_text(encoding="utf-8-sig")
        desc = sm.split("---")[1].split("description:", 1)[1].strip()
        self.assertLessEqual(len(desc), 1024)
        matrix = json.loads((ROOT / "configs" / "bot_role_and_skill_matrix.json").read_text(encoding="utf-8-sig"))
        academic = json.loads((ROOT / "configs" / "academic_presets.json").read_text(encoding="utf-8-sig"))
        for bot in matrix["bots"]:
            self.assertIn("belajar-pemula", bot["required_skills"])
        for preset_id in ("academic-mahasiswa", "academic-dosen"):
            for role, skills in academic["presets"][preset_id]["roles"].items():
                self.assertIn("belajar-pemula", skills, f"belajar-pemula missing on {role} in {preset_id}")

        # Chalk MIT vendored code-only (no large docs/*.png)
        chalk_dir = ROOT / "hermes_plugins" / "chalk"
        for req in ("LICENSE", "plugin.yaml", "__init__.py", "lesson.py", "desktop/plugin.js"):
            self.assertTrue((chalk_dir / req).is_file(), f"Missing chalk file {req}")
        self.assertFalse((chalk_dir / "docs").exists())
        total_bytes = sum(p.stat().st_size for p in chalk_dir.rglob("*") if p.is_file())
        self.assertLess(total_bytes, 150_000)

        # LearnLoop (AGPL-3.0) and CodeCoach (large 5.1 MB) MUST NOT be vendored in MIT repo
        self.assertFalse((ROOT / "hermes_plugins" / "learnloop").exists())
        self.assertFalse((ROOT / "skills" / "learnloop").exists())
        self.assertFalse((ROOT / "hermes_plugins" / "codecoach").exists())

        # Deterministic beginner routing (0 LLM calls, no slash commands required)
        for topic, expected_mode in (
            ("ekonomi dasar", "guided_concept"),
            ("gambar cara kerja transformer di papan tulis", "visual_concept"),
            ("python dari nol coding pertama", "coding_beginner"),
            ("kurikulum ossu ilmu komputer", "ossu_cs_university"),
        ):
            r = learn_mod.route_beginner_topic(topic)
            self.assertEqual(r["mode"], expected_mode)
            self.assertFalse(r["slash_command_required"])

        routed = sysmod.route_task("Saya pemula total belum paham dari nol mau ajarin python")
        self.assertEqual(routed["core_mission"], "1_belajar_jadi_guru")
        self.assertIn("belajar-pemula", routed["recommended_skills"])

    def test_beginner_research_scope_and_chat_prompts(self):
        from msshi_learn import route_beginner_topic

        for topic, mode, lead in (
            ("Riset dari nol", "research_beginner", "shizuka"),
            ("skripsi tentang algoritma Python", "research_beginner", "shizuka"),
            ("cara membuat penelitian", "research_beginner", "shizuka"),
            ("python dari nol untuk skripsi", "coding_beginner", "shikaku"),
            ("diagram untuk tugas akhir", "visual_concept", "shizuka"),
            ("menulis deskripsi dari nol", "guided_concept", "shizuka"),
            ("hipotesis dari nol", "guided_concept", "shizuka"),
        ):
            with self.subTest(topic=topic):
                plan = route_beginner_topic(topic)
                self.assertEqual((plan["mode"], plan["lead_bot"]), (mode, lead))
                self.assertIn(topic, plan["try_in_hermes_chat"])
                self.assertEqual(plan["try_in_hermes_chat"].casefold().count("dari nol"), topic.casefold().count("dari nol"))
                if mode == "research_beginner":
                    self.assertTrue(any("Val" in tool for tool in plan["recommended_tools"]))
        with self.assertRaises(ValueError):
            route_beginner_topic("   ")

    def test_beginner_tools_match_tutor_profile(self):
        from unittest.mock import patch
        import msshi_learn as learn_mod

        enabled = {name: {"enabled_profiles": ["yukino"]} for name in ("chalk", "learnloop", "codecoach")}
        status = {"plugins": enabled, "codecoach_platform": {"native_supported": True}}
        with patch.object(learn_mod, "learn_status", return_value=status):
            visual = learn_mod.route_beginner_topic("gambar alur", ROOT)
            self.assertIn("diagram teks", visual["try_in_hermes_chat"])
            self.assertFalse(any("learnloop" in t for t in visual["recommended_tools"]))
            coding = learn_mod.route_beginner_topic("python", ROOT)
            self.assertFalse(any("codecoach" in t for t in coding["recommended_tools"]))
            enabled["chalk"]["enabled_profiles"].append("shizuka")
            self.assertIn("Chalk", learn_mod.route_beginner_topic("gambar alur", ROOT)["try_in_hermes_chat"])

    def test_val_only_indonesian_global_deep_research_skill(self):
        skill_dir = ROOT / "skills" / "riset-mendalam-nusantara-global"
        sm = (skill_dir / "SKILL.md").read_text(encoding="utf-8-sig")
        desc = sm.split("---")[1].split("description:", 1)[1].strip()
        self.assertLessEqual(len(desc), 1024)
        refs = ("pipeline.md", "metodologi.md", "indonesia.md", "global.md", "glosarium-id-en.md", "checklist.md")
        combined = sm
        for ref in refs:
            p = skill_dir / "references" / ref
            self.assertTrue(p.is_file(), f"Missing lazy reference {ref}")
            combined += "\n" + p.read_text(encoding="utf-8-sig")
        for must_have in ("SINTA", "Garuda", "RAMA", "EYD V", "Scopus", "PRISMA 2020", "Devil's Advocate", "DOI"):
            self.assertIn(must_have, combined)
        for excluded in ("Persian", "Farsi", "Iranian", "Tehran"):
            self.assertNotIn(excluded.lower(), combined.lower())

        # Strictly Val-ONLY across bot matrix and both Academic presets
        matrix = json.loads((ROOT / "configs" / "bot_role_and_skill_matrix.json").read_text(encoding="utf-8-sig"))
        academic = json.loads((ROOT / "configs" / "academic_presets.json").read_text(encoding="utf-8-sig"))
        for bot in matrix["bots"]:
            present = "riset-mendalam-nusantara-global" in bot["required_skills"] + bot.get("optional_skills", [])
            self.assertEqual(present, bot["id"] == "val", f"Wrong scope on {bot['id']}")
        for preset_id in ("academic-mahasiswa", "academic-dosen"):
            for role, skills in academic["presets"][preset_id]["roles"].items():
                self.assertEqual("riset-mendalam-nusantara-global" in skills, role == "val", f"Wrong scope on {role}/{preset_id}")

        routed = sysmod.route_task("Saya butuh riset mendalam standar SINTA dan Scopus PRISMA untuk tesis")
        self.assertEqual(routed["core_mission"], "2_tugas_skripsi_tesis_disertasi")
        self.assertEqual(routed["lead_bot"], "val")
        self.assertIn("riset-mendalam-nusantara-global", routed["recommended_skills"])

    def test_upstreams_check_non_applying_and_git_fallback_and_doctor_connections(self):
        import os
        from unittest.mock import patch
        from urllib.error import URLError
        import msshi_context_sources as cs_mod
        import msshi_doctor as doc_mod
        import msshi_upstreams as up_mod

        # 1. Read-only non-applying upstream update check (mocked resolver, includes OSSU)
        fake_heads = {
            "https://github.com/ossu/computer-science": "f" * 40,
            "https://github.com/JuliusBrussee/caveman": "3dc497a7f858c774d6e15b25e8c6120ef3a0eda8",
        }
        chk = up_mod.check_updates(
            ids=["ossu-computer-science", "caveman"],
            workers=1,
            resolver=lambda url: fake_heads.get(url),
        )
        self.assertFalse(chk["auto_update"])
        self.assertFalse(chk["applied"])
        self.assertEqual(chk["summary"]["up_to_date"], 1)
        self.assertEqual(chk["summary"]["update_available"], 1)
        self.assertEqual(chk["updates_available"][0]["id"], "ossu-computer-science")

        # 2. Context-source git fallback triggers when api.github.com raises URLError
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "hermes-home"
            home.mkdir()
            sentinel = home / "msshi-private" / "context-sources" / "ossu-computer-science" / cs_mod.PINNED["ossu-computer-science"][1]
            with patch.object(cs_mod, "fetch", side_effect=URLError("rate limit")), \
                 patch.object(cs_mod, "_materialize_via_git", return_value=sentinel) as git_mock:
                got = cs_mod.materialize(home, "ossu-computer-science")
                self.assertEqual(got, sentinel)
                git_mock.assert_called_once()

        # 3. msshi_doctor includes read-only connections summary (6 planes, 0 network)
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {"HERMES_HOME": str(Path(tmp) / "empty-home"), "MSSHI_IGNORE_REGISTRY_HERMES_HOME": "1"}), \
                 patch("urllib.request.urlopen", side_effect=AssertionError("network forbidden")):
                rep = doc_mod.diagnose()
                self.assertIn("connections", rep)
                self.assertEqual(rep["connections"]["planes_governed"], 6)

    def test_cross_bot_lazy_skill_finder_4_layers_boundaries_and_open_confinement(self):
        import msshi_skill_finder as finder

        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "hermes-home"
            home.mkdir()
            (home / "config.yaml").write_text("model: keep\n", encoding="utf-8")
            for bot in ("yukino", "shizuka", "val", "kiki-chii", "shikaku"):
                pdir = home / "profiles" / bot
                (pdir / "skills").mkdir(parents=True)
                (pdir / "config.yaml").write_text("model: keep\n", encoding="utf-8")

            # Active skills across different bots
            (home / "profiles" / "yukino" / "skills" / "focus-my-energy").mkdir(parents=True)
            (home / "profiles" / "yukino" / "skills" / "focus-my-energy" / "SKILL.md").write_text(
                "---\nname: focus-my-energy\ndescription: Atur jadwal harian dan energi.\n---\nBody\n",
                encoding="utf-8",
            )
            (home / "profiles" / "val" / "skills" / "riset-mendalam-nusantara-global").mkdir(parents=True)
            (home / "profiles" / "val" / "skills" / "riset-mendalam-nusantara-global" / "SKILL.md").write_text(
                "---\nname: riset-mendalam-nusantara-global\ndescription: Riset mendalam SINTA Scopus skripsi tesis.\n---\nBody\n",
                encoding="utf-8",
            )
            (home / "profiles" / "kiki-chii" / "skills" / "slide-generation").mkdir(parents=True)
            (home / "profiles" / "kiki-chii" / "skills" / "slide-generation" / "SKILL.md").write_text(
                "---\nname: slide-generation\ndescription: Generate clean presentation slides and decks.\n---\nBody\n",
                encoding="utf-8",
            )

            # Archived vault (1 general skill + 1 restricted specialist skill)
            arch_pptx = home / "msshi-private" / "archived-skill-imports" / "openclaw-imports" / "pptx-pro"
            arch_pptx.mkdir(parents=True)
            (arch_pptx / "SKILL.md").write_text(
                "---\nname: pptx-pro\ndescription: Build PowerPoint presentation decks from markdown outlines.\n---\n# PPTX Pro\nSteps here.\n",
                encoding="utf-8",
            )
            arch_tfm = home / "msshi-private" / "archived-skill-imports" / "default-extras" / "timesfm-forecasting"
            arch_tfm.mkdir(parents=True)
            (arch_tfm / "SKILL.md").write_text(
                "---\nname: timesfm-forecasting\ndescription: Time series forecasting with TimesFM.\n---\nVal only.\n",
                encoding="utf-8",
            )

            # Layer 4 index builds and caches under msshi-runtime/skill-index/archive-catalog.json
            idx = finder.build_or_load_archive_index(home, refresh=True)
            self.assertEqual(idx["count"], 2)
            self.assertTrue((home / "msshi-runtime" / "skill-index" / "archive-catalog.json").is_file())

            # Auto-profile detection from env
            self.assertEqual(finder._detect_profile(None, {"HERMES_PROFILE": "Val"}), "val")
            self.assertEqual(finder._detect_profile(None, {"HERMES_HOME": str(home / "profiles" / "shikaku")}), "shikaku")
            self.assertEqual(finder._detect_profile("kiki-chii", {"HERMES_PROFILE": "val"}), "kiki-chii")

            # Query 1: Yukino asks about skripsi SINTA -> delegates to Val, never leaks Val-only archive
            r_skripsi = finder.find_skills("Saya mau mengerjakan riset skripsi SINTA, apakah ada skill?", home, profile="yukino")
            self.assertEqual(r_skripsi["llm_calls"], 0)
            self.assertTrue(any(x["slug"] == "riset-mendalam-nusantara-global" for x in r_skripsi["delegate_to_teammate"]))
            self.assertIn("val", r_skripsi["recommendation"].lower())

            # Query 2: Yukino asks about forecasting -> timesfm-forecasting NOT leaked from archive to yukino
            r_fc = finder.find_skills("prediksi forecasting timesfm", home, profile="yukino")
            self.assertFalse(any(x["slug"] == "timesfm-forecasting" for x in r_fc["archived_vault"]))

            # Query 3: Yukino asks about presentation -> finds Kiki-Chii active AND pptx-pro in archive
            r_pres = finder.find_skills("Saya mau bikin presentasi powerpoint", home, profile="yukino")
            self.assertTrue(any(x["slug"] == "slide-generation" for x in r_pres["delegate_to_teammate"]))
            self.assertTrue(any(x["slug"] == "pptx-pro" for x in r_pres["archived_vault"]))

            # Query 4: Yukino asks about OSSU CS -> finds connected university in Layer 3
            r_ossu = finder.find_skills("belajar kurikulum ossu ilmu komputer", home, profile="yukino")
            self.assertTrue(any(x["slug"] == "ossu-computer-science" for x in r_ossu["connected_sources"]))

            # --open reads 1 archived file safely for general skills, blocks specialist-only leak
            opened = finder.open_archived_skill("pptx-pro", home, profile="yukino")
            self.assertEqual(opened["slug"], "pptx-pro")
            self.assertIn("PPTX Pro", opened["content"])
            with self.assertRaises(ValueError):
                finder.open_archived_skill("timesfm-forecasting", home, profile="yukino")
            # Val IS allowed to inspect its own specialist skill if needed
            opened_val = finder.open_archived_skill("timesfm-forecasting", home, profile="val")
            self.assertEqual(opened_val["slug"], "timesfm-forecasting")


if __name__ == "__main__":
    unittest.main()
