"""Expose the self-contained CLI-Anything skill runtime to the MSSHI CLI."""
from pathlib import Path
from runpy import run_path


_BRIDGE_DIR = Path(__file__).resolve().parents[1] / "skills" / "cli-anything-universal-bridge" / "scripts"
_bridge = run_path(str(_BRIDGE_DIR / "setup_cli_anything_hermes.py"))

configure_parser = _bridge["configure_parser"]
plan_connections = _bridge["plan_connections"]
registry_lock = _bridge["registry_lock"]
run = _bridge["run"]
status = _bridge["status"]
main = _bridge["main"]

if __name__ == "__main__":
    raise SystemExit(main())
