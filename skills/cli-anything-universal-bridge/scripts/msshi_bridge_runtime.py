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
    "filmcraft", "effectcraft", "photocraft", "lightcraft", "soundcraft",
    "designcraft", "vectorcraft", "figcraft", "wordcraft", "gridcraft",
    "deckcraft", "pdfcraft", "cadcraft", "solidcraft", "craftanything",
)
GENERIC_CLI = re.compile(r"cli:[a-z0-9][a-z0-9-]{0,63}")
CATALOG_URL = "https://clianything.cc/"
PROJECT_URL = "https://github.com/HKUDS/CLI-Anything"
WEB_TARGETS = {
    "gdrive-web": ("https://drive.google.com/drive/my-drive", "https://drive.google.com/drive/search", "q"),
    "perplexity": ("https://www.perplexity.ai/", "https://www.perplexity.ai/search", "q"),
    "youtube-chrome": ("https://www.youtube.com/", "https://www.youtube.com/results", "search_query"),
    "tiktok": ("https://www.tiktok.com/", "https://www.tiktok.com/search", "q"),
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
        rows = {key: {"route": row["kind"], "readiness": row["readiness"],
                      "require_task_ticket": True}
                for key,row in data["targets"].items()}
        for name,enabled in connectors.items():
            if normalized(name) in {"gitlab", "tinyfish"}:
                rows[mcp_id(name)] = {"route": "hermes-mcp", "readiness": "configured" if enabled else "disabled",
                                     "connector": name, "registration_source": "hermes-config",
                                     "require_task_ticket": False}
        return rows
    rows = {}
    for target in (*WEB_TARGETS, "antigravity"):
        if target == "gdrive-web":
            rows[target] = {"route": "web", "readiness": "available_web"}
            continue
        path = app_executable(target)
        if target == "youtube-chrome":
            rows[target] = {"route": "chrome", "readiness": "available" if path else "needs_install"}
        elif target == "antigravity":
            rows[target] = {"route": "desktop", "readiness": "available" if path else "needs_install"}
        else:
            desktop = path or WINDOWS_STORE_APPS[target] in store_app_ids()
            rows[target] = {"route": "hybrid", "readiness": "available" if desktop else "available_web"}
    for target in (*ARTCRAFT, "blender"):
        rows[target] = {"route": "hermes-mcp", "readiness": "missing_config"}
    for name, enabled in connectors.items():
        target = mcp_id(name)
        prior = rows.get(target, {})
        if prior.get("readiness") != "configured":
            rows[target] = {"route": "hermes-mcp", "readiness": "configured" if enabled else "disabled",
                            "connector": name}
    for target in (*HARNESS, *NATIVE, *installed_extension_ids()):
        rows[target] = {"route": "native-cli" if target in NATIVE else "cli-anything",
                        "readiness": "available" if harness_executable(target, hermes_home) else "needs_install"}
    return rows


def safe_process(path, args, wait):
    if os.name == "nt" and Path(path).suffix.lower() in {".cmd", ".bat", ".ps1"}:
        raise ValueError("Gunakan executable native untuk menjalankan rute ini.")
    return subprocess.run([path, *args], check=False).returncode if wait else subprocess.Popen([path, *args])


def open_target(target, query=None):
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
    state, _ = migrated_state(hermes_home)
    if (state / "policy.json").is_file():
        raise ValueError("MSSHI v3 execution requires msshi runtime run and a one-use task ticket.")
    if target not in (*HARNESS, *NATIVE) and not GENERIC_CLI.fullmatch(target):
        raise ValueError("Rute ini dipakai melalui tool MCP Hermes atau perintah --open.")
    if not (app := harness_executable(target, hermes_home)):
        raise ValueError("Executable belum terdeteksi. Gunakan --catalog dan tinjau prasyarat di CLI-Hub.")
    return safe_process(app, argv, True)
