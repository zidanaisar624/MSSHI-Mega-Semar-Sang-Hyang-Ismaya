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
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

sys.dont_write_bytecode = True
PINNED = {
    'career-ops': ('career-ops-hq/career-ops', 'c687a6f89aa766de468d41402df1ce24bdd86315'),
    'remote-jobs': ('remoteintech/remote-jobs', '155939ad935d22afa8edbaaf0770b99f9d0dbf0d'),
    'mattpocock-skills': ('mattpocock/skills', '5863806dd4e15c63174bee4e7515a4256792ecfa'),
    'rea-video': ('JuneYaooo/rea-video', '820d661e807034e0f0284262b4e93085cfd3da49'),
    'grim-prompter': ('jmanico/grim-prompter', '2a94457c7bc63ffbc4a44ea50ae645ab8cee26bf'),
    'claude-bughunter': ('elementalsouls/Claude-BugHunter', '0e70a021e59d6875004e7a563f8511aca2ba3bc1'),
    'ossu-computer-science': ('ossu/computer-science', '8f8272b1d378d31494240aa1d667aa6b045c6552'),
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
    if path.stat().st_size > MAX_FILE:
        raise ValueError('Source/runtime metadata exceeds size budget')
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
    if name == 'grim-prompter':
        return (row['path'] in {'MODELS.md', 'runbook.md', 'start-here.md', 'catalog.md'}
                or (row['path'].startswith(('skills/threat-model/', 'helpers/', 'methods/', 'quick/', 'deep/', 'privacy/', 'reference/'))
                    and path.suffix == '.md'))
    if name == 'claude-bughunter':
        return (row['path'] in {'LICENSE-CONTENT', 'SECURITY.md', 'USAGE.md', 'ENGAGEMENTS.md', 'INSTALL.md', 'CHANGELOG.md', 'cbh/data/skill_index.json'}
                or (row['path'].startswith(('skills/', 'commands/', 'docs/')) and path.suffix == '.md'))
    if name == 'ossu-computer-science':
        return (row['path'] in {'CURRICULAR_GUIDELINES.md', 'FAQ.md', 'HELP.md', 'CONTRIBUTING.md', 'CHANGELOG.md'}
                or (row['path'].startswith(('coursepages/', 'extras/')) and path.suffix == '.md'))
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


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        while chunk := fh.read(65536):
            h.update(chunk)
    return h.hexdigest()


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
        if (not isinstance(digest, str) or path.stat().st_size > MAX_FILE
                or _sha256_file(path) != digest):
            raise ValueError(f'Cached source changed: {name}/{name_}')
    return state


def _required_files(name):
    required = ['README.md', 'LICENSE']
    if name == 'career-ops':
        required += ['AGENTS.md', '.agents/skills/career-ops/SKILL.md', 'package.json',
                     'modes/_shared.md', 'modes/_writing.md']
    if name == 'rea-video':
        required += ['pyproject.toml', 'skills/rea-video/SKILL.md']
    if name == 'grim-prompter':
        required += ['runbook.md', 'catalog.md', 'skills/threat-model/SKILL.md']
    if name == 'claude-bughunter':
        required += ['LICENSE-CONTENT', 'NOTICE', 'SECURITY.md', 'cbh/data/skill_index.json']
    if name == 'ossu-computer-science':
        required += ['CURRICULAR_GUIDELINES.md', 'FAQ.md']
    return required


def _materialize_via_git(home, name, required):
    """Fallback when api.github.com hits rate limit or raw.githubusercontent.com stalls.

    Clones a bare shallow repository at the reviewed commit, verifies Git blob SHA-1,
    enforces the same path/size/partial-cache guards, and writes MSSHI_SNAPSHOT.json.
    """
    repo, pin = PINNED[name]
    root = folder(home, name)
    with tempfile.TemporaryDirectory(prefix='msshi-git-src-') as tmp:
        clone_dir = Path(tmp) / 'repo'
        subprocess.run(
            ['git', '-c', 'http.postBuffer=16m', '-c', 'pack.windowMemory=32m', '-c', 'pack.threads=1',
             'clone', '--bare', '--depth=1', f'https://github.com/{repo}.git', str(clone_dir)],
            check=True, capture_output=True, timeout=180,
        )
        probe = subprocess.run(['git', '-C', str(clone_dir), 'cat-file', '-e', f'{pin}^{{commit}}'],
                               capture_output=True, timeout=30)
        if probe.returncode != 0:
            subprocess.run(
                ['git', '-C', str(clone_dir), '-c', 'http.postBuffer=16m', '-c', 'pack.windowMemory=32m',
                 '-c', 'pack.threads=1', 'fetch', '--depth=1', 'origin', pin],
                check=True, capture_output=True, timeout=180,
            )
        ls = subprocess.run(['git', '-C', str(clone_dir), 'ls-tree', '-r', '-l', '-z', pin],
                            check=True, capture_output=True, timeout=60)
        rows = []
        for entry in ls.stdout.split(b'\x00'):
            if not entry:
                continue
            meta, path_b = entry.split(b'\t', 1)
            parts = meta.decode('ascii').split()
            if len(parts) < 4:
                continue
            mode, typ, sha, size_raw = parts[0], parts[1], parts[2], parts[3]
            size = int(size_raw) if size_raw.isdigit() else 0
            row = {'mode': mode, 'type': typ, 'sha': sha, 'size': size, 'path': path_b.decode('utf-8')}
            if selected_file(name, row):
                rows.append(row)
        if not rows or len(rows) > 3000 or sum(r.get('size', 0) for r in rows) > MAX_TOTAL:
            raise ValueError('Selected source exceeds file/size budget')
        selected_paths = {r['path'] for r in rows}
        missing = [p for p in required if p not in selected_paths]
        if missing:
            raise ValueError('Pinned source is missing required workflow/license files: ' + ', '.join(missing))
        hashes = {}
        for row in rows:
            rel = relative(row['path'])
            target = checked(root / rel)
            if target.is_file():
                if target.stat().st_size > MAX_FILE:
                    raise ValueError(f'Partial cached source exceeds size budget: {name}/{row["path"]}')
                data = target.read_bytes()
                if hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest() != row['sha']:
                    raise ValueError(f'Partial cached source differs from reviewed pin; preserve and review it: {name}/{row["path"]}')
                hashes[row['path']] = hashlib.sha256(data).hexdigest()
                continue
            blob = subprocess.run(['git', '-C', str(clone_dir), 'cat-file', 'blob', row['sha']],
                                  check=True, capture_output=True, timeout=60)
            data = blob.stdout
            if len(data) > MAX_FILE:
                raise ValueError('Source file exceeds size budget')
            if hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest() != row['sha']:
                raise ValueError('Upstream Git blob mismatch')
            atomic(target, data)
            hashes[row['path']] = hashlib.sha256(data).hexdigest()
    if any(p not in hashes for p in required):
        raise ValueError('Pinned source is missing a required workflow/license file')
    if name == 'career-ops' and not any(p.startswith('modes/') for p in hashes):
        raise ValueError('CareerOps needs its complete workflow modes')
    atomic(root / 'MSSHI_SNAPSHOT.json', encode({'repository': repo, 'commit': pin, 'files': hashes,
        'dependencies_installed': False, 'model_calls': 0, 'auto_start': False}))
    return root


def materialize(home, name):
    previous = verify_cached(home, name)
    if previous:
        return folder(home, name)
    repo, pin = PINNED[name]
    required = _required_files(name)
    try:
        tree = json.loads(fetch(f'https://api.github.com/repos/{repo}/git/trees/{pin}?recursive=1'))
    except (HTTPError, URLError, TimeoutError):
        return _materialize_via_git(home, name, required)
    if tree.get('sha') != pin or tree.get('truncated'):
        raise ValueError('Incomplete pinned source tree')
    rows = [row for row in tree['tree'] if selected_file(name, row)]
    if not rows or len(rows) > 3000 or sum(row.get('size', 0) for row in rows) > MAX_TOTAL:
        raise ValueError('Selected source exceeds file/size budget')
    # CareerOps deliberately has no root npm lock at this reviewed pin. The
    # web/package-lock.json belongs to a separate web project, not this CLI.
    selected_paths = {row['path'] for row in rows}
    missing = [path for path in required if path not in selected_paths]
    if missing:
        raise ValueError('Pinned source is missing required workflow/license files: ' + ', '.join(missing))
    root = folder(home, name)
    def one(row):
        rel = relative(row['path'])
        target = checked(root / rel)
        if target.is_file():
            if target.stat().st_size > MAX_FILE:
                raise ValueError(f'Partial cached source exceeds size budget: {name}/{row["path"]}')
            data = target.read_bytes()
            if hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest() != row['sha']:
                raise ValueError(f'Partial cached source differs from reviewed pin; preserve and review it: {name}/{row["path"]}')
            return row['path'], hashlib.sha256(data).hexdigest()
        data = fetch(f'https://raw.githubusercontent.com/{repo}/{pin}/{row["path"]}')
        if hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest() != row['sha']:
            raise ValueError('Upstream Git blob mismatch')
        atomic(target, data)
        return row['path'], hashlib.sha256(data).hexdigest()
    try:
        with ThreadPoolExecutor(max_workers=4) as pool:
            hashes = dict(pool.map(one, rows))
    except (HTTPError, URLError, TimeoutError):
        return _materialize_via_git(home, name, required)
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
    lock_path = checked(root / 'package-lock.json')
    lock_verified = (lock_path.is_file() and lock_path.stat().st_size <= MAX_FILE and bool(runtime_state.get('dependency_lock_sha256'))
                     and hashlib.sha256(lock_path.read_bytes()).hexdigest() == runtime_state['dependency_lock_sha256']) if name == 'career-ops' else True
    runtime_ready = cached is not None and runtime_state.get('commit') == PINNED[name][1] and executable_ready and lock_verified
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
                      dependency_lock_verified=bool(lock_verified),
                      dependency_lock_origin=runtime_state.get('dependency_lock_origin'),
                      prerequisite='Workflow source, Node dependencies, user CV/profile; root dependency lock is generated locally on explicit runtime setup; browser only for requested browser/PDF work')
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
    install_metadata = {}
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
        # The pinned CLI has package.json but no root package-lock.json. Generate
        # a local resolution only on this explicit runtime action, then use ci.
        # This resolution is not represented as an upstream-supplied lock/pin.
        lock = checked(root / 'package-lock.json')
        if not lock.is_file():
            subprocess.run([npm, 'install', '--package-lock-only', '--ignore-scripts', '--no-audit', '--no-fund'],
                           cwd=root, env=env, check=True, timeout=900)
        if not lock.is_file() or lock.stat().st_size > MAX_FILE:
            raise ValueError('CareerOps local dependency lock was not generated within size budget')
        lock_data = read(lock)
        package_data = read(root / 'package.json')
        packages = lock_data.get('packages', {}) if isinstance(lock_data, dict) else {}
        root_package = packages.get('', {}) if isinstance(packages, dict) else {}
        if (not isinstance(lock_data, dict) or not isinstance(root_package, dict)
                or lock_data.get('lockfileVersion') not in {2, 3}
                or root_package.get('name') != package_data.get('name')
                or root_package.get('dependencies', {}) != package_data.get('dependencies', {})):
            raise ValueError('CareerOps local dependency lock does not match the reviewed package manifest')
        lock_hash = hashlib.sha256(lock.read_bytes()).hexdigest()
        if marker_state := ((runtime / 'installed.json') if (runtime / 'installed.json').is_file() else None):
            previous_hash = read(marker_state).get('dependency_lock_sha256')
            if previous_hash and previous_hash != lock_hash:
                raise ValueError('CareerOps dependency lock changed after setup; preserve and review it before reinstalling')
        # Lifecycle hooks normally fetch Chromium. Never run them here.
        subprocess.run([npm, 'ci', '--ignore-scripts', '--no-audit', '--no-fund'], cwd=root, env=env, check=True, timeout=900)
        if hashlib.sha256(lock.read_bytes()).hexdigest() != lock_hash:
            raise ValueError('CareerOps dependency lock changed during installation')
        install_metadata = {'dependency_lock_sha256': lock_hash,
                            'dependency_lock_origin': 'generated-local-resolution',
                            'upstream_root_lockfile': False}
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
        'lifecycle_scripts': False, 'auto_start': False, **install_metadata}))
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
            if args.name not in {'mattpocock-skills', 'claude-bughunter'}:raise ValueError('--list/--skill apply to mattpocock-skills or claude-bughunter only')
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
