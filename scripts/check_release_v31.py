"""Audit MSSHI 3.1 package, preserved profiles, and recorded integration evidence.

This reader never launches a model, renderer, browser, account probe, or network request.
Only an explicitly selected JSON --output is written.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import check_release_v3 as legacy
from msshi_sources import data_root

ROOT = Path(__file__).resolve().parents[1]
SCOPES = {"unslop": {"kiki-chii", "val", "shikaku"}, "brag": {"kiki-chii"},
          "scrapling": {"val", "shikaku"}, "harness2": {"val", "shikaku"}}
FORBIDDEN = {".git", "node_modules", "venv", ".venv", "site-packages", "__pycache__"}
AUDITS = {"unslop": "msshi-private/v3.1-sources/unslop-integration-audit.json",
          "brag": "msshi-private/v3.1-brag-audit.json",
          "scrapling": "msshi-private/v3.1-scrapling-integration-audit.json",
          "harness2": "msshi-private/v3.1-sources/harness2-integration-audit.json",
          "rea": "msshi-private/v3.1-sources/rea-integration-audit.json"}


def read(path):
    if path.stat().st_size > 8 * 1024 * 1024:
        raise ValueError("Audit metadata exceeds 8 MiB")
    return legacy.read(path)


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def linked(path):
    info = path.lstat()
    return path.is_symlink() or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def private_artifact(home, record):
    try:
        path = Path(record.get("path", "__missing__")).expanduser().absolute()
        private = (home / "msshi-private").resolve(strict=True)
        canonical = path.resolve(strict=True)
        if not canonical.is_relative_to(private): return False
        for part in (path, *path.parents):
            if linked(part): return False
        return canonical.is_file() and digest(canonical) == record.get("sha256")
    except (OSError, ValueError, TypeError):
        return False


def audit_file_mapping(data):
    rows = data.get("source_files", {})
    if isinstance(rows, dict):
        return {name: row["sha256"] for name, row in rows.items()}
    mapping = {}
    for row in rows:
        parts = row["path"].replace("\\", "/").split("/")
        # Earlier integration receipts used absolute source paths. Rebase only a
        # recognized package subtree; never read arbitrary receipt-supplied paths.
        anchor = next((index for index, part in enumerate(parts) if part in {"scripts", "docs", "skills", "optional", "configs"}), None)
        name = "/".join(parts[anchor:]) if anchor is not None else row["path"]
        mapping[name] = row["sha256"]
    return mapping


def cli_helper(repo, slug):
    """Resolve the dispatch declared in the CLI, including skill-local helpers."""
    source = repo / "scripts/msshi_cli.py"
    tree = ast.parse(source.read_text(encoding="utf-8-sig"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict): continue
        for key, value in zip(node.keys, node.values):
            if (isinstance(key, ast.Constant) and key.value == slug and isinstance(value, ast.Constant)
                    and isinstance(value.value, str) and value.value.endswith(".py")):
                helper = (source.parent / value.value).resolve()
                if helper.is_relative_to(repo.resolve()): return helper
    return None


def small_tree(folder):
    """Hash only a small, regular-file skill tree, without traversing links."""
    if not folder.is_dir():
        return {}, {"missing": str(folder)}
    if linked(folder):
        return {}, {"linked_directory": str(folder)}
    files = {}
    issues = []
    total = 0
    for parent, directories, names in os.walk(folder, followlinks=False):
        parent = Path(parent)
        for name in list(directories):
            child = parent / name
            if name.lower() in FORBIDDEN or linked(child):
                issues.append(str(child.relative_to(folder)))
                directories.remove(name)
        for name in names:
            child = parent / name
            relative = child.relative_to(folder).as_posix()
            if name.lower() in FORBIDDEN or linked(child) or not child.is_file():
                issues.append(relative)
                continue
            size = child.stat().st_size
            total += size
            if size > 512 * 1024 or total > 1024 * 1024 or len(files) >= 64:
                issues.append("skill tree exceeds the 1 MiB / 64 file / 512 KiB per-file audit bound")
                return files, {"issues": issues, "bytes_seen": total}
            files[relative] = digest(child)
    return files, {"issues": issues, "files": len(files), "bytes": total}


def checked_hashes(repo, mapping):
    missing, changed = [], []
    for relative, expected in mapping.items():
        parts = str(relative).replace("\\", "/").split("/")
        if not parts or any(part in ("", ".", "..") for part in parts) or ":" in parts[0]:
            raise ValueError("Audit contains an unsafe repository-relative path")
        path = repo.joinpath(*parts)
        if not path.is_file(): missing.append(relative)
        elif digest(path) != expected: changed.append(relative)
    return {"recorded_files": len(mapping), "missing": missing, "changed": changed}


def full_preservation(home):
    path = home / "msshi-private/v3.1-before-profile-hashes.json"
    if not path.is_file():
        return "PENDING", {"missing": str(path)}
    before = read(path).get("files", {})
    if not isinstance(before, dict) or not before:
        return "NEEDS_ATTENTION", {"baseline": str(path), "error": "No full-file baseline hashes"}
    changed, missing, outside = [], [], []
    recorded = set()
    for name, expected in before.items():
        file = Path(name).absolute()
        if not file.is_relative_to(home):
            outside.append(name)
            continue
        recorded.add(file)
        if not file.is_file(): missing.append(name)
        elif digest(file) != expected: changed.append(name)
    required = set()
    for alias in legacy.ROLES.values():
        profile = home / "profiles" / alias if alias else home
        for filename in ("config.yaml", "config.json", "SOUL.md", "user_creative_dna.json", "configs/user_creative_dna.json"):
            file = profile / filename
            if file.is_file(): required.add(file.absolute())
    uncovered = sorted(str(file) for file in required - recorded)
    good = not changed and not missing and not outside and not uncovered
    return "PASS" if good else "NEEDS_ATTENTION", {"baseline": str(path), "recorded_files": len(before),
           "changed": changed, "missing": missing, "outside_selected_home": outside, "uncovered_protected_files": uncovered}


def optional_services(home):
    """Expose historical observed state; registration never means a live connection."""
    result = {"steel": {"authenticated_now": "not_probed", "live_session_tested": False},
              "tinyfish": {"authenticated_now": "not_probed"}}
    steel = home / "msshi-private/v3-steel-browser-audit.json"
    if steel.is_file():
        data = read(steel)
        result["steel"].update(evidence=str(steel), recorded_live_session_tested=data.get("live_session_tested") is True,
                               policy_tests_passed=data.get("unit_passed"),
                               prerequisite="An authorized account/key and scoped browser task remain necessary; policy installation is not a connected session")
    web = home / "msshi-private/v3-web-services-audit.json"
    if web.is_file():
        profiles = read(web).get("profiles", {})
        result["tinyfish"].update(evidence=str(web), recorded_profiles={name: {"registered": row.get("tinyfish", {}).get("registered"),
              "recorded_authenticated": row.get("tinyfish", {}).get("authenticated"),
              "recorded_discovered": row.get("tinyfish", {}).get("discovered"),
              "recorded_read_operation": row.get("tinyfish", {}).get("read_operation")} for name, row in profiles.items()},
              prerequisite="Interactive login and an explicitly authorized operation are separate; this audit does not authenticate or spend quota")
    return result


def audit(repo, home, package_only=False, baseline_override=None):
    repo, home = repo.expanduser().absolute(), home.expanduser().absolute()
    checks = legacy.audit(repo, home, package_only, baseline_override)
    readiness = {}

    def record(name, status, evidence):
        checks[name] = {"status": status if isinstance(status, str) else "PASS" if status else "NEEDS_ATTENTION", "evidence": evidence}

    version = read(repo / "VERSION.json")
    matrix = read(repo / "configs/bot_role_and_skill_matrix.json")
    entries = read(repo / "configs/upstreams.json")["entries"]
    rows = {row["id"]: row for row in entries}
    bundled = [row for row in matrix["skills"] if row.get("status") == "bundled"]
    observed_skills = [file.parent for file in (repo / "skills").rglob("SKILL.md") if file.is_file()]
    record("v31_version_inventory", str(version.get("version", "")).startswith("3.1.")
           and version.get("bundled_skills") == len(bundled) == len(observed_skills)
           and version.get("external_sources") == len(entries),
           {"version": version.get("version"), "declared_skills": version.get("bundled_skills"),
            "catalog_bundled": len(bundled), "actual_skill_folders": len(observed_skills), "actual_sources": len(entries)})
    bots = {row["id"]: row for row in matrix["bots"]}
    profiles = {"default": home}
    profile_folder = home / "profiles"
    if not package_only and profile_folder.is_dir():
        profiles.update({file.name: file for file in profile_folder.iterdir() if file.is_dir() and not file.name.startswith(".")})

    scopes = {slug: set(roles) for slug, roles in SCOPES.items()}
    catalog = {row["slug"]: row for row in matrix["skills"]}
    if (repo / "optional/rea").exists() or catalog.get("rea", {}).get("optional_path"):
        scopes["rea"] = {"shikaku"}
    for slug, expected_roles in scopes.items():
        configured = {role for role, row in bots.items() if slug in row.get("required_skills", []) + row.get("optional_skills", [])}
        source_row = rows.get(slug, {})
        record(f"v31_{slug}_roles", configured == expected_roles and set(source_row.get("roles", [])) == expected_roles
               and source_row.get("auto_start") is False,
               {"expected": sorted(expected_roles), "matrix": sorted(configured), "upstream_roles": source_row.get("roles"),
                "auto_start": source_row.get("auto_start"), "revision": source_row.get("revision")})
        folder = repo / "optional/rea" if slug == "rea" else repo / "skills" / slug
        if slug == "rea":
            row = catalog.get(slug, {})
            optional_manifest = repo / "optional/manifest.json"
            optional_entries = read(optional_manifest).get("entries", []) if optional_manifest.is_file() else []
            declarations = [entry for entry in optional_entries if entry.get("id") == "rea"]
            record("v31_rea_public_default_off", row.get("public_default") is False and
                   row.get("optional_path") == "optional/rea/SKILL.md" and not (repo / "skills/rea").exists() and
                   len(declarations) == 1 and declarations[0].get("public_default") is False and
                   declarations[0].get("path") == "optional/rea" and declarations[0].get("roles") == ["shikaku"] and
                   version.get("optional_skills") == len(optional_entries),
                   {"public_default": row.get("public_default"), "optional_path": row.get("optional_path"),
                    "bundled_default_folder_present": (repo / "skills/rea").exists(), "declarations": declarations,
                    "optional_declared_count": version.get("optional_skills"), "actual_optional_entries": len(optional_entries)})
        source_files, detail = small_tree(folder)
        source_ready = bool(source_files) and "SKILL.md" in source_files and not detail.get("issues") and not detail.get("missing")
        record(f"v31_{slug}_small_source", "PASS" if source_ready else "PENDING" if detail.get("missing") else "NEEDS_ATTENTION", detail)
        if slug in {"brag", "scrapling", "harness2", "rea"}:
            helper = cli_helper(repo, slug)
            fallback = folder / "scripts" / f"msshi_{slug}.py"
            exists = helper is not None and helper.is_file() and fallback.is_file()
            record(f"v31_{slug}_standalone_helper", "PASS" if exists and digest(helper) == digest(fallback) else
                   "NEEDS_ATTENTION" if exists else "PENDING", {"helper": str(helper), "fallback": str(fallback), "files_present": exists})
        readiness[slug] = {"configuration": {"package_skill_present": source_ready, "roles": sorted(expected_roles)},
                           "tested_operations": [], "not_tested": [], "evidence": None}
        if package_only:
            readiness[slug]["evidence_status"] = "not_evaluated_package_only"
            continue
        expected_profiles = {legacy.ROLES[role] or "default" for role in expected_roles}
        if slug == "rea":
            registry_path = data_root() / "state.json"
            registry = read(registry_path) if registry_path.is_file() else {}
            bindings = [binding for binding in registry.get("managed_bindings", []) if binding.get("skill") == "rea"]
            selected = []
            invalid = []
            fingerprint = hashlib.sha256(json.dumps(source_files, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
            for binding in bindings:
                logical = Path(binding.get("logical", "__missing__")).absolute()
                if not logical.is_relative_to(home): continue
                names = [name for name, profile in profiles.items() if logical == profile / "skills/rea"]
                if (names and names[0] in expected_profiles and binding.get("optional") is True and
                        binding.get("source_rel") == "optional/rea" and binding.get("fingerprint") == fingerprint and
                        Path(binding.get("physical", "__missing__")).resolve() == logical.resolve()):
                    selected.append(names[0])
                else:
                    invalid.append(str(logical))
            record("v31_rea_opt_in_registry", not invalid,
                   {"path": str(registry_path), "enabled_profiles": sorted(selected), "invalid_bindings": invalid})
            expected_profiles = set(selected)
            readiness[slug]["configuration"].update(public_default=False, enabled_profiles=sorted(selected))
        observed = {name for name, profile in profiles.items() if (profile / "skills" / slug).exists()}
        missing, extra = sorted(expected_profiles - observed), sorted(observed - expected_profiles)
        copy_details = {}
        for name in sorted(expected_profiles & observed):
            actual, tree_detail = small_tree(profiles[name] / "skills" / slug)
            copy_details[name] = {"matches_source": actual == source_files and not tree_detail.get("issues"), **tree_detail}
        copy_good = source_ready and all(row["matches_source"] for row in copy_details.values())
        record(f"v31_{slug}_live_scope_and_copies", "NEEDS_ATTENTION" if extra or any(not row["matches_source"] for row in copy_details.values()) else
               "PENDING" if missing or not source_ready else "PASS",
               {"expected_profiles": sorted(expected_profiles), "observed_profiles": sorted(observed),
                "missing": missing, "unexpected": extra, "copies": copy_details})
        readiness[slug]["configuration"].update(installed_exact_scope=not missing and not extra and copy_good,
                                                 observed_profiles=sorted(observed))
        if slug == "rea" and not expected_profiles and not observed:
            readiness[slug]["evidence_status"] = "not_enabled_public_default_off"
            record("v31_rea_recorded_operations", "NOT_APPLICABLE", {"reason": "Optional capability is not enabled in this Hermes home"})
            continue
        path = home / AUDITS[slug]
        if slug == "rea" and not path.is_file() and (home / "msshi-private/v3.1-rea-audit.json").is_file():
            path = home / "msshi-private/v3.1-rea-audit.json"
        if not path.is_file():
            record(f"v31_{slug}_recorded_operations", "PENDING", {"missing": str(path)})
            readiness[slug]["evidence_status"] = "pending_integration_audit"
            continue
        try:
            data = read(path)
            if not isinstance(data, dict): raise ValueError("Expected an audit object")
        except (OSError, ValueError) as error:
            record(f"v31_{slug}_recorded_operations", "NEEDS_ATTENTION", {"path": str(path), "error_type": type(error).__name__})
            readiness[slug].update(evidence=str(path), evidence_status="invalid_integration_audit")
            continue
        readiness[slug].update(evidence=str(path), evidence_sha256=digest(path), evidence_status="recorded")
        tested = False
        evidence = {"path": str(path)}
        revision = data.get("source_commit") or data.get("upstream", {}).get("commit")
        record(f"v31_{slug}_audit_pin", revision == source_row.get("revision"),
               {"audit_revision": revision, "manifest_revision": source_row.get("revision")})
        if slug == "unslop":
            mapping = {f"skills/unslop/{row['path']}": row["sha256"] for row in data.get("adaptation", {}).get("skill_files", [])}
            canonical = data.get("canonical_license_normalization", {}).get("sha256")
            if canonical:
                mapping["skills/unslop/LICENSE"] = canonical
            hashes = checked_hashes(repo, mapping)
            validation = data.get("validation", {})
            tested = (bool(mapping) and not hashes["changed"] and not hashes["missing"] and
                      validation.get("local_license_link") is True and "passed" in str(validation.get("quick_validate", "")))
            evidence.update(source_hashes=hashes, validation=validation)
            readiness[slug].update(tested_operations=["recorded skill validation, attribution/license, exact-copy checks"],
                                   not_tested=["Task-specific UI implementation and render/interaction validation"],
                                   prerequisites=data.get("remaining_prerequisites", {}))
        elif slug == "scrapling":
            mapping = {name: row["sha256"] for name, row in data.get("source_files", {}).items()}
            hashes = checked_hashes(repo, mapping)
            proof_path = home / "msshi-private/v3.1-scrapling-audit.json"
            proof = read(proof_path) if proof_path.is_file() else {}
            operations = proof.get("checks", {})
            artifacts = []
            proof_directory = Path(proof.get("proof_directory", "__missing__")).absolute()
            if proof_directory.is_relative_to(home / "msshi-private"):
                for name, expected in proof.get("output_hashes", {}).items():
                    file = proof_directory / name
                    artifacts.append(Path(name).name == name and file.is_file() and digest(file) == expected)
            marker = home / "msshi-private/scrapling-runtime/INSTALLATION.json"
            installation = read(marker) if marker.is_file() else {}
            tested = (data.get("success") is True and bool(mapping) and not hashes["changed"] and not hashes["missing"] and
                      proof.get("success") is True and len(operations) >= 13 and all(value is True for value in operations.values()) and
                      bool(artifacts) and all(artifacts) and installation.get("source_commit") == source_row.get("revision") and
                      installation.get("lock_sha256") == data.get("lock_sha256") and
                      data.get("offline_selftest_audit_sha256") == digest(proof_path))
            evidence.update(source_hashes=hashes, recorded_checks=operations, artifacts_verified=len(artifacts),
                            dependency_wheels_recorded=len(data.get("package_wheels_verified_against_official_pypi", [])),
                            runtime_pin_recorded=installation.get("source_commit"))
            readiness[slug].update(tested_operations=["13 recorded offline parsing/input/output safety checks and retained artifact hashes"],
                                   not_tested=["Live HTTP extraction, JavaScript, stealth/CAPTCHA, browser/session access, crawling"],
                                   prerequisites="Separate scoped authorization/policy for any network or browser operation; adapter accepts local HTML only")
        elif slug == "brag":
            hashes = checked_hashes(repo, audit_file_mapping(data))
            tests = data.get("tests", {})
            render = tests.get("render", {})
            state = data.get("readiness", {})
            artifact_good = private_artifact(home, data.get("render_artifact", {}))
            runtime = data.get("runtime", {})
            runtime_files = {name: private_artifact(home, runtime.get(name, {}))
                             for name in ("package_metadata", "package_lock", "entrypoint")}
            tested = (data.get("success") is True and hashes["recorded_files"] > 0 and not hashes["missing"] and not hashes["changed"] and
                      state.get("tiny_local_render_verified") is True and tests.get("hyperframes_check", {}).get("ok") is True and
                      (render.get("ok") is True or render.get("status") == "passed") and render.get("width") == 320 and render.get("height") == 180 and
                      render.get("frames") == 30 and artifact_good and all(runtime_files.values()) and
                      runtime.get("warm_check_daemon_disabled_by_CI") is True and runtime.get("remaining_owned_processes") == 0)
            evidence.update(tests=tests, readiness=state, source_hashes=hashes, retained_render_hash_verified=artifact_good,
                            current_runtime_file_hashes_verified=runtime_files)
            readiness[slug].update(tested_operations=["Recorded tiny local Hyperframes validation and 1-second synthetic render"],
                                   not_tested=["Production-quality video, real product assets, voice/model/account operation"],
                                   prerequisites=data.get("pending_production_requirements", data.get("blockers", [])),
                                   production_video=state.get("production_video") is True)
        elif slug == "harness2":
            hashes = checked_hashes(repo, audit_file_mapping(data))
            tests = data.get("tests", {})
            runtime = data.get("runtime", {})
            proof = runtime.get("demo_proof", {})
            artifact_good = private_artifact(home, {"path": runtime.get("demo_proof_path", "__missing__"),
                                                    "sha256": runtime.get("demo_proof_sha256")})
            guards = tests.get("deployed_guard_fixtures", {})
            tested = (data.get("success") is True and hashes["recorded_files"] > 0 and not hashes["missing"] and not hashes["changed"] and
                      proof.get("success") is True and proof.get("done") == 2 and proof.get("failed") == 0 and
                      proof.get("execution_count") == 28 and proof.get("editor_calls") == 32 and
                      proof.get("api_calls_made") == 0 and guards.get("passed") == 6 and guards.get("failed") == 0 and artifact_good)
            evidence.update(tests=tests, demo_proof=proof, source_hashes=hashes, retained_demo_hash_verified=artifact_good)
            readiness[slug].update(tested_operations=["Recorded deterministic local Propose-Probe-Compose demonstration"],
                                   not_tested=["Paid model benchmarks, benchmark accuracy, automated harness promotion"],
                                   prerequisites=data.get("remaining_prerequisites", data.get("blockers", [])))
        else:
            hashes = checked_hashes(repo, audit_file_mapping(data))
            tests = data.get("tests", {})
            required_tests = {"runtime_ready_pinned", "javascript_full_output_ok", "zip_full_output_ok",
                "owned_javascript_modules_seen", "javascript_execution_sentinel_absent", "owned_zip_member_seen",
                "optional_helper_identical", "live_helper_identical", "live_skill_identical", "no_default_skills_rea_folder",
                "frida_not_installed", "mcp_disabled", "no_boot_start", "missing_target_refused", "report_in_input_tree_refused",
                "existing_report_refused", "existing_report_bytes_preserved", "setup_not_exposed", "ida_mcp_provider_not_exposed",
                "personal_profile_coder_only"}
            proof_good = private_artifact(home, data.get("proof", {}))
            marker = home / "msshi-private/rea-runtime/INSTALLATION.json"
            installation = read(marker) if marker.is_file() else {}
            source_entry_sha = data.get("reviewed_upstream_files", {}).get("scripts/rea.mjs", {}).get("sha256")
            entry_good = private_artifact(home, {"path": data.get("status", {}).get("entry", "__missing__"),
                                                 "sha256": source_entry_sha})
            tested = (data.get("success") is True and hashes["recorded_files"] > 0 and not hashes["missing"] and not hashes["changed"]
                      and all(tests.get(name) is True for name in required_tests) and proof_good and entry_good and
                      installation.get("source_commit") == source_row.get("revision") and installation.get("entry_sha256") == source_entry_sha and
                      installation.get("integrity") == data.get("upstream", {}).get("npm_integrity") and
                      tests.get("cli_reported_version") == data.get("upstream", {}).get("npm_version"))
            evidence.update(source_hashes=hashes, tests=tests, retained_proof_hash_verified=proof_good,
                            current_cli_entry_hash_verified=entry_good, installation_pin=installation.get("source_commit"))
            readiness[slug].update(tested_operations=data.get("tested_operations", []),
                                   not_tested=data.get("not_tested", []), prerequisites=data.get("remaining_prerequisites", []))
        record(f"v31_{slug}_recorded_operations", tested, evidence)
        readiness[slug]["recorded_operation_checks_passed"] = tested

    if not package_only:
        state, evidence = full_preservation(home)
        record("v31_full_config_soul_dna_preservation", state, evidence)
    return checks, readiness, {} if package_only else optional_services(home)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")))
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--package-only", action="store_true")
    parser.add_argument("--baseline", type=Path, help="Legacy provider/model baseline override; the v3.1 full-file baseline remains separate")
    args = parser.parse_args(argv)
    try:
        checks, readiness, services = audit(args.repo, args.home, args.package_only, args.baseline)
        failures = [name for name, row in checks.items() if row["status"] == "NEEDS_ATTENTION"]
        pending = [name for name, row in checks.items() if row["status"] == "PENDING"]
        result = {"version": read(args.repo / "VERSION.json")["version"], "auditor": "MSSHI 3.1",
                  "checked_utc": datetime.now(timezone.utc).isoformat(), "package_only": args.package_only,
                  "scope": "Read-only package/profile checks and existing recorded operation evidence. No models, renders, browsers, account probes, or network tests were run by this auditor.",
                  "checks": checks, "integration_readiness": readiness, "external_service_readiness": services,
                  "failures": failures, "pending": pending,
                  "known_limitations": ["Existing v3 performance/budget/policy limits remain; configuration does not certify operational or paid-provider guarantees.",
                      "Tiny local deterministic/parser/render checks do not establish production performance, benchmark gains, or complete crawler capability.",
                      "Steel account/key, Tinyfish login, paid benchmarks, and task-specific human approval are separate prerequisites; no connected state is inferred."],
                  "overall_verdict": "NEEDS_ATTENTION" if failures else "PENDING" if pending else "PASS_SUCCESS"}
        content = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            output = args.output.expanduser().absolute()
            home = args.home.expanduser().absolute()
            if output.suffix.lower() != ".json" or output == home / "msshi-private/v3.1-before-profile-hashes.json":
                raise ValueError("Choose a JSON audit output distinct from the preservation baseline")
            if output.is_relative_to(home) and not output.is_relative_to(home / "msshi-private"):
                raise ValueError("Outputs inside the selected Hermes home must stay in msshi-private")
            for part in (output, *output.parents):
                try:
                    if linked(part): raise ValueError("Refusing symlink/junction output")
                except FileNotFoundError:
                    pass
            inputs = {home / value for value in AUDITS.values()} | {
                home / "msshi-private/v3.1-scrapling-audit.json", home / "msshi-private/v3-provider-model-baseline.json",
                home / "msshi-private/v3-web-services-audit.json", home / "msshi-private/v3-steel-browser-audit.json",
                home / "msshi-private/v3-integrations-audit.json", home / "msshi-private/v3-desktop-audit.json"}
            if args.baseline: inputs.add(args.baseline.expanduser().absolute())
            if output in inputs or output.name in {"INSTALLATION.json", "OWNER.json"}:
                raise ValueError("Do not overwrite integration evidence with the aggregate audit")
            if output.exists():
                previous = read(output)
                if (not isinstance(previous, dict) or previous.get("auditor") != "MSSHI 3.1"
                        or "checks" not in previous or "overall_verdict" not in previous):
                    raise ValueError("Existing output is not an aggregate from this auditor; choose a new filename")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(content, encoding="utf-8")
        print(content)
        return 0 if not failures and not pending else 2
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"Audit could not complete: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
