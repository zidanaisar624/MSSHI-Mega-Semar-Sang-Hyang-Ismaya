"""Plan a new native Hermes profile; provisioning is explicit and model-independent."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import msshi_hermes_profiles as profiles
import msshi_trim_setup as trim
import msshi_skill_index as skill_index
import msshi_light as light_mod

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = 'https://github.com/BkashJEE/hermes-bot-forge'


def roster(home):
    result = []
    for identifier, folder in [('default', home), *profiles.live_named_profiles(home).items()]:
        if not folder.is_dir():
            continue
        scan = skill_index.scan_profile_skills(folder / 'skills', write_cache=False, source=ROOT)
        result.append({'profile': identifier, 'skills': [row['slug'] for row in scan['skills']]})
    return result


def provision(home, blueprint, apply=False):
    """Use the native MSSHI profile transaction, without running the external Forge."""
    if set(blueprint) != {'id', 'name', 'purpose', 'skills', 'gap', 'reviews'}:
        raise ValueError('Blueprint must contain id, name, purpose, skills, gap and reviews only (no model, provider or connection settings).')
    identifier = blueprint['id']
    if not isinstance(identifier, str) or not profiles.valid_profile_id(identifier) or identifier == 'default':
        raise ValueError('Choose a new valid named profile ID.')
    for field in ('name', 'purpose', 'gap'):
        value = blueprint[field]
        if not isinstance(value, str) or not value.strip() or len(value) > 2048 or '\x00' in value:
            raise ValueError(f'Invalid field: {field}')
    if (home / 'profiles' / identifier).exists() or (home / 'profiles' / '.deleted' / identifier).exists():
        raise ValueError('Profile ID already exists or was deleted. Choose another ID.')
    if not isinstance(blueprint['reviews'], dict) or not blueprint['reviews'] or any(not isinstance(k,str) or not isinstance(v,str) for k,v in blueprint['reviews'].items()):
        raise ValueError('Record existing-role capability reviews and limitations first.')
    if not isinstance(blueprint['skills'], list) or not all(isinstance(x,str) for x in blueprint['skills']):
        raise ValueError('skills must be a list of bundled skill IDs.')
    catalog = {p.parent.name: p.parent for p in (ROOT / 'skills').glob('*/SKILL.md')}
    selected = list(dict.fromkeys(blueprint['skills'] + ['cli-anything-universal-bridge']))
    if not set(selected) <= set(catalog):
        raise ValueError('Choose bundled skills only; external programs require separate setup.')
    # Profile creation is a generic planning and productivity feature. Do not attach
    # offensive security or automatic attack workflows to new autonomous profiles.
    if any(x in {'antigravity-webdev-cybersec', 'rea', 'rea-exploit', 'reverse-engineer-anything'} for x in selected):
        raise ValueError('Use a separate defensive code-review workflow for security tasks.')
    try:
        active_rp = light_mod.read_resource_profile(home)
    except (OSError, ValueError):
        active_rp = {'profile': 'normal', 'configured': False}
    low_ram = active_rp.get('profile') == 'light'
    result = {'profile': identifier, 'name': blueprint['name'], 'skills': selected,
              'status': 'PLAN_ONLY', 'provider_model': 'USER_CONFIGURES_IN_HERMES',
              'resource_profile': active_rp.get('profile', 'normal'),
              'low_ram_mode': low_ram,
              'single_active_runtime_advised': low_ram,
              'model_calls': 0, 'gateway_started': False, 'upstream': UPSTREAM}
    if not apply:
        return result
    target = home / 'profiles' / identifier / 'skills'
    soul = (f"# {blueprint['name']}\n\nPurpose: {blueprint['purpose']}\n\n"
            "Work within the agreed user scope, collaborate with existing roles when helpful, "
            "and ask for approval before external sends, paid actions, or irreversible changes. "
            "Use user-selected model/provider settings. Do not copy credentials or private memory.\n")
    with_profile = profiles.sync_hermes_profile(home, identifier, blueprint['name'], soul,
        'Read SOUL.md. Use only the approved skills and native tools for the task.',
        [(catalog[slug], target/slug) for slug in selected], description=blueprint['purpose'])
    result.update(status='CREATED_PENDING_USER_MODEL', profile_receipt=with_profile['receipt'])
    try:
        cache_file = home / 'msshi-runtime' / 'skill-index' / f'{identifier}.json'
        idx = skill_index.scan_profile_skills(target, cache_file, write_cache=True, source=ROOT)
        result['skill_index'] = {'skill_count': idx['skill_count'], 'cache_path': idx['cache_path']}
    except (OSError, ValueError):
        pass
    try:
        staged = trim.install(home, source_root=ROOT, selected=[identifier], apply=True, allow_download=False)
        result['trim'] = {'profiles': staged['profiles'], 'binary': staged['binary']['status'], 'receipt': staged['receipt']}
    except (OSError, ValueError) as exc:
        result['trim'] = {'status': 'NEEDS_REPAIR', 'error_type': type(exc).__name__}
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path)
    parser.add_argument('--roster', action='store_true', help='List IDs and installed skill names only.')
    parser.add_argument('--blueprint', type=Path, help='Preview a JSON design; no profile is created by default.')
    parser.add_argument('--apply', action='store_true', help='Create the approved profile after interactive confirmation.')
    args = parser.parse_args(argv)
    home = profiles.resolve_hermes_home(args.home)
    if args.blueprint:
        design = json.loads(args.blueprint.read_text(encoding='utf-8-sig'))
        print(json.dumps(provision(home, design), ensure_ascii=False, indent=2))
        if args.apply:
            if input('Create this bot without inheriting model or credentials? [y/N] ').strip().lower() not in {'y','yes','ya'}:
                return 1
            print(json.dumps(provision(home, design, apply=True), ensure_ascii=False, indent=2))
    else:
        try:
            rp = light_mod.read_resource_profile(home).get('profile', 'normal')
        except (OSError, ValueError):
            rp = 'normal'
        print(json.dumps({'profiles': roster(home), 'resource_profile': rp, 'low_ram_mode': rp == 'light', 'upstream': UPSTREAM, 'model_calls': 0}, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, EOFError) as exc:
        # Don't echo arbitrary file strings or configuration values in diagnostics.
        print(f'Forge stopped: {type(exc).__name__}. Review the blueprint and profile ID.')
        raise SystemExit(1)
