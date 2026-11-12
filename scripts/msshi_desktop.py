"""Start Hermes Desktop after its local gateway is ready on Windows."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


def hidden_options():
    return {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}


def install_shortcut(home: Path) -> None:
    """Back up and repoint only shortcuts to this installation's Desktop."""
    home = home.expanduser().resolve()
    stable = home / "tools/msshi/msshi_desktop.py"
    stable.parent.mkdir(parents=True, exist_ok=True)
    content = Path(__file__).read_bytes()
    if Path(__file__).resolve() != stable:
        with tempfile.NamedTemporaryFile(dir=stable.parent, delete=False) as stream:
            stage = Path(stream.name)
            stream.write(content)
        os.replace(stage, stable)
    interpreter = Path(sys.executable).with_name("pythonw.exe")
    if not interpreter.is_file():
        raise ValueError("pythonw.exe is required for the Windows shortcut.")
    env = dict(os.environ, MSSHI_DESKTOP_HOME=str(home), MSSHI_DESKTOP_PYTHON=str(interpreter),
               MSSHI_DESKTOP_SCRIPT=str(stable))
    script = r'''
$ErrorActionPreference='Stop'
$root=$env:MSSHI_DESKTOP_HOME
$exe=Join-Path $root 'hermes-agent\apps\desktop\release\win-unpacked\Hermes.exe'
$known=@((Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Hermes.lnk'),
    (Join-Path ([Environment]::GetFolderPath('Desktop')) 'Hermes.lnk'))
$shell=New-Object -ComObject WScript.Shell
$backup=Join-Path $root ('msshi-private\desktop-backups\'+[DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss-fffffff'))
$changed=0
foreach($file in $known){
    if(-not (Test-Path -LiteralPath $file -PathType Leaf)){continue}
    $link=$shell.CreateShortcut($file)
    if(($link.TargetPath -ine $exe) -and
       -not (($link.TargetPath -ieq $env:MSSHI_DESKTOP_PYTHON) -and $link.Arguments.Contains($env:MSSHI_DESKTOP_SCRIPT))){continue}
    if(($link.TargetPath -ieq $env:MSSHI_DESKTOP_PYTHON) -and $link.Arguments.Contains($env:MSSHI_DESKTOP_SCRIPT)){continue}
    New-Item -Path $backup -ItemType Directory -Force|Out-Null
    $save=Join-Path $backup (($changed.ToString())+'.lnk')
    Copy-Item -LiteralPath $file -Destination $save
    $link.TargetPath=$env:MSSHI_DESKTOP_PYTHON
    $link.Arguments='"'+$env:MSSHI_DESKTOP_SCRIPT+'" --hermes-home "'+$root+'"'
    $link.WorkingDirectory=$root
    $link.IconLocation=$exe+',0'
    $link.Save()
    [Console]::WriteLine('MSSHI_SHORTCUT|'+$file+'|'+$save)
    $changed+=1
}
[Console]::WriteLine('MSSHI_SHORTCUT_DONE|'+$changed)
'''
    result = subprocess.run([shutil.which("powershell.exe"), "-NoProfile", "-NonInteractive", "-Command", script],
                            env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
                            timeout=90, **hidden_options())
    if result.returncode:
        raise ValueError("Could not install the Desktop shortcut: " + result.stderr.strip()[-2000:])
    import hashlib
    changes = []
    for row in result.stdout.splitlines():
        if row.startswith("MSSHI_SHORTCUT|"):
            _, target, backup = row.split("|", 2)
            changes.append({"path": target, "backup": backup,
                            "before_sha256": hashlib.sha256(Path(backup).read_bytes()).hexdigest(),
                            "after_sha256": hashlib.sha256(Path(target).read_bytes()).hexdigest()})
    if changes:
        receipt = Path(changes[0]["backup"]).parent / "receipt.json"
        receipt.write_text(json.dumps({"changes": changes}, indent=2) + "\n", encoding="utf-8")
    print(f"Hermes shortcuts updated: {len(changes)}")


