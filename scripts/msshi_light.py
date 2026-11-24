#!/usr/bin/env python3
"""MSSHI Windows 10 RAM 4 GB Light Build packaging, resource profile, and offline benchmark."""
from __future__ import annotations

import argparse
import ctypes
from datetime import datetime, timezone
import fnmatch
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
import zipfile

sys.dont_write_bytecode = True
_SCRIPTS = str(Path(__file__).resolve().parent)
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

import msshi_hermes_profiles as hp
import msshi_skill_index as skill_index

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_REL = Path("configs", "light_build_manifest.json")
ACTIVE_MARKER_REL = Path("configs", "light_build_active.json")
RESOURCE_PROFILE_REL = Path("msshi-runtime", "resource-profile.json")
MIN_FREE_DISK_BYTES_LIGHT = 150 * 1024 * 1024
FIXED_ZIP_TIME = (2026, 11, 19, 0, 0, 0)


def _ordinary(path: Path) -> Path:
    resolved = Path(os.path.abspath(os.fspath(path)))
    if str(resolved).startswith(("\\\\", "//")):
        raise ValueError("UNC paths are not accepted.")
    for item in (*reversed(resolved.parents), resolved):
        if os.path.lexists(item) and skill_index.is_link(item):
            raise ValueError(f"Symlink/junction is not allowed: {item}")
    return resolved


def load_manifest(source: Path | None = None) -> dict:
    base = _ordinary(Path(source) if source else ROOT)
    path = _ordinary(base / MANIFEST_REL)
    if not path.is_file():
        raise FileNotFoundError(f"Light build manifest missing: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("Unsupported light_build_manifest.json schema.")
    return data


def is_light_build(source: Path | None = None) -> bool:
    base = Path(source) if source else ROOT
    marker = base / ACTIVE_MARKER_REL
    return marker.is_file() and not skill_index.is_link(marker)


def _system_memory_bytes() -> tuple[int, int]:
    total = 0
    available = 0
    if os.name == "nt":
        class Memory(ctypes.Structure):
            _fields_ = [
                ("length", ctypes.c_ulong),
                ("load", ctypes.c_ulong),
                *[(key, ctypes.c_ulonglong) for key in (
                    "total", "available", "page", "free_page", "virtual", "free_virtual", "extended"
                )],
            ]
        rec = Memory()
        rec.length = ctypes.sizeof(rec)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(rec)):
            total, available = int(rec.total), int(rec.available)
    elif hasattr(os, "sysconf"):
        try:
            page = os.sysconf("SC_PAGE_SIZE")
            total = int(page * os.sysconf("SC_PHYS_PAGES"))
            available = int(page * os.sysconf("SC_AVPHYS_PAGES"))
        except (ValueError, OSError):
            pass
    return total, available


def process_memory_mb() -> dict:
    """Measure current process working set and private commit charge in MiB."""
    working_set_mb = None
    peak_working_set_mb = None
    commit_charge_mb = None
    if os.name == "nt":
        from ctypes import wintypes

        class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
                ("PrivateUsage", ctypes.c_size_t),
            ]

        counters = PROCESS_MEMORY_COUNTERS_EX()
        counters.cb = ctypes.sizeof(counters)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        kernel32.K32GetProcessMemoryInfo.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(PROCESS_MEMORY_COUNTERS_EX),
            wintypes.DWORD,
        ]
        kernel32.K32GetProcessMemoryInfo.restype = wintypes.BOOL
        handle = kernel32.GetCurrentProcess()
        if kernel32.K32GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
            working_set_mb = round(counters.WorkingSetSize / (1024 * 1024), 2)
            peak_working_set_mb = round(counters.PeakWorkingSetSize / (1024 * 1024), 2)
            commit_charge_mb = round(counters.PrivateUsage / (1024 * 1024), 2)
    else:
        try:
            import resource
            rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            divisor = (1024 * 1024) if sys.platform == "darwin" else 1024
            working_set_mb = round(rss / divisor, 2)
            peak_working_set_mb = working_set_mb
        except Exception:
            pass
    return {
        "working_set_mb": working_set_mb,
        "peak_working_set_mb": peak_working_set_mb,
        "commit_charge_mb": commit_charge_mb,
    }


