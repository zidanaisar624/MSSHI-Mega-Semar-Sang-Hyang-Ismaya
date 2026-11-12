"""Local BRAG scaffolding and pinned renderer launcher; no LLM calls."""
from __future__ import annotations

import argparse
import ctypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

UPSTREAM_COMMIT = "669ab9286aa28b6c3ee30e75f181ee74319d012a"
HYPERFRAMES_VERSION = "0.9.38"


def resource_budget(runtime):
    physical = commit = None
    if os.name == "nt":
        class MemoryStatus(ctypes.Structure):
            _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong),
                        ("total_physical", ctypes.c_ulonglong), ("available_physical", ctypes.c_ulonglong),
                        ("total_pagefile", ctypes.c_ulonglong), ("available_pagefile", ctypes.c_ulonglong),
                        ("total_virtual", ctypes.c_ulonglong), ("available_virtual", ctypes.c_ulonglong),
                        ("available_extended_virtual", ctypes.c_ulonglong)]
        status = MemoryStatus()
        status.length = ctypes.sizeof(status)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            physical, commit = status.available_physical, status.available_pagefile
    elif Path("/proc/meminfo").is_file():
        values = {}
        for line in Path("/proc/meminfo").read_text().splitlines():
            key, value = line.split(":", 1)
            values[key] = int(value.strip().split()[0]) * 1024
        physical = values.get("MemAvailable")
        if "CommitLimit" in values and "Committed_AS" in values:
            commit = max(0, values["CommitLimit"] - values["Committed_AS"])
    ancestor = Path(runtime)
    while not ancestor.exists() and ancestor != ancestor.parent:
        ancestor = ancestor.parent
    disk_free = shutil.disk_usage(ancestor).free
    allowed = physical is not None and commit is not None and physical >= 512 * 1024**2 and commit >= 1024**3 and disk_free >= 1024**3
    return {"available_physical_bytes": physical, "available_commit_bytes": commit,
            "runtime_disk_free_bytes": disk_free, "minimum_physical_bytes": 512 * 1024**2,
            "minimum_commit_bytes": 1024**3, "minimum_disk_bytes": 1024**3,
            "browser_diagnostic_allowed": allowed,
            "note": "Minimum guard only; a production film may require substantially more memory and disk."}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def root_path(value=None):
    value = value or os.environ.get("MSSHI_HERMES_HOME") or os.environ.get("HERMES_HOME")
    root = Path(value or ("D:/HermesData" if os.name == "nt" and Path("D:/HermesData").is_dir() else Path.home() / ".hermes")).expanduser().absolute()
    return root.parent.parent if root.parent.name.lower() == "profiles" else root


def checked_destination(value):
    path = Path(os.path.abspath(Path(value).expanduser()))
    for candidate in (path, *path.parents):
        if candidate.is_symlink() or (candidate.exists() and getattr(candidate.lstat(), "st_file_attributes", 0) & 0x400):
            raise ValueError(f"Refusing a symlink or junction destination: {candidate}")
    return path


def tool(root, name):
    found = shutil.which(name)
    if found:
        return Path(found)
    executable = name + (".exe" if os.name == "nt" else "")
    # Only inspect immediate managed tool folders, never a user browser profile.
    tools = root / "tools"
    if tools.is_dir():
        for folder in sorted(tools.glob(name + "-*"), reverse=True):
            for candidate in (folder / executable, folder / "bin" / executable):
                if candidate.is_file():
                    return candidate
    return None


