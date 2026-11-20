#!/usr/bin/env python3
"""MSSHI upstream governance CLI: non-applying update check, local integrity audit, and pinned Ponytail installer.

MSSHI pins upstream GitHub repositories to reviewed commits and NEVER auto-updates silently.
`msshi upstreams check` only reports whether upstream HEAD has moved ahead of our pin.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any
from urllib.parse import urlsplit

sys.dont_write_bytecode = True

_SCRIPTS_DIR = str(Path(__file__).resolve().parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import msshi_context_sources as cs
import msshi_hermes_profiles as hp

ROOT = Path(__file__).resolve().parents[1]
UPSTREAMS_MANIFEST = ROOT / "configs" / "upstreams.json"
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
PONYTAIL_REPO = "dietrichgebert/ponytail"
PONYTAIL_PIN = "96608e078b2d5ea607c5c3b8b5a54d1c1fba6846"
CAVEMAN_PIN = "3dc497a7f858c774d6e15b25e8c6120ef3a0eda8"


def _load_entries(manifest_path: Path = UPSTREAMS_MANIFEST) -> list[dict[str, Any]]:
    data = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    return [row for row in data.get("entries", []) if isinstance(row, dict)]


def _git_ls_remote_head(url: str, *, timeout: int = 20) -> str | None:
    """Resolve remote HEAD commit SHA via `git ls-remote` (avoids 60 req/hr GitHub REST API limits)."""
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc.lower() != "github.com":
        return None
    git_url = f"https://github.com{parsed.path.rstrip('/').removesuffix('.git')}.git"
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(
        GIT_CONFIG_NOSYSTEM="1",
        GIT_CONFIG_GLOBAL=os.devnull,
        GIT_TERMINAL_PROMPT="0",
        GIT_LFS_SKIP_SMUDGE="1",
    )
    proc = subprocess.run(
        [
            "git",
            "-c", "protocol.allow=never",
            "-c", "protocol.https.allow=always",
            "-c", "credential.helper=",
            "ls-remote", "--symref", git_url, "HEAD",
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if proc.returncode != 0:
        return None
    for line in proc.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "HEAD" and COMMIT_RE.fullmatch(parts[0]):
            return parts[0]
    return None


def check_updates(
    *,
    manifest_path: Path = UPSTREAMS_MANIFEST,
    ids: list[str] | None = None,
    limit: int | None = None,
    workers: int = 4,
    resolver=_git_ls_remote_head,
) -> dict[str, Any]:
    """Compare pinned revisions against live upstream HEAD without modifying or installing anything."""
    entries = _load_entries(manifest_path)
    if ids:
        wanted = {item.strip().lower() for item in ids if item.strip()}
        entries = [row for row in entries if str(row.get("id", "")).lower() in wanted]
    if limit is not None and limit > 0:
        entries = entries[:limit]

    def inspect_one(row: dict[str, Any]) -> dict[str, Any]:
        uid = str(row.get("id", ""))
        src = str(row.get("source", ""))
        pin = str(row.get("revision") or "").strip()
        stype = str(row.get("source_type") or "")
        base = {
            "id": uid,
            "source": src,
            "source_type": stype,
            "pinned_revision": pin or None,
            "license": row.get("license"),
        }
        if stype != "git":
            return {**base, "remote_head": None, "status": "non_git"}
        try:
            remote_head = resolver(src)
        except Exception as exc:  # noqa: BLE001
            return {**base, "remote_head": None, "status": "unreachable", "error": str(exc)[:160]}
        if not remote_head:
            return {**base, "remote_head": None, "status": "unreachable"}
        if not pin:
            return {**base, "remote_head": remote_head, "status": "unpinned"}
        status = "up_to_date" if remote_head.lower() == pin.lower() else "update_available"
        return {**base, "remote_head": remote_head, "status": status}

    max_workers = max(1, min(workers, len(entries) or 1))
    if max_workers == 1:
        rows = [inspect_one(row) for row in entries]
    else:
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            rows = list(pool.map(inspect_one, entries))

    counts = {
        "total_checked": len(rows),
        "up_to_date": sum(1 for r in rows if r["status"] == "up_to_date"),
        "update_available": sum(1 for r in rows if r["status"] == "update_available"),
        "unpinned": sum(1 for r in rows if r["status"] == "unpinned"),
        "non_git": sum(1 for r in rows if r["status"] == "non_git"),
        "unreachable": sum(1 for r in rows if r["status"] == "unreachable"),
    }
    return {
        "mode": "read_only_report_only",
        "auto_update": False,
        "applied": False,
        "note": "MSSHI mengunci upstream ke commit terpin demi keamanan. Pembaruan tidak pernah dipasang otomatis — review diff dulu sebelum menaikkan pin.",
        "summary": counts,
        "updates_available": [r for r in rows if r["status"] == "update_available"],
        "entries": rows,
    }


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while chunk := fh.read(65536):
            h.update(chunk)
    return h.hexdigest()


def integrity_report(home: Path) -> dict[str, Any]:
    """Offline integrity check for Caveman (5 named bots), Ponytail (Shikaku), and pinned context sources."""
    home = cs.checked(home)
    live = hp.live_named_profiles(home)

    # 1. Caveman integrity
    cav_root = home / "msshi-private" / "v3-sources" / "caveman" / CAVEMAN_PIN
    cav_snap = cav_root / "MSSHI_SNAPSHOT.json"
    cav_mismatches: list[str] = []
    if cav_snap.is_file():
        snap = json.loads(cav_snap.read_text(encoding="utf-8-sig"))
        for rel, expected in (snap.get("files") or {}).items():
            f = cav_root / rel
            if not f.is_file() or _sha256(f) != expected:
                cav_mismatches.append(rel)
    cav_profiles: dict[str, dict[str, Any]] = {}
    cav_hashes: set[str] = set()
    for role in ("yukino", "shizuka", "val", "kiki-chii", "shikaku"):
        folder = live.get(role)
        sk = (folder / "skills" / "caveman" / "SKILL.md") if folder else None
        lic = (folder / "skills" / "caveman" / "LICENSE") if folder else None
        digest = _sha256(sk)[:16] if sk and sk.is_file() else None
        if digest:
            cav_hashes.add(digest)
        cav_profiles[role] = {
            "installed": bool(sk and sk.is_file()),
            "license_present": bool(lic and lic.is_file()),
            "skill_sha256_prefix": digest,
        }

    # 2. Ponytail integrity (Shikaku)
    pony_root = home / "msshi-private" / "v3-sources" / "ponytail" / PONYTAIL_PIN
    pony_snap = pony_root / "MSSHI_SNAPSHOT.json"
    pony_mismatches: list[str] = []
    if pony_snap.is_file():
        snap = json.loads(pony_snap.read_text(encoding="utf-8-sig"))
        for rel, expected in (snap.get("files") or {}).items():
            f = pony_root / rel
            if not f.is_file() or _sha256(f) != expected:
                pony_mismatches.append(rel)
    shikaku_dir = live.get("shikaku")
    pony_sk = (shikaku_dir / "skills" / "ponytail" / "SKILL.md") if shikaku_dir else None
    pony_lic = (shikaku_dir / "skills" / "ponytail" / "LICENSE") if shikaku_dir else None

    # 3. Context sources cache status (read-only)
    ctx_sources: dict[str, bool] = {}
    for name in cs.PINNED:
        try:
            ctx_sources[name] = cs.verify_cached(home, name) is not None
        except (OSError, ValueError):
            ctx_sources[name] = False

    return {
        "hermes_home": str(home),
        "network_calls": 0,
        "caveman": {
            "pin": CAVEMAN_PIN,
            "snapshot_present": cav_snap.is_file(),
            "snapshot_mismatches": cav_mismatches,
            "installed_profiles": sum(1 for v in cav_profiles.values() if v["installed"]),
            "all_profiles_consistent": len(cav_hashes) == 1 and all(v["installed"] for v in cav_profiles.values()),
            "profiles": cav_profiles,
        },
        "ponytail": {
            "pin": PONYTAIL_PIN,
            "target_profile": "shikaku",
            "snapshot_present": pony_snap.is_file(),
            "snapshot_mismatches": pony_mismatches,
            "installed": bool(pony_sk and pony_sk.is_file()),
            "license_present": bool(pony_lic and pony_lic.is_file()),
            "skill_sha256_prefix": _sha256(pony_sk)[:16] if pony_sk and pony_sk.is_file() else None,
        },
        "context_sources_cached": ctx_sources,
        "context_sources_ready": sum(1 for ok in ctx_sources.values() if ok),
        "context_sources_total": len(ctx_sources),
    }


def install_ponytail(home: Path) -> dict[str, Any]:
    """Install MIT Ponytail from reviewed pinned commit 96608e07 into Shikaku's skills/ only."""
    home = cs.checked(home)
    live = hp.live_named_profiles(home)
    shikaku_dir = live.get("shikaku")
    if shikaku_dir is None:
        raise ValueError("Profil shikaku tidak ditemukan di " + str(home))

    snap_root = cs.checked(home / "msshi-private" / "v3-sources" / "ponytail" / PONYTAIL_PIN)
    wanted_files = ("skills/ponytail/SKILL.md", "LICENSE", "README.md")
    hashes: dict[str, str] = {}

    if not (snap_root / "MSSHI_SNAPSHOT.json").is_file():
        with tempfile.TemporaryDirectory(prefix="msshi-ponytail-") as tmp:
            clone_dir = Path(tmp) / "repo"
            subprocess.run(
                [
                    "git", "-c", "http.postBuffer=16m", "-c", "pack.windowMemory=32m", "-c", "pack.threads=1",
                    "clone", "--bare", "--depth=1", f"https://github.com/{PONYTAIL_REPO}.git", str(clone_dir),
                ],
                check=True, capture_output=True, timeout=120,
            )
            if subprocess.run(["git", "-C", str(clone_dir), "cat-file", "-e", f"{PONYTAIL_PIN}^{{commit}}"], capture_output=True).returncode != 0:
                subprocess.run(
                    ["git", "-C", str(clone_dir), "fetch", "--depth=1", "origin", PONYTAIL_PIN],
                    check=True, capture_output=True, timeout=120,
                )
            ls = subprocess.run(["git", "-C", str(clone_dir), "ls-tree", "-r", "-z", PONYTAIL_PIN],
                                check=True, capture_output=True, timeout=30)
            sha_map: dict[str, str] = {}
            for entry in ls.stdout.split(b"\x00"):
                if not entry:
                    continue
                meta, path_b = entry.split(b"\t", 1)
                parts = meta.decode("ascii").split()
                if len(parts) >= 3 and parts[1] == "blob":
                    sha_map[path_b.decode("utf-8")] = parts[2]
            for rel in wanted_files:
                if rel not in sha_map:
                    raise ValueError(f"Ponytail pinned commit missing {rel}")
                data = subprocess.run(["git", "-C", str(clone_dir), "cat-file", "blob", sha_map[rel]],
                                      check=True, capture_output=True, timeout=30).stdout
                if hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest() != sha_map[rel]:
                    raise ValueError(f"Ponytail blob SHA-1 mismatch: {rel}")
                cs.atomic(snap_root / cs.relative(rel), data)
                hashes[rel] = hashlib.sha256(data).hexdigest()
            cs.atomic(
                snap_root / "MSSHI_SNAPSHOT.json",
                cs.encode({"repository": PONYTAIL_REPO, "commit": PONYTAIL_PIN, "license": "MIT", "files": hashes}),
            )

    dest = cs.checked(shikaku_dir / "skills" / "ponytail")
    skill_bytes = (snap_root / "skills" / "ponytail" / "SKILL.md").read_bytes()
    lic_bytes = (snap_root / "LICENSE").read_bytes()
    cs.atomic(dest / "SKILL.md", skill_bytes)
    cs.atomic(dest / "LICENSE", lic_bytes)
    return {
        "installed": True,
        "repository": PONYTAIL_REPO,
        "commit": PONYTAIL_PIN,
        "license": "MIT",
        "profile": "shikaku",
        "dest": str(dest),
        "provider_model_mutated": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="msshi upstreams", description=__doc__)
    sub = parser.add_subparsers(dest="action")

    p_check = sub.add_parser("check", help="Cek apakah ada commit baru di GitHub upstream tanpa memasang apa pun.")
    p_check.add_argument("--id", action="append", help="Filter 1 atau lebih ID upstream (mis. --id ossu-computer-science --id caveman).")
    p_check.add_argument("--limit", type=int, help="Batasi jumlah upstream yang diperiksa.")
    p_check.add_argument("--json", action="store_true", help="Keluaran JSON.")

    p_int = sub.add_parser("integrity", help="Audit integritas lokal Caveman, Ponytail, dan cache context-sources (offline).")
    p_int.add_argument("--home", type=Path, help="Folder Hermes home.")
    p_int.add_argument("--json", action="store_true", help="Keluaran JSON.")

    p_pony = sub.add_parser("install-ponytail", help="Pasang Ponytail (MIT, pin 96608e07) ke profil Shikaku saja.")
    p_pony.add_argument("--home", type=Path, help="Folder Hermes home.")
    p_pony.add_argument("--json", action="store_true", help="Keluaran JSON.")

    args = parser.parse_args(argv)
    action = args.action or "integrity"
    try:
        if action == "check":
            res = check_updates(ids=args.id, limit=args.limit)
            if args.json:
                print(json.dumps(res, ensure_ascii=False, indent=2))
            else:
                s = res["summary"]
                print(f"=== MSSHI Upstreams Check (Read-Only, Auto-Update=OFF) ===")
                print(f"Diperiksa: {s['total_checked']} | Sama: {s['up_to_date']} | Ada Update: {s['update_available']} | Non-Git: {s['non_git']} | Gagal/Unreachable: {s['unreachable']}")
                if res["updates_available"]:
                    print("\nUpstream dengan commit lebih baru dari pin MSSHI:")
                    for row in res["updates_available"]:
                        print(f"  - {row['id']:<28} pin={str(row['pinned_revision'])[:8]} -> remote={str(row['remote_head'])[:8]} ({row['source']})")
                print("\nCatatan:", res["note"])
            return 0

        home = cs.checked(hp.resolve_hermes_home(getattr(args, "home", None)))
        if action == "integrity":
            res = integrity_report(home)
            if args.json:
                print(json.dumps(res, ensure_ascii=False, indent=2))
            else:
                cav = res["caveman"]
                pony = res["ponytail"]
                print(f"=== MSSHI Upstreams Integrity ({res['hermes_home']}) ===")
                print(f"Caveman  (pin {cav['pin'][:8]}): {cav['installed_profiles']}/5 bot bernama, konsisten={cav['all_profiles_consistent']}, mismatch_snapshot={len(cav['snapshot_mismatches'])}")
                print(f"Ponytail (pin {pony['pin'][:8]}): terpasang di shikaku={pony['installed']}, lisensi={pony['license_present']}, mismatch_snapshot={len(pony['snapshot_mismatches'])}")
                print(f"Context Sources Cached     : {res['context_sources_ready']}/{res['context_sources_total']}")
            return 0

        if action == "install-ponytail":
            res = install_ponytail(home)
            print(json.dumps(res, ensure_ascii=False, indent=2))
            return 0

        parser.print_help()
        return 0
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"msshi upstreams: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
