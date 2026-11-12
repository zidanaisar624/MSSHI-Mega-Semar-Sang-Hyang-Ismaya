"""Inventory local persona sources without uploading them or changing source files."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import zipfile


EXCLUDED = {".git", "node_modules", "__pycache__", "venv", ".venv", "upstreams",
            "msshi-upstream", "installs", "backups", "temp", ".hub"}


def collect(roots):
    found = {"souls": [], "voice_samples": [], "notebook_sources": [], "archives": []}
    seen = set()
    for root in roots:
        for directory, dirs, names in os.walk(root, followlinks=False):
            dirs[:] = [name for name in dirs if name not in EXCLUDED
                       and not Path(directory, name).is_symlink()
                       and not getattr(Path(directory, name).lstat(), "st_file_attributes", 0) & 0x400]
            for name in names:
                path = Path(directory, name)
                if path in seen or path.is_symlink():
                    continue
                seen.add(path)
                lower = name.lower()
                group = ("souls" if lower == "soul.md" else
                         "voice_samples" if path.suffix.lower() in {".mp3", ".wav", ".flac"} else
                         "notebook_sources" if any(word in lower for word in ("notebook", "600", "knowledge_base")) else
                         "archives" if lower.startswith("paket_lengkap_chatgpt") and lower.endswith(".zip") else None)
                if group:
                    found[group].append({"path": str(path), "bytes": path.stat().st_size})
                    if group == "archives":
                        with zipfile.ZipFile(path) as archive:
                            found[group][-1]["entries"] = len(archive.infolist())
                            found[group][-1]["audio_entries"] = [info.filename for info in archive.infolist()
                                if Path(info.filename).suffix.lower() in {".mp3", ".wav", ".flac"}]
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = collect(args.root)
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(json.dumps({"counts": {name: len(rows) for name, rows in result.items()},
                          "output": str(args.output)}, indent=2))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