def renderer_environment(root, runtime):
    env = {key: value for key, value in os.environ.items()
           if not any(part in key.upper() for part in ("TOKEN", "SECRET", "PASSWORD", "API_KEY"))}
    process_home = runtime / "process-home"
    env.update({
        "HYPERFRAMES_CONFIG_DIR": str(runtime / "config"),
        "HYPERFRAMES_CACHE_DIR": str(runtime / "cache"),
        "HYPERFRAMES_NO_TELEMETRY": "1", "HYPERFRAMES_NO_UPDATE_CHECK": "1",
        "DO_NOT_TRACK": "1", "PRODUCER_MAX_WORKERS": "1",
        # Upstream non-TTY `check` otherwise starts a detached 5-minute browser worker.
        "CI": "1",
        "PRODUCER_LOW_MEMORY_MODE": "true", "NODE_OPTIONS": "--max-old-space-size=1024",
        "TEMP": str(runtime / "temp"), "TMP": str(runtime / "temp"),
        "HYPERFRAMES_EXTRACT_CACHE_DIR": str(runtime / "cache" / "extracted-frames"),
        # Prevent upstream configuration seeding from the user's real home.
        "USERPROFILE": str(process_home), "HOME": str(process_home),
    })
    ffmpeg = tool(root, "ffmpeg")
    if ffmpeg:
        env["HYPERFRAMES_FFMPEG_PATH"] = str(ffmpeg)
        env["PATH"] = str(ffmpeg.parent) + os.pathsep + env.get("PATH", "")
    managed_browser = root / "tools" / "chromium-1208" / "chrome-win64" / "chrome.exe"
    if managed_browser.is_file():
        env["HYPERFRAMES_BROWSER_PATH"] = str(managed_browser)
    return env


def version(path, env):
    if path is None:
        return {"available": False}
    try:
        result = subprocess.run([str(path), "-version" if path.stem.lower() == "ffmpeg" else "--version"],
                                capture_output=True, text=True, timeout=15, env=env, check=False)
        line = (result.stdout or result.stderr).splitlines()
        return {"available": result.returncode == 0, "path": str(path), "version": line[0] if line else "unknown"}
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"available": False, "path": str(path), "error": type(error).__name__}


def doctor(args):
    root = root_path(args.hermes_root)
    runtime = Path(args.runtime).expanduser().absolute() if args.runtime else root / "msshi-private" / "brag-runtime"
    package = runtime / "node_modules" / "hyperframes" / "package.json"
    cli = package.parent / "bin" / "hyperframes.mjs"
    renderer = {"installed": False, "expected_version": HYPERFRAMES_VERSION, "path": str(cli), "smoke_verified": False}
    if package.is_file():
        data = json.loads(package.read_text(encoding="utf-8-sig"))
        renderer.update({"version": data.get("version"), "license": data.get("license"),
                         "installed": data.get("version") == HYPERFRAMES_VERSION and cli.is_file()})
        if cli.is_file():
            renderer["entrypoint_sha256"] = digest(cli)
    receipt = runtime / "verification" / "smoke-audit.json"
    if renderer["installed"] and receipt.is_file():
        proof = json.loads(receipt.read_text(encoding="utf-8-sig"))
        movie = Path(proof.get("output", ""))
        lock = runtime / "package-lock.json"
        renderer["smoke_verified"] = bool(
            proof.get("status") == "passed" and proof.get("hyperframes_version") == HYPERFRAMES_VERSION
            and proof.get("entrypoint_sha256") == renderer.get("entrypoint_sha256")
            and lock.is_file() and proof.get("package_lock_sha256") == digest(lock)
            and movie.is_file() and proof.get("output_sha256") == digest(movie))
        renderer["verification_receipt"] = str(receipt)
    env = renderer_environment(root, runtime)
    node = version(tool(root, "node"), env)
    ffmpeg = version(tool(root, "ffmpeg"), env)
    try:
        node_ok = node["available"] and int(node["version"].lstrip("v").split(".")[0]) >= 22
    except (KeyError, ValueError):
        node_ok = False
    return {"scope": "kiki-chii", "upstream_commit": UPSTREAM_COMMIT,
            "concept_scaffolding_ready": True, "node": node, "ffmpeg": ffmpeg, "renderer": renderer,
            "resource_budget": resource_budget(runtime),
            "tiny_local_render_verified": bool(node_ok and ffmpeg["available"] and renderer["smoke_verified"]),
            "production_video": "requires project, approved concepts/storyboard/preview, assets and human review",
            "network_calls": 0, "llm_calls": 0, "paid_operations": 0}


