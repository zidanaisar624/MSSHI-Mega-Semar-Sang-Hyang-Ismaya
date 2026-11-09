"""Update installed MSSHI skills from a reviewed release folder."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import stat
import sys
from tempfile import mkdtemp


ROOT = Path(__file__).resolve().parents[1]
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def validate_path(path: Path) -> None:
    for part in (*reversed(path.parents), path):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or (
            getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        ):
            raise ValueError(f"Symlink atau junction tidak didukung: {part}")


def inventory(path: Path) -> dict[str, str]:
    validate_path(path)
    if not path.is_dir():
        raise ValueError(f"Folder skill tidak ada: {path}")
    result = {}
    for entry in sorted(path.rglob("*")):
        validate_path(entry)
        if entry.is_file():
            digest = hashlib.sha256()
            with entry.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            result[entry.relative_to(path).as_posix()] = digest.hexdigest()
        elif not entry.is_dir():
            raise ValueError(f"Entri tidak didukung: {entry}")
    return result


def release_version(path: Path) -> str:
    version_file = path / "VERSION.json"
    validate_path(version_file)
    return json.loads(version_file.read_text(encoding="utf-8-sig"))["version"]


def update_skill(incoming: Path, target: Path, backup_root: Path,
                 source_files: dict[str, str], target_files: dict[str, str]) -> None:
    # Keep staging outside the discoverable skills tree, on its parent volume.
    workspace = target.parent.parent
    staging = Path(mkdtemp(prefix=".msshi-stage-", dir=workspace))
    candidate = staging / "incoming"
    backup = backup_root / target.name
    try:
        shutil.copytree(incoming, candidate, symlinks=True)
        if inventory(candidate) != source_files or inventory(target) != target_files:
            raise ValueError(f"Isi berubah selama persiapan: {target.name}")
        target.rename(backup)
        try:
            candidate.rename(target)
        except OSError:
            backup.rename(target)
            raise
    finally:
        validate_path(staging)
        if staging.resolve(strict=True).parent != workspace:
            raise ValueError(f"Folder sementara berada di luar target: {staging}")
        shutil.rmtree(staging)


def run(args: argparse.Namespace) -> dict:
    source = args.source.absolute()
    validate_path(source)
    source = source.resolve(strict=True)
    available = release_version(source)
    baseline = args.baseline.absolute() if args.baseline else None
    installed_version = release_version(baseline) if baseline else None
    if baseline:
        baseline = baseline.resolve(strict=True)
    destination = args.skills_dir.absolute()
    validate_path(destination)
    if not destination.is_dir():
        raise ValueError(f"Folder instalasi tidak ada: {destination}")
    destination = destination.resolve(strict=True)
    for release in (source, baseline):
        if release and (destination.is_relative_to(release / "skills")
                        or (release / "skills").is_relative_to(destination)):
            raise ValueError("Folder instalasi harus terpisah dari folder skill sumber dan baseline.")
    upstream = source / "skills"
    validate_path(upstream)
    selected = set(args.skills or ())
    if selected and args.mode != "select":
        raise ValueError("--skills hanya berlaku untuk --mode select.")
    if args.mode == "select" and not selected:
        raise ValueError("--mode select memerlukan --skills SLUG [SLUG ...].")
    if args.mode == "check" and args.apply:
        raise ValueError("--mode check hanya membaca.")
    if not all(SLUG.fullmatch(name) for name in selected):
        raise ValueError("Slug skill harus memakai huruf kecil, angka, dan tanda hubung.")
    names = selected or {path.name for path in upstream.iterdir()
                         if SLUG.fullmatch(path.name) and (destination / path.name).is_dir()}
    rows = []
    pending = []
    for name in sorted(names):
        incoming, target = upstream / name, destination / name
        source_files, target_files = inventory(incoming), inventory(target)
        if "SKILL.md" not in source_files or "SKILL.md" not in target_files:
            raise ValueError(f"SKILL.md hilang: {name}")
        if source_files == target_files:
            status = "current"
        elif args.replace_custom or (baseline and (old := baseline / "skills" / name).is_dir()
                                      and inventory(old) == target_files):
            status = "update_available"
            pending.append((incoming, target, source_files, target_files))
        else:
            status = "different_needs_baseline_or_review"
        rows.append({"skill": name, "status": status})
    backup_root = None
    if args.apply and pending:
        lock = destination / ".msshi-update-lock"
        try:
            lock.mkdir()
        except FileExistsError as exc:
            raise ValueError(f"Ada pembaruan lain atau lock tersisa: {lock}") from exc
        try:
            backup_root = Path(mkdtemp(prefix=".msshi-backup-", dir=destination.parent))
            for incoming, target, source_files, target_files in pending:
                update_skill(incoming, target, backup_root, source_files, target_files)
                next(row for row in rows if row["skill"] == target.name)["status"] = "updated"
        finally:
            lock.rmdir()
    return {"mode": args.mode, "baseline_version": installed_version, "source_version": available,
            "backup": str(backup_root) if backup_root else None, "skills": rows}


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="msshi-update",
        description="MSSHI — Mega Semar Sang Hyang Ismaya: Sovereign Sage")
    parser.add_argument("--mode", choices=("check", "auto", "select"), default="check")
    parser.add_argument("--source", type=Path, default=ROOT, help="Folder rilis baru yang sudah ditinjau")
    parser.add_argument("--baseline", type=Path, help="Folder rilis yang dahulu dipasang")
    parser.add_argument("--skills-dir", type=Path, required=True)
    parser.add_argument("--skills", nargs="+", help="Slug yang dipilih dalam mode select")
    parser.add_argument("--apply", action="store_true", help="Terapkan perubahan dengan cadangan")
    parser.add_argument("--replace-custom", action="store_true",
                        help="Izinkan menimpa isi berbeda setelah meninjau dan mencadangkannya")
    args = parser.parse_args()
    try:
        print(json.dumps(run(args), ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError) as error:
        print(f"msshi-update: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
