"""Model-independent Academic presets and local, ordinary project templates."""
from __future__ import annotations

import json
import os
from pathlib import Path

import msshi_hermes_profiles as hp

MODES = ('academic-mahasiswa', 'academic-dosen')
ALIAS = 'academic-mahasiswa-dosen'
MARKER = Path('msshi-runtime/active-preset.json')
PROFILE_FIELDS = ('academic_level', 'academic_topic', 'academic_deadline',
                  'academic_campus_guideline', 'preferred_name')


def is_academic(mode):
    return mode in (*MODES, ALIAS)


def canonical(mode):
    return 'academic-mahasiswa' if mode == ALIAS else mode


def existing_mode(hermes_home, state=None):
    root = hp.normalize_hermes_root(hermes_home)
    for candidate in (root / MARKER, root / 'msshi-runtime/pending-bots.json'):
        if candidate.is_file() and not candidate.is_symlink() and candidate.stat().st_size <= 262144:
            try:
                value = json.loads(candidate.read_text(encoding='utf-8-sig'))
                mode = value.get('preset') or value.get('mode')
                if mode in (*MODES, 'muza-preset', 'solo', 'selective', 'custom-bots'):
                    return mode
            except (OSError, ValueError, AttributeError):
                pass
    mode = (state or {}).get('setup_mode')
    if mode in (*MODES, 'muza-preset', 'solo', 'selective', 'custom-bots'):
        return mode
    if any((root / 'profiles' / name).is_dir() for name in hp.TEAM_ROLE_IDS):
        return 'muza-preset'
    return None


def preset_matrix(data, mode, source):
    mode = canonical(mode)
    if mode not in MODES:
        return data
    definition = json.loads((source / 'configs/academic_presets.json').read_text(encoding='utf-8-sig'))['presets'][mode]
    old = {bot['id']: bot for bot in data['bots']}
    labels = {'yukino': 'Yukino Yukinoshita', 'shizuka': 'Sensei Shizuka Hiratsuka',
              'val': 'Val', 'kiki-chii': 'Kiki-Chii', 'shikaku': 'Sir. Robot'}
    bots = [{**old[role], 'label': labels[role], 'required_skills': definition['roles'][role],
             'optional_skills': [], 'persona_file': definition['persona_files'][role],
             'role': definition['description']} for role in hp.TEAM_ROLE_IDS]
    return {**data, 'preset': mode, 'bots': bots}


def record_active(root, mode, source, transaction=None):
    """Only called after an explicitly accepted setup; never changes model/provider."""
    root = Path(root)
    files = {root / MARKER: {'schema': 1, 'preset': mode}}
    if mode in MODES:
        policy = json.loads((source / 'configs/academic_app_policy.json').read_text(encoding='utf-8-sig'))
        files[root / 'msshi-runtime/academic-app-policy.json'] = policy
    for path, value in files.items():
        data = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        if transaction is not None:
            transaction.write(path, data, 0o600)
        elif not path.is_file() or path.read_bytes() != data:
            hp._atomic_write_bytes(hp._confined(root, path), data, 0o600)


def project_path(root, explicit=None):
    """Keep Academic work inside native Hermes home; never adopt a personal vault."""
    root = hp.normalize_hermes_root(Path(root)).absolute()
    if explicit:
        candidate = Path(explicit).expanduser().absolute()
        if not candidate.is_relative_to(root / 'workspace'):
            raise ValueError('Workspace Academic harus berada di dalam folder workspace Hermes.')
        return candidate
    return root / 'workspace/academic'


