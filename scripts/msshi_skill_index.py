#!/usr/bin/env python3
"""Lazy per-role skill indexer with hash/mtime caching and targeted invalidation.

Keeps all Hermes profiles visible while scanning only lightweight SKILL.md
frontmatter on cache miss. Never descends into .git, node_modules, model/
checkpoint, video, eval, cache, or upstream directories. Full SKILL.md bodies
and reference files are loaded lazily only when requested.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import time

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "configs" / "light_build_manifest.json"
DEFAULT_EXCLUDED_SCAN_DIRS = frozenset({
    ".git",
    "node_modules",
    "model",
    "models",
    "checkpoint",
    "checkpoints",
    "video",
    "videos",
    "eval",
    "evals",
    "cache",
    ".cache",
    "venv",
    ".venv",
    "__pycache__",
    "upstreams",
    "context-sources",
})
STAGING_PREFIXES = (".msshi-backup-", ".msshi-stage-")
FRONTMATTER_LIMIT_BYTES = 4096
FRONTMATTER_NAME_RE = re.compile(r"(?m)^name:[ \t]*['\"]?([^'\"\r\n]+?)['\"]?[ \t]*$")
FRONTMATTER_DESC_RE = re.compile(r"(?m)^description:[ \t]*['\"]?(.+?)['\"]?[ \t]*$")
SAFE_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$", re.I)


def excluded_scan_dirs(source: Path | None = None) -> frozenset[str]:
    """Return lowercase directory names excluded from skill scanning."""
    manifest = (Path(source) if source else ROOT) / "configs" / "light_build_manifest.json"
    try:
        if manifest.is_file() and not is_link(manifest):
            data = json.loads(manifest.read_text(encoding="utf-8-sig"))
            items = data.get("excluded_skill_scan_dirs")
            if isinstance(items, list) and items:
                return frozenset(str(item).strip().lower() for item in items if str(item).strip())
    except (OSError, ValueError):
        pass
    return DEFAULT_EXCLUDED_SCAN_DIRS


def is_link(path: Path) -> bool:
    """Return True if path is a symlink or Windows reparse point (junction)."""
    try:
        info = path.lstat()
    except OSError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    )


def _check_ordinary_ancestors(path: Path) -> Path:
    resolved = Path(os.path.abspath(os.fspath(path)))
    if str(resolved).startswith(("\\\\", "//")):
        raise ValueError("UNC paths are not accepted for skill index operations.")
    for part in (*reversed(resolved.parents), resolved):
        if os.path.lexists(part) and is_link(part):
            raise ValueError(f"Symlink/junction is not allowed in skill index path: {part}")
    return resolved


def _atomic_write_json(path: Path, payload: dict) -> None:
    target = _check_ordinary_ancestors(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".skill-idx-", delete=False) as handle:
        temp = Path(handle.name)
        handle.write(raw)
        handle.flush()
    try:
        os.replace(temp, target)
    finally:
        temp.unlink(missing_ok=True)


def _read_frontmatter_metadata(skill_md: Path) -> dict:
    """Read at most FRONTMATTER_LIMIT_BYTES from SKILL.md for lightweight metadata."""
    with skill_md.open("rb") as handle:
        head = handle.read(FRONTMATTER_LIMIT_BYTES)
    digest = hashlib.sha256(head).hexdigest()
    text = head.decode("utf-8-sig", errors="replace")
    name = skill_md.parent.name
    description = ""
    if text.startswith("---"):
        lines = text.splitlines()
        block_lines = []
        for line in lines[1:]:
            if line.strip() == "---":
                break
            block_lines.append(line)
        block = "\n".join(block_lines)
        match_name = FRONTMATTER_NAME_RE.search(block)
        if match_name:
            name = match_name.group(1).strip()
        match_desc = FRONTMATTER_DESC_RE.search(block)
        if match_desc:
            description = match_desc.group(1).strip()[:240]
    return {
        "name": name,
        "description": description,
        "head_sha256": digest,
    }


def _load_cache(cache_path: Path | None) -> dict:
    if cache_path is None:
        return {}
    try:
        target = _check_ordinary_ancestors(cache_path)
        if not target.is_file() or target.stat().st_size > 4 * 1024 * 1024:
            return {}
        data = json.loads(target.read_text(encoding="utf-8-sig"))
        if isinstance(data, dict) and data.get("schema_version") == 1 and isinstance(data.get("entries"), dict):
            return data
    except (OSError, ValueError):
        pass
    return {}


def scan_profile_skills(
    skills_dir: Path,
    cache_path: Path | None = None,
    *,
    verify_hashes: bool = False,
    write_cache: bool = True,
    source: Path | None = None,
) -> dict:
    """Incrementally index a single profile's skills directory with mtime/size cache.

    Cache hits avoid reading SKILL.md from disk entirely unless verify_hashes=True.
    Invalidation is targeted strictly to added, modified, or removed skill folders.
    """
    started = time.perf_counter()
    skills_root = _check_ordinary_ancestors(skills_dir)
    excluded = excluded_scan_dirs(source)
    prior = _load_cache(cache_path)
    prior_entries = prior.get("entries", {}) if isinstance(prior, dict) else {}

    entries: dict[str, dict] = {}
    excluded_skipped: list[str] = []
    hygiene_warnings: list[str] = []
    cache_hits = 0
    cache_misses = 0
    invalidated: list[str] = []
    added: list[str] = []

    if skills_root.is_dir() and not prior_entries:
        try:
            from msshi_rust_accel import try_skill_scan
            fast = try_skill_scan(skills_root, excluded)
        except ImportError:
            fast = None
        if isinstance(fast, dict) and isinstance(fast.get("entries"), dict):
            entries = fast["entries"]
            excluded_skipped = list(fast.get("excluded_skipped") or [])
            hygiene_warnings = list(fast.get("hygiene_warnings") or [])
            cache_misses = len(entries)
            added = sorted(entries)
            duration_ms = round((time.perf_counter() - started) * 1000.0, 3)
            cache_payload = {
                "schema_version": 1,
                "skills_dir": str(skills_root),
                "skill_count": len(entries),
                "excluded_scan_dirs": sorted(excluded),
                "entries": entries,
            }
            if write_cache and cache_path is not None and (cache_misses > 0 or not cache_path.is_file()):
                _atomic_write_json(cache_path, cache_payload)
            return {
                "skills_dir": str(skills_root),
                "cache_path": str(cache_path) if cache_path else None,
                "skill_count": len(entries),
                "cache_hits": 0,
                "cache_misses": cache_misses,
                "added": added,
                "invalidated": [],
                "removed": [],
                "excluded_dirs_skipped": sorted(excluded_skipped),
                "hygiene_warnings": hygiene_warnings,
                "duration_ms": duration_ms,
                "body_loaded": False,
                "skills": [
                    {
                        "slug": row["slug"],
                        "name": row["name"],
                        "description": row["description"],
                        "has_references": row["has_references"],
                        "has_scripts": row["has_scripts"],
                    }
                    for row in entries.values()
                ],
            }

    if skills_root.is_dir():
        try:
            with os.scandir(skills_root) as it:
                dir_entries = sorted(it, key=lambda e: e.name.lower())
        except OSError as exc:
            raise OSError(f"Cannot scan skills directory {skills_root}: {exc}") from exc

        for entry in dir_entries:
            name = entry.name
            lower = name.lower()
            child = Path(entry.path)
            if name.startswith(STAGING_PREFIXES) or is_link(child):
                excluded_skipped.append(name)
                continue
            if lower in excluded:
                excluded_skipped.append(name)
                hygiene_warnings.append(
                    f"Excluded heavy directory '{name}' found inside skills root ({skills_root}); move outside skills."
                )
                continue
            if not entry.is_dir(follow_symlinks=False):
                continue

            skill_md = child / "SKILL.md"
            if not os.path.lexists(skill_md) or is_link(skill_md):
                # Check for nested heavy directories inside non-skill folders without descending deeply
                continue
            try:
                st = skill_md.stat()
            except OSError:
                continue

            # Lightweight check for accidental heavy child dirs directly under a skill folder
            try:
                with os.scandir(child) as sub_it:
                    sub_names = {sub.name.lower() for sub in sub_it if sub.is_dir(follow_symlinks=False)}
            except OSError:
                sub_names = set()
            nested_heavy = sorted(sub_names & excluded)
            for heavy in nested_heavy:
                excluded_skipped.append(f"{name}/{heavy}")
                hygiene_warnings.append(
                    f"Excluded heavy directory '{name}/{heavy}' inside skill '{name}'; skipped by lazy indexer."
                )

            cached = prior_entries.get(name)
            unchanged = (
                isinstance(cached, dict)
                and cached.get("mtime_ns") == st.st_mtime_ns
                and cached.get("size") == st.st_size
                and cached.get("has_references") == ("references" in sub_names)
                and cached.get("has_scripts") == ("scripts" in sub_names)
            )
            if unchanged and verify_hashes:
                fresh = _read_frontmatter_metadata(skill_md)
                if fresh["head_sha256"] != cached.get("head_sha256"):
                    unchanged = False
            if unchanged:
                entries[name] = cached
                cache_hits += 1
            else:
                meta = _read_frontmatter_metadata(skill_md)
                entries[name] = {
                    "slug": name,
                    "name": meta["name"],
                    "description": meta["description"],
                    "rel_path": f"{name}/SKILL.md",
                    "mtime_ns": st.st_mtime_ns,
                    "size": st.st_size,
                    "head_sha256": meta["head_sha256"],
                    "has_references": "references" in sub_names,
                    "has_scripts": "scripts" in sub_names,
                    "body_loaded": False,
                }
                cache_misses += 1
                if name in prior_entries:
                    invalidated.append(name)
                else:
                    added.append(name)

    removed = sorted(set(prior_entries) - set(entries))
    duration_ms = round((time.perf_counter() - started) * 1000.0, 3)

    cache_payload = {
        "schema_version": 1,
        "skills_dir": str(skills_root),
        "skill_count": len(entries),
        "excluded_scan_dirs": sorted(excluded),
        "entries": entries,
    }
    if write_cache and cache_path is not None and (cache_misses > 0 or removed or not cache_path.is_file()):
        _atomic_write_json(cache_path, cache_payload)

    return {
        "skills_dir": str(skills_root),
        "cache_path": str(cache_path) if cache_path else None,
        "skill_count": len(entries),
        "cache_hits": cache_hits,
        "cache_misses": cache_misses,
        "added": sorted(added),
        "invalidated": sorted(invalidated),
        "removed": removed,
        "excluded_dirs_skipped": sorted(excluded_skipped),
        "hygiene_warnings": hygiene_warnings,
        "duration_ms": duration_ms,
        "body_loaded": False,
        "skills": [
            {
                "slug": row["slug"],
                "name": row["name"],
                "description": row["description"],
                "has_references": row["has_references"],
                "has_scripts": row["has_scripts"],
            }
            for row in entries.values()
        ],
    }


def scan_all_profiles(
    home: Path,
    *,
    profile_filter: str | None = None,
    verify_hashes: bool = False,
    write_cache: bool = True,
    source: Path | None = None,
) -> dict:
    """Build or refresh lazy skill indices for every live Hermes profile."""
    started = time.perf_counter()
    hermes_root = _check_ordinary_ancestors(home)
    index_root = hermes_root / "msshi-runtime" / "skill-index"

    profile_dirs: dict[str, Path] = {}
    if (hermes_root / "skills").is_dir() or (hermes_root / "config.yaml").is_file():
        profile_dirs["default"] = hermes_root
    profiles_parent = hermes_root / "profiles"
    if profiles_parent.is_dir() and not is_link(profiles_parent):
        deleted_dir = profiles_parent / ".deleted"
        for child in sorted(profiles_parent.iterdir(), key=lambda p: p.name.lower()):
            if child.name.startswith(".") or not child.is_dir() or is_link(child):
                continue
            if (deleted_dir / child.name).exists():
                continue
            if (child / "skills").is_dir() or (child / "config.yaml").is_file() or (child / "profile.yaml").is_file():
                profile_dirs[child.name] = child

    if profile_filter:
        if profile_filter not in profile_dirs:
            raise ValueError(f"Profile '{profile_filter}' not found under {hermes_root}")
        profile_dirs = {profile_filter: profile_dirs[profile_filter]}

    results = {}
    total_skills = 0
    total_hits = 0
    total_misses = 0
    all_warnings: list[str] = []
    for name, folder in profile_dirs.items():
        cache_path = index_root / f"{name}.json"
        row = scan_profile_skills(
            folder / "skills",
            cache_path,
            verify_hashes=verify_hashes,
            write_cache=write_cache,
            source=source,
        )
        results[name] = row
        total_skills += row["skill_count"]
        total_hits += row["cache_hits"]
        total_misses += row["cache_misses"]
        all_warnings.extend(f"[{name}] {msg}" for msg in row["hygiene_warnings"])

    upstream_in_skills = any(
        (folder / "skills" / bad).exists()
        for folder in profile_dirs.values()
        for bad in ("upstreams", "context-sources")
    )
    return {
        "home": str(hermes_root),
        "profiles_visible": sorted(profile_dirs.keys()),
        "profile_count": len(profile_dirs),
        "total_skills_indexed": total_skills,
        "total_cache_hits": total_hits,
        "total_cache_misses": total_misses,
        "upstream_cache_outside_skills": not upstream_in_skills,
        "hygiene_warnings": all_warnings,
        "total_duration_ms": round((time.perf_counter() - started) * 1000.0, 3),
        "profiles": results,
    }


def load_skill_content(
    skills_dir: Path,
    slug: str,
    *,
    reference: str | None = None,
    max_bytes: int = 262144,
) -> dict:
    """Lazily read a single skill's SKILL.md (or one named reference file) on demand."""
    if not isinstance(slug, str) or not SAFE_SLUG_RE.fullmatch(slug):
        raise ValueError(f"Invalid skill slug: {slug!r}")
    root = _check_ordinary_ancestors(skills_dir)
    skill_dir = _check_ordinary_ancestors(root / slug)
    if not skill_dir.is_relative_to(root) or not skill_dir.is_dir():
        raise FileNotFoundError(f"Skill folder not found: {slug}")
    if reference:
        rel = Path(reference)
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError(f"Invalid reference path: {reference!r}")
        target = _check_ordinary_ancestors(skill_dir / "references" / rel)
        if not target.is_relative_to(skill_dir / "references"):
            raise ValueError(f"Reference escapes skill directory: {reference!r}")
    else:
        target = _check_ordinary_ancestors(skill_dir / "SKILL.md")
    if not target.is_file():
        raise FileNotFoundError(f"Requested skill file not found: {target.name}")
    size = target.stat().st_size
    if size > max_bytes:
        raise ValueError(f"Requested file exceeds max_bytes ({size} > {max_bytes})")
    raw = target.read_bytes()
    return {
        "slug": slug,
        "path": str(target),
        "size_bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "content": raw.decode("utf-8-sig", errors="replace"),
    }
