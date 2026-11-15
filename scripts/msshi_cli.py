"""Interactive setup and guarded updates for the public MSSHI package."""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager, redirect_stdout
from datetime import datetime, timezone
import hashlib
import io
from types import SimpleNamespace
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory, mkdtemp
from urllib.error import HTTPError

sys.dont_write_bytecode = True

import install_msshi as installer
import msshi_hermes_profiles as hermes_profiles
import setup_cli_anything_hermes as connections
import msshi_choices as choice_help
from msshi_sources import RAW, REPOSITORY, clone, data_root, download, fetch_upstreams, write_json
from msshi_update import inventory, release_version, update_skill


ROOT = Path(__file__).resolve().parents[1]
MATRIX = Path("configs", "bot_role_and_skill_matrix.json")
UPSTREAMS = Path("configs", "upstreams.json")
STATE_FILE = "state.json"
RELEASE_ID = re.compile(r"(?:[0-9a-f]{24}|[0-9a-f]{64})")
SEMVER = re.compile(r"(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?")
PLATFORMS = (*installer.HOSTS, "manual")
MODES = ("solo", "custom-bots", "selective", "muza-preset")
RELEASE_DIRS = ("scripts", "configs", "skills", "docs", "portable", "assets", "adapters",
                "business-sage", ".claude-plugin", "hermes_plugins", "optional", "notebooks")
RELEASE_FILES = ("VERSION.json", "CHANGELOG.md", "README.md", "README_EN.md",
                 "LICENSE", "SKILL.md", "install.ps1", "install.sh", "package.json",
                 "THIRD_PARTY_NOTICES.md", "CREDITS.md", "UPDATE_OTOMATIS_KE_V3.bat",
                 "MULAI_DI_SINI_PEMULA.bat", "MULAI_SKRIPSI_DRAG_AND_DROP.bat")


@contextmanager
def locked(root):
    installer.reject_links(root)
    root.mkdir(parents=True, exist_ok=True)
    lock = root / ".msshi-update-lock"
    try:
        lock.mkdir()
    except FileExistsError as error:
        raise ValueError(f"Operasi MSSHI lain sedang berjalan atau lock masih ada: {lock}") from error
    try:
        yield
    finally:
        lock.rmdir()


def read_state(root):
    path = root / STATE_FILE
    installer.reject_links(path)
    state = installer.read_json(path) if path.exists() else {"schema_version": 1, "targets": {}}
    if (not isinstance(state, dict) or state.get("schema_version") != 1
            or not isinstance(state.get("targets"), dict)
            or any(not isinstance(skills, dict) for skills in state["targets"].values())):
        raise ValueError(f"Format state MSSHI tidak didukung: {path}")
    return state