def setup_profile(args, mode, prompt=None):
    values = {field: str(getattr(args, field, '') or '').strip() for field in PROFILE_FIELDS}
    if prompt is not None:
        print('\nProfil akademik opsional — boleh dilewati, tanpa password/API key:')
        prompts = {'academic_level': 'Jenjang (S1/S2/S3)', 'academic_topic': 'Topik/bidang yang sedang dikerjakan',
                   'academic_deadline': 'Target selesai/tenggat', 'academic_campus_guideline': 'Pedoman kampus (judul/lokasi file, bukan isi pribadi)',
                   'preferred_name': 'Ingin dipanggil apa? (ejaan/nama singkatan pilihan Anda)'}
        for field, text in prompts.items():
            if not values[field]:
                values[field] = prompt(text + ' [Enter=lewati]: ', '')
    for field, value in values.items():
        if len(value) > 1000 or any(ord(char) < 32 for char in value):
            raise ValueError('Isian profil harus satu baris pendek: ' + field)
    if values['academic_level'] and values['academic_level'].upper() not in {'S1', 'S2', 'S3'}:
        raise ValueError('Jenjang akademik harus S1, S2 atau S3; boleh dikosongkan.')
    values['academic_level'] = values['academic_level'].upper()
    return values


def install_project(root, mode, source, values=None, explicit=None):
    """Create ordinary templates, not an Obsidian vault, accounts or access rules."""
    from install_msshi import reject_links
    destination = project_path(root, explicit)
    reject_links(destination)
    source_folder = source / 'templates/academic'
    if not source_folder.is_dir():
        raise ValueError('Template Academic tidak ditemukan dalam paket.')
    created, preserved = [], []
    for source_file in source_folder.rglob('*.md'):
        relative = source_file.relative_to(source_folder)
        # Profile/status live at project root, reusable templates under _Templates.
        target = destination / relative if relative.name.startswith(('00_', '01_STATUS_')) else destination / '_Templates' / relative
        reject_links(target)
        if target.exists():
            preserved.append(str(target)); continue
        content = source_file.read_text(encoding='utf-8')
        if relative.name == '00_PROFIL_AKADEMIK_PENGGUNA.md':
            labels = {'preferred_name': 'Nama/sapaan pilihan (ejaan persis)',
                      'academic_level': 'Jenjang terkait', 'academic_topic': 'Bidang/topik',
                      'academic_deadline': 'Tenggat dan target yang dapat ditinjau',
                      'academic_campus_guideline': 'Pedoman kampus/format yang digunakan'}
            for field, label in labels.items():
                value = (values or {}).get(field, '')
                if value:
                    lines = content.splitlines()
                    content = '\n'.join('- ' + label + ': ' + value if line.startswith('- ' + label + ':') else line for line in lines) + '\n'
            content = content.replace('- Peran: mahasiswa / dosen / pimpinan kampus / lainnya',
                                      '- Peran: ' + ('mahasiswa' if mode == 'academic-mahasiswa' else 'dosen / pimpinan kampus'))
        hp._atomic_write_bytes(target, content.encode('utf-8'), 0o600)
        created.append(str(target))
    for role in hp.TEAM_ROLE_IDS:
        folder = destination / 'workspace' / role
        reject_links(folder)
        folder.mkdir(parents=True, exist_ok=True)
    data = {'schema': 1, 'preset': mode, 'project': str(destination), 'profile': values or {},
            'obsidian_installed_or_configured': False, 'accounts_configured': False,
            'private_folder_access_granted': False, 'model_provider_changed': False}
    for target in (destination / '.msshi-academic-project.json', Path(root) / 'msshi-runtime/academic-profile.json'):
        reject_links(target)
        if not target.exists():
            hp._atomic_write_bytes(target, (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode(), 0o600)
            created.append(str(target))
        else:
            preserved.append(str(target))
    return {'project': str(destination), 'created': created, 'preserved': preserved,
            'obsidian_configured': False, 'model_provider_changed': False}


def add_arguments(parser):
    parser.add_argument('--academic-project', type=Path, help='Subfolder workspace Hermes untuk catatan Academic; tidak memasang Obsidian atau membaca vault pribadi.')
    parser.add_argument('--academic-level', default='', help='Profil opsional: S1, S2 atau S3.')
    parser.add_argument('--academic-topic', default='', help='Bidang/topik akademik singkat; disimpan lokal saja.')
    parser.add_argument('--academic-deadline', default='', help='Tenggat/target selesai opsional.')
    parser.add_argument('--academic-campus-guideline', default='', help='Judul/lokasi pedoman kampus; file tidak dibaca saat setup.')
    parser.add_argument('--preferred-name', default='', help='Nama panggilan pilihan pengguna; tidak otomatis dipanggil MuZA.')
