"""Detect local application capabilities and route explicit MSSHI requests."""
from __future__ import annotations

import ctypes
import json
import os
import re
import shutil
import subprocess
import sys
import webbrowser
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlencode


ARTCRAFT = (
    "anicraft", "filmcraft", "effectcraft", "photocraft", "lightcraft", "soundcraft",
    "designcraft", "vectorcraft", "figcraft", "wordcraft", "gridcraft",
    "deckcraft", "pdfcraft", "cadcraft", "solidcraft", "craftanything", "materialcraft", "texturecraft",
)
ROLE_ALIASES = {
    "default": "default", "yukino": "yukino", "shizuka": "shizuka", "shizuka-hiratsuka": "shizuka",
    "val": "val", "kiki-chii": "kiki-chii", "shikaku": "shikaku",
    "shikaku-nara": "shikaku", "nyenyenye-ya-gw-coder": "shikaku",
}
MUZA_ARTCRAFT = {
    "default": (), "yukino": (), "shizuka": (),
    "val": ("pdfcraft", "gridcraft", "wordcraft", "deckcraft"),
    "shikaku": ("craftanything", "figcraft"),
    "kiki-chii": ("anicraft", "filmcraft", "effectcraft", "soundcraft", "photocraft", "lightcraft",
                  "designcraft", "figcraft", "vectorcraft", "cadcraft", "solidcraft", "materialcraft", "texturecraft"),
}
MUZA_NON_ART = {
    "val": ("perplexity", "python", "whatsapp-web", "youtube-chrome"),
    "shikaku": ("antigravity", "git", "node", "perplexity", "python", "youtube-chrome"),
    "kiki-chii": ("blender", "ffmpeg", "node", "obs", "perplexity", "python", "tiktok", "youtube-chrome"),
}
SHARED_UTILITIES = {"hersona", "llmtrim", "graphify"}
DISALLOWED_TARGETS = {"gdrive", "gdrive-web", "googledrive", "google-drive", "gimp", "libreoffice", "solvecraft"}
GENERIC_CLI = re.compile(r"cli:[a-z0-9][a-z0-9-]{0,63}")
CATALOG_URL = "https://clianything.cc/"
PROJECT_URL = "https://github.com/HKUDS/CLI-Anything"
WEB_TARGETS = {
    "gdrive-web": ("https://drive.google.com/drive/my-drive", "https://drive.google.com/drive/search", "q"),
    "perplexity": ("https://www.perplexity.ai/", "https://www.perplexity.ai/search", "q"),
    "youtube-chrome": ("https://www.youtube.com/", "https://www.youtube.com/results", "search_query"),
    "tiktok": ("https://www.tiktok.com/", "https://www.tiktok.com/search", "q"),
    "whatsapp-web": ("https://web.whatsapp.com/", "https://web.whatsapp.com/", "q"),
}
HARNESS = {
    "blender-cli": "cli-anything-blender",
    "libreoffice": "cli-anything-libreoffice",
    "gimp": "cli-anything-gimp",
    "obs": "cli-anything-obs-studio",
    "audacity": "cli-anything-audacity",
    "inkscape": "cli-anything-inkscape",
    "krita": "cli-anything-krita",
    "kdenlive": "cli-anything-kdenlive",
    "drawio": "cli-anything-drawio",
}
NATIVE = {"ffmpeg": "ffmpeg", "cli-hub": "cli-hub"}
WINDOWS_STORE_APPS = {
    "perplexity": "PerplexityAI.PerplexityApp_3jh4kjrg4dzr2!ai.perplexity.PerplexityPersonalComputer.Electron",
    "tiktok": "BytedancePte.Ltd.TikTok_6yccndn6064se!App",
}
MCP_ALIASES = {
    "craft-anything": "craftanything",
    "blender-mcp": "blender",
    "blender-mcp-server": "blender",
    **{f"artcraft-{name}": name for name in ARTCRAFT},
    "artcraft-craft-anything": "craftanything",
}


def role_for_profile(profile):
    return ROLE_ALIASES.get(str(profile or "default").lower(), "custom")


