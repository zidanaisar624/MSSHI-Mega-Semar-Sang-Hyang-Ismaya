"""Read-only explanations for public MSSHI installation choices."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SECTIONS = ('modes', 'platforms', 'packs', 'skills', 'features', 'apps')


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def help_data(source=ROOT):
    path = source / 'configs/option_help.json'
    return read(path) if path.is_file() else {}


def describe(kind, name, *, source=ROOT, lang='id', aliases=None):
    """Return copy only; never probe apps, download dependencies or change settings."""
    data = help_data(source)
    canonical = (aliases or {}).get(name, name) if kind == 'skills' else name
    text = data.get(kind, {}).get(canonical, {}).get(lang, '')
    if not text and kind == 'skills':
        matrix = source / 'configs/bot_role_and_skill_matrix.json'
        if matrix.is_file():
            entry = next((row for row in read(matrix)['skills'] if row['slug'] == canonical), {})
            text = entry.get('purpose', '')
    if canonical != name:
        prefix = f'Alias {canonical}. ' if lang == 'id' else f'Alias of {canonical}. '
        return prefix + text
    return text


def skill_labels(source=ROOT, lang='id'):
    data = read(source / 'configs/bot_role_and_skill_matrix.json')
    labels = {}
    for row in data['skills']:
        if row.get('optional_path'):
            label = 'opsional; default OFF; runtime terpisah' if lang == 'id' else 'optional; default OFF; separate runtime'
        elif row['status'] == 'bundled':
            label = 'instruksi dibundel' if lang == 'id' else 'bundled instructions'
        else:
            label = 'eksternal; pemasangan terpisah' if lang == 'id' else 'external; separate installation'
        labels[row['slug']] = label
    for alias, canonical in data.get('aliases', {}).items():
        labels[alias] = labels[canonical]
    return labels


def menu_descriptions(items, kind, *, source=ROOT, lang='id', aliases=None):
    labels = skill_labels(source, lang) if kind == 'skills' else {}
    result = {}
    for name in items:
        text = describe(kind, name, source=source, lang=lang, aliases=aliases)
        if name in labels:
            text = f'[{labels[name]}] {text}'
        result[name] = text
    return result


def feature(name, *, source=ROOT, lang='id'):
    text = describe('features', name, source=source, lang=lang)
    if text:
        print(text)


def rows(source=ROOT, lang='id'):
    data = help_data(source)
    labels = skill_labels(source, lang)
    result = []
    for kind in SECTIONS[:-1]:
        for name, entry in data.get(kind, {}).items():
            result.append({'kind': kind, 'id': name, 'description': entry[lang],
                           **({'status': labels[name]} if kind == 'skills' and name in labels else {})})
    apps = source / 'skills/cli-anything-universal-bridge/scripts/connection_help.json'
    if apps.is_file():
        # The same copy travels with standalone bridge skills.
        for name, entry in read(apps).get('targets', {}).items():
            result.append({'kind': 'apps', 'id': name, 'description': entry[lang]})
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('item', nargs='?', help='ID fitur/skill/paket, misalnya rea, kat, filmmaking atau unslop.')
    parser.add_argument('--kind', choices=('all', *SECTIONS), default='all', help='Batasi daftar ke jenis pilihan tertentu.')
    parser.add_argument('--lang', choices=('id', 'en'), default='id', help='Bahasa penjelasan: id atau en.')
    parser.add_argument('--json', action='store_true', help='Keluarkan katalog penjelasan sebagai JSON.')
    args = parser.parse_args(argv)
    try:
        selected = rows(lang=args.lang)
        if args.kind != 'all':
            selected = [row for row in selected if row['kind'] == args.kind]
        if args.item:
            matrix = read(ROOT / 'configs/bot_role_and_skill_matrix.json')
            name = matrix.get('aliases', {}).get(args.item, args.item)
            selected = [row for row in selected if row['id'] == name]
            if not selected:
                raise ValueError(f'Pilihan tidak dikenal: {args.item}')
        if args.json:
            print(json.dumps({'language': args.lang, 'choices': selected}, ensure_ascii=False, indent=2))
        else:
            print('MSSHI v3.1.0 | Penjelasan pilihan' if args.lang == 'id' else 'MSSHI v3.1.0 | Choice guide')
            for row in selected:
                status = f" [{row['status']}]" if row.get('status') else ''
                print(f"  {row['kind']}/{row['id']}{status}: {row['description']}")
            print('\nInstruksi skill, aplikasi, runtime, model, dan akun adalah komponen terpisah. Opsi dapat ditambahkan nanti.'
                  if args.lang == 'id' else '\nSkill instructions, apps, runtimes, models and accounts are separate. Skipped options can be added later.')
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'msshi choices: {error}\n')


if __name__ == '__main__':
    raise SystemExit(main())
