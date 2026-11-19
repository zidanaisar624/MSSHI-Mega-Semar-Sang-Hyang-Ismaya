#!/usr/bin/env python3
"""MSSHI readiness diagnostics; default read-only, optional ownership-proven repair."""
from __future__ import annotations

import argparse
import hashlib
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
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError, AttributeError):
        return False


def _issue(issues, code, message, command, *, severity="warning", profile=None):
    row = {"code": code, "severity": severity, "message": message, "suggested_command": command}
    if profile:
        row["profile"] = profile
    issues.append(row)


def _json(path, issues, component, *, required=False):
    try:
        if path.is_symlink() or (path.exists() and getattr(path.lstat(), "st_file_attributes", 0) & 0x400):
            raise ValueError("linked")
        if path.stat().st_size > 4 * 1024 * 1024:
            raise ValueError("oversized")
        value = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(value, dict):
            raise ValueError("mapping required")
        return value
    except FileNotFoundError:
        if required:
            _issue(issues, "MISSING_METADATA", component + " belum tersedia.", "msshi update", severity="error")
    except (OSError, ValueError, UnicodeError):
        _issue(issues, "INVALID_METADATA", component + " tidak dapat dibaca dengan aman.", "msshi update", severity="error")
    return {}


def _native_health(issues):
    """Metadata only: no native plugin registration or account/model requests."""
    import msshi_hermes_profiles as hp
    import msshi_interaction as interaction
    try:
        home = hp.resolve_hermes_home(create_adaptive=False)
        if not (home / "config.yaml").is_file() and not (home / "profiles").is_dir():
            return {"status": "NOT_INSTALLED", "profiles": [], "provider_execution_tested": False}
        mapping = hp.team_role_profiles(home)
        team = (home / "msshi-runtime/team-layout.json").is_file() or any(
            (home / "profiles" / role).is_dir() for role in hp.TEAM_ROLE_IDS)
        expected = mapping if team else {"default": "default"}
        controller = interaction._plugin(ROOT)
        rows = []
        for role, native_id in expected.items():
            folder = home if native_id == "default" else home / "profiles" / native_id
            cfg_path = folder / "config.yaml"
            row = {"role": role, "profile": native_id, "native_config_present": cfg_path.is_file()}
            rows.append(row)
            if not cfg_path.is_file():
                _issue(issues, "MISSING_NATIVE_PROFILE", "Profil tim belum selesai disiapkan.", "msshi desktop", profile=role)
                continue
            try:
                # Existing safety helper rejects links/junctions before reading.
                controller._ordinary(cfg_path)
                raw = cfg_path.read_bytes()
                if len(raw) > 4 * 1024 * 1024:
                    raise ValueError("oversized")
                cfg = hp.load_yaml_mapping(raw)
                if not cfg:
                    raise ValueError("empty")
            except Exception:
                row["config_status"] = "UNREADABLE"
                _issue(issues, "INVALID_NATIVE_CONFIG", "Konfigurasi profil tidak dapat dibaca; nilainya tidak ditampilkan.", "Periksa konfigurasi melalui Settings Hermes dan cadangan pribadi.", severity="error", profile=role)
                continue
            row["config_status"] = "READABLE"
            plugins = cfg.get("plugins") or {}
            plugins = plugins if isinstance(plugins, dict) else {}
            enabled = plugins.get("enabled") or []
            disabled = plugins.get("disabled") or []
            entries = plugins.get("entries") or {}
            entries = entries if isinstance(entries, dict) else {}
            for plugin in ("msshi-auto-trim", *(["msshi-interaction"] if team else [])):
                entry = entries.get(plugin) or {}
                entry = entry if isinstance(entry, dict) else {}
                settings = entry.get("settings") or {}
                settings = settings if isinstance(settings, dict) else {}
                explicitly_off = plugin in disabled or (isinstance(enabled, dict) and enabled.get(plugin) is False) or settings.get("enabled") is False
                active = (enabled.get(plugin) is True if isinstance(enabled, dict) else plugin in enabled) and not explicitly_off
                present = all((folder / "plugins" / plugin / name).is_file() for name in ("plugin.yaml", "__init__.py"))
                row[plugin] = "DISABLED_BY_USER" if explicitly_off else "REGISTERED_NOT_EXECUTION_TESTED" if active and present else "SETUP_REQUIRED"
                if not explicitly_off and not (active and present):
                    cmd = "msshi trim --install --apply --download-runtime" if plugin == "msshi-auto-trim" else "msshi interaction --install --apply"
                    _issue(issues, "PLUGIN_SETUP_REQUIRED", plugin + " memerlukan pemeriksaan pemasangan/aktivasi.", cmd, profile=role)
                if plugin == "msshi-auto-trim" and active and not explicitly_off:
                    binary = settings.get("binary")
                    try:
                        exists = controller._ordinary(binary).is_file() if isinstance(binary, str) and binary else bool(shutil.which("llmtrim"))
                    except (OSError, ValueError):
                        exists = False
                    row["trim_binary_present"] = exists
                    if not exists:
                        _issue(issues, "TRIM_RUNTIME_MISSING", "Hook trim aktif tetapi executable lokal belum tersedia/terbaca.", "msshi trim --install --apply --download-runtime", profile=role)
            row["skill_folders"] = sum(1 for _ in (folder / "skills").glob("*/SKILL.md"))
            if team and row["skill_folders"] == 0:
                _issue(issues, "PROFILE_SKILLS_MISSING", "Belum ada folder skill pada profil ini; pilih ulang paket yang sesuai.", "msshi setup", profile=role)
            soul = folder / "SOUL.md"
            try:
                content = soul.read_bytes()
                content.decode("utf-8-sig")
                row["soul_valid_utf8_nul_free"] = bool(content) and b"\x00" not in content
            except (OSError, UnicodeError):
                row["soul_valid_utf8_nul_free"] = False
            if not row["soul_valid_utf8_nul_free"]:
                _issue(issues, "SOUL_REQUIRES_REVIEW", "SOUL kosong/rusak atau tidak tersedia; persona pribadi tidak ditimpa otomatis.", "Pulihkan SOUL dari receipt/cadangan yang sesuai, lalu msshi doctor.", profile=role)
            if role in controller.T2:
                try:
                    entry = entries.get("msshi-interaction") or {}
                    opts = entry.get("settings") or entry.get("config") or {}
                    _, _, readiness, _ = controller.council_binding(cfg, bool(opts.get("use_current_main_for_council")))
                    row["council_readiness"] = readiness
                except (AttributeError, TypeError, ValueError):
                    row["council_readiness"] = "NEEDS_COUNCIL_CONFIG"
                if row["council_readiness"] == "NEEDS_COUNCIL_CONFIG":
                    _issue(issues, "NEEDS_COUNCIL_CONFIG", "Dewan belum dipilih pengguna; Doctor tidak mengisi model/provider/endpoint.", "Atur Reference Agents dan Aggregator di Hermes, lalu msshi interaction --status.", profile=role)
            elif role in controller.T1:
                advisor = cfg.get("delegation") or {}
                configured = isinstance(advisor, dict) and bool(advisor.get("model"))
                row["advisor_readiness"] = "CONFIGURED_NOT_PROVIDER_TESTED" if configured else "NEEDS_ADVISOR_CONFIG"
                if not configured:
                    _issue(issues, "NEEDS_ADVISOR_CONFIG", "Advisor belum dipilih pengguna; Doctor tidak mengganti pilihan model.", "Atur Advisor melalui Settings Hermes, lalu msshi interaction --status.", profile=role)
            route_path = home / "msshi-runtime/profiles" / native_id / "routes.json"
            routes = _json(route_path, issues, "Metadata rute " + role) if route_path.exists() else {}
            row["auto_open_on_boot"] = routes.get("auto_open_on_boot")
            if routes.get("auto_open_on_boot") is True:
                _issue(issues, "AUTO_OPEN_ENABLED", "Rute dapat membuka aplikasi saat startup; pengaturan ini perlu ditinjau.", "msshi runtime migrate", profile=role)
        return {"status": "CONFIGURATION_INSPECTED", "profiles": rows, "provider_execution_tested": False,
                "model_calls": 0, "network_requests": 0, "apps_launched": 0}
    except Exception:
        _issue(issues, "NATIVE_DIAGNOSTICS_UNAVAILABLE", "Pemeriksaan metadata native belum dapat diselesaikan; nilai konfigurasi tidak ditampilkan.", "msshi interaction --status")
        return {"status": "INSPECTION_INCOMPLETE", "profiles": [], "provider_execution_tested": False}


