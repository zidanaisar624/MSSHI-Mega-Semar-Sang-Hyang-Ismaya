#!/usr/bin/env python3
"""MSSHI v3 local migration and task-scoped native CLI execution.

No polling of creative applications or model API requests occurs here. Runtime
state is private to Hermes home. Tickets express an active user's task, not an
OS security boundary. Only processes launched by this dispatcher are owned.
"""
from __future__ import annotations

import argparse
import contextlib
import ctypes
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid

VERSION = "3.0.0"
DISABLED_MCP = {
    "blender", "wordcraft", "lightcraft", "cadcraft", "craftanything",
    "deckcraft", "designcraft", "effectcraft", "figcraft", "filmcraft",
    "gridcraft", "materialcraft", "pdfcraft", "photocraft", "solidcraft",
    "soundcraft", "texturecraft", "vectorcraft",
}
UTILITY_MCP = {"hersona", "llmtrim"}
MIGRATED_MCP = DISABLED_MCP | UTILITY_MCP
RETAINED_MCP = {"gitlab", "tinyfish"}
ARTCRAFT = DISABLED_MCP - {"blender"}
ROLES = {
    "default": "yukino", "yukino": "yukino", "shizuka-hiratsuka": "shizuka",
    "shizuka": "shizuka", "val": "val", "kiki-chii": "kiki-chii",
    "nyenyenye-ya-gw-coder": "shikaku", "shikaku-nara": "shikaku", "shikaku": "shikaku",
}
PROTECTED_KEYS = ("provider", "model", "providers", "fallback_providers", "display_name", "name")
SLUG = re.compile(r"^[a-z0-9][a-z0-9_-]{0,95}$")


def norm(value):
    return re.sub(r"[^a-z0-9]", "", value.lower().removeprefix("mcp:"))


def safe_path(path):
    path = Path(path).absolute()
    for item in (path, *path.parents):
        if item.is_symlink() or (item.exists() and getattr(item.lstat(), "st_file_attributes", 0) & 0x400):
            raise ValueError(f"Managed state cannot use a link: {item}")
    return path


def read_json(path, fallback=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return fallback


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def atomic(path, data):
    path = safe_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temp = Path(stream.name)
        stream.write(data)
    try:
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def sha(value):
    return hashlib.sha256(value).hexdigest()


@contextlib.contextmanager
def locked(path):
    path = safe_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    stream = path.open("a+b")
    try:
        if stream.tell() == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    except OSError as error:
        raise ValueError(f"Operation lock failed: {path}") from error
    finally:
        stream.close()


def yaml_module():
    try:
        from ruamel.yaml import YAML
        return YAML
    except ImportError:
        # Hermes' committed environment is authoritative; no dependency install.
        roots = [Path(os.environ.get("HERMES_HOME", "~/.hermes")).expanduser()]
        roots.extend(Path.home().glob(".hermes"))
        for root in roots:
            if root.parent.name == "profiles":
                root = root.parent.parent
            for facts in root.glob("installs/*/facts.json"):
                env = read_json(facts, {}).get("packages", {}).get("venv", {}).get("environment")
                if not env:
                    continue
                library = Path(env) / "Lib/site-packages"
                if not library.is_dir():
                    continue
                sys.path.insert(0, str(library))
                try:
                    from ruamel.yaml import YAML
                    return YAML
                except ImportError:
                    sys.path.remove(str(library))
        raise ValueError("ruamel.yaml is required for config migration. Run with Hermes' Python environment.")


def yaml_read(data):
    parser = yaml_module()(typ="safe")
    result = parser.load(data.decode("utf-8-sig")) or {}
    if not isinstance(result, dict):
        raise ValueError("Configuration must be a YAML mapping")
    return result


def protected(data):
    cfg = yaml_read(data)
    return sha(encoded({name: cfg[name] for name in PROTECTED_KEYS if name in cfg}))


def profiles(home):
    result = {"default": home}
    for path in sorted((home / "profiles").glob("*")):
        if path.is_dir() and not path.is_symlink() and (path / "config.yaml").is_file():
            result[path.name] = path
    return result


def hardware():
    total = 0
    available = 0
    if os.name == "nt":
        class Memory(ctypes.Structure):
            _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong),
                        *[(key, ctypes.c_ulonglong) for key in ("total", "available", "page", "free_page", "virtual", "free_virtual", "extended")]]
        record = Memory()
        record.length = ctypes.sizeof(record)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(record)):
            total, available = record.total, record.available
    elif hasattr(os, "sysconf"):
        total = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
        available = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_AVPHYS_PAGES")
    gib = total / 2**30
    tier = 1 if gib < 12 else 2 if gib < 24 else 3
    return {"tier": tier, "physical_gib": round(gib, 2), "available_gib": round(available / 2**30, 2),
            "render_workers": 1 if tier <= 2 else 2, "app_concurrency": 1,
            "browser_timeout_seconds": 90, "idle_unload_seconds": 15 if tier == 1 else 45 if tier == 2 else 60}


def executable(candidates):
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if path.is_file():
            return str(path.absolute())
        found = shutil.which(candidate)
        if found:
            return found
    return None


