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
import msshi_academic as academic
from msshi_sources import RAW, REPOSITORY, clone, data_root, download, fetch_upstreams, write_json
from msshi_update import inventory, release_version, update_skill


ROOT = Path(__file__).resolve().parents[1]
MATRIX = Path("configs", "bot_role_and_skill_matrix.json")
UPSTREAMS = Path("configs", "upstreams.json")
STATE_FILE = "state.json"
RELEASE_ID = re.compile(r"(?:[0-9a-f]{24}|[0-9a-f]{64})")
SEMVER = re.compile(r"(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?")
PLATFORMS = (*installer.HOSTS, "manual")
MODES = ("solo", "custom-bots", "selective", "muza-preset", *academic.MODES)
TEAM_MODES = {"custom-bots", "muza-preset", *academic.MODES}
PRESET_MODES = {"muza-preset", *academic.MODES}
RELEASE_DIRS = ("scripts", "configs", "skills", "docs", "portable", "assets", "adapters",
                "business-sage", ".claude-plugin", "hermes_plugins", "optional", "notebooks", "templates")
RELEASE_FILES = ("VERSION.json", "CHANGELOG.md", "README.md", "README_EN.md",
                 "LICENSE", "SKILL.md", "install.ps1", "install.sh", "package.json",
                 "THIRD_PARTY_NOTICES.md", "CREDITS.md", "UPDATE_OTOMATIS_KE_V3.bat",
                 "MULAI_DI_SINI_PEMULA.bat", "MULAI_SKRIPSI_DRAG_AND_DROP.bat", "INSTALL_FOR_AGENTS.md")


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