def initialize(args):
    project = Path(args.project).expanduser().absolute()
    if not project.is_dir():
        raise ValueError("--project must name an existing authorized project directory")
    output = checked_destination(args.output)
    if output == project or project.is_relative_to(output):
        raise ValueError("Choose a new child or separate output folder, not the project or an ancestor")
    if not 15 <= args.duration <= 25:
        raise ValueError("The initial BRAG brief duration must be 15–25 seconds")
    if "\n" in args.title or "\r" in args.title:
        raise ValueError("--title must be a single line")
    output.mkdir(parents=True, exist_ok=False)
    request = {"schema": 1, "created_utc": datetime.now(timezone.utc).isoformat(), "scope": "kiki-chii",
               "project": str(project), "title": args.title, "duration_seconds": args.duration,
               "format": args.format, "fps": 30, "tone": args.tone, "voice": False,
               "upstream_commit": UPSTREAM_COMMIT, "renderer_version": HYPERFRAMES_VERSION,
               "stage": "concept_pending_human_review", "project_contents_read": False,
               "human_approvals": [], "generated_media": []}
    (output / "request.json").write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    concept = f"""# Concepting First: {args.title}

Status: scaffold only; no creative stage approved.

Purpose and audience: TODO
Verified product promise and evidence: TODO
Actual entry → action → result flow: TODO
Authorized public/source material: TODO
Format: {args.format}; 30 fps; target {args.duration} seconds
Tone: {args.tone}

## Three distinct concepts

1. TODO — premise, hook, why it fits this product
2. TODO — a different premise and hook
3. TODO — a different premise and hook

Recommendation and reason: TODO
User's choice and feedback: PENDING
Resource/time/spending estimate and dependencies: TODO
Assets, licenses, and attribution: TODO
Missing facts: TODO

Stop for human concept selection before scripting or media generation.
"""
    (output / "CONCEPT.md").write_text(concept, encoding="utf-8")
    review = """# Human review gates

Each row needs an actual user decision with the reviewed artifact/version.
An automated check, installation permission, or scaffold is never approval.

| Stage | Reviewed artifact/version | Human feedback and decision | Status |
| --- | --- | --- | --- |
| Concepting First | CONCEPT.md | | PENDING |
| Script/storyboard | brag-plan.md | | PENDING |
| Rough composition | rough frames/preview | | PENDING |
| Polished preview | preview, checks, audio and rights | | PENDING |
| Final delivery | decoded MP4, poster, source and credits | | PENDING |

Publishing or messaging is a separate explicit action.
"""
    (output / "REVIEW.md").write_text(review, encoding="utf-8")
    return {"output": str(output), "files": ["request.json", "CONCEPT.md", "REVIEW.md"],
            "stage": request["stage"], "project_contents_read": False,
            "network_calls": 0, "llm_calls": 0, "paid_operations": 0}


