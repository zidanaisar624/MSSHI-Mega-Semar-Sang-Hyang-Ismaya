#!/usr/bin/env python3
"""Scan repository text files for leaked credentials, tokens, private paths, and sensitive files."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv"}
SENSITIVE_FILENAMES = re.compile(
    r"(?:^|/)(?:\.env(?:\.[^/]+)?|[^/]+\.(?:pem|key|p12)|auth\.json|credentials\.json)$",
    re.I,
)
SECRET_PATTERNS = re.compile(
    r"(?<![\w-])(?:sk-[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{30,}|"
    r"github_pat_[A-Za-z0-9_]{30,}|AIza[A-Za-z0-9_-]{35})"
    r"|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
)
PRIVATE_PATTERNS = re.compile(
    r"[A-Z]:\\" + r"Zidan\\|https?://(?:notebooklm|notebook)\.google\.com/notebook/",
    re.I,
)
TEXT_EXTENSIONS = {
    ".json", ".md", ".py", ".ps1", ".sh", ".svg", ".cmd", ".bat", ".txt", ".yml", ".yaml", ".ipynb"
}


def scan_repository(repo_root: Path) -> dict:
    findings: list[dict] = []
    files_scanned = 0
    for folder, dirs, files in os.walk(repo_root):
        parent = Path(folder)
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".msshi-check-")]
        for name in files:
            path = parent / name
            rel = path.relative_to(repo_root).as_posix()
            if name != ".env.example" and SENSITIVE_FILENAMES.search(rel):
                findings.append({"type": "sensitive_file", "file": rel, "detail": "Blocked secret filename"})
            if path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            files_scanned += 1
            try:
                text = path.read_text(encoding="utf-8-sig")
            except UnicodeDecodeError:
                text = path.read_text(encoding="utf-8", errors="ignore")
            if m := SECRET_PATTERNS.search(text):
                findings.append({"type": "secret_token", "file": rel, "detail": m.group(0)[:12] + "..."})
            if m := PRIVATE_PATTERNS.search(text):
                findings.append({"type": "private_reference", "file": rel, "detail": m.group(0)})
    return {
        "status": "PASS" if not findings else "FAIL",
        "repo_root": str(repo_root),
        "files_scanned": files_scanned,
        "findings_count": len(findings),
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MSSHI repository secret and privacy guardrail scanner.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root directory to scan.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)
    report = scan_repository(args.root.expanduser().resolve())
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"[secret_scan] status={report['status']} files_scanned={report['files_scanned']} findings={report['findings_count']}")
        for item in report["findings"]:
            print(f"  - [{item['type']}] {item['file']}: {item['detail']}")
    return 0 if report["findings_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
