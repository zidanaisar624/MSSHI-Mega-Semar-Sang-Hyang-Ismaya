"""MSSHI REA: pinned, explicit local CLI analysis for Hermes Coder."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import zipfile

sys.dont_write_bytecode = True
VERSION = "6.9.0"
SOURCE_COMMIT = "a8527d43b8439476f5c9d1497315dfe7dd5e1f38"
INTEGRITY = "sha512-KqDn1UR5BMqHoQ3MGAnPuWiSKwgdFaz1L/uUNgrKt+1W8kPtgYP8AWEOXIF1lDIOBVyPuYIIst2iamo1Wf3r8g=="
OWNER = {"schema": 1, "owner": "MSSHI REA isolated CLI runtime"}
INSPECT = {
    "archive": "inspect-artifact", "managed": "inspect-managed-artifact",
    "pe-imports": "inspect-pe-imports", "pe-certificates": "inspect-pe-certificates",
    "go": "inspect-go-binary", "rust": "inspect-rust-binary",
    "model": "inspect-model-artifact", "wasm": "inspect-wasm-artifact",
}


def encode(value):
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8")


def checked(value):
    path = Path(os.path.abspath(Path(value).expanduser()))
    for part in (path, *path.parents):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if part.is_symlink() or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("Symlink/junction paths are not supported")
    return path


def root_home(value=None):
    path = checked(value or os.environ.get("MSSHI_HERMES_HOME") or os.environ.get("HERMES_HOME") or
                   ("D:/HermesData" if os.name == "nt" and Path("D:/HermesData").exists() else Path.home() / ".hermes"))
    return path.parent.parent if path.parent.name.casefold() == "profiles" else path


def paths(home):
    folder = checked(home / "msshi-private" / "rea-runtime")
    return folder, folder / "node_modules" / "rea-agents" / "scripts" / "rea.mjs"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def write_new(path, value):
    with checked(path).open("xb") as stream:
        stream.write(encode(value))


def node_path():
    result = shutil.which("node")
    if not result:
        raise ValueError("Install a supported Node.js runtime explicitly first")
    return result


def supported_node(version):
    parts = tuple(int(p) for p in version.strip().lstrip("v").split(".")[:3])
    return (parts[0] == 22 and parts >= (22, 23, 4)) or (parts[0] == 24 and parts >= (24, 22, 1)) or parts >= (26, 12, 1)


def status(home):
    folder, entry = paths(home)
    package = entry.parent.parent / "package.json"
    lock = folder / "package-lock.json"
    marker = folder / "INSTALLATION.json"
    owned = (folder / "OWNER.json").is_file() and read(folder / "OWNER.json") == OWNER
    node = shutil.which("node")
    node_version = subprocess.run([node, "--version"], capture_output=True, text=True, timeout=10).stdout.strip() if node else None
    package_version = read(package).get("version") if package.is_file() else None
    package_integrity = read(lock).get("packages", {}).get("node_modules/rea-agents", {}).get("integrity") if lock.is_file() else None
    state = read(marker) if marker.is_file() else {}
    ready = bool(owned and entry.is_file() and package_version == VERSION and package_integrity == INTEGRITY and
                 node_version and supported_node(node_version) and state.get("entry_sha256") == digest(entry))
    return {"ready": ready, "version": VERSION, "source_commit": SOURCE_COMMIT, "license": "MIT",
            "runtime": str(folder), "entry": str(entry), "node": node, "node_version": node_version,
            "package_version": package_version, "package_integrity": package_integrity,
            "mode": "local-cli-only", "scope": ["nyenyenye-ya-gw-coder"], "mcp_enabled": False,
            "starts_on_boot": False, "optional_frida_installed": (folder / "node_modules" / "frida").exists(),
            "llm_calls": 0, "api_credits_used": 0, "last_selftest": state.get("last_selftest")}


def install(home):
    folder, entry = paths(home)
    folder.mkdir(parents=True, exist_ok=True)
    identity = folder / "OWNER.json"
    if identity.exists():
        if read(identity) != OWNER:
            raise ValueError("Runtime ownership mismatch")
    elif any(folder.iterdir()):
        raise ValueError("Existing unowned runtime; inspect it before any explicit adoption")
    else:
        write_new(identity, OWNER)
    if status(home)["ready"]:
        return status(home)
    node = node_path()
    version = subprocess.run([node, "--version"], capture_output=True, text=True, timeout=10, check=True).stdout
    if not supported_node(version):
        raise ValueError("REA requires Node 22.23.4+, 24.22.1+, or 26.12.1+ in the supported release lines")
    npm = Path(node).parent / "node_modules" / "npm" / "bin" / "npm-cli.js"
    if not npm.is_file():
        raise ValueError("The selected Node must have its matching npm-cli.js; no global installation will be changed")
    lockfile = folder / "install.lock"
    fd = os.open(lockfile, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.close(fd)
    try:
        subprocess.run([node, str(npm), "install", "--prefix", str(folder), "--ignore-scripts", "--omit=dev", "--omit=optional",
                        "--no-audit", "--no-fund", "--save-exact", "--registry=https://registry.npmjs.org", f"rea-agents@{VERSION}"],
                       timeout=900, check=True, **({"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}))
        package_integrity = read(folder / "package-lock.json")["packages"]["node_modules/rea-agents"]["integrity"]
        if package_integrity != INTEGRITY or read(entry.parent.parent / "package.json")["version"] != VERSION:
            raise ValueError("Installed release/integrity differs from the reviewed pin; do not run it")
        marker = folder / "INSTALLATION.json"
        payload = {"version": VERSION, "source_commit": SOURCE_COMMIT, "integrity": INTEGRITY,
                   "entry_sha256": digest(entry), "installed_utc": datetime.now(timezone.utc).isoformat(),
                   "lifecycle_scripts": False, "optional_dependencies": False, "last_selftest": None}
        marker.write_bytes(encode(payload))
    finally:
        lockfile.unlink(missing_ok=True)
    return status(home)


def environment(folder):
    # Analysis receives OS/runtime variables, never the agent's API tokens.
    allow = {"PATH", "PATHEXT", "SYSTEMROOT", "WINDIR", "COMSPEC", "TEMP", "TMP", "TMPDIR", "SYSTEMDRIVE",
             "PROGRAMFILES", "PROGRAMFILES(X86)", "PROCESSOR_ARCHITECTURE", "JAVA_HOME", "GHIDRA_INSTALL_DIR", "IDADIR"}
    env = {key: value for key, value in os.environ.items() if key.upper() in allow or key.startswith("REA_")}
    state = folder / "state"
    state.mkdir(exist_ok=True)
    env.update(HOME=str(state), USERPROFILE=str(state), APPDATA=str(state), LOCALAPPDATA=str(state),
               XDG_CACHE_HOME=str(state / "cache"), XDG_CONFIG_HOME=str(state / "config"),
               REA_LOG_LEVEL="silent", NO_COLOR="1", PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD="1")
    return env


def run_analysis(home, arguments, target, output, timeout=90):
    info = status(home)
    if not info["ready"]:
        raise ValueError("Pinned isolated REA runtime is not ready; run status, then explicit install if absent")
    target = checked(target)
    if not target.exists():
        raise ValueError("Select an existing local artifact explicitly")
    output = checked(output)
    stderr = output.with_suffix(output.suffix + ".stderr.txt")
    if output.suffix.lower() != ".json" or not output.parent.is_dir():
        raise ValueError("Output must be a new .json file in an existing directory")
    if output == target or target.is_dir() and output.is_relative_to(target):
        raise ValueError("Save the report outside the analyzed input tree")
    if output.exists() or stderr.exists():
        raise FileExistsError("Report or diagnostics already exist; choose a new output filename")
    folder, entry = paths(home)
    command = [info["node"], str(entry), *arguments, "--json", "--full-output"]
    process = None
    timed_out = False
    with output.open("xb") as out, stderr.open("xb") as err:
        process = subprocess.Popen(command, cwd=folder, env=environment(folder), stdout=out, stderr=err,
                                   start_new_session=os.name != "nt",
                                   **({"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}))
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            if os.name == "nt":
                subprocess.run(["taskkill.exe", "/PID", str(process.pid), "/T", "/F"], capture_output=True, timeout=10)
            else:
                os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=10)
            code = 124
    return {"success": code == 0, "exit_code": code, "timed_out": timed_out, "report": str(output),
            "report_sha256": digest(output), "stderr": str(stderr), "stderr_sha256": digest(stderr),
            "command": command[2:], "evidence_review_required": True}


def selftest(home):
    folder, _ = paths(home)
    with tempfile.TemporaryDirectory(prefix="msshi-rea-fixture-", dir=folder) as temp:
        work = Path(temp)
        app = work / "owned-app"
        app.mkdir()
        (app / "package.json").write_text('{"name":"msshi-owned-fixture","version":"1.0.0","type":"module"}', encoding="utf-8")
        sentinel = work / "EXECUTED.txt"
        (app / "index.js").write_text('import { add } from "./math.js";\nimport { writeFileSync } from "node:fs";\n' +
                                     f'writeFileSync({json.dumps(str(sentinel))}, "executed");\n' +
                                     'throw new Error("STATIC_ONLY_DO_NOT_EXECUTE");\nexport const answer = add(20, 22);\n', encoding="utf-8")
        (app / "math.js").write_text('export function add(a, b) { return a + b; }\n', encoding="utf-8")
        result = run_analysis(home, ["analyze-javascript-application", str(app), "--analysis-timeout-ms", "30000"], app, work / "evidence.json")
        evidence = read(work / "evidence.json")
        rendered = json.dumps(evidence)
        result["fixture_modules_seen"] = all(name in rendered for name in ("index.js", "math.js"))
        result["fixture_not_executed"] = not sentinel.exists()
        archive = work / "owned.zip"
        with zipfile.ZipFile(archive, "w") as bundle:
            bundle.writestr("README.txt", "MSSHI owned benign fixture\n")
        archive_result = run_analysis(home, ["inspect-artifact", str(archive)], archive, work / "archive.json")
        archive_evidence = read(work / "archive.json")
        result["archive_inventory"] = archive_result["success"] and "README.txt" in json.dumps(archive_evidence)
        result["archive_evidence"] = archive_evidence
        result["success"] = result["success"] and evidence.get("ok") is True and archive_evidence.get("ok") is True and result["fixture_modules_seen"] and result["fixture_not_executed"] and result["archive_inventory"]
        result["evidence"] = evidence
        result["tested_utc"] = datetime.now(timezone.utc).isoformat()
        audit = folder / "selftest.json"
        audit.write_bytes(encode(result))
        marker = folder / "INSTALLATION.json"
        state = read(marker)
        state["last_selftest"] = {key: value for key, value in result.items() if key in ("success", "tested_utc", "fixture_modules_seen", "fixture_not_executed", "archive_inventory")}
        marker.write_bytes(encode(state))
        return {"success": result["success"], "proof": str(audit), "proof_sha256": digest(audit), **state["last_selftest"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hermes-home")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("status", "install", "selftest"):
        sub.add_parser(name)
    js = sub.add_parser("javascript", help="Static extracted JavaScript/Electron directory or ASAR inspection")
    js.add_argument("path")
    js.add_argument("--output", required=True)
    js.add_argument("--analysis-timeout-ms", type=int, default=30000, choices=range(1000, 120001), metavar="1000..120000")
    inspect = sub.add_parser("inspect", help="Read-only local artifact routes; no extraction or target execution")
    inspect.add_argument("kind", choices=INSPECT)
    inspect.add_argument("path")
    inspect.add_argument("--output", required=True)
    native = sub.add_parser("native", help="Explicit installed native engine; may launch that local engine")
    native.add_argument("operation", choices=("analyze", "search", "function", "decompile", "xrefs", "trace"))
    native.add_argument("path")
    native.add_argument("--provider", required=True, choices=("ghidra", "hopper", "kuna"))
    native.add_argument("--query")
    native.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    home = root_home(args.hermes_home)
    if args.command in ("status", "install", "selftest"):
        result = globals()[args.command](home)
    else:
        target = checked(args.path)
        if args.command == "javascript":
            arguments = ["analyze-javascript-application", str(target), "--analysis-timeout-ms", str(args.analysis_timeout_ms)]
            timeout = args.analysis_timeout_ms / 1000 + 60
        elif args.command == "inspect":
            arguments, timeout = [INSPECT[args.kind], str(target)], 90
        else:
            if args.operation != "analyze" and (not args.query or args.query.startswith("-")):
                raise ValueError("This native operation requires a non-option --query symbol, address, or pattern")
            if target.is_dir():
                raise ValueError("Select one authorized native binary file")
            arguments = [args.operation, str(target), *([args.query] if args.operation != "analyze" else []), "--provider", args.provider]
            timeout = 180
        result = run_analysis(home, arguments, target, args.output, timeout)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result.get("exit_code", 0 if result.get("success", True) else 1)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError, KeyError) as exc:
        print(json.dumps({"success": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
