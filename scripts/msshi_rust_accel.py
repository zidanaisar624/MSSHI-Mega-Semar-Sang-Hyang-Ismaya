#!/usr/bin/env python3
"""Optional bridge to the native MSSHI Rust hot-path accelerator (`msshi-accel`).

Follows the MSSHI Hot-Path Only rule (< 40% Rust surface): orchestrators, CLI UX,
personas, and configuration transactions remain in Python/Node, while high-I/O tree
walks, SHA-256 inventories, SKILL.md frontmatter indexing, and large text compaction
use `msshi-accel` when present and fall back transparently to Python otherwise.
"""
from __future__ import annotations

from collections.abc import Iterable
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BIN_NAME = "msshi-accel.exe" if os.name == "nt" else "msshi-accel"


def resolve_accel_binary() -> Path | None:
    """Locate a verified local `msshi-accel` binary without network or build side effects."""
    if os.environ.get("MSSHI_DISABLE_RUST_ACCEL") == "1":
        return None
    candidates: list[Path] = []
    if env_bin := os.environ.get("MSSHI_ACCEL_BIN"):
        candidates.append(Path(env_bin))
    candidates.append(ROOT / "crates" / "msshi-rust-accel" / "target" / "release" / BIN_NAME)
    if hermes_home := os.environ.get("HERMES_HOME"):
        candidates.append(Path(hermes_home) / "tools" / "msshi-accel" / BIN_NAME)
    if os.name == "nt":
        d_drive = os.environ.get("MSSHI_WINDOWS_D_DRIVE", "D:/")
        candidates.append(Path(d_drive) / "HermesData" / "tools" / "msshi-accel" / BIN_NAME)
    if which_bin := shutil.which("msshi-accel"):
        candidates.append(Path(which_bin))

    for cand in candidates:
        try:
            if cand.is_file() and not cand.is_symlink():
                return cand
        except OSError:
            continue
    return None


def _run_json(args: list[str], *, input_text: str | None = None, timeout: int = 30) -> dict | None:
    binary = resolve_accel_binary()
    if binary is None:
        return None
    try:
        proc = subprocess.run(
            [str(binary), *args],
            input=input_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
        )
        if proc.returncode != 0:
            return None
        data = json.loads(proc.stdout)
        return data if isinstance(data, dict) else None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def try_secret_scan(repo_root: Path) -> dict | None:
    """Run native Rust secret/privacy scan if `msshi-accel` is installed."""
    return _run_json(["secret-scan", str(repo_root)], timeout=45)


def try_inventory(directory: Path) -> dict[str, str] | None:
    """Compute recursive SHA-256 file map via `msshi-accel` if installed."""
    data = _run_json(["inventory", str(directory)], timeout=45)
    if data is None or not all(isinstance(k, str) and isinstance(v, str) for k, v in data.items()):
        return None
    return data


def try_skill_scan(skills_dir: Path, excluded: Iterable[str]) -> dict | None:
    """Scan SKILL.md 4 KiB frontmatter blocks via `msshi-accel` if installed."""
    csv = ",".join(sorted(set(excluded)))
    return _run_json(["skill-scan", str(skills_dir), csv], timeout=20)


def try_compact_text(text: str, max_chars: int) -> str | None:
    """Compact large prose via `msshi-accel` while keeping code fences and citations."""
    binary = resolve_accel_binary()
    if binary is None:
        return None
    try:
        proc = subprocess.run(
            [str(binary), "compact-text", str(max_chars)],
            input=text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=15,
        )
        if proc.returncode != 0:
            return None
        return proc.stdout.rstrip("\r\n")
    except (OSError, subprocess.SubprocessError):
        return None
