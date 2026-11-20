#!/usr/bin/env python3
"""Optional MSSHI bridge helper for Imagination Studio (Kiki-Chii Filmmaker collaboration).

Strictly read-only & deterministic by default: 0 LLM calls, 0 network requests,
0 auto-starts, 0 model downloads, and 0 provider/model mutations.
Explicit --probe connects ONLY to a loopback Imagination Studio URL (127.0.0.1/localhost/::1).
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

sys.dont_write_bytecode = True

_HERE = Path(__file__).resolve()
for _candidate in (_HERE.parent, _HERE.parents[1] / "scripts", _HERE.parents[2] / "scripts"):
    if _candidate.is_dir() and str(_candidate) not in sys.path:
        sys.path.insert(0, str(_candidate))

UPSTREAM_REPO = "https://github.com/Keys-Wasserman/Imagination-Studio-by-keys-Wasserman"
UPSTREAM_COMMIT = "16f00b462a5a389e2c5e19c2cbf7d9527ad526ea"
HERMES_PLUGIN_URL = "https://hermeswatcher.com/plugins/imagination-studio"
DEFAULT_STUDIO_URL = "http://127.0.0.1:7870"
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
HERMES_PLUGIN_TOOLS = (
    "studio_status",
    "studio_picture",
    "studio_clip",
    "studio_voice",
    "studio_song",
    "studio_sound",
    "studio_job",
    "studio_jobs",
    "studio_cancel",
    "studio_library",
)


def _validate_loopback_url(url: str) -> str:
    parsed = urllib.parse.urlparse((url or "").strip())
    if parsed.scheme not in {"http", "https"} or parsed.hostname not in LOOPBACK_HOSTS:
        raise ValueError(
            f"Refusing non-loopback Studio URL {url!r}. Only http(s)://127.0.0.1, localhost, or [::1] is permitted."
        )
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("Studio URL must not contain credentials, query strings, or fragments.")
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


def _resolve_home(explicit: Path | None) -> Path:
    try:
        import msshi_hermes_profiles as hp
        return hp.resolve_hermes_home(explicit)
    except Exception:
        if explicit is not None:
            return Path(explicit).expanduser().absolute()
        env = (os.environ.get("HERMES_HOME") or "").strip()
        if env:
            return Path(env).expanduser().absolute()
        return (Path.home() / ".hermes").absolute()


def _detect_ram_gib() -> float | None:
    try:
        import msshi_light as light_mod
        hw = light_mod.detect_hardware_ram()
        val = hw.get("physical_gib")
        return float(val) if val is not None else None
    except Exception:
        return None


def _plugin_enabled(config_path: Path, plugin_id: str) -> bool:
    if not config_path.is_file():
        return False
    try:
        import msshi_hermes_profiles as hp
        cfg = hp.load_yaml_mapping(config_path)
    except Exception:
        return False
    plugins = cfg.get("plugins") if isinstance(cfg.get("plugins"), dict) else {}
    enabled = plugins.get("enabled") if isinstance(plugins.get("enabled"), list) else []
    disabled = plugins.get("disabled") if isinstance(plugins.get("disabled"), list) else []
    return plugin_id in enabled and plugin_id not in disabled


def _probe_studio(base_url: str, timeout: float = 2.0) -> dict[str, Any]:
    safe_url = _validate_loopback_url(base_url)
    result: dict[str, Any] = {
        "probed": True,
        "url": safe_url,
        "reachable": False,
        "headroom_mb": None,
        "running_jobs": None,
        "error": None,
    }
    try:
        req = urllib.request.Request(f"{safe_url}/api/memory", headers={"User-Agent": "msshi-studio-check"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            mem = json.loads(resp.read().decode("utf-8", errors="replace"))
        result["reachable"] = True
        if isinstance(mem, dict):
            result["headroom_mb"] = mem.get("headroom_mb")
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        result["error"] = f"Studio not reachable at {safe_url}: {exc}"
        return result

    try:
        req_jobs = urllib.request.Request(f"{safe_url}/api/jobs", headers={"User-Agent": "msshi-studio-check"})
        with urllib.request.urlopen(req_jobs, timeout=timeout) as resp:
            jobs = json.loads(resp.read().decode("utf-8", errors="replace"))
        if isinstance(jobs, list):
            result["running_jobs"] = sum(1 for j in jobs if isinstance(j, dict) and j.get("status") == "running")
        elif isinstance(jobs, dict) and isinstance(jobs.get("jobs"), list):
            result["running_jobs"] = sum(1 for j in jobs["jobs"] if isinstance(j, dict) and j.get("status") == "running")
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        pass
    return result


def studio_status(
    home: Path | None = None,
    *,
    url: str = DEFAULT_STUDIO_URL,
    probe: bool = False,
) -> dict[str, Any]:
    """Read-only readiness audit for Imagination Studio + Kiki-Chii Filmmaker collaboration."""
    resolved = _resolve_home(home)
    safe_url = _validate_loopback_url(url)
    kiki_root = resolved / "profiles" / "kiki-chii"
    wrapper_present = (kiki_root / "skills" / "imagination-studio" / "SKILL.md").is_file()
    filmmaker_present = (kiki_root / "skills" / "filmmaking-videography-photography-s2" / "SKILL.md").is_file()
    hermes_plugin_enabled = _plugin_enabled(kiki_root / "config.yaml", "imagination-studio")
    ram_gib = _detect_ram_gib()
    high_ram_local_ready = ram_gib is not None and ram_gib >= 32.0

    probe_info = _probe_studio(safe_url) if probe else {
        "probed": False,
        "url": safe_url,
        "reachable": None,
        "note": "Offline status check (0 network requests). Pass --probe to check local http://127.0.0.1:7870.",
    }

    return {
        "integration": "imagination-studio",
        "optional_public_default": False,
        "owner_role": "kiki-chii",
        "collaborates_with": ["filmmaking-videography-photography-s2", "motion-graphics-suite", "rea-video", "brag"],
        "upstream": {
            "repository": UPSTREAM_REPO,
            "pinned_commit": UPSTREAM_COMMIT,
            "license": "Apache-2.0 (ships zero weights; credit Keys & Sam Wasserman / Wasserman Productions)",
            "hermes_plugin_listing": HERMES_PLUGIN_URL,
        },
        "hermes_home": str(resolved),
        "kiki_chii": {
            "profile_exists": kiki_root.is_dir(),
            "optional_wrapper_enabled": wrapper_present,
            "filmmaker_partner_present": filmmaker_present,
            "collaboration_ready": wrapper_present and filmmaker_present,
            "hermes_plugin_enabled": hermes_plugin_enabled,
        },
        "hardware_guidance": {
            "physical_ram_gib": ram_gib,
            "full_local_gpu_suite_advisory": (
                "Full local video/image models target high-RAM Apple Silicon / DGX Spark / RTX Spark (up to 128 GiB). "
                "On 4-16 GB RAM laptops, use Slate planning locally, bridge via remote ComfyUI/Comfy Cloud, "
                "or fall back seamlessly to ArtCraft / Motion-as-Code / Higgsfield."
            ),
            "high_ram_local_candidate": high_ram_local_ready,
        },
        "local_studio_probe": probe_info,
        "setup_commands": {
            "enable_msshi_wrapper": f'msshi optional enable imagination-studio --target-dir "{kiki_root / "skills"}"',
            "install_hermes_plugin": "hermes plugins install imagination-studio && hermes plugins enable imagination-studio",
            "studio_tools": list(HERMES_PLUGIN_TOOLS),
        },
        "guardrails": {
            "auto_open_on_boot": False,
            "model_calls": 0,
            "network_requests": 1 if probe else 0,
            "weights_auto_downloaded": False,
            "provider_model_mutated": False,
        },
    }


def plan_collaboration(concept: str, *, fmt: str = "youtube") -> dict[str, Any]:
    """Generate a deterministic 5-Phase Filmmaker x Imagination Studio handoff plan (0 LLM calls)."""
    cleaned = (concept or "").strip()
    if not cleaned:
        raise ValueError("Concept must not be empty.")
    aspect_map = {
        "short": ("9:16", "15-60s", "-14 LUFS"),
        "youtube": ("16:9", "10-40 min (chaptered)", "-14 LUFS"),
        "cinema": ("2.39:1", "Narrative short/feature", "-24 LKFS"),
    }
    aspect, runtime_target, loudness = aspect_map[fmt]
    ram_gib = _detect_ram_gib()
    low_ram_mode = ram_gib is not None and ram_gib < 32.0

    return {
        "concept": cleaned,
        "format": fmt,
        "aspect_ratio": aspect,
        "runtime_target": runtime_target,
        "loudness_target": loudness,
        "lead_bot": "kiki-chii",
        "coordinator_bot": "shizuka",
        "partner_skills": ["filmmaking-videography-photography-s2", "imagination-studio"],
        "hardware_mode": (
            "slate_planning_or_remote_comfy_bridge" if low_ram_mode else "local_studio_queue_eligible"
        ),
        "phases": [
            {
                "phase": "1_concepting_first_and_script",
                "owner": "filmmaking-videography-photography-s2",
                "actions": [
                    "Kunci Core Emotion (51%), Story (23%), hook 3 detik, dan 2-3 arah konsep untuk review manusia.",
                    "Tulis naskah Fountain / Two-Column AV Script (dialog, shot size, gerak kamera, audio).",
                ],
                "human_gate": True,
            },
            {
                "phase": "2_slate_preproduction_and_coverage",
                "owner": "imagination-studio (Slate workflow)",
                "actions": [
                    "Pecah Master Shot List menjadi Slate setups, coverage plan, kontinuitas karakter/lokasi, dan seed terkunci.",
                    "Tahap Slate planning & organisasi proyek berjalan ringan tanpa unduhan bobot GPU besar.",
                ],
                "human_gate": True,
            },
            {
                "phase": "3_headroom_check_and_studio_queue",
                "owner": "imagination-studio (Hermes plugin / stdio MCP)",
                "actions": [
                    "Wajib cek memori dulu via `msshi studio status --probe` / `studio_status` / `memory_status` (127.0.0.1:7870).",
                    "Antrekan aset HANYA lewat Studio queue (`studio_picture`, `studio_clip`, `studio_voice`, `studio_song`, `studio_sound`) — jangan jalankan skrip render terpisah.",
                    (
                        "RAM perangkat < 32 GiB: jalankan hanya resep yang lulus Feature checks, pakai bridge ComfyUI PC/Comfy Cloud, atau fallback ke ArtCraft/Motion-as-Code/Higgsfield."
                        if low_ram_mode
                        else "Jalankan satu pekerjaan berat dalam satu waktu via antrean Studio sambil menjaga memory floor."
                    ),
                ],
                "human_gate": True,
            },
            {
                "phase": "4_postproduction_editing_color_sound",
                "owner": "filmmaking-videography-photography-s2 + ArtCraft / Blender",
                "actions": [
                    "Ambil hasil dari `HERMES_HOME/plugin-data/imagination-studio/outputs` atau `$STUDIO_URL/files/<path>`.",
                    f"Rakit cut dengan Walter Murch's Rule of Six (`filmcraft`), grading ACES/Rec.709 (`lightcraft`), dan mix loudness {loudness} (`soundcraft`).",
                ],
                "human_gate": True,
            },
            {
                "phase": "5_review_and_delivery",
                "owner": "kiki-chii -> shizuka -> user",
                "actions": [
                    "Tampilkan preview timecode & daftar aset untuk persetujuan pengguna sebelum ekspor final atau publikasi.",
                ],
                "human_gate": True,
            },
        ],
        "guardrails": {
            "auto_open_on_boot": False,
            "model_calls": 0,
            "bypass_studio_queue_forbidden": True,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="msshi studio", description=__doc__)
    parser.add_argument("--hermes-home", type=Path, help="Hermes data root (auto-detected if omitted).")
    sub = parser.add_subparsers(dest="action", required=True)

    p_status = sub.add_parser("status", help="Inspect Imagination Studio wrapper & Kiki-Chii Filmmaker readiness.")
    p_status.add_argument("--url", default=DEFAULT_STUDIO_URL, help="Loopback Studio URL (default http://127.0.0.1:7870).")
    p_status.add_argument("--probe", action="store_true", help="Explicitly probe local loopback /api/memory and /api/jobs.")
    p_status.add_argument("--json", action="store_true", help="Output JSON.")

    p_plan = sub.add_parser("plan", help="Generate a 5-phase Filmmaker x Imagination Studio collaboration blueprint.")
    p_plan.add_argument("--concept", required=True, help="Short description of the film/video concept.")
    p_plan.add_argument("--format", choices=("short", "youtube", "cinema"), default="youtube")
    p_plan.add_argument("--json", action="store_true", help="Output JSON.")

    args = parser.parse_args(argv)
    try:
        if args.action == "status":
            data = studio_status(args.hermes_home, url=args.url, probe=args.probe)
            if args.json:
                print(json.dumps(data, ensure_ascii=False, indent=2))
            else:
                k = data["kiki_chii"]
                print("=== MSSHI Imagination Studio Bridge (Optional — Kiki-Chii) ===")
                print(f"Hermes Home          : {data['hermes_home']}")
                print(f"Optional Wrapper     : {'ENABLED' if k['optional_wrapper_enabled'] else 'OFF (opt-in)'}")
                print(f"Filmmaker Partner    : {'READY' if k['filmmaker_partner_present'] else 'MISSING'}")
                print(f"Collaboration Ready  : {k['collaboration_ready']}")
                print(f"Hermes Plugin Active : {k['hermes_plugin_enabled']}")
                print(f"Local Studio Probe   : {data['local_studio_probe'].get('reachable') if args.probe else 'not probed (use --probe)'}")
            return 0
        if args.action == "plan":
            plan = plan_collaboration(args.concept, fmt=args.format)
            print(json.dumps(plan, ensure_ascii=False, indent=2))
            return 0
    except (OSError, ValueError) as exc:
        parser.exit(1, f"msshi studio: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