def stage_release(source, home, *, build_profile="full"):
    """Publish a separate, verified release directory and keep old baselines."""
    releases = home / "releases"
    installer.reject_links(releases)
    releases.mkdir(exist_ok=True)
    light_requested = build_profile == "light" or (source / "configs" / "light_build_active.json").is_file()
    with TemporaryDirectory(prefix=".msshi-stage-", dir=releases) as scratch:
        staging = Path(scratch) / "release"
        staging.mkdir()
        if light_requested and (source / "configs" / "light_build_manifest.json").is_file():
            import msshi_light as light_mod
            light_mod.stage_light_tree(source, staging)
        else:
            for name in RELEASE_DIRS:
                directory = source / name
                installer.reject_links(directory)
                if directory.is_dir():
                    installer.validate_tree(directory)
                    shutil.copytree(directory, staging / name, symlinks=True,
                                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
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
            hint = " (bebas drive C:/D:/E:/folder mana saja)" if os.name == "nt" else " (bebas folder mana saja)"
            target_dir = input(f"Folder {kind}{hint} [{default}]: ").strip() or default
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
    team = mode in TEAM_MODES
    if team and target.name.lower() == "profiles":
        roots = []
        for folder in selections:
            parent = folder.parent
            if parent == profile_home:
                label = ("yukino" if mode in PRESET_MODES and
                         hermes_profiles.team_role_profiles(profile_home)["yukino"] == "default" else "default")
                roots.append((label, profile_home, "default", profile_home))
            else:
                roots.append((parent.name, profile_home, parent.name, parent))
        return roots
    return [("default", profile_home, "default", profile_home)]


def _stage_auto_trim_plugin(profile_home, target, mode, selections):
    """Stage/enable the single native MSSHITrim hook; runtime downloads are install-only."""
    import msshi_trim_setup as trim_setup
    roots = _hermes_profile_roots("hermes", target, mode, selections, profile_home)
    if (profile_home / "config.yaml").is_file() and all(item[3] != profile_home for item in roots):
        roots = [*roots, ("default", profile_home, "default", profile_home)]
    names = list(trim_setup.profile_dirs(profile_home))
    if not names:
        return {"staged": False, "reason": "native profiles are not created yet", "profiles": [], "llmtrim_binary": False}
    try:
        result = trim_setup.install(profile_home, source_root=ROOT, selected=names,
                                    apply=True, allow_download=True)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        # A blocked download is not permission to reconfigure a provider or abort
        # the rest of setup. Stage lightweight files, retaining a pending state.
        result = trim_setup.install(profile_home, source_root=ROOT, selected=names,
                                    apply=True, allow_download=False)
        result["download_pending"] = type(error).__name__
    staged_ids = {row["profile"] for row in result["profiles"]
                  if not row["status"].startswith("preserved_")}
    staged = [label for label, _, _, folder in roots
              if ("default" if folder == profile_home else folder.name) in staged_ids]
    wise_result = None
    try:
        wise_result = hermes_profiles.install_wise_plugins(profile_home, ROOT, plugin_ids=("spacewise", "sharewise", "chalk"))
    except (OSError, ValueError):
        wise_result = {"installed": False}
    return {"staged": bool(staged), "profiles": staged,
            "llmtrim_binary": result["binary"]["status"].startswith("verified_"),
            "fail_open": True, "display_name": "MSSHITrim", "wise_plugins": wise_result, "details": result}


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
    """Step [1/4]: Optionally add extra packs/skills per target/bot and opt-in REA / Imagination Studio."""
    choice_help.feature('setup-skills', lang=lang)
    choice_help.feature('rea', lang=lang)
    choice_help.feature('imagination-studio', lang=lang)
    cli_packs = getattr(args, 'extra_packs', None) or []
    cli_skills = getattr(args, 'extra_skills', None) or []
    with_rea = bool(getattr(args, 'with_rea', False))
    with_studio = bool(getattr(args, 'with_imagination_studio', False))
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

    if not yes and not (cli_packs or cli_skills or with_rea or with_studio):
        print("\n[1/4] Skills Tambahan & Opsional (REA & Imagination Studio default OFF):" if lang == "id"
              else "\n[1/4] Extra Skills & Optional Wrappers (REA & Imagination Studio default OFF):")
        print("  1. Pertahankan skill bawaan saat ini (Rekomendasi)" if lang == "id"
              else "  1. Keep current bundled skills (Recommended)")
        print("  2. Tambah extra packs/skills ke target atau bot" if lang == "id"
              else "  2. Add extra packs/skills to target or bots")
        print("  3. Tambah extra packs/skills + pasang wrapper opsional REA" if lang == "id"
              else "  3. Add extra packs/skills + install optional REA wrapper")
        print("  4. Pasang wrapper opsional REA saja (khusus Coder; runtime Node/npm terpisah)" if lang == "id"
              else "  4. Install optional REA wrapper only (Coder; separate Node/npm runtime)")
        print("  5. Pasang wrapper opsional Imagination Studio saja (khusus Kiki-Chii / Content Creator; bekerja sama dengan Filmmaker)" if lang == "id"
              else "  5. Install optional Imagination Studio wrapper only (Kiki-Chii / Content Creator; collaborates with Filmmaker)")
        print("  6. Pasang kedua wrapper opsional: REA (Coder) + Imagination Studio (Kiki-Chii)" if lang == "id"
              else "  6. Install both optional wrappers: REA (Coder) + Imagination Studio (Kiki-Chii)")
        pick = _prompt_choice("Pilihan Skills [1]: ", "1")
        if pick not in {"1", "2", "3", "4", "5", "6"}:
            raise ValueError("Pilihan Skills harus 1, 2, 3, 4, 5, atau 6.")
        if pick in {"2", "3"}:
            seed_slugs = _select_extra_slugs_interactive(catalog, packs)
        if pick in {"3", "4", "6"}:
            with_rea = True
        if pick in {"5", "6"}:
            with_studio = True

    applied_targets = {}
    expanded_extra = installer.include_mandatory(seed_slugs, catalog) if seed_slugs else []
    if expanded_extra:
        folder_map = {
            ("yukino" if (mode in PRESET_MODES and profile_home is not None and folder.parent == profile_home)
             else (folder.parent.name if mode in TEAM_MODES else folder.name)): folder
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
        for folder in setup_targets(mode, selections, name='rea', source=ROOT):
            result = enable('rea', folder, source=ROOT, home=home)
            rea_results.append(result)
            print(json.dumps(result, ensure_ascii=False, indent=2))
    studio_results = []
    if with_studio:
        from msshi_optional import enable, setup_targets
        for folder in setup_targets(mode, selections, name='imagination-studio', source=ROOT):
            result = enable('imagination-studio', folder, source=ROOT, home=home)
            studio_results.append(result)
            print(json.dumps(result, ensure_ascii=False, indent=2))
    return {
        "choice": pick,
        "extra_packs": list(cli_packs),
        "extra_skills": sorted(set(expanded_extra)),
        "applied_targets": applied_targets,
        "rea_enabled": with_rea,
        "rea_results": rea_results,
        "imagination_studio_enabled": with_studio,
        "imagination_studio_results": studio_results,
    }


def _setup_plugins_and_addons(args, mode, platform, target, selections, profile_home, lang, yes):
    """Step [2/4]: Configure optional local addons; external service/browser login stays manual."""
    if platform != "hermes":
        print(f"\n[2/4] Plugin & Addon Hermes: dilewati (platform '{platform}' memakai workspace masing-masing).")
        return {"status": "skipped", "reason": f"platform={platform}"}

    from msshi_integrations import dream, kat, voice_enable, voice_status
    choice_help.feature('setup-plugins', lang=lang)
    voice_stat = voice_status(profile_home)
    kat_stat = kat(profile_home, "status")
    print("\n[2/4] Plugin & Addon Hermes:")
    print(f"  - KAT-Coder saat ini : {kat_stat.get('mode', 'skip')} ({kat_stat.get('status', 'not configured')})")
    print(f"  - OmniVoice runtime  : {'terverifikasi' if voice_stat.get('synthesis_verified') else 'belum diverifikasi (opsional via msshi voice)'}")

    kat_modes = {"1": "light", "2": "ideal", "3": "cloud", "4": "skip"}
    req_kat = getattr(args, 'kat_mode', None)
    req_stage_trim = bool(getattr(args, 'stage_auto_trim', False))
    req_steel = bool(getattr(args, 'install_steel', False))
    if req_steel:
        print("  --install-steel sudah dihentikan; tidak ada plugin/browser/akun yang dipasang. Pilih browser pada langkah 3.")
    pick = "5"
    kat_choice = req_kat
    stage_trim = True  # MSSHITrim is standard for new native profiles; explicit disables remain preserved.
    run_dream = False
    enable_voice = False

    if req_kat or req_stage_trim or req_steel:
        pick = "cli"
    elif yes:
        pick = "yes-default"
    else:
        print("  MSSHITrim otomatis: JSON tool besar dipadatkan lokal; runtime terpin, tanpa proxy/model/API calls.")
        print("  1. Siapkan/verifikasi MSSHITrim saja; pertahankan addon lain (Rekomendasi)")
        print("  2. Atur endpoint KAT-Coder opsional + input key privat; model utama tetap")
        print("  3. Siapkan auto-trim, buat laporan Dreaming lokal SEKALI, dan aktifkan OmniVoice jika sudah terverifikasi")
        print("     Dreaming tidak otomatis dijadwalkan. Jadwal opsional: msshi dream --register (Windows, 03.00 WIB).")
        print("  4. Atur browser pilihan pada langkah berikutnya (tanpa login otomatis)")
        print("  5. Pertahankan addon opsional; MSSHITrim standar tetap disiapkan")
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
            stage_trim = True
        elif pick == "3":
            stage_trim = True
            run_dream = True
            enable_voice = True
        elif pick == "4":
            pass  # Browser selection happens in step 3; no addon is installed here.

    kat_result = kat(profile_home, kat_choice, interactive=False if yes else None) if kat_choice is not None else kat_stat
    print("  KAT:", json.dumps(kat_result, ensure_ascii=False))
    if stage_trim:
        trim_result = _stage_auto_trim_plugin(profile_home, target, mode, selections)
        print(f"  MSSHITrim: profil {trim_result['profiles']} (fail-open, runtime_terverifikasi={trim_result['llmtrim_binary']}).")
        details = trim_result.get('details', {})
        if details.get('binary', {}).get('status', '').startswith('pending_'):
            print(f"  Runtime belum siap: {details['binary']['status']}; plugin menunggu, setup lain tetap berjalan.")
        if details.get('download_pending'):
            print("  Unduhan runtime tertunda; ulangi: msshi trim --install --apply --download-runtime")
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

    steel_result = {"status": "retired", "installed": False, "credentials_touched": False}

    choice_help.feature('artcraft', lang=lang)
    interaction_result = {"status": "skipped_non_team_mode", "model_calls": 0}
    if mode in PRESET_MODES and profile_home is not None:
        choice_help.feature('interaction', lang=lang)
        from msshi_interaction import install_existing
        interaction_result = install_existing(profile_home, ROOT, apply=True)
        print("  Interaksi dua tipe:", json.dumps(interaction_result, ensure_ascii=False))
    return {
        "choice": pick,
        "kat": kat_result,
        "auto_trim": trim_result,
        "dreaming": dream_result,
        "omnivoice": voice_result,
        "steel_policy": steel_result,
        "interaction": interaction_result,
    }


def _setup_service_connections(args, platform, profile_home, lang, yes):
    """Step [3/4]: User-selected browser labels only; never install external services."""
    if platform != "hermes":
        print(f"\n[3/4] Pilihan browser: dilewati untuk platform '{platform}'.")
        return {"status": "skipped", "reason": f"platform={platform}", "external_services_installed": False}
    import msshi_browser_preferences as browser_preferences
    if getattr(args, 'connect_services', None):
        print("  --connect-services sudah dihentikan. Tidak ada layanan/OAuth yang dipasang atau dibagikan.")
    saved = browser_preferences.current(profile_home)
    choice = getattr(args, 'setup_browser', None)
    profile_label = getattr(args, 'browser_profile_label', '') or ''
    account_label = getattr(args, 'browser_account_label', '') or ''
    print("\n[3/4] Pilih browser dan label akun yang ingin digunakan:")
    print("  Ini menyimpan pilihan saja. Tidak membuka browser, login, menyalin cookie, atau membaca akun.")
    if choice is None and yes:
        if profile_label or account_label:
            raise ValueError("Label profil/akun memerlukan --browser.")
        return {**saved, "changed": False, "external_services_installed": False}
    if choice is None:
        print("  1. Google Chrome")
        print("  2. Microsoft Edge")
        print("  3. Mozilla Firefox")
        print("  4. Tidak memilih browser sekarang")
        options = {"1": "chrome", "2": "edge", "3": "firefox", "4": "none"}
        default_pick = next((key for key, value in options.items() if value == saved.get('browser')), "4")
        pick = _prompt_choice(f"Pilihan Browser [{default_pick}]: ", default_pick)
        if pick not in options:
            raise ValueError("Pilihan browser harus 1-4.")
        choice = options[pick]
        if choice != 'none':
            profile_label = _prompt_choice("Label profil browser (boleh kosong, bukan lokasi cookie): ", "")
            account_label = _prompt_choice("Label akun untuk login manual (boleh kosong, bukan password): ", "")
    result = browser_preferences.select(profile_home, choice, profile_label, account_label)
    print(f"  Browser pilihan: {choice}; akun/login belum diverifikasi dan tidak dipindahkan.")
    return {**result, "external_services_installed": False}


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
              f"browser-login=manual")
        print(f"Pilihan Browser : {services_info.get('browser') or 'belum dipilih'} ({services_info.get('status', 'skipped')}; login manual)")
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
    mode_home = (hermes_profiles.resolve_target_hermes_home(Path(args.target_dir))
                 if getattr(args, 'platform', None) == 'hermes' and getattr(args, 'target_dir', None) and Path(args.target_dir).name.lower() in {'profiles', 'skills'}
                 else hermes_profiles.resolve_hermes_home())
    current_mode = academic.existing_mode(mode_home, state)
    default_mode = current_mode or 'academic-mahasiswa'
    if requested_mode:
        mode = academic.canonical(requested_mode)
    elif yes:
        mode = default_mode
        print(f"Mode: {mode} ({'pilihan instalasi lama dipertahankan' if current_mode else 'default instalasi baru'}).")
    else:
        for index, mode_name in enumerate(MODES, 1):
            print(f"{index}. {mode_name} - {choice_help.describe('modes', mode_name, lang=lang)}")
        default_pick = str(MODES.index(default_mode) + 1)
        pick = _prompt_choice(f"Mode [{default_pick}]: ", default_pick)
        if pick not in {str(i) for i in range(1, len(MODES) + 1)}:
            raise ValueError(f"Mode harus 1 sampai {len(MODES)}.")
        mode = MODES[int(pick) - 1]
    team = mode in TEAM_MODES
    platform, target = choose_targets(home, args.platform, args.target_dir, team, lang, yes=yes)
    print('Instruksi skill, aplikasi, runtime, model, dan akun dipasang terpisah; opsi dapat ditambahkan nanti.'
          if lang == 'id' else 'Skill instructions, apps, runtimes, models and accounts are separate; skipped options can be added later.')
    data, catalog, packs = installer.read_matrix(ROOT / MATRIX)
    if mode in academic.MODES:
        data = academic.preset_matrix(data, mode, ROOT)
        academic_values = academic.setup_profile(args, mode, prompt=None if yes else _prompt_choice)
    else:
        academic_values = None
    command = ["--mode", mode, "--platform", platform, "--target-dir", str(target)]
    if mode in academic.MODES:
        for field, value in (academic_values or {}).items():
            if value:
                command.extend(('--' + field.replace('_', '-'), value))
        if getattr(args, 'academic_project', None):
            command.extend(('--academic-project', str(args.academic_project)))
    default_bot_mode = getattr(args, 'default_bot', 'auto')
    hermes_root_dir = (hermes_profiles.resolve_target_hermes_home(target)
                       if platform == "hermes" and target.name.lower() == "profiles" else None)
    yukino_is_default = bool(mode in PRESET_MODES and hermes_root_dir is not None and
                            hermes_profiles.resolve_default_bot(hermes_root_dir, default_bot_mode) == "yukino")
    if platform == "hermes" and mode in PRESET_MODES and default_bot_mode != "auto":
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
    state["setup_mode"] = mode
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
            if mode in academic.MODES:
                academic.install_project(profile_home, mode, ROOT, academic_values,
                                         explicit=getattr(args, 'academic_project', None))
            migrate_runtime(ROOT, profile_home)
    skills_report = _setup_extra_skills_and_optional(
        args, mode, platform, target, catalog, packs, selections, home, state, lang, yes, profile_home=profile_home,
    )
    plugins_report = _setup_plugins_and_addons(args, mode, platform, target, selections, profile_home, lang, yes)
    services_report = _setup_service_connections(args, platform, profile_home, lang, yes)
    apps_report = _setup_bot_app_connections(args, mode, platform, target, selections, profile_home, home, lang, yes)
    resource_report = {"profile": "normal", "applied": False}
    if platform == "hermes" and profile_home is not None:
        import msshi_light as light_mod
        import msshi_skill_index as skill_index
        requested_rp = "light" if getattr(args, "low_ram", False) else getattr(args, "resource_profile", None)
        current_rp = light_mod.read_resource_profile(profile_home)
        if requested_rp:
            resource_report = light_mod.apply_resource_profile(profile_home, requested_rp, apply=True, source=ROOT)
            print(f"  Mode Resource   : {resource_report['profile']} (provider/model tidak diubah).")
        elif not yes:
            hw = light_mod.hardware_profile(source=ROOT)
            default_pick = "2" if (current_rp.get("profile") == "light" or (not current_rp.get("configured") and hw.get("low_ram_detected"))) else "1"
            print("\n[5/5] Mode Resource Perangkat (Standar vs Mode Hemat Windows 10 RAM 4 GB):" if lang == "id"
                  else "\n[5/5] Device Resource Profile (Standard vs Windows 10 4 GB Low-RAM Mode):")
            print(f"  RAM terdeteksi  : {hw.get('physical_gib')} GiB (rekomendasi: {'Mode Hemat' if hw.get('low_ram_detected') else 'Standar'})")
            print("  1. Standar (Normal — seluruh fitur & paralelisme aktif)" if lang == "id"
                  else "  1. Standard (Normal — all features & parallel workflows enabled)")
            print("  2. Mode Hemat Windows 10 RAM 4 GB (Low-RAM <= 150 MB, single active runtime, hemat memori)" if lang == "id"
                  else "  2. Windows 10 4 GB Low-RAM Mode (<= 150 MB budget, single active runtime, low memory)")
            rp_pick = _prompt_choice(f"Pilihan Mode Resource [1/2, Enter={default_pick}]: ", default_pick)
            if rp_pick not in {"1", "2"}:
                raise ValueError("Pilihan Mode Resource harus 1 atau 2.")
            chosen_rp = "light" if rp_pick == "2" else "normal"
            if chosen_rp == "light" or current_rp.get("configured"):
                if chosen_rp != current_rp.get("profile") or not current_rp.get("configured"):
                    resource_report = light_mod.apply_resource_profile(profile_home, chosen_rp, apply=True, source=ROOT)
                    print(f"  Mode Resource   : {resource_report['profile']} (provider/model tidak diubah).")
                else:
                    resource_report = {"profile": chosen_rp, "applied": False, "configured": True}
            else:
                resource_report = {"profile": "normal", "applied": False, "configured": False}
        else:
            resource_report = {"profile": current_rp.get("profile", "normal"), "applied": False, "configured": current_rp.get("configured", False)}
        if getattr(args, "with_learnloop", False) or getattr(args, "with_codecoach", False):
            import msshi_learn as learn_mod
            if getattr(args, "with_learnloop", False):
                print("LearnLoop (AGPL-3.0 opt-in):", json.dumps(learn_mod.install_learnloop(profile_home), ensure_ascii=False))
            if getattr(args, "with_codecoach", False):
                print("CodeCoach (MIT opt-in):", json.dumps(learn_mod.install_codecoach(profile_home), ensure_ascii=False))
        try:
            skill_index.scan_all_profiles(profile_home, write_cache=True, source=ROOT)
        except (OSError, ValueError):
            pass
    _emit_setup_report(
        home, mode, platform, target, profile_home,
        {
            "default_bot": ("yukino" if yukino_is_default else ("keep-hermes" if mode in PRESET_MODES and platform == "hermes" else "default")),
            "resource_profile": resource_report,
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
    from msshi_interaction import install_existing
    interaction = install_existing(candidate, source, apply=True)
    if interaction.get('files_planned'):
        print('Interaction plugin:', json.dumps(interaction, ensure_ascii=False))
    if (source / "hermes_plugins/msshi-auto-trim/plugin.yaml").is_file():
        import msshi_trim_setup as trim_setup
        try:
            trim_setup.install(candidate, source_root=source, apply=True, allow_download=False)
        except (OSError, ValueError, subprocess.SubprocessError):
            pass
    # Browser/account selection is declarative. Updates never reinstall a cloud browser.
    return 0


def update(args, home, state, source, commit):
    current = release_version(ROOT)
    _, catalog, _ = validate_release(source, current)
    light_mode = bool(getattr(args, "light", False) or (source / "configs" / "light_build_active.json").is_file())
    release_id = stage_release(source, home, build_profile="light" if light_mode else "full")
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
    if explicit_pdf or (has_manual_catalog and not light_mode and not getattr(args, "no_pdf", False)):
        from msshi_manuals import prompt_manual_download
        prompt_manual_download(args, source_root=source)
    if args.skip_upstreams or light_mode:
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
    updater.add_argument("--light", action="store_true", help="Stage Light Build ringan (<= 50 MB) tanpa aset berat, PDF otomatis, dan upstream cache.")
    updater.add_argument("--hermes-home", type=Path, help="Folder Hermes untuk migrasi v3.")
    updater.add_argument("--source", type=Path, help="Pakai kandidat lokal yang sudah diperiksa.")
    updater.add_argument("--download-pdf", action="store_true", help="Unduh Buku Panduan PDF lengkap untuk versi ini.")
    updater.add_argument("--no-pdf", action="store_true", help="Lewati penyalinan otomatis panduan PDF.")
    updater.add_argument("--pdf-version", help="Versi PDF panduan yang diunduh (latest, v3.1.0, v3.0).")
    updater.add_argument("--pdf-dest", type=Path, help="Folder tujuan simpan PDF panduan.")
    for verb in ("runtime", "integrations", "desktop", "audit", "doctor", "light", "system", "find", "ossu", "learn", "upstreams", "skripsi", "assets", "compact", "browser", "trim", "interaction", "forge", "managed", "services", "timesfm", "brag", "scrapling", "harness2", "optional", "rea", "studio", "choices", "manual"):
        descriptions = {
            'runtime': 'Migrasi profil dan jalankan alat sesuai tiket tugas.',
            'integrations': 'Siapkan integrasi opsional dengan prasyarat terpisah.',
            'desktop': 'Status dan peluncur Hermes Desktop.',
            'audit': 'Periksa paket/profil dan bukti tanpa chat LLM.',
            'doctor': 'Cek kesehatan sistem, Drive C:/D:, dependensi skripsi & paritas MSSHI.',
            'light': 'Light Build Win10 RAM 4 GB: status, mode Low-RAM, indeks skill lazy, paket <= 50 MB, benchmark.',
            'system': 'Sistem Interaksi Cerdas 4 Pilar: status, rute hemat token, dan siklus riset/prediksi/Harness2.',
            'find': 'Cari skill otomatis lintas bot aktif, bot spesialis, sumber terhubung, dan brankas arsip (0 panggilan LLM; baca 1 SKILL.md on-demand).',
            'ossu': 'Koneksi Universitas Computer Science Open-Source OSSU (roadmap, daftar kuliah, buka materi dasar CS).',
            'learn': 'Mode Belajar Pemula Total: status, rekomendasi topik tanpa /command, dan pasang plugin belajar (Chalk/LearnLoop/CodeCoach).',
            'upstreams': 'Cek update GitHub upstream tanpa pasang otomatis (read-only), audit Caveman/Ponytail, dan pasang Ponytail.',
            'skripsi': 'Rakit template skripsi Word (.docx) drag-and-drop via MuZA Skripsi v1.1.',
            'assets': 'Cari bahan persona pribadi di lokasi yang dipilih.',
            'compact': 'Padatkan data internal sesuai format yang didukung.',
            'browser': 'Simpan pilihan browser dan label akun; login manual, tanpa transfer cookie.',
            'trim': 'Ringkas JSON yang memenuhi syarat tanpa kehilangan nilai.',
            'interaction': 'Status/protokol dua tipe bot dan pemasangan plugin lokal tanpa panggilan model.',
            'forge': 'Tinjau roster dan rancang profil baru; model dan akun dipilih pengguna.',
            'managed': 'Kelola pembaruan salinan skill yang cocok dengan fingerprint.',
            'services': 'Kompatibilitas lama; koneksi layanan diatur sendiri oleh pengguna.',
            'timesfm': 'Peramalan deret waktu lokal; runtime/model terpisah.',
            'brag': 'Konsep dan video HTML/MP4; runtime dan aset terpisah.',
            'scrapling': 'Ekstrak CSS/XPath dari HTML lokal tanpa crawler jaringan.',
            'harness2': 'Demo deterministik dan proposal eksperimen harness.',
            'optional': 'Lihat atau pasang opsi tambahan; default OFF.',
            'rea': 'Analisis statis JavaScript/arsip; opsi Coder, runtime terpisah.',
            'studio': 'Status & rencana kolaborasi opsional Imagination Studio (Kiki-Chii / Filmmaker; 0 panggilan LLM).',
            'choices': 'Baca fungsi dan prasyarat setiap pilihan tanpa memasang apa pun.',
            'manual': 'Lihat atau unduh Buku Panduan PDF Lengkap per versi.',
        }
        command = subparsers.add_parser(verb, add_help=False, help=descriptions[verb])
        command.add_argument("arguments", nargs=argparse.REMAINDER)
    for verb in ("dream", "voice", "kat", "coder"):
        command = subparsers.add_parser(verb, add_help=False, help={
            'dream': 'Proposal pelajaran lokal untuk ditinjau, bukan promosi memori otomatis.',
            'voice': 'Status/setup OmniVoice lokal untuk audio yang diminta.',
            'kat': 'Wizard opsional KAT untuk Coder; masukkan endpoint dan key secara privat.',
            'coder': 'Status, preset, dan setup endpoint KAT opsional khusus Shikaku.',
        }[verb])
        command.add_argument("arguments", nargs=argparse.REMAINDER)
    for action in ("setup", "select"):
        wizard = subparsers.add_parser(action, help="Pilih Academic, MuZA, Solo, Custom Multi-Bot, atau Selective." if action == "setup" else "Pilih skill atau paket.")
        wizard.add_argument("--platform", choices=PLATFORMS)
        wizard.add_argument("--target-dir", type=Path)
        wizard.add_argument("--lang", choices=('id', 'en'), default='id', help="Bahasa penjelasan pilihan (id/en); format input tetap sama.")
        if action == "setup":
            wizard.add_argument("--mode", choices=(*MODES, academic.ALIAS), help="Pilih mode langsung tanpa prompt.")
            wizard.add_argument("--yes", "-y", action="store_true", help="Konfirmasi otomatis tanpa prompt.")
            wizard.add_argument("--default-bot", choices=("auto", "yukino", "keep-hermes"), default="auto", help="auto: baru = default Yukino + 4 spesialis; existing dipertahankan. yukino: ubah default tanpa memindahkan model/chat. keep-hermes: default netral + 5 profil bernama.")
            wizard.add_argument("--extra-packs", nargs="+", help="Tambahkan extra packs di langkah [1/4] Skills.")
            wizard.add_argument("--extra-skills", nargs="+", help="Tambahkan extra skill slugs di langkah [1/4] Skills.")
            wizard.add_argument("--kat-mode", choices=("light", "ideal", "cloud", "skip"), help="Buka wizard endpoint KAT khusus Coder (light/ideal/cloud alias kompatibilitas); skip menonaktifkan KAT saja. Tidak mengunduh model.")
            wizard.add_argument("--stage-auto-trim", action="store_true", help="Stage plugin fail-open msshi-auto-trim ke profil Hermes di langkah [2/4] Plugin.")
            wizard.add_argument("--install-steel", action="store_true", help="Deprecated: diterima sebagai no-op; tidak memasang Steel.")
            wizard.add_argument("--connect-services", choices=("skip", "per-profile", "share-oauth"), help="Deprecated: no-op; layanan eksternal dihubungkan sendiri oleh pengguna.")
            academic.add_arguments(wizard)
            wizard.add_argument("--browser", dest="setup_browser", choices=("chrome", "edge", "firefox", "none"), help="Simpan pilihan browser; tidak membuka browser atau login.")
            wizard.add_argument("--browser-profile-label", default="", help="Label profil browser saja; cookie dan direktori profil tidak dibaca.")
            wizard.add_argument("--browser-account-label", default="", help="Label akun untuk login manual; jangan masukkan password/API key.")
            wizard.add_argument("--connect-apps", choices=("skip", "auto-reconnect", "select"), help="Sambungkan Bot -> CLI-Anything -> Apps di langkah [4/4].")
            wizard.add_argument("--connect-bots", help="Daftar bot (dipisah koma atau 'all') untuk langkah [4/4].")
            wizard.add_argument("--connect-targets", help="Daftar app target (dipisah koma atau 'detected') untuk langkah [4/4].")
            wizard.add_argument("--with-rea", action="store_true", help="Opt-in analisis statis JavaScript/arsip: pasang instruksi REA; runtime Node/npm dan engine native terpisah. Default OFF.")
            wizard.add_argument("--with-imagination-studio", action="store_true", help="Opt-in Imagination Studio untuk Kiki-Chii / Content Creator: pasang wrapper kolaborasi Filmmaker + Slate/Studio queue; aplikasi Studio & plugin Hermes terpisah. Default OFF.")
            wizard.add_argument("--with-learnloop", action="store_true", help="Opt-in LearnLoop (AGPL-3.0, diunduh langsung dari upstream tanpa vendoring di repo MIT) untuk Shizuka & Yukino. Default OFF di installer publik.")
            wizard.add_argument("--with-codecoach", action="store_true", help="Opt-in CodeCoach (MIT, pin upstream) untuk Shikaku & Shizuka (sandbox penuh di Linux/WSL2; laporan fallback jujur di Windows). Default OFF.")
            wizard.add_argument("--low-ram", action="store_true", help="Aktifkan mode Low-RAM (hemat memori untuk perangkat <= 6 GB RAM) tanpa mengubah provider/model.")
            wizard.add_argument("--resource-profile", choices=("auto", "light", "normal"), help="Atur profil resource (auto/light/normal) tanpa mengubah provider/model.")
            wizard.add_argument("--download-pdf", action="store_true", help="Sekalian unduh Buku Panduan PDF Lengkap untuk versi ini.")
            wizard.add_argument("--no-pdf", action="store_true", help="Lewati penyalinan otomatis panduan PDF.")
            wizard.add_argument("--pdf-version", help="Versi PDF panduan yang diunduh (latest, v3.1.0, v3.0).")
            wizard.add_argument("--pdf-dest", type=Path, help="Folder tujuan simpan PDF panduan.")
        if action == "select":
            wizard.add_argument("--local", action="store_true", help="Pilih dari rilis lokal tanpa mengakses GitHub.")
    launcher = subparsers.add_parser("bootstrap", help="Pasang launcher global dari rilis lokal.")
    launcher.add_argument("--no-path", action="store_true", help="Jangan ubah PATH user.")
    launcher.add_argument("--light", action="store_true", help="Stage Light Build ringan (<= 50 MB) tanpa aset besar atau penyalinan PDF otomatis.")
    launcher.add_argument("--no-pdf", action="store_true", help="Lewati penyalinan otomatis panduan PDF.")
    launcher.add_argument("--pdf-version", help="Pilih versi panduan; default latest.")
    launcher.add_argument("--pdf-dest", type=Path, help="Folder PDF; default Downloads/MSSHI_Manuals.")
    effective = list(sys.argv[1:] if argv is None else argv)
    passthrough = {"runtime", "integrations", "desktop", "audit", "doctor", "light", "system", "find", "ossu", "learn", "upstreams", "skripsi", "assets", "dream", "voice", "kat", "coder", "compact", "browser", "trim", "interaction", "forge", "managed", "services", "timesfm", "brag", "scrapling", "harness2", "optional", "rea", "studio", "choices", "manual"}
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
        entrypoints = {"choices": "msshi_choices.py", "manual": "msshi_manuals.py", "doctor": "msshi_doctor.py", "light": "msshi_light.py", "system": "msshi_system.py", "find": "msshi_skill_finder.py", "ossu": "msshi_ossu.py", "learn": "msshi_learn.py", "upstreams": "msshi_upstreams.py", "forge": "msshi_forge.py", "skripsi": "msshi_skripsi_drop.py", "rea": "msshi_rea.py", "studio": "msshi_imagination_studio.py", "runtime": "msshi_runtime.py", "integrations": "msshi_integrations.py",
                       "desktop": "msshi_desktop.py", "audit": "check_release_v31.py", "assets": "find_muza_assets.py",
                       "compact": "caveman_context_filter.py", "browser": "msshi_browser_preferences.py", "trim": "msshi_llmtrim.py", "interaction": "msshi_interaction.py",
                       "managed": "msshi_managed.py", "optional": "msshi_optional.py", "services": "msshi_service_connections.py", "timesfm": "msshi_timesfm.py",
                       "brag": "../skills/brag/scripts/msshi_brag.py", "scrapling": "msshi_scrapling.py", "harness2": "msshi_harness2.py",
                       "dream": "msshi_integrations.py", "voice": "msshi_integrations.py", "kat": "msshi_integrations.py", "coder": "msshi_coder_helpers.py"}
        if args.command == "services":
            print(json.dumps({"status": "manual_user_setup", "changed": False,
                "message": "Automatic external-service setup has been retired. Connect the service yourself in Hermes when needed.",
                "credentials_read_or_written": False, "network_requests": 0}, indent=2))
            return 0
        if args.command in entrypoints:
            prefix = [args.command] if args.command in {"dream", "voice", "kat"} else []
            result = subprocess.call([sys.executable, "-B", "-X", "utf8", str(ROOT / "scripts" / entrypoints[args.command]),
                                      *prefix, *args.arguments])
            if result == 0 and args.command == 'runtime' and '--help' not in args.arguments:
                runtime_args = list(args.arguments)
                runtime_home = None
                if '--home' in runtime_args:
                    position = runtime_args.index('--home')
                    if position + 1 < len(runtime_args):
                        runtime_home = runtime_args[position + 1]
                        del runtime_args[position:position + 2]
                if runtime_args[:1] == ['migrate']:
                    from msshi_interaction import install_existing
                    install_existing(hermes_profiles.resolve_hermes_home(runtime_home), ROOT, apply=True)
            return result
        with locked(home):
            state = read_state(home)
            if args.command == "bootstrap":
                current = active_script(home)
                validate_release(ROOT, release_version(current.parents[1] if current else ROOT))
                migration = migrate_runtime(ROOT)
                if migration:
                    return migration
                light_boot = bool(getattr(args, "light", False) or (ROOT / "configs" / "light_build_active.json").is_file())
                bootstrap(home, stage_release(ROOT, home, build_profile="light" if light_boot else "full"), state, args.no_path)
                if not light_boot or getattr(args, "pdf_version", None):
                    from msshi_manuals import prompt_manual_download
                    prompt_manual_download(args, source_root=ROOT)
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
