#!/usr/bin/env python3
"""Private child entry point for the pinned, deterministic Harness2 demo only."""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import socket
import subprocess
import sys
import time
import types
from pathlib import Path


def deny_network(*args, **kwargs):
    raise PermissionError("Network access is disabled in the MSSHI deterministic demo")


def windows_demo_flock():
    """Implement only the two flock operations used by this demo's summary writer."""
    if os.name != "nt":
        return False
    import msvcrt
    shim = types.ModuleType("fcntl")
    shim.LOCK_EX, shim.LOCK_UN = 2, 8

    def flock(file, operation):
        if operation not in (shim.LOCK_EX, shim.LOCK_UN):
            raise ValueError("Demo flock supports LOCK_EX and LOCK_UN only")
        position = file.tell()
        file.seek(0)
        try:
            if operation == shim.LOCK_UN:
                msvcrt.locking(file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                deadline = time.monotonic() + 30
                while True:
                    try:
                        msvcrt.locking(file.fileno(), msvcrt.LK_NBLCK, 1)
                        break
                    except OSError:
                        if time.monotonic() >= deadline:
                            raise TimeoutError("Timed out acquiring demo summary lock")
                        time.sleep(0.025)
        finally:
            file.seek(position)

    shim.flock = flock
    sys.modules["fcntl"] = shim
    return True


def ledger_process_guard(root, allowed_scripts):
    original = subprocess.Popen

    def guarded(command, *args, **kwargs):
        if not isinstance(command, (list, tuple)) or len(command) != 3 or kwargs.get("shell") or kwargs.get("executable"):
            raise PermissionError("Only the reviewed local ledger Python execution is allowed")
        executable, script, ledger = map(Path, command)
        if executable.resolve() != Path(sys.executable).resolve():
            raise PermissionError("The demo may only execute its isolated Python interpreter")
        script, ledger = script.resolve(), ledger.resolve()
        if not script.is_relative_to(root) or not ledger.is_relative_to(root) or script.name != "summarize.py" or ledger.name != "ledger.csv":
            raise PermissionError("The demo may only execute generated files inside its output")
        if script.read_text(encoding="utf-8").replace("\r\n", "\n") not in allowed_scripts:
            raise PermissionError("The generated ledger program differs from the reviewed deterministic fixture")
        return original(command, *args, **kwargs)

    subprocess.Popen = guarded
    return guarded


def windows_demo_tree_keys():
    """Normalize the demo's in-memory component keys; do not change installed source."""
    if os.name != "nt":
        return False
    from harness2.core import tree
    original = tree.read_tree

    def read_tree(surface, directory, *, rejected=None):
        off_surface = []
        result = original(surface, directory, rejected=off_surface)
        stubs = {name for name, _ in surface.stubs}
        if rejected is not None:
            rejected.extend(tree.normalize_rel(name) for name in off_surface if tree.normalize_rel(name) not in stubs)
        return {tree.normalize_rel(name): value for name, value in result.items()}

    tree.read_tree = read_tree
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    root = args.output.resolve()
    if Path.cwd().resolve() != root or (root / ".env").exists() or (root / "pyproject.toml").exists():
        raise ValueError("The demo requires a fresh output CWD without .env or pyproject.toml")
    if set(p.name for p in root.iterdir()) - {"worker.log"}:
        raise ValueError("The worker output directory is not fresh")
    for name in os.environ:
        if any(token in name.upper() for token in ("API_KEY", "TOKEN", "SECRET", "CREDENTIAL", "VERTEX", "CODEX", "ANTHROPIC", "GEMINI", "PROXY")):
            raise ValueError(f"Credential-related environment variable was inherited: {name}")
    socket.socket.connect = deny_network
    socket.socket.connect_ex = deny_network
    socket.socket.sendto = deny_network
    socket.create_connection = deny_network
    socket.getaddrinfo = deny_network
    shim = windows_demo_flock()
    import harness2
    from harness2.demo import BASE_SCRIPT
    from harness2.cli.demo import main as upstream_demo
    tree_shim = windows_demo_tree_keys()
    guarded = ledger_process_guard(root, {BASE_SCRIPT, BASE_SCRIPT.replace(" if amount > 0", "")})
    # Behavioral guards are exercised before the real deterministic workflow.
    try:
        socket.create_connection(("127.0.0.1", 9))
    except PermissionError:
        network_guard = True
    else:
        raise AssertionError("Network guard did not reject a connection")
    try:
        guarded(["gcloud", "auth", "list"])
    except PermissionError:
        process_guard = True
    else:
        raise AssertionError("Process guard did not reject a cloud command")
    code = upstream_demo(["--output", str(root), "--k", "2", "--mode", "both"])
    report = json.loads((root / "demo.json").read_text(encoding="utf-8"))
    summaries = sorted((root / "runs").rglob("summary.json"))
    selected = []
    for summary in summaries:
        value = json.loads(summary.read_text(encoding="utf-8"))
        for mode, selection in value.get("selections", {}).items():
            selected.append({"task": value.get("task_id"), "mode": mode, "selection": selection})
    if len(selected) != 4 or {r["mode"] for r in selected} != {"agg", "seq"} or not all(r["selection"].get("ok") and not r["selection"].get("chosen_is_base") for r in selected):
        raise AssertionError("Both modes must select an improved candidate for each ledger")
    # Exact signed totals prove that the fixture changed observable behavior.
    answers = [p.read_text(encoding="utf-8").strip() for p in (root / "executions").rglob("answer.txt")]
    totals = {"ledger-1": "Total: 85.15", "ledger-2": "Total: 20.25"}
    if code or report.get("failed") != 0 or report.get("done") != 2 or not all(t in answers for t in totals.values()):
        raise AssertionError("The real upstream deterministic demo did not complete both ledgers correctly")
    proof = {"success": True, "demo_only": True, "python": sys.version, "package_version": importlib.metadata.version("harness2"), "package_path": str(Path(harness2.__file__).resolve()), "recursion_budget": 2, "modes": ["parallel", "sequential"], "done": report["done"], "failed": report["failed"], "execution_count": report["execution_count"], "editor_calls": report["editor_calls"], "observed_signed_totals": totals, "network_guard_exercised": network_guard, "process_guard_exercised": process_guard, "windows_demo_flock_shim": shim, "windows_demo_tree_key_shim": tree_shim, "fresh_cwd_without_dotenv": True, "credential_environment_allowlisted": True, "api_calls_made": 0, "live_harness_mutated": False, "selection_records": len(selected), "limitation": "Deterministic demo proof only; not model-backed benchmark validation or general Windows support"}
    (root / "MSSHI_DEMO_PROOF.json").write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
