"""Interactive setup and guarded updates for the public MSSHI package."""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
import hashlib
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
                "business-sage", ".claude-plugin", "hermes_plugins", "optional")
RELEASE_FILES = ("VERSION.json", "CHANGELOG.md", "README.md", "README_EN.md",
                 "LICENSE", "SKILL.md", "install.ps1", "install.sh", "package.json",
                 "THIRD_PARTY_NOTICES.md", "CREDITS.md", "UPDATE_OTOMATIS_KE_V3.bat", "MULAI_DI_SINI_PEMULA.bat")


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


def choose_targets(home, platform=None, target_dir=None, team=False, lang='id'):
    if not platform:
        detected, _ = installer.detect_host("auto")
        for name in PLATFORMS:
            print(f"  {name}: {choice_help.describe('platforms', name, lang=lang)}")
        platform = (input(f"Platform [{'/'.join(PLATFORMS)}] ({detected}): ").strip()
                    or detected)
    if platform not in PLATFORMS:
        raise ValueError(f"Platform tidak dikenal: {platform}")
    print(f"{platform}: {choice_help.describe('platforms', platform, lang=lang)}")
    _, detected = installer.detect_host(platform)
    default = (Path.cwd() / "msshi-agents" if team else detected or Path.cwd() / "msshi-skills")
    if not target_dir:
        target_dir = input(f"Folder {'workspace tim' if team else 'skills'} [{default}]: ").strip() or default
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


def setup(args, home, state):
    lang = getattr(args, 'lang', 'id')
    for index, mode_name in enumerate(MODES, 1):
        print(f"{index}. {mode_name} - {choice_help.describe('modes', mode_name, lang=lang)}")
    pick = input("Mode [1]: ").strip() or "1"
    if pick not in {"1", "2", "3", "4"}:
        raise ValueError("Mode harus 1, 2, 3, atau 4.")
    mode = MODES[int(pick) - 1]
    team = mode in {"custom-bots", "muza-preset"}
    platform, target = choose_targets(home, args.platform, args.target_dir, team, lang)
    print('Instruksi skill, aplikasi, runtime, model, dan akun dipasang terpisah; opsi dapat ditambahkan nanti.'
          if lang == 'id' else 'Skill instructions, apps, runtimes, models and accounts are separate; skipped options can be added later.')
    data, catalog, packs = installer.read_matrix(ROOT / MATRIX)
    command = ["--mode", mode, "--platform", platform, "--target-dir", str(target)]
    selections = {}
    with TemporaryDirectory(prefix=".msshi-stage-", dir=home) as scratch:
        if mode == "custom-bots":
            data = custom_matrix(data, catalog, lang)
        elif mode == "muza-preset":
            choice_help.feature('custom-display-names', lang=lang)
            if input("Custom display names? [y/N]: ").strip().lower() in {"y", "yes", "ya"}:
                data = {**data, "bots": [{**bot, "label": input(f"{bot['label']} [{bot['id']}]: ").strip() or bot["label"]}
                                        for bot in data["bots"]]}
        if team:
            matrix = Path(scratch) / "matrix.json"
            write_json(matrix, data)
            command.extend(("--matrix", str(matrix)))
        if team:
            for bot_id, _, skills, _ in installer.team_plan(data, mode, catalog):
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
        if not confirmed():
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
    if platform == "hermes":
        choice_help.feature('kat', lang=lang)
        for index, name in enumerate(('kat-light', 'kat-ideal', 'kat-cloud', 'kat-skip'), 1):
            print(f"{index}. {choice_help.describe('features', name, lang=lang)}")
        choice = input("Pilihan KAT [4]: ").strip() or "4"
        modes = {"1": "light", "2": "ideal", "3": "cloud", "4": "skip"}
        if choice not in modes:
            raise ValueError("Pilihan KAT harus 1-4.")
        from msshi_integrations import kat
        profile_home = Path(os.environ.get("HERMES_HOME") or Path.home() / ".hermes").absolute()
        print(json.dumps(kat(profile_home, modes[choice]), ensure_ascii=False, indent=2))
        choice_help.feature('artcraft', lang=lang)
    with_rea = getattr(args, 'with_rea', False)
    choice_help.feature('rea', lang=lang)
    if not with_rea and sys.stdin.isatty():
        try:
            with_rea = input("Pasang wrapper REA opsional (runtime terpisah)? [y/N]: ").strip().lower() in {"y", "yes", "ya"}
        except EOFError:
            with_rea = False
    if with_rea:
        from msshi_optional import enable, setup_targets
        for folder in setup_targets(mode, selections, source=ROOT):
            print(json.dumps(enable('rea', folder, source=ROOT, home=home), ensure_ascii=False, indent=2))
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
    candidate = Path(hermes_home or os.environ.get("HERMES_HOME") or Path.home() / ".hermes").absolute()
    if not (candidate / "config.yaml").is_file():
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
    candidate = Path(getattr(args, 'hermes_home', None) or os.environ.get("HERMES_HOME") or Path.home() / ".hermes").absolute()
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
    for verb in ("runtime", "integrations", "desktop", "audit", "assets", "compact", "browser", "trim", "managed", "services", "timesfm", "brag", "scrapling", "harness2", "optional", "rea", "choices", "manual"):
        descriptions = {
            'runtime': 'Migrasi profil dan jalankan alat sesuai tiket tugas.',
            'integrations': 'Siapkan integrasi opsional dengan prasyarat terpisah.',
            'desktop': 'Status dan peluncur Hermes Desktop.',
            'audit': 'Periksa paket/profil dan bukti tanpa chat LLM.',
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
    passthrough = {"runtime", "integrations", "desktop", "audit", "assets", "dream", "voice", "kat", "compact", "browser", "trim", "managed", "services", "timesfm", "brag", "scrapling", "harness2", "optional", "rea", "choices", "manual"}
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
        entrypoints = {"choices": "msshi_choices.py", "manual": "msshi_manuals.py", "rea": "msshi_rea.py", "runtime": "msshi_runtime.py", "integrations": "msshi_integrations.py",
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
