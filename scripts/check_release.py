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
import stat
import subprocess
import sys
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True

from catalog_api import catalog_handler

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "configs" / "bot_role_and_skill_matrix.json"
LOCAL_FILES = re.compile(r"(?:^|/)(?:\.env(?:\.[^/]+)?|[^/]+\.(?:pem|key|p12)|"
                         r"(?:curiosity_ledger|\.msshi-backup-[^/]*|\.msshi-stage-[^/]*))(?:/|$)", re.I)
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
    sources = {row["source"] for row in upstreams["entries"]}
    require(len(sources) == len(upstreams["entries"]) == version["external_sources"],
            "Upstream inventory and VERSION.json disagree")
    require(len(matrix["bots"]) == 5 and len(matrix["packs"]) == 6,
            "Preset must describe five bots and six packs")

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
            require(header and re.search(rf"^name:\s*{re.escape(path.parent.name)}\s*$", header[1], re.M)
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


def run_cli(script, *args, ok=True):
    result = subprocess.run(
        [sys.executable, "-B", "-X", "utf8", str(ROOT / "scripts" / script), *map(str, args)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=60,
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
    require(len(list(target.glob("*/SKILL.md"))) == 50, "Solo did not install all bundled skills")
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
    team = work / "preset"
    run_cli("install_msshi.py", "--mode", "muza-preset", *options, team, "--apply")
    require(len(list(team.glob("*/SOUL.md"))) == 5 and len(list(team.glob("*/AGENTS.md"))) == 5,
            "Preset did not write five workspaces")
    matrix = read_json(MATRIX)
    custom = matrix["bots"][0]
    custom["id"] = "test-bot"
    custom["label"] = "Test Bot"
    matrix["bots"] = [custom]
    matrix_path = work / "matrix.json"
    matrix_path.write_text(json.dumps(matrix), encoding="utf-8")
    run_cli("install_msshi.py", "--mode", "custom-bots", "--matrix", matrix_path,
            *options, work / "team", "--apply")
    require((work / "team" / "test-bot" / "SOUL.md").is_file(), "Custom bot workspace missing")
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
            catalog_smoke()
            print("Smoke tests passed: four installer modes, three updater modes and catalog guardrails")
        if not (ROOT / "LICENSE").is_file():
            print("Publication review: LICENSE is missing. Check the release license and provenance.")
    except (ValueError, OSError, SyntaxError, ET.ParseError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, f"Release check failed: {exc}\n")


if __name__ == "__main__":
    main()