def run_renderer(args):
    root = root_path(args.hermes_root)
    runtime = checked_destination(args.runtime or root / "msshi-private" / "brag-runtime")
    package = runtime / "node_modules" / "hyperframes" / "package.json"
    cli = package.parent / "bin" / "hyperframes.mjs"
    if not package.is_file() or json.loads(package.read_text(encoding="utf-8-sig")).get("version") != HYPERFRAMES_VERSION or not cli.is_file():
        raise ValueError(f"Pinned Hyperframes {HYPERFRAMES_VERSION} is missing; follow docs/BRAG.md setup")
    node = tool(root, "node")
    if not node:
        raise ValueError("Node.js 22+ is required")
    env = renderer_environment(root, runtime)
    node_info = version(node, env)
    if not node_info["available"] or int(node_info["version"].lstrip("v").split(".")[0]) < 22:
        raise ValueError("Node.js 22+ is required")
    if args.action != "doctor" and not env.get("HYPERFRAMES_BROWSER_PATH"):
        raise ValueError("Set HYPERFRAMES_BROWSER_PATH to a local Chromium executable; no browser is downloaded automatically")
    budget = resource_budget(runtime)
    if args.action != "doctor" and not budget["browser_diagnostic_allowed"]:
        return {"action": args.action, "returncode": 3, "started_browser": False,
                "reason": "Insufficient or unverifiable memory/commit/disk budget. Close unneeded apps yourself, then rerun doctor.",
                "resource_budget": budget}
    for folder in (runtime / "process-home", runtime / "config", runtime / "cache", runtime / "temp"):
        checked_destination(folder).mkdir(parents=True, exist_ok=True)
    project = Path(args.project).expanduser().absolute() if args.project else None
    if args.action != "doctor" and (project is None or not (project / "index.html").is_file()):
        raise ValueError("--project must name an authorized composition containing index.html")
    command = [str(node), str(cli), args.action]
    if args.action == "doctor":
        command += ["--json"]
    elif args.action == "check":
        command += [str(project), "--json"]
    else:
        if not args.human_approved_preview:
            raise ValueError("Rendering requires --human-approved-preview after the user reviewed this exact preview")
        if not args.output:
            raise ValueError("--output is required for a render")
        output = checked_destination(args.output)
        if output.exists():
            raise ValueError("Output already exists; choose a new filename")
        if output.suffix.lower() != ".mp4" or not output.parent.is_dir():
            raise ValueError("--output must be a new .mp4 in an existing output directory")
        check = subprocess.run([str(node), str(cli), "check", str(project), "--json"], env=env, cwd=project, check=False)
        if check.returncode:
            return {"action": "check", "returncode": check.returncode, "rendered": False}
        budget = resource_budget(runtime)
        if not budget["browser_diagnostic_allowed"]:
            return {"action": "render", "returncode": 3, "rendered": False,
                    "reason": "Resource budget dropped after the composition check; render was not started.",
                    "resource_budget": budget}
        command += [str(project), "--output", str(output), "--workers", "1", "--low-memory-mode",
                    "--no-browser-gpu", "--no-best-effort", "--quality", args.quality]
    if args.action == "doctor":
        result = subprocess.run(command, env=env, cwd=runtime, capture_output=True, text=True, check=False)
        report = json.loads(result.stdout)
        return {"action": "doctor", "returncode": result.returncode or (0 if report.get("ok") else 2),
                "upstream_report": report, "cloud_render": False, "telemetry": False,
                "credentials_seeded_from_user_home": False}
    result = subprocess.run(command, env=env, cwd=project or runtime, check=False)
    return {"action": args.action, "returncode": result.returncode, "workers": 1,
            "cloud_render": False, "telemetry": False, "credentials_seeded_from_user_home": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("doctor", help="Read local tool/version/verification status; no downloads or browser launch")
    check.add_argument("--hermes-root")
    check.add_argument("--runtime")
    create = commands.add_parser("init", help="Create a new concept/review scaffold without reading project contents")
    create.add_argument("--project", required=True)
    create.add_argument("--output", required=True)
    create.add_argument("--title", default="Project launch")
    create.add_argument("--duration", type=int, default=20)
    create.add_argument("--format", choices=("landscape", "vertical", "square"), default="landscape")
    create.add_argument("--tone", default="polished")
    local = commands.add_parser("renderer", help="Run only the pinned local doctor/check/render, with an isolated process home")
    local.add_argument("action", choices=("doctor", "check", "render"))
    local.add_argument("--hermes-root")
    local.add_argument("--runtime")
    local.add_argument("--project")
    local.add_argument("--output")
    local.add_argument("--quality", choices=("draft", "delivery"), default="draft")
    local.add_argument("--human-approved-preview", action="store_true")
    for action in ("check", "render"):
        direct = commands.add_parser(action, help="Run the pinned local " + action + " with resource checks")
        direct.set_defaults(action=action)
        direct.add_argument("--hermes-root")
        direct.add_argument("--runtime")
        direct.add_argument("--project", required=True)
        direct.add_argument("--output")
        direct.add_argument("--quality", choices=("draft", "delivery"), default="draft")
        direct.add_argument("--human-approved-preview", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = doctor(args) if args.command == "doctor" else initialize(args) if args.command == "init" else run_renderer(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return result.get("returncode", 0)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
