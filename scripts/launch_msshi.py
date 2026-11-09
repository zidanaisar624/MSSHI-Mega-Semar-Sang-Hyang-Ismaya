"""Stable launcher copied to the MSSHI user data directory."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys


def main():
    home = Path(__file__).resolve().parent
    try:
        state = json.loads((home / "state.json").read_text(encoding="utf-8"))
        release = state["current"]
        if not re.fullmatch(r"(?:[0-9a-f]{24}|[0-9a-f]{64})", release):
            raise ValueError("ID rilis lokal tidak valid.")
        command = home / "releases" / release / "scripts" / "msshi_cli.py"
        if not command.is_file():
            raise FileNotFoundError(command)
        os.environ["MSSHI_HOME"] = str(home)
        return subprocess.call([sys.executable, "-B", "-X", "utf8", str(command), *sys.argv[1:]])
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"msshi: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
