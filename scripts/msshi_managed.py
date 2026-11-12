"""Enroll exact MSSHI copies, including explicitly reviewed shared skill links."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
from tempfile import mkdtemp
import sys

sys.dont_write_bytecode = True
from install_msshi import reject_links, safe_slug
from msshi_sources import data_root, write_json
from msshi_update import inventory, update_skill
from msshi_optional import binding_source, optional_sources

ROOT = Path(__file__).resolve().parents[1]

def digest(files):
    return hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def load(home):
    path = home / 'state.json'
    reject_links(path)
    state = json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else {'schema_version': 1, 'targets': {}}
    if state.get('schema_version') != 1 or not isinstance(state.get('targets'), dict):
        raise ValueError('Unsupported MSSHI state')
    bindings = state.get('managed_bindings', [])
    if not isinstance(bindings, list) or any(not isinstance(row, dict) for row in bindings):
        raise ValueError('Invalid managed binding registry')
    return state


def validate_sources(state, source):
    # Validate before ownership transfers or any writes, including unselected rows.
    for binding in state.get('managed_bindings', []):
        binding_source(source, binding)

def physical(logical):
    # Only an explicitly supplied single skill junction may be resolved. Ancestors
    # and all descendants of the resolved directory must remain ordinary paths.
    reject_links(logical.parent)
    actual = logical.resolve(strict=True)
    reject_links(actual)
    if not actual.is_dir() or not (actual / 'SKILL.md').is_file():
        raise ValueError(f'Not a skill directory: {logical}')
    return actual


def ordinary_owners(state):
    """Index existing regular updater ownership by actual skill directory."""
    owners = {}
    for root, skills in state.get('targets', {}).items():
        if not isinstance(skills, dict):
            raise ValueError('Invalid ordinary updater target registry')
        root = Path(root)
        reject_links(root)
        for slug in skills:
            name = safe_slug(slug, 'skill')
            logical = root / name
            if logical.exists():
                actual = physical(logical)
                owners.setdefault(actual, []).append({'root': str(root), 'skill': name})
    return owners


def split_ordinary_overlaps(bindings, owners):
    retained, transfers = [], []
    for binding in bindings:
        # Compare the recorded physical address, not a newly retargeted logical link.
        # Retargeted links remain in the managed registry and are blocked by refresh.
        actual = Path(binding['physical'])
        try:
            reject_links(actual)
            actual = actual.resolve(strict=True)
        except (OSError, ValueError):
            retained.append(binding)
            continue
        same_owner = owners.get(actual)
        if same_owner:
            try:
                stable = physical(Path(binding['logical'])) == actual
            except (OSError, ValueError):
                stable = False
            if stable:
                transfers.append({'skill': binding['skill'], 'logical': binding['logical'],
                                  'physical': str(actual), 'ordinary_owners': same_owner})
                continue
        retained.append(binding)
    return retained, transfers

def register(home, source, roots, baseline=None, apply=False, include_optional=(), only_names=None):
    state = load(home)
    validate_sources(state, source)
    owners = ordinary_owners(state)
    existing, transfers = split_ordinary_overlaps(state.get('managed_bindings', []), owners)
    keys = {(x['logical'], x['skill']) for x in existing}
    additions, skipped = [], []
    incoming_sources = [(path, False) for path in sorted((source / 'skills').iterdir())]
    optional = optional_sources(source) if include_optional else {}
    for name in dict.fromkeys(include_optional):
        if name not in optional:
            raise ValueError(f'Optional skill is not declared: {name}')
        incoming_sources.append((optional[name], True))
    for root in roots:
        root = root.absolute()
        reject_links(root)
        if not root.is_dir():
            raise ValueError(f'Skill root not found: {root}')
        for incoming, is_optional in incoming_sources:
            if not incoming.is_dir() or not (incoming / 'SKILL.md').is_file():
                continue
            name = safe_slug(incoming.name, 'skill')
            if only_names is not None and name not in only_names:
                continue
            logical = root / name
            if not logical.exists():
                continue
            if (str(logical), name) in keys:
                continue
            actual = physical(logical)
            if actual in owners:
                skipped.append({'skill': name, 'logical': str(logical), 'reason': 'ordinary_updater_owned',
                                'ordinary_owners': owners[actual]})
                continue
            # Never enroll the release source itself or updater's immutable data.
            if actual.is_relative_to(source) or source.is_relative_to(actual) or actual.is_relative_to(home):
                skipped.append({'skill': name, 'logical': str(logical), 'reason': 'source_or_state_overlap'})
                continue
            files = inventory(actual)
            approved = None
            for release in (source, baseline):
                old = ((optional_sources(release).get(name) if is_optional else release / 'skills' / name)
                       if release else None)
                if old and old.is_dir() and files == inventory(old):
                    approved = json.loads((release / 'VERSION.json').read_text(encoding='utf-8-sig'))['version']
                    break
            if approved is None:
                skipped.append({'skill': name, 'logical': str(logical), 'reason': 'custom_or_unproven'})
                continue
            binding = {'skill': name, 'logical': str(logical), 'physical': str(actual),
                       'fingerprint': digest(files), 'baseline_version': approved}
            if is_optional:
                binding.update(source_rel=incoming.relative_to(source).as_posix(), optional=True)
            additions.append(binding)
            keys.add((str(logical), name))
    result = {'registered_existing': len(existing), 'additions': additions, 'skipped': skipped,
              'ordinary_ownership_transfers': transfers, 'applied': apply}
    if apply:
        state['managed_bindings'] = existing + additions
        write_json(home / 'state.json', state)
    return result

def refresh(home, source, apply=False, names=None):
    state = load(home)
    validate_sources(state, source)
    owners = ordinary_owners(state)
    bindings, transfers = split_ordinary_overlaps(state.get('managed_bindings', []), owners)
    rows = [{'skill': x['skill'], 'logical': x['logical'], 'physical': x['physical'],
             'status': 'ordinary_updater_owned', 'ordinary_owners': x['ordinary_owners']} for x in transfers]
    if apply and transfers:
        # Only metadata is transferred. The ordinary updater keeps sole ownership;
        # no skill is written, removed, or adopted using a stale shared fingerprint.
        state['managed_bindings'] = bindings
        write_json(home / 'state.json', state)
    groups = {}
    selected_physical = ({Path(x['physical']) for x in bindings if x['skill'] in names}
                         if names else None)
    for binding in bindings:
        name = safe_slug(binding['skill'], 'skill')
        if selected_physical is not None and Path(binding['physical']) not in selected_physical:
            continue
        logical = Path(binding['logical'])
        try:
            actual = physical(logical)
            expected = Path(binding['physical'])
            reject_links(expected)
            expected = expected.resolve(strict=True)
            if actual != expected:
                raise ValueError('registered junction was retargeted')
            groups.setdefault(actual, []).append(binding)
        except (OSError, ValueError) as error:
            rows.append({'skill': name, 'logical': str(logical), 'status': 'blocked', 'reason': str(error)})
    selected_groups = 0
    for target, references in groups.items():
        aliases = sorted({x['skill'] for x in references})
        if names and not set(aliases).intersection(names):
            continue
        selected_groups += 1
        name, raw = aliases[0], str(target)
        base = {'skill': name, 'aliases': aliases, 'physical': raw, 'logical_references': len(references)}
        inputs = [binding_source(source, binding) for binding in references]
        if not all(incoming.is_dir() for incoming in inputs):
            rows.append({**base, 'status': 'retained_missing_upstream'})
            continue
        try:
            inventories = [inventory(incoming) for incoming in inputs]
            if any(files != inventories[0] for files in inventories[1:]):
                rows.append({**base, 'status': 'blocked', 'reason': 'ambiguous_alias_upstream'})
                continue
            incoming, new = inputs[0], inventories[0]
            current = inventory(target)
        except (OSError, ValueError) as error:
            rows.append({**base, 'status': 'blocked', 'reason': str(error)})
            continue
        old_hash = digest(current)
        status, backup = 'current', None
        if current != new:
            if any(x['fingerprint'] != old_hash for x in references):
                status = 'custom_preserved'
            elif apply:
                backup = Path(mkdtemp(prefix='.msshi-backup-', dir=target.parent.parent))
                update_skill(incoming, target, backup, new, current)
                status = 'updated'
            else:
                status = 'update_available'
        if apply and status in {'current', 'updated'}:
            for x in references:
                x['fingerprint'] = digest(new)
            # Checkpoint each successful physical update; shared targets updated once.
            write_json(home / 'state.json', state)
        rows.append({**base, 'status': status, 'backup': str(backup) if backup else None})
    return {'scope': 'exact registered MSSHI bundles only; custom/third-party packages retained',
            'bindings': len(bindings), 'physical_targets': selected_groups,
            'ordinary_ownership_transfers': transfers,
            'applied': apply, 'results': rows}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('register', 'status', 'update'))
    parser.add_argument('--source', type=Path, default=ROOT)
    parser.add_argument('--baseline', type=Path)
    parser.add_argument('--skills-dir', type=Path, action='append', default=[])
    parser.add_argument('--home', type=Path, default=data_root())
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--include-optional', choices=('rea',), action='append', default=[],
                        help='Explicitly enroll exact copies of this optional wrapper; default is none.')
    args = parser.parse_args(argv)
    try:
        from msshi_cli import locked
        with locked(args.home):
            if args.action == 'register':
                if not args.skills_dir:
                    raise ValueError('--skills-dir is required for registration')
                result = register(args.home, args.source.absolute(), args.skills_dir, args.baseline, args.apply,
                                  include_optional=args.include_optional)
            else:
                if args.include_optional:
                    raise ValueError('--include-optional is only valid for register')
                result = refresh(args.home, args.source.absolute(), args.apply and args.action == 'update')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return int(any(x.get('status') == 'blocked' for x in result.get('results', [])))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f'msshi managed: {error}\n')

if __name__ == '__main__':
    raise SystemExit(main())
