"""Explicit opt-in installation of lightweight optional MSSHI skill wrappers."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True

import install_msshi as installer
from msshi_sources import data_root
from msshi_update import inventory

ROOT = Path(__file__).resolve().parents[1]
# Manifest declarations cannot turn arbitrary release directories into skills.
OPTIONAL_PATHS = {'rea': 'optional/rea'}


def optional_sources(source):
    """Read the public opt-in allowlist; old releases have no optional entries."""
    source = installer.absolute(source)
    manifest = source / 'optional' / 'manifest.json'
    installer.reject_links(manifest)
    if not manifest.exists():
        return {}
    data = installer.read_json(manifest)
    if (not isinstance(data, dict) or data.get('schema_version') != 1
            or not isinstance(data.get('entries'), list)):
        raise ValueError('Unsupported optional manifest')
    result = {}
    for entry in data['entries']:
        if not isinstance(entry, dict):
            raise ValueError('Invalid optional manifest entry')
        name = installer.safe_slug(entry.get('id'), 'optional skill')
        if (name in result or name not in OPTIONAL_PATHS
                or entry.get('path') != OPTIONAL_PATHS[name]
                or entry.get('public_default') is not False):
            raise ValueError(f'Invalid optional declaration: {name}')
        incoming = source / OPTIONAL_PATHS[name]
        installer.reject_links(incoming)
        result[name] = incoming
    return result


def binding_source(source, binding):
    """Resolve only an ordinary skill or an explicitly declared optional wrapper."""
    name = installer.safe_slug(binding['skill'], 'skill')
    relative = binding.get('source_rel', f'skills/{name}')
    if relative == f'skills/{name}' and binding.get('optional', False) is False:
        incoming = source / 'skills' / name
        if 'source_rel' in binding and not (incoming / 'SKILL.md').is_file():
            raise ValueError(f'Unknown managed source: {relative!r}')
    elif (name in OPTIONAL_PATHS and relative == OPTIONAL_PATHS[name]
          and binding.get('optional') is True and name in optional_sources(source)):
        incoming = source / relative
    else:
        raise ValueError(f'Unapproved managed source for {name}: {relative!r}')
    installer.reject_links(incoming)
    return incoming


def setup_targets(mode, selections, *, source=ROOT):
    """Choose only the setup destinations explicitly covered by this opt-in."""
    if mode in {'solo', 'selective'}:
        return list(selections)
    if mode == 'muza-preset':
        manifest = installer.read_json(source / 'optional' / 'manifest.json')
        entry = next(row for row in manifest['entries'] if row['id'] == 'rea')
        roles = installer.names(entry.get('roles', []), 'optional role')
        return [folder for folder in selections if folder.parent.name in roles]
    # A custom team has no implied Coder mapping. A separate explicit selection
    # is required, and piped wizard input must retain its existing prompt order.
    message = 'Pilih folder bot: msshi optional enable rea --target-dir PATH_TO_SKILLS'
    if not sys.stdin.isatty():
        print(message)
        return []
    from msshi_cli import checklist
    choices = {folder.parent.name: folder for folder in selections}
    print('Hanya folder bot yang dipilih akan menerima REA; bot lain tetap tanpa tambahan ini.')
    try:
        return [choices[name] for name in checklist(list(choices), 'bot untuk REA (opt-in)',
                {name: f'Pasang instruksi REA pada {folder}; runtime tetap terpisah.' for name, folder in choices.items()})]
    except (EOFError, ValueError):
        print(message)
        return []


def enable(name, target_dir, *, source=ROOT, home=None, install_runtime=False,
           hermes_home=None):
    """An explicit call authorizes this wrapper only; existing custom skills win."""
    name = installer.safe_slug(name, 'optional skill')
    source = installer.absolute(source)
    target = installer.absolute(target_dir)
    home = installer.absolute(home or data_root())
    sources = optional_sources(source)
    if name not in sources:
        raise ValueError(f'Optional skill is not declared: {name}')
    incoming = sources[name]
    installer.reject_links(target)
    if (target.is_relative_to(source) or source.is_relative_to(target)
            or target.is_relative_to(home) or home.is_relative_to(target)):
        raise ValueError('Optional skill target must be separate from release and MSSHI data')
    if not (incoming / 'SKILL.md').is_file():
        raise ValueError(f'Optional skill is missing: {incoming}')
    expected = inventory(incoming)
    destination = target / name
    copied = False
    if installer.existing(destination):
        try:
            exact = inventory(destination) == expected
        except (OSError, ValueError):
            exact = False
        if not exact:
            return {'id': name, 'target': str(destination), 'status': 'custom_preserved',
                    'registered': False, 'runtime_installed': False}
    elif name in installer.indexed_skills(target):
        return {'id': name, 'target': str(destination), 'status': 'custom_preserved',
                'registered': False, 'runtime_installed': False}
    else:
        installer.copy_skill(incoming, destination)
        copied = True
    from msshi_managed import load, register
    registration = register(home, source, [target], apply=True, include_optional=(name,), only_names={name})
    # A source-identical preexisting wrapper is safe to enroll without a baseline.
    registered = any(binding['skill'] == name and binding['logical'] == str(destination)
                     for binding in load(home).get('managed_bindings', []))
    result = {'id': name, 'target': str(destination),
              'status': 'enabled' if copied else 'already_present',
              'registered': registered, 'registration': registration, 'runtime_installed': False}
    if install_runtime:
        if not registered:
            raise ValueError('Optional runtime requires an explicitly registered wrapper')
        runtime_home = installer.absolute(hermes_home or os.environ.get('HERMES_HOME') or Path.home() / '.hermes')
        helper = source / 'scripts' / 'msshi_rea.py'
        installer.reject_links(helper)
        if not helper.is_file():
            raise ValueError(f'Optional runtime helper is missing: {helper}')
        subprocess.run([sys.executable, '-B', '-X', 'utf8', str(helper),
                        '--hermes-home', str(runtime_home), 'install'], check=True)
        result['runtime_installed'] = True
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT)
    sub = parser.add_subparsers(dest='action', required=True)
    listing = sub.add_parser('list', help='Lihat fungsi, peran, dan prasyarat opsi; semua default publik OFF.')
    listing.add_argument('--lang', choices=('id', 'en'), default='id', help='Bahasa penjelasan.')
    activate = sub.add_parser('enable', help='Pasang instruksi opsi yang dipilih secara eksplisit; runtime terpisah.',
        description='REA: analisis statis JavaScript/arsip milik Anda atau yang diizinkan. '
                    'Memasang wrapper ringan saja; default OFF. Runtime Node/npm dan engine native dipasang terpisah.')
    activate.add_argument('name', choices=tuple(OPTIONAL_PATHS))
    activate.add_argument('--target-dir', type=Path, required=True, help='Chosen host/profile skills directory.')
    activate.add_argument('--install-runtime', action='store_true', help='Juga unduh dependency npm ke runtime terisolasi; perlu Node/npm kompatibel dan internet. Engine native tidak ikut dipasang.')
    activate.add_argument('--hermes-home', type=Path, help='Hermes root/profile for the explicitly requested runtime.')
    args = parser.parse_args(argv)
    try:
        if args.action == 'list':
            from msshi_choices import describe
            result = {'optional_skills': [{'id': name, 'path': OPTIONAL_PATHS[name], 'public_default': False,
                      'description': describe('features', name, source=args.source, lang=args.lang),
                      'runtime': describe('features', name + '-runtime', source=args.source, lang=args.lang),
                      'recommended_role': 'Coder / Shikaku', 'installs': 'skill wrapper only'}
                      for name in optional_sources(args.source)]}
        else:
            from msshi_cli import locked
            with locked(data_root()):
                result = enable(args.name, args.target_dir, source=args.source,
                                install_runtime=args.install_runtime, hermes_home=args.hermes_home)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        parser.exit(1, f'msshi optional: {error}\n')


if __name__ == '__main__':
    raise SystemExit(main())
