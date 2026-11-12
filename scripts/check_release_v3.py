"""Check the candidate and installed runtime using observed evidence."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ROLES = {"yukino": "", "shizuka": "shizuka-hiratsuka", "val": "val",
         "kiki-chii": "kiki-chii", "shikaku": "nyenyenye-ya-gw-coder"}
BLOCKED = {"blender", "wordcraft", "lightcraft", "cadcraft", "craftanything", "deckcraft",
           "designcraft", "effectcraft", "figcraft", "filmcraft", "gridcraft",
           "materialcraft", "pdfcraft", "photocraft", "solidcraft",
           "soundcraft", "texturecraft", "vectorcraft"}
UTILITY_MCP = {"hersona", "llmtrim"}
MIGRATED_MCP = BLOCKED | UTILITY_MCP

def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def normalize(value):
    return "".join(letter for letter in value.lower() if letter.isalnum())

def protected(config):
    result = {}
    def visit(data, trail=()):
        if isinstance(data, dict):
            for key, value in data.items():
                part = trail + (str(key),)
                if part[0] in {"tts", "stt", "voice", "audio", "browser"}:
                    continue
                if "provider" in str(key).lower() or "model" in str(key).lower():
                    result["/".join(part)] = hashlib.sha256(
                        json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
                else:
                    visit(value, part)
        elif isinstance(data, list):
            for index, value in enumerate(data):
                visit(value, trail + (str(index),))
    visit(config)
    return result

def audit(repo, home, package_only=False, baseline_override=None):
    checks = {}
    def record(name, passed, evidence):
        checks[name] = {"status": "PASS" if passed else "NEEDS_ATTENTION", "evidence": evidence}
    version = read(repo / "VERSION.json")
    rows = read(repo / "configs/upstreams.json")["entries"]
    record("package_version", version["version"] == "3.0.0",
           {"version": version["version"], "sources": len(rows)})
    record("source_manifest", len(rows) == version["external_sources"] and len({row["source"] for row in rows}) == version["external_sources"],
           {"entries": len(rows)})
    required = ("scripts/msshi_runtime.py", "scripts/msshi_integrations.py", "scripts/msshi_desktop.py",
                "scripts/find_muza_assets.py", "UPDATE_OTOMATIS_KE_V3.bat", "MULAI_DI_SINI_PEMULA.bat",
                "THIRD_PARTY_NOTICES.md", "CREDITS.md", "docs/V3_MIGRATION.md", "scripts/msshi_llmtrim.py")
    missing = [name for name in required if not (repo / name).is_file()]
    record("package_entrypoints", not missing, {"missing": missing})
    if package_only:
        return checks
    try:
        import yaml
        load_yaml = lambda data: yaml.safe_load(data) or {}
    except ImportError:
        # Hermes ships ruamel.yaml; use the same safe reader as its migrator
        # instead of requiring a second YAML implementation in the global CLI.
        from msshi_runtime import yaml_read
        load_yaml = yaml_read
    baseline_path = baseline_override or home / "msshi-private/v3-provider-model-baseline.json"
    baseline = read(baseline_path) if baseline_path.is_file() else {}
    for role, alias in ROLES.items():
        profile = home / "profiles" / alias if alias else home
        file = profile / "config.yaml"
        if not file.is_file():
            record(role + "_profile", False, "Profile config missing")
            continue
        config = load_yaml(file.read_bytes())
        before = baseline.get(str(profile), {}).get("llm_fields")
        # Browser cloud_provider is a browsing backend, not LLM routing.
        # Keep the approved baseline file immutable and compare its LLM subset.
        if before is not None:
            before = {key: value for key, value in before.items() if key.split('/')[0] != 'browser'}
        record(role + "_main_model_provider", before is not None and protected(config) == before,
               {"baseline_present": before is not None, "baseline_path": str(baseline_path)})
        registered = [name for name in (config.get("mcp_servers") or {}) if normalize(name) in MIGRATED_MCP]
        active = [name for name, settings in (config.get("mcp_servers") or {}).items()
                  if normalize(name) in MIGRATED_MCP and isinstance(settings, dict)
                  and settings.get("enabled", True) is not False]
        plugin_config = config.get("plugins") or {}
        active_plugins = [name for name in plugin_config.get("enabled", []) if normalize(name) in MIGRATED_MCP
                          and name not in plugin_config.get("disabled", [])]
        record(role + "_mcp", not registered and not active_plugins,
               {"registered_desktop_servers": [name for name in registered if normalize(name) in BLOCKED],
                "registered_utility_servers": [name for name in registered if normalize(name) in UTILITY_MCP], "active_legacy_servers": active,
                "active_legacy_plugins": active_plugins})
        routes_file = home / "msshi-runtime/profiles" / ("default" if role == "yukino" else alias) / "routes.json"
        routes = read(routes_file).get("targets", {}) if routes_file.is_file() else {}
        utility_routes = {key: routes.get(key, {}) for key in sorted(UTILITY_MCP)}
        utility_ready = all(route.get("kind") == "native-cli" and route.get("readiness") == "available"
                            and Path(route.get("executable") or "__missing__").is_file()
                            for route in utility_routes.values())
        record(role + "_utility_cli", utility_ready,
               {"mcp_registrations_absent": not any(normalize(name) in UTILITY_MCP for name in registered),
                "routes": {key: row.get("readiness", "missing") for key, row in utility_routes.items()},
                "catalog_only": utility_routes.get("hersona", {}).get("catalog_only") is True,
                "compression_local_only": utility_routes.get("llmtrim", {}).get("local_only") is True})
        trim_entry = ((plugin_config.get("entries") or {}).get("msshi-auto-trim") or {}).get("settings") or {}
        trim_plugin = profile / "plugins/msshi-auto-trim"
        hook_installed = ("msshi-auto-trim" in plugin_config.get("enabled", [])
                          and "msshi-auto-trim" not in plugin_config.get("disabled", [])
                          and Path(trim_entry.get("binary") or "__missing__").is_file()
                          and all((trim_plugin / name).is_file() for name in ("plugin.yaml", "__init__.py", "README.md")))
        record(role + "_automatic_trim_hook", hook_installed,
               {"configured_and_files_present": hook_installed,
                "runtime_dispatch_test": "Verified separately; configuration presence alone does not prove live hook execution."})
        record(role + "_gdrive", all(routes.get(key, {}).get("readiness") == "disabled" for key in ("gdrive", "gdrive-web")),
               {"routes": {key: routes.get(key, {}).get("readiness") for key in ("gdrive", "gdrive-web")}})
        voice = (config.get("tts") or {}).get("provider")
        record(role + "_voice", voice == "omnivoice", {"tts_provider": voice})
        record(role + "_persona", (profile / "SOUL.md").is_file(),
               {"soul_present": (profile / "SOUL.md").is_file()})
    for name in ("msshi-runtime/policy.json", "msshi-runtime/profiles/default/routes.json",
                 "msshi-private/v3-integrations-audit.json", "msshi-private/v3-desktop-audit.json"):
        path = home / name
        if path.is_file():
            value = read(path)
            record(name.replace("/", "_"), True, {"path": str(path), "keys": sorted(value)})
        else:
            record(name.replace("/", "_"), False, {"missing": str(path)})
    desktop = home / "msshi-private/v3-desktop-audit.json"
    if desktop.is_file():
        data = read(desktop)
        record("desktop_skills_visible", data.get("skills_panel_visible") is True,
               {"observed": data.get("skills_panel_visible")})
        video = data.get("remotion", {})
        record("remotion_mp4", video.get("passed", video.get("mp4_success")) is True, video)
    enabled_files = {}
    for role, alias in ROLES.items():
        folder = (home / "profiles" / alias if alias else home) / "skills"
        enabled_files[role] = sum(1 for file in folder.rglob("SKILL.md") if file.is_file())
    record("skill_inventory", all(enabled_files.values()), enabled_files)
    return checks

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")))
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--package-only", action="store_true")
    parser.add_argument("--baseline", type=Path, help="Explicit preserved or user-approved provider/model baseline file")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        checks = audit(args.repo, args.home, args.package_only, args.baseline)
        failures = [name for name, row in checks.items() if row["status"] != "PASS"]
        result = {"version": "3.0.0", "scope": "Observed local/package checks only. This verdict is not full compliance with every PDF performance or security claim.",
                  "known_limitations": [
                      "The <5 MiB guardian target is not certified; the local observation was about 21 MiB working set.",
                      "The US$1 policy is not proof of a provider-side hard spending cap or current balance.",
                      "Dreaming's 64 MB input bound is not an enforced OS working-set cap.",
                      "Steel routing policy alone does not activate a Steel account/session or certify consent enforcement.",
                      "KAT is optional; stored setup choices are not proof of an active coding subagent.",
                      "CLI compression availability does not itself prove automatic compression of every model request."],
                  "checks": checks, "pending": failures,
                  "overall_verdict": "PASS_SUCCESS" if not failures else "NEEDS_ATTENTION"}
        content = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content, encoding="utf-8")
        print(content)
        return 0 if not failures else 2
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"Audit could not complete: {error}\n")

if __name__ == "__main__":
    raise SystemExit(main())