def fingerprint(files):
    contents = json.dumps(files, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(contents).hexdigest()


def version_key(value):
    # The unpublished candidate used a temporary number above the public v2.1 release.
    ordered = "2.1.0-stage2-preview" if value == "2.2.0-stage2" else value
    match = SEMVER.fullmatch(ordered)
    if not match:
        raise ValueError(f"Versi MSSHI tidak dikenal: {value}")
    major, minor, patch, prerelease = match.groups()
    parts = []
    for identifier in (prerelease or "").split("."):
        for part in re.findall(r"\d+|\D+", identifier):
            parts.append((0, int(part)) if part.isdigit() else (1, part))
    return int(major), int(minor), int(patch), prerelease is None, tuple(parts)


def check_release():
    current = release_version(ROOT)
    latest = json.loads(download(f"{RAW}/VERSION.json").decode("utf-8-sig"))["version"]
    installed, available = version_key(current), version_key(latest)
    print(f"Versi lokal: {current}\nVersi GitHub main: {latest}")
    if installed < available:
        print("Pembaruan tersedia. Jalankan msshi update atau msshi select.")
    elif installed > available:
        print("Versi lokal lebih baru dari main GitHub.")
    else:
        print("Versi lokal sama dengan main GitHub.")
    try:
        print("\n" + download(f"{RAW}/CHANGELOG.md").decode("utf-8-sig").strip())
    except HTTPError as error:
        if error.code != 404:
            raise
        print("CHANGELOG.md belum tersedia di main GitHub.")


def connection_summary(args, home):
    try:
        report = connections.status(default_state_dir=home, hermes_home=args.hermes_home,
                                    profile=args.profile, state_dir=args.state_dir)
    except (OSError, ValueError) as error:
        print(f"Status CLI-Anything tidak tersedia. Periksa dengan msshi connect --status. {error}")
        return
    counts = Counter(row["readiness"] for row in report["connections"])
    detail = ", ".join(f"{label}: {count}" for label, count in sorted(counts.items()))
    suffix = f" ({detail})" if detail else ""
    print(f"CLI-Anything: {sum(counts.values())} koneksi terdaftar{suffix}. auto_open_on_boot: false")
    for warning in report.get("warnings", []):
        print(f"  {warning}")
    print("Detail per aplikasi: msshi connect --status")


def validate_release(source, current):
    incoming = release_version(source)
    if version_key(incoming) < version_key(current):
        raise ValueError(f"GitHub main masih {incoming}. Versi lokal {current} dipertahankan.")
    if not (source / "scripts" / "msshi_cli.py").is_file():
        raise ValueError("GitHub main belum berisi CLI Tahap 2.")
    data, catalog, packs = installer.read_matrix(source / MATRIX, source)
    if sum(path is not None for path in catalog.values()) != installer.read_json(source / "VERSION.json")["bundled_skills"]:
        raise ValueError("Jumlah skill di VERSION.json dan matriks berbeda.")
    return data, catalog, packs


def stage_release(source, home):
    """Publish a separate, verified release directory and keep old baselines."""
    releases = home / "releases"
    installer.reject_links(releases)
    releases.mkdir(exist_ok=True)
    with TemporaryDirectory(prefix=".msshi-stage-", dir=releases) as scratch:
        staging = Path(scratch) / "release"
        staging.mkdir()
        for name in RELEASE_DIRS:
            directory = source / name
            installer.reject_links(directory)
            if directory.is_dir():
                installer.validate_tree(directory)
                shutil.copytree(directory, staging / name, symlinks=True,
                                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for name in RELEASE_FILES:
            path = source / name
            installer.reject_links(path)
            if path.is_file():
                shutil.copy2(path, staging / name)
        files = inventory(staging)
        # The shorter key leaves room for deeply nested Windows skill paths.
        release_id = fingerprint(files)[:24]
        destination = releases / release_id
        installer.reject_links(destination)
        if destination.exists():
            if inventory(destination) != files:
                raise ValueError(f"Salinan rilis lokal berubah: {destination}")
        else:
            staging.rename(destination)
    return release_id


def remote_release(scratch):
    source = scratch / "repo"
    print("Mengambil MSSHI dari GitHub main...", flush=True)
    commit = clone(REPOSITORY, source, branch="main")
    return source, commit


def protected_backup(home, targets):
    paths = set()
    for target in targets:
        target = Path(target)
        paths.update({
            target / "SOUL.md", target / "user_creative_dna.json",
            target.parent / "SOUL.md", target.parent / "user_creative_dna.json",
            target.parent / "configs" / "user_creative_dna.json",
            target.parent.parent / "user_creative_dna.json",
            target.parent.parent / "configs" / "user_creative_dna.json",
        })
    sources = []
    for path in sorted(paths):
        installer.reject_links(path)
        if path.is_file():
            sources.append(path)
    if not sources:
        return
    root = home / "backups"
    installer.reject_links(root)
    root.mkdir(exist_ok=True)
    backup = Path(mkdtemp(prefix="protected-", dir=root))
    records = []
    for index, path in enumerate(sources, 1):
        saved = backup / f"{index:03d}-{path.name}"
        shutil.copy2(path, saved)
        records.append({"original": str(path), "backup": saved.name})
    write_json(backup / "files.json", records)
    print(f"Cadangan SOUL.md / DNA kreatif: {backup}")


def ensure_target(target, home, source):
    installer.reject_links(target)
    if (target.is_relative_to(home) or home.is_relative_to(target)
            or source.is_relative_to(target)
            or any(target.is_relative_to(source / name) for name in RELEASE_DIRS)):
        raise ValueError(f"Target skill harus terpisah dari repositori dan data MSSHI: {target}")


def update_target(target, choices, catalog, managed, *, apply, install_missing=()):
    installer.reject_links(target)
    occupied = installer.indexed_skills(target)
    plan = []
    for name in sorted(set(choices)):
        incoming = catalog.get(name)
        folder = target / name
        installer.reject_links(folder)
        if incoming is None:
            print(f"  {name}: tidak ada di bundel terbaru; salinan lokal dipertahankan.")
            continue
        source_files = inventory(incoming)
        if not installer.existing(folder):
            if name in install_missing and name not in occupied:
                print(f"  {name}: pasang.")
                plan.append((incoming, folder, source_files, None))
            else:
                print(f"  {name}: tidak ditemukan di target; dilewati.")
        elif not folder.is_dir() or not (folder / "SKILL.md").is_file():
            print(f"  {name}: folder sudah ditempati; dipertahankan.")
        elif (target_files := inventory(folder)) == source_files:
            if apply:
                managed[name] = fingerprint(source_files)
        elif managed.get(name) == fingerprint(target_files):
            print(f"  {name}: perbarui.")
            plan.append((incoming, folder, source_files, target_files))
        else:
            print(f"  {name}: kustom atau di luar kelolaan MSSHI; dipertahankan.")
    if not apply or not plan:
        return
    backup = None
    for incoming, folder, source_files, target_files in plan:
        if target_files is None:
            installer.copy_skill(incoming, folder)
        else:
            if backup is None:
                backup = Path(mkdtemp(prefix=".msshi-backup-", dir=target.parent))
                print(f"Cadangan skill: {backup}")
            update_skill(incoming, folder, backup, source_files, target_files)
        managed[folder.name] = fingerprint(source_files)


def choose_targets(home, platform=None, target_dir=None, team=False, lang='id', yes=False):
    if not platform:
        detected, _ = installer.detect_host("auto")
        if yes:
            platform = detected
        else:
            for name in PLATFORMS:
                print(f"  {name}: {choice_help.describe('platforms', name, lang=lang)}")
            platform = (input(f"Platform [{'/'.join(PLATFORMS)}] ({detected}): ").strip()
                        or detected)
    if platform not in PLATFORMS:
        raise ValueError(f"Platform tidak dikenal: {platform}")
    print(f"{platform}: {choice_help.describe('platforms', platform, lang=lang)}")
    _, detected = installer.detect_host(platform)
    if team and platform == "hermes":
        default = hermes_profiles.resolve_hermes_home() / "profiles"
    elif team:
        default = Path.cwd() / "msshi-agents"
    else:
        default = detected or Path.cwd() / "msshi-skills"
    if not target_dir:
        if yes:
            target_dir = default
        else:
            kind = "profil Hermes" if (team and platform == "hermes") else ("workspace tim" if team else "skills")
            target_dir = input(f"Folder {kind} [{default}]: ").strip() or default
    target = installer.absolute(target_dir)
    ensure_target(target, home, ROOT)
    return platform, target


def checklist(items, label, descriptions=None):
    for index, item in enumerate(items, 1):
        detail = (descriptions or {}).get(item, '')
        print(f"  [ ] {index:2d}. {item}" + (f" - {detail}" if detail else ''))
    value = input(f"Pilih {label} (angka/nama, pisahkan koma, atau all): ").strip().lower()
    if value == "all":
        return list(items)
    if not value:
        raise ValueError("Belum ada pilihan.")
    picked = []
    for raw in value.split(","):
        item = raw.strip()
        if item.isdecimal():
            index = int(item) - 1
            if not 0 <= index < len(items):
                raise ValueError(f"Nomor pilihan tidak ada: {item}")
            item = items[index]
        if item not in items:
            raise ValueError(f"Pilihan tidak ada: {item}")
        picked.append(item)
    return list(dict.fromkeys(picked))


def custom_matrix(data, catalog, lang='id'):
    count = int(input("Jumlah bot: ").strip())
    if count < 1:
        raise ValueError("Siapkan minimal satu bot.")
    aliases = data.get("aliases", {})
    bots = []
    for index in range(1, count + 1):
        slug = installer.safe_slug(input(f"ID bot {index} (huruf kecil dan tanda hubung): ").strip(), "bot")
        label = input(f"Nama tampilan [{slug}]: ").strip() or slug
        role = input("Peran utama: ").strip() or "Asisten proyek"
        items = [*catalog, *aliases]
        names = checklist(items, f"skill untuk {label}",
                          choice_help.menu_descriptions(items, 'skills', lang=lang, aliases=aliases))
        skills = installer.resolve_skills(names, catalog, aliases)
        bots.append({
            "id": slug, "label": label, "persona_text": f"# {label}\n\nPeran: {role}.\n",
            "required_skills": [name for name in skills if catalog[name]],
            "optional_skills": [name for name in skills if not catalog[name]],
        })
    return {**data, "bots": bots}


def _prompt_choice(prompt, default=""):
    """Read interactive input safely, falling back to default on blank or EOF."""
    try:
        return input(prompt).strip() or default
    except EOFError:
        return default


def _resolve_bot_selection(raw, labels):
    """Resolve 'all', empty input, 1-based indices, or bot IDs into unique ordered IDs."""
    text = (raw or "").strip()
    if not text or text.lower() in {"all", "*", "semua"}:
        return list(labels)
    by_lower = {label.lower(): label for label in labels}
    chosen = []
    for token in text.split(","):
        item = token.strip()
        if not item:
            continue
        if item.isdigit():
            index = int(item)
            if not 1 <= index <= len(labels):
                raise ValueError(f"Nomor bot di luar jangkauan (1-{len(labels)}): {item}")
            label = labels[index - 1]
        else:
            label = by_lower.get(item.lower())
            if not label:
                raise ValueError(f"Bot tidak dikenal: {item}")
        if label not in chosen:
            chosen.append(label)
    if not chosen:
        raise ValueError("Pilih minimal satu bot.")
    return chosen


def _resolve_app_targets(raw, ready_ids):
    """Map user-entered app numbers, names, or 'detected' into target IDs or empty list."""
    text = (raw or "").strip()
    if not text or text.lower() in {"detected", "all", "*"}:
        return list(ready_ids)
    if text.lower() in {"skip", "none", "0", "-"}:
        return []
    by_lower = {item.lower(): item for item in ready_ids}
    chosen = []
    for token in text.split(","):
        item = token.strip()
        if not item:
            continue
        if item.isdigit():
            index = int(item)
            if not 1 <= index <= len(ready_ids):
                raise ValueError(f"Nomor aplikasi di luar jangkauan (1-{len(ready_ids)}): {item}")
            mapped = ready_ids[index - 1]
        else:
            mapped = by_lower.get(item.lower(), item)
        if mapped not in chosen:
            chosen.append(mapped)
    return chosen


def _hermes_profile_roots(platform, target, mode, selections, profile_home):
    """Return list of (label, base_hermes_home, profile_arg, profile_dir) tuples."""
    if platform != "hermes":
        return []
    team = mode in {"custom-bots", "muza-preset"}
    if team and target.name.lower() == "profiles":
        roots = []
        for folder in selections:
            parent = folder.parent
            if parent == profile_home:
                roots.append(("yukino" if mode == "muza-preset" else "default", profile_home, "default", profile_home))
            else:
                roots.append((parent.name, profile_home, parent.name, parent))
        return roots
    return [("default", profile_home, "default", profile_home)]


def _stage_auto_trim_plugin(profile_home, target, mode, selections):
    """Stage fail-open msshi-auto-trim plugin files into Hermes profile(s) without mutating config.yaml."""
    plugin_src = ROOT / "hermes_plugins" / "msshi-auto-trim"
    files = [plugin_src / name for name in ("__init__.py", "plugin.yaml", "README.md")
             if (plugin_src / name).is_file()]
    if not files:
        return {"staged": False, "reason": "plugin source missing", "profiles": [], "llmtrim_binary": False}
    roots = _hermes_profile_roots("hermes", target, mode, selections, profile_home)
    if (profile_home / "config.yaml").is_file() and all(item[3] != profile_home for item in roots):
        roots = [*roots, ("default", profile_home, "default", profile_home)]
    staged_profiles = []
    for label, _, _, profile_dir in roots:
        if not profile_dir.is_dir():
            continue
        dest_dir = profile_dir / "plugins" / "msshi-auto-trim"
        installer.reject_links(dest_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)
        for src in files:
            dest_file = dest_dir / src.name
            installer.reject_links(dest_file)
            shutil.copy2(src, dest_file)
        staged_profiles.append(label)
    llmtrim_binary = bool(shutil.which("llmtrim") or shutil.which("llmtrim.exe"))
    return {
        "staged": bool(staged_profiles),
        "profiles": staged_profiles,
        "llmtrim_binary": llmtrim_binary,
        "fail_open": True,
    }


def _select_extra_slugs_interactive(catalog, packs):
    """Collect additional packs and individual skill slugs interactively."""
    pack_names = list(packs)
    for index, name in enumerate(pack_names, 1):
        print(f"  {index}. {name} ({len(packs[name])} skills)")
    raw_packs = _prompt_choice("Tambah extra packs (nomor/nama dipisah koma, atau Enter=lewati): ", "")
    seed_slugs = []
    if raw_packs and raw_packs.lower() not in {"skip", "none", "0", "-"}:
        by_lower = {name.lower(): name for name in pack_names}
        for token in raw_packs.split(","):
            item = token.strip()
            if not item:
                continue
            if item.isdigit():
                index = int(item)
                if not 1 <= index <= len(pack_names):
                    raise ValueError(f"Nomor pack di luar jangkauan (1-{len(pack_names)}): {item}")
                pack = pack_names[index - 1]
            else:
                pack = by_lower.get(item.lower())
                if not pack:
                    raise ValueError(f"Pack tidak dikenal: {item}")
            seed_slugs.extend(packs[pack])
    raw_skills = _prompt_choice("Tambah skill individu (slug dipisah koma, atau Enter=lewati): ", "")
    if raw_skills and raw_skills.lower() not in {"skip", "none", "0", "-"}:
        for token in raw_skills.split(","):
            slug = token.strip()
            if not slug:
                continue
            if slug not in catalog:
                raise ValueError(f"Skill tidak ditemukan di katalog: {slug}")
            seed_slugs.append(slug)
    return list(dict.fromkeys(seed_slugs))


def _setup_extra_skills_and_optional(args, mode, platform, target, catalog, packs, selections, home, state, lang, yes, profile_home=None):
    """Step [1/4]: Optionally add extra packs/skills per target/bot and opt-in REA."""
    choice_help.feature('setup-skills', lang=lang)
    choice_help.feature('rea', lang=lang)
    cli_packs = getattr(args, 'extra_packs', None) or []
    cli_skills = getattr(args, 'extra_skills', None) or []
    with_rea = bool(getattr(args, 'with_rea', False))
    pick = "1"
    seed_slugs = []
    for pack in cli_packs:
        if pack not in packs:
            raise ValueError(f"Pack tidak dikenal: {pack}")
        seed_slugs.extend(packs[pack])
    for slug in cli_skills:
        if slug not in catalog:
            raise ValueError(f"Skill tidak dikenal: {slug}")
        seed_slugs.append(slug)

    if not yes and not (cli_packs or cli_skills or with_rea):
        print("\n[1/4] Skills Tambahan & Opsional (REA default OFF):" if lang == "id"
              else "\n[1/4] Extra Skills & Optional Wrappers (REA default OFF):")
        print("  1. Pertahankan skill bawaan saat ini (Rekomendasi)" if lang == "id"
              else "  1. Keep current bundled skills (Recommended)")
        print("  2. Tambah extra packs/skills ke target atau bot" if lang == "id"
              else "  2. Add extra packs/skills to target or bots")
        print("  3. Tambah extra packs/skills + pasang wrapper opsional REA" if lang == "id"
              else "  3. Add extra packs/skills + install optional REA wrapper")
        print("  4. Pasang wrapper opsional REA saja (runtime Node/npm terpisah)" if lang == "id"
              else "  4. Install optional REA wrapper only (separate Node/npm runtime)")
        pick = _prompt_choice("Pilihan Skills [1]: ", "1")
        if pick not in {"1", "2", "3", "4"}:
            raise ValueError("Pilihan Skills harus 1, 2, 3, atau 4.")
        if pick in {"2", "3"}:
            seed_slugs = _select_extra_slugs_interactive(catalog, packs)
        if pick in {"3", "4"}:
            with_rea = True

    applied_targets = {}
    expanded_extra = installer.include_mandatory(seed_slugs, catalog) if seed_slugs else []
    if expanded_extra:
        folder_map = {
            ("yukino" if (mode == "muza-preset" and profile_home is not None and folder.parent == profile_home)
             else (folder.parent.name if mode in {"custom-bots", "muza-preset"} else folder.name)): folder
            for folder in selections
        }
        labels = list(folder_map)
        chosen_labels = labels
        if not yes and not (cli_packs or cli_skills) and len(labels) > 1:
            print("Target/bot tersedia: " + ", ".join(f"{i}.{name}" for i, name in enumerate(labels, 1)))
            raw_bots = _prompt_choice("Terapkan ke bot mana [all]: ", "all")
            chosen_labels = _resolve_bot_selection(raw_bots, labels)
        for label in chosen_labels:
            folder = folder_map[label]
            existing = list(selections.get(folder, ()))
            missing_only = [slug for slug in expanded_extra if slug not in existing]
            merged = sorted(set(existing) | set(expanded_extra))
            if missing_only:
                with locked(folder):
                    managed = state["targets"].setdefault(str(folder), {})
                    update_target(folder, merged, catalog, managed, apply=True, install_missing=missing_only)
                    write_json(home / STATE_FILE, state)
                selections[folder] = merged
            applied_targets[label] = missing_only

    rea_results = []
    if with_rea:
        from msshi_optional import enable, setup_targets
        for folder in setup_targets(mode, selections, source=ROOT):
            result = enable('rea', folder, source=ROOT, home=home)
            rea_results.append(result)
            print(json.dumps(result, ensure_ascii=False, indent=2))
    return {
        "choice": pick,
        "extra_packs": list(cli_packs),
        "extra_skills": sorted(set(expanded_extra)),
        "applied_targets": applied_targets,
        "rea_enabled": with_rea,
        "rea_results": rea_results,
    }


def _setup_plugins_and_addons(args, mode, platform, target, selections, profile_home, lang, yes):
    """Step [2/4]: Configure KAT, msshi-auto-trim plugin staging, Dreaming, OmniVoice, and opt-in Steel."""
    if platform != "hermes":
        print(f"\n[2/4] Plugin & Addon Hermes: dilewati (platform '{platform}' memakai workspace masing-masing).")
        return {"status": "skipped", "reason": f"platform={platform}"}

    from msshi_integrations import dream, kat, voice_enable, voice_status
    import msshi_browser_policy as browser_policy

    choice_help.feature('setup-plugins', lang=lang)
    steel_stat = browser_policy.status(profile_home)
    steel_config_present = bool(steel_stat.get("config_present", (profile_home / "config.yaml").is_file()))
    voice_stat = voice_status(profile_home)
    kat_stat = kat(profile_home, "status")
    print("\n[2/4] Plugin & Addon Hermes:")
    print(f"  - KAT-Coder saat ini : {kat_stat.get('mode', 'skip')} ({kat_stat.get('status', 'not configured')})")
    print(f"  - OmniVoice runtime  : {'terverifikasi' if voice_stat.get('synthesis_verified') else 'belum diverifikasi (opsional via msshi voice)'}")
    print(f"  - Steel Browser Policy: {'siap (config.yaml ada)' if steel_config_present else 'menunggu config.yaml Hermes'}")

    kat_modes = {"1": "light", "2": "ideal", "3": "cloud", "4": "skip"}
    req_kat = getattr(args, 'kat_mode', None)
    req_stage_trim = bool(getattr(args, 'stage_auto_trim', False))
    req_steel = bool(getattr(args, 'install_steel', False))
    pick = "5"
    kat_choice = req_kat
    stage_trim = req_stage_trim
    run_dream = False
    enable_voice = False

    if req_kat or req_stage_trim or req_steel:
        pick = "cli"
    elif yes:
        pick = "yes-default"
    else:
        print("  1. Stage plugin aman msshi-auto-trim (fail-open; pertahankan KAT saat ini) (Rekomendasi)")
        print("  2. Atur KAT-Coder (light / ideal / cloud / skip) + opsional msshi-auto-trim")
        print("  3. Aktifkan plugin lokal aman (msshi-auto-trim + Dreaming offline + OmniVoice jika terverifikasi)")
        print("  4. Opt-in Steel Browser Policy (butuh config.yaml & repo terpin)")
        print("  5. Lewati / pertahankan kondisi saat ini")
        pick = _prompt_choice("Pilihan Plugin [5]: ", "5")
        if pick not in {"1", "2", "3", "4", "5"}:
            raise ValueError("Pilihan Plugin harus 1-5.")
        if pick == "1":
            stage_trim = True
        elif pick == "2":
            choice_help.feature('kat', lang=lang)
            for index, name in enumerate(('kat-light', 'kat-ideal', 'kat-cloud', 'kat-skip'), 1):
                print(f"    {index}. {choice_help.describe('features', name, lang=lang)}")
            k_pick = _prompt_choice("Pilihan KAT [4]: ", "4")
            if k_pick not in kat_modes:
                raise ValueError("Pilihan KAT harus 1-4.")
            kat_choice = kat_modes[k_pick]
            stage_trim = _prompt_choice("Stage juga plugin fail-open msshi-auto-trim? [Y/n]: ", "y").lower() in {"y", "yes", "ya"}
        elif pick == "3":
            stage_trim = True
            run_dream = True
            enable_voice = True
        elif pick == "4":
            req_steel = True

    kat_result = kat(profile_home, kat_choice) if kat_choice is not None else kat_stat
    print("  KAT:", json.dumps(kat_result, ensure_ascii=False))
    if stage_trim:
        trim_result = _stage_auto_trim_plugin(profile_home, target, mode, selections)
        print(f"  msshi-auto-trim: staged ke profil {trim_result['profiles']} (fail-open, llmtrim_binary={trim_result['llmtrim_binary']}).")
    else:
        existing_trim = [
            label for label, _, _, profile_dir in _hermes_profile_roots("hermes", target, mode, selections, profile_home)
            if (profile_dir / "plugins" / "msshi-auto-trim" / "plugin.yaml").is_file()
        ]
        trim_result = {
            "staged": bool(existing_trim),
            "profiles": existing_trim,
            "llmtrim_binary": bool(shutil.which("llmtrim") or shutil.which("llmtrim.exe")),
            "fail_open": True,
        }

    dream_result = {"status": "skipped"}
    if run_dream:
        try:
            dream_result = {"status": "ok", "summary": dream(profile_home)}
            print(f"  Hermes-Dreaming: selesai lokal untuk {len(dream_result['summary'].get('profiles', []))} profil (0 LLM calls).")
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            dream_result = {"status": "deferred", "reason": str(error)}
            print(f"  Hermes-Dreaming: ditunda ({error}).")

    voice_result = {"status": "skipped", **voice_stat}
    if enable_voice:
        if voice_stat.get("synthesis_verified"):
            try:
                voice_result = {"status": "enabled", **voice_enable(profile_home)}
                print("  OmniVoice: diaktifkan untuk profil Hermes.")
            except (OSError, ValueError) as error:
                voice_result = {"status": "error", "reason": str(error)}
                print(f"  OmniVoice: gagal aktivasi ({error}).")
        else:
            voice_result = {"status": "not_verified", **voice_stat}
            print("  OmniVoice: belum diverifikasi; jalankan 'msshi voice --install-runtime' bila ingin mengaktifkan.")

    steel_result = {"status": "skipped", "config_present": steel_config_present}
    if req_steel:
        if not steel_config_present:
            steel_result = {"status": "deferred_pre_hermes", "reason": "config.yaml belum ada sebelum Hermes dibuka"}
            print("  Steel Policy: ditunda karena config.yaml Hermes belum ada.")
        else:
            try:
                steel_result = {"status": "installed", **browser_policy.install(profile_home, ROOT)}
                print("  Steel Policy: terpasang (opt-in).")
            except (OSError, ValueError, subprocess.SubprocessError) as error:
                steel_result = {"status": "error", "reason": str(error)}
                print(f"  Steel Policy: ditunda ({error}).")

    choice_help.feature('artcraft', lang=lang)
    return {
        "choice": pick,
        "kat": kat_result,
        "auto_trim": trim_result,
        "dreaming": dream_result,
        "omnivoice": voice_result,
        "steel_policy": steel_result,
    }


def _setup_service_connections(args, platform, profile_home, lang, yes):
    """Step [3/4]: Inspect and configure external service MCP/OAuth connections safely."""
    if platform != "hermes":
        print(f"\n[3/4] Koneksi eksternal (GitLab / Tinyfish): dilewati untuk platform '{platform}'.")
        return {"status": "skipped", "reason": f"platform={platform}", "brightdata_enabled": False}

    import msshi_service_connections as service_connections

    choice_help.feature('setup-services', lang=lang)
    svc_stat = service_connections.status(profile_home)
    config_present = bool(svc_stat) and all(bool(row.get("config_present")) for row in svc_stat.values())
    print("\n[3/4] Koneksi Eksternal (GitLab / Tinyfish; BrightData tetap OFF):")
    if config_present:
        print(f"  - Config Hermes siap di: {profile_home / 'config.yaml'}")
    else:
        print(f"  - Belum ada config.yaml di {profile_home} (mode sebelum Hermes dibuka).")

    req_svc = getattr(args, 'connect_services', None)
    if req_svc:
        selected = req_svc
    elif yes:
        selected = "skip"
    else:
        print("  1. Pasang koneksi MCP GitLab & Tinyfish per-profil (aman, mempertahankan model/provider)")
        print("  2. Pasang + bagikan token OAuth GitLab aktif ke profil lain (--share-oauth)")
        print("  3. Lewati (atur nanti via 'msshi services install')")
        pick = _prompt_choice("Pilihan Koneksi [3]: ", "3")
        mapping = {"1": "per-profile", "2": "share-oauth", "3": "skip"}
        if pick not in mapping:
            raise ValueError("Pilihan Koneksi harus 1, 2, atau 3.")
        selected = mapping[pick]

    if selected == "skip":
        existing_profiles = [
            name for name, row in svc_stat.items()
            if any(svc.get("registered") for svc in (row.get("services") or {}).values())
        ]
        return {
            "mode": "skip",
            "status": ("preserved" if existing_profiles else "skipped"),
            "existing_profiles": existing_profiles,
            "config_present": config_present,
            "brightdata_enabled": False,
        }
    if not config_present:
        print("  Koneksi eksternal ditunda: buka Hermes satu kali lalu jalankan 'msshi services install'.")
        return {"mode": selected, "status": "deferred_pre_hermes", "config_present": False, "brightdata_enabled": False}
    try:
        installed = service_connections.install(profile_home, share_oauth=(selected == "share-oauth"))
        print(f"  Koneksi eksternal terpasang di {len(installed.get('profiles', {}))} profil (BrightData tetap OFF).")
        return {"mode": selected, "status": "installed", "config_present": True,
                "brightdata_enabled": False, "receipt": installed.get("receipt"),
                "profiles": list(installed.get("profiles", {}))}
    except (OSError, ValueError) as error:
        print(f"  Koneksi eksternal memerlukan tindak lanjut: {error}")
        return {"mode": selected, "status": "deferred", "config_present": True,
                "brightdata_enabled": False, "error": str(error)}


def _setup_bot_app_connections(args, mode, platform, target, selections, profile_home, home, lang, yes):
    """Step [4/4]: Map Hermes bots to detected local/web apps via CLI-Anything without opening apps."""
    choice_help.feature('setup-bot-apps', lang=lang)
    if platform != "hermes":
        print(f"\n[4/4] Bot ke CLI-Anything ke Apps: dilewati (platform '{platform}'); gunakan 'msshi connect' untuk Hermes.")
        return {"mode": "skipped", "reason": f"platform={platform}", "bots": {},
                "auto_open_on_boot": False, "execution": "msshi-runtime-ticket"}

    bot_roots = _hermes_profile_roots(platform, target, mode, selections, profile_home)
    bot_labels = [label for label, _, _, _ in bot_roots]
    inv_profile = next((pdir for _, _, _, pdir in bot_roots if pdir.is_dir()), profile_home)
    try:
        candidates, inv_warnings = connections.inventory(inv_profile)
    except (OSError, ValueError) as error:
        candidates, inv_warnings = {}, [str(error)]

    ready_ids = sorted(tid for tid, row in candidates.items()
                       if row.get("readiness") in {"configured", "available", "available_web"})
    needs_install = sorted(tid for tid, row in candidates.items() if row.get("readiness") == "needs_install")

    print("\n[4/4] Bot ke CLI-Anything ke Apps (auto_open_on_boot=false):")
    print("  - Bot tersedia      : " + ", ".join(f"{i}.{name}" for i, name in enumerate(bot_labels, 1)))
    if ready_ids:
        print(f"  - App siap ({len(ready_ids)}): " + ", ".join(f"{i}.{tid}" for i, tid in enumerate(ready_ids, 1)))
    else:
        print("  - App siap          : belum ada target terdeteksi (katalog tetap tersedia).")
    print(f"  - App belum terpasang: {len(needs_install)} target opsional.")
    for warning in inv_warnings:
        print(f"  - Catatan: {warning}")

    req_mode = getattr(args, 'connect_apps', None)
    req_bots = getattr(args, 'connect_bots', None)
    req_targets = getattr(args, 'connect_targets', None)

    plan = []
    chosen_action = "skip"
    if req_mode == "skip":
        chosen_action = "skip"
    elif req_mode in {"auto-reconnect", "select"}:
        chosen_action = req_mode
        selected_bots = _resolve_bot_selection(req_bots or "all", bot_labels)
        mapped_targets = _resolve_app_targets(req_targets or "detected", ready_ids) if req_mode == "select" or req_targets else None
        targets_arg = ",".join(mapped_targets) if mapped_targets else None
        effective_mode = "select" if targets_arg else "auto-reconnect"
        for label in selected_bots:
            plan.append((label, effective_mode, targets_arg))
    elif yes:
        chosen_action = "skip"
    else:
        print("  1. Auto-reconnect SEMUA bot ke aplikasi terdeteksi (Rekomendasi)")
        print("  2. Auto-reconnect bot PILIHAN ke aplikasi terdeteksi")
        print("  3. Pilih manual aplikasi spesifik per bot (mapping bot -> apps)")
        print("  4. Lewati / atur nanti via 'msshi connect'")
        pick = _prompt_choice("Pilihan Bot -> Apps [4]: ", "4")
        if pick not in {"1", "2", "3", "4"}:
            raise ValueError("Pilihan Bot -> Apps harus 1-4.")
        if pick == "1":
            chosen_action = "auto-reconnect-all"
            plan = [(label, "auto-reconnect", None) for label in bot_labels]
        elif pick == "2":
            chosen_action = "auto-reconnect-selected"
            raw_bots = _prompt_choice("Pilih bot (nomor/ID dipisah koma, atau 'all') [all]: ", "all")
            for label in _resolve_bot_selection(raw_bots, bot_labels):
                plan.append((label, "auto-reconnect", None))
        elif pick == "3":
            chosen_action = "manual-per-bot"
            raw_bots = _prompt_choice("Pilih bot yang ingin dimapping (nomor/ID dipisah koma, atau 'all') [all]: ", "all")
            for label in _resolve_bot_selection(raw_bots, bot_labels):
                raw_apps = _prompt_choice(
                    f"  Aplikasi untuk bot '{label}' (nomor/ID dipisah koma, 'detected', atau 'skip') [detected]: ",
                    "detected",
                )
                mapped = _resolve_app_targets(raw_apps, ready_ids)
                if mapped:
                    plan.append((label, "select", ",".join(mapped)))

    root_by_label = {label: (base_root, profile_arg, profile_dir)
                     for label, base_root, profile_arg, profile_dir in bot_roots}
    bot_results = {}
    for label, conn_mode, targets_arg in plan:
        base_root, profile_arg, profile_dir = root_by_label[label]
        if not profile_dir.is_dir():
            bot_results[label] = {"status": "skipped", "reason": "profile directory missing"}
            continue
        run_args = SimpleNamespace(
            hermes_home=base_root, profile=profile_arg, state_dir=None, mode=conn_mode,
            targets=targets_arg, query=None, open=None, command_args=[], run=None,
            dry_run=False, catalog=False, status=False, add=None, remove=None, json=True, ticket=None,
        )
        capture = io.StringIO()
        try:
            with redirect_stdout(capture):
                exit_code = connections.run(run_args, default_state_dir=home)
        except (OSError, ValueError) as error:
            bot_results[label] = {"status": "error", "error": str(error)}
            print(f"  - {label}: gagal menyambungkan ({error})")
            continue
        conn_file = profile_dir / "msshi-bridge" / "connections.json"
        if conn_file.is_file():
            doc = installer.read_json(conn_file)
            targets_connected = list(doc.get("targets", []))
        else:
            targets_connected = []
        bot_results[label] = {
            "status": "connected" if exit_code == 0 else "warning",
            "mode": conn_mode,
            "targets": targets_connected,
            "count": len(targets_connected),
            "connections_file": str(conn_file),
        }
        preview = ", ".join(targets_connected[:6]) + ("..." if len(targets_connected) > 6 else "")
        print(f"  - {label}: {len(targets_connected)} app tersambung ({preview}), auto_open_on_boot=false")

    existing_connected_bots = {}
    if not plan:
        for label, _, _, profile_dir in bot_roots:
            conn_file = profile_dir / "msshi-bridge" / "connections.json"
            if conn_file.is_file():
                try:
                    existing_connected_bots[label] = len(installer.read_json(conn_file).get("targets", []))
                except (OSError, ValueError):
                    pass

    return {
        "mode": chosen_action,
        "detected_ready": ready_ids,
        "needs_install_count": len(needs_install),
        "bots": bot_results,
        "existing_connected_bots": existing_connected_bots,
        "auto_open_on_boot": False,
        "execution": "msshi-runtime-ticket",
    }


def _emit_setup_report(home, mode, platform, target, profile_home, report_data, lang):
    """Persist structured setup summary JSON and print concise user report."""
    report_path = home / "reports" / "last-setup-report.json"
    installer.reject_links(report_path.parent)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "version": release_version(ROOT),
        "mode": mode,
        "platform": platform,
        "target": str(target),
        "profile_home": str(profile_home) if profile_home else None,
        "provider_model_mutated": False,
        **report_data,
    }
    write_json(report_path, payload)
    skills_info = report_data["skills"]
    plugins_info = report_data["plugins"]
    services_info = report_data["services"]
    apps_info = report_data["bot_app_connections"]
    print("\n=== LAPORAN SETUP MSSHI ===" if lang == "id" else "\n=== MSSHI SETUP REPORT ===")
    print(f"Mode/Platform   : {mode} / {platform}")
    if platform == "hermes" and report_data.get("default_bot") == "yukino":
        print(f"Bot Default     : Yukino Yukinoshita ({profile_home})")
    print(f"Target Skill    : {skills_info['target_count']} folder (REA={'ON' if skills_info['rea_enabled'] else 'OFF'})")
    if platform == "hermes":
        print(f"Plugin & Addon  : KAT={plugins_info.get('kat', {}).get('mode', 'skip')}, "
              f"auto-trim={'staged' if plugins_info.get('auto_trim', {}).get('staged') else 'off'}, "
              f"OmniVoice={plugins_info.get('omnivoice', {}).get('status', 'skipped')}, "
              f"Steel={plugins_info.get('steel_policy', {}).get('status', 'skipped')}")
        print(f"Koneksi Service : {services_info.get('status', 'skipped')} (BrightData=OFF)")
        existing_conns = apps_info.get('existing_connected_bots') or {}
        if apps_info.get('bots'):
            print(f"Bot -> Apps     : {apps_info.get('mode', 'skipped')} "
                  f"({len(apps_info.get('bots', {}))} bot dipetakan, auto_open_on_boot=false)")
        elif existing_conns:
            print(f"Bot -> Apps     : preserved ({len(existing_conns)} bot sudah tersambung, auto_open_on_boot=false)")
        else:
            print(f"Bot -> Apps     : {apps_info.get('mode', 'skipped')} "
                  f"(0 bot dipetakan, auto_open_on_boot=false)")
    print(f"Provider/Model  : dipertahankan utuh (provider_model_mutated=false)")
    print(f"File Laporan    : {report_path}")
    return report_path


def setup(args, home, state):
    lang = getattr(args, 'lang', 'id')
    yes = getattr(args, 'yes', False)
    requested_mode = getattr(args, 'mode', None)
    if requested_mode:
        mode = requested_mode
    else:
        for index, mode_name in enumerate(MODES, 1):
            print(f"{index}. {mode_name} - {choice_help.describe('modes', mode_name, lang=lang)}")
        pick = input("Mode [1]: ").strip() or "1"
        if pick not in {"1", "2", "3", "4"}:
            raise ValueError("Mode harus 1, 2, 3, atau 4.")
        mode = MODES[int(pick) - 1]
    team = mode in {"custom-bots", "muza-preset"}
    platform, target = choose_targets(home, args.platform, args.target_dir, team, lang, yes=yes)
    print('Instruksi skill, aplikasi, runtime, model, dan akun dipasang terpisah; opsi dapat ditambahkan nanti.'
          if lang == 'id' else 'Skill instructions, apps, runtimes, models and accounts are separate; skipped options can be added later.')
    data, catalog, packs = installer.read_matrix(ROOT / MATRIX)
    command = ["--mode", mode, "--platform", platform, "--target-dir", str(target)]
    default_bot_mode = getattr(args, 'default_bot', 'auto')
    yukino_is_default = (
        platform == "hermes"
        and mode == "muza-preset"
        and target.name.lower() == "profiles"
        and default_bot_mode != "keep-hermes"
    )
    if platform == "hermes" and mode == "muza-preset" and default_bot_mode != "auto":
        command.extend(("--default-bot", default_bot_mode))
    selections = {}
    custom_names_used = False
    with TemporaryDirectory(prefix=".msshi-stage-", dir=home) as scratch:
        if mode == "custom-bots":
            data = custom_matrix(data, catalog, lang)
            custom_names_used = True
        elif mode == "muza-preset" and not yes:
            choice_help.feature('custom-display-names', lang=lang)
            if input("Custom display names? [y/N]: ").strip().lower() in {"y", "yes", "ya"}:
                custom_names_used = True
                data = {**data, "bots": [{**bot, "label": input(f"{bot['label']} [{bot['id']}]: ").strip() or bot["label"]}
                                        for bot in data["bots"]]}
        if team:
            if platform == "hermes" and custom_names_used:
                command.append("--update-display-names")
            matrix = Path(scratch) / "matrix.json"
            write_json(matrix, data)
            command.extend(("--matrix", str(matrix)))
        if team:
            hermes_root_dir = (
                hermes_profiles.resolve_target_hermes_home(target)
                if (platform == "hermes" and target.name.lower() == "profiles")
                else None
            )
            for bot_id, _, skills, _ in installer.team_plan(data, mode, catalog):
                if yukino_is_default and bot_id == "yukino" and hermes_root_dir is not None:
                    selections[hermes_root_dir / "skills"] = skills
                else:
                    selections[target / bot_id / "skills"] = skills
        elif mode == "selective":
            chosen = checklist(list(packs), "paket", choice_help.menu_descriptions(packs, 'packs', lang=lang))
            command.extend(("--packs", *chosen))
            selections[target] = installer.include_mandatory(
                (slug for pack in chosen for slug in packs[pack]), catalog,
            )
        else:
            selections[target] = list(catalog)
        installer.main(command)
        if not yes and not confirmed():
            print("Setup dibatalkan.")
            return
        installer.main([*command, "--apply"])
        for folder, skills in selections.items():
            ensure_target(folder, home, ROOT)
            managed = state["targets"].setdefault(str(folder), {})
            for slug in skills:
                installed = folder / slug
                if catalog[slug] and installed.is_dir() and (installed / "SKILL.md").is_file():
                    files = inventory(installed)
                    if files == inventory(catalog[slug]):
                        managed[slug] = fingerprint(files)
        write_json(home / STATE_FILE, state)
    print(f"Target terdaftar untuk pembaruan MSSHI: {len(selections)}.")
    profile_home = None
    if platform == "hermes":
        is_hermes_target = target.name.lower() in {"profiles", "skills"}
        profile_home = (
            hermes_profiles.resolve_target_hermes_home(target)
            if is_hermes_target
            else hermes_profiles.resolve_hermes_home()
        )
        if is_hermes_target:
            migrate_runtime(ROOT, profile_home)
    skills_report = _setup_extra_skills_and_optional(
        args, mode, platform, target, catalog, packs, selections, home, state, lang, yes, profile_home=profile_home,
    )
    plugins_report = _setup_plugins_and_addons(args, mode, platform, target, selections, profile_home, lang, yes)
    services_report = _setup_service_connections(args, platform, profile_home, lang, yes)
    apps_report = _setup_bot_app_connections(args, mode, platform, target, selections, profile_home, home, lang, yes)
    _emit_setup_report(
        home, mode, platform, target, profile_home,
        {
            "default_bot": ("yukino" if yukino_is_default else ("keep-hermes" if mode == "muza-preset" and platform == "hermes" else "default")),
            "skills": {
                "target_count": len(selections),
                "targets": {str(folder): sorted(set(items)) for folder, items in selections.items()},
                **skills_report,
            },
            "plugins": plugins_report,
            "services": services_report,
            "bot_app_connections": apps_report,
        },
        lang,
    )
    if yes and not getattr(args, 'download_pdf', False) and not getattr(args, 'pdf_version', None):
        args.no_pdf = True
    from msshi_manuals import prompt_manual_download
    prompt_manual_download(args, source_root=ROOT, lang=lang)


def confirmed():
    return input("Terapkan rencana? [y/N]: ").strip().lower() in {"y", "yes", "ya"}


def select(args, home, state, source, commit):
    data, catalog, packs = validate_release(source, release_version(ROOT))
    lang = getattr(args, 'lang', 'id')
    _, target = choose_targets(home, args.platform, args.target_dir, lang=lang)
    ensure_target(target, home, source)
    choice_help.feature('skill-vs-pack', source=source, lang=lang)
    kind = input("Pilih (p)aket atau (s)kill individual? [p]: ").strip().lower() or "p"
    if kind == "p":
        names = [slug for pack in checklist(list(packs), "paket", choice_help.menu_descriptions(packs, 'packs', source=source, lang=lang)) for slug in packs[pack]]
    elif kind == "s":
        aliases = data.get("aliases", {})
        bundled = {slug: path for slug, path in catalog.items() if path}
        items = [*bundled, *aliases]
        names = installer.resolve_skills(checklist(items, "skill", choice_help.menu_descriptions(items, 'skills', source=source, lang=lang, aliases=aliases)), bundled, aliases)
    else:
        raise ValueError("Masukkan p atau s.")
    names = installer.include_mandatory(names, catalog)
    managed = state["targets"].get(str(target), {})
    print(f"Rencana pilihan di {target}:")
    update_target(target, names, catalog, managed, apply=False, install_missing=names)
    if not confirmed():
        print("Pilihan dibatalkan.")
        return
    release_id = stage_release(source, home)
    protected_backup(home, [target])
    with locked(target):
        state["targets"][str(target)] = managed
        try:
            update_target(target, names, catalog, managed, apply=True, install_missing=names)
        finally:
            write_json(home / STATE_FILE, state)
    state.update(current=release_id, git_commit=commit)
    write_json(home / STATE_FILE, state)


def migrate_runtime(source, hermes_home=None):
    """Invoke the incoming migration so upgrades from v2 use the new implementation."""
    candidate = hermes_profiles.resolve_hermes_home(hermes_home)
    sync_summary = hermes_profiles.sync_pending_profile_configs(candidate)
    if sync_summary.get("seeded_configs") or sync_summary.get("seeded_envs"):
        hermes_profiles.notify_live_multiplexer(candidate)
    if not (candidate / "config.yaml").is_file():
        if (candidate / "profiles").is_dir():
            print(
                f"Profil Hermes sudah disiapkan di {candidate / 'profiles'}. "
                "Buka Hermes & atur provider/model Anda, lalu jalankan 'msshi desktop' atau 'msshi runtime migrate'."
            )
        else:
            print("Hermes profile not detected. Public skills updated. Run msshi setup to choose a host.")
        return 0
    script = source / "scripts" / "msshi_runtime.py"
    if not script.is_file():
        return 0
    outcome = subprocess.call([sys.executable, "-B", "-X", "utf8", str(script),
                               "migrate", "--home", str(candidate)])
    if outcome:
        return outcome
    # Refresh an explicitly enrolled policy only. Fresh installations select
    # Steel with msshi browser --install; no surprise browser account access.
    from msshi_runtime import profiles, yaml_read
    helper = source / 'scripts/msshi_browser_policy.py'
    for folder in profiles(candidate).values():
        config = yaml_read((folder / 'config.yaml').read_bytes())
        if 'msshi-steel-policy' not in ((config.get('plugins') or {}).get('enabled') or []):
            continue
        if helper.is_file():
            outcome = subprocess.call([sys.executable, '-B', '-X', 'utf8', str(helper),
                                       '--install', '--hermes-home', str(folder)])
            if outcome:
                return outcome
    return 0


def update(args, home, state, source, commit):
    current = release_version(ROOT)
    _, catalog, _ = validate_release(source, current)
    release_id = stage_release(source, home)
    protected_backup(home, state["targets"])
    required = installer.mandatory_skills(catalog)
    for raw, managed in state["targets"].items():
        target = installer.absolute(raw)
        ensure_target(target, home, source)
        print(f"Target {target}:")
        if not target.is_dir():
            print("  Folder instalasi tidak ada; dipertahankan.")
            continue
        with locked(target):
            try:
                update_target(target, (*managed, *required), catalog, managed,
                              apply=True, install_missing=required)
            finally:
                write_json(home / STATE_FILE, state)
    from msshi_managed import refresh as refresh_managed
    managed_result = refresh_managed(home, source, apply=True)
    print(json.dumps(managed_result, ensure_ascii=False, indent=2))
    # refresh() checkpoints its fingerprints; retain them in the caller state.
    state['managed_bindings'] = read_state(home).get('managed_bindings', [])
    if any(row.get('status') == 'blocked' for row in managed_result['results']):
        print('Registered shared skill link changed; review msshi managed status before retrying.')
        return 1
    migration = migrate_runtime(source, getattr(args, 'hermes_home', None))
    if migration:
        print("Migration needs attention. The previous active release remains selected.")
        return migration
    state.update(current=release_id, git_commit=commit)
    write_json(home / STATE_FILE, state)
    print(f"Rilis MSSHI: {current} -> {release_version(source)} ({commit[:12]}).")
    if not state["targets"] and not state.get("managed_bindings"):
        print("Belum ada target. Jalankan msshi setup untuk memasang dan mendaftarkan skills.")
    has_manual_catalog = (source / "docs" / "manuals" / "pdf_catalog.json").is_file()
    explicit_pdf = bool(getattr(args, "download_pdf", False) or getattr(args, "pdf_version", None))
    if explicit_pdf or (has_manual_catalog and sys.stdin.isatty() and not getattr(args, "no_pdf", False)):
        from msshi_manuals import prompt_manual_download
        prompt_manual_download(args, source_root=source)
    if args.skip_upstreams:
        return 0
    rows = fetch_upstreams(source / UPSTREAMS, home / "upstreams")
    failed = int(any(row["status"] == "failed" for row in rows.values()))
    candidate = hermes_profiles.resolve_hermes_home(getattr(args, 'hermes_home', None))
    integration = source / "scripts" / "msshi_integrations.py"
    if (candidate / "config.yaml").is_file() and integration.is_file():
        failed = max(failed, subprocess.call([sys.executable, "-B", "-X", "utf8", str(integration),
                                             "install", "--home", str(candidate)]))
    return failed


def active_script(home):
    state = read_state(home)
    if current := state.get("current"):
        if not RELEASE_ID.fullmatch(current):
            raise ValueError("ID rilis lokal tidak valid.")
        script = home / "releases" / current / "scripts" / "msshi_cli.py"
        installer.reject_links(script)
        if not script.is_file():
            raise ValueError(f"Rilis lokal hilang: {script}. Jalankan installer ulang.")
        return script
    return None


def main(argv=None):
    from msshi_launchers import bootstrap

    parser = argparse.ArgumentParser(prog="msshi", description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check", aliases=["status"],
                                  help="Bandingkan versi lokal dan GitHub main dan lihat status koneksi.")
    check.add_argument("--hermes-home", type=Path, help="Folder Hermes untuk pemeriksaan koneksi.")
    check.add_argument("--profile", help="Profil Hermes untuk pemeriksaan koneksi.")
    check.add_argument("--state-dir", type=Path, help="Folder penyimpanan koneksi yang akan diperiksa.")
    connect = subparsers.add_parser("connect", help="Kelola koneksi aplikasi CLI-Anything.")
    connections.configure_parser(connect)
    updater = subparsers.add_parser("update", help="Perbarui rilis, skill yang dikelola, dan cache upstream.")
    updater.add_argument("--skip-upstreams", action="store_true", help="Hanya perbarui MSSHI dan skill bundel.")
    updater.add_argument("--hermes-home", type=Path, help="Folder Hermes untuk migrasi v3.")
    updater.add_argument("--source", type=Path, help="Pakai kandidat lokal yang sudah diperiksa.")
    updater.add_argument("--download-pdf", action="store_true", help="Unduh Buku Panduan PDF lengkap untuk versi ini.")
    updater.add_argument("--no-pdf", action="store_true", help="Lewati pertanyaan unduh Buku Panduan PDF.")
    updater.add_argument("--pdf-version", help="Versi PDF panduan yang diunduh (latest, v3.1.0, v3.0).")
    updater.add_argument("--pdf-dest", type=Path, help="Folder tujuan simpan PDF panduan.")
    for verb in ("runtime", "integrations", "desktop", "audit", "doctor", "skripsi", "assets", "compact", "browser", "trim", "managed", "services", "timesfm", "brag", "scrapling", "harness2", "optional", "rea", "choices", "manual"):
        descriptions = {
            'runtime': 'Migrasi profil dan jalankan alat sesuai tiket tugas.',
            'integrations': 'Siapkan integrasi opsional dengan prasyarat terpisah.',
            'desktop': 'Status dan peluncur Hermes Desktop.',
            'audit': 'Periksa paket/profil dan bukti tanpa chat LLM.',
            'doctor': 'Cek kesehatan sistem, Drive C:/D:, dependensi skripsi & paritas MSSHI.',
            'skripsi': 'Rakit template skripsi Word (.docx) drag-and-drop via MuZA Skripsi v1.1.',
            'assets': 'Cari bahan persona pribadi di lokasi yang dipilih.',
            'compact': 'Padatkan data internal sesuai format yang didukung.',
            'browser': 'Periksa kebijakan Steel dan persetujuan browser personal.',
            'trim': 'Ringkas JSON yang memenuhi syarat tanpa kehilangan nilai.',
            'managed': 'Kelola pembaruan salinan skill yang cocok dengan fingerprint.',
            'services': 'Status dan penyiapan MCP web GitLab/Tinyfish.',
            'timesfm': 'Peramalan deret waktu lokal; runtime/model terpisah.',
            'brag': 'Konsep dan video HTML/MP4; runtime dan aset terpisah.',
            'scrapling': 'Ekstrak CSS/XPath dari HTML lokal tanpa crawler jaringan.',
            'harness2': 'Demo deterministik dan proposal eksperimen harness.',
            'optional': 'Lihat atau pasang opsi tambahan; default OFF.',
            'rea': 'Analisis statis JavaScript/arsip; opsi Coder, runtime terpisah.',
            'choices': 'Baca fungsi dan prasyarat setiap pilihan tanpa memasang apa pun.',
            'manual': 'Lihat atau unduh Buku Panduan PDF Lengkap per versi.',
        }
        command = subparsers.add_parser(verb, add_help=False, help=descriptions[verb])
        command.add_argument("arguments", nargs=argparse.REMAINDER)
    for verb in ("dream", "voice", "kat"):
        command = subparsers.add_parser(verb, add_help=False, help={
            'dream': 'Proposal pelajaran lokal untuk ditinjau, bukan promosi memori otomatis.',
            'voice': 'Status/setup OmniVoice lokal untuk audio yang diminta.',
            'kat': 'Catat preferensi subagen coding; model/endpoint belum otomatis aktif.',
        }[verb])
        command.add_argument("arguments", nargs=argparse.REMAINDER)
    for action in ("setup", "select"):
        wizard = subparsers.add_parser(action, help="Buka wizard empat mode." if action == "setup" else "Pilih skill atau paket.")
        wizard.add_argument("--platform", choices=PLATFORMS)
        wizard.add_argument("--target-dir", type=Path)
        wizard.add_argument("--lang", choices=('id', 'en'), default='id', help="Bahasa penjelasan pilihan (id/en); format input tetap sama.")
        if action == "setup":
            wizard.add_argument("--mode", choices=MODES, help="Pilih mode langsung tanpa prompt.")
            wizard.add_argument("--yes", "-y", action="store_true", help="Konfirmasi otomatis tanpa prompt.")
            wizard.add_argument("--default-bot", choices=("auto", "yukino", "keep-hermes"), default="auto", help="Di mode muza-preset untuk Hermes, atur apakah profil 'default' otomatis menjadi Yukino ('auto'/'yukino') atau dipertahankan sebagai 'Hermes' ('keep-hermes').")
            wizard.add_argument("--extra-packs", nargs="+", help="Tambahkan extra packs di langkah [1/4] Skills.")
            wizard.add_argument("--extra-skills", nargs="+", help="Tambahkan extra skill slugs di langkah [1/4] Skills.")
            wizard.add_argument("--kat-mode", choices=("light", "ideal", "cloud", "skip"), help="Atur mode KAT-Coder di langkah [2/4] Plugin.")
            wizard.add_argument("--stage-auto-trim", action="store_true", help="Stage plugin fail-open msshi-auto-trim ke profil Hermes di langkah [2/4] Plugin.")
            wizard.add_argument("--install-steel", action="store_true", help="Opt-in Steel Browser Policy di langkah [2/4] Plugin.")
            wizard.add_argument("--connect-services", choices=("skip", "per-profile", "share-oauth"), help="Atur koneksi MCP GitLab/Tinyfish di langkah [3/4] Koneksi.")
            wizard.add_argument("--connect-apps", choices=("skip", "auto-reconnect", "select"), help="Sambungkan Bot -> CLI-Anything -> Apps di langkah [4/4].")
            wizard.add_argument("--connect-bots", help="Daftar bot (dipisah koma atau 'all') untuk langkah [4/4].")
            wizard.add_argument("--connect-targets", help="Daftar app target (dipisah koma atau 'detected') untuk langkah [4/4].")
            wizard.add_argument("--with-rea", action="store_true", help="Opt-in analisis statis JavaScript/arsip: pasang instruksi REA; runtime Node/npm dan engine native terpisah. Default OFF.")
            wizard.add_argument("--download-pdf", action="store_true", help="Sekalian unduh Buku Panduan PDF Lengkap untuk versi ini.")
            wizard.add_argument("--no-pdf", action="store_true", help="Lewati pertanyaan unduh Buku Panduan PDF.")
            wizard.add_argument("--pdf-version", help="Versi PDF panduan yang diunduh (latest, v3.1.0, v3.0).")
            wizard.add_argument("--pdf-dest", type=Path, help="Folder tujuan simpan PDF panduan.")
        if action == "select":
            wizard.add_argument("--local", action="store_true", help="Pilih dari rilis lokal tanpa mengakses GitHub.")
    launcher = subparsers.add_parser("bootstrap", help="Pasang launcher global dari rilis lokal.")
    launcher.add_argument("--no-path", action="store_true", help="Jangan ubah PATH user.")
    effective = list(sys.argv[1:] if argv is None else argv)
    passthrough = {"runtime", "integrations", "desktop", "audit", "doctor", "skripsi", "assets", "dream", "voice", "kat", "compact", "browser", "trim", "managed", "services", "timesfm", "brag", "scrapling", "harness2", "optional", "rea", "choices", "manual"}
    if effective and effective[0] in passthrough:
        args = parser.parse_args([effective[0], "--", *effective[1:]])
        args.arguments = args.arguments[1:]
    else:
        args = parser.parse_args(effective)
    home = data_root()
    try:
        if args.command != "bootstrap" and not (args.command == "update" and args.source):
            active = active_script(home)
            if active and active != Path(__file__).resolve():
                return subprocess.call([sys.executable, "-B", "-X", "utf8", str(active),
                                        *(sys.argv[1:] if argv is None else argv)])
        if args.command in {"check", "status"}:
            connection_summary(args, home)
            bindings = read_state(home).get('managed_bindings', [])
            print(f'MSSHI managed bundles: {len(bindings)} registered logical references. Details: msshi managed status')
            check_release()
            return 0
        if args.command == "connect":
            return connections.run(args, default_state_dir=home)
        entrypoints = {"choices": "msshi_choices.py", "manual": "msshi_manuals.py", "doctor": "msshi_doctor.py", "skripsi": "msshi_skripsi_drop.py", "rea": "msshi_rea.py", "runtime": "msshi_runtime.py", "integrations": "msshi_integrations.py",
                       "desktop": "msshi_desktop.py", "audit": "check_release_v31.py", "assets": "find_muza_assets.py",
                       "compact": "caveman_context_filter.py", "browser": "msshi_browser_policy.py", "trim": "msshi_llmtrim.py",
                       "managed": "msshi_managed.py", "optional": "msshi_optional.py", "services": "msshi_service_connections.py", "timesfm": "msshi_timesfm.py",
                       "brag": "../skills/brag/scripts/msshi_brag.py", "scrapling": "msshi_scrapling.py", "harness2": "msshi_harness2.py",
                       "dream": "msshi_integrations.py", "voice": "msshi_integrations.py", "kat": "msshi_integrations.py"}
        if args.command in entrypoints:
            prefix = [args.command] if args.command in {"dream", "voice", "kat"} else []
            return subprocess.call([sys.executable, "-B", "-X", "utf8", str(ROOT / "scripts" / entrypoints[args.command]),
                                    *prefix, *args.arguments])
        with locked(home):
            state = read_state(home)
            if args.command == "bootstrap":
                current = active_script(home)
                validate_release(ROOT, release_version(current.parents[1] if current else ROOT))
                migration = migrate_runtime(ROOT)
                if migration:
                    return migration
                bootstrap(home, stage_release(ROOT, home), state, args.no_path)
            elif args.command == "setup":
                setup(args, home, state)
            elif args.command == "select" and args.local:
                select(args, home, state, ROOT, state.get("git_commit"))
            elif args.command == "update" and args.source:
                source = installer.absolute(args.source)
                commit = "local-candidate"
                return update(args, home, state, source, commit)
            else:
                with TemporaryDirectory(prefix=".msshi-stage-", dir=home) as scratch:
                    source, commit = remote_release(Path(scratch))
                    if args.command == "select":
                        select(args, home, state, source, commit)
                    else:
                        return update(args, home, state, source, commit)
    except (OSError, ValueError, KeyError, TypeError, EOFError, subprocess.SubprocessError) as error:
        parser.exit(1, f"msshi: {error}\n")
    except KeyboardInterrupt:
        parser.exit(130, "\nmsshi: dibatalkan.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
