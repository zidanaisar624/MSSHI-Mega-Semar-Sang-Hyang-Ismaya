#!/usr/bin/env python3
"""MSSHI Closed-Loop Cognitive Operating System: status, token-efficient routing, and improvement cycles.

Unifies MSSHITrim, Caveman compaction, lazy skill/source caches, msshi-interaction,
msshi-team-routing, Hermes-Dreaming, Harness2 (Propose-Probe-Compose), and Val's
research + TimesFM 2.5 forecasting stack.

Strictly read-only/deterministic: 0 LLM calls, 0 network requests, 0 provider/model mutations.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from typing import Any

sys.dont_write_bytecode = True

_SCRIPTS_DIR = str(Path(__file__).resolve().parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import msshi_hermes_profiles as hp
import msshi_light as light_mod

ROOT = Path(__file__).resolve().parents[1]
SYSTEM_MANIFEST = ROOT / "configs" / "msshi_cognitive_system.json"
TEAM_ROLES = ("yukino", "shizuka", "val", "kiki-chii", "shikaku")

_ROUTE_RULES: tuple[dict[str, Any], ...] = (
    {
        "domain": "learning",
        "mission": "1_belajar_jadi_guru",
        "keywords": (
            "belajar", "ajari", "ajarkan", "guru", "tutor", "mentor", "kuliah", "materi",
            "konsep", "latihan", "soal", "kuis", "quiz", "ujian", "paham", "pahami",
            "jelaskan", "kurikulum", "socratic", "teach", "learn", "study", "mengajar",
        ),
        "lead": "shizuka",
        "coordinator": "shizuka",
        "optional_support": ["yukino", "val", "shikaku", "kiki-chii"],
        "interaction_type": "type_1_advisor_if_complex_else_main",
        "skills": [
            "parenting-6d-gad-mdd",
            "focus-my-energy",
            "math-reasoning",
            "deep-research",
            "notebooklm-thinking-datascience",
            "harness2",
        ],
        "plugins_and_tools": [
            "msshi-auto-trim (MSSHITrim JSON compaction)",
            "parenting-6d-gad-mdd + focus-my-energy (pacing adaptif & empatik)",
            "msshi dream (simpan celah pemahaman / knowledge gaps untuk sesi belajar berikutnya)",
        ],
        "workflow": [
            "1. Cek level awal & energi pembelajar dulu (jangan langsung kirim kuliah panjang — hemat token).",
            "2. Ajarkan 1 konsep inti secara bertahap: intuisi -> analogi -> contoh nyata -> formalisasi (panggil Val/Shikaku/Kiki hanya jika topik perlu verifikasi teori, latihan kode, atau visual).",
            "3. Beri 1-2 soal cek pemahaman (Socratic / active recall) dan umpan balik sebelum lanjut ke bab berikutnya.",
            "4. Catat konsep yang dikuasai vs knowledge gap agar msshi dream & Harness2 mempertajam metode mengajar di sesi berikutnya.",
        ],
    },
    {
        "domain": "prediction",
        "mission": "2_tugas_skripsi_tesis_disertasi",
        "keywords": (
            "prediksi", "forecast", "forecasting", "ramal", "peramalan", "time series",
            "deret waktu", "timesfm", "tren", "trend", "backtest", "proyeksi", "demand",
            "horizon", "kuantil", "quantile", "regresi", "regression", "statistik",
        ),
        "lead": "val",
        "coordinator": "shizuka",
        "optional_support": ["shikaku", "kiki-chii"],
        "interaction_type": "type_2_council_if_complex_else_main",
        "skills": [
            "data-analysis",
            "timesfm-forecasting",
            "math-reasoning",
            "symbolic-equation",
            "backward-traceability",
        ],
        "plugins_and_tools": [
            "msshi-auto-trim (MSSHITrim JSON compaction)",
            "msshi timesfm status / forecast (local Apache-2.0 CPU)",
            "caveman (compact internal handoff to Shizuka)",
        ],
        "workflow": [
            "1. Val memvalidasi timestamp, unit, missing values, dan memisahkan chronological holdout (anti-leakage).",
            "2. Val membandingkan TimesFM 2.5 lokal (atau persamaan simbolik/statistik) terhadap naive & seasonal-naive baseline.",
            "3. Val melaporkan error empiris, interval ketidakpastian (quantile), dan asumsi dengan jejak bukti ke Shizuka.",
            "4. Libatkan Shikaku hanya jika butuh skrip pra-pemrosesan data; libatkan Kiki-Chii hanya jika butuh grafik publikasi.",
        ],
    },
    {
        "domain": "research",
        "mission": "2_tugas_skripsi_tesis_disertasi",
        "keywords": (
            "riset", "research", "tugas", "skripsi", "tesis", "disertasi", "jurnal", "paper",
            "makalah", "literatur", "literature", "novelty", "kebaruan", "sitasi", "doi",
            "rebuttal", "metodologi", "bab 1", "bab 2", "bab 3", "survei", "analisis data", "sidang",
        ),
        "lead": "val",
        "coordinator": "shizuka",
        "optional_support": ["yukino", "kiki-chii"],
        "interaction_type": "type_2_council_if_complex_else_main",
        "skills": [
            "deep-research",
            "literature-review",
            "novelty-assessment",
            "backward-traceability",
            "paper-context-resolver",
            "muza-skripsi-template",
        ],
        "plugins_and_tools": [
            "msshi-auto-trim (MSSHITrim JSON compaction)",
            "unlimited-ocr-2 (ekstraksi PDF berhalaman sesuai kebutuhan)",
            "caveman (ringkas dossier internal Val -> Shizuka)",
        ],
        "workflow": [
            "1. Pakai Lima Lapis Konteks: peta dokumen dulu, ekstrak hanya halaman relevan, simpan penunjuk doc#halaman.",
            "2. Val menelusuri bukti, menguji klaim kebaruan, dan menyusun dossier terverifikasi dengan backward-traceability.",
            "3. Shizuka mensintesis temuan menjadi naskah tugas/skripsi/tesis/disertasi (termasuk muza-skripsi-template & humanizer) tanpa membangunkan bot yang tidak relevan.",
            "4. Catat keputusan riset terverifikasi untuk refleksi msshi dream dan evaluasi Harness2.",
        ],
    },
    {
        "domain": "security",
        "mission": "4_coding",
        "keywords": (
            "security", "keamanan", "threat model", "stride", "pasta", "linddun", "grim-prompter",
            "bughunter", "bug bounty", "kerentanan", "vulnerability", "audit keamanan", "pentest",
            "owasp", "xss", "sqli", "ssrf", "idor", "csrf", "oauth", "privasi", "gdpr", "ccpa",
        ),
        "lead": "shikaku",
        "coordinator": "shizuka",
        "optional_support": ["val"],
        "interaction_type": "type_2_council_if_complex_else_main",
        "skills": [
            "analyze-project",
            "grim-prompter",
            "claude-bughunter",
            "antigravity-webdev-cybersec",
        ],
        "plugins_and_tools": [
            "msshi integrations source --name grim-prompter (read-only threat modeling)",
            "msshi integrations source --name claude-bughunter --skill <kelas> (muat 1 skill saja)",
            "msshi-auto-trim (MSSHITrim JSON compaction)",
        ],
        "workflow": [
            "1. Verifikasi izin/scope tertulis (aset milik sendiri, bug bounty in-scope, atau lab/CTF berizin).",
            "2. Mulai read-only dengan grim-prompter untuk memetakan trust boundaries & ancaman berbasis bukti kode.",
            "3. Muat HANYA 1-2 skill relevan dari cache claude-bughunter (--skill) untuk triage-validation & evidence-hygiene.",
            "4. Terapkan perbaikan dengan TDD (mattpocock-engineering) dan laporkan bukti verifikasi ke Shizuka.",
        ],
    },
    {
        "domain": "coding",
        "mission": "4_coding",
        "keywords": (
            "kode", "code", "coding", "bug", "debug", "refactor", "arsitektur", "api", "web",
            "backend", "frontend", "script", "python", "javascript", "typescript", "flutter",
            "test", "tdd", "benchmark", "optimasi", "harness", "harness2", "plugin", "cli",
        ),
        "lead": "shikaku",
        "coordinator": "shizuka",
        "optional_support": ["val"],
        "interaction_type": "type_2_council_if_complex_else_main",
        "skills": [
            "analyze-project",
            "explore-code",
            "mattpocock-engineering",
            "explore-run",
            "harness2",
        ],
        "plugins_and_tools": [
            "msshi-auto-trim (MSSHITrim JSON compaction)",
            "msshi integrations source --name mattpocock-skills --skill <disiplin>",
            "msshi harness2 plan (jika memperbaiki alur/prompt/script berulang)",
        ],
        "workflow": [
            "1. Petakan struktur & risiko perubahan dengan analyze-project sebelum mengedit kode.",
            "2. Implementasi perubahan terisolasi dengan disiplin TDD (mattpocock-engineering) dan uji regresi.",
            "3. Gunakan MSSHITrim otomatis untuk hasil tool JSON besar dan caveman untuk handoff internal.",
            "4. Jika ada kegagalan berulang, buat proposal Harness2 Propose-Probe-Compose untuk tinjauan pengguna.",
        ],
    },
    {
        "domain": "creative",
        "mission": "3_konten_kreasi",
        "keywords": (
            "konten", "kreasi", "video", "film", "foto", "fotografi", "desain", "design", "ui", "ux",
            "slide", "presentasi", "ppt", "grafik", "plot", "motion", "animasi", "storyboard",
            "thumbnail", "brand", "remake", "visual", "brag", "unslop", "youtube", "reels", "tiktok",
        ),
        "lead": "kiki-chii",
        "coordinator": "shizuka",
        "optional_support": ["yukino", "val", "shikaku"],
        "interaction_type": "type_2_council_if_complex_else_main",
        "skills": [
            "filmmaking-videography-photography-s2",
            "motion-graphics-suite",
            "academic-plotting",
            "slide-generation",
            "unslop",
            "rea-video",
            "brag",
        ],
        "plugins_and_tools": [
            "msshi-auto-trim (MSSHITrim JSON compaction)",
            "msshi integrations source --name rea-video (bedah video lokal ringan --no-vlm)",
            "cli-anything-universal-bridge (on-demand task ticket, auto_open_on_boot=false)",
        ],
        "workflow": [
            "1. Mulai dengan Concepting First (hook, storyboard, gaya visual) dan review manusia sebelum rendering/produksi berat.",
            "2. Untuk video referensi, jalankan rea-video lokal ringan (--no-vlm) dan baca VIDEO.md terlebih dahulu.",
            "3. Untuk grafik ilmiah/slide, ambil angka terverifikasi dari Val sebelum visualisasi.",
        ],
    },
    {
        "domain": "companion_daily",
        "mission": "5_teman_curhat_dan_daily_scheduling",
        "keywords": (
            "curhat", "capek", "stres", "stress", "lelah", "galau", "sedih", "cemas",
            "overwhelmed", "ngobrol", "daily", "harian", "jadwal", "schedule", "scheduling",
            "agenda", "to-do", "todo", "reminder", "pengingat", "rutinitas", "routine",
            "kebiasaan", "habit", "energi", "semangat", "teman bicara", "check-in",
        ),
        "lead": "yukino",
        "coordinator": "shizuka",
        "optional_support": [],
        "interaction_type": "fast_main_only",
        "skills": [
            "parenting-6d-gad-mdd",
            "focus-my-energy",
            "prep-for-meetings",
            "prep-for-meetings-2",
        ],
        "plugins_and_tools": [
            "Main-only mode (0 sub-agent / 0 Dewan — hemat token maksimal)",
            "parenting-6d-gad-mdd + focus-my-energy (empati hangat & manajemen energi)",
            "prep-for-meetings / daily scheduling checklist (tanpa mengubah akun eksternal tanpa izin)",
        ],
        "workflow": [
            "1. Jalankan Main-only di Yukino (0 delegasi bot lain) agar percakapan hangat, cepat, dan hemat token.",
            "2. Dengarkan dengan empati & dukungan otonomi (gaya bahasa alami, bukan caveman; bukan pengganti layanan klinis).",
            "3. Untuk daily scheduling/agenda, pecah rencana hari ini sesuai energi pengguna menjadi 1-3 langkah kecil yang realistis.",
            "4. Eskalasi ke Shizuka/spesialis HANYA jika pengguna secara eksplisit meminta proyek teknis/akademik dari obrolan tersebut.",
        ],
    },
    {
        "domain": "ideation_and_learning",
        "mission": "0_ideasi_dan_orkestrasi",
        "keywords": (
            "ide", "brainstorm", "rencana", "plan", "strategi", "rapat", "meeting", "prioritas",
            "dream", "dreaming", "refleksi", "evaluasi", "makin pintar", "memori",
        ),
        "lead": "yukino",
        "coordinator": "shizuka",
        "optional_support": ["val"],
        "interaction_type": "type_1_advisor_if_complex_else_main",
        "skills": [
            "brainstorming-research-ideas",
            "idea-generation",
            "wise-judgment-and-sovereign-orchestrator",
            "autoresearch",
            "harness2",
        ],
        "plugins_and_tools": [
            "msshi dream (distilasi pelajaran offline ke memories/DREAMS.md, 0 LLM calls)",
            "msshi harness2 plan (proposal perbaikan terisolasi berdasar kegagalan nyata)",
            "caveman (ringkas handoff Yukino -> Shizuka)",
        ],
        "workflow": [
            "1. Yukino menampung ide, energi, dan prioritas awal tanpa memicu riset/kode prematur.",
            "2. Shizuka memecah proyek terkonfirmasi hanya ke spesialis yang dibutuhkan.",
            "3. Setelah sesi selesai, jalankan msshi dream (offline) dan tinjau proposal Harness2 bila ada pola error berulang.",
        ],
    },
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _profile_map(home: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    if home.is_dir():
        result["default"] = home
    for name, folder in sorted(hp.live_named_profiles(home).items()):
        result[name] = folder
    return result


def _read_trim_savings(home: Path, profiles: dict[str, Path]) -> dict[str, Any]:
    enabled_profiles: list[str] = []
    binary_present = any((home / "tools" / "llmtrim" / name).is_file() for name in ("llmtrim.exe", "llmtrim"))
    desktop_ui_present = (home / "desktop-plugins" / "msshi-auto-trim" / "plugin.js").is_file()
    for name, folder in profiles.items():
        cfg_path = folder / "config.yaml"
        if not cfg_path.is_file():
            continue
        try:
            cfg = hp.load_yaml_mapping(cfg_path)
        except (OSError, ValueError):
            continue
        plugins = cfg.get("plugins") if isinstance(cfg.get("plugins"), dict) else {}
        enabled = plugins.get("enabled") if isinstance(plugins.get("enabled"), list) else []
        disabled = plugins.get("disabled") if isinstance(plugins.get("disabled"), list) else []
        if "msshi-auto-trim" in enabled and "msshi-auto-trim" not in disabled:
            enabled_profiles.append(name)
    return {
        "enabled_profiles": enabled_profiles,
        "enabled_count": len(enabled_profiles),
        "total_profiles": len(profiles),
        "binary_present": binary_present,
        "desktop_ui_staged": desktop_ui_present,
    }


def _plugin_coverage(profiles: dict[str, Path], plugin_id: str) -> list[str]:
    found: list[str] = []
    for name, folder in profiles.items():
        cfg_path = folder / "config.yaml"
        if not cfg_path.is_file():
            continue
        try:
            cfg = hp.load_yaml_mapping(cfg_path)
        except (OSError, ValueError):
            continue
        plugins = cfg.get("plugins") if isinstance(cfg.get("plugins"), dict) else {}
        enabled = plugins.get("enabled") if isinstance(plugins.get("enabled"), list) else []
        disabled = plugins.get("disabled") if isinstance(plugins.get("disabled"), list) else []
        if plugin_id in enabled and plugin_id not in disabled:
            found.append(name)
    return found


def _skill_coverage(profiles: dict[str, Path], slug: str) -> list[str]:
    return [name for name, folder in profiles.items() if (folder / "skills" / slug / "SKILL.md").is_file()]


def system_status(home: Path, *, source_root: Path = ROOT) -> dict[str, Any]:
    """Read-only readiness inspection of all 4 MSSHI Cognitive System pillars (0 LLM/network calls)."""
    home = Path(home).expanduser().absolute()
    manifest = _read_json(source_root / "configs" / "msshi_cognitive_system.json")
    profiles = _profile_map(home)
    rp = light_mod.read_resource_profile(home) if home.is_dir() else {"profile": "normal", "configured": False}

    # Pillar 1: Token Efficiency
    trim_info = _read_trim_savings(home, profiles)
    caveman_profiles = _skill_coverage(profiles, "caveman")
    skill_cache_dir = home / "msshi-runtime" / "skill-index"
    skill_cache_files = sorted(p.name for p in skill_cache_dir.glob("*.json")) if skill_cache_dir.is_dir() else []
    import msshi_context_sources as context_sources

    cached_sources: dict[str, dict[str, Any]] = {}
    for src_name, (repo_id, pin) in context_sources.PINNED.items():
        marker = home / "msshi-private" / "context-sources" / src_name / pin / "MSSHI_SNAPSHOT.json"
        if marker.is_file() and not marker.is_symlink():
            try:
                snap = _read_json(marker)
                files_map = snap.get("files") if isinstance(snap.get("files"), dict) else {}
                ok = snap.get("repository") == repo_id and snap.get("commit") == pin and bool(files_map)
                cached_sources[src_name] = {"cached": ok, "files": len(files_map) if ok else 0, "commit": pin}
            except (OSError, ValueError):
                cached_sources[src_name] = {"cached": False, "files": 0, "commit": pin}
        else:
            cached_sources[src_name] = {"cached": False, "files": 0, "commit": pin}

    # Pillar 2: Continuous Learning (Dreaming + Harness2)
    harness2_profiles = _skill_coverage(profiles, "harness2")
    harness2_runtime = home / "msshi-private" / "harness2-runtime"
    harness2_ready = any((harness2_runtime / m).is_file() for m in ("INSTALLATION.json", "installed.json"))
    dream_dir = home / "msshi-private" / "integrations" / "dream"
    dream_reports = sorted(p.name for p in dream_dir.glob("*-latest.json")) if dream_dir.is_dir() else []
    dream_source_cached = (home / "msshi-private" / "v3-sources" / "hermes-dreaming").is_dir()

    # Pillar 3: Research & Prediction (Val + TimesFM + Security/Engineering)
    timesfm_profiles = _skill_coverage(profiles, "timesfm-forecasting")
    timesfm_runtime = home / "msshi-private" / "timesfm-runtime"
    timesfm_ready = any((timesfm_runtime / m).is_file() for m in ("INSTALLATION.json", "installed.json"))
    grim_profiles = _skill_coverage(profiles, "grim-prompter")
    bughunter_profiles = _skill_coverage(profiles, "claude-bughunter")
    research_profiles = _skill_coverage(profiles, "deep-research")

    # Pillar 4: Governance & Orchestration
    routing_profiles = _plugin_coverage(profiles, "msshi-team-routing")
    interaction_profiles = _plugin_coverage(profiles, "msshi-interaction")
    bridge_profiles = _skill_coverage(profiles, "cli-anything-universal-bridge")

    # Preset parity check from repo
    matrix = _read_json(source_root / "configs" / "bot_role_and_skill_matrix.json")
    academic = _read_json(source_root / "configs" / "academic_presets.json")
    preset_harness2 = {
        "muza-preset": all("harness2" in b.get("required_skills", []) for b in matrix.get("bots", [])),
        "academic-mahasiswa": all("harness2" in skills for skills in academic["presets"]["academic-mahasiswa"]["roles"].values()),
        "academic-dosen": all("harness2" in skills for skills in academic["presets"]["academic-dosen"]["roles"].values()),
    }
    preset_timesfm = {
        "muza-preset": any(b["id"] == "val" and "timesfm-forecasting" in b.get("required_skills", []) for b in matrix.get("bots", [])),
        "academic-mahasiswa": "timesfm-forecasting" in academic["presets"]["academic-mahasiswa"]["roles"].get("val", []),
        "academic-dosen": "timesfm-forecasting" in academic["presets"]["academic-dosen"]["roles"].get("val", []),
    }

    return {
        "system": manifest["name"],
        "version": manifest["version"],
        "core_missions": [m["id"] for m in manifest.get("core_missions", [])],
        "hermes_home": str(home),
        "profiles_detected": list(profiles),
        "resource_profile": rp.get("profile", "normal"),
        "preset_parity": {
            "harness2_all_bots": preset_harness2,
            "timesfm_on_val": preset_timesfm,
        },
        "pillars": {
            "1_token_efficiency": {
                "msshi_trim": trim_info,
                "caveman_profiles": caveman_profiles,
                "skill_index_cache_files": len(skill_cache_files),
                "external_context_sources": cached_sources,
                "interaction_gating_profiles": interaction_profiles,
            },
            "2_continuous_learning": {
                "harness2_skill_profiles": harness2_profiles,
                "harness2_runtime_ready": harness2_ready,
                "dreaming_source_cached": dream_source_cached,
                "dreaming_reports": dream_reports,
                "auto_promotion": False,
                "human_review_required": True,
            },
            "3_research_and_prediction": {
                "deep_research_profiles": research_profiles,
                "timesfm_skill_profiles": timesfm_profiles,
                "timesfm_runtime_ready": timesfm_ready,
                "timesfm_install_command": "msshi timesfm install",
                "coder_security_profiles": {
                    "grim_prompter": grim_profiles,
                    "claude_bughunter": bughunter_profiles,
                },
            },
            "4_governance_and_routing": {
                "team_routing_profiles": routing_profiles,
                "interaction_profiles": interaction_profiles,
                "universal_bridge_profiles": bridge_profiles,
            },
        },
        "guardrails": {
            "model_calls": 0,
            "network_requests": 0,
            "provider_model_mutated": False,
            "auto_open_on_boot": False,
        },
    }


def route_task(task: str, *, low_ram: bool = False) -> dict[str, Any]:
    """Deterministic, 0-LLM-call task router choosing the minimal token-efficient pipeline."""
    cleaned = (task or "").strip()
    if not cleaned:
        raise ValueError("Task description must not be empty.")
    low = cleaned.casefold()
    words = re.findall(r"[a-z0-9_-]+", low)
    is_brief = len(words) <= 6 and not any(
        k in low for k in (
            "belajar", "ajari", "ajarkan", "guru", "tutor", "kuis", "ujian",
            "riset", "prediksi", "forecast", "tugas", "skripsi", "tesis", "disertasi",
            "konten", "kreasi", "video", "desain", "slide",
            "coding", "kode", "code", "audit", "threat", "bangun", "build", "analisis",
            "curhat", "jadwal", "schedule", "scheduling", "agenda", "rutinitas",
        )
    )

    scores: list[tuple[int, dict[str, Any]]] = []
    for rule in _ROUTE_RULES:
        hits = sum(1 for kw in rule["keywords"] if kw in low)
        if hits:
            scores.append((hits, rule))
    scores.sort(key=lambda item: item[0], reverse=True)

    if not scores:
        chosen = _ROUTE_RULES[-1]  # ideation_and_learning
        matched_domains = ["general"]
    else:
        chosen = scores[0][1]
        matched_domains = [item[1]["domain"] for item in scores[:2]]

    interaction_mode = "fast_main_only" if is_brief else chosen["interaction_type"]
    if low_ram and interaction_mode == "type_2_council_if_complex_else_main":
        interaction_mode = "sequential_single_inference_low_ram"

    return {
        "task": cleaned,
        "core_mission": chosen.get("mission", "0_ideasi_dan_orkestrasi"),
        "primary_domain": chosen["domain"] if scores else "general",
        "secondary_domains": matched_domains[1:],
        "lead_bot": chosen["lead"],
        "coordinator_bot": chosen["coordinator"],
        "optional_support_bots": [] if is_brief else list(chosen["optional_support"]),
        "wake_all_bots": False,
        "interaction_mode": interaction_mode,
        "recommended_skills": list(chosen["skills"][: (2 if is_brief else 6)]),
        "token_efficiency_stack": [
            "MSSHITrim (otomatis memadatkan output JSON tool >= 2048 karakter)",
            "Lazy context-sources (muat 1 file saja dari msshi-private/context-sources)",
            "Caveman compact handoff (hanya untuk pesan internal antar-bot)",
            "Main-only untuk obrolan singkat (tanpa membangunkan Advisor/Dewan)",
        ],
        "plugins_and_tools": list(chosen["plugins_and_tools"]),
        "workflow_steps": list(chosen["workflow"]),
        "learning_followup": (
            "Setelah tugas selesai, simpan keputusan + penunjuk bukti (doc#halaman / file:baris); "
            "jalankan `msshi dream` secara berkala (offline) dan `msshi harness2 plan` bila ditemukan pola kegagalan berulang."
        ),
        "model_calls": 0,
    }


def plan_cycle(home: Path, goal: str, *, domain: str = "general") -> dict[str, Any]:
    """Build a human-reviewable Research, Prediction & Self-Improvement Cycle brief (0 LLM calls)."""
    goal_clean = (goal or "").strip()
    if not goal_clean:
        raise ValueError("Goal must not be empty.")
    home = Path(home).expanduser().absolute()
    route = route_task(f"{domain} {goal_clean}")
    status = system_status(home)
    timesfm_ready = status["pillars"]["3_research_and_prediction"]["timesfm_runtime_ready"]
    harness2_ready = status["pillars"]["2_continuous_learning"]["harness2_runtime_ready"]
    return {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "goal": goal_clean,
        "domain": domain,
        "hermes_home": str(home),
        "routing": {
            "lead_bot": route["lead_bot"],
            "coordinator_bot": route["coordinator_bot"],
            "optional_support_bots": route["optional_support_bots"],
            "skills": route["recommended_skills"],
        },
        "phases": [
            {
                "phase": "1_token_budget_and_context",
                "actions": [
                    "Gunakan indeks skill lazy dan ambil maksimal 1-2 sumber terpin dari msshi-private/context-sources/.",
                    "Biarkan MSSHITrim memadatkan hasil tool JSON besar secara lossless (0 LLM calls).",
                    "Pakai format ringkas Caveman hanya untuk handoff internal antar-bot.",
                ],
            },
            {
                "phase": "2_research_or_prediction_execution",
                "actions": route["workflow_steps"],
                "timesfm_ready": timesfm_ready,
                "timesfm_note": (
                    "TimesFM 2.5 CPU siap untuk forecast lokal dengan chronological holdout."
                    if timesfm_ready
                    else "Skill timesfm-forecasting tersedia; jalankan `msshi timesfm install` hanya jika ingin mengunduh runtime CPU + bobot Apache-2.0 (~925 MB)."
                ),
            },
            {
                "phase": "3_offline_reflection_dreaming",
                "command": f'msshi dream --home "{home}"',
                "actions": [
                    "Distilasi pelajaran deterministik ke memories/DREAMS.md (0 panggilan LLM).",
                    "Tinjau secara manual sebelum mempromosikan pelajaran apa pun ke memori aktif.",
                ],
            },
            {
                "phase": "4_harness2_propose_probe_compose",
                "harness2_runtime_ready": harness2_ready,
                "command": f'msshi harness2 --hermes-home "{home}" plan --goal "{goal_clean}"',
                "actions": [
                    "Ubah kegagalan/bottleneck yang terukur menjadi hipotesis perubahan kecil pada salinan terisolasi.",
                    "Bandingkan baseline vs kandidat pada tugas probe & holdout terpisah (Val bukti, Shikaku diff, Shizuka sintesis).",
                    "Terapkan hanya setelah persetujuan pengguna dan simpan rollback receipt; bobot model & SOUL tidak diubah otomatis.",
                ],
            },
        ],
        "guardrails": {
            "model_calls": 0,
            "auto_promotion": False,
            "provider_model_mutated": False,
            "human_approval_required": True,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="msshi system", description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)

    p_status = sub.add_parser("status", help="Inspect readiness of all 4 MSSHI Cognitive System pillars (0 LLM calls).")
    p_status.add_argument("--home", type=Path, help="Hermes data root (auto-detected if omitted).")
    p_status.add_argument("--json", action="store_true", help="Output machine-readable JSON.")

    p_route = sub.add_parser("route", help="Deterministically choose the minimal token-efficient bot/skill pipeline.")
    p_route.add_argument("--task", required=True, help="Short description of the user task.")
    p_route.add_argument("--low-ram", action="store_true", help="Apply Low-RAM sequential gating.")
    p_route.add_argument("--json", action="store_true", help="Output machine-readable JSON.")

    p_cycle = sub.add_parser("cycle", help="Generate a closed-loop Research, Prediction & Harness2/Dreaming cycle brief.")
    p_cycle.add_argument("--home", type=Path, help="Hermes data root (auto-detected if omitted).")
    p_cycle.add_argument("--goal", required=True, help="Target research, prediction, or system improvement hypothesis.")
    p_cycle.add_argument("--domain", choices=("general", "learning", "research", "prediction", "coding", "security", "creative", "daily"), default="general")
    p_cycle.add_argument("--json", action="store_true", help="Output machine-readable JSON.")

    args = parser.parse_args(argv)
    try:
        if args.action == "status":
            home = hp.resolve_hermes_home(args.home)
            report = system_status(home)
            if args.json:
                print(json.dumps(report, ensure_ascii=False, indent=2))
            else:
                p1 = report["pillars"]["1_token_efficiency"]
                p2 = report["pillars"]["2_continuous_learning"]
                p3 = report["pillars"]["3_research_and_prediction"]
                p4 = report["pillars"]["4_governance_and_routing"]
                print(f"=== {report['system']} (v{report['version']}) ===")
                print(f"5 Misi Utama      : {', '.join(report['core_missions'])}")
                print(f"Hermes Home       : {report['hermes_home']} ({len(report['profiles_detected'])} profil)")
                print(f"1. Hemat Token    : MSSHITrim={p1['msshi_trim']['enabled_count']}/{p1['msshi_trim']['total_profiles']}, "
                      f"Caveman={len(p1['caveman_profiles'])}, "
                      f"CachedSources={sum(1 for v in p1['external_context_sources'].values() if v['cached'])}/{len(p1['external_context_sources'])}")
                print(f"2. Makin Pintar   : Harness2 skills={len(p2['harness2_skill_profiles'])} profil (runtime_ready={p2['harness2_runtime_ready']}), "
                      f"Dreaming source={p2['dreaming_source_cached']}")
                print(f"3. Riset/Prediksi : DeepResearch={len(p3['deep_research_profiles'])}, "
                      f"TimesFM skill={len(p3['timesfm_skill_profiles'])} (runtime_ready={p3['timesfm_runtime_ready']}), "
                      f"CoderSecurity=(grim={len(p3['coder_security_profiles']['grim_prompter'])}, bughunter={len(p3['coder_security_profiles']['claude_bughunter'])})")
                print(f"4. Orkestrasi     : TeamRouting={len(p4['team_routing_profiles'])}, "
                      f"Interaction={len(p4['interaction_profiles'])}, Bridge={len(p4['universal_bridge_profiles'])}")
            return 0
        if args.action == "route":
            result = route_task(args.task, low_ram=args.low_ram)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.action == "cycle":
            home = hp.resolve_hermes_home(args.home)
            result = plan_cycle(home, args.goal, domain=args.domain)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    except (OSError, ValueError) as exc:
        parser.exit(1, f"msshi system: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
