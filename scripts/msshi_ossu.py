#!/usr/bin/env python3
"""MSSHI connector for OSSU (Open Source Society University) Computer Science.

OSSU is NOT a bot skill — it is a free, open-source undergraduate-equivalent
Computer Science curriculum (https://cs.ossu.dev | https://github.com/ossu/computer-science).
This connector exposes a read-only local curriculum browser and study launcher
over the pinned cache in msshi-private/context-sources/ossu-computer-science/.

Zero background LLM calls, zero auto-open on boot, zero provider/model mutation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
import webbrowser

sys.dont_write_bytecode = True

_SCRIPTS_DIR = str(Path(__file__).resolve().parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import msshi_context_sources as cs
import msshi_hermes_profiles as hp

SOURCE_NAME = "ossu-computer-science"
PORTAL_URL = "https://cs.ossu.dev"
REPO_URL = "https://github.com/ossu/computer-science"
DISCORD_URL = "https://discord.gg/wuytwK5s9h"

GUIDE_ALIASES: dict[str, tuple[str, str]] = {
    "intro-cs": ("coursepages/intro-cs/README.md", "Intro CS — Introduction to Computer Science and Programming using Python (MIT 6.100L OCW)"),
    "intro-programming": ("coursepages/intro-programming/README.md", "Absolute Beginner — Introduction to Programming (Python for Everybody)"),
    "spd": ("coursepages/spd/README.md", "Core Programming — Systematic Program Design"),
    "spd-project": ("coursepages/spd/space-invaders-instructions.md", "Systematic Program Design — Space Invaders Final Project"),
    "class-based": ("coursepages/class-based/README.md", "Core Programming — Class-based Program Design"),
    "ostep": ("coursepages/ostep/README.md", "Core Systems — Operating Systems: Three Easy Pieces"),
    "ostep-reading": ("coursepages/ostep/Reading-order.md", "OSTEP — Recommended Reading & Project Order"),
    "ostep-xv6-1b": ("coursepages/ostep/Project-1B-initial-xv6.md", "OSTEP Lab — Project 1B Initial xv6"),
    "ostep-xv6-2a": ("coursepages/ostep/Project-2A-processes-shell.md", "OSTEP Lab — Project 2A Processes & Shell"),
    "ostep-xv6-lottery": ("coursepages/ostep/Scheduling-xv6-lottery.md", "OSTEP Lab — xv6 Lottery Scheduling"),
    "ostep-xv6-vm": ("coursepages/ostep/vm-xv6-intro.md", "OSTEP Lab — xv6 Virtual Memory"),
    "guidelines": ("CURRICULAR_GUIDELINES.md", "CS 2013 Curricular Guidelines Alignment"),
    "faq": ("FAQ.md", "OSSU Frequently Asked Questions"),
    "help": ("HELP.md", "Getting Help & Study Community"),
    "extras-courses": ("extras/courses.md", "Extra Recommended CS Courses"),
    "readings": ("extras/readings.md", "Classic Computer Science Books & Readings"),
    "puzzles": ("extras/puzzles-practice-plods.md", "Practice Problems, Coding Puzzles & Exercises"),
    "other-curricula": ("extras/other_curricula.md", "Related Open-Source Curricula"),
    "readme": ("README.md", "Full OSSU Computer Science Curriculum README"),
}

SHORTCUTS: dict[str, str] = {
    "start": "intro-cs",
    "dasar": "intro-cs",
    "mulai": "intro-cs",
    "beginner": "intro-programming",
    "pemula": "intro-programming",
    "py4e": "intro-programming",
    "python": "intro-cs",
    "oop": "class-based",
    "os": "ostep",
    "operating-systems": "ostep",
    "sistem-operasi": "ostep",
    "books": "readings",
    "buku": "readings",
    "latihan": "puzzles",
    "practice": "puzzles",
    "cs2013": "guidelines",
    "curriculum": "readme",
}

_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slug(text: str) -> str:
    return _SLUG_RE.sub("-", text.strip().lower()).strip("-")


def _strip_md(text: str) -> str:
    cleaned = _LINK_RE.sub(r"\1", text)
    cleaned = cleaned.replace("`", "").replace("**", "").replace("*", "")
    return " ".join(cleaned.split()).strip()


def _resolve_home(raw: Path | None) -> Path:
    return cs.checked(hp.resolve_hermes_home(raw))


def _is_safe_https(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and bool(parsed.netloc) and not parsed.username and not parsed.password


def _fetch_via_git(home: Path) -> Path:
    repo, pin = cs.PINNED[SOURCE_NAME]
    root = cs.folder(home, SOURCE_NAME)
    with tempfile.TemporaryDirectory(prefix="msshi-ossu-") as tmp:
        clone_dir = Path(tmp) / "repo"
        subprocess.run(
            [
                "git",
                "-c", "http.postBuffer=16m",
                "-c", "pack.windowMemory=32m",
                "-c", "pack.threads=1",
                "clone", "--bare", "--depth=1",
                f"https://github.com/{repo}.git",
                str(clone_dir),
            ],
            check=True,
            capture_output=True,
            timeout=120,
        )
        # If upstream moved past the reviewed pin, fetch the exact reviewed commit object.
        probe = subprocess.run(
            ["git", "-C", str(clone_dir), "cat-file", "-e", f"{pin}^{{commit}}"],
            capture_output=True,
            timeout=30,
        )
        if probe.returncode != 0:
            subprocess.run(
                [
                    "git", "-C", str(clone_dir),
                    "-c", "http.postBuffer=16m",
                    "-c", "pack.windowMemory=32m",
                    "-c", "pack.threads=1",
                    "fetch", "--depth=1", "origin", pin,
                ],
                check=True,
                capture_output=True,
                timeout=120,
            )
        ls = subprocess.run(
            ["git", "-C", str(clone_dir), "ls-tree", "-r", "-z", pin],
            check=True,
            capture_output=True,
            timeout=30,
        )
        rows = []
        for entry in ls.stdout.split(b"\x00"):
            if not entry:
                continue
            meta, path_b = entry.split(b"\t", 1)
            mode_b, typ_b, sha_b = meta.split(b" ", 2)
            row = {
                "mode": mode_b.decode("ascii"),
                "type": typ_b.decode("ascii"),
                "sha": sha_b.decode("ascii"),
                "path": path_b.decode("utf-8"),
            }
            if cs.selected_file(SOURCE_NAME, row):
                rows.append(row)
        required = ["README.md", "LICENSE", "CURRICULAR_GUIDELINES.md", "FAQ.md"]
        selected_paths = {row["path"] for row in rows}
        missing = [item for item in required if item not in selected_paths]
        if missing:
            raise ValueError("Pinned OSSU source is missing required files: " + ", ".join(missing))
        hashes: dict[str, str] = {}
        for row in rows:
            blob = subprocess.run(
                ["git", "-C", str(clone_dir), "cat-file", "blob", row["sha"]],
                check=True,
                capture_output=True,
                timeout=30,
            )
            data = blob.stdout
            if hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest() != row["sha"]:
                raise ValueError(f"Git blob SHA-1 mismatch for {row['path']}")
            target = cs.checked(root / cs.relative(row["path"]))
            cs.atomic(target, data)
            hashes[row["path"]] = hashlib.sha256(data).hexdigest()
        cs.atomic(
            root / "MSSHI_SNAPSHOT.json",
            cs.encode({
                "repository": repo,
                "commit": pin,
                "files": hashes,
                "dependencies_installed": False,
                "model_calls": 0,
                "auto_start": False,
            }),
        )
    if not cs.verify_cached(home, SOURCE_NAME):
        raise ValueError("OSSU cache verification failed after git fetch")
    return root


def fetch_curriculum(home: Path, *, refresh: bool = False) -> dict[str, Any]:
    root = cs.folder(home, SOURCE_NAME)
    if refresh and root.exists():
        shutil.rmtree(cs.checked(root))
    if not refresh and cs.verify_cached(home, SOURCE_NAME):
        return cs.status(home, SOURCE_NAME)
    try:
        cs.materialize(home, SOURCE_NAME)
    except (HTTPError, URLError, OSError, TimeoutError):
        _fetch_via_git(home)
    return cs.status(home, SOURCE_NAME)


def parse_curriculum(readme_text: str) -> dict[str, Any]:
    """Parse OSSU README.md into structured stages, tracks, and courses."""
    tracks: list[dict[str, Any]] = []
    courses: list[dict[str, Any]] = []
    current_stage = ""
    current_track: dict[str, Any] | None = None
    headers: list[str] = []
    in_table = False
    in_curriculum = False
    course_id = 0

    def ensure_track(stage_title: str, track_title: str) -> dict[str, Any]:
        slug = _slug(track_title)
        for existing in tracks:
            if existing["slug"] == slug:
                return existing
        item = {
            "stage": stage_title,
            "stage_slug": _slug(stage_title),
            "title": track_title,
            "slug": slug,
            "topics": [],
            "course_count": 0,
        }
        tracks.append(item)
        return item

    lines = readme_text.splitlines()
    for raw_line in lines:
        line = raw_line.strip()
        if line == "# Curriculum":
            in_curriculum = True
            continue
        if in_curriculum and line.startswith("# ") and line != "# Curriculum":
            break
        if not in_curriculum:
            continue

        if line.startswith("## "):
            title = line[3:].strip()
            in_table = False
            headers = []
            if title.lower() in {"congratulations", "prerequisites"}:
                current_stage = title
                current_track = None
                continue
            current_stage = title
            if title.lower() in {"intro cs", "final project"}:
                current_track = ensure_track(title, title)
            else:
                current_track = None
            continue

        if line.startswith("### "):
            title = line[4:].strip()
            in_table = False
            headers = []
            current_track = ensure_track(current_stage or "Core CS", title)
            continue

        if current_track is not None and not in_table and line.startswith("`") and line.endswith("`") and len(line) > 2:
            topic = line.strip("`").strip()
            if topic and topic.lower() != "and more":
                current_track["topics"].append(topic)
            continue

        if current_track is not None and "|" in line:
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if not in_table and cells and cells[0].lower().startswith("courses"):
                headers = [cell.lower() for cell in cells]
                in_table = True
                continue
            if in_table:
                if all(set(cell) <= {":", "-", " "} for cell in cells):
                    continue
                links = _LINK_RE.findall(cells[0]) if cells else []
                if not links:
                    in_table = False
                    continue
                primary_title, primary_url = links[0]
                alternatives = [{"label": lbl, "url": url} for lbl, url in links[1:]]
                col_map = {headers[i]: cells[i] for i in range(min(len(headers), len(cells)))}
                course_id += 1
                is_local = not primary_url.startswith(("http://", "https://"))
                record = {
                    "id": course_id,
                    "stage": current_track["stage"],
                    "stage_slug": current_track["stage_slug"],
                    "track": current_track["title"],
                    "track_slug": current_track["slug"],
                    "title": primary_title.strip(),
                    "primary_url": primary_url.strip(),
                    "is_local_coursepage": is_local,
                    "alternatives": alternatives,
                    "duration": _strip_md(col_map.get("duration", "-")) or "-",
                    "effort": _strip_md(col_map.get("effort", "-")) or "-",
                    "prerequisites": _strip_md(col_map.get("prerequisites", "-")) or "-",
                }
                courses.append(record)
                current_track["course_count"] += 1
            continue

        if in_table and not line:
            in_table = False

    return {
        "university": "Open Source Society University (OSSU) — Computer Science",
        "kind": "open-source-university-curriculum",
        "portal_url": PORTAL_URL,
        "repository_url": REPO_URL,
        "discord_url": DISCORD_URL,
        "total_tracks": len(tracks),
        "total_courses": len(courses),
        "tracks": tracks,
        "courses": courses,
    }


def _load_curriculum(home: Path) -> tuple[Path, dict[str, Any]]:
    cached = cs.verify_cached(home, SOURCE_NAME)
    if not cached:
        raise ValueError(
            "Cache lokal OSSU Computer Science belum tersedia. "
            "Jalankan: msshi ossu fetch --home " + str(home)
        )
    root = cs.folder(home, SOURCE_NAME)
    readme = cs.checked(root / "README.md").read_text(encoding="utf-8-sig")
    return root, parse_curriculum(readme)


def status_report(home: Path) -> dict[str, Any]:
    raw = cs.status(home, SOURCE_NAME)
    result: dict[str, Any] = {
        "name": SOURCE_NAME,
        "university": "Open Source Society University (OSSU) — Computer Science",
        "kind": "connected-open-university-curriculum",
        "is_bot_skill": False,
        "portal_url": PORTAL_URL,
        "repository_url": REPO_URL,
        "discord_url": DISCORD_URL,
        "commit": raw["commit"],
        "source_cached": raw["source_cached"],
        "source_files": raw["source_files"],
        "source_path": raw["source_path"],
        "auto_start": False,
        "auto_open_browser": False,
        "model_calls": 0,
        "quick_commands": [
            "msshi ossu roadmap",
            "msshi ossu courses intro-cs",
            "msshi ossu open start",
            "msshi ossu open portal --browser",
        ],
    }
    if raw["source_cached"]:
        _, parsed = _load_curriculum(home)
        result["total_tracks"] = parsed["total_tracks"]
        result["total_courses"] = parsed["total_courses"]
        result["stages"] = ["Prerequisites", "Intro CS", "Core CS", "Advanced CS", "Final project"]
    return result


def open_target(home: Path, target: str, *, launch_browser: bool = False) -> dict[str, Any]:
    key = target.strip().lower()
    if key in {"portal", "website", "web", "ossu", "home"}:
        if launch_browser and _is_safe_https(PORTAL_URL):
            webbrowser.open(PORTAL_URL)
        return {
            "kind": "portal",
            "title": "OSSU Computer Science Official Portal",
            "url": PORTAL_URL,
            "repository_url": REPO_URL,
            "browser_opened": bool(launch_browser),
        }
    if key in {"repo", "github"}:
        if launch_browser and _is_safe_https(REPO_URL):
            webbrowser.open(REPO_URL)
        return {
            "kind": "repository",
            "title": "OSSU Computer Science GitHub Repository",
            "url": REPO_URL,
            "browser_opened": bool(launch_browser),
        }

    root, parsed = _load_curriculum(home)
    guide_key = SHORTCUTS.get(key, key)
    if guide_key in GUIDE_ALIASES:
        rel_path, label = GUIDE_ALIASES[guide_key]
        file_path = cs.checked(root / cs.relative(rel_path))
        content = file_path.read_text(encoding="utf-8-sig")
        external_links = [
            {"label": lbl, "url": url}
            for lbl, url in _LINK_RE.findall(content)
            if _is_safe_https(url)
        ]
        github_view_url = f"{REPO_URL}/blob/{cs.PINNED[SOURCE_NAME][1]}/{rel_path}"
        if launch_browser:
            webbrowser.open(github_view_url)
        return {
            "kind": "coursepage_guide",
            "guide": guide_key,
            "title": label,
            "local_path": str(file_path),
            "github_url": github_view_url,
            "external_links": external_links[:12],
            "browser_opened": bool(launch_browser),
            "content": content,
        }

    matched = None
    if key.isdigit():
        cid = int(key)
        matched = next((row for row in parsed["courses"] if row["id"] == cid), None)
    if matched is None:
        matched = next(
            (
                row
                for row in parsed["courses"]
                if key in row["title"].lower()
                or key in row["track_slug"]
                or key in row["primary_url"].lower()
            ),
            None,
        )
    if matched is None:
        raise ValueError(
            f"Target OSSU '{target}' tidak ditemukan. "
            "Coba: msshi ossu roadmap, msshi ossu courses, msshi ossu guides, atau msshi ossu open start"
        )

    coursepage_content = ""
    local_coursepage_path = ""
    open_url = matched["primary_url"]
    if matched["is_local_coursepage"]:
        cp_file = cs.checked(root / cs.relative(matched["primary_url"]))
        if cp_file.is_file():
            local_coursepage_path = str(cp_file)
            coursepage_content = cp_file.read_text(encoding="utf-8-sig")
        open_url = f"{REPO_URL}/blob/{cs.PINNED[SOURCE_NAME][1]}/{matched['primary_url']}"
    if launch_browser and _is_safe_https(open_url):
        webbrowser.open(open_url)
    return {
        "kind": "course",
        "course": matched,
        "url": open_url,
        "local_coursepage_path": local_coursepage_path,
        "coursepage_content": coursepage_content,
        "browser_opened": bool(launch_browser),
    }


def _print_roadmap(parsed: dict[str, Any]) -> None:
    print(f"=== {parsed['university']} ===")
    print(f"Portal Resmi  : {parsed['portal_url']}")
    print(f"Repositori    : {parsed['repository_url']}")
    print(f"Total Materi  : {parsed['total_tracks']} jalur, {parsed['total_courses']} mata kuliah (setara S1 Computer Science, gratis/open-source)")
    print("Prasyarat     : Matematika SMA (Aljabar, Geometri, Pra-kalkulus) -> https://ossu.dev/precollege-math")
    print()
    last_stage = ""
    for track in parsed["tracks"]:
        if track["stage"] != last_stage:
            last_stage = track["stage"]
            print(f"[{last_stage}]")
        topics = ", ".join(track["topics"][:5])
        suffix = f" — topik: {topics}" if topics else ""
        print(f"  - {track['slug']:<30} ({track['course_count']:>2} mata kuliah){suffix}")
    print()
    print("Mulai belajar dari dasar:")
    print("  msshi ossu open pemula        # Belum pernah coding (Python for Everybody)")
    print("  msshi ossu open start         # Intro CS (MITx 6.00.1x Python)")
    print("  msshi ossu courses core-math  # Lihat daftar mata kuliah & link resmi per jalur")
    print("  msshi ossu open <nomor/topik> # Buka detail & panduan mata kuliah")


def _print_courses(courses: list[dict[str, Any]], heading: str) -> None:
    print(f"=== OSSU Computer Science — {heading} ({len(courses)} mata kuliah) ===")
    for row in courses:
        print(f"[{row['id']:>2}] {row['title']} ({row['track']})")
        print(f"     Durasi: {row['duration']} | Beban: {row['effort']} | Prasyarat: {row['prerequisites']}")
        print(f"     Link  : {row['primary_url']}")
        for alt in row["alternatives"]:
            print(f"     Alt   : {alt['label']} -> {alt['url']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="msshi ossu", description=__doc__)
    sub = parser.add_subparsers(dest="action")

    for name, help_text in (
        ("status", "Cek koneksi OSSU Open-Source CS University & status cache lokal."),
        ("fetch", "Tarik & verifikasi cache lokal kurikulum OSSU CS terpin (MIT)."),
        ("roadmap", "Tampilkan peta kurikulum lengkap S1 Computer Science OSSU."),
        ("guides", "Daftar panduan & halaman mata kuliah lokal OSSU yang bisa langsung dibuka."),
    ):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--home", type=Path, help="Folder Hermes home.")
        p.add_argument("--json", action="store_true", help="Keluaran JSON.")
        if name == "fetch":
            p.add_argument("--refresh", action="store_true", help="Tarik ulang cache OSSU dari commit terpin saat ini setelah pin dinaikkan.")

    p_courses = sub.add_parser("courses", help="Lihat daftar mata kuliah OSSU per jalur atau cari berdasarkan kata kunci.")
    p_courses.add_argument("track", nargs="?", default="", help="Filter jalur/tahap (mis. intro-cs, core-programming, core-math, core-systems, advanced).")
    p_courses.add_argument("--search", "-s", default="", help="Cari kata kunci di judul/jalur/prasyarat mata kuliah.")
    p_courses.add_argument("--home", type=Path, help="Folder Hermes home.")
    p_courses.add_argument("--json", action="store_true", help="Keluaran JSON.")

    p_open = sub.add_parser("open", help="Buka langsung materi/coursepage dasar OSSU atau detail & link mata kuliah.")
    p_open.add_argument("target", nargs="?", default="start", help="Nama panduan (start/pemula/ostep/readings/portal/repo), nomor mata kuliah, atau kata kunci.")
    p_open.add_argument("--browser", action="store_true", help="Buka tautan https resmi di browser pengguna (hanya saat diminta eksplisit).")
    p_open.add_argument("--home", type=Path, help="Folder Hermes home.")
    p_open.add_argument("--json", action="store_true", help="Keluaran JSON.")

    args = parser.parse_args(argv)
    action = args.action or "status"
    try:
        home = _resolve_home(getattr(args, "home", None))
        as_json = bool(getattr(args, "json", False))

        if action == "status":
            data = status_report(home)
            if as_json:
                print(json.dumps(data, ensure_ascii=False, indent=2))
            else:
                print(f"=== {data['university']} ===")
                print(f"Jenis         : Universitas Computer Science Open-Source terhubung (bukan skill bot)")
                print(f"Portal Resmi  : {data['portal_url']}")
                print(f"Repositori    : {data['repository_url']} @ {data['commit'][:8]}")
                print(f"Cache Lokal   : {'SIAP' if data['source_cached'] else 'BELUM'} ({data['source_files']} file terverifikasi)")
                if data.get("total_courses"):
                    print(f"Kurikulum     : {data['total_tracks']} jalur, {data['total_courses']} mata kuliah (Intro CS -> Core CS -> Advanced CS -> Final Project)")
                print("Perintah cepat: msshi ossu roadmap | msshi ossu courses intro-cs | msshi ossu open start")
            return 0

        if action == "fetch":
            data = fetch_curriculum(home, refresh=bool(getattr(args, "refresh", False)))
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return 0

        if action == "roadmap":
            _, parsed = _load_curriculum(home)
            if as_json:
                print(json.dumps({k: v for k, v in parsed.items() if k != "courses"}, ensure_ascii=False, indent=2))
            else:
                _print_roadmap(parsed)
            return 0

        if action == "guides":
            root, _ = _load_curriculum(home)
            rows = [
                {"id": k, "title": title, "path": str(root / cs.relative(rel)), "exists": (root / cs.relative(rel)).is_file()}
                for k, (rel, title) in GUIDE_ALIASES.items()
            ]
            if as_json:
                print(json.dumps({"guides": rows, "shortcuts": SHORTCUTS}, ensure_ascii=False, indent=2))
            else:
                print("=== Panduan & Coursepage OSSU Computer Science ===")
                for row in rows:
                    print(f"  {row['id']:<20} — {row['title']}")
                print("\nBuka langsung: msshi ossu open <id>  (contoh: msshi ossu open start | msshi ossu open pemula | msshi ossu open ostep)")
            return 0

        if action == "courses":
            _, parsed = _load_curriculum(home)
            rows = list(parsed["courses"])
            track_q = _slug(args.track) if args.track else ""
            if track_q:
                rows = [r for r in rows if track_q in r["track_slug"] or track_q in r["stage_slug"]]
            if args.search.strip():
                terms = args.search.casefold().split()
                rows = [
                    r for r in rows
                    if all(t in f"{r['title']} {r['track']} {r['stage']} {r['prerequisites']} {r['primary_url']}".casefold() for t in terms)
                ]
            if as_json:
                print(json.dumps({"filter": args.track, "search": args.search, "count": len(rows), "courses": rows}, ensure_ascii=False, indent=2))
            else:
                heading = args.track or (f"Pencarian '{args.search}'" if args.search else "Semua Mata Kuliah")
                _print_courses(rows, heading)
            return 0

        if action == "open":
            data = open_target(home, args.target, launch_browser=bool(args.browser))
            if as_json:
                print(json.dumps(data, ensure_ascii=False, indent=2))
            elif data["kind"] in {"portal", "repository"}:
                print(f"{data['title']}: {data['url']}")
                if data["browser_opened"]:
                    print("Dibuka di browser pengguna.")
            elif data["kind"] == "coursepage_guide":
                print(f"=== {data['title']} ===")
                print(f"Sumber Lokal : {data['local_path']}")
                print(f"GitHub Resmi : {data['github_url']}")
                print()
                print(data["content"])
            else:
                c = data["course"]
                print(f"=== [{c['id']}] {c['title']} ===")
                print(f"Tahap / Jalur : {c['stage']} / {c['track']}")
                print(f"Durasi / Beban: {c['duration']} | {c['effort']}")
                print(f"Prasyarat     : {c['prerequisites']}")
                print(f"Tautan Resmi  : {data['url']}")
                for alt in c["alternatives"]:
                    print(f"Alternatif    : {alt['label']} -> {alt['url']}")
                if data["coursepage_content"]:
                    print("\n--- Panduan Resmi OSSU ---")
                    print(data["coursepage_content"])
            return 0

        parser.print_help()
        return 0
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"msshi ossu: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
