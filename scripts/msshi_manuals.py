"""Versioned PDF manual catalog inspection, selection, and verified download."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from install_msshi import absolute, read_json, reject_links
from msshi_sources import RAW, data_root, download, write_atomic


ROOT = Path(__file__).resolve().parents[1]
CATALOG_REL = Path("docs", "manuals", "pdf_catalog.json")
MAX_PDF_BYTES = 32 * 1024 * 1024


def default_manual_dest() -> Path:
    """Choose a clear local folder for downloaded PDF manuals."""
    downloads = Path.home() / "Downloads"
    if downloads.is_dir():
        return absolute(downloads / "MSSHI_Manuals")
    return absolute(data_root() / "manuals")


def load_catalog(source_root: Path | None = None) -> dict:
    """Read docs/manuals/pdf_catalog.json locally or from GitHub main."""
    base = Path(source_root) if source_root else ROOT
    local = base / CATALOG_REL
    if local.is_file():
        reject_links(local)
        data = read_json(local)
    else:
        payload = download(f"{RAW}/{CATALOG_REL.as_posix()}", limit=512 * 1024)
        data = json.loads(payload.decode("utf-8-sig"))
    if not isinstance(data, dict) or not isinstance(data.get("manuals"), list):
        raise ValueError("Format pdf_catalog.json tidak valid.")
    return data


def resolve_manual(catalog: dict, version: str = "latest") -> dict:
    """Find a catalog entry matching 'latest', 'v3.1.0', '3.1.0', 'v3.0', or '3.0.0'."""
    key = (version or "latest").strip().lower()
    aliases = {"3.1.0": "v3.1.0", "3.1": "v3.1.0", "3.0.0": "v3.0", "3.0": "v3.0"}
    normalized = aliases.get(key, key)
    for item in catalog["manuals"]:
        if item.get("version", "").lower() == normalized:
            return item
    available = ", ".join(item.get("version", "") for item in catalog["manuals"])
    raise ValueError(f"Versi panduan PDF tidak ditemukan: {version}. Tersedia: {available}")


def _validate_filename(filename: str) -> str:
    if not filename or "/" in filename or "\\" in filename or filename in {".", ".."}:
        raise ValueError(f"Nama file PDF tidak valid: {filename!r}")
    if Path(filename).name != filename or not filename.lower().endswith(".pdf"):
        raise ValueError(f"Nama file PDF tidak aman: {filename!r}")
    return filename


def save_manual(entry: dict, dest_dir: Path | None = None, source_root: Path | None = None) -> dict:
    """Copy a cataloged PDF from source_root or download it over HTTPS and verify SHA256."""
    filename = _validate_filename(entry["filename"])
    target_dir = absolute(dest_dir) if dest_dir else default_manual_dest()
    reject_links(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / filename
    reject_links(target_path)

    base = Path(source_root) if source_root else ROOT
    local_pdf = base / entry["rel_path"]
    if local_pdf.is_file():
        reject_links(local_pdf)
        data = local_pdf.read_bytes()
        origin = str(local_pdf)
    else:
        url = entry.get("raw_download_url") or f"{RAW}/{entry['rel_path']}"
        data = download(url, limit=MAX_PDF_BYTES)
        origin = url

    digest = hashlib.sha256(data).hexdigest()
    expected = entry.get("sha256")
    if expected and digest != expected:
        raise ValueError(f"Checksum SHA256 PDF tidak cocok ({digest} != {expected}).")

    write_atomic(target_path, data)
    return {
        "version": entry.get("version"),
        "title": entry.get("title_id") or filename,
        "pages": entry.get("pages"),
        "size_bytes": len(data),
        "sha256": digest,
        "origin": origin,
        "saved_to": str(target_path),
    }


def prompt_manual_download(args, source_root: Path | None = None, lang: str = "id") -> dict | None:
    """Optionally offer or run PDF manual download at the end of setup/update."""
    if getattr(args, "no_pdf", False):
        return None
    requested_version = getattr(args, "pdf_version", None)
    explicit = bool(getattr(args, "download_pdf", False) or requested_version)
    if not explicit and not sys.stdin.isatty():
        return None

    try:
        catalog = load_catalog(source_root)
    except (OSError, ValueError) as exc:
        print(f"Katalog panduan PDF tidak tersedia ({exc}); dilewati.")
        return None

    selected_version = requested_version or "latest"
    if not explicit:
        header = (
            "\n=== Buku Panduan PDF Lengkap ==="
            if lang == "id"
            else "\n=== Complete PDF Client Handbook ==="
        )
        print(header)
        for item in catalog["manuals"]:
            size_mb = item.get("size_bytes", 0) / (1024 * 1024)
            title = item.get("title_id") if lang == "id" else item.get("title_en")
            print(f"  - [{item['version']}] {title} ({item.get('pages', '?')} hal, {size_mb:.2f} MB)")
        prompt = (
            "Apakah Anda ingin sekalian mengunduh Buku Panduan PDF Lengkap untuk versi ini? [Y/N/P(ilih versi), default N]: "
            if lang == "id"
            else "Download the Complete PDF Handbook for this version now? [Y/N/P(pick version), default N]: "
        )
        try:
            answer = input(prompt).strip().lower()
        except EOFError:
            return None
        if answer in {"", "n", "no", "tidak", "skip"}:
            print("Unduh PDF dilewati. Kapan saja bisa unduh lewat: msshi manual download")
            return None
        if answer in {"p", "pilih", "pick", "2"}:
            ver = input("Ketik versi [latest / v3.1.0 / v3.0, default v3.1.0]: ").strip() or "v3.1.0"
            selected_version = ver
        elif answer not in {"y", "yes", "ya", "1"}:
            print("Pilihan tidak dikenal; unduh PDF dilewati.")
            return None

    entry = resolve_manual(catalog, selected_version)
    dest = getattr(args, "pdf_dest", None)
    result = save_manual(entry, dest_dir=dest, source_root=source_root)
    print(f"PDF tersimpan: {result['saved_to']} ({result['pages']} hal, {result['size_bytes']:,} bytes)")
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="msshi manual", description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("list", help="Tampilkan daftar Buku Panduan PDF per versi.")
    dl = sub.add_parser("download", help="Unduh Buku Panduan PDF versi pilihan dengan verifikasi SHA256.")
    dl.add_argument("--version", default="latest", help="Versi PDF: latest, v3.1.0, atau v3.0.")
    dl.add_argument("--dest", type=Path, help="Folder tujuan simpan PDF (default: ~/Downloads/MSSHI_Manuals).")
    dl.add_argument("--json", action="store_true", help="Cetak output sebagai JSON.")

    args = parser.parse_args(argv)
    catalog = load_catalog(ROOT)
    if args.action == "list":
        print(json.dumps(catalog, ensure_ascii=False, indent=2))
        return 0
    entry = resolve_manual(catalog, args.version)
    result = save_manual(entry, dest_dir=args.dest, source_root=ROOT)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"PDF {result['version']} tersimpan di: {result['saved_to']}")
        print(f"SHA256 terverifikasi: {result['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
