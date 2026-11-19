"""Store a user's browser choice; never start a browser, log in, or copy cookies."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
import uuid

import msshi_hermes_profiles as hermes_profiles

BROWSERS = ('chrome', 'edge', 'firefox', 'none')
RELATIVE = Path('msshi-private/browser/preferences.json')


def checked(path: Path) -> Path:
    result = Path(os.path.abspath(Path(path).expanduser()))
    for part in (result, *result.parents):
        if os.path.lexists(part) and (part.is_symlink() or getattr(part.lstat(), 'st_file_attributes', 0) & 0x400):
            raise ValueError('Browser preferences must not cross a symlink/junction')
    return result


def label(value: str, field: str) -> str:
    value = str(value or '').strip()
    if len(value) > 120 or any(ord(c) < 32 for c in value):
        raise ValueError(field + ' must be a single label of at most 120 characters')
    if any(part in value.lower() for part in ('sk-proj-', 'github_pat_', '-----begin', 'access_token=', 'api_key=')):
        raise ValueError('Enter a label only, never a password or API token')
    return value


def encode(data: dict) -> bytes:
    return (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def atomic(path: Path, data: bytes) -> None:
    checked(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.msshi-browser-', delete=False) as stream:
        stream.write(data)
        candidate = Path(stream.name)
    try:
        os.chmod(candidate, 0o600)
        os.replace(candidate, path)
    finally:
        candidate.unlink(missing_ok=True)


def root_home(home: Path) -> Path:
    return checked(hermes_profiles.normalize_hermes_root(home))


def current(home: Path) -> dict:
    home = root_home(home)
    path = checked(home / RELATIVE)
    if not path.is_file():
        return {'schema': 1, 'status': 'not_selected', 'browser': None,
                'profile_label': '', 'account_label': '', 'auto_open_on_boot': False,
                'logged_in': 'not_verified', 'cookies_copied': False,
                'model_provider_mutated': False, 'network_requests': 0}
    if path.stat().st_size > 65536:
        raise ValueError('Browser preference file is unexpectedly large')
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(data, dict) or data.get('schema') != 1 or data.get('browser') not in BROWSERS:
        raise ValueError('Invalid stored browser choice; preserved for review')
    return {**data, 'status': 'selected' if data['browser'] != 'none' else 'disabled_by_user',
            'logged_in': 'not_verified', 'network_requests': 0,
            'preference_file': str(path)}


def select(home: Path, browser: str, profile_label: str = '', account_label: str = '') -> dict:
    """Write only MSSHI-owned preference/receipt files; config and credentials stay untouched."""
    if browser not in BROWSERS:
        raise ValueError('Choose chrome, edge, firefox, or none')
    home = root_home(home)
    path = checked(home / RELATIVE)
    original = path.read_bytes() if path.is_file() else None
    data = {'schema': 1, 'browser': browser,
            'profile_label': label(profile_label, 'Profile label'),
            'account_label': label(account_label, 'Account label'),
            'auto_open_on_boot': False, 'account_login': 'manual_in_selected_browser',
            'account_transfer': False, 'cookies_copied': False,
            'model_provider_mutated': False,
            'note': 'Labels describe user intent only; they do not prove login or authorize cookie transfer.'}
    content = encode(data)
    if original == content:
        return {**current(home), 'changed': False, 'receipt': None}
    folder = checked(home / 'msshi-runtime/browser-receipts' /
                     (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '-' + uuid.uuid4().hex[:8]))
    receipt = folder / 'receipt.json'
    journal = {'schema': 1, 'kind': 'browser-preference-only', 'home': str(home),
               'target': str(path), 'before_sha256': hashlib.sha256(original).hexdigest() if original is not None else None,
               'after_sha256': hashlib.sha256(content).hexdigest(), 'backup': 'preferences.bak' if original is not None else None,
               'state': 'prepared', 'credentials_read_or_written': False, 'browser_started': False}
    if original is not None:
        atomic(folder / 'preferences.bak', original)
    atomic(receipt, encode(journal))
    if (path.read_bytes() if path.is_file() else None) != original:
        raise ValueError('Preferences changed concurrently; preserve the new user edit')
    try:
        atomic(path, content)
        journal['state'] = 'applied'
        atomic(receipt, encode(journal))
    except OSError:
        # Restore only our still-matching write; never clobber a concurrent edit.
        if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == journal['after_sha256']:
            if original is None:
                path.unlink()
            else:
                atomic(path, original)
        raise
    return {**current(home), 'changed': True, 'receipt': str(receipt)}


def rollback(home: Path, receipt: Path, apply: bool = False) -> dict:
    home, receipt = root_home(home), checked(receipt)
    if not receipt.is_relative_to(home / 'msshi-runtime/browser-receipts') or receipt.name != 'receipt.json':
        raise ValueError('Choose a browser preference receipt inside the selected Hermes root')
    data = json.loads(receipt.read_text(encoding='utf-8-sig'))
    target = checked(home / RELATIVE)
    if (data.get('schema') != 1 or data.get('kind') != 'browser-preference-only'
            or data.get('home') != str(home) or data.get('target') != str(target)):
        raise ValueError('Not a matching browser-preference receipt; no config/account rollback performed')
    before = data.get('before_sha256')
    backup = None
    if before is not None:
        if data.get('backup') != 'preferences.bak':
            raise ValueError('Invalid preference backup')
        backup = checked(receipt.parent / 'preferences.bak').read_bytes()
        if hashlib.sha256(backup).hexdigest() != before:
            raise ValueError('Preference backup hash mismatch')
    current_hash = hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else None
    if current_hash == before:
        return {'status': 'already_restored', 'applied': False, 'receipt': str(receipt)}
    if current_hash != data.get('after_sha256'):
        return {'status': 'conflict_preserved', 'applied': False, 'receipt': str(receipt)}
    if apply:
        if backup is None:
            target.unlink()
        else:
            atomic(target, backup)
        data['state'] = 'rolled_back'
        atomic(receipt, encode(data))
    return {'status': 'restored' if apply else 'rollback_preview', 'applied': apply,
            'target': str(target), 'receipt': str(receipt), 'credentials_read_or_written': False}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', '--hermes-home', dest='home', type=Path,
                        default=hermes_profiles.resolve_hermes_home())
    parser.add_argument('--status', action='store_true', help='Read the saved choice without accessing a browser/account.')
    parser.add_argument('--browser', choices=BROWSERS, help='Save the requested browser; none opts out.')
    parser.add_argument('--profile-label', default='', help='Profile label only; no profile directory/cookies are read.')
    parser.add_argument('--account-label', default='', help='Account label only; sign in manually in the selected browser.')
    # Old command lines must not silently reinstall Steel or transfer an account.
    for name in ('install', 'steel-ready', 'personal-account', 'account-transfer', 'approved'):
        parser.add_argument('--' + name, action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--steel-source', help=argparse.SUPPRESS)
    parser.add_argument('--approval-note', default='', help=argparse.SUPPRESS)
    parser.add_argument('--rollback', type=Path, help='Preview restoring only this browser-preference receipt.')
    parser.add_argument('--apply', action='store_true', help='Apply a selected preference rollback; otherwise preview only.')
    args = parser.parse_args(argv)
    try:
        if any((args.install, args.steel_ready, args.personal_account, args.account_transfer,
                args.approved, args.steel_source, args.approval_note)):
            result = {'status': 'legacy_steel_action_retired', 'changed': False,
                      'message': 'Steel/account-transfer setup is no longer provided. Choose a browser with --browser; log in manually.',
                      'network_requests': 0, 'credentials_read_or_written': False}
        elif args.rollback:
            result = rollback(args.home, args.rollback, args.apply)
        elif args.browser:
            result = select(args.home, args.browser, args.profile_label, args.account_label)
        elif args.profile_label or args.account_label:
            raise ValueError('Profile/account labels require --browser')
        else:
            result = current(args.home)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, TypeError) as error:
        parser.exit(1, 'Browser choice: ' + str(error) + '\n')


if __name__ == '__main__':
    raise SystemExit(main())
