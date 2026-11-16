"""Pinned, opt-in source/runtime support for contextual MSSHI integrations.

Status and local queries never fetch or call a model. Source caches, dependencies,
and user career data stay outside every skills/ scanner directory.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.request import Request, urlopen

sys.dont_write_bytecode = True
PINNED = {
    'career-ops': ('career-ops-hq/career-ops', 'c687a6f89aa766de468d41402df1ce24bdd86315'),
    'remote-jobs': ('remoteintech/remote-jobs', '155939ad935d22afa8edbaaf0770b99f9d0dbf0d'),
    'mattpocock-skills': ('mattpocock/skills', '5863806dd4e15c63174bee4e7515a4256792ecfa'),
    'rea-video': ('JuneYaooo/rea-video', '820d661e807034e0f0284262b4e93085cfd3da49'),
}
MAX_FILE = 8 * 1024 * 1024
MAX_TOTAL = 64 * 1024 * 1024


def checked(value):
    path = Path(os.path.abspath(Path(value).expanduser()))
    for part in (path, *path.parents):
        if os.path.lexists(part) and (part.is_symlink() or getattr(part.lstat(), 'st_file_attributes', 0) & 0x400):
            raise ValueError(f'Refusing linked source/runtime path: {part}')
    return path


def relative(value):
    if (not isinstance(value, str) or not value or '\\' in value or ':' in value
            or any(part in {'', '.', '..'} for part in value.split('/'))):
        raise ValueError('Unsafe cached source path')
    path = PurePosixPath(value)
    if path.is_absolute():raise ValueError('Unsafe cached source path')
    return Path(*path.parts)


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def atomic(path, value):
    path = checked(path); path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.msshi-', delete=False) as stream:
        stream.write(value); staged = Path(stream.name)
    try:
        os.replace(staged, path)
    finally:
        staged.unlink(missing_ok=True)


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def fetch(url, limit=MAX_FILE):
    with urlopen(Request(url, headers={'User-Agent': 'MSSHI-context-sources'}), timeout=60) as response:
        if not response.url.startswith('https://'):
            raise ValueError('Insecure source redirect')
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError('Source file exceeds size budget')
    return data


def selected_file(name, row):
    path = PurePosixPath(row['path']); parts = path.parts
    if row.get('type') != 'blob' or row.get('mode') not in {'100644', '100755'}:
        return False
    if any(part in {'.git', 'node_modules', '__pycache__', 'evals', '.venv', 'venv'} for part in parts):
        return False
    if row['path'] in {'LICENSE', 'LICENSE.md', 'LICENSE.txt', 'NOTICE', 'README.md', 'AGENTS.md',
                        'DATA_CONTRACT.md', 'package.json', 'package-lock.json', 'pyproject.toml'}:
        return True
    if name == 'remote-jobs':
        return row['path'].startswith('src/companies/') and path.suffix == '.md'
    if name == 'mattpocock-skills':
        return row['path'].startswith('skills/') and path.suffix in {'.md', '.json', '.yaml', '.yml', '.py', '.sh', '.js', '.ts'}
    if name == 'rea-video':
        return (row['path'].startswith(('rea_video/', 'skills/rea-video/'))
                and path.suffix in {'.py', '.md', '.json', '.yaml', '.yml', '.sh'})
    # Preserve the upstream workflow source, scripts, templates and modes. User
    # inputs/output never become part of the public reference checkout.
    if parts[0] in {'data', 'reports', 'output', 'employers', 'docs', 'web', 'dashboard', 'tests', 'batch'}:
        return False
    if row['path'] in {'cv.md', 'portals.yml', 'article-digest.md',
                        'modes/_profile.md', 'modes/_custom.md', 'modes/_brief.md'}:
        return False
    return path.suffix in {'.md', '.mjs', '.cjs', '.js', '.json', '.yml', '.yaml', '.html', '.css', '.tex', '.svg'}


def folder(home, name):
    return checked(home / 'msshi-private' / 'context-sources' / name / PINNED[name][1])


def verify_cached(home, name):
    root = folder(home, name); marker = checked(root / 'MSSHI_SNAPSHOT.json')
    if not marker.is_file():
        return None
    state = read(marker)
    if state.get('repository') != PINNED[name][0] or state.get('commit') != PINNED[name][1]:
        raise ValueError('Source snapshot identity mismatch')
    hashes = state.get('files')
    if not isinstance(hashes, dict) or not hashes or len(hashes) > 3000:
        raise ValueError('Invalid source inventory')
    for name_, digest in hashes.items():
        path = checked(root / relative(name_))
        if not isinstance(digest, str) or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f'Cached source changed: {name}/{name_}')
    return state


def materialize(home, name):
    previous = verify_cached(home, name)
    if previous:
        return folder(home, name)
    repo, pin = PINNED[name]
    tree = json.loads(fetch(f'https://api.github.com/repos/{repo}/git/trees/{pin}?recursive=1'))
    if tree.get('sha') != pin or tree.get('truncated'):
        raise ValueError('Incomplete pinned source tree')
    rows = [row for row in tree['tree'] if selected_file(name, row)]
    if not rows or len(rows) > 3000 or sum(row.get('size', 0) for row in rows) > MAX_TOTAL:
        raise ValueError('Selected source exceeds file/size budget')
    root = folder(home, name)
    def one(row):
        rel = relative(row['path'])
        data = fetch(f'https://raw.githubusercontent.com/{repo}/{pin}/{row["path"]}')
        if hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest() != row['sha']:
            raise ValueError('Upstream Git blob mismatch')
        atomic(root / rel, data)
        return row['path'], hashlib.sha256(data).hexdigest()
    with ThreadPoolExecutor(max_workers=4) as pool:
        hashes = dict(pool.map(one, rows))
    required = ['README.md', 'LICENSE']
    if name == 'career-ops': required += ['AGENTS.md', '.agents/skills/career-ops/SKILL.md', 'package-lock.json']
    if name == 'rea-video': required += ['pyproject.toml', 'skills/rea-video/SKILL.md']
    if any(path not in hashes for path in required):
        raise ValueError('Pinned source is missing a required workflow/license file')
    if name == 'career-ops' and not any(path.startswith('modes/') for path in hashes):
        raise ValueError('CareerOps needs its complete workflow modes')
    atomic(root / 'MSSHI_SNAPSHOT.json', encode({'repository': repo, 'commit': pin, 'files': hashes,
        'dependencies_installed': False, 'model_calls': 0, 'auto_start': False}))
    return root


def status(home, name):
    cached = verify_cached(home, name); root = folder(home, name)
    runtime = checked(home / 'msshi-private' / 'context-runtimes' / name)
    marker = checked(runtime / 'installed.json')
    runtime_state = read(marker) if marker.is_file() else {}
    executable_ready = ((root / 'node_modules/.package-lock.json').is_file() if name == 'career-ops'
                        else (runtime / 'venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')).is_file())
    runtime_ready = cached is not None and runtime_state.get('commit') == PINNED[name][1] and executable_ready
    result = {'name': name, 'repository': PINNED[name][0], 'commit': PINNED[name][1],
              'source_cached': cached is not None, 'source_path': str(root),
              'source_files': len(cached['files']) if cached else 0,
              'runtime_installed': runtime_ready, 'runtime_path': str(runtime),
              'runtime_required': name in {'career-ops', 'rea-video'},
              'auto_start': False, 'model_calls': 0, 'operation_tested': False}
    if name == 'career-ops':
        data = home / 'msshi-private' / 'career-ops-data'
        result.update(data_root=str(data), cv_present=(data / 'cv.md').is_file(),
                      environment={'CAREER_OPS_DATA_DIR': str(data)},
                      prerequisite='Workflow source, Node dependencies, user CV/profile; browser only for requested browser/PDF work')
    elif name == 'rea-video':
        python = runtime / 'venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        result.update(python=str(python), prerequisite='Python runtime and ffmpeg/ffprobe; OCR/ASR/VLM/model downloads are separate opt-ins',
                      local_flags=['--no-vlm','--no-whole','--no-ocr','--no-packaging','--no-asr','--no-speakers','--no-stems','--workers','1','--lang','en'])
    return result


def skills(home, name):
    if not verify_cached(home, name):raise ValueError('Source not cached; explicitly request --fetch first')
    root = folder(home, name); rows = []
    for path in sorted((root / 'skills').glob('**/SKILL.md')):
        text = path.read_text(encoding='utf-8-sig')
        rows.append({'name': path.parent.name, 'path': str(path),
                     'explicit_only': bool(re.search(r'(?m)^disable-model-invocation:\s*true\s*$', text)),
                     'in_progress': 'in-progress' in path.parts})
    return rows


def query_companies(home, query, limit=10):
    if not query.strip():raise ValueError('Provide a nonempty company/directory query')
    if not verify_cached(home, 'remote-jobs'):raise ValueError('Directory not cached; explicitly request --fetch first')
    terms = query.casefold().split(); rows = []
    for path in sorted((folder(home, 'remote-jobs') / 'src/companies').glob('*.md')):
        text = path.read_text(encoding='utf-8-sig')
        if all(term in text.casefold() for term in terms):
            title = re.search(r'(?m)^(?:name|title):\s*["\x27]?(.+?)["\x27]?\s*$', text)
            rows.append({'company': title.group(1) if title else path.stem, 'source': str(path),
                         'excerpt': next((line.strip()[:240] for line in text.splitlines() if query.casefold() in line.casefold()), path.stem),
                         'active_job_verified': False})
            if len(rows) >= limit:break
    return {'query': query, 'results': rows, 'limit': limit, 'note': 'Directory matches, not verified current vacancies. Check the employer career page when requested.'}


def install_runtime(home, name):
    if name not in {'career-ops', 'rea-video'}:
        raise ValueError('This source needs no managed runtime installer')
    root = materialize(home, name)
    runtime = checked(home / 'msshi-private' / 'context-runtimes' / name)
    runtime.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(runtime).free < 1024**3:raise ValueError('At least 1 GiB free disk required for runtime setup')
    # Package tools need OS paths, not the agent's model/browser credentials.
    inherited = {'PATH', 'SYSTEMROOT', 'WINDIR', 'COMSPEC', 'PATHEXT', 'APPDATA',
                 'LOCALAPPDATA', 'USERPROFILE', 'HOMEDRIVE', 'HOMEPATH', 'PROGRAMFILES',
                 'PROGRAMFILES(X86)', 'PROGRAMDATA', 'LANG', 'LC_ALL'}
    env = {key: value for key, value in os.environ.items() if key.upper() in inherited}
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    temp = runtime / 'temp'; temp.mkdir(exist_ok=True)
    env.update(TEMP=str(temp), TMP=str(temp), PIP_CACHE_DIR=str(runtime / 'pip-cache'),
               PIP_DISABLE_PIP_VERSION_CHECK='1', PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD='1',
               npm_config_cache=str(runtime / 'npm-cache'))
    if name == 'career-ops':
        npm = shutil.which('npm.cmd' if os.name == 'nt' else 'npm')
        node = shutil.which('node')
        if not npm or not node:raise ValueError('Node/npm required; install them separately')
        version = subprocess.run([node, '--version'], capture_output=True, text=True, check=True, timeout=15).stdout.strip()
        match = re.fullmatch(r'v?(\d+)\.(\d+)\.(\d+)(?:[-+].*)?', version)
        if not match:raise ValueError('Cannot verify Node version')
        major, minor, _ = map(int, match.groups())
        if not ((major == 22 and minor >= 13) or (major == 23 and minor >= 4) or major >= 24):
            raise ValueError('CareerOps requires Node ^22.13.0 or >=23.4.0')
        # Lifecycle hooks in upstream normally fetch Chromium. Never run them here.
        subprocess.run([npm, 'ci', '--ignore-scripts', '--no-audit', '--no-fund'], cwd=root, env=env, check=True, timeout=900)
        data = home / 'msshi-private' / 'career-ops-data'; data.mkdir(parents=True, exist_ok=True)
        runtime_command = ['node', str(root / 'doctor.mjs')]
    else:
        python = runtime / 'venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        if not python.is_file():subprocess.run([sys.executable, '-m', 'venv', str(runtime / 'venv')], env=env, check=True, timeout=180)
        subprocess.run([str(python), '-m', 'pip', 'install', '--no-input', str(root)], env=env, check=True, timeout=900)
        subprocess.run([str(python), '-m', 'pip', 'check'], env=env, check=True, timeout=90)
        runtime_command = [str(python), '-m', 'rea_video']
    atomic(runtime / 'installed.json', encode({'name': name, 'commit': PINNED[name][1],
        'installed_utc': datetime.now(timezone.utc).isoformat(), 'command': runtime_command,
        'models_downloaded': False, 'browser_downloaded': False, 'operations_tested': False,
        'lifecycle_scripts': False, 'auto_start': False}))
    return status(home, name)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, required=True, help='Hermes root; all caches/runtimes remain under msshi-private.')
    parser.add_argument('--name', choices=tuple(PINNED), required=True)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument('--fetch', action='store_true', help='Explicitly cache reviewed pinned source; no dependency install or execution.')
    actions.add_argument('--install-runtime', action='store_true', help='Explicit dependency setup for CareerOps/rea-video; no model/browser downloads or task runs.')
    actions.add_argument('--list', action='store_true', help='List cached Matt Pocock skill paths and explicit-only flags.')
    actions.add_argument('--skill', help='Read one cached Matt Pocock skill, by exact directory name.')
    actions.add_argument('--query', help='Query the cached remote-company directory without network access.')
    parser.add_argument('--limit', type=int, choices=range(1,51), default=10, metavar='1..50')
    args = parser.parse_args(argv)
    try:
        home = checked(args.home)
        if args.fetch:materialize(home, args.name); result = status(home, args.name)
        elif args.install_runtime:result = install_runtime(home, args.name)
        elif args.list or args.skill:
            if args.name != 'mattpocock-skills':raise ValueError('--list/--skill apply to mattpocock-skills only')
            entries = skills(home, args.name)
            if args.skill:
                selected = next((row for row in entries if row['name'] == args.skill), None)
                if selected is None:raise ValueError('Requested cached skill not found')
                result = {**selected, 'content': Path(selected['path']).read_text(encoding='utf-8-sig')}
            else:result = {'skills': entries}
        elif args.query:
            if args.name != 'remote-jobs':raise ValueError('--query applies to remote-jobs only')
            result = query_companies(home, args.query, args.limit)
        else:result = status(home, args.name)
        print(json.dumps(result, ensure_ascii=False, indent=2));return 0
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        parser.exit(1, f'msshi integrations source: {exc}\n')


if __name__ == '__main__':raise SystemExit(main())
