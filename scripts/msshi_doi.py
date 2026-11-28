#!/usr/bin/env python3
"""MSSHI CLI wrapper for Bot Val's 2-Layer Legal DOI & Academic Paper Search Engine."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
VAL_SCRIPTS = ROOT / "skills" / "val-doi-research" / "scripts"
DOI_ENGINE = VAL_SCRIPTS / "doi_engine.py"
SEARCH_ENGINE = VAL_SCRIPTS / "search_paper_engine.py"


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] in {"topic", "topik", "paper-search"}:
        target = SEARCH_ENGINE
        forwarded = args[1:]
    else:
        target = DOI_ENGINE
        forwarded = args
    if not target.is_file():
        sys.stderr.write(f"msshi doi: engine script missing: {target}\n")
        return 1
    return subprocess.call([sys.executable, "-B", "-X", "utf8", str(target), *forwarded])


if __name__ == "__main__":
    raise SystemExit(main())