def repair_owned_files():
    """Restore only missing files proven by prior MSSHI ownership hashes.

    Existing edits, config, SOUL, accounts, services, and runtime binaries are never
    written. No downloads, native plugin execution or setup wizard occur here.
    """
    import msshi_hermes_profiles as hp
    import msshi_trim_setup as safety
    from msshi_update import inventory
    from msshi_cli import fingerprint
    home = safety.checked(hp.resolve_hermes_home(create_adaptive=False))
    result = {"applied": False, "files_restored": 0, "receipt": None,
              "custom_edits_preserved": True, "protected_config_files_untouched": True,
              "network_requests": 0, "model_calls": 0, "apps_launched": 0,
              "scope": "Only missing files with existing MSSHI ownership proof; all other issues require the displayed commands."}
    if not home.is_dir():
        return result
    plans = {}
    folders = {home, *[home / "profiles" / native_id for native_id in hp.team_role_profiles(home).values() if native_id != "default"]}
    protected = {path: path.read_bytes() for folder in folders for name in ("config.yaml", ".env", "auth.json", "auth_keys.json", "SOUL.md")
                 if (path := safety.checked(folder / name)).is_file()}
    for folder in folders:
        record = safety.checked(folder / "msshi-runtime/interaction-install.json")
        if not record.is_file():
            continue
        try:
            owned = json.loads(record.read_text(encoding="utf-8-sig"))
            if owned.get("managed_by") != "msshi-interaction":
                continue
            files = owned.get("files") or {}
            for name in ("__init__.py", "plugin.yaml"):
                target = safety.checked(folder / "plugins/msshi-interaction" / name)
                source = safety.checked(ROOT / "hermes_plugins/msshi-interaction" / name)
                if not target.exists() and source.is_file():
                    incoming = source.read_bytes()
                    if hashlib.sha256(incoming).hexdigest() == files.get(name):
                        plans[target] = incoming
        except (OSError, ValueError, AttributeError):
            continue
    state_path = safety.checked(data_root() / "state.json")
    if state_path.is_file():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8-sig"))
            targets = state.get("targets") or {}
            for raw_target, managed in targets.items():
                target = safety.checked(raw_target)
                if not target.is_relative_to(home) or target.name != "skills" or not isinstance(managed, dict):
                    continue
                for slug, expected in managed.items():
                    if not isinstance(slug, str) or not slug or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in slug):
                        continue
                    source = safety.checked(ROOT / "skills" / slug)
                    current = safety.checked(target / slug)
                    if not source.is_dir():
                        continue
                    incoming = inventory(source)
                    if fingerprint(incoming) != expected:
                        continue
                    actual = inventory(current) if current.is_dir() else {}
                    if any(incoming.get(name) != digest for name, digest in actual.items()):
                        continue
                    for name in incoming.keys() - actual.keys():
                        plans[safety.checked(current / name)] = (source / name).read_bytes()
        except (OSError, ValueError, AttributeError, TypeError):
            pass
    if not plans:
        return result
    tx = hp.ProfileTransaction(home)
    try:
        for path, incoming in plans.items():
            if path.exists():
                raise ValueError("Concurrent file edit; repair cancelled")
            tx.write(path, incoming, 0o600)
        if any(not path.is_file() or path.read_bytes() != original for path, original in protected.items()):
            raise ValueError("Protected file changed during repair; repair cancelled")
        result.update(applied=True, files_restored=len(plans), receipt=tx.commit())
        return result
    except BaseException:
        tx.rollback()
        raise


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
    issues = []
    pylibs = inject_adaptive_pylibs()
    version = _json(ROOT / "VERSION.json", issues, "VERSION", required=True)
    matrix = _json(ROOT / "configs/bot_role_and_skill_matrix.json", issues, "Katalog skill", required=True)
    sam = _json(ROOT / "configs/manifests/skill_activation_matrix.json", issues, "Matriks aktivasi", required=True)

    disk_skills = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
    matrix_rows = matrix.get("skills") or []
    matrix_bundled = sorted(row["slug"] for row in matrix_rows if isinstance(row, dict) and row.get("status") == "bundled" and isinstance(row.get("slug"), str)) if isinstance(matrix_rows, list) else []

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

    foundation = matrix.get("shared_foundation") or {}
    connection = sam.get("app_connection_policy") or {}
    routing_locked = (isinstance(foundation, dict) and isinstance(connection, dict)
                      and foundation.get("jev_model_routing") is False
                      and connection.get("jev_model_routing") is False)
    parity_ok = (
        len(disk_skills) == version.get("bundled_skills") == len(matrix_bundled)
        and disk_skills == matrix_bundled
    )
    skripsi_ok = all(skripsi_present.values()) and all(notebooks_present.values()) and (ROOT / "MULAI_SKRIPSI_DRAG_AND_DROP.bat").is_file()

    if not parity_ok:
        _issue(issues, "SKILL_PARITY_FAILED", "Folder skill dan katalog rilis tidak cocok.", "msshi update", severity="error")
    if not routing_locked:
        _issue(issues, "ROUTING_POLICY_FAILED", "Kebijakan penjagaan pemilihan model perlu diperiksa.", "msshi update", severity="error")
    if not skripsi_ok:
        _issue(issues, "SKRIPSI_FILES_MISSING", "Sebagian berkas template/notebook akademik belum tersedia.", "msshi update", severity="error")
    for dep, available in deps.items():
        if not available:
            package = {"docx": "python-docx", "PIL": "Pillow"}.get(dep, dep)
            _issue(issues, "OPTIONAL_DEPENDENCY_MISSING", "Modul untuk fungsi dokumen belum tersedia: " + dep,
                   "python -m pip install " + package)
    native = _native_health(issues)
    errors = sum(row["severity"] == "error" for row in issues)
    warnings = sum(row["severity"] == "warning" for row in issues)

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
        "native": native,
        "issues": issues,
        "checks_read_only": True,
        "protected_values_included": False,
        "status": "NEEDS_ATTENTION" if errors or warnings else "HEALTHY",
        "core_status": "NEEDS_ATTENTION" if errors else "HEALTHY",
        "exit_code": 1 if errors else 2 if warnings else 0,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="MSSHI health diagnostics: read-only by default, optional scoped --fix.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--fix", action="store_true", help="Restore missing files proven MSSHI-owned; preserve custom edits and all model/provider/endpoint/account settings. No downloads or app launches.")
    args = parser.parse_args(argv)
    repair = None
    repair_failed = False
    if args.fix:
        try:
            repair = repair_owned_files()
        except (OSError, ValueError, TypeError, ImportError, AttributeError):
            repair_failed = True
            repair = {"applied": False, "status": "REPAIR_STOPPED", "note": "No unproven repair attempted; inspect receipts and the displayed suggested commands."}
    report = diagnose()
    if repair is not None:
        report["repair"] = repair
        report["checks_read_only"] = False
    if repair_failed:
        _issue(report["issues"], "REPAIR_STOPPED", "Perbaikan terhenti pada pemeriksaan pengaman; konfigurasi pribadi tidak ditulis.", "Periksa receipt yang sesuai sebelum mencoba ulang.", severity="error")
        report.update(status="NEEDS_ATTENTION", exit_code=1)
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
        print(f"Native Profiles       : {report['native']['status']} (provider execution not tested)")
        if repair is not None:
            print(f"Scoped Repair         : {repair.get('files_restored', 0)} missing MSSHI-owned files restored; receipt={repair.get('receipt')}")
        for issue in report["issues"]:
            profile = f" [{issue['profile']}]" if issue.get("profile") else ""
            print(f"{issue['severity'].upper()} {issue['code']}{profile}: {issue['message']}")
            print(f"  Saran: {issue['suggested_command']}")
        print("Doctor tidak menjalankan chat, jaringan, atau aplikasi; pilihan model/provider/endpoint/API key tidak ditampilkan atau diganti.")
    return report["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