def academic_policy(hermes_home):
    if hermes_home is None:
        return None
    state, _ = migrated_state(hermes_home)
    marker = state / 'active-preset.json'
    if not marker.is_file():
        return None
    for path in (marker, state / 'academic-app-policy.json'):
        for node in (path, *path.parents):
            if node.is_symlink() or (node.exists() and getattr(node.lstat(), 'st_file_attributes', 0) & 0x400):
                raise ValueError('Academic policy must not use linked paths')
    value = json.loads(marker.read_text(encoding='utf-8-sig'))
    if value.get('preset') not in {'academic-mahasiswa', 'academic-dosen'}:
        return None
    policy = json.loads((state / 'academic-app-policy.json').read_text(encoding='utf-8-sig'))
    if policy.get('schema_version') != 1:
        raise ValueError('Unsupported Academic application policy')
    return policy


def academic_role(profile, hermes_home):
    role = role_for_profile(profile)
    if role == 'default':
        state, _ = migrated_state(hermes_home)
        layout = state / 'team-layout.json'
        if layout.is_file():
            data = json.loads(layout.read_text(encoding='utf-8-sig'))
            if data.get('schema') == 1 and data.get('roles', {}).get('yukino') == 'default':
                return 'yukino'
    return role


def optional_executable(target, hermes_home):
    if target in ARTCRAFT:
        return artcraft_executable(target)
    if target == 'blender':
        return app_executable('blender') or shutil.which('blender') or harness_executable('blender-cli', hermes_home)
    return harness_executable(target, hermes_home)


def academic_optional_allowed(profile, target, hermes_home, explicit=False):
    policy = academic_policy(hermes_home)
    if not policy or target not in policy.get('optional_installed_only', []):
        return False
    if not optional_executable(target, hermes_home):
        return False
    if explicit:
        return True
    state, _ = migrated_state(hermes_home)
    route = state / 'profiles' / str(profile) / 'routes.json'
    if not route.is_file():
        return False
    data = json.loads(route.read_text(encoding='utf-8-sig'))
    return data.get('targets', {}).get(target, {}).get('academic_opt_in') is True


def target_allowed(profile, target, hermes_home=None, allow_installed_optional=False):
    """Preset routing is role-scoped; it is not an operating-system security boundary."""
    remote = str(target).lower().startswith("mcp:")
    target = normalized(str(target)).removeprefix("mcp:")
    target = MCP_ALIASES.get(target, target)
    # A generic adapter for a known application has the same role restrictions.
    if target.startswith("cli:"):
        application = MCP_ALIASES.get(target[4:], target[4:])
        if application in {*ARTCRAFT, *DISALLOWED_TARGETS, "blender", "blender-cli"}:
            target = application
    if target == "blender-cli":
        target = "blender"
    if target in DISALLOWED_TARGETS:
        return False
    policy = academic_policy(hermes_home)
    if policy is not None:
        role = academic_role(profile, hermes_home)
        allowed = set(policy.get('artcraft', {}).get(role, [])) | set(policy.get('non_artcraft', {}).get(role, [])) | set(policy.get('shared_utilities', []))
        return target in allowed or academic_optional_allowed(profile, target, hermes_home, explicit=allow_installed_optional)
    role = role_for_profile(profile)
    if role == "custom":
        return True
    if target in ARTCRAFT:
        return target in MUZA_ARTCRAFT[role]
    if remote and target != "blender":
        return True
    if target in SHARED_UTILITIES:
        return True
    if role in MUZA_NON_ART:
        # Existing remote service connectors have independent auth/permissions.
        return target in MUZA_NON_ART[role] or target in {"gitlab", "tinyfish"}
    return target != "blender"


def artcraft_root():
    value = os.environ.get("MSSHI_ARTCRAFT_ROOT")
    if value:
        path = Path(value).expanduser()
        if not path.is_absolute():
            raise ValueError("MSSHI_ARTCRAFT_ROOT must be an absolute application directory")
        return path
    return Path("D:/Program/ArtCraft Apps") if os.name == "nt" else Path.home() / "Applications/ArtCraft Apps"


def artcraft_executable(target):
    if target not in ARTCRAFT:
        return None
    folder = "craft-anything" if target == "craftanything" else target
    path = artcraft_root() / folder / (folder + ("-cli.exe" if os.name == "nt" else "-cli"))
    return str(path.absolute()) if path.is_file() else None


def scope_capabilities(rows, profile, hermes_home=None):
    for name, row in rows.items():
        if not target_allowed(profile, name, hermes_home):
            row.update(readiness="disabled" if name in {"gdrive", "gdrive-web"} else "blocked_by_specialization",
                       policy_role=role_for_profile(profile), require_task_ticket=True)
    return rows


def normalized(value):
    return value.lower().replace("_", "-")


