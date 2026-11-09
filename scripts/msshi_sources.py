"""Fetch the release and optional upstream references without running their code."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

sys.dont_write_bytecode = True

from install_msshi import absolute, read_json, reject_links, safe_slug


REPOSITORY = "https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya.git"
RAW = "https://raw.githubusercontent.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/main"
COMMIT = re.compile(r"[0-9a-f]{40}")
REPO_PATH = re.compile(r"/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")


def data_root():
    if value := os.environ.get("MSSHI_HOME"):
        return absolute(value)
    home = Path.home()
    if os.name == "nt":
        return absolute(os.environ.get("LOCALAPPDATA") or home / "AppData" / "Local") / "MSSHI"
    return absolute(os.environ.get("XDG_DATA_HOME") or home / ".local" / "share") / "msshi"


def write_atomic(path, content):
    reject_links(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(prefix=".msshi-", dir=path.parent, delete=False) as handle:
        temp = Path(handle.name)
        try:
            handle.write(content)
        except OSError:
            handle.close()
            temp.unlink(missing_ok=True)
            raise
    try:
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def write_json(path, value):
    write_atomic(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def download(url, limit=2 * 1024 * 1024):
    with urlopen(Request(url, headers={"User-Agent": "MSSHI-release-cli"}), timeout=30) as response:
        if urlsplit(response.url).scheme != "https":
            raise ValueError("Unduhan dialihkan ke alamat non-HTTPS.")
        content = response.read(limit + 1)
    if len(content) > limit:
        raise ValueError("Unduhan metadata melebihi batas ukuran.")
    return content


def git(*args, cwd=None):
    env = {key: value for key, value in os.environ.items()
           if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_TERMINAL_PROMPT="0", GIT_LFS_SKIP_SMUDGE="1")
    result = subprocess.run(
        ["git", "-c", "core.fsmonitor=false", "-c", "core.longpaths=true",
         "-c", "protocol.allow=never", "-c", "protocol.https.allow=always",
         "-c", "credential.helper=", *map(str, args)],
        cwd=cwd, env=env, capture_output=True, text=True, errors="replace", timeout=300,
    )
    if result.returncode:
        detail = result.stderr.strip().splitlines()
        raise ValueError("\n".join(detail[-8:]) if detail else f"Git keluar dengan status {result.returncode}.")
    return result.stdout.strip()


def clone(url, destination, branch=None, *, metadata_only=False):
    options = ["--branch", branch] if branch else []
    if metadata_only:
        options += ["--filter=blob:none", "--no-checkout"]
    git("clone", "--template=", "--depth", "1", "--no-tags", *options, "--", url, destination)
    commit = git("rev-parse", "HEAD", cwd=destination)
    if not COMMIT.fullmatch(commit):
        raise ValueError("Commit Git tidak valid.")
    return commit


def upstream_entries(manifest):
    reject_links(manifest)
    data = read_json(manifest)
    if data.get("schema_version") != 1:
        raise ValueError("Manifest upstream harus memakai schema_version 1.")
    items = {}
    for entry in data["entries"]:
        name = safe_slug(entry["id"], "upstream")
        kind, source = entry["source_type"], urlsplit(entry["source"])
        host, path = source.netloc.lower(), source.path.rstrip("/")
        expected = {"git": "github.com", "model-card": "huggingface.co", "registry-site": "clianything.cc"}
        if (name in items or source.scheme != "https" or expected.get(kind) != host
                or (kind != "registry-site" and not REPO_PATH.fullmatch(path))
                or (kind == "registry-site" and path)):
            raise ValueError(f"Sumber upstream tidak didukung: {name}.")
        if kind == "git":
            url = f"https://{host}{path.removesuffix('.git')}.git"
        elif kind == "model-card":
            url = f"https://{host}{path}/raw/main/README.md"
        else:
            url = f"https://{host}/"
        items[name] = (kind, url, entry["pack"])
    return items


def fetch_upstreams(manifest, cache, packs=None):
    """Store commit-addressed snapshots, the model card and a registry page."""
    items = upstream_entries(manifest)
    cache = absolute(cache)
    reject_links(cache)
    cache.mkdir(parents=True, exist_ok=True)
    lock = cache / ".msshi-update-lock"
    lock.mkdir()
    try:
        rows = {}
        for name, (kind, url, pack) in items.items():
            if packs and pack not in packs:
                continue
            print(f"Upstream {name}...", file=sys.stderr)
            try:
                folder = cache / name
                reject_links(folder)
                folder.mkdir(exist_ok=True)
                if kind == "git":
                    with TemporaryDirectory(prefix=".msshi-stage-", dir=folder) as staging:
                        source = Path(staging) / "repo"
                        commit = clone(url, source, metadata_only=True)
                        destination = folder / commit
                        reject_links(destination)
                        if destination.exists():
                            reject_links(destination / ".git")
                            if (git("rev-parse", "HEAD", cwd=destination) != commit
                                    or git("config", "--local", "--get", "remote.origin.url",
                                           cwd=destination) != url):
                                raise ValueError("Identitas snapshot cache berubah. Periksa salinan sebelum memperbarui.")
                        else:
                            source.rename(destination)
                    row = {"status": "cached", "commit": commit, "layout": "git_objects",
                           "location": str(destination)}
                else:
                    destination = folder / ("MODEL_CARD.md" if kind == "model-card" else "registry.html")
                    write_atomic(destination, download(url))
                    row = {"status": "cached", "location": str(destination)}
            except (OSError, ValueError, subprocess.SubprocessError) as error:
                row = {"status": "failed", "error": str(error)}
                print(f"  {error}", file=sys.stderr)
            rows[name] = {"kind": kind, "source": url, **row}
        write_json(cache / "last-fetch.json", rows)
    finally:
        lock.rmdir()
    success = sum(row["status"] == "cached" for row in rows.values())
    print(f"Upstream: {success}/{len(rows)} tersimpan. Laporan: {cache / 'last-fetch.json'}", file=sys.stderr)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstreams-dir", type=Path, default=data_root() / "upstreams")
    args = parser.parse_args()
    manifest = Path(__file__).resolve().parents[1] / "configs" / "upstreams.json"
    try:
        return int(any(row["status"] == "failed"
                       for row in fetch_upstreams(manifest, args.upstreams_dir).values()))
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f"msshi: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
