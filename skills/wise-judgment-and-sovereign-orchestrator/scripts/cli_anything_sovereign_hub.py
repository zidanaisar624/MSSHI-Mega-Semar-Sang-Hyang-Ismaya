"""Compatibility entry point for the shared MSSHI CLI."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    skill = Path(__file__).resolve().parents[2] / "persona-shizuka-yukino-shikaku"
    entry = skill / "scripts" / "cli_anything_sovereign_hub.py"
    if not entry.is_file():
        raise SystemExit("Install the shared persona skill or run the CLI from the MSSHI checkout.")
    runpy.run_path(str(entry), run_name="__main__")
