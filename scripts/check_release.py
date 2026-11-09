#!/usr/bin/env python3
"""Validate the MSSHI release offline, without touching an installed agent."""
from __future__ import annotations

import argparse
import ast
import io
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from urllib.parse import unquote, urlsplit
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True

from catalog_api import catalog_handler
import msshi_cli
import msshi_sources
from install_msshi import UNIVERSAL_BRIDGE

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "configs" / "bot_role_and_skill_matrix.json"
LOCAL_FILES = re.compile(
    r"(?:^|/)(?:\.env(?:\.[^/]+)?|[^/]+\.(?:pem|key|p12)|"
    r"curiosity_ledger|\.msshi-backup-[^/]*|\.msshi-stage-[^/]*|msshi-bridge|bridge-profiles|msshi-private|"
    r"Install_Tahap2_MuZA_Hermes_Full\.ps1|Audit_Dry_Run_MuZA\.txt|PANDUAN_INSTAL_MUZA\.md)(?:/|$)",
    re.I,
)
SECRET = re.compile(r"(?<![\w-])(?:sk-[a-zA-Z0-9_-]{24,}|gh[pousr]_[a-zA-Z0-9]{30,}|"
                    r"github_pat_[a-zA-Z0-9_]{30,}|AIza[a-zA-Z0-9_-]{35})"
                    r"|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
PRIVATE = re.compile(r"[A-Z]:\\Zidan\\|https?://(?:notebooklm|notebook)\.google\.com/notebook/", re.I)
LINK = re.compile(r"\]\(([^()\s]+)\)")
SVG_NS = {"svg": "http://www.w3.org/2000/svg"}


def require(condition, description):
    if not condition:
        raise ValueError(description)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def release_files():
    excluded = {".git", ".pytest_cache", "__pycache__"}
    for folder, dirs, files in os.walk(ROOT):
        parent = Path(folder)
        dirs[:] = [name for name in dirs if name not in excluded
                   and not name.startswith(".msshi-check-")]
        for name in (*dirs, *files):
            path = parent / name
            rel = path.relative_to(ROOT).as_posix()
            metadata = path.lstat()
            require(not stat.S_ISLNK(metadata.st_mode)
                    and not getattr(metadata, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT,
                    f"Link or reparse point in release: {rel}")
            require(path.name == ".env.example" or not LOCAL_FILES.search(rel),
                    f"Private file or directory in release: {rel}")
        yield from (parent / name for name in files)


def check_links(path, source):
    count = 0
    for link in LINK.findall(source):
        try:
            url = urlsplit(link)
        except ValueError:
            continue
        if url.scheme or url.netloc or not url.path:
            continue
        target = (path.parent / unquote(url.path)).resolve()
        require(target.is_relative_to(ROOT) and target.exists(),
                f"Broken local link in {path.relative_to(ROOT)}: {link}")
        count += 1
    return count


def static_checks():
    matrix = read_json(MATRIX)
    version = read_json(ROOT / "VERSION.json")
    upstreams = read_json(ROOT / "configs" / "upstreams.json")
    expected = {item["slug"] for item in matrix["skills"] if item["status"] == "bundled"}
    shipped = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
    require(expected == shipped and len(shipped) == version["bundled_skills"],
            "Bundled skill folders, matrix, and VERSION.json disagree")
    require(read_json(ROOT / "package.json")["version"] == version["version"],
            "npm and VERSION.json versions disagree")
    aliases = matrix.get("aliases", {})
    require(all(alias not in shipped and slug in shipped for alias, slug in aliases.items()),
            "Aliases collide with bundled skill names or point outside the bundle")
    sources = {row["source"] for row in upstreams["entries"]}
    require(len(sources) == len(upstreams["entries"]) == version["external_sources"],
            "Upstream inventory and VERSION.json disagree")
    require(len(matrix["bots"]) == 5 and len(matrix["packs"]) == 6,
            "Preset must describe five bots and six packs")

    wrappers = {row["slug"] for row in matrix["skills"] if row.get("kind") == "integration-wrapper"}
    require(wrappers <= expected and len(wrappers) == version["integration_wrappers"]
            and len(expected - wrappers) == version["core_skills"],
            "Core and wrapper counts disagree with the release matrix")
    require(all(UNIVERSAL_BRIDGE in bot["required_skills"] for bot in matrix["bots"]),
            "The universal bridge is not assigned to all five profiles")
    policies = read_json(ROOT / "skill_activation_matrix.json")["app_connection_policy"]
    require(policies.get("auto_open_on_boot") is False,
            "The activation policy must keep application launch on demand")
    for file in (
        "scripts/cli_anything_sovereign_hub.py", "scripts/setup_cli_anything_hermes.py",
        f"skills/{UNIVERSAL_BRIDGE}/scripts/setup_cli_anything_hermes.py",
    ):
        require((ROOT / file).is_file(), f"Missing standalone bridge component: {file}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    visual_count = links = file_count = 0
    for path in release_files():
        file_count += 1
        rel = path.relative_to(ROOT)
        suffix = path.suffix.lower()
        if suffix in {".json", ".md", ".py", ".ps1", ".sh", ".svg", ".cmd", ".txt", ".yml", ".yaml"}:
            text = path.read_text(encoding="utf-8-sig")
            require(not SECRET.search(text) and not PRIVATE.search(text),
                    f"Credential or private source pattern in {rel}")
        if suffix == ".json":
            read_json(path)
        if suffix == ".py":
            ast.parse(text, filename=str(rel), feature_version=(3, 10))
        if path.name == "SKILL.md":
            header = re.match(r"\A---\s*\n(.*?)\n---(?:\n|$)", text, re.S)
            name = "msshi" if path.parent == ROOT else path.parent.name
            require(header and re.search(rf"^name:\s*{re.escape(name)}\s*$", header[1], re.M)
                    and re.search(r"^description:\s*\S", header[1], re.M),
                    f"Missing or mismatched skill metadata in {rel}")
        if suffix == ".md" and (len(rel.parts) == 1 or rel.parts[0] in {"docs", "assets"}):
            links += check_links(path, text)
        if suffix == ".svg" and rel.parts[0] == "assets":
            visual_count += 1
            svg = ET.fromstring(text)
            require(svg.findtext("svg:title", namespaces=SVG_NS)
                    and svg.findtext("svg:desc", namespaces=SVG_NS),
                    f"Missing SVG accessibility text in {rel}")
            require(f"({rel.as_posix()})" in readme, f"SVG is unused in README: {rel}")
    require(visual_count == 7, "Expected seven README diagrams")
    run_cli("render_bot_audit.py", "--check")
    print(f"Static checks passed: {file_count} files, {len(shipped)} skills, "
          f"{len(sources)} upstream sources, {visual_count} SVGs, {links} local links")


def run_cli(script, *args, ok=True, env=None, input_text=None):
    result = subprocess.run(
        [sys.executable, "-B", "-X", "utf8", str(ROOT / "scripts" / script), *map(str, args)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=90,
        env=env, input=input_text,
    )
    require((result.returncode == 0) == ok,
            f"{script} returned {result.returncode}: {(result.stderr or result.stdout)[-400:]}")
    return result.stdout


def installer_smoke(work):
    options = ("--platform", "manual", "--target-dir")
    target = work / "solo profile"
    run_cli("install_msshi.py", "--mode", "solo", *options, target)
    require(not target.exists(), "Installer dry-run wrote output")
    target.mkdir()
    config = target / "config.yaml"
    sentinel = b"provider: preserve-me\nmodel: preserve-me\n"
    config.write_bytes(sentinel)
    run_cli("install_msshi.py", "--mode", "solo", *options, target, "--apply")
    require(len(list(target.glob("*/SKILL.md"))) == read_json(ROOT / "VERSION.json")["bundled_skills"],
            "Solo did not install all bundled skills")
    existing = target / "academic-plotting" / "SKILL.md"
    existing.write_text("custom content", encoding="utf-8")
    run_cli("install_msshi.py", "--mode", "solo", *options, target, "--apply")
    require(existing.read_text(encoding="utf-8") == "custom content" and config.read_bytes() == sentinel,
            "Installer changed an existing skill or provider/model config")
    selective = work / "selected"
    run_cli("install_msshi.py", "--mode", "selective", "--packs", "core,business",
            *options, selective, "--apply")
    require((selective / "business-sage" / "SKILL.md").is_file()
            and not (selective / "academic-plotting").exists(), "Selective pack leaked unrelated skills")
    require((selective / UNIVERSAL_BRIDGE / "SKILL.md").is_file(),
            "Selective install omitted the universal bridge")
    team = work / "preset"
    run_cli("install_msshi.py", "--mode", "muza-preset", *options, team, "--apply")
    require(len(list(team.glob("*/SOUL.md"))) == 5 and len(list(team.glob("*/AGENTS.md"))) == 5,
            "Preset did not write five workspaces")
    require(len(list(team.glob(f"*/skills/{UNIVERSAL_BRIDGE}/SKILL.md"))) == 5,
            "The preset omitted the bridge from one or more bots")
    matrix = read_json(MATRIX)
    custom = matrix["bots"][0]
    custom["id"] = "test-bot"
    custom["label"] = "Test Bot"
    custom["required_skills"].remove(UNIVERSAL_BRIDGE)
    matrix["bots"] = [custom]
    matrix["skills"] = [entry for entry in matrix["skills"] if entry["slug"] != UNIVERSAL_BRIDGE]
    for pack in matrix["packs"].values():
        if UNIVERSAL_BRIDGE in pack:
            pack.remove(UNIVERSAL_BRIDGE)
    matrix_path = work / "matrix.json"
    matrix_path.write_text(json.dumps(matrix), encoding="utf-8")
    run_cli("install_msshi.py", "--mode", "custom-bots", "--matrix", matrix_path,
            *options, work / "team", "--apply")
    custom_root = work / "team" / "test-bot"
    require((custom_root / "SOUL.md").is_file(), "Custom bot workspace missing")
    require((custom_root / "skills" / UNIVERSAL_BRIDGE / "SKILL.md").is_file(),
            "Legacy custom matrix omitted the universal bridge")
    run_cli("install_msshi.py", "--mode", "selective", "--packs", "unknown",
            *options, work / "invalid", "--apply", ok=False)
    require(not (work / "invalid").exists(), "Invalid pack wrote output")


def updater_smoke(work):
    source, baseline, installed = (work / name for name in ("incoming", "baseline", "installed"))
    for root, tag in ((source, "new"), (baseline, "old")):
        root.mkdir()
        (root / "VERSION.json").write_text(json.dumps({"version": tag}), encoding="utf-8")
        for slug in ("test-one", "test-two", "test-custom"):
            skill = root / "skills" / slug
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(tag, encoding="utf-8")
    for slug in ("test-one", "test-two", "test-custom"):
        folder = installed / slug
        folder.mkdir(parents=True)
        (folder / "SKILL.md").write_text("local" if slug == "test-custom" else "old", encoding="utf-8")
    base = ("--source", source, "--baseline", baseline, "--skills-dir", installed)
    check = json.loads(run_cli("msshi_update.py", *base, "--mode", "check"))
    require(check["source_version"] == "new" and not list(installed.parent.glob(".msshi-backup-*")),
            "Updater check failed or wrote a backup")
    selected = json.loads(run_cli("msshi_update.py", *base, "--mode", "select",
                                  "--skills", "test-one", "--apply"))
    backup = Path(selected["backup"])
    require(backup.parent == installed.parent and not list(installed.glob(".msshi-*")),
            "Updater exposed backup or staging files to the skill loader")
    require((backup / "test-one" / "SKILL.md").read_text() == "old"
            and (installed / "test-two" / "SKILL.md").read_text() == "old", "Selective update lost backup or changed an unselected skill")
    run_cli("msshi_update.py", *base, "--mode", "auto", "--apply")
    require((installed / "test-two" / "SKILL.md").read_text() == "new"
            and (installed / "test-custom" / "SKILL.md").read_text() == "local",
            "Auto update missed a skill or overwrote local content")


def global_smoke(work):
    home, profile = work / "state", work / "profile"
    target = profile / "skills"
    env = {**os.environ, "MSSHI_HOME": str(home)}
    run_cli("msshi_cli.py", "setup", "--platform", "manual", "--target-dir", target,
            env=env, input_text="3\nbusiness\ny\n")
    state = msshi_cli.read_state(home)
    managed = state["targets"][str(target)]
    require(len(managed) >= 3 and UNIVERSAL_BRIDGE in managed,
            "Global setup did not register the bridge and selected skills")
    changed, custom = sorted(managed.keys() - {UNIVERSAL_BRIDGE})[:2]
    # Simulate a managed profile from the prior installer, before the bridge existed.
    old_target = work / "old-profile" / "skills"
    old_target.mkdir(parents=True)
    state["targets"][str(old_target)] = {}
    (target / custom / "SKILL.md").write_text("local skill customization", encoding="utf-8")
    soul = profile / "SOUL.md"
    dna = profile / "user_creative_dna.json"
    soul.write_text("local persona", encoding="utf-8")
    dna.write_text('{"style":"local"}', encoding="utf-8")
    source = work / "latest"
    source.mkdir()
    for name in ("configs", "skills", "scripts"):
        shutil.copytree(ROOT / name, source / name, ignore=shutil.ignore_patterns("__pycache__"))
    version = read_json(ROOT / "VERSION.json")
    (source / "VERSION.json").write_text(json.dumps({**version, "version": "99.0.0"}), encoding="utf-8")
    for slug in (changed, custom):
        with (source / "skills" / slug / "SKILL.md").open("a", encoding="utf-8") as file:
            file.write("\nFixture update.\n")
    require(msshi_cli.update(SimpleNamespace(skip_upstreams=True), home, state, source, "a" * 40) == 0,
            "Global update failed")
    require((target / changed / "SKILL.md").read_bytes() == (source / "skills" / changed / "SKILL.md").read_bytes()
            and (target / custom / "SKILL.md").read_text(encoding="utf-8") == "local skill customization",
            "Global update failed to update a managed skill or preserve a customization")
    require((old_target / UNIVERSAL_BRIDGE / "SKILL.md").is_file()
            and UNIVERSAL_BRIDGE in state["targets"][str(old_target)],
            "Global update did not install and register the bridge for the existing profile")
    backups = list((home / "backups").glob("*/files.json"))
    require(len(backups) == 1, "Protected backup missing")
    require({Path(item["original"]): (backups[0].parent / item["backup"]).read_bytes()
             for item in read_json(backups[0])} == {soul: soul.read_bytes(), dna: dna.read_bytes()},
            "Protected backup did not retain the original persona and DNA")
    aliases = read_json(MATRIX)["aliases"]
    spelling = "auto-curiosity-for-film-making"
    run_cli("msshi_cli.py", "select", "--local", "--platform", "manual", "--target-dir", target,
            env=env, input_text=f"s\n{spelling}\ny\n")
    require((target / aliases[spelling] / "SKILL.md").is_file(), "Global select did not resolve skill alias")
    responses = (json.dumps({"version": "99.0.0"}).encode(), b"# Changelog fixture")
    with patch.object(msshi_cli, "download", side_effect=responses) as get:
        msshi_cli.check_release()
        require(get.call_count == 2, "Global check did not query VERSION.json and CHANGELOG.md")


def version_migration_smoke(work):
    order = msshi_cli.version_key
    require(order("2.1.0-stage1.2") < order("2.2.0-stage2") < order("2.1.0") < order("2.2.0"),
            "Stage 1, old preview, v2.1, and later release are not ordered correctly")
    home = work / "v"
    old_id = "d" * 24
    old = home / "releases" / old_id
    (old / "scripts").mkdir(parents=True)
    (old / "VERSION.json").write_text('{"version":"2.2.0-stage2"}', encoding="utf-8")
    (old / "scripts" / "msshi_cli.py").write_text(
        'raise SystemExit("Migration unexpectedly invoked the preview launcher")\n', encoding="utf-8",
    )
    (home / "state.json").write_text(
        json.dumps({"schema_version": 1, "current": old_id, "targets": {}}), encoding="utf-8",
    )
    env = {**os.environ, "MSSHI_HOME": str(home)}
    run_cli("msshi_cli.py", "bootstrap", "--no-path", env=env)
    active = msshi_cli.active_script(home)
    require(active is not None and msshi_cli.release_version(active.parents[1]) == msshi_cli.release_version(ROOT),
            "Reinstall did not migrate the installed preview to the public v2.1 release")
    require("connect" in run_cli(active, "--help", env=env),
            "The migrated CLI has no connect command")


def bridge_smoke(work):
    home = work / "hermes"
    selected_home = home / "profiles" / "test-bot"
    selected_home.mkdir(parents=True)
    marker = "fixture-secret-never-expose"
    settings = {
        selected_home / "config.yaml": (
            "provider: preserve-me\nmodel: preserve-me\nmcp_servers:\n"
            f"  filmcraft:\n    command: '{marker}'\n"
            f"  lightcraft:\n    enabled: false\n    url: 'https://example.invalid/{marker}'\n"
        ).encode(),
        selected_home / "mcp_config.json": json.dumps({
            "mcpServers": {"blender": {"command": marker}},
        }).encode(),
    }
    for file, contents in settings.items():
        file.write_bytes(contents)

    env = {**os.environ, "MSSHI_HOME": str(work / "connect-state")}
    base = ("connect", "--hermes-home", home, "--profile", "test-bot", "--json")

    def connect(*flags, ok=True):
        output = run_cli("msshi_cli.py", *base, *flags, env=env, ok=ok)
        require(marker not in output, "Connector settings or tokens were disclosed")
        return json.loads(output) if ok else None

    before = set(selected_home.rglob("*"))
    preview = connect("--mode", "auto-reconnect", "--dry-run")
    require(preview.get("auto_open_on_boot") is False, "Preview would open applications at startup")
    require(set(selected_home.rglob("*")) == before, "Auto-reconnect preview wrote into the profile")
    require(not connect("--status")["connections"], "Auto-reconnect preview registered connections")

    connect("--mode", "auto-reconnect")
    status = connect("--status")
    rows = {row["id"]: row for row in status["connections"]}
    require({"filmcraft", "blender"} <= rows.keys()
            and rows["filmcraft"]["readiness"] == "configured"
            and rows["blender"]["readiness"] == "configured",
            "Auto-reconnect did not detect configured MCP routes from both config files")
    require(status.get("auto_open_on_boot") is False,
            "Auto-reconnect enabled application startup")

    manual_state = ("connect", "--hermes-home", home, "--profile", "default", "--json")
    run_cli("msshi_cli.py", *manual_state, "--mode", "select", "--targets",
            "gdrive-web,youtube-chrome", env=env)
    run_cli("msshi_cli.py", *manual_state, "--add", "tiktok", env=env)
    run_cli("msshi_cli.py", *manual_state, "--remove", "youtube-chrome", env=env)
    selected = json.loads(run_cli("msshi_cli.py", *manual_state, "--status", env=env))
    require({row["id"] for row in selected["connections"]} == {"gdrive-web", "tiktok"},
            "Select/add/remove did not preserve the selected routes")
    require({row["id"] for row in connect("--status")["connections"]} == rows.keys(),
            "A route change leaked into a different Hermes profile")
    connect("--add", "../untrusted", ok=False)
    connect("--open", "gdrive-web", "--dry-run", ok=False)

    manual = ("connect", "--hermes-home", home, "--profile", "manual")
    run_cli("msshi_cli.py", *manual, env=env, input_text="2\n2,5\n")
    menu_report = json.loads(run_cli("msshi_cli.py", *manual, "--status", "--json", env=env))
    require({row["id"] for row in menu_report["connections"]} == {"gdrive-web", "tiktok"},
            "Interactive target selection did not register both requested routes")
    require(all(file.read_bytes() == contents for file, contents in settings.items()),
            "Bridge modified Hermes configuration")

    standalone = selected_home / "skills" / UNIVERSAL_BRIDGE
    standalone.parent.mkdir()
    shutil.copytree(ROOT / "skills" / UNIVERSAL_BRIDGE, standalone)
    output = run_cli(standalone / "scripts" / "setup_cli_anything_hermes.py",
                     "--hermes-home", home, "--profile", "test-bot", "--status", "--json", env=env)
    require({row["id"] for row in json.loads(output)["connections"]} == rows.keys(),
            "The skill-local bridge could not run without the repository or global CLI")


def upstream_smoke(work):
    def clone(url, destination, *, metadata_only=False):
        require(url.endswith(".git") and metadata_only, "Upstream must use a metadata-only Git snapshot")
        destination.mkdir()
        return "a" * 40

    cache = work / "upstreams"
    with patch.object(msshi_sources, "clone", side_effect=clone) as git, \
            patch.object(msshi_sources, "download", return_value=b"public source metadata") as get:
        rows = msshi_sources.fetch_upstreams(ROOT / "configs" / "upstreams.json", cache)
        require(len(rows) == 37 and git.call_count == 35 and get.call_count == 2,
                "Manifest fetch did not cover the 37 source entries")
        require(all(item["status"] == "cached" for item in rows.values())
                and read_json(cache / "last-fetch.json") == rows, "Upstream cache report is incomplete")


def catalog_smoke():
    # Exercise the real HTTP handler without binding a network port.
    handler = catalog_handler(read_json(MATRIX), "local-test")
    def call(path, token="", method="GET"):
        request = object.__new__(handler)
        request.command = method
        request.path = path
        request.headers = {"Authorization": f"Bearer {token}"}
        request.request_version = "HTTP/1.1"
        request.requestline = f"{method} {path} HTTP/1.1"
        request.wfile = io.BytesIO()
        getattr(request, f"do_{method}")()
        headers, payload = request.wfile.getvalue().split(b"\r\n\r\n", 1)
        return int(headers.split(b" ", 2)[1]), json.loads(payload)
    require(call("/skills")[0] == 401, "Catalog accepted missing auth")
    status, data = call("/skills?pack=core", "local-test")
    require(status == 200 and data["skills"] and
            set(data["skills"][0]) == {"slug", "status", "purpose"}, "Catalog exposed unexpected fields")
    require(call("/skills/../config.yaml", "local-test")[0] == 404, "Catalog exposed a local path")
    require(call("/skills", "local-test", "POST")[0] == 405, "Catalog accepted writes")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true",
                        help="Also test installer, updater and catalogue using disposable local fixtures.")
    args = parser.parse_args()
    try:
        static_checks()
        if args.smoke:
            with TemporaryDirectory(prefix=".msshi-check-", dir=ROOT) as scratch:
                installer_smoke(Path(scratch))
                updater_smoke(Path(scratch))
                global_smoke(Path(scratch))
                version_migration_smoke(Path(scratch))
                bridge_smoke(Path(scratch))
                upstream_smoke(Path(scratch))
            catalog_smoke()
            print("Smoke tests passed: installer, updater, global CLI, v2.1 migration, application routes, upstream cache and catalog guardrails")
        if not (ROOT / "LICENSE").is_file():
            print("Publication review: LICENSE is missing. Check the release license and provenance.")
    except (ValueError, OSError, SyntaxError, ET.ParseError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, f"Release check failed: {exc}\n")


if __name__ == "__main__":
    main()
