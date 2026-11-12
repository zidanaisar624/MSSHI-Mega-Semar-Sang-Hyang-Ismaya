"""Compact structured context locally and report exactly what was changed."""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
import sys

def compact(text, kind):
    if kind == "json":
        return json.dumps(json.loads(text), ensure_ascii=False, separators=(",", ":")), {"mode": "json", "lossy": False}
    groups = []
    duplicates = 0
    for line, matches in itertools.groupby(text.splitlines()):
        count = sum(1 for _ in matches)
        groups.append(line)
        if count > 1:
            groups.append(f"[previous line repeated {count - 1} additional times]")
            duplicates += count - 1
    return "\n".join(groups), {"mode": "log", "repeated_lines": duplicates, "lossy": True,
                              "representation": "run-length encoded consecutive lines"}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--format", choices=("json", "log", "auto"), default="auto")
    parser.add_argument("--max-bytes", type=int, default=4 * 1024 * 1024)
    args = parser.parse_args(argv)
    if not 1 <= args.max_bytes <= 16 * 1024 * 1024:
        parser.error("max-bytes must be between 1 and 16777216")
    if args.file.stat().st_size > args.max_bytes:
        parser.error("File exceeds the configured read budget. Choose a relevant slice first.")
    text = args.file.read_text(encoding="utf-8-sig")
    kind = args.format
    if kind == "auto":
        kind = "json" if args.file.suffix.lower() == ".json" else "log"
    try:
        output, info = compact(text, kind)
    except ValueError as error:
        parser.error(str(error))
    info.update(input_bytes=len(text.encode()), output_bytes=len(output.encode()), llm_calls=0)
    print(output)
    print(json.dumps(info, ensure_ascii=False), file=sys.stderr)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