def mcp_id(name):
    key = normalized(name)
    key = MCP_ALIASES.get(key, key)
    return key if key in (*ARTCRAFT, "blender") else f"mcp:{name.lower()}"


def executable(names, windows=(), mac=()):
    for name in names:
        if path := shutil.which(name):
            return path
    if os.name == "nt":
        for variable, relative in windows:
            base = os.environ.get(variable)
            if base and (path := Path(base) / relative).is_file():
                return str(path)
    elif sys.platform == "darwin":
        for relative in mac:
            for base in (Path("/Applications"), Path.home() / "Applications"):
                if (path := base / relative).is_file():
                    return str(path)
    return None


def app_executable(target):
    if target == 'blender':
        found = executable(('blender',), (), ('Blender.app/Contents/MacOS/Blender',))
        if found:
            return found
        if os.name == 'nt':
            for name in ('ProgramFiles', 'ProgramFiles(x86)'):
                value = os.environ.get(name)
                if not value:
                    continue
                base = Path(value) / 'Blender Foundation'
                if base.is_dir():
                    for item in sorted(base.glob('Blender*/blender.exe'), reverse=True):
                        if item.is_file():
                            return str(item)
        return None
    if target == "youtube-chrome":
        return executable(
            ("google-chrome", "google-chrome-stable", "chrome"),
            tuple((base, "Google/Chrome/Application/chrome.exe")
                  for base in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA")),
            ("Google Chrome.app/Contents/MacOS/Google Chrome",),
        )
    if target == "perplexity":
        return executable(
            ("perplexity", "Perplexity"),
            (("LOCALAPPDATA", "Programs/Perplexity/Perplexity.exe"),
             ("LOCALAPPDATA", "Perplexity/Perplexity.exe"),
             ("ProgramFiles", "Perplexity/Perplexity.exe")),
            ("Perplexity.app/Contents/MacOS/Perplexity",),
        )
    if target == "tiktok":
        return executable(
            ("tiktok", "TikTok"),
            (("LOCALAPPDATA", "Microsoft/WindowsApps/TikTok.exe"),
             ("LOCALAPPDATA", "Programs/TikTok/TikTok.exe")),
            ("TikTok.app/Contents/MacOS/TikTok",),
        )
    if os.name == "nt" and (shim := shutil.which("antigravity-ide")):
        candidate = Path(shim).parent.parent / "Antigravity IDE.exe"
        if candidate.is_file():
            return str(candidate)
    return executable(
        ("antigravity", "Antigravity"),
        (("LOCALAPPDATA", "Programs/Antigravity/Antigravity.exe"),
         ("LOCALAPPDATA", "Programs/Google/Antigravity/Antigravity.exe"),
         ("ProgramFiles", "Google/Antigravity/Antigravity.exe")),
        ("Antigravity.app/Contents/MacOS/Antigravity",),
    )


@lru_cache(maxsize=1)
def store_app_ids():
    if os.name != "nt":
        return set()
    powershell = Path(os.environ.get("SystemRoot", "C:/Windows")) / "System32/WindowsPowerShell/v1.0/powershell.exe"
    if not powershell.is_file():
        return set()
    try:
        output = subprocess.check_output(
            [str(powershell), "-NoProfile", "-NonInteractive", "-Command",
             "Get-StartApps | ForEach-Object { $_.AppID }"],
            stderr=subprocess.DEVNULL, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW,
        )
    except (OSError, subprocess.SubprocessError):
        return set()
    return set(output.decode("ascii", errors="ignore").splitlines()).intersection(WINDOWS_STORE_APPS.values())


def memory_available():
    """Return available and total bytes, or None if the platform probe fails."""
    try:
        if os.name == "nt":
            class MemoryStatus(ctypes.Structure):
                _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong),
                            *((name, ctypes.c_ulonglong) for name in (
                                "total", "available", "page_total", "page_available",
                                "virtual_total", "virtual_available", "extended_available"))]
            status = MemoryStatus()
            status.length = ctypes.sizeof(status)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)) and status.total:
                return status.available, status.total
        elif sys.platform == "darwin":
            total = int(subprocess.check_output(
                ["/usr/sbin/sysctl", "-n", "hw.memsize"], timeout=3, stderr=subprocess.DEVNULL,
            ))
            vmstat = subprocess.check_output(["/usr/bin/vm_stat"], timeout=3, text=True)
            first, *lines = vmstat.splitlines()
            page_size = int(first.split("page size of ")[1].split()[0])
            pages = dict(line.split(":", 1) for line in lines if ":" in line)
            available = sum(int(pages.get(key, "0").strip().removesuffix("."))
                            for key in ("Pages free", "Pages inactive", "Pages speculative"))
            if total > 0 and available >= 0:
                return min(available * page_size, total), total
        elif Path("/proc/meminfo").is_file():
            values = {}
            for line in Path("/proc/meminfo").read_text(encoding="ascii").splitlines():
                key, _, value = line.partition(":")
                if key in {"MemAvailable", "MemTotal"}:
                    values[key] = int(value.split()[0]) * 1024
            if values["MemTotal"] > 0:
                return values["MemAvailable"], values["MemTotal"]
    except (OSError, ValueError, KeyError, IndexError, subprocess.SubprocessError):
        pass
    return None


