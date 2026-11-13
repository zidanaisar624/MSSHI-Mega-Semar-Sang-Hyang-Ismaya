"""Plan and maintain a lazy per-profile CLI-Anything route registry."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

# Load the sibling by filename so copied skills also work in deep Windows profiles.
runtime_path = Path(__file__).with_name("msshi_bridge_runtime.py")
runtime_spec = importlib.util.spec_from_file_location("msshi_bridge_runtime", runtime_path)
hub = importlib.util.module_from_spec(runtime_spec)
runtime_spec.loader.exec_module(hub)


PROFILE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}")
CONNECTOR = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}")
STATE_FILE = "connections.json"
LIMIT_BYTES = 8 * 1024 * 1024
MCP_FILES = ("mcp_config.json", "mcp.json", ".mcp.json", "config.yaml")


def help_language():
    """Keep copied skill help usable without global MSSHI modules."""
    value = os.environ.get("MSSHI_LANG") or os.environ.get("LANG", "id")
    return "en" if value.lower().startswith("en") else "id"


def connection_help():
    path = Path(__file__).with_name("connection_help.json")
    try:
        if path.stat().st_size > 256 * 1024:
            return {}
        document = json.loads(path.read_text(encoding="utf-8-sig"))
        return document if isinstance(document, dict) and document.get("schema_version") == 1 else {}
    except (OSError, ValueError, RecursionError):
        # Older standalone copies may not have the new, optional help resource.
        return {}


def description(key, section="targets"):
    """Describe choices only; never probe, launch, or change a route."""
    document, language = connection_help(), help_language()
    entries = document.get(section, {})
    entry = entries.get(key, {}) if isinstance(entries, dict) else {}
    if not entry and section == "targets":
        kind = "mcp" if key.startswith("mcp:") else "cli_extension" if hub.GENERIC_CLI.fullmatch(key) else "unknown"
        fallbacks = document.get("fallbacks", {})
        entry = fallbacks.get(kind, {}) if isinstance(fallbacks, dict) else {}
    text = entry.get(language) or entry.get("id") if isinstance(entry, dict) else None
    if not isinstance(text, str) or not text.strip():
        text = ("Route registration only; apps, runtimes, authentication and permissions are separate. No tool is executed."
                if language == "en" else
                "Hanya registrasi rute; aplikasi, runtime, autentikasi, dan izin diperiksa terpisah. Tidak menjalankan alat.")
    return " ".join(text.split())


def absolute(path):
    return Path(os.path.abspath(Path(path).expanduser()))


def data_root():
    if value := os.environ.get("MSSHI_HOME"):
        return absolute(value)
    home = Path.home()
    if os.name == "nt":
        return absolute(os.environ.get("LOCALAPPDATA") or home / "AppData" / "Local") / "MSSHI"
    return absolute(os.environ.get("XDG_DATA_HOME") or home / ".local" / "share") / "msshi"


def selected_profile(hermes_home=None, profile=None):
    if profile is not None and not PROFILE.fullmatch(profile):
        raise ValueError("Nama profil Hermes tidak valid.")
    if hermes_home is not None:
        base = absolute(hermes_home)
    elif value := os.environ.get("HERMES_HOME"):
        base = absolute(value)
    else:
        user = Path.home()
        default = user / ".hermes"
        candidates = (default, user / "HermesData", *((Path("D:/HermesData"),) if os.name == "nt" else ()))
        base = next((candidate for candidate in candidates
                     if any((candidate / filename).is_file() for filename in MCP_FILES)), default)
    if not profile:
        return base
    if base.parent.name.lower() == "profiles":
        if base.name.casefold() == profile.casefold():
            return base
        base = base.parent.parent
    return base if profile.lower() == "default" else base / "profiles" / profile


def destination_for(profile_home, default_state_dir=None, state_dir=None):
    if state_dir is None and profile_home.is_dir():
        return profile_home / "msshi-bridge" / STATE_FILE
    storage = absolute(state_dir or default_state_dir or data_root())
    identity = os.path.normcase(str(profile_home))
    key = hashlib.sha256(os.fsencode(identity)).hexdigest()[:20]
    return storage / "bridge-profiles" / key / STATE_FILE


def reject_links(path):
    for entry in (path, *path.parents):
        try:
            info = entry.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("Folder registri CLI-Anything melewati symlink atau junction.")


def read_text(path):
    with path.open(encoding="utf-8-sig") as stream:
        text = stream.read(LIMIT_BYTES + 1)
    if len(text) > LIMIT_BYTES:
        raise ValueError("File melebihi batas ukuran bridge.")
    return text


def yaml_mcp_subset(text):
    """Parse the common block-form MCP map when PyYAML is unavailable."""
    block_indent = item_indent = field_indent = None
    entries = {}
    name = None
    for raw in text.splitlines():
        trimmed = raw.strip()
        if not trimmed or trimmed.startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if block_indent is None:
            if indent != 0:
                continue
            root = re.fullmatch(r"(?:mcp_servers|mcpServers)\s*:\s*(.*?)\s*(?:#.*)?", trimmed)
            if root:
                if root[1] == "{}":
                    return entries
                if root[1]:
                    raise ValueError("MCP YAML memakai format yang memerlukan PyYAML.")
                block_indent = indent
            continue
        if indent <= block_indent:
            break
        if item_indent is None:
            item_indent = indent
        if indent == item_indent:
            item = re.fullmatch(r"""(?:"([A-Za-z0-9_.-]+)"|'([A-Za-z0-9_.-]+)'|([A-Za-z0-9_.-]+))\s*:\s*(.*?)\s*(?:#.*)?""", trimmed)
            name = next((value for value in item.groups()[:3] if value is not None), None) if item else None
            field_indent = None
            if name:
                inline = item[4]
                if inline not in {"", "{}"}:
                    entries[name] = {"enabled": False}
                else:
                    entries[name] = {}
            continue
        if name and indent > item_indent:
            if field_indent is None:
                field_indent = indent
            if indent != field_indent:
                continue
            field = re.fullmatch(r"(enabled|disabled)\s*:\s*(true|false)\s*(?:#.*)?", trimmed, re.I)
            if field:
                entries[name][field[1].lower()] = field[2].lower() == "true"
            elif re.match(r"(?:enabled|disabled)\s*:", trimmed, re.I):
                entries[name]["enabled"] = False
    return entries


def connectors(profile_home):
    result, warnings = {}, []
    for filename in MCP_FILES:
        path = profile_home / filename
        if not path.is_file():
            continue
        try:
            text = read_text(path)
            if path.suffix == ".json":
                document = json.loads(text)
            else:
                try:
                    import yaml
                except ImportError:
                    document = {"mcp_servers": yaml_mcp_subset(text)}
                else:
                    try:
                        document = yaml.safe_load(text)
                    except yaml.YAMLError as error:
                        raise ValueError("Invalid MCP YAML") from error
            if document is None:
                continue
            if not isinstance(document, dict):
                raise ValueError("Invalid MCP map")
            servers = document.get("mcp_servers", document.get("mcpServers", document.get("servers", {}) if path.suffix == ".json" else {}))
            if not isinstance(servers, dict):
                raise ValueError("Invalid MCP map")
            for name, config in servers.items():
                if isinstance(name, str) and CONNECTOR.fullmatch(name) and isinstance(config, dict):
                    result[name] = config.get("enabled", True) is True and config.get("disabled", False) is False
        except (OSError, ValueError, RecursionError):
            warnings.append(f"Nama konektor tidak dapat dibaca dari {filename}. Periksa formatnya.")
    return result, warnings


def canonical(target):
    value = target.strip().lower()
    if value.startswith("mcp:") and CONNECTOR.fullmatch(value[4:]):
        return hub.mcp_id(value[4:])
    value = hub.normalized(value)
    return hub.MCP_ALIASES.get(value, value)


def allowed_id(target):
    return bool(
        target in (*hub.WEB_TARGETS, "antigravity", "blender", *hub.ARTCRAFT, *hub.HARNESS, *hub.NATIVE,
                   "git", "gitlab", "node", "python", "graphify", "whatsapp-web", "materialcraft", "texturecraft", "hersona", "llmtrim")
        or target.startswith("mcp:") and CONNECTOR.fullmatch(target[4:])
        or hub.GENERIC_CLI.fullmatch(target)
    )


def read_registry(destination):
    reject_links(destination)
    if not destination.is_file():
        return set()
    try:
        raw = json.loads(read_text(destination))
        values = raw["targets"]
        if (raw.get("schema_version") not in {1,3} or not isinstance(values, list)
                or not all(isinstance(item, str) and allowed_id(item) and canonical(item) == item for item in values)):
            raise ValueError("Invalid route registry")
        return set(values)
    except (ValueError, TypeError, KeyError):
        raise ValueError("Format registri CLI-Anything tidak valid.") from None


def registry_bytes(registered):
    return (json.dumps({"schema_version": 1, "auto_open_on_boot": False, "targets": sorted(registered)},
                       indent=2) + "\n").encode("utf-8")


@contextlib.contextmanager
def registry_lock(destination):
    reject_links(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    lock = destination.parent / ".connections.lock"
    try:
        lock.mkdir()
    except FileExistsError:
        raise ValueError("Registri CLI-Anything sedang dipakai oleh proses lain.") from None
    try:
        yield
    finally:
        lock.rmdir()


def write_registry(destination, data):
    reject_links(destination)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".msshi-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
        os.replace(temporary, destination)
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)


def inventory(profile_home):
    declared, warnings = connectors(profile_home)
    return hub.capabilities(declared, profile_home), warnings


def current_capability(target, candidates):
    if target in candidates:
        return candidates[target]
    if hub.GENERIC_CLI.fullmatch(target):
        return {"route": "cli-anything",
                "readiness": "available" if hub.harness_executable(target) else "needs_install"}
    return {"route": "hermes-mcp", "readiness": "missing_config"}


def report(destination, registered, candidates, warnings, selected=None):
    declared_remote = {key for key,row in candidates.items() if row.get("registration_source") == "hermes-config"}
    ids = sorted(registered | declared_remote) if selected is None else selected
    schema = json.loads(read_text(destination)).get("schema_version",1) if destination.is_file() else 1
    return {
        "schema_version": schema, "auto_open_on_boot": False, "registry": str(destination),
        "connections": [{"id": key, **current_capability(key, candidates), "description": description(key),
                         "registered": (current_capability(key,candidates)["readiness"] == "configured"
                                        if key in declared_remote else key in registered)}
                        for key in ids],
        "warnings": warnings,
    }


def status(default_state_dir=None, hermes_home=None, profile=None, state_dir=None):
    home = selected_profile(hermes_home, profile)
    destination = destination_for(home, default_state_dir, state_dir)
    candidates, warnings = inventory(home)
    return report(destination, read_registry(destination), candidates, warnings)


def resolve_targets(targets, candidates, registered, remove=False):
    existing = [key for key, row in candidates.items() if row["readiness"] == "configured"]
    if remove:
        existing = [key for key in registered if current_capability(key, candidates)["route"] == "hermes-mcp"]
    selected = []
    for name in targets:
        name = canonical(name)
        if name == "artcraft":
            selected.extend(hub.ARTCRAFT)
        elif name == "existing":
            selected.extend(existing)
        elif name in candidates or hub.GENERIC_CLI.fullmatch(name) or (remove and name in registered):
            selected.append(name)
        else:
            raise ValueError("Target koneksi tidak dikenal. Lihat --catalog.")
    return set(selected)


def plan_connections(hermes_home=None, profile=None, mode="auto-reconnect", targets=None,
                     allowed_targets=None, default_state_dir=None, state_dir=None):
    home = selected_profile(hermes_home, profile)
    destination = destination_for(home, default_state_dir, state_dir)
    candidates, warnings = inventory(home)
    return planned_registration(destination, candidates, warnings, mode, targets, allowed_targets)


def planned_registration(destination, candidates, warnings, mode, targets, allowed_targets=None):
    current = read_registry(destination)
    if mode == "auto-reconnect":
        selected = {key for key, row in candidates.items()
                    if row["readiness"] in {"configured", "available", "available_web"}}
    elif mode == "select" and targets:
        selected = resolve_targets(targets, candidates, current)
    else:
        raise ValueError("Pilih mode auto-reconnect atau berikan target untuk mode select.")
    if allowed_targets is not None:
        allow = {canonical(key) for key in allowed_targets}
        if "artcraft" in allow:
            allow.update(hub.ARTCRAFT)
        if "existing" in allow:
            allow.update(key for key, row in candidates.items() if row["readiness"] == "configured")
        selected &= allow
    registered = current | selected
    result = report(destination, registered, candidates, warnings)
    result.update(added=sorted(registered - current), selected=sorted(selected))
    return destination, registry_bytes(registered), result


def emit(result, as_json):
    if as_json:
        print(json.dumps(result, indent=2))
        return
    print("CLI-Anything Universal Bridge | auto_open_on_boot: false")
    if "mode" in result:
        print(result["mode"])
    for row in result.get("connections", []):
        state = "terdaftar" if row["registered"] else "tersedia di katalog"
        print(f"  {row['id']} | {row['route']} | {row['readiness']} | {state}")
        print(f"    {row.get('description') or description(row['id'])}")
    if result.get("groups"):
        print("Kelompok pilihan: " + ", ".join(result["groups"]))
        for key in result["groups"]:
            print(f"  {key} - {description(key)}")
        print(f"CLI-Hub: {hub.CATALOG_URL}")
        print(description("registration", "notes"))
    for warning in result.get("warnings", []):
        print(f"  {warning}")


def select_menu(candidates):
    options = ["existing", "gdrive-web", "perplexity", "youtube-chrome", "tiktok", "antigravity", "artcraft",
               "blender", "blender-cli", "ffmpeg", "cli-hub"]
    options.extend(key for key in candidates if key not in options)
    for index, key in enumerate(options, 1):
        print(f" {index:>2}. {key} - {description(key)}")
    print(description("registration", "notes"))
    value = input("Masukkan nomor atau ID target, dipisah koma: ").strip()
    if not value:
        raise ValueError("Tidak ada target yang dipilih.")
    selected = []
    for entry in value.split(","):
        token = entry.strip()
        if token.isdecimal():
            number = int(token)
            if not 1 <= number <= len(options):
                raise ValueError("Nomor target di luar daftar.")
            token = options[number - 1]
        selected.append(token)
    return selected


def configure_parser(parser):
    parser.add_argument("--hermes-home", type=Path, help="Folder Hermes atau profil aktif.")
    parser.add_argument("--profile", help="Nama profil Hermes, atau default.")
    parser.add_argument("--state-dir", type=Path, help="Folder alternatif registri per profil.")
    parser.add_argument("--json", action="store_true", help="Tampilkan hasil dalam JSON.")
    parser.add_argument("--dry-run", action="store_true", help="Pratinjau perubahan tanpa menulis registri.")
    parser.add_argument("--targets", help="ID target dipisah koma untuk --mode select.")
    parser.add_argument("--query", help="Kueri web atau path workspace Antigravity saat --open.")
    parser.add_argument("--ticket", help="One-use task ticket from msshi runtime ticket.")
    operation = parser.add_mutually_exclusive_group()
    operation.add_argument("--mode", choices=("auto-reconnect", "select"), help="Pilih mode koneksi.")
    operation.add_argument("--catalog", action="store_true", help="Lihat pilihan target yang dikenal.")
    operation.add_argument("--status", action="store_true", help="Lihat rute yang terdaftar.")
    operation.add_argument("--add", metavar="TARGET", help="Daftarkan target atau grup.")
    operation.add_argument("--remove", metavar="TARGET", help="Lepas target dari registri MSSHI.")
    operation.add_argument("--open", metavar="TARGET", help="Buka rute web atau aplikasi yang terdaftar.")
    operation.add_argument("--run", metavar="TARGET", help="Jalankan rute CLI terdaftar dengan argumen setelah --.")
    parser.add_argument("command_args", nargs=argparse.REMAINDER, help=argparse.SUPPRESS)


def run(args, default_state_dir=None):
    home = selected_profile(args.hermes_home, args.profile)
    destination = destination_for(home, default_state_dir, args.state_dir)
    mode = args.mode
    targets = args.targets.split(",") if args.targets is not None else None
    if (targets is not None and mode != "select" or args.query is not None and not args.open
            or args.command_args and not args.run):
        raise ValueError("Gunakan --targets dengan mode select, --query dengan --open, dan argumen setelah -- dengan --run.")
    if args.dry_run and (args.open or args.run):
        raise ValueError("Gunakan --status untuk memeriksa rute tanpa membukanya.")
    if args.catalog or args.status:
        candidates, warnings = inventory(home)
        registered = read_registry(destination)
        rows = sorted(candidates.keys() | registered) if args.catalog else None
        result = report(destination, registered, candidates, warnings, selected=rows)
        if args.catalog:
            result.update(groups=["existing", "artcraft"], registry_catalog=hub.CATALOG_URL,
                          extension="cli:<slug> resolves cli-anything-<slug> on PATH")
        emit(result, args.json)
        return 0
    installation = home.parent.parent if home.parent.name.casefold() == "profiles" else home
    runtime_state = installation / "msshi-runtime"
    if (runtime_state / "policy.json").is_file():
        if args.open or args.run:
            if not getattr(args, "ticket", None):
                raise ValueError("MSSHI v3 requires a one-use task ticket. Use msshi runtime ticket, then msshi runtime run.")
            target = canonical(args.open or args.run).removeprefix("mcp:")
            arguments = args.command_args[1:] if args.command_args[:1] == ["--"] else args.command_args
            if args.query:
                raise ValueError("Use the registered web destination through msshi runtime run; query routing is not configured.")
            runtime = runtime_state / "runtime.py"
            if not runtime.is_file():
                raise ValueError("MSSHI v3 runtime is missing. Run msshi runtime migrate.")
            return subprocess.call([sys.executable, "-B", str(runtime), "run", "--home", str(installation),
                                    "--profile", "default" if home == installation else home.name,
                                    "--ticket", args.ticket, target, "--", *arguments])
    if args.open or args.run:
        target = canonical(args.open or args.run)
        if target not in read_registry(destination):
            raise ValueError("Daftarkan target terlebih dahulu dengan --add.")
        if args.run:
            argv = args.command_args
            if argv[:1] == ["--"]:
                argv = argv[1:]
            elif argv:
                raise ValueError("Letakkan -- sebelum argumen executable.")
            return hub.run_target(target, argv, home)
        kind = hub.open_target(target, args.query)
        result = {"mode": f"{target} dibuka lewat {kind}.", "target": target,
                  "route": kind, "auto_open_on_boot": False}
        emit(result, args.json)
        return 0
    if not (mode or args.add or args.remove):
        print("1. Auto-Reconnect Semua - " + description("auto-reconnect", "modes"))
        print("2. Pilih Connect Satu-Satu - " + description("select", "modes"))
        choice = input("Pilih 1 atau 2: ").strip()
        if choice not in {"1", "2"}:
            raise ValueError("Pilih 1 atau 2.")
        mode = "auto-reconnect" if choice == "1" else "select"
    if mode == "select" and targets is None:
        candidates, _ = inventory(home)
        targets = select_menu(candidates)
    with contextlib.nullcontext() if args.dry_run else registry_lock(destination):
        if args.remove:
            candidates, warnings = inventory(home)
            current = read_registry(destination)
            removed = resolve_targets([args.remove], candidates, current, remove=True)
            registered = current - removed
            data = registry_bytes(registered)
            result = report(destination, registered, candidates, warnings)
            result["removed"] = sorted(current - registered)
        else:
            candidates, warnings = inventory(home)
            _, data, result = planned_registration(
                destination, candidates, warnings, "select" if args.add else mode, [args.add] if args.add else targets,
            )
        if not args.dry_run:
            if (runtime_state / "policy.json").is_file():
                registry = json.loads(data)
                registry.update(schema_version=3,execution="msshi-runtime-ticket",auto_open_on_boot=False)
                data = (json.dumps(registry,indent=2)+"\n").encode("utf-8")
            write_registry(destination, data)
    result["mode"] = "Pratinjau. Registri tetap." if args.dry_run else "Registri disimpan. Semua rute on-demand."
    emit(result, args.json)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    configure_parser(parser)
    args = parser.parse_args(argv)
    try:
        return run(args)
    except (OSError, ValueError, EOFError, subprocess.SubprocessError) as error:
        parser.exit(1, f"{parser.prog}: {error}\n")
    except KeyboardInterrupt:
        parser.exit(130, f"{parser.prog}: dibatalkan.\n")


if __name__ == "__main__":
    raise SystemExit(main())