def software_rendering_preference(home: Path) -> bool:
    """Read a device-local rendering preference without changing Hermes config."""
    path = home / "tools/msshi/desktop-preferences.json"
    if not path.is_file():
        return False
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
        return isinstance(value, dict) and value.get("software_rendering") is True
    except (OSError, ValueError):
        print("Ignoring an unreadable MSSHI Desktop rendering preference.", file=sys.stderr)
        return False


def run(home: Path, timeout: int, check_only: bool = False, software_rendering: bool = False) -> int:
    if os.name != "nt":
        raise ValueError("This launcher currently supports the Windows Desktop installation.")
    home = home.expanduser().resolve()
    source = home / "hermes-agent"
    desktop = source / "apps/desktop/release/win-unpacked/Hermes.exe"
    launcher = home / "bin/hermes.exe"
    reclaim = source / "scripts/desktop-update/windows.ps1"
    powershell = shutil.which("powershell.exe")
    if not all(path.is_file() for path in (desktop, launcher, reclaim)) or not powershell:
        raise ValueError("The existing Windows Hermes installation is incomplete.")
    env = dict(os.environ, HERMES_HOME=str(home), HERMES_SUPERVISED_CHILD="1")
    # Native marker recovery checks process identity and exclusive update locks.
    # It refuses to reclaim a live update. The pending source build remains owed.
    marker = subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-File", str(reclaim),
         "-MarkerOp", "reclaim", "-InstallRoot", str(source)],
        env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=45, **hidden_options(),
    )
    verdict = marker.stdout.strip().splitlines()
    if marker.returncode or not verdict or verdict[-1].strip() not in {"absent", "reclaimed"}:
        raise ValueError("Hermes reports an active or unresolved update. Finish it before starting Desktop.")
    print("Preparing the existing Hermes gateway...", flush=True)
    probe = subprocess.run(
        [str(launcher), "gateway", "ensure", "--json", "--timeout", str(timeout)],
        env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=timeout + 120, **hidden_options(),
    )
    response = None
    for line in probe.stdout.splitlines():
        try:
            value = json.loads(line)
        except ValueError:
            continue
        if isinstance(value, dict) and "state" in value:
            response = value
    if probe.returncode or not response or response.get("state") != "ready":
        reason = response.get("reason_code", "no ready response") if response else "no ready response"
        raise ValueError(f"Gateway is not ready ({reason}). Inspect logs/gateway.log before retrying.")
    print("Gateway ready. Provider and model settings were read from the existing profiles.", flush=True)
    if check_only:
        return 0
    # Inherit the supported supervised-child flag only in this process tree. When
    # dependencies are current, this prevents the owed source build from replaying
    # inside Desktop's fixed 75-second connection window.
    desktop_env = dict(env)
    if software_rendering or software_rendering_preference(home):
        # Supported by Hermes itself before Electron app readiness. This only
        # affects the Desktop child, never registry/global env or model config.
        desktop_env["HERMES_DESKTOP_DISABLE_GPU"] = "1"
        print("Hermes Desktop software rendering requested.", flush=True)
    subprocess.Popen([str(desktop)], cwd=desktop.parent, env=desktop_env,
                     creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
    print("Hermes Desktop opened.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hermes-home", type=Path,
                        default=Path(os.environ.get("HERMES_HOME", r"D:\HermesData")))
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--software-rendering", action="store_true",
                        help="Use Hermes' supported GPU fallback for this Desktop launch only")
    parser.add_argument("--install-shortcut", action="store_true",
                        help="Back up existing Hermes shortcuts and use gateway prewarming on future launches")
    args = parser.parse_args(argv)
    if not 30 <= args.timeout <= 600:
        parser.error("--timeout must be between 30 and 600 seconds")
    if sys.stdout is None:
        log = args.hermes_home / "logs/msshi-desktop.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        sys.stdout = log.open("a", encoding="utf-8", buffering=1)
        sys.stderr = sys.stdout
        print(datetime.now(timezone.utc).isoformat(), "Desktop launch requested")
    try:
        if args.install_shortcut:
            install_shortcut(args.hermes_home)
        return run(args.hermes_home, args.timeout, args.check_only, args.software_rendering)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"MSSHI Desktop: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