def memory_is_ready():
    reading = memory_available()
    if reading is None:
        return False
    available, total = reading
    return available >= 2.2 * 1024**3 and available >= total * .20


def harness_executable(target, hermes_home=None):
    command = HARNESS.get(target) or NATIVE.get(target)
    if command is None and GENERIC_CLI.fullmatch(target):
        command = f"cli-anything-{target[4:]}"
    if not command:
        return None
    names = (command, "cli-anything-obs") if target == "obs" else (command,)
    for name in names:
        if (path := shutil.which(name)) and (
            os.name != "nt" or Path(path).suffix.lower() not in {".cmd", ".bat", ".ps1"}
        ):
            return path
    if target == "ffmpeg" and os.name == "nt" and hermes_home is not None:
        home = hermes_home.parent.parent if hermes_home.parent.name.lower() == "profiles" else hermes_home
        tools = home / "tools"
        for path in sorted(tools.glob("ffmpeg-*/bin/ffmpeg.exe"), reverse=True):
            if path.is_file() and path.resolve().is_relative_to(tools.resolve()):
                return str(path)
    return None


def installed_extension_ids():
    """Recognize additional CLI-Anything executables from PATH without launching them."""
    prefix = "cli-anything-"
    known = {*HARNESS.values(), "cli-anything-obs"}
    result = set()
    directories = dict.fromkeys(os.get_exec_path())
    for directory in directories:
        # Ignore relative and UNC entries. Only normal absolute PATH dirs are inventoried.
        if not os.path.isabs(directory) or directory.startswith(("\\\\", "//")):
            continue
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    filename = entry.name.lower()
                    if os.name == "nt":
                        stem, ext = os.path.splitext(filename)
                        if ext not in {".exe", ".com"}:
                            continue
                        filename = stem
                    if not filename.startswith(prefix) or filename in known:
                        continue
                    target = "cli:" + filename[len(prefix):]
                    if GENERIC_CLI.fullmatch(target) and entry.is_file() and os.access(entry.path, os.X_OK):
                        result.add(target)
        except OSError:
            continue
    return sorted(result)


def migrated_state(hermes_home=None):
    base = Path(hermes_home or os.environ.get("HERMES_HOME", "~/.hermes")).expanduser()
    profile = base.name if base.parent.name.casefold() == "profiles" else "default"
    installation = base.parent.parent if profile != "default" else base
    state = installation / "msshi-runtime"
    return state, profile


