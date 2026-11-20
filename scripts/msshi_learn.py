#!/usr/bin/env python3
"""MSSHI beginner-friendly learning router & plugin manager (`msshi learn`).

Unifies:
- `belajar-pemula` skill (natural chat, 1 concept at a time, zero jargon)
- `chalk` plugin (MIT, vendored in hermes_plugins/chalk/ — visual chalkboard)
- `learnloop` plugin (AGPL-3.0, NEVER vendored in MIT repo — opt-in direct upstream install)
- `codecoach` plugin (MIT, pinned external install — Linux/WSL2 bubblewrap sandbox; honest Windows fallback)
- `ossu` open-source CS university (`msshi ossu`)
- `msshi-auto-trim` (MSSHITrim lossless JSON compaction)

Zero LLM calls, zero auto-open on boot, zero provider/model/SOUL mutations.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any

sys.dont_write_bytecode = True

_SCRIPTS_DIR = str(Path(__file__).resolve().parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import msshi_context_sources as cs
import msshi_hermes_profiles as hp
import msshi_ossu as ossu_mod

ROOT = Path(__file__).resolve().parents[1]

LEARNLOOP_REPO = "https://github.com/huss-wrld/learnloop.git"
LEARNLOOP_PIN = "fdcf3d1acf95c7d4056dfe746347ca6b97e38c04"
LEARNLOOP_PROFILES = ("shizuka", "yukino")

CODECOACH_REPO = "https://github.com/heyitstony97-max/codecoach.git"
CODECOACH_PIN = "68cbfb6a78bc16f3fb60c4a8dac21e4882a8c20d"
CODECOACH_PROFILES = ("shikaku", "shizuka")

_CODING_KW = (
    "coding", "ngoding", "pemrograman", "programming", "python", "javascript", "typescript",
    "rust", "golang", "java", "c++", "bahasa c", "bash", "html", "css", "sql", "codecoach",
    "program pertama", "hello world", "variabel", "loop", "fungsi",
)
_VISUAL_KW = (
    "gambar", "diagram", "visual", "grafik", "papan tulis", "chalk", "whiteboard",
    "ilustrasi", "cara kerja", "alur", "skema", "siklus", "fisika", "biologi", "kimia",
    "kalkulus", "geometri", "jaringan", "transformer", "attention",
)
_OSSU_KW = (
    "ossu", "computer science", "ilmu komputer", "kurikulum cs", "kuliah cs",
    "sistem operasi", "ostep", "nand2tetris", "struktur data", "algoritma", "kompiler",
)


def _codecoach_platform_check() -> dict[str, Any]:
    has_resource = importlib.util.find_spec("resource") is not None
    bwrap = shutil.which("bwrap")
    supported = os.name != "nt" and has_resource and bool(bwrap)
    reason = (
        "Sandbox bubblewrap + modul POSIX resource tersedia."
        if supported
        else (
            "CodeCoach memakai modul POSIX `resource` dan sandbox Linux `bubblewrap` (`bwrap`). "
            "Pada Windows native, jalankan belajar coding lewat Shikaku (tutor interaktif langsung di workspace) "
            "atau jalankan Hermes di WSL2/Linux untuk sandbox CodeCoach penuh."
        )
    )
    return {
        "os_name": os.name,
        "posix_resource_available": has_resource,
        "bubblewrap_path": bwrap,
        "native_supported": supported,
        "mode": "full_sandbox" if supported else "windows_limited_fallback_to_shikaku",
        "reason": reason,
    }


def _plugin_enabled(profile_dir: Path, plugin_id: str) -> bool:
    cfg_path = profile_dir / "config.yaml"
    if not cfg_path.is_file():
        return False
    try:
        cfg = hp.load_yaml_mapping(cfg_path)
    except Exception:
        return False
    plugins = cfg.get("plugins") or {}
    if not isinstance(plugins, dict):
        return False
    enabled = plugins.get("enabled") or []
    disabled = plugins.get("disabled") or []
    if plugin_id in disabled:
        return False
    if isinstance(enabled, dict):
        return enabled.get(plugin_id) is True
    return plugin_id in enabled


def learn_status(home: Path) -> dict[str, Any]:
    home = cs.checked(home)
    live = hp.live_named_profiles(home)
    all_profiles = {"default": home, **live}
    plugins_state: dict[str, dict[str, Any]] = {}
    for pid in ("chalk", "learnloop", "codecoach", "msshi-auto-trim"):
        installed_on = [n for n, p in sorted(all_profiles.items()) if (p / "plugins" / pid / "plugin.yaml").is_file()]
        enabled_on = [n for n, p in sorted(all_profiles.items()) if _plugin_enabled(p, pid) and n in installed_on]
        plugins_state[pid] = {
            "installed_profiles": installed_on,
            "enabled_profiles": enabled_on,
            "count": len(enabled_on),
        }
    skill_profiles = [n for n, p in sorted(all_profiles.items()) if (p / "skills" / "belajar-pemula" / "SKILL.md").is_file()]
    ossu_st = ossu_mod.status_report(home)
    cc_plat = _codecoach_platform_check()
    return {
        "hermes_home": str(home),
        "network_calls": 0,
        "model_calls": 0,
        "belajar_pemula_skill_profiles": skill_profiles,
        "plugins": plugins_state,
        "codecoach_platform": cc_plat,
        "ossu_university": {
            "cached": bool(ossu_st.get("source_cached")),
            "files": ossu_st.get("source_files", 0),
            "courses": ossu_st.get("total_courses"),
            "portal_url": ossu_st.get("portal_url"),
        },
        "token_compaction_active": plugins_state["msshi-auto-trim"]["count"] > 0,
    }


def route_beginner_topic(topic: str, home: Path | None = None) -> dict[str, Any]:
    """Deterministically pick the simplest beginner path (0 LLM calls)."""
    low = f" {topic.casefold()} "
    st = learn_status(home) if home and home.is_dir() else None
    chalk_on = bool(st and st["plugins"]["chalk"]["count"] > 0)
    ll_on = bool(st and st["plugins"]["learnloop"]["count"] > 0)
    cc_on = bool(st and st["plugins"]["codecoach"]["count"] > 0 and st["codecoach_platform"]["native_supported"])

    if any(k in low for k in _OSSU_KW):
        mode = "ossu_cs_university"
        lead = "shizuka"
        tools = ["msshi ossu open pemula", "msshi ossu open start", "chalk (visualisasi)" if chalk_on else "analogis sederhana"]
        first_step = "Buka kurikulum dasar OSSU lewat `msshi ossu open pemula` (belum pernah coding) atau `msshi ossu open start` (MIT 6.100L Python)."
        chat_prompt = f"Halo Shizuka, aku pemula dan mau belajar {topic.strip()} mengikuti kurikulum OSSU dari dasar, satu langkah kecil per balasan ya."
    elif any(k in low for k in _CODING_KW):
        mode = "coding_beginner"
        lead = "shikaku"
        if cc_on:
            tools = ["codecoach (sandbox step-by-step)", "chalk (diagram alur)" if chalk_on else "contoh kode mini"]
            first_step = "Mulai proyek mini terverifikasi di CodeCoach atau minta Shikaku ajarkan 1 konsep kode kecil lalu langsung dicoba."
        else:
            tools = ["Shikaku interactive coding tutor (mode Windows native)", "chalk (diagram alur)" if chalk_on else "contoh kode mini"]
            first_step = "Mulai 1 program super kecil (5-10 baris) bersama Shikaku: baca kode -> tebak output -> jalankan -> ubah 1 baris."
        chat_prompt = f"Halo Shikaku, aku pemula total dan mau belajar {topic.strip()} dari nol. Mulai dari contoh paling kecil dulu, satu langkah per balasan ya."
    elif any(k in low for k in _VISUAL_KW):
        mode = "visual_concept"
        lead = "shizuka"
        tools = [
            "chalk (`chalk_teach` papan tulis visual)" if chalk_on else "diagram teks langkah demi langkah",
            "learnloop (cek pemahaman bertahap)" if ll_on else "Socratic check bawaan Shizuka",
        ]
        first_step = "Minta Shizuka menggambar konsep inti di papan tulis Chalk dalam 5-7 langkah singkat, lalu jawab 1 pertanyaan cek pemahaman."
        chat_prompt = f"Halo Shizuka, jelaskan {topic.strip()} untuk pemula total pakai papan tulis Chalk biar kebayang, pelan-pelan satu konsep dulu ya."
    else:
        mode = "guided_concept"
        lead = "shizuka"
        tools = [
            "learnloop (probe -> plan -> teach -> practice)" if ll_on else "Socratic tutor bawaan Shizuka (fallback aktif)",
            "chalk (`chalk_teach` saat butuh gambar/skema)" if chalk_on else "analogi sehari-hari",
        ]
        first_step = "Shizuka cek dulu pemahaman awal & energimu dalam 2 pertanyaan singkat, lalu ajarkan 1 konsep kecil dengan contoh nyata."
        chat_prompt = f"Halo Shizuka, aku pemula total dan mau belajar {topic.strip()} dari nol. Cek dulu levelku, lalu ajarkan pelan-pelan satu konsep per balasan ya."

    return {
        "topic": topic.strip(),
        "mode": mode,
        "lead_bot": lead,
        "recommended_tools": tools,
        "first_step": first_step,
        "try_in_hermes_chat": chat_prompt,
        "slash_command_required": False,
        "token_budget_rule": "1 konsep inti per balasan; MSSHITrim (msshi-auto-trim) memadatkan output tool JSON >= 2048 karakter otomatis.",
    }


def _clone_pinned_to_dir(repo_url: str, pin: str, dest_dir: Path) -> int:
    """Clone exact pinned commit cleanly (no .git kept in plugin folder) and return copied file count."""
    with tempfile.TemporaryDirectory(prefix="msshi-plug-") as tmp:
        clone_dir = Path(tmp) / "repo"
        subprocess.run(
            [
                "git", "-c", "http.postBuffer=16m", "-c", "pack.windowMemory=32m", "-c", "pack.threads=1",
                "clone", "--depth=1", repo_url, str(clone_dir),
            ],
            check=True, capture_output=True, timeout=180,
        )
        head = subprocess.run(["git", "-C", str(clone_dir), "rev-parse", "HEAD"],
                              check=True, capture_output=True, text=True).stdout.strip()
        if head.lower() != pin.lower():
            subprocess.run(
                [
                    "git", "-C", str(clone_dir), "-c", "http.postBuffer=16m", "-c", "pack.windowMemory=32m",
                    "-c", "pack.threads=1", "fetch", "--depth=1", "origin", pin,
                ],
                check=True, capture_output=True, timeout=180,
            )
            subprocess.run(["git", "-C", str(clone_dir), "checkout", "--detach", pin],
                           check=True, capture_output=True, timeout=60)
            actual = subprocess.run(["git", "-C", str(clone_dir), "rev-parse", "HEAD"],
                                    check=True, capture_output=True, text=True).stdout.strip()
            if actual.lower() != pin.lower():
                raise ValueError(f"Pinned commit verification failed: expected {pin}, got {actual}")

        if dest_dir.exists():
            shutil.rmtree(dest_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)
        count = 0
        for item in sorted(clone_dir.rglob("*")):
            if item.is_symlink() or not item.is_file():
                continue
            rel = item.relative_to(clone_dir)
            if ".git" in rel.parts or "__pycache__" in rel.parts or item.suffix in {".pyc", ".pyo"}:
                continue
            out = dest_dir / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, out)
            count += 1
        return count


def install_chalk(home: Path, repo_source: Path = ROOT) -> dict[str, Any]:
    """Install vendored MIT Chalk plugin across default and all live named profiles."""
    return hp.install_wise_plugins(home, repo_source, plugin_ids=("chalk",))


def install_learnloop(home: Path, profiles: tuple[str, ...] = LEARNLOOP_PROFILES) -> dict[str, Any]:
    """Opt-in installer for AGPL-3.0 LearnLoop fetched unmodified straight from upstream GitHub (never vendored in MIT repo)."""
    home = cs.checked(home)
    live = hp.live_named_profiles(home)
    targets = [(name, live[name]) for name in profiles if name in live]
    if not targets:
        raise ValueError("Profil target LearnLoop tidak ditemukan: " + ", ".join(profiles))

    cache_dir = cs.checked(home / "msshi-private" / "external-plugins" / "learnloop" / LEARNLOOP_PIN)
    if not (cache_dir / "plugin.yaml").is_file() or not (cache_dir / "LICENSE").is_file():
        _clone_pinned_to_dir(LEARNLOOP_REPO, LEARNLOOP_PIN, cache_dir)

    tx = hp.ProfileTransaction(home)
    rows: dict[str, Any] = {}
    try:
        for name, profile_dir in targets:
            dst_root = hp._confined(home, profile_dir / "plugins" / "learnloop")
            for src_file in sorted(cache_dir.rglob("*")):
                if src_file.is_symlink() or not src_file.is_file():
                    continue
                rel = src_file.relative_to(cache_dir)
                if rel.parts and rel.parts[0] == "tests":
                    continue
                tx.write(hp._confined(home, dst_root / rel), src_file.read_bytes())
            rows[name] = hp._activate_plugins_in_config(profile_dir / "config.yaml", ("learnloop",), tx)
        receipt = tx.commit()
    except Exception:
        tx.rollback()
        raise
    return {
        "installed": True,
        "plugin": "learnloop",
        "license": "AGPL-3.0-only",
        "source": LEARNLOOP_REPO,
        "commit": LEARNLOOP_PIN,
        "vendored_in_msshi_repo": False,
        "profiles": rows,
        "receipt": receipt,
    }


def install_codecoach(
    home: Path,
    profiles: tuple[str, ...] = CODECOACH_PROFILES,
    *,
    force_stage_on_windows: bool = False,
) -> dict[str, Any]:
    """Install pinned MIT CodeCoach directly from upstream (Linux/WSL2 enabled; honest Windows guard)."""
    home = cs.checked(home)
    plat = _codecoach_platform_check()
    if not plat["native_supported"]:
        staged_path = None
        if force_stage_on_windows:
            cache_dir = cs.checked(home / "msshi-private" / "external-plugins" / "codecoach" / CODECOACH_PIN)
            if not (cache_dir / "plugin.yaml").is_file():
                _clone_pinned_to_dir(CODECOACH_REPO, CODECOACH_PIN, cache_dir)
            staged_path = str(cache_dir)
        return {
            "installed": False,
            "enabled": False,
            "plugin": "codecoach",
            "license": "MIT",
            "source": CODECOACH_REPO,
            "commit": CODECOACH_PIN,
            "platform": plat,
            "staged_cache": staged_path,
            "fallback": "Gunakan Shikaku (tutor coding interaktif Windows native) + Chalk + LearnLoop + OSSU.",
        }

    live = hp.live_named_profiles(home)
    targets = [(name, live[name]) for name in profiles if name in live]
    if not targets:
        raise ValueError("Profil target CodeCoach tidak ditemukan: " + ", ".join(profiles))
    cache_dir = cs.checked(home / "msshi-private" / "external-plugins" / "codecoach" / CODECOACH_PIN)
    if not (cache_dir / "plugin.yaml").is_file():
        _clone_pinned_to_dir(CODECOACH_REPO, CODECOACH_PIN, cache_dir)

    tx = hp.ProfileTransaction(home)
    rows: dict[str, Any] = {}
    try:
        for name, profile_dir in targets:
            dst_root = hp._confined(home, profile_dir / "plugins" / "codecoach")
            for src_file in sorted(cache_dir.rglob("*")):
                if src_file.is_symlink() or not src_file.is_file():
                    continue
                rel = src_file.relative_to(cache_dir)
                if rel.parts and rel.parts[0] in {"tests", "demo", "devtools"}:
                    continue
                tx.write(hp._confined(home, dst_root / rel), src_file.read_bytes())
            rows[name] = hp._activate_plugins_in_config(profile_dir / "config.yaml", ("codecoach",), tx)
        receipt = tx.commit()
    except Exception:
        tx.rollback()
        raise
    return {
        "installed": True,
        "enabled": True,
        "plugin": "codecoach",
        "license": "MIT",
        "source": CODECOACH_REPO,
        "commit": CODECOACH_PIN,
        "platform": plat,
        "profiles": rows,
        "receipt": receipt,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="msshi learn", description=__doc__)
    sub = parser.add_subparsers(dest="action")

    p_st = sub.add_parser("status", help="Lihat status alat belajar pemula (Chalk, LearnLoop, CodeCoach, OSSU, MSSHITrim).")
    p_st.add_argument("--home", type=Path, help="Folder Hermes home.")
    p_st.add_argument("--json", action="store_true", help="Keluaran JSON.")

    p_start = sub.add_parser("start", help="Rekomendasikan jalur belajar paling sederhana untuk topik tertentu (0 LLM).")
    p_start.add_argument("topic", nargs="+", help="Topik yang ingin dipelajari.")
    p_start.add_argument("--home", type=Path, help="Folder Hermes home.")
    p_start.add_argument("--json", action="store_true", help="Keluaran JSON.")

    p_inst = sub.add_parser("install", help="Pasang plugin belajar (Chalk MIT, LearnLoop AGPL opt-in, CodeCoach MIT).")
    p_inst.add_argument("--chalk", action="store_true", help="Pasang Chalk (MIT) ke semua profil.")
    p_inst.add_argument("--learnloop", action="store_true", help="Opt-in: unduh & pasang LearnLoop (AGPL-3.0) langsung dari upstream ke Shizuka & Yukino.")
    p_inst.add_argument("--codecoach", action="store_true", help="Pasang CodeCoach (MIT) ke Shikaku & Shizuka (Linux/WSL2; laporan jujur di Windows).")
    p_inst.add_argument("--force-stage-codecoach", action="store_true", help="Simpan cache CodeCoach di Windows tanpa mengaktifkannya di plugins.enabled.")
    p_inst.add_argument("--home", type=Path, help="Folder Hermes home.")
    p_inst.add_argument("--json", action="store_true", help="Keluaran JSON.")

    args = parser.parse_args(argv)
    action = args.action or "status"
    try:
        home = cs.checked(hp.resolve_hermes_home(getattr(args, "home", None)))
        if action == "status":
            data = learn_status(home)
            if args.json:
                print(json.dumps(data, ensure_ascii=False, indent=2))
            else:
                p = data["plugins"]
                cc = data["codecoach_platform"]
                ossu = data["ossu_university"]
                print(f"=== MSSHI Mode Belajar Pemula ({data['hermes_home']}) ===")
                print(f"Skill belajar-pemula : {len(data['belajar_pemula_skill_profiles'])} profil")
                print(f"Chalk (papan tulis)  : aktif di {p['chalk']['count']} profil {p['chalk']['enabled_profiles']}")
                print(f"LearnLoop (AGPL opt) : aktif di {p['learnloop']['count']} profil {p['learnloop']['enabled_profiles']}")
                print(f"CodeCoach (coding)   : aktif di {p['codecoach']['count']} profil ({cc['mode']})")
                print(f"OSSU CS University   : cached={ossu['cached']} ({ossu['files']} file, {ossu['courses']} matkul)")
                print(f"MSSHITrim Hemat Token: aktif di {p['msshi-auto-trim']['count']} profil")
                print("Coba langsung: msshi learn start \"python dari nol\"")
            return 0

        if action == "start":
            topic_str = " ".join(args.topic)
            data = route_beginner_topic(topic_str, home)
            if args.json:
                print(json.dumps(data, ensure_ascii=False, indent=2))
            else:
                print(f"=== Rencana Belajar Pemula: {data['topic']} ===")
                print(f"Bot Pembimbing : {data['lead_bot']} (mode: {data['mode']})")
                print(f"Alat Dipakai   : {', '.join(data['recommended_tools'])}")
                print(f"Langkah Pertama: {data['first_step']}")
                print(f"Langsung Chat  : \"{data['try_in_hermes_chat']}\"")
            return 0

        if action == "install":
            results: dict[str, Any] = {}
            if not (args.chalk or args.learnloop or args.codecoach):
                args.chalk = True
            if args.chalk:
                results["chalk"] = install_chalk(home)
            if args.learnloop:
                results["learnloop"] = install_learnloop(home)
            if args.codecoach:
                results["codecoach"] = install_codecoach(home, force_stage_on_windows=bool(args.force_stage_codecoach))
            print(json.dumps(results, ensure_ascii=False, indent=2))
            return 0

        parser.print_help()
        return 0
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"msshi learn: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
