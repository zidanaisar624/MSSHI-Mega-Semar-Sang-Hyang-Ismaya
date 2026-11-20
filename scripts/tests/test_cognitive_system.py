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
        self.assertEqual(cov["connection_planes_governed"], 5)
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
                            "Coding",
                            "Daily companion/curhat",
                            "MSSHITrim",
                            "caveman",
                            "timesfm-forecasting",
                            "grim-prompter",
                            "claude-bughunter",
                            "msshi dream",
                            "harness2",
                            "never auto-promote",
                        ):
                            self.assertIn(token, policy)


if __name__ == "__main__":
    unittest.main()