def native_routes(home, profile, cfg):
    previous = read_json(home / "msshi-runtime/profiles" / profile / "routes.json", {})
    routes = {name: row for name, row in previous.get("targets", {}).items()
              if norm(name) not in RETAINED_MCP}
    for route in routes.values():
        if route.get("executable") and not Path(route["executable"]).is_file():
            route["readiness"] = "optional_missing"
            route["executable"] = None
    utility_config = {norm(name): item for name, item in (cfg.get("mcp_servers") or {}).items()
                      if norm(name) in UTILITY_MCP and isinstance(item, dict)}
    old_hersona = utility_config.get("hersona", {}).get("command")
    hersona_candidates = [routes.get("hersona", {}).get("executable")]
    if old_hersona:
        former = Path(old_hersona)
        if former.name.lower() in {"hersona", "hersona.exe"}:
            hersona_candidates.append(former)
        hersona_candidates.extend([former.with_name("hersona.exe"), former.with_name("hersona")])
    hersona_candidates.append("hersona")
    hersona = executable(hersona_candidates)
    routes["hersona"] = {"kind": "native-cli", "executable": hersona,
                         "readiness": "available" if hersona else "optional_missing",
                         "prefix": ["--plain"], "catalog_only": True,
                         "env": {"PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}}
    old_trim = utility_config.get("llmtrim", {}).get("command")
    if old_trim and Path(old_trim).name.lower() not in {"llmtrim", "llmtrim.exe"}:
        old_trim = None
    trim = executable([old_trim, routes.get("llmtrim", {}).get("native_binary"),
                       home / "tools/llmtrim/llmtrim.exe", home / "tools/llmtrim/llmtrim", "llmtrim"])
    wrapper = home / "tools/msshi/msshi_llmtrim.py"
    wrapper_available = wrapper.is_file() or Path(__file__).with_name("msshi_llmtrim.py").is_file()
    routes["llmtrim"] = {"kind": "native-cli", "executable": sys.executable if trim and wrapper_available else None,
                         "native_binary": trim, "readiness": "available" if trim and wrapper_available else "optional_missing",
                         "prefix": ["-B", "-X", "utf8", str(wrapper), "--home", str(home), "--binary", trim or ""],
                         "local_only": True, "preset": "safe",
                         "env": {"PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}}
    for name, item in (cfg.get("mcp_servers") or {}).items():
        slug = norm(name)
        if slug not in DISABLED_MCP or not isinstance(item, dict):
            continue
        if slug in ARTCRAFT:
            filename = "craft-anything" if slug == "craftanything" else slug
            former = item.get("command", "")
            cli = executable([former if str(former).lower().endswith("-cli.exe") else None,
                              home / "applications" / filename / f"{filename}-cli.exe",
                              Path("D:/Program/ArtCraft Apps") / filename / f"{filename}-cli.exe",
                              f"{filename}-cli"])
            routes[slug] = {"kind": "native-cli", "executable": cli,
                            "readiness": "available" if cli else "optional_missing",
                            "env": {key: str(value) for key, value in item.get("env", {}).items()
                                    if key in {"APPDATA", "LOCALAPPDATA", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "TEMP", "TMP"}}}
        else:
            routes[slug] = {"kind": "native-cli", "executable": None,
                            "readiness": "requires_native_adapter"}
    blender = executable(["blender", r"D:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe",
                          r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"])
    routes["blender"] = {"kind": "native-cli", "executable": blender,
                          "readiness": "available" if blender else "optional_missing", "prefix": ["--background"]}
    for slug, names in {
        "ffmpeg": [home / "tools/ffmpeg-9.0.1-win32-x64/bin/ffmpeg.exe", "ffmpeg"],
        "git": ["git", home / "tools/git-2.53.0+3-win32-x64/cmd/git.exe"],
        "node": [home / "tools/node-26.12.1-win32-x64/node.exe", "node"],
        "python": [sys.executable], "gitlab": ["glab"],
        "graphify": [home / "msshi-private/graphify-runtime/venv/Scripts/graphify.exe", "graphify"],
        "antigravity": [r"D:\Program\Antigravity IDE\Antigravity IDE\Antigravity IDE.exe", "antigravity-ide", "antigravity", Path.home() / "AppData/Local/Programs/Antigravity/bin/antigravity.cmd"],
    }.items():
        command = executable(names)
        if command and Path(command).suffix.lower() in {".cmd", ".bat"}:
            if slug == "antigravity":
                base = Path(command).parent
                command = executable([base.parent / "Antigravity IDE.exe", base.parent / "Antigravity.exe", base / "Antigravity.exe"])
            else:
                command = None
        routes[slug] = {"kind": "native-cli", "executable": command,
                        "readiness": "available" if command else "optional_missing"}
        if slug == "antigravity" and command:
            cli = Path(command).parent / "resources/app/out/cli.js"
            if cli.is_file():
                routes[slug].update(prefix=[str(cli)],env={"ELECTRON_RUN_AS_NODE": "1"})
            else:
                routes[slug]["readiness"] = "requires_native_adapter"
    routes["gdrive-web"] = {"kind": "web", "readiness": "disabled", "reason": "User disabled GDrive"}
    routes["gdrive"] = {"kind": "desktop", "readiness": "disabled", "reason": "User disabled GDrive"}
    chrome = executable([r"C:\Program Files\Google\Chrome\Application\chrome.exe", "google-chrome", "chromium"])
    for name,url in {"youtube-chrome": "https://www.youtube.com/", "tiktok": "https://www.tiktok.com/",
                     "perplexity": "https://www.perplexity.ai/", "whatsapp-web": "https://web.whatsapp.com/"}.items():
        routes[name] = {"kind": "browser", "executable": chrome,
                        "readiness": "available" if chrome else "optional_missing", "url": url}
    return {"schema": 3, "profile": profile, "role": ROLES.get(profile, "custom"),
            "auto_open_on_boot": False, "require_task_ticket": True, "targets": routes}


def yaml_section(lines, key):
    first = next((i for i,line in enumerate(lines)
                  if re.match(rf"^{re.escape(key)}:\s*(?:#.*)?$", line.rstrip())), None)
    if first is None:
        return None
    last = next((i for i in range(first + 1, len(lines))
                 if re.match(r"^[^\s#][^:]*:", lines[i])), len(lines))
    return first,last


def replace_plugins(lines, plugin, newline):
    section = yaml_section(lines, "plugins")
    if section is None:
        return
    stream = io.StringIO()
    yaml_module()().dump({"plugins": plugin}, stream)
    first,last = section
    lines[first:last] = stream.getvalue().replace("\n",newline).splitlines(keepends=True)


def config_update(original, restore_from=None, auto_trim_binary=None):
    """Remove desktop/utility MCP registrations and restore retained service flags.

    Current retained URLs and credentials remain in place. Their flags are restored
    only from an original MSSHI migration backup when that backup exists.
    """
    text = original.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    newline = "\r\n" if "\r\n" in text else "\n"
    cfg = yaml_read(original)
    prior = yaml_read(restore_from) if restore_from else {}
    changed = []
    section = yaml_section(lines,"mcp_servers")
    if section is not None:
        first,end = section
        entries = [(i,re.match(r"^  ([^\s:#]+):",lines[i]).group(1))
                   for i in range(first + 1,end) if re.match(r"^  ([^\s:#]+):",lines[i])]
        for index in range(len(entries) - 1,-1,-1):
            offset,name = entries[index]
            last = entries[index+1][0] if index+1 < len(entries) else end
            if norm(name) in MIGRATED_MCP or norm(name) in {"googledrive","gdrive"}:
                lines[offset:last] = []
                changed.append(name)
                continue
            if norm(name) not in RETAINED_MCP:
                continue
            old = (prior.get("mcp_servers") or {}).get(name)
            if not isinstance(old,dict):
                continue
            chunk = lines[offset:last]
            for flag in ("enabled","lazy"):
                positions = [i for i,line in enumerate(chunk) if re.match(rf"^    {flag}:",line)]
                if flag in old:
                    value = old[flag]
                    if not isinstance(value,bool):
                        raise ValueError(f"Original remote flag needs review: {name}.{flag}")
                    replacement = f"    {flag}: {'true' if value else 'false'}{newline}"
                    if positions:
                        chunk[positions[0]] = replacement
                    else:
                        chunk.insert(1,replacement)
                else:
                    chunk = [line for line in chunk if not re.match(rf"^    {flag}:",line)]
            lines[offset:last] = chunk
    plugin = cfg.get("plugins",{})
    previous_plugins = prior.get("plugins",{})
    remove = {name for name in plugin.get("enabled",[]) if norm(name) in MIGRATED_MCP}
    remote_enabled = {name for name in previous_plugins.get("enabled",[]) if norm(name) in RETAINED_MCP}
    remote_disabled = {name for name in previous_plugins.get("disabled",[]) if norm(name) in RETAINED_MCP}
    if auto_trim_binary:
        entry_id = "msshi-auto-trim"
        entries = dict(plugin.get("entries") or {})
        entry = dict(entries.get(entry_id) or {})
        settings = dict(entry.get("settings") or {})
        for key, value in {"enabled": True, "min_chars": 2048, "max_chars": 262144, "timeout_seconds": 3.0}.items():
            settings.setdefault(key, value)
        settings["binary"] = str(auto_trim_binary)
        entry["settings"] = settings
        entries[entry_id] = entry
        plugin["entries"] = entries
        plugin["enabled"] = list(dict.fromkeys([*plugin.get("enabled", []), entry_id]))
        plugin["disabled"] = [name for name in plugin.get("disabled", []) if name != entry_id]
    if remove or remote_enabled or remote_disabled or auto_trim_binary:
        plugin["enabled"] = list(dict.fromkeys(
            [name for name in plugin.get("enabled",[]) if name not in remove and name not in remote_disabled]
            + sorted(remote_enabled)))
        plugin["disabled"] = sorted((set(plugin.get("disabled",[])) | remove | remote_disabled) - remote_enabled)
        replace_plugins(lines,plugin,newline)
    result = "".join(lines).encode("utf-8-sig" if original.startswith(b"\xef\xbb\xbf") else "utf-8")
    final = yaml_read(result)
    if any(norm(name) in MIGRATED_MCP or norm(name) in {"gdrive","googledrive"}
           for name in (final.get("mcp_servers") or {})):
        raise ValueError("Migrated desktop/utility MCP registration remains after migration")
    if protected(original) != protected(result):
        raise ValueError("Protected provider/model or display metadata changed")
    return result,sorted(changed)


def original_config(home,path):
    """Find the earliest pre-migration config without trusting unrelated paths."""
    for receipt in sorted((home/"msshi-runtime/backups").glob("*/receipt.json")):
        details = read_json(receipt,{})
        if details.get("home") != str(home):
            continue
        for row in details.get("changes",[]):
            if row.get("path") != str(path) or not row.get("backup"):
                continue
            name = row["backup"]
            if not re.fullmatch(r"\d+\.bak",name):
                raise ValueError("Unexpected backup name in migration receipt")
            data = (receipt.parent/name).read_bytes()
            if sha(data) != row["before_sha256"]:
                raise ValueError("Original config backup checksum failed")
            return data
    return None


def transaction(home, changes, protected_checks):
    root = home / "msshi-runtime"
    backup = root / "backups" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S-%fZ")
    changed = {safe_path(path): data for path, data in changes.items() if not path.is_file() or path.read_bytes() != data}
    for path, expected in protected_checks.items():
        if protected(path.read_bytes()) != expected:
            raise ValueError(f"Configuration changed during migration: {path}")
    backup.mkdir(parents=True)
    receipt = {"home": str(home), "version": VERSION, "changes": [], "provider_model_preserved": True}
    for i, (path, data) in enumerate(changed.items()):
        before = path.read_bytes() if path.is_file() else None
        saved = f"{i:04}.bak" if before is not None else None
        if saved:
            atomic(backup / saved, before)
        receipt["changes"].append({"path": str(path), "before_sha256": sha(before) if before is not None else None,
                                   "after_sha256": sha(data), "backup": saved})
    receipt_path = backup / "receipt.json"
    atomic(receipt_path, encoded(receipt))
    applied = []
    try:
        for row in receipt["changes"]:
            path = Path(row["path"])
            before = sha(path.read_bytes()) if path.is_file() else None
            if before != row["before_sha256"]:
                raise ValueError(f"Concurrent file change: {path}")
            atomic(path, changed[path])
            applied.append(row)
        for path, expected in protected_checks.items():
            if protected(path.read_bytes()) != expected:
                raise ValueError(f"Protected config changed: {path}")
    except BaseException:
        for row in reversed(applied):
            restore_row(row, backup)
        raise
    return receipt_path, len(changed)


def restore_row(row, backup):
    path = safe_path(row["path"])
    if not path.is_file() or sha(path.read_bytes()) != row["after_sha256"]:
        return False
    if row["backup"]:
        data = (backup / row["backup"]).read_bytes()
        if sha(data) != row["before_sha256"]:
            raise ValueError("Backup checksum failed")
        atomic(path, data)
    else:
        path.unlink()
    return True


def utilities_skill(home, profile):
    return f'''---
name: msshi-local-utilities
description: "Use local CLI tools to compress structured requests or inspect and draft persona attributes."
---
<!-- MSSHI managed utility route -->
# Local compression and persona tools

Llmtrim and Hersona run as short-lived local CLI processes. Their MCP registrations
are removed. Discover current readiness with `msshi runtime status --home "{home}"`.

For a supplied provider-shaped JSON payload, preserve the original and run
`msshi trim --home "{home}" --input INPUT.json --output NEW_OUTPUT.json`.
This command only compresses local data using the safe preset and never sends a
provider request. It is separate from any installed automatic token hook. Do not
claim all conversations are automatically compressed from CLI availability alone.
Do not run llmtrim setup, serve, start, wrap, send, or change model/provider/proxy settings.

Use Hersona when the user asks to inspect attributes, compare a recipe, or draft a
persona change. Create a task ticket for target hersona and profile {profile}, then
run its catalog command through `msshi runtime run`. Safe examples are `list`,
`show personality/kuudere`, `blend personality/kuudere speech/soft --compact`, and
`export personality/kuudere speech/soft --format json`. Export is a draft, not a
system instruction. Read only the requested attribute instead of the full matrix
when that is sufficient. Never use soul, persistent, decide, update, or persona
installation/switch commands through this catalog route.

The saved native Hermes personality and SOUL.md remain active without a Hersona
call on each reply. Permanent persona edits need the user's explicit request and
the existing persona helper with backup. Preserve provider/model settings.
'''.encode("utf-8")


def migrate(home):
    root = home / "msshi-runtime"
    with locked(root / ".migration-lock"):
        changes = {}
        checks = {}
        report = {"version": VERSION, "profiles": {}, "hardware": hardware(), "gdrive": "disabled",
                  "auto_open_on_boot": False, "jev_model_routing": False,
                  "artcraft_optional": True, "provider_model_preserved": True}
        wrapper_source = Path(__file__).with_name("msshi_llmtrim.py")
        if wrapper_source.is_file():
            changes[home / "tools/msshi/msshi_llmtrim.py"] = wrapper_source.read_bytes()
        legacy_hersona = home / "integrations/databyte-yupiai/skills/persona/hersona/SKILL.md"
        if legacy_hersona.is_file() and sha(legacy_hersona.read_bytes()) == "02269a237d8dca52d5f4ef90c612828f9abef004cf893a93e11ddcdcbdf5f09d":
            changes[legacy_hersona] = utilities_skill(home, "default").replace(
                b"name: msshi-local-utilities", b'name: hersona\nversion: 1.11.1-hermes.2\nauthor: "shiro-0x; Muhammad Zidan Aisar (Hermes adapter)"\nlicense: MIT').replace(
                b"# Local compression and persona tools", b"# Hersona local CLI catalog")
        here = Path(__file__).resolve().parent
        bridge_source = here if (here / "msshi_bridge_runtime.py").is_file() else here.parent / "skills/cli-anything-universal-bridge/scripts"
        plugin_source = here.parent / "hermes_plugins/msshi-auto-trim"
        plugin_names = ("__init__.py", "plugin.yaml", "README.md")
        plugin_files = {filename: (plugin_source / filename).read_bytes() for filename in plugin_names
                        if (plugin_source / filename).is_file()}
        auto_trim_available = len(plugin_files) == len(plugin_names)
        for name, profile in profiles(home).items():
            path = profile / "config.yaml"
            if not path.is_file():
                continue
            original = path.read_bytes()
            cfg = yaml_read(original)
            checks[path] = protected(original)
            routes = native_routes(home, name, cfg)
            trim_binary = routes["targets"]["llmtrim"].get("native_binary") if auto_trim_available else None
            changes[path], disabled = config_update(original, original_config(home,path), trim_binary)
            if trim_binary:
                for filename, content in plugin_files.items():
                    changes[profile / "plugins/msshi-auto-trim" / filename] = content
            changes[root / "profiles" / name / "routes.json"] = encoded(routes)
            registry = profile / "msshi-bridge/connections.json"
            old = read_json(registry, {"schema_version": 1, "targets": []})
            old.update(auto_open_on_boot=False, schema_version=3, execution="msshi-runtime-ticket",
                       targets=sorted(target for target, row in routes["targets"].items() if row["readiness"] == "available"))
            changes[registry] = encoded(old)
            old_policy = profile / "msshi-bridge/policy.json"
            changes[old_policy] = encoded({"auto_open_on_boot": False, "gdrive": "disabled",
                                           "require_task_ticket": True, "jev_model_routing": False})
            bridge = profile / "skills/cli-anything-universal-bridge/scripts"
            if bridge.is_dir():
                changes[bridge / "msshi_runtime.py"] = Path(__file__).read_bytes()
                for filename in ("msshi_bridge_runtime.py", "setup_cli_anything_hermes.py"):
                    source = bridge_source / filename
                    if source.is_file():
                        changes[bridge / filename] = source.read_bytes()
            utility_skill = profile / "skills/msshi-local-utilities/SKILL.md"
            if not utility_skill.is_file() or b"<!-- MSSHI managed utility route -->" in utility_skill.read_bytes():
                changes[utility_skill] = utilities_skill(home, name)
            report["profiles"][name] = {"home": str(profile), "role": ROLES.get(name, "custom"),
                "removed_desktop_mcp": [key for key in disabled if norm(key) in DISABLED_MCP],
                "removed_utility_mcp": [key for key in disabled if norm(key) in UTILITY_MCP],
                "automatic_trim_plugin": bool(trim_binary),
                "disabled_mcp": disabled, "native_cli_available": sorted(key for key,row in routes["targets"].items() if row["readiness"] == "available"),
                "unavailable_native_adapters": sorted(key for key,row in routes["targets"].items() if row["readiness"] == "requires_native_adapter")}
        policy = {"version": VERSION, "gdrive": "disabled", "auto_open_on_boot": False,
                  "jev_model_routing": False, "require_ai_task_ticket": True, "app_concurrency": 1,
                  "tokenshield_reserve_usd": 1.0, "paid_actions_require_confirmed_budget": True,
                  "guardian": {"mode": "owned_process_watchdog", "monitor_unknown_processes": False,
                               "incident_action": "alert_then_contain_owned_expired_job_then_report"}}
        changes[root / "policy.json"] = encoded(policy)
        report["protected_config_hashes"] = {str(path): value for path,value in checks.items()}
        changes[root / "last-migration.json"] = encoded(report)
        changes[root / "runtime.py"] = Path(__file__).read_bytes()
        inventory = {"version": VERSION, "passive_only": True, "launches_applications": False,
                     "domains": {"content_creation": [], "academic": [], "internet": [], "ai_coding": []}}
        for name,detail in report["profiles"].items():
            for target in detail["native_cli_available"]:
                domain = ("content_creation" if target in ARTCRAFT or target in {"blender","ffmpeg"} else
                          "internet" if target in {"youtube-chrome","tiktok","perplexity","whatsapp-web"} else "ai_coding")
                inventory["domains"][domain].append({"profile": name,"target": target})
        changes[root / "curiosity_ledger/inventory.json"] = encoded(inventory)
        receipt, count = transaction(home, changes, checks)
        report["rollback_receipt"] = str(receipt)
        report["files_changed"] = count
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0


def normalized_home(value):
    path = Path(value or os.environ.get("HERMES_HOME", "~/.hermes")).expanduser().absolute()
    return path.parent.parent if path.parent.name.lower() == "profiles" else path


def profile_name(value):
    value = value or os.environ.get("HERMES_PROFILE", "default")
    if not SLUG.fullmatch(value):
        raise ValueError("Invalid profile ID")
    return value


def ticket(home, profile, target, task, source, ttl):
    root = home / "msshi-runtime"
    routes = read_json(root / "profiles" / profile / "routes.json")
    if not routes or target not in routes["targets"] or routes["targets"][target]["readiness"] != "available":
        raise ValueError("Native CLI route is unavailable or disabled. Run runtime status.")
    if len(task.strip()) < 8 or not 1 <= ttl <= 3600:
        raise ValueError("Provide a specific active task and a TTL between 1 and 3600 seconds")
    identifier = uuid.uuid4().hex
    row = {"id": identifier, "profile": profile, "target": target, "source": source,
           "task_sha256": sha(task.strip().encode()), "created_at": time.time(),
           "expires_at": time.time() + ttl, "state": "pending", "max_runs": 1}
    atomic(root / "tickets" / (identifier + ".json"), encoded(row))
    atomic(root / "active_ai_task_ticket.json", encoded({"active_tickets": [row]}))
    print(identifier)
    return 0


class ProcessJob:
    """Kill-on-close Windows Job; Unix uses a private process session."""
    def __init__(self):
        self.handle = None
        if os.name == "nt":
            from ctypes import wintypes
            class Basic(ctypes.Structure):
                _fields_ = [("process_time", ctypes.c_int64), ("job_time", ctypes.c_int64),
                            ("flags", wintypes.DWORD), ("min_ws", ctypes.c_size_t), ("max_ws", ctypes.c_size_t),
                            ("active_limit", wintypes.DWORD), ("affinity", ctypes.c_size_t),
                            ("priority", wintypes.DWORD), ("scheduling", wintypes.DWORD)]
            class Counters(ctypes.Structure):
                _fields_ = [(str(i), ctypes.c_ulonglong) for i in range(6)]
            class Extended(ctypes.Structure):
                _fields_ = [("basic", Basic), ("io", Counters), ("process_mem", ctypes.c_size_t),
                            ("job_mem", ctypes.c_size_t), ("peak_process", ctypes.c_size_t), ("peak_job", ctypes.c_size_t)]
            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel.CreateJobObjectW.restype = wintypes.HANDLE
            kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
            kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
            kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
            kernel.CloseHandle.argtypes = [wintypes.HANDLE]
            self.kernel = kernel
            self.handle = kernel.CreateJobObjectW(None, None)
            info = Extended()
            info.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            if not self.handle or not kernel.SetInformationJobObject(self.handle, 9, ctypes.byref(info), ctypes.sizeof(info)):
                self.close()
                raise OSError("Cannot create managed kill-on-close job")

    def attach(self, process):
        if self.handle and not self.kernel.AssignProcessToJobObject(self.handle, process._handle):
            raise OSError("Cannot assign process to managed job")

    def close(self):
        if self.handle:
            self.kernel.CloseHandle(self.handle)
            self.handle = None


def run_target(home, profile, identifier, target, arguments, timeout):
    if not re.fullmatch(r"[a-f0-9]{32}", identifier):
        raise ValueError("A valid one-use task ticket is required")
    root = home / "msshi-runtime"
    route = read_json(root / "profiles" / profile / "routes.json", {}).get("targets", {}).get(target)
    if not route or route.get("readiness") != "available" or not route.get("executable"):
        raise ValueError("Native CLI route is unavailable or disabled")
    if any(arg.lower() == "mcp" or arg.lower().startswith("--connect") for arg in arguments):
        raise ValueError("MCP and unmanaged application connections are disabled for runtime routes")
    if target == "hersona":
        permitted = {"list", "show", "matrix", "blend", "preview", "diff", "reanchor", "export", "--help", "-h"}
        if not arguments or (arguments[0] not in permitted and arguments[:2] != ["personas", "list"]):
            raise ValueError("Hersona route permits local catalog/draft commands only; persona and provider mutation is disabled")
    if target == "llmtrim" and any(arg.split("=", 1)[0] in {"--home", "--binary"} for arg in arguments):
        raise ValueError("The local compression route cannot override its registered runtime or binary")
    command = [route["executable"], *route.get("prefix", []), *arguments]
    if route["kind"] == "browser":
        if arguments:
            raise ValueError("Web routes open only their registered destination")
        browser_state = safe_path(root / "browser-tasks" / identifier)
        command = [route["executable"], f"--user-data-dir={browser_state}", "--new-window", f"--app={route['url']}"]
    if not Path(command[0]).is_file():
        raise ValueError("Registered executable is no longer available")
    if Path(command[0]).suffix.lower() in {".cmd", ".bat"}:
        raise ValueError("This route requires a native executable adapter, not a shell shim")
    ticket_path = root / "tickets" / (identifier + ".json")
    with locked(root / "locks" / (identifier + ".lock")), locked(root / "locks/app-concurrency.lock"):
        row = read_json(ticket_path, {})
        if (row.get("profile"), row.get("target"), row.get("state")) != (profile, target, "pending") or row.get("expires_at", 0) <= time.time():
            raise ValueError("Task ticket is expired, consumed, or scoped to another route/profile")
        row["state"] = "running"
        row["execution_started_at"] = time.time()
        atomic(ticket_path, encoded(row))
        env = {**os.environ, **route.get("env", {})}
        job = None
        process = None
        code = 1
        try:
            job = ProcessJob()
            process = subprocess.Popen(command, env=env, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr,
            start_new_session=(os.name != "nt"),
            creationflags=0x08000004 if os.name == "nt" else 0)
            job.attach(process)
            if os.name == "nt":
                resume = ctypes.WinDLL("ntdll").NtResumeProcess
                resume.argtypes = [ctypes.c_void_p]
                resume.restype = ctypes.c_long
                if resume(process._handle):
                    raise OSError("Cannot resume managed child process")
            row.update(pid=process.pid, executable=str(Path(command[0]).resolve()), started_at=time.time())
            atomic(ticket_path, encoded(row))
            limit = max(1, min(timeout, row["expires_at"] - time.time()))
            code = process.wait(timeout=limit)
            return code
        except subprocess.TimeoutExpired:
            code = 124
            alert(home, {"event": "managed_task_timeout", "ticket": identifier, "profile": profile,
                         "target": target, "pid": process.pid if process else None,
                         "action": "close_owned_process_job"})
            return code
        finally:
            if os.name != "nt" and process:
                with contextlib.suppress(ProcessLookupError):
                    os.killpg(process.pid, signal.SIGTERM)
            if job:
                job.close()
            if process and process.poll() is None:
                process.kill()
                process.wait(timeout=10)
            row.update(state="finished", finished_at=time.time(), exit_code=code)
            atomic(ticket_path, encoded(row))
            atomic(root / "active_ai_task_ticket.json", encoded({"active_tickets": []}))


def alert(home, event):
    event["at"] = datetime.now(timezone.utc).isoformat()
    path = home / "msshi-runtime/alerts" / (uuid.uuid4().hex + ".json")
    atomic(path, encoded(event))


def scan_secrets(path):
    path = Path(path).absolute()
    patterns = {
        "private_key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        "github_token": re.compile(rb"\b(?:ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{40,})\b"),
        "api_token": re.compile(rb"\bsk-(?:proj-)?[A-Za-z0-9_-]{28,}\b"),
        "aws_access_key": re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    }
    findings = []
    seen = 0
    scanned = 0
    def candidates():
        if path.is_file():
            yield path
            return
        for base,dirs,names in os.walk(path,followlinks=False):
            dirs[:] = [name for name in dirs if name not in {".git","node_modules",".venv","venv","__pycache__","backups"}
                       and not Path(base,name).is_symlink()
                       and not (getattr(Path(base,name).lstat(),"st_file_attributes",0) & 0x400)]
            for name in names:
                yield Path(base,name)
    files = candidates()
    for file in files:
        relative = file.relative_to(path) if path.is_dir() else Path(file.name)
        if set(relative.parts).intersection({".git", "node_modules", ".venv", "venv", "__pycache__", "backups"}):
            continue
        if file.is_symlink() or not file.is_file() or file.stat().st_size > 2 * 1024 * 1024:
            continue
        if seen >= 2000 or scanned + file.stat().st_size > 64 * 1024 * 1024 or len(findings) >= 1000:
            break
        data = file.read_bytes()
        seen += 1
        scanned += len(data)
        for kind, pattern in patterns.items():
            if len(findings) >= 1000:
                break
            for match in pattern.finditer(data):
                findings.append({"file": str(file), "line": data.count(b"\n", 0, match.start()) + 1,
                                 "kind": kind, "value": "[REDACTED]"})
                if len(findings) >= 1000:
                    break
    return {"scan": "deterministic_secret_patterns", "files": seen, "bytes": scanned,
            "findings": findings, "manual_review_required": bool(findings)}


def guardian(home, once, interval, scan_root=None):
    """Report stale owned task records. Dispatcher jobs enforce process lifetime.

    Unknown OS processes are deliberately not classified as intrusions. It is not
    an antivirus or an autonomous reverse engineering agent.
    """
    root = home / "msshi-runtime"
    with locked(root / "locks/guardian.lock"):
        while True:
            findings = []
            for path in (root / "tickets").glob("*.json"):
                row = read_json(path, {})
                if row.get("state") == "running" and row.get("expires_at", 0) < time.time() and not row.get("expiry_alerted"):
                    event = {"event": "owned_task_expired", "ticket": row.get("id"),
                             "profile": row.get("profile"), "pid": row.get("pid"),
                             "action": "alert_dispatcher_job_owns_containment"}
                    findings.append(event)
                    alert(home, event)
                    row["expiry_alerted"] = True
                    atomic(path, encoded(row))
            state = {"pid": os.getpid(), "updated_at": time.time(), "mode": "owned_task_watchdog",
                     "llm_calls": 0, "findings": findings, "unknown_process_killing": False}
            if scan_root:
                state["static_scan"] = scan_secrets(scan_root)
            atomic(root / "guardian-state.json", encoded(state))
            if once:
                print(json.dumps({"guardian": "owned_task_watchdog", "findings": findings}, indent=2))
                return 0
            time.sleep(interval)


def status(home):
    root = home / "msshi-runtime"
    policy = read_json(root / "policy.json", {})
    result = {"version": VERSION, "migrated": bool(policy), "hardware": hardware(), "policy": policy, "profiles": {}}
    for file in sorted((root / "profiles").glob("*/routes.json")):
        row = read_json(file)
        result["profiles"][row["profile"]] = {"role": row["role"], "routes": {
            key: route["readiness"] for key, route in row["targets"].items()}}
        config = home / "config.yaml" if row["profile"] == "default" else home / "profiles" / row["profile"] / "config.yaml"
        cfg = yaml_read(config.read_bytes())
        actual = {name: item.get("enabled", True) is not False for name,item in (cfg.get("mcp_servers") or {}).items()
                  if norm(name) in MIGRATED_MCP and isinstance(item,dict)}
        result["profiles"][row["profile"]]["disabled_mcp_actual"] = sorted(name for name,value in actual.items() if not value)
        result["profiles"][row["profile"]]["enabled_targeted_mcp"] = sorted(name for name,value in actual.items() if value)
        result["profiles"][row["profile"]]["enabled_targeted_plugins"] = sorted(name for name in cfg.get("plugins",{}).get("enabled",[]) if norm(name) in MIGRATED_MCP)
    migration = read_json(root / "last-migration.json",{})
    checks = migration.get("protected_config_hashes",{})
    result["provider_model_preserved"] = bool(checks) and all(protected(Path(path).read_bytes()) == value for path,value in checks.items())
    receipts = sorted((root / "backups").glob("*/receipt.json"))
    result["rollback_receipt"] = str(receipts[-1]) if receipts else None
    guardian_row = read_json(root / "guardian-state.json",{})
    result["guardian"] = {"mode": "owned_task_watchdog", "running": time.time()-guardian_row.get("updated_at",0) < 180,
                          "automated_reverse_engineering": False}
    valid = (bool(policy) and result["provider_model_preserved"]
             and all(not row["enabled_targeted_mcp"] and not row["enabled_targeted_plugins"]
                     for row in result["profiles"].values()))
    result["result"] = "PASS_SUCCESS" if valid else "SETUP_REQUIRED"
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if valid else 2


def install_guardian(home):
    if os.name != "nt":
        raise ValueError("Use the host's service manager to run runtime guardian on this platform")
    root = home / "msshi-runtime"
    script = root / "runtime.py"
    if not script.is_file():
        raise ValueError("Run runtime migrate before installing the guardian")
    name = "MSSHI-Guardian-" + sha(str(home).encode())[:8]
    arguments = subprocess.list2cmdline(["-B", str(script), "guardian", "--home", str(home), "--interval", "60"])
    def psquote(value):
        return "'" + str(value).replace("'", "''") + "'"
    code = (
        "$ErrorActionPreference='Stop';"
        "$action=New-ScheduledTaskAction -Execute " + psquote(sys.executable) + " -Argument " + psquote(arguments) + ";"
        "$trigger=New-ScheduledTaskTrigger -AtLogOn;"
        "$principal=New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited;"
        "$settings=New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::Zero) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries;"
        "Register-ScheduledTask -TaskName " + psquote(name) + " -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null;"
        "Start-ScheduledTask -TaskName " + psquote(name)
    )
    result = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", code],
                            capture_output=True, text=True, creationflags=0x08000000)
    persistent = result.returncode == 0
    startup = None
    if not persistent:
        appdata = os.environ.get("APPDATA")
        if not appdata:
            raise ValueError("User Startup folder is unavailable")
        startup = safe_path(Path(appdata) / "Microsoft/Windows/Start Menu/Programs/Startup" / (name + ".vbs"))
        pythonw = Path(sys.executable).with_name("pythonw.exe")
        command = subprocess.list2cmdline([str(pythonw if pythonw.is_file() else sys.executable),
                                          "-B",str(script),"guardian","--home",str(home),"--interval","60"])
        content = ('\' MSSHI managed guardian launcher\r\nSet sh = CreateObject("WScript.Shell")\r\n'
                   + 'sh.Run "' + command.replace('"','""') + '", 0, False\r\n')
        if startup.is_file():
            current = startup.read_bytes()
            if not current.startswith(b"' MSSHI managed guardian launcher"):
                raise ValueError("Existing Startup file is not managed by MSSHI")
            backup = root / "guardian-startup-backup.vbs"
            if not backup.exists():
                atomic(backup,current)
        atomic(startup,content.encode("utf-8"))
        persistent = True
        state = read_json(root / "guardian-state.json",{})
        if time.time()-state.get("updated_at",0) > 180:
            pythonw = Path(sys.executable).with_name("pythonw.exe")
            subprocess.Popen([str(pythonw if pythonw.is_file() else sys.executable), "-B", str(script),
                              "guardian", "--home", str(home), "--interval", "60"],
                             creationflags=0x08000000 | 0x00000200, close_fds=True,
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    report = {"guardian": "owned_task_watchdog", "scheduled_task": name,
              "persistent_logon": persistent, "startup_fallback": str(startup) if startup else None, "llm_calls": 0,
              "memory_limit_mb_guaranteed": False,
              "scheduler_error": "" if result.returncode == 0 else result.stderr.strip()[:1000]}
    atomic(root / "guardian-install.json", encoded(report))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if persistent else 3


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", help="Hermes data root")
    commands = parser.add_subparsers(dest="operation", required=True)
    for verb in ("migrate", "status", "hardware", "guardian-install"):
        p = commands.add_parser(verb)
        p.add_argument("--home", dest="sub_home")
        p.add_argument("--json", action="store_true", help="Output is always JSON")
    p = commands.add_parser("ticket")
    p.add_argument("--home", dest="sub_home")
    p.add_argument("--profile")
    p.add_argument("--target", required=True)
    p.add_argument("--task", required=True)
    p.add_argument("--source", choices=("direct", "context"), default="direct")
    p.add_argument("--ttl", type=int, default=600)
    p = commands.add_parser("run")
    p.add_argument("--home", dest="sub_home")
    p.add_argument("--profile")
    p.add_argument("--ticket", required=True)
    p.add_argument("--timeout", type=int, default=600)
    p.add_argument("target")
    p.add_argument("arguments", nargs=argparse.REMAINDER)
    p = commands.add_parser("guardian")
    p.add_argument("--home", dest="sub_home")
    p.add_argument("--once", action="store_true")
    p.add_argument("--interval", type=int, default=60)
    p.add_argument("--scan-root", type=Path)
    p = commands.add_parser("scan")
    p.add_argument("path", type=Path)
    p.add_argument("--home", dest="sub_home")
    p = commands.add_parser("rollback")
    p.add_argument("receipt", type=Path)
    p.add_argument("--home", dest="sub_home")
    args = parser.parse_args(argv)
    home = safe_path(normalized_home(args.sub_home or args.home))
    os.environ["HERMES_HOME"] = str(home)
    if args.operation == "migrate":
        return migrate(home)
    if args.operation == "status":
        return status(home)
    if args.operation == "hardware":
        print(json.dumps(hardware(), indent=2))
        return 0
    if args.operation == "guardian-install":
        return install_guardian(home)
    if args.operation == "ticket":
        return ticket(home, profile_name(args.profile), args.target, args.task, args.source, args.ttl)
    if args.operation == "run":
        arguments = args.arguments[1:] if args.arguments[:1] == ["--"] else args.arguments
        return run_target(home, profile_name(args.profile), args.ticket, args.target, arguments, args.timeout)
    if args.operation == "guardian":
        if not 5 <= args.interval <= 3600:
            raise ValueError("Guardian interval must be between 5 and 3600 seconds")
        return guardian(home, args.once, args.interval, args.scan_root)
    if args.operation == "scan":
        result = scan_secrets(args.path)
        print(json.dumps(result, indent=2))
        return 2 if result["findings"] else 0
    path = safe_path(args.receipt)
    if not path.is_relative_to(home / "msshi-runtime/backups"):
        raise ValueError("Receipt is outside this Hermes runtime")
    row = read_json(path)
    if row.get("home") != str(home):
        raise ValueError("Receipt belongs to another installation")
    restored = 0
    with locked(home / "msshi-runtime/.migration-lock"):
        for item in reversed(row["changes"]):
            target = safe_path(item["path"])
            if not target.is_relative_to(home):
                raise ValueError("Rollback path is outside Hermes home")
            restored += restore_row(item, path.parent)
    print(json.dumps({"restored": restored}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"MSSHI runtime: {error}", file=sys.stderr)
        raise SystemExit(2)
