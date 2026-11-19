"""Preview/apply managed SOUL interaction blocks; never configure models or tools."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ('yukino', 'shizuka', 'val', 'kiki-chii', 'shikaku')
COMMON = (b'<!-- MSSHI USER ADDRESS BEGIN -->', b'<!-- MSSHI USER ADDRESS END -->')


def checked(value: Path) -> Path:
    path = Path(os.path.abspath(Path(value).expanduser()))
    for item in (path, *path.parents):
        if os.path.lexists(item) and (item.is_symlink() or getattr(item.lstat(), 'st_file_attributes', 0) & 0x400):
            raise ValueError('Refusing linked/reparse SOUL path: ' + str(item))
    return path


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic(path: Path, data: bytes) -> None:
    path = checked(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.msshi-soul-', delete=False) as handle:
        handle.write(data)
        staged = Path(handle.name)
    try:
        os.chmod(staged, 0o600)
        os.replace(staged, path)
    finally:
        staged.unlink(missing_ok=True)


def encode(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def markers(profile: str) -> list[tuple[bytes, bytes]]:
    if profile not in PROFILES:
        raise ValueError('Unknown MSSHI role')
    return [COMMON, (f'<!-- MSSHI INTERACTION {profile} BEGIN -->'.encode(),
                     f'<!-- MSSHI INTERACTION {profile} END -->'.encode())]


def legacy_markers(profile: str) -> tuple[bytes, bytes]:
    """Old mixed-workflow protocol; replaced only inside its exact managed range."""
    return (f'<!-- MSSHI COLLABORATION {profile} BEGIN -->'.encode(),
            f'<!-- MSSHI COLLABORATION {profile} END -->'.encode())


def span(data: bytes, begin: bytes, end: bytes) -> tuple[int, int] | None:
    left, right = data.count(begin), data.count(end)
    if left == right == 0:
        return None
    if left != 1 or right != 1:
        raise ValueError('Managed SOUL block is duplicated or incomplete; preserve and review it')
    first, last = data.index(begin), data.index(end) + len(end)
    if first >= last - len(end):
        raise ValueError('Managed SOUL block markers are out of order')
    return first, last


def render(original: bytes, template: bytes, profile: str) -> bytes:
    """Only marked ranges change; private persona bytes outside those ranges remain exact."""
    original.decode('utf-8-sig')
    newline = b'\r\n' if b'\r\n' in original else b'\n'
    result = original
    # Validate all managed ranges before preparing a replacement. Incomplete or
    # duplicated old blocks are never silently deleted as part of a migration.
    legacy = span(result, *legacy_markers(profile))
    incoming_interaction = markers(profile)[1]
    current_interaction = span(result, *incoming_interaction)
    ranges = [where for where in (span(result, *COMMON), legacy, current_interaction)
              if where is not None]
    if any(a[0] < b[1] and b[0] < a[1]
           for index, a in enumerate(ranges) for b in ranges[index + 1:]):
        raise ValueError('Managed SOUL ranges overlap; preserve and review the file')
    if legacy is not None:
        if current_interaction is None:
            required = span(template, *incoming_interaction)
            if required is None:
                raise ValueError('Public persona lacks the two-type interaction protocol')
            incoming = template[required[0]:required[1]].replace(b'\r\n', b'\n').replace(b'\n', newline)
            result = result[:legacy[0]] + incoming + result[legacy[1]:]
        else:
            # A previous migration may have added the new protocol without
            # withdrawing the old block. Remove only the known managed range.
            result = result[:legacy[0]] + result[legacy[1]:]
    for begin, end in markers(profile):
        required = span(template, begin, end)
        if required is None:
            raise ValueError('Public persona template lacks a required managed protocol')
        incoming = template[required[0]:required[1]].replace(b'\r\n', b'\n').replace(b'\n', newline)
        existing = span(result, begin, end)
        if existing is None:
            separator = newline if result.endswith(newline) else newline + newline
            result += separator + incoming + newline
        else:
            result = result[:existing[0]] + incoming + result[existing[1]:]
    return result


def protected(home: Path) -> dict[str, str]:
    """Hash only local protection evidence; secret/config contents never enter a receipt."""
    folders = [home, *(home / 'profiles' / name for name in PROFILES)]
    return {str(path): sha(path.read_bytes()) for folder in folders
            for name in ('config.yaml', 'SOUL.md', '.env')
            if (path := checked(folder / name)).is_file()}


def apply_protocol(home: Path, profiles: list[str], apply: bool = False, source: Path = ROOT) -> dict:
    home, source = checked(home), checked(source)
    names = list(dict.fromkeys(profiles))
    if not names or any(name not in PROFILES for name in names):
        raise ValueError('Choose existing named MSSHI profiles only')
    plans = []
    for name in names:
        soul = checked(home / 'profiles' / name / 'SOUL.md')
        template = checked(source / 'configs' / 'personas' / (name + '.md'))
        if not soul.is_file():
            raise ValueError('Existing named SOUL required: ' + str(soul))
        before = soul.read_bytes()
        after = render(before, template.read_bytes(), name)
        plans.append((name, soul, before, after))
    changes = [row for row in plans if row[2] != row[3]]
    result = {'operation': 'managed-soul-protocol', 'applied': False,
              'profiles': names, 'changed_profiles': [row[0] for row in changes],
              'protocol_schema': 2, 'scope': 'managed-ranges-only',
              'interaction_types': {name: (1 if name in {'yukino', 'shizuka'} else 2) for name in names},
              'config_or_model_written': False, 'vault_written': False, 'network_or_model_calls': 0}
    if not apply or not changes:
        result['status'] = 'preview' if not apply else 'already_current'
        return result
    before_protected = protected(home)
    folder = checked(home / 'msshi-runtime' / 'soul-receipts' /
                     (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '-' + uuid.uuid4().hex[:8]))
    receipt = folder / 'receipt.json'
    data = {'schema': 1, 'kind': 'managed-soul-protocol', 'home': str(home), 'state': 'applying',
            'created_utc': datetime.now(timezone.utc).isoformat(), 'entries': [],
            'protected_before_sha256': before_protected}
    # Prepare every backup and journal entry before the first SOUL write.
    for index, (name, soul, before, after) in enumerate(changes):
        backup = folder / f'{index:02d}-{name}.bak'
        atomic(backup, before)
        data['entries'].append({'profile': name, 'path': str(soul), 'backup': backup.name,
                                'before_sha256': sha(before), 'after_sha256': sha(after), 'applied': False})
    atomic(receipt, encode(data))
    try:
        for entry, (_, soul, before, after) in zip(data['entries'], changes):
            if soul.read_bytes() != before:
                raise ValueError('SOUL changed after preview; stop and review the new user edit')
            entry['write_intended'] = True
            atomic(receipt, encode(data))
            atomic(soul, after)
            entry['applied'] = True
            atomic(receipt, encode(data))
        after_protected = protected(home)
        selected = {str(row[1]) for row in changes}
        unchanged = {k: v for k, v in before_protected.items() if k not in selected} == {
            k: v for k, v in after_protected.items() if k not in selected}
        data.update(state='applied', non_selected_protected_files_preserved=unchanged,
                    protected_after_sha256=after_protected)
        atomic(receipt, encode(data))
        if not unchanged:
            raise ValueError('An unrelated protected file changed concurrently; inspect the receipt')
    except Exception:
        # Roll back only our still-matching applied blocks, never concurrent user edits.
        rollback(home, receipt, apply=True)
        raise
    return {**result, 'applied': True, 'status': 'applied', 'receipt': str(receipt),
            'non_selected_protected_files_preserved': True}


def rollback(home: Path, receipt: Path, apply: bool = False) -> dict:
    home, receipt = checked(home), checked(receipt)
    base = checked(home / 'msshi-runtime' / 'soul-receipts')
    if not receipt.is_relative_to(base) or receipt.name != 'receipt.json':
        raise ValueError('SOUL receipt is outside the selected Hermes root')
    data = json.loads(receipt.read_text(encoding='utf-8-sig'))
    if data.get('kind') != 'managed-soul-protocol' or data.get('schema') != 1 or data.get('home') != str(home):
        raise ValueError('Not a matching SOUL-only receipt')
    prepared = []
    for entry in data.get('entries', []):
        name = entry.get('profile')
        if name not in PROFILES:
            raise ValueError('Invalid receipt profile')
        path = checked(home / 'profiles' / name / 'SOUL.md')
        if entry.get('path') != str(path):
            raise ValueError('Receipt may restore SOUL only')
        backup_name = entry.get('backup', '')
        if not re.fullmatch(r'\d{2}-[a-z0-9-]+\.bak', backup_name):
            raise ValueError('Invalid SOUL backup filename')
        backup = checked(receipt.parent / backup_name)
        before = backup.read_bytes()
        if sha(before) != entry.get('before_sha256'):
            raise ValueError('SOUL backup hash mismatch')
        prepared.append((entry, path, before))
    restored, conflicts = [], []
    for entry, path, before in reversed(prepared):
        if not entry.get('applied') and not entry.get('write_intended'):
            continue
        if path.is_file() and sha(path.read_bytes()) == entry.get('before_sha256'):
            continue  # An intended write did not happen, or this entry is already restored.
        if not path.is_file() or sha(path.read_bytes()) != entry.get('after_sha256'):
            conflicts.append(str(path))
            continue
        if apply:
            atomic(path, before)
        restored.append(str(path))
    result = {'operation': 'rollback-managed-soul-protocol', 'applied': apply,
              'restored' if apply else 'would_restore': restored, 'conflicts': conflicts, 'receipt': str(receipt)}
    if apply:
        data['state'] = 'rollback_conflicts' if conflicts else 'rolled_back'
        data['rollback'] = result
        atomic(receipt, encode(data))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, required=True, help='Existing Hermes root; only named profile SOUL files can change.')
    parser.add_argument('--profiles', nargs='+', choices=PROFILES, default=list(PROFILES))
    parser.add_argument('--apply', action='store_true', help='Apply reviewed marked blocks with backups; default previews only.')
    parser.add_argument('--rollback', type=Path, help='Preview or apply a SOUL-only receipt rollback; later edits become conflicts.')
    args = parser.parse_args(argv)
    try:
        result = rollback(args.home, args.rollback, args.apply) if args.rollback else apply_protocol(args.home, args.profiles, args.apply)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result.get('conflicts') else 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, 'SOUL protocol: ' + str(error) + '\n')


if __name__ == '__main__':
    raise SystemExit(main())
