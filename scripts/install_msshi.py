#!/usr/bin/env python3
"""Plan or copy bundled MSSHI skills and export editable team workspaces."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "configs" / "bot_role_and_skill_matrix.json"
TITLE = "MSSHI — Mega Semar Sang Hyang Ismaya: Sovereign Sage"
HOSTS = ("hermes", "openclaw", "claude", "codex", "antigravity")
MUZA_TEAM = ("yukino", "shizuka", "val", "kiki-chii", "shikaku")
UNIVERSAL_BRIDGE = "cli-anything-universal-bridge"
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
WINDOWS_RESERVED = {
    "con", "prn", "aux", "nul",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
}
SKILL_NAME = re.compile(r"(?m)^name:[ \t]*['\"]?([a-z0-9-]+)['\"]?[ \t]*$")


def safe_slug(value, label):
    if not isinstance(value, str) or not SLUG.fullmatch(value) or value in WINDOWS_RESERVED:
        raise ValueError(f"ID {label} tidak valid: {value!r}")
    return value


def is_link(path):
    """Reject symlinks and Windows reparse points, including junctions."""
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    )


def existing(path):
    return os.path.lexists(path)


def reject_links(path):
    for part in (*reversed(path.parents), path):
        if existing(part) and is_link(part):
            raise ValueError(f"Path lewat symlink/junction: {part}")


def absolute(path):
    return Path(os.path.abspath(os.path.expanduser(os.fspath(path))))


def local_file(value, suffix, root=ROOT):
    if not isinstance(value, str) or "\\" in value or ":" in value:
        raise ValueError(f"Path relatif paket tidak valid: {value!r}")
    path = Path(value)
    if path.is_absolute() or not path.parts or ".." in path.parts or path.suffix.lower() != suffix:
        raise ValueError(f"Path relatif paket tidak valid: {value!r}")
    source = root / path
    reject_links(source)
    if not source.is_file():
        raise ValueError(f"File paket tidak ditemukan: {value}")
    return source


def validate_tree(source):
    for folder, dirs, files in os.walk(source, followlinks=False):
        for name in (*dirs, *files):
            child = Path(folder) / name
            if is_link(child) or not (child.is_dir() or child.is_file()):
                raise ValueError(f"Item paket bukan file/folder biasa: {child}")


def read_json(path):
    with path.open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def names(values, label):
    if not isinstance(values, list):
        raise ValueError(f"{label} harus berupa array.")
    return list(dict.fromkeys(safe_slug(value, label) for value in values))


def read_matrix(path, root=ROOT):
    data = read_json(path)
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("Matriks harus memakai schema_version 1.")
    catalog = {}
    for entry in data["skills"]:
        slug = safe_slug(entry["slug"], "skill")
        if slug in catalog or entry["status"] not in {"bundled", "external"}:
            raise ValueError(f"Skill duplikat atau status tidak dikenal: {slug}")
        catalog[slug] = None
        if entry["status"] == "bundled":
            source = local_file(entry["path"], ".md", root)
            if source.name != "SKILL.md" or source.parent.name != slug or source.parent.parent != root / "skills":
                raise ValueError(f"Skill {slug} harus berada di skills/{slug}/SKILL.md.")
            catalog[slug] = source.parent
    bridge = f"skills/{UNIVERSAL_BRIDGE}/SKILL.md"
    if catalog.get(UNIVERSAL_BRIDGE) is None and (root / bridge).is_file():
        # Old custom matrices can omit the bridge introduced in v2.1.
        catalog[UNIVERSAL_BRIDGE] = local_file(bridge, ".md", root).parent
    packs = {}
    for pack, slugs in data["packs"].items():
        pack = safe_slug(pack, "paket")
        packs[pack] = names(slugs, pack)
        if missing := set(packs[pack]) - catalog.keys():
            raise ValueError(f"Skill tidak dikenal dalam paket {pack}: {', '.join(sorted(missing))}")
    return data, catalog, packs


def host_roots(home):
    choices = []
    if value := os.environ.get("HERMES_HOME"):
        choices.append(absolute(value))
    for candidate in (home / ".hermes", home / "HermesData"):
        if candidate.is_dir():
            choices.append(candidate)
    if os.name == "nt":
        # A custom Windows path only counts if it actually looks like Hermes.
        candidate = Path("D:/HermesData")
        if (candidate / "skills").is_dir() or (candidate / "config.yaml").is_file():
            choices.append(candidate)
    openclaw = absolute(os.environ["OPENCLAW_STATE_DIR"]) if os.environ.get("OPENCLAW_STATE_DIR") else home / ".openclaw"
    claude = absolute(os.environ["CLAUDE_CONFIG_DIR"]) if os.environ.get("CLAUDE_CONFIG_DIR") else home / ".claude"
    return {
        "hermes": [path / "skills" for path in choices] or [home / ".hermes" / "skills"],
        "openclaw": [openclaw / "skills"],
        "claude": [claude / "skills"],
        "codex": [home / ".agents" / "skills"],
        "antigravity": [home / ".gemini" / "config" / "skills"],
    }


def detect_host(requested):
    home = Path.home()
    roots = host_roots(home)
    explicit_roots = {
        "hermes": "HERMES_HOME",
        "openclaw": "OPENCLAW_STATE_DIR",
        "claude": "CLAUDE_CONFIG_DIR",
    }
    if requested != "auto":
        return requested, roots[requested][0] if requested in roots else None
    for host in HOSTS:
        for target in roots[host]:
            if os.environ.get(explicit_roots.get(host, "")) or target.is_dir() or target.parent.is_dir() or (
                host == "antigravity" and (home / ".gemini").is_dir()
            ):
                return host, target
    return "manual", None


def indexed_skills(root):
    """Treat an existing nested or flat skill as occupied by its name."""
    occupied = set()
    if not root.is_dir():
        return occupied
    for folder, dirs, files in os.walk(root, followlinks=False):
        base = Path(folder)
        dirs[:] = [
            name for name in dirs
            if not name.startswith((".msshi-backup-", ".msshi-stage-")) and not is_link(base / name)
        ]
        skill = base / "SKILL.md"
        if "SKILL.md" not in files or is_link(skill):
            continue
        occupied.add(base.name.lower())
        with skill.open(encoding="utf-8-sig", errors="replace") as handle:
            if handle.readline().strip() == "---":
                lines = []
                for line in handle:
                    if line.strip() == "---" or len(lines) == 100:
                        break
                    lines.append(line)
                if name := SKILL_NAME.search("".join(lines)):
                    occupied.add(name.group(1))
        dirs.clear()
    return occupied


def skill_plan(root, selected, catalog):
    reject_links(root)
    if existing(root) and not root.is_dir():
        raise ValueError(f"Target skill bukan folder: {root}")
    occupied = indexed_skills(root)
    copies, preserved, external = [], [], []
    for slug in dict.fromkeys(selected):
        source = catalog[slug]
        destination = root / slug
        if source is None:
            external.append(slug)
        elif slug in occupied or existing(destination):
            preserved.append(slug)
        else:
            if source in destination.parents or destination in source.parents:
                raise ValueError(f"Sumber dan target skill tumpang tindih: {destination}")
            validate_tree(source)
            copies.append((source, destination))
    return copies, preserved, external


def mandatory_skills(catalog):
    return (UNIVERSAL_BRIDGE,) if catalog.get(UNIVERSAL_BRIDGE) is not None else ()


def include_mandatory(values, catalog):
    return list(dict.fromkeys((*values, *mandatory_skills(catalog))))


def team_plan(data, mode, catalog):
    bots = {}
    for bot in data["bots"]:
        bot_id = safe_slug(bot["id"], "bot")
        if bot_id in bots:
            raise ValueError(f"ID bot duplikat: {bot_id}")
        label = bot.get("label", bot_id)
        if not isinstance(label, str) or not label.strip() or "\n" in label or "\r" in label:
            raise ValueError(f"Label bot tidak valid: {bot_id}")
        skills = include_mandatory(
            names(bot["required_skills"], "required_skills") + names(bot["optional_skills"], "optional_skills"),
            catalog,
        )
        if unknown := set(skills) - catalog.keys():
            raise ValueError(f"Skill tidak dikenal untuk {bot_id}: {', '.join(sorted(unknown))}")
        if mode == "custom-bots" and "persona_text" in bot:
            persona = bot["persona_text"]
            if not isinstance(persona, str) or not persona.strip():
                raise ValueError(f"Persona kosong: {bot_id}")
        else:
            persona = local_file(bot["persona_file"], ".md").read_text(encoding="utf-8-sig")
        bots[bot_id] = (label, skills, persona)
    order = MUZA_TEAM if mode == "muza-preset" else bots
    if missing := set(order) - bots.keys():
        raise ValueError(f"Bot preset belum lengkap: {', '.join(sorted(missing))}")
    if not order:
        raise ValueError("Matriks custom harus berisi minimal satu bot.")
    return [(bot_id, *bots[bot_id]) for bot_id in order]


def resolve_skills(values, catalog, aliases):
    selected = list(dict.fromkeys(aliases.get(value, value) for value in values))
    if missing := set(selected) - catalog.keys():
        raise ValueError(f"Skill tidak dikenal: {', '.join(sorted(missing))}")
    return selected


def selected_skills(args, catalog, packs, aliases):
    if args.mode == "solo":
        return list(catalog)
    if args.skills:
        return include_mandatory(resolve_skills(args.skills, catalog, aliases), catalog)
    picks = [pack.strip() for item in (args.packs or []) for pack in item.split(",") if pack.strip()]
    if not picks:
        raise ValueError("Mode selective perlu --skills atau --packs, misalnya --packs core,filmmaking.")
    if picks == ["all"]:
        picks = list(packs)
    if unknown := set(picks) - packs.keys():
        raise ValueError(f"Paket tidak dikenal: {', '.join(sorted(unknown))}. Pilihan: {', '.join(packs)}.")
    return include_mandatory((slug for pack in picks for slug in packs[pack]), catalog)


def copy_skill(source, destination):
    reject_links(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".msshi-stage-", dir=destination.parent.parent) as work:
        candidate = Path(work) / destination.name
        shutil.copytree(source, candidate, symlinks=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        validate_tree(candidate)
        if existing(destination):
            raise FileExistsError(f"Skill muncul saat persiapan: {destination}")
        candidate.rename(destination)


def create_text(path, content):
    reject_links(path.parent)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
    except FileExistsError:
        print(f"  Pertahankan file yang sudah ada: {path}")


def print_plan(copies, preserved, external):
    for source, destination in copies:
        print(f"  Salin {source.name} -> {destination}")
    if preserved:
        print(f"  Pertahankan yang sudah ada: {', '.join(preserved)}")
    if external:
        print(f"  Integrasi eksternal perlu dipasang terpisah: {', '.join(external)}")


def main(argv=None):
    from msshi_sources import data_root, fetch_upstreams, upstream_entries

    parser = argparse.ArgumentParser(description=TITLE + " — M.S.S.H.I. (Multi-Agent Sovereign Sage & Hermes Intelligence)")
    parser.add_argument("--mode", choices=("solo", "custom-bots", "selective", "muza-preset"), default="solo")
    parser.add_argument("--platform", choices=("auto", *HOSTS, "chatgpt", "manual"), default="auto")
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--packs", nargs="+", metavar="PAKET", help="Daftar paket selective, dipisah koma atau spasi.")
    selection.add_argument("--skills", nargs="+", metavar="SKILL", help="Daftar slug skill selective, dipisah spasi.")
    parser.add_argument("--matrix", type=Path, default=MATRIX, help="Matriks kustom. Path aset di dalam JSON relatif ke repo.")
    parser.add_argument("--target-dir", type=Path, help="Folder skill (solo/selective) atau induk workspace bot (mode tim).")
    parser.add_argument("--pull-upstreams", action="store_true", help="Ambil sumber eksternal ke cache terpisah saat --apply.")
    parser.add_argument("--upstreams-dir", type=Path, default=data_root() / "upstreams", help="Folder cache sumber eksternal.")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--dry-run", action="store_true", help="Tampilkan rencana saja (default).")
    action.add_argument("--apply", action="store_true", help="Tulis hanya file baru sesuai rencana.")
    args = parser.parse_args(argv)
    if (args.packs or args.skills) and args.mode != "selective":
        parser.error("--packs dan --skills hanya untuk --mode selective.")
    try:
        data, catalog, packs = read_matrix(args.matrix.expanduser())
        host, detected = detect_host(args.platform)
        is_team = args.mode in {"custom-bots", "muza-preset"}
        if args.target_dir:
            target = absolute(args.target_dir)
        elif is_team:
            target = Path.cwd() / "msshi-agents"
        else:
            target = detected or Path.cwd() / "msshi-skills"
        reject_links(target)
        if existing(target) and not target.is_dir():
            raise ValueError(f"Target bukan folder: {target}")
        print(f"{TITLE}\nMode: {args.mode} | Platform: {host} | Target: {target}")
        if not args.apply:
            print("Simulasi. Tambahkan --apply setelah meninjau rencana.")
        if args.pull_upstreams:
            manifest = ROOT / "configs" / "upstreams.json"
            print(f"Sumber eksternal: {len(upstream_entries(manifest))} entri -> {absolute(args.upstreams_dir)}")
        if is_team:
            plans = []
            for bot_id, label, skills, soul in team_plan(data, args.mode, catalog):
                bot_dir = target / bot_id
                reject_links(bot_dir)
                if existing(bot_dir) and not bot_dir.is_dir():
                    raise ValueError(f"Target bot bukan folder: {bot_dir}")
                copies, preserved, external = skill_plan(bot_dir / "skills", skills, catalog)
                print(f"\n{label} ({bot_id})")
                print_plan(copies, preserved, external)
                for filename in ("SOUL.md", "AGENTS.md"):
                    if existing(bot_dir / filename):
                        print(f"  Pertahankan {bot_dir / filename}")
                    else:
                        print(f"  Buat {bot_dir / filename}")
                plans.append((bot_dir, label, soul, copies, skills, external))
            if args.apply:
                for bot_dir, label, soul, copies, skills, external in plans:
                    for source, destination in copies:
                        copy_skill(source, destination)
                    local_skills = ", ".join(slug for slug in dict.fromkeys(skills) if catalog[slug])
                    create_text(bot_dir / "SOUL.md", soul)
                    create_text(
                        bot_dir / "AGENTS.md",
                        f"# {label}\n\nBaca SOUL.md untuk persona dan batas peran.\n\n"
                        f"Skill paket untuk bot ini: {local_skills or '—'}.\n\n"
                        f"Integrasi eksternal yang perlu disiapkan: {', '.join(external) or '—'}.\n",
                    )
            print("Workspace tim portabel. Daftarkan tiap bot di platform Anda bila diperlukan.")
        else:
            copies, preserved, external = skill_plan(
                target, selected_skills(args, catalog, packs, data.get("aliases", {})), catalog,
            )
            print_plan(copies, preserved, external)
            if args.apply:
                for source, destination in copies:
                    copy_skill(source, destination)
            if host == "chatgpt":
                print("Gunakan panduan docs/platforms.md untuk menambahkan instruksi dan referensi ke ChatGPT.")
        print("Selesai menyiapkan file." if args.apply else "Tidak ada file yang ditulis.")
        if args.pull_upstreams and args.apply:
            rows = fetch_upstreams(manifest, args.upstreams_dir)
            if any(row["status"] == "failed" for row in rows.values()):
                return 1
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        parser.exit(2, f"Kesalahan: {exc}\n")
    return 0


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    raise SystemExit(main())