def capabilities(connectors, hermes_home=None):
    """Return sanitized, current readiness and the internal route hints."""
    state, profile = migrated_state(hermes_home)
    routes = state / "profiles" / profile / "routes.json"
    if (state / "policy.json").is_file() and routes.is_file():
        data = json.loads(routes.read_text(encoding="utf-8"))
        rows = {key: {"route": row["kind"], "readiness": ("optional_missing" if row.get("readiness") == "available"
                      and row.get("kind") in {"native-cli", "browser", "desktop"}
                      and not (row.get("executable") and Path(row["executable"]).is_file()) else row["readiness"]),
                      "require_task_ticket": True}
                for key,row in data["targets"].items()}
        for name,enabled in connectors.items():
            if normalized(name) in {"gitlab", "tinyfish"}:
                rows[mcp_id(name)] = {"route": "hermes-mcp", "readiness": "configured" if enabled else "disabled",
                                     "connector": name, "registration_source": "hermes-config",
                                     "require_task_ticket": False}
        return scope_capabilities(rows, profile, hermes_home)
    rows = {}
    for target in (*WEB_TARGETS, "antigravity"):
        if target == "gdrive-web":
            rows[target] = {"route": "web", "readiness": "disabled"}
            continue
        path = app_executable(target)
        if target == "youtube-chrome":
            rows[target] = {"route": "chrome", "readiness": "available" if path else "needs_install"}
        elif target == "antigravity":
            rows[target] = {"route": "desktop", "readiness": "available" if path else "needs_install"}
        else:
            desktop = path or (target in WINDOWS_STORE_APPS and WINDOWS_STORE_APPS[target] in store_app_ids())
            rows[target] = {"route": "hybrid", "readiness": "available" if desktop else "available_web"}
    for target in ARTCRAFT:
        rows[target] = {"route": "native-cli", "readiness": "requires_migration" if artcraft_executable(target) else "needs_install",
                        "require_task_ticket": True}
    rows["blender"] = {"route": "native-cli", "readiness": "requires_migration", "require_task_ticket": True}
    for name, enabled in connectors.items():
        target = mcp_id(name)
        prior = rows.get(target, {})
        if prior.get("readiness") != "configured":
            if target not in ARTCRAFT and target != "blender":
                rows[target] = {"route": "hermes-mcp", "readiness": "configured" if enabled else "disabled",
                                "connector": name}
    for target in (*HARNESS, *NATIVE, *installed_extension_ids()):
        rows[target] = {"route": "native-cli" if target in NATIVE else "cli-anything",
                        "readiness": "available" if harness_executable(target, hermes_home) else "needs_install"}
    return scope_capabilities(rows, profile, hermes_home)


def safe_process(path, args, wait):
    if os.name == "nt" and Path(path).suffix.lower() in {".cmd", ".bat", ".ps1"}:
        raise ValueError("Gunakan executable native untuk menjalankan rute ini.")
    return subprocess.run([path, *args], check=False).returncode if wait else subprocess.Popen([path, *args])


def open_target(target, query=None):
    if target in DISALLOWED_TARGETS:
        raise ValueError("Rute ini dinonaktifkan oleh kebijakan MSSHI.")
    state, _ = migrated_state()
    if (state / "policy.json").is_file():
        raise ValueError("MSSHI v3 execution requires msshi runtime run and a one-use task ticket.")
    if target == "antigravity":
        if not (app := app_executable(target)):
            raise ValueError("Antigravity IDE belum terdeteksi.")
        workspace = Path(query).expanduser().resolve(strict=True) if query else None
        if workspace is not None and not workspace.is_dir():
            raise ValueError("Workspace Antigravity harus berupa folder.")
        safe_process(app, [str(workspace)] if workspace else [], False)
        return "desktop"
    if target not in WEB_TARGETS:
        raise ValueError("Rute ini dipakai melalui tool MCP Hermes atau perintah --run.")
    home, search, param = WEB_TARGETS[target]
    url = f"{search}?{urlencode({param: query})}" if query else home
    if target == "youtube-chrome":
        if not (app := app_executable(target)):
            raise ValueError("Google Chrome belum terdeteksi.")
        safe_process(app, [url], False)
        return "chrome"
    if target in {"perplexity", "tiktok"} and not query and (target != "perplexity" or memory_is_ready()):
        if app := app_executable(target):
            safe_process(app, [], False)
            return "desktop"
        app_id = WINDOWS_STORE_APPS[target]
        if app_id in store_app_ids():
            explorer = Path(os.environ.get("SystemRoot", "C:/Windows")) / "explorer.exe"
            if explorer.is_file():
                safe_process(str(explorer), [f"shell:AppsFolder\\{app_id}"], False)
                return "desktop"
    if not webbrowser.open(url):
        raise ValueError("Browser bawaan tidak dapat dibuka.")
    return "web"


def run_target(target, argv, hermes_home=None):
    state, profile = migrated_state(hermes_home)
    if not target_allowed(profile, target, hermes_home):
        raise ValueError("Target di luar spesialisasi profil atau dinonaktifkan oleh kebijakan.")
    if (state / "policy.json").is_file():
        raise ValueError("MSSHI v3 execution requires msshi runtime run and a one-use task ticket.")
    if target not in (*HARNESS, *NATIVE) and not GENERIC_CLI.fullmatch(target):
        raise ValueError("Rute ini dipakai melalui tool MCP Hermes atau perintah --open.")
    if not (app := harness_executable(target, hermes_home)):
        raise ValueError("Executable belum terdeteksi. Gunakan --catalog dan tinjau prasyarat di CLI-Hub.")
    return safe_process(app, argv, True)
