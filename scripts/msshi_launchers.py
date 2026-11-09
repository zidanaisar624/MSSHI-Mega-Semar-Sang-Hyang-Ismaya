"""Create per-user launchers and register their bin directory on the user PATH."""
from __future__ import annotations

import os
from pathlib import Path
import shlex
import shutil
import sys

from install_msshi import reject_links
from msshi_sources import write_atomic, write_json


def windows_path(bin_dir):
    import winreg

    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, "Environment", 0,
                           winreg.KEY_QUERY_VALUE | winreg.KEY_SET_VALUE) as key:
        try:
            value, kind = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            value, kind = "", winreg.REG_EXPAND_SZ
        if kind not in (winreg.REG_SZ, winreg.REG_EXPAND_SZ):
            raise ValueError("Tipe PATH user Windows tidak didukung.")
        current = {os.path.normcase(os.path.normpath(os.path.expandvars(part.strip('"'))))
                   for part in value.split(";") if part}
        if os.path.normcase(os.path.normpath(bin_dir)) not in current:
            winreg.SetValueEx(key, "Path", 0, kind, ";".join(filter(None, (value, str(bin_dir)))))
    # Let desktop-launched terminals inherit the user environment on next launch.
    import ctypes

    ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001A, 0, "Environment", 2, 1000, None)


def shell_path(bin_dir):
    if str(bin_dir) in os.environ.get("PATH", "").split(os.pathsep):
        return
    user = Path.home()
    shell = Path(os.environ.get("SHELL", "sh")).name
    quoted = shlex.quote(str(bin_dir))
    line = f'export PATH={quoted}:"$PATH"'
    if shell == "fish":
        # Fish accepts its own single-quoted literal with backslash escapes.
        literal = str(bin_dir).replace("\\", "\\\\").replace("'", "\\'")
        line = f"fish_add_path --path '{literal}'"
        config = Path(os.environ.get("XDG_CONFIG_HOME") or user / ".config")
        profiles = (config / "fish" / "config.fish",)
    elif shell == "zsh":
        zdot = Path(os.environ.get("ZDOTDIR") or user)
        profiles = (zdot / ".zshrc",)
    elif shell == "bash":
        login = next((user / name for name in (".bash_profile", ".bash_login")
                      if (user / name).exists()), user / ".profile")
        profiles = (user / ".bashrc", login)
    else:
        profiles = (user / ".profile",)
    for profile in profiles:
        reject_links(profile)
        profile.parent.mkdir(parents=True, exist_ok=True)
        content = profile.read_text(encoding="utf-8") if profile.exists() else ""
        if line not in content.splitlines():
            with profile.open("a", encoding="utf-8") as handle:
                handle.write(f"\n# MSSHI command\n{line}\n")


def bootstrap(home, release, state, no_path):
    bin_dir = home / "bin"
    reject_links(bin_dir)
    bin_dir.mkdir(exist_ok=True)
    launcher = home / "launch.py"
    source = Path(__file__).with_name("launch_msshi.py")
    reject_links(source)
    write_atomic(launcher, source.read_bytes())
    if os.name == "nt":
        shim = bin_dir / "msshi.cmd"
        if sys.executable.isascii():
            python = '"' + sys.executable.replace("%", "%%") + '"'
        elif shutil.which("py"):
            python = "py -3"
        else:
            python = "python" if shutil.which("python") else "python3"
        content = ('@echo off\nsetlocal DisableDelayedExpansion\n'
                   f'{python} -B -X utf8 "%~dp0..\\launch.py" %*\n'
                   'exit /b %errorlevel%\n')
    else:
        shim = bin_dir / "msshi"
        content = ("#!/bin/sh\n"
                   'msshi_bin=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd) || exit 1\n'
                   f'exec {shlex.quote(sys.executable)} -B -X utf8 "$msshi_bin/../launch.py" "$@"\n')
    write_atomic(shim, content.encode("utf-8"))
    if os.name != "nt":
        shim.chmod(0o755)
    if state.get("current") != release:
        state.pop("git_commit", None)
    state["current"] = release
    write_json(home / "state.json", state)
    if not no_path:
        (windows_path if os.name == "nt" else shell_path)(bin_dir)
    print(f"msshi tersedia: {shim}")
    if not no_path:
        print("Buka terminal baru agar perubahan PATH berlaku.")