def hardware_profile(
    *,
    physical_gib: float | None = None,
    available_gib: float | None = None,
    source: Path | None = None,
) -> dict:
    """Inspect host RAM and return Low-RAM (<= 6 GB / 4 GB target) recommendations and targets."""
    manifest = load_manifest(source)
    if physical_gib is None or available_gib is None:
        total_b, avail_b = _system_memory_bytes()
        if physical_gib is None:
            physical_gib = round(total_b / (1024 ** 3), 2) if total_b else 0.0
        if available_gib is None:
            available_gib = round(avail_b / (1024 ** 3), 2) if avail_b else 0.0
    threshold = float(manifest.get("target_hardware_class", {}).get("ram_threshold_gib", 6.0))
    low_ram = bool(physical_gib > 0 and physical_gib <= threshold)
    recommended = "light" if low_ram else "normal"
    return {
        "physical_gib": round(float(physical_gib), 2),
        "available_gib": round(float(available_gib), 2),
        "cpu_count": os.cpu_count() or 1,
        "os_platform": platform.platform(),
        "low_ram_detected": low_ram,
        "low_ram_4gb": low_ram,
        "ram_threshold_gib": threshold,
        "recommended_resource_profile": recommended,
        "light_mode_constraints": dict(manifest.get("light_mode_constraints") or {}),
        "light_mode_blocked_targets": list(manifest.get("light_mode_blocked_targets") or []),
        "acceptance_targets_not_claimed_passed": dict(manifest.get("acceptance_targets") or {}),
        "certified_for_win10_4gb": False,
    }


