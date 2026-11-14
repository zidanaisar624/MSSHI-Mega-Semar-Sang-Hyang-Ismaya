#!/usr/bin/env python3
"""MSSHI System & MuZA Skripsi Readiness Doctor (read-only check)."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from msshi_sources import data_root


def inject_adaptive_pylibs():
    candidates = [
        Path.home() / "HermesData" / "skripsi-pylibs",
        Path("D:/HermesData/skripsi-pylibs"),
    ]
    found = []
    for cand in candidates:
        if cand.is_dir():
            s = str(cand)
            if s not in sys.path:
                sys.path.insert(0, s)
            found.append(s)
    return found


def has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def find_soffice() -> str | None:
    found = shutil.which("soffice") or shutil.which("libreoffice")
    if found:
        return found
    for c in (
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\LibreOffice\program\soffice.exe"),
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/usr/bin/soffice",
    ):
        if c and os.path.exists(c):
            return c
    return None


def adaptive_skripsi_output() -> Path:
    if os.name == "nt" and Path("D:/").exists():
        d_root = Path("D:/HermesData")
        if d_root.exists() or os.access("D:/", os.W_OK):
            return d_root / "Skripsi_Output"
    return Path.home() / "Documents" / "MuZA_Skripsi_Output"


def diagnose() -> dict:
    pylibs = inject_adaptive_pylibs()
    version = json.loads((ROOT / "VERSION.json").read_text(encoding="utf-8-sig"))
    matrix = json.loads((ROOT / "configs" / "bot_role_and_skill_matrix.json").read_text(encoding="utf-8-sig"))
    sam = json.loads((ROOT / "configs" / "manifests" / "skill_activation_matrix.json").read_text(encoding="utf-8-sig"))

    disk_skills = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
    matrix_bundled = sorted(row["slug"] for row in matrix["skills"] if row.get("status") == "bundled")

    skripsi_dir = ROOT / "skills" / "muza-skripsi-template"
    skripsi_files = [
        "SKILL.md",
        "scripts/build_template.py",
        "scripts/campus_lookup.py",
        "scripts/extract_guideline.py",
        "references/spec_schema.md",
        "assets/example_spec.json",
        "assets/presets/preset_informatika_ilkom.json",
        "assets/presets/preset_kuantitatif.json",
        "assets/presets/preset_kualitatif.json",
        "assets/presets/preset_rnd.json",
        "assets/presets/preset_ptk.json",
    ]
    skripsi_present = {rel: (skripsi_dir / rel).is_file() for rel in skripsi_files}
    notebooks_present = {
        name: (ROOT / "notebooks" / "skripsi" / name).is_file()
        for name in ("MuZA_Search.ipynb", "MuZA_Skripsi_Builder.ipynb")
    }

    home = data_root()
    drive_d_exists = Path("D:/").exists() if os.name == "nt" else False
    try:
        disk_free_mb = round(shutil.disk_usage(home if home.exists() else ROOT).free / (1024 * 1024), 1)
    except OSError:
        disk_free_mb = None

    deps = {mod: has_module(mod) for mod in ("docx", "lxml", "pypdf", "PIL", "reportlab")}
    tools = {
        "git": shutil.which("git"),
        "node": shutil.which("node"),
        "soffice": find_soffice(),
    }

    routing_locked = (
        matrix.get("shared_foundation", {}).get("jev_model_routing") is False
        and sam.get("app_connection_policy", {}).get("jev_model_routing") is False
    )
    parity_ok = (
        len(disk_skills) == version.get("bundled_skills") == len(matrix_bundled)
        and disk_skills == matrix_bundled
    )
    skripsi_ok = all(skripsi_present.values()) and all(notebooks_present.values()) and (ROOT / "MULAI_SKRIPSI_DRAG_AND_DROP.bat").is_file()

    return {
        "suite": version.get("suite_name"),
        "version": version.get("version"),
        "bundled_skills": len(disk_skills),
        "core_skills": version.get("core_skills"),
        "wrappers": version.get("integration_wrappers"),
        "external_sources": version.get("external_sources"),
        "parity_ok": parity_ok,
        "provider_model_routing_locked": routing_locked,
        "adaptive_hermes_data": str(home),
        "adaptive_skripsi_output": str(adaptive_skripsi_output()),
        "drive_d_available": drive_d_exists,
        "target_drive_free_mb": disk_free_mb,
        "pylibs_detected": pylibs,
        "python_modules": deps,
        "tools": tools,
        "muza_skripsi_ready": skripsi_ok,
        "muza_skripsi_files_count": sum(skripsi_present.values()),
        "notebooks_present": notebooks_present,
        "pdf_guides_present": (ROOT / "docs" / "pdf-guides" / "Panduan_Master_MSSHI_v3.1.0.pdf").is_file(),
        "status": "HEALTHY" if (parity_ok and routing_locked and skripsi_ok and deps["docx"] and deps["lxml"]) else "NEEDS_ATTENTION",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="MSSHI system & MuZA Skripsi health check (read-only).")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    args = parser.parse_args(argv)
    report = diagnose()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"=== MSSHI DOCTOR ({report['version']}) ===")
        print(f"Status                : {report['status']}")
        print(f"Skills Parity         : {report['parity_ok']} ({report['bundled_skills']} bundled = {report['core_skills']} core + {report['wrappers']} wrappers; {report['external_sources']} upstreams)")
        print(f"Provider/Model Lock   : {report['provider_model_routing_locked']} (jev_model_routing: false)")
        print(f"Adaptive Data Root    : {report['adaptive_hermes_data']} (Drive D: {report['drive_d_available']}, free: {report['target_drive_free_mb']} MB)")
        print(f"Adaptive Skripsi Out  : {report['adaptive_skripsi_output']}")
        print(f"MuZA Skripsi v1.1     : {report['muza_skripsi_ready']} ({report['muza_skripsi_files_count']}/11 skill files)")
        print(f"Python Modules        : {report['python_modules']}")
        print(f"External Binaries     : git={bool(report['tools']['git'])}, node={bool(report['tools']['node'])}, libreoffice={bool(report['tools']['soffice'])}")
        print(f"PDF Guides Dir        : {report['pdf_guides_present']}")
    return 0 if report["parity_ok"] and report["provider_model_routing_locked"] and report["muza_skripsi_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
