"""Versioned PDF manual catalog inspection, selection, and verified download."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

from install_msshi import absolute, read_json, reject_links
from msshi_sources import RAW, data_root, download, write_atomic


ROOT = Path(__file__).resolve().parents[1]
CATALOG_REL = Path("docs", "manuals", "pdf_catalog.json")
MAX_PDF_BYTES = 32 * 1024 * 1024


def default_manual_dest() -> Path:
    """Choose a clear local folder for downloaded PDF manuals."""
    if os.environ.get('MSSHI_PDF_DIR'):
        return absolute(os.environ['MSSHI_PDF_DIR'])
    if sys.platform == 'win32':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders') as key:
                value, _ = winreg.QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')
            return absolute(Path(os.path.expandvars(value)) / 'MSSHI_Manuals')
        except (OSError, ImportError, TypeError):
            pass
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
    aliases = {"3.1": catalog.get('latest_version', 'v3.1.0'), "3.0.0": "v3.0", "3.0": "v3.0"}
    normalized = aliases.get(key, key if key == 'latest' or key.startswith('v') else 'v' + key)
    for item in catalog["manuals"]:
        if item.get("version", "").lower() == normalized:
            return item
    available = ", ".join(item.get("version", "") for item in catalog["manuals"])
    raise ValueError(f"Versi panduan PDF tidak ditemukan: {version}. Tersedia: {available}")


def _validate_filename(filename: str) -> str:
    if not filename or any(char in filename for char in ('/', '\\', ':', '\0')) or filename in {".", ".."}:
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
    relative = Path(entry['rel_path'])
    if relative.is_absolute() or '..' in relative.parts or relative.parts[:2] != ('docs', 'manuals') or relative.suffix.lower() != '.pdf':
        raise ValueError('Path PDF harus berada di docs/manuals di dalam paket.')
    local_pdf = base / relative
    if not local_pdf.resolve().is_relative_to(base.resolve()):
        raise ValueError('Path PDF keluar dari source paket.')
    if local_pdf.is_file():
        reject_links(local_pdf)
        data = local_pdf.read_bytes()
        origin = str(local_pdf)
    else:
        url = f"{RAW}/{relative.as_posix()}"
        if entry.get('raw_download_url') not in (None, url):
            raise ValueError('URL PDF bukan URL kanonis repositori ini.')
        data = download(url, limit=MAX_PDF_BYTES)
        origin = url

    digest = hashlib.sha256(data).hexdigest()
    expected = entry.get("sha256")
    if not isinstance(expected, str) or not re.fullmatch(r'[0-9a-f]{64}', expected):
        raise ValueError('Katalog PDF harus menyertakan SHA256 yang valid.')
    if digest != expected:
        raise ValueError(f"Checksum SHA256 PDF tidak cocok ({digest} != {expected}).")
    if not data.startswith(b'%PDF-') or len(data) > MAX_PDF_BYTES:
        raise ValueError('Berkas panduan bukan PDF valid atau melebihi batas ukuran.')
    backup = None
    present = target_path.is_file() and hashlib.sha256(target_path.read_bytes()).hexdigest() == digest
    if target_path.exists() and not present:
        backup = target_path.with_name(target_path.stem + '.previous-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.pdf')
        reject_links(backup)
        write_atomic(backup, target_path.read_bytes())
    if not present:
        write_atomic(target_path, data)
    return {
        'status': 'already_present' if present else 'saved',
        "version": entry.get("version"),
        "title": entry.get("title_id") or filename,
        "pages": entry.get("pages"),
        "size_bytes": len(data),
        "sha256": digest,
        "origin": origin,
        "saved_to": str(target_path),
        'previous_backup': str(backup) if backup else None,
    }


def prompt_manual_download(args, source_root: Path | None = None, lang: str = "id") -> dict | None:
    """Automatically deliver the bundled guide; opt-out never blocks the main setup."""
    if getattr(args, "no_pdf", False) or os.environ.get('MSSHI_NO_PDF') == '1':
        return None
    requested_version = getattr(args, "pdf_version", None)
    explicit = bool(getattr(args, "download_pdf", False) or requested_version)
    base = Path(source_root) if source_root else ROOT
    if not explicit and (base / "configs" / "light_build_active.json").is_file():
        print("Light Build: panduan PDF ditunda agar hemat disk/unduhan. Unduh kapan saja via: msshi manual download --version latest")
        return None
    if not explicit and not (base / CATALOG_REL).is_file():
        # Old/minimal releases and offline fixtures never make an implicit network call.
        return None

    try:
        catalog = load_catalog(source_root)
    except (OSError, ValueError) as exc:
        print(f"Katalog panduan PDF tidak tersedia ({exc}); dilewati.")
        return None

    entry = resolve_manual(catalog, requested_version or 'latest')
    try:
        result = save_manual(entry, dest_dir=getattr(args, 'pdf_dest', None), source_root=source_root)
    except (OSError, ValueError) as error:
        if explicit:
            raise
        print(f'Panduan PDF belum dapat disalin ({error}). Coba: msshi manual download --dest PATH.')
        return {'status': 'manual_delivery_failed', 'reason': str(error)}
    print(f"PDF tersimpan: {result['saved_to']} ({result['pages']} hal, {result['size_bytes']:,} bytes)")
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="msshi manual", description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("list", help="Tampilkan daftar Buku Panduan PDF per versi.")
    dl = sub.add_parser("download", help="Unduh Buku Panduan PDF versi pilihan dengan verifikasi SHA256.")
    dl.add_argument("--version", default="latest", help="Versi PDF: latest atau versi yang tercantum di msshi manual list.")
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