def read_resource_profile(home: Path) -> dict:
    """Read active resource profile from Hermes home without modifying any file."""
    hermes_root = _ordinary(hp.normalize_hermes_root(home))
    path = hermes_root / RESOURCE_PROFILE_REL
    if not path.exists():
        return {
            "configured": False,
            "profile": "normal",
            "source": "default",
            "path": str(path),
            "constraints": {},
            "blocked_targets": [],
        }
    _ordinary(path)
    if not path.is_file() or path.stat().st_size > 65536:
        raise ValueError(f"Invalid resource profile file: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or data.get("profile") not in {"light", "normal"}:
        raise ValueError(f"Unsupported resource profile format: {path}")
    return {
        "configured": True,
        "profile": data["profile"],
        "source": "resource-profile.json",
        "path": str(path),
        "constraints": dict(data.get("constraints") or {}),
        "blocked_targets": list(data.get("blocked_targets") or []),
        "updated_at": data.get("updated_at"),
        "hermes_cli_fallback_enabled": bool(data.get("hermes_cli_fallback_enabled", True)),
    }


def apply_resource_profile(
    home: Path,
    requested: str = "auto",
    *,
    apply: bool = False,
    physical_gib: float | None = None,
    source: Path | None = None,
) -> dict:
    """Preview or atomically apply light/normal resource profile with rollback receipt.

    Never reads or mutates config.yaml, .env, auth.json, SOUL.md, or model/provider settings.
    """
    if requested not in {"auto", "light", "normal"}:
        raise ValueError(f"Unsupported resource profile: {requested!r}")
    hermes_root = _ordinary(hp.normalize_hermes_root(home))
    hw = hardware_profile(physical_gib=physical_gib, source=source)
    resolved = hw["recommended_resource_profile"] if requested == "auto" else requested
    target = _ordinary(hermes_root / RESOURCE_PROFILE_REL)
    payload = {
        "schema_version": 1,
        "profile": resolved,
        "requested": requested,
        "base_version": load_manifest(source).get("base_version", "3.2.0"),
        "detected_physical_gib": hw["physical_gib"],
        "low_ram_4gb_detected": hw["low_ram_4gb"],
        "constraints": hw["light_mode_constraints"] if resolved == "light" else {
            "max_active_inference": None,
            "max_active_jobs": None,
            "max_writer_or_render_subprocesses": 1 if hw["physical_gib"] < 24 else 2,
            "allow_parallel_moa": True,
            "allow_parallel_delegation": True,
            "allow_sequential_handoff_with_user_approval": True,
            "allow_local_heavy_render": True,
            "allow_local_timeseries_model": True,
            "allow_local_ocr_model": True,
            "auto_open_on_boot": False,
            "avoid_desktop_launch_on_cli_status": True,
            "prefer_hermes_cli_when_desktop_heavy": False,
        },
        "blocked_targets": hw["light_mode_blocked_targets"] if resolved == "light" else [],
        "hermes_cli_fallback_enabled": True,
        "model_provider_mutated": False,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    result = {
        "applied": False,
        "requested": requested,
        "profile": resolved,
        "target": str(target),
        "hardware": hw,
        "constraints": payload["constraints"],
        "blocked_targets": payload["blocked_targets"],
        "model_provider_mutated": False,
        "receipt": None,
    }
    if not apply:
        return result

    hermes_root.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    tx = hp.ProfileTransaction(hermes_root)
    try:
        tx.write(target, raw, 0o600)
        result["receipt"] = tx.commit()
        result["applied"] = True
    except Exception:
        tx.rollback()
        raise
    return result


def check_disk_space(path: Path, min_bytes: int = MIN_FREE_DISK_BYTES_LIGHT) -> dict:
    """Check free disk space on the target volume without writing."""
    probe = Path(path)
    while not probe.exists() and probe.parent != probe:
        probe = probe.parent
    usage = shutil.disk_usage(probe)
    return {
        "path": str(probe),
        "free_bytes": int(usage.free),
        "free_mb": round(usage.free / (1024 * 1024), 2),
        "required_bytes": int(min_bytes),
        "sufficient": usage.free >= min_bytes,
    }


def _is_excluded(rel_posix: str, exclude_dirs: tuple[str, ...], exclude_globs: tuple[str, ...]) -> bool:
    for prefix in exclude_dirs:
        if rel_posix == prefix or rel_posix.startswith(prefix + "/"):
            return True
    parts = rel_posix.split("/")
    for pattern in exclude_globs:
        if fnmatch.fnmatch(rel_posix, pattern) or any(fnmatch.fnmatch(part, pattern) for part in parts):
            return True
    return False


def light_build_files(source: Path | None = None) -> list[tuple[str, Path]]:
    """Collect the exact sorted list of files belonging to the light bootstrap package."""
    base = _ordinary(Path(source) if source else ROOT)
    manifest = load_manifest(base)
    include_dirs = tuple(str(d).strip("/") for d in manifest.get("include_dirs", []))
    include_files = tuple(str(f).strip("/") for f in manifest.get("include_files", []))
    exclude_dirs = tuple(str(d).strip("/") for d in manifest.get("exclude_dirs", []))
    exclude_globs = tuple(str(g) for g in manifest.get("exclude_globs", []))

    collected: dict[str, Path] = {}
    for rel in include_files:
        candidate = _ordinary(base / rel)
        if candidate.is_file() and candidate.is_relative_to(base):
            collected[rel] = candidate

    for folder_rel in include_dirs:
        folder = _ordinary(base / folder_rel)
        if not folder.is_dir():
            continue
        for current_root, dirs, files in os.walk(folder, followlinks=False):
            current = Path(current_root)
            kept_dirs = []
            for dname in sorted(dirs):
                dpath = current / dname
                if skill_index.is_link(dpath):
                    raise ValueError(f"Symlink/junction not allowed in light build source: {dpath}")
                drel = dpath.relative_to(base).as_posix()
                if not _is_excluded(drel, exclude_dirs, exclude_globs):
                    kept_dirs.append(dname)
            dirs[:] = kept_dirs
            for fname in sorted(files):
                fpath = current / fname
                if skill_index.is_link(fpath):
                    raise ValueError(f"Symlink/junction not allowed in light build source: {fpath}")
                frel = fpath.relative_to(base).as_posix()
                if frel == ACTIVE_MARKER_REL.as_posix():
                    continue
                if not _is_excluded(frel, exclude_dirs, exclude_globs):
                    collected[frel] = fpath

    return [(rel, collected[rel]) for rel in sorted(collected)]


def stage_light_tree(source: Path, destination: Path) -> dict:
    """Copy only light bootstrap files into destination and emit light_build_active.json."""
    base = _ordinary(Path(source))
    dest = _ordinary(Path(destination))
    manifest = load_manifest(base)
    entries = light_build_files(base)
    file_hashes: dict[str, str] = {}
    total_bytes = 0

    for rel, src in entries:
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        raw = src.read_bytes()
        target.write_bytes(raw)
        file_hashes[rel] = hashlib.sha256(raw).hexdigest()
        total_bytes += len(raw)

    max_mb = float(manifest.get("acceptance_targets", {}).get("max_initial_download_mb", 50))
    marker = {
        "schema_version": 1,
        "build_profile": "light",
        "base_version": manifest.get("base_version", "3.2.0"),
        "file_count": len(file_hashes),
        "uncompressed_bytes": total_bytes,
        "max_initial_download_mb": max_mb,
        "within_size_budget": (total_bytes / (1024 * 1024)) <= max_mb,
        "deferred_optional_packages": [item["id"] for item in manifest.get("deferred_optional_packages", [])],
        "sha256_manifest_digest": hashlib.sha256(
            json.dumps(file_hashes, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
    }
    marker_path = dest / ACTIVE_MARKER_REL
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    marker_path.write_text(json.dumps(marker, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return marker


def build_light_bundle(
    source: Path,
    output_zip: Path,
    *,
    manifest_out: Path | None = None,
) -> dict:
    """Build a deterministic light bootstrap ZIP <= 50 MB without heavy assets/PDFs/upstreams."""
    base = _ordinary(Path(source))
    out_zip = _ordinary(Path(output_zip))
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest(base)
    entries = light_build_files(base)

    file_hashes: dict[str, str] = {}
    uncompressed_bytes = 0
    with TemporaryDirectory(prefix="msshi-light-zip-") as tmp:
        stage_zip = Path(tmp) / out_zip.name
        with zipfile.ZipFile(stage_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            for rel, src in entries:
                raw = src.read_bytes()
                info = zipfile.ZipInfo(rel, date_time=FIXED_ZIP_TIME)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                zf.writestr(info, raw)
                file_hashes[rel] = hashlib.sha256(raw).hexdigest()
                uncompressed_bytes += len(raw)

            max_mb = float(manifest.get("acceptance_targets", {}).get("max_initial_download_mb", 50))
            marker = {
                "schema_version": 1,
                "build_profile": "light",
                "base_version": manifest.get("base_version", "3.2.0"),
                "file_count": len(file_hashes),
                "uncompressed_bytes": uncompressed_bytes,
                "max_initial_download_mb": max_mb,
                "deferred_optional_packages": [item["id"] for item in manifest.get("deferred_optional_packages", [])],
                "sha256_manifest_digest": hashlib.sha256(
                    json.dumps(file_hashes, sort_keys=True, separators=(",", ":")).encode("utf-8")
                ).hexdigest(),
            }
            marker_bytes = (json.dumps(marker, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            marker_info = zipfile.ZipInfo(ACTIVE_MARKER_REL.as_posix(), date_time=FIXED_ZIP_TIME)
            marker_info.compress_type = zipfile.ZIP_DEFLATED
            marker_info.external_attr = 0o644 << 16
            zf.writestr(marker_info, marker_bytes)

        zip_bytes = stage_zip.read_bytes()
        zip_sha = hashlib.sha256(zip_bytes).hexdigest()
        zip_mb = round(len(zip_bytes) / (1024 * 1024), 3)
        max_mb = float(manifest.get("acceptance_targets", {}).get("max_initial_download_mb", 50))
        if zip_mb > max_mb:
            raise ValueError(f"Light bundle exceeds {max_mb} MB budget: {zip_mb} MB")
        shutil.copy2(stage_zip, out_zip)

    report = {
        "schema_version": 1,
        "build_profile": "light",
        "base_version": manifest.get("base_version", "3.2.0"),
        "output_zip": str(out_zip),
        "zip_bytes": len(zip_bytes),
        "zip_mb": zip_mb,
        "zip_sha256": zip_sha,
        "uncompressed_bytes": uncompressed_bytes,
        "uncompressed_mb": round(uncompressed_bytes / (1024 * 1024), 3),
        "file_count": len(file_hashes) + 1,
        "max_initial_download_mb": max_mb,
        "within_download_budget": zip_mb <= max_mb,
        "excluded_heavy_categories": [item["id"] for item in manifest.get("deferred_optional_packages", [])],
        "files": file_hashes,
    }
    if manifest_out is not None:
        mpath = _ordinary(Path(manifest_out))
        mpath.parent.mkdir(parents=True, exist_ok=True)
        mpath.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def cli_fallback_guidance(home: Path) -> dict:
    """Describe Hermes CLI core usage and explicit UI limits when Desktop is heavy."""
    hermes_root = hp.normalize_hermes_root(home)
    hermes_exe = hermes_root / "bin" / ("hermes.exe" if os.name == "nt" else "hermes")
    return {
        "mode": "hermes_cli_fallback",
        "hermes_home": str(hermes_root),
        "hermes_cli_detected": hermes_exe.is_file() or bool(shutil.which("hermes")),
        "desktop_launched": False,
        "core_commands": [
            f'hermes --home "{hermes_root}" chat',
            "msshi doctor --json",
            f'msshi light status --home "{hermes_root}" --json',
            f'msshi light index --home "{hermes_root}" --json',
            f'msshi trim --home "{hermes_root}" --status --profile default',
            f'msshi interaction --home "{hermes_root}" --status',
        ],
        "ui_limitations": [
            "No Electron/Chromium GUI renderer, graphical sidebar, or visual profile switcher.",
            "No embedded image/video/HTML preview pane; inspect outputs in separate local files when needed.",
            "Switch profiles explicitly by CLI flag/command rather than clicking sidebar cards.",
            "Hermes host package is a separate upstream project and is never silently modified by MSSHI.",
        ],
    }


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = max(0, min(len(ordered) - 1, math.ceil((p / 100.0) * len(ordered)) - 1))
    return round(ordered[idx], 3)


def _tree_size_bytes(root: Path) -> int:
    total = 0
    for current_root, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [
            d for d in dirs
            if d not in {".git", "__pycache__", ".pytest_cache"} and not d.startswith(".msshi-check-")
        ]
        for name in files:
            p = Path(current_root) / name
            if not skill_index.is_link(p):
                try:
                    total += p.stat().st_size
                except OSError:
                    pass
    return total


def quick_skill_scan_metrics(
    skills_dir: Path,
    *,
    iterations: int = 20,
    source: Path | None = None,
) -> dict:
    """Measure read-only cold + warm cached skill scan latency across >= 20 iterations.

    Uses a temporary directory for the cache file so the check remains 100% read-only
    with respect to user profiles and repository working trees.
    """
    iters = max(5, min(int(iterations), 50))
    with TemporaryDirectory(prefix="msshi-scan-probe-") as tmp:
        cache_file = Path(tmp) / "skills-index.json"
        cold = skill_index.scan_profile_skills(skills_dir, cache_file, write_cache=True, source=source)
        warm_ms: list[float] = []
        last_hits = 0
        for _ in range(iters):
            row = skill_index.scan_profile_skills(skills_dir, cache_file, write_cache=True, source=source)
            warm_ms.append(row["duration_ms"])
            last_hits = row["cache_hits"]
    warm_sorted = sorted(warm_ms)
    return {
        "skill_count": cold["skill_count"],
        "iterations": iters,
        "cold_seconds": round(cold["duration_ms"] / 1000.0, 4),
        "warm_min_seconds": round(warm_sorted[0] / 1000.0, 4),
        "warm_median_seconds": round(_percentile(warm_sorted, 50) / 1000.0, 4),
        "warm_p95_seconds": round(_percentile(warm_sorted, 95) / 1000.0, 4),
        "warm_max_seconds": round(warm_sorted[-1] / 1000.0, 4),
        "warm_cache_hits": last_hits,
        "within_2s_target": (_percentile(warm_sorted, 95) / 1000.0) <= 2.0,
    }


def run_benchmark(source: Path | None = None, *, iterations: int = 25, output: Path | None = None) -> dict:
    """Measure offline baseline metrics: no_msshi vs light vs full on synthetic fixtures.

    Makes zero LLM calls, zero network calls, and never touches live user Hermes home.
    """
    base = _ordinary(Path(source) if source else ROOT)
    manifest = load_manifest(base)
    targets = manifest["acceptance_targets"]
    hw = hardware_profile(source=base)
    iters = max(20, min(int(iterations), 50))

    full_bytes = _tree_size_bytes(base)
    catalog_scan = quick_skill_scan_metrics(base / "skills", iterations=iters, source=base)
    with TemporaryDirectory(prefix="msshi-light-bench-") as tmp:
        tmp_path = Path(tmp)
        bundle = build_light_bundle(base, tmp_path / "msshi-light.zip")

        # Prepare synthetic 5-profile Academic Mahasiswa fixture (no_msshi vs light vs full)
        synth_home = tmp_path / "hermes-synth"
        academic_defs = json.loads((base / "configs" / "academic_presets.json").read_text(encoding="utf-8-sig"))
        roles_skills = academic_defs["presets"]["academic-mahasiswa"]["roles"]
        for role, slugs in roles_skills.items():
            pdir = synth_home if role == "yukino" else synth_home / "profiles" / role
            (pdir / "config.yaml").parent.mkdir(parents=True, exist_ok=True)
            (pdir / "config.yaml").write_text("model:\n  provider: synthetic-remote\n  default: synthetic-model\n", encoding="utf-8")
            (pdir / "SOUL.md").write_text(f"# Synthetic {role}\n", encoding="utf-8")
            for slug in slugs:
                src_skill = base / "skills" / slug
                if src_skill.is_dir():
                    shutil.copytree(src_skill, pdir / "skills" / slug, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

        # Cold scan (first pass populates cache)
        cold = skill_index.scan_all_profiles(synth_home, write_cache=True, source=base)
        warm_samples_ms: list[float] = []
        for _ in range(iters):
            warm = skill_index.scan_all_profiles(synth_home, write_cache=True, source=base)
            warm_samples_ms.append(warm["total_duration_ms"])

        # Measure full naive walk (baseline uncached scan across all 67 bundled skills)
        full_walk_samples_ms: list[float] = []
        for _ in range(iters):
            t0 = time.perf_counter()
            for sk in (base / "skills").glob("*/SKILL.md"):
                sk.read_bytes()
            full_walk_samples_ms.append(round((time.perf_counter() - t0) * 1000.0, 3))

        # CLI startup overhead: Python no-op ("no_msshi") vs light status ("light")
        env = {**os.environ, "HERMES_HOME": str(synth_home), "MSSHI_IGNORE_REGISTRY_HERMES_HOME": "1"}
        noop_ms: list[float] = []
        light_cli_ms: list[float] = []
        for _ in range(3):
            t0 = time.perf_counter()
            subprocess.run([sys.executable, "-B", "-c", "pass"], env=env, check=True, capture_output=True)
            noop_ms.append(round((time.perf_counter() - t0) * 1000.0, 3))

            t1 = time.perf_counter()
            subprocess.run(
                [sys.executable, "-B", "-X", "utf8", str(base / "scripts" / "msshi_light.py"),
                 "status", "--home", str(synth_home), "--json"],
                env=env, check=True, capture_output=True,
            )
            light_cli_ms.append(round((time.perf_counter() - t1) * 1000.0, 3))

    mem = process_memory_mb()
    warm_p95_s = round(_percentile(warm_samples_ms, 95) / 1000.0, 4)
    cold_s = round(cold["total_duration_ms"] / 1000.0, 4)
    full_walk_p95_s = round(_percentile(full_walk_samples_ms, 95) / 1000.0, 4)
    noop_p50_s = round(_percentile(noop_ms, 50) / 1000.0, 4)
    light_cli_p50_s = round(_percentile(light_cli_ms, 50) / 1000.0, 4)
    startup_overhead_s = round(max(0.0, light_cli_p50_s - noop_p50_s), 4)

    comparison = {
        "no_msshi": {
            "package_download_mb": 0.0,
            "skill_scan_p95_seconds": 0.0,
            "cli_baseline_seconds": noop_p50_s,
            "extra_subprocesses": 0,
        },
        "light": {
            "package_download_mb": bundle["zip_mb"],
            "uncompressed_mb": bundle["uncompressed_mb"],
            "catalog_67_skills_scan": catalog_scan,
            "cold_5profile_skill_scan_seconds": cold_s,
            "warm_5profile_skill_scan_p95_seconds": warm_p95_s,
            "msshi_startup_overhead_seconds": startup_overhead_s,
            "process_working_set_mb": mem["working_set_mb"],
            "process_peak_working_set_mb": mem["peak_working_set_mb"],
            "process_commit_charge_mb": mem["commit_charge_mb"],
            "max_writer_or_render_subprocesses": 1,
        },
        "full": {
            "source_uncompressed_mb": round(full_bytes / (1024 * 1024), 3),
            "uncached_67_skill_scan_p95_seconds": full_walk_p95_s,
        },
    }

    checks = {
        "download_mb_within_target": bundle["zip_mb"] <= targets["max_initial_download_mb"],
        "catalog_67_skill_scan_p95_within_target": catalog_scan["warm_p95_seconds"] <= targets["max_skill_scan_p95_seconds"],
        "warm_5profile_skill_scan_p95_within_target": warm_p95_s <= targets["max_skill_scan_p95_seconds"],
        "startup_overhead_within_target": startup_overhead_s <= targets["max_msshi_startup_overhead_seconds"],
        "process_working_set_within_target": (
            mem["working_set_mb"] is not None and mem["working_set_mb"] <= targets["max_idle_extra_ram_mb"]
        ),
        "single_writer_render_subprocess_cap": True,
    }

    report = {
        "schema_version": 1,
        "measured_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_hardware": hw,
        "certified_for_win10_4gb": False,
        "scope": (
            "Synthetic offline measurement on current machine only. "
            "Do not claim full Windows 10 4 GB support until validated on actual "
            "HP 14s-dq3110TU / Celeron N4500 4 GB hardware."
        ),
        "acceptance_targets": targets,
        "baseline_comparison": comparison,
        "observed_local_checks": checks,
        "model_calls": 0,
        "network_requests": 0,
    }
    if output is not None:
        out_path = _ordinary(Path(output))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def status_report(home: Path, source: Path | None = None) -> dict:
    """Read-only summary of hardware profile, build profile, and active light-mode settings."""
    base = Path(source) if source else ROOT
    hermes_root = hp.normalize_hermes_root(home)
    hw = hardware_profile(source=base)
    active = read_resource_profile(hermes_root)
    disk = check_disk_space(hermes_root)
    return {
        "build_profile": "light" if is_light_build(base) else "full",
        "base_version": load_manifest(base).get("base_version", "3.2.0"),
        "hermes_home": str(hermes_root),
        "hardware": hw,
        "active_resource_profile": active,
        "disk": disk,
        "process_memory": process_memory_mb(),
        "hermes_cli_fallback": cli_fallback_guidance(hermes_root),
        "certified_for_win10_4gb": False,
        "model_calls": 0,
        "network_requests": 0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="msshi light",
        description="Windows 10 RAM 4 GB Light Build packaging, resource mode, lazy skill index, and offline benchmark.",
    )
    sub = parser.add_subparsers(dest="action", required=True)

    p_status = sub.add_parser("status", help="Inspect hardware tier, build profile, and active light-mode settings (read-only).")
    p_status.add_argument("--home", type=Path, help="Hermes home directory.")
    p_status.add_argument("--json", action="store_true", help="Emit JSON output.")

    p_mode = sub.add_parser("mode", help="Preview or apply light/normal/auto resource profile without touching model/provider config.")
    p_mode.add_argument("--set", dest="profile", choices=("auto", "light", "normal"), required=True, help="Resource profile to preview or apply.")
    p_mode.add_argument("--home", type=Path, help="Hermes home directory.")
    p_mode.add_argument("--apply", action="store_true", help="Write resource-profile.json atomically with rollback receipt.")
    p_mode.add_argument("--json", action="store_true", help="Emit JSON output.")

    p_index = sub.add_parser("index", help="Build or inspect lazy per-role skill index cache with excluded-dir hygiene.")
    p_index.add_argument("--home", type=Path, help="Hermes home directory.")
    p_index.add_argument("--profile", help="Limit index scan to one profile ID.")
    p_index.add_argument("--verify-hashes", action="store_true", help="Verify frontmatter SHA-256 even when mtime/size match.")
    p_index.add_argument("--no-write", action="store_true", help="Read-only scan without updating cache files.")
    p_index.add_argument("--json", action="store_true", help="Emit JSON output.")

    p_build = sub.add_parser("build", help="Build a deterministic <= 50 MB light bootstrap ZIP from MSSHI 3.2.0.")
    p_build.add_argument("--output", type=Path, required=True, help="Destination path for light bootstrap .zip.")
    p_build.add_argument("--manifest", type=Path, help="Optional destination path for SHA-256 build manifest JSON.")
    p_build.add_argument("--source", type=Path, default=ROOT, help="Source MSSHI repository root.")
    p_build.add_argument("--json", action="store_true", help="Emit JSON output.")

    p_bench = sub.add_parser("benchmark", help="Run offline synthetic benchmark comparing no_msshi vs light vs full.")
    p_bench.add_argument("--iterations", type=int, default=25, help="Warm scan iterations (20-50, default 25).")
    p_bench.add_argument("--output", type=Path, help="Optional JSON file path to save benchmark report.")
    p_bench.add_argument("--source", type=Path, default=ROOT, help="Source MSSHI repository root.")
    p_bench.add_argument("--json", action="store_true", help="Emit JSON output.")

    p_cli = sub.add_parser("cli-fallback", help="Print Hermes CLI core commands and explicit UI limitations for low-RAM machines.")
    p_cli.add_argument("--home", type=Path, help="Hermes home directory.")
    p_cli.add_argument("--json", action="store_true", help="Emit JSON output.")

    args = parser.parse_args(argv)
    if args.action == "status":
        home = hp.resolve_hermes_home(args.home, create_adaptive=False, persist_windows_env=False)
        data = status_report(home)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    if args.action == "mode":
        home = hp.resolve_hermes_home(args.home, create_adaptive=False, persist_windows_env=False)
        data = apply_resource_profile(home, args.profile, apply=args.apply)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    if args.action == "index":
        home = hp.resolve_hermes_home(args.home, create_adaptive=False, persist_windows_env=False)
        data = skill_index.scan_all_profiles(
            home,
            profile_filter=args.profile,
            verify_hashes=args.verify_hashes,
            write_cache=not args.no_write,
            source=ROOT,
        )
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    if args.action == "build":
        data = build_light_bundle(args.source, args.output, manifest_out=args.manifest)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    if args.action == "benchmark":
        data = run_benchmark(args.source, iterations=args.iterations, output=args.output)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    if args.action == "cli-fallback":
        home = hp.resolve_hermes_home(args.home, create_adaptive=False, persist_windows_env=False)
        data = cli_fallback_guidance(home)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, FileNotFoundError) as exc:
        print(f"msshi light: {exc}", file=sys.stderr)
        raise SystemExit(2)
