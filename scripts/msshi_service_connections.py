#!/usr/bin/env python3
"""Register the two web MCP services without changing model/persona settings.

The optional Windows OAuth junction is an explicit same-user, same-account
workspace choice, not a Hermes credential-inheritance feature. No key is copied
into public source or config. Discovery never starts an interactive OAuth flow.
"""
from __future__ import annotations
import argparse
import copy
import csv
from datetime import datetime, timezone
import hashlib
import io
import importlib.util
import json
import logging
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import urllib.request

SERVICES = {
    'gitlab': {'url': 'https://gitlab.com/api/v4/mcp', 'auth': 'oauth',
               'tools': {'exclude': ['get_mcp_server_version', 'list_duo_sessions']}},
    'tinyfish': {'url': 'https://agent.tinyfish.ai/mcp', 'auth': 'oauth',
                'oauth': {'flow': 'browser', 'timeout': 300},
                'tools': {'include': ['search', 'fetch_content'], 'resources': False, 'prompts': False}},
}
PROFILE_NAMES = ['shizuka-hiratsuka', 'val', 'kiki-chii', 'nyenyenye-ya-gw-coder']
TOKEN_NAME = re.compile(r'^(gitlab|tinyfish)\.(json|client\.json|meta\.json|cimd-off|json\.refresh\.lock)$')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def yaml_api():
    # Same optional-dependency lookup used by the public MSSHI migration helper.
    from msshi_runtime import yaml_module
    return yaml_module()


def config(data):
    value = yaml_api()(typ='safe').load(data.decode('utf-8-sig')) or {}
    if not isinstance(value, dict):
        raise ValueError('config.yaml must be a mapping')
    return value


def homes(root):
    result = {'default': root}
    for name in PROFILE_NAMES:
        home = root/'profiles'/name
        if (home/'config.yaml').is_file():
            result[name] = home
    return result


def is_link(path):
    return path.is_symlink() or (path.exists() and bool(getattr(path.lstat(), 'st_file_attributes', 0) & 0x400))


def direct(path):
    for p in [path, *path.parents]:
        if is_link(p):
            raise ValueError(f'Refusing unmanaged reparse point: {p}')
    return path


def add_missing(data):
    """Surgical insertion: every original config byte is retained unchanged."""
    original = config(data)
    current = original.get('mcp_servers', {}) or {}
    missing = {}
    for name, template in SERVICES.items():
        existing = current.get(name)
        if existing is not None:
            if existing.get('url', '').rstrip('/') != template['url'] or existing.get('auth') != 'oauth':
                raise ValueError(f'Conflicting existing {name} configuration; not overwritten')
            if existing.get('enabled', True) is False:
                raise ValueError(f'{name} explicitly disabled; not overridden')
        else:
            missing[name] = copy.deepcopy(template)
    if not missing:
        return data, []
    newline = b'\r\n' if b'\r\n' in data else b'\n'
    y = yaml_api()()
    stream = io.StringIO()
    y.dump({'mcp_servers': missing}, stream)
    rendered = stream.getvalue().encode('utf-8').splitlines()
    lines = data.splitlines(keepends=True)
    idx = next((i for i, line in enumerate(lines) if re.match(rb'^mcp_servers:\s*(?:#.*)?$', line.rstrip(b'\r\n'))), None)
    if idx is None:
        result = data + (b'' if not data or data.endswith((b'\r', b'\n')) else newline) + newline.join(rendered) + newline
    else:
        end = len(lines)
        for i in range(idx + 1, len(lines)):
            if re.match(rb'^[^\s#][^:]*:', lines[i]):
                end = i
                break
        insertion = newline.join(rendered[1:]) + newline
        prefix = b''.join(lines[:end])
        result = prefix + (b'' if prefix.endswith(b'\n') else newline) + insertion + b''.join(lines[end:])
    expected = copy.deepcopy(original)
    expected.setdefault('mcp_servers', {}).update(missing)
    if config(result) != expected:
        raise ValueError('Insertion changed settings outside the intended missing MCP entries')
    return result, list(missing)


def status(root):
    output = {}
    for name, home in homes(root).items():
        c = config((home/'config.yaml').read_bytes())
        directory = home/'mcp-tokens'
        output[name] = {'credential_directory': str(directory.resolve()), 'services': {}}
        for service in SERVICES:
            item = (c.get('mcp_servers') or {}).get(service)
            output[name]['services'][service] = {
                'registered': bool(item), 'enabled': bool(item and item.get('enabled', True)),
                'endpoint_matches': bool(item and item.get('url') == SERVICES[service]['url']),
                'cached_oauth': (directory/f'{service}.json').is_file(),
                'discovery': 'not tested by status', 'authentication': 'not tested by status',
            }
    return output


def gitlab_identity(directory):
    """Read-only account proof; no token ever appears in a URL, log, or result."""
    token = json.loads((directory/'gitlab.json').read_text(encoding='utf-8-sig'))['access_token']
    request = urllib.request.Request('https://gitlab.com/oauth/token/info', headers={'Authorization': 'Bearer '+token})
    # Never forward Authorization to a redirect target.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None
    with urllib.request.build_opener(NoRedirect).open(request, timeout=20) as response:
        payload = json.load(response)
    return digest(str(payload['resource_owner_id']).encode())


def private_acl(directory):
    """Protect canonical token/backup directories for this Windows user + SYSTEM."""
    output = subprocess.check_output(['whoami', '/user', '/fo', 'csv', '/nh'], text=True)
    sid = next(csv.reader(io.StringIO(output)))[-1]
    result = subprocess.run(['icacls', str(directory), '/inheritance:r', '/grant:r',
                             f'*{sid}:(OI)(CI)F', '*S-1-5-18:(OI)(CI)F', '/Q'],
                            capture_output=True, text=True)
    if result.returncode:
        raise ValueError('Could not secure the private credential directory ACL')
    # Files do not accept inheritable container ACEs. Reset descendants to the
    # restricted parent, rather than applying (OI)(CI) recursively to files.
    for item in directory.iterdir():
        result = subprocess.run(['icacls', str(item), '/reset', '/T', '/Q'],
                                capture_output=True, text=True)
        if result.returncode:
            raise ValueError('Could not inherit the restricted credential directory ACL')


def make_junction(path, target):
    # Literal paths passed as process arguments, never interpolated as shell code.
    script = 'param($Link,$Target); New-Item -ItemType Junction -Path $Link -Target $Target -ErrorAction Stop | Out-Null'
    shell = shutil.which('pwsh') or shutil.which('powershell')
    if not shell:
        raise ValueError('PowerShell is required to create the guarded directory junction')
    result = subprocess.run([shell, '-NoProfile', '-NonInteractive', '-Command', '& { '+script+' }', str(path), str(target)], capture_output=True, text=True)
    if result.returncode or not is_link(path) or path.resolve() != target.resolve():
        raise ValueError('OAuth junction creation or exact-target verification failed')


def rollback(receipt, canonical):
    results = []
    for entry in reversed(receipt['changes']):
        path = Path(entry['config'])
        restored = []
        if path.exists() and digest(path.read_bytes()) == entry['after_sha256']:
            path.write_bytes(Path(entry['config_backup']).read_bytes())
            restored.append('config')
        directory = entry['shared_token_directory']
        if directory:
            directory = Path(directory)
            if is_link(directory) and directory.resolve() == canonical.resolve():
                # rmdir removes only the verified junction, never its contents.
                os.rmdir(directory)
                restored.append('junction removed')
            original = entry['original_token_directory_backup']
            if original and not directory.exists() and not is_link(directory):
                Path(original).rename(directory)
                restored.append('original token cache restored')
        results.append({'profile': entry['profile'], 'restored': restored})
    return results


def install(root, share_oauth=False):
    root = direct(root.absolute())
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S-%fZ')
    backup = root/'msshi-runtime'/'backups'/f'{stamp}-web-services'
    plans = []
    canonical = direct(root/'mcp-tokens')
    identity = None
    if share_oauth:
        if os.name != 'nt':
            raise ValueError('Shared OAuth junctions are currently Windows-only; use per-profile hermes mcp login elsewhere')
        if not canonical.is_dir():
            raise ValueError('Authorize default GitLab/Tinyfish first; no canonical OAuth cache exists')
        identity = gitlab_identity(canonical)
        if any(not TOKEN_NAME.fullmatch(p.name) or not p.is_file() for p in canonical.iterdir()):
            raise ValueError('Canonical OAuth directory has unrelated entries; sharing refused')
    for name, home in homes(root).items():
        direct(home)
        path = direct(home/'config.yaml')
        before = path.read_bytes()
        after, added = add_missing(before)
        token_dir = home/'mcp-tokens'
        shared = name != 'default' and share_oauth
        if shared and is_link(token_dir):
            if token_dir.resolve() != canonical.resolve():
                raise ValueError(f'Unexpected existing credential junction for {name}')
            shared = False
        if shared and token_dir.exists():
            if any(not TOKEN_NAME.fullmatch(p.name) or not p.is_file() for p in token_dir.iterdir()):
                raise ValueError(f'Unrelated credential cache in {name}; not overwritten')
            if (token_dir/'gitlab.json').exists() and gitlab_identity(token_dir) != identity:
                raise ValueError(f'GitLab account conflict for {name}; sharing refused')
            if (token_dir/'tinyfish.json').exists() and (token_dir/'tinyfish.json').read_bytes() != (canonical/'tinyfish.json').read_bytes():
                raise ValueError(f'Independent Tinyfish account in {name}; sharing refused')
        plans.append((name, path, before, after, added, token_dir, shared))
    backup.mkdir(parents=True)
    receipt = {'schema': 1, 'kind': 'web-service-registration', 'root': str(root),
               'created_at': datetime.now(timezone.utc).isoformat(), 'changes': [],
               'shared_oauth_home': str(canonical) if share_oauth else None,
               'same_gitlab_account_verified': bool(identity), 'status': 'applying'}
    if share_oauth:
        private_acl(canonical)
        private_acl(backup)
    try:
        for name, path, before, after, added, token_dir, shared in plans:
            if before == after and not shared:
                continue
            folder = backup/name
            folder.mkdir()
            (folder/'config.yaml').write_bytes(before)
            entry = {'profile': name, 'config': str(path), 'before_sha256': digest(before),
                     'after_sha256': digest(after), 'config_backup': str(folder/'config.yaml'),
                     'added': added, 'shared_token_directory': str(token_dir) if shared else None,
                     'original_token_directory_backup': None}
            receipt['changes'].append(entry)
            if shared:
                if token_dir.exists():
                    moved = folder/'mcp-tokens'
                    token_dir.rename(moved)
                    entry['original_token_directory_backup'] = str(moved)
                make_junction(token_dir, canonical)
            if path.read_bytes() != before:
                raise ValueError('Concurrent configuration edit detected; transaction cancelled')
            if before != after:
                path.write_bytes(after)
        receipt['status'] = 'complete'
    except Exception:
        receipt['rollback'] = rollback(receipt, canonical)
        receipt['status'] = 'failed; automatic guarded rollback attempted'
        raise
    finally:
        (backup/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    return {'receipt': str(backup/'receipt.json'), 'profiles': status(root)}


def probe(home, service, source, read_test=False):
    """Use the installed Hermes transport, with interactive OAuth suppressed."""
    os.environ['HERMES_HOME'] = str(home)
    sys.path.insert(0, str(source))
    from ruamel.yaml import YAML
    from hermes_cli.mcp_config import _probe_single_server
    from tools.mcp_oauth import suppress_interactive_oauth
    c = YAML(typ='safe').load((home/'config.yaml').read_text(encoding='utf-8-sig'))
    s = c.get('mcp_servers', {}).get(service)
    out = {'profile': home.name, 'service': service, 'registered': bool(s),
           'discovered': False, 'authenticated': False, 'read_operation': 'not executed'}
    if not s:
        return out
    try:
        details = {}
        with suppress_interactive_oauth():
            found = _probe_single_server(service, s, connect_timeout=45, details=details)
        out.update(discovered=True, authenticated=True, discovered_tool_names=[x[0] for x in found],
                   initialized=details.get('initialized', False))
        if service == 'gitlab' and read_test:
            gitlab_identity(home/'mcp-tokens')
            out['read_operation'] = 'GET /oauth/token/info succeeded; account ID not emitted'
    except Exception as error:
        # Some transport exceptions include headers/URLs. Only classify the TYPE.
        out['error_type'] = type(error).__name__
        out['next_step'] = f'Run hermes mcp login {service} in this profile if authorization is required; inspect Hermes private logs otherwise'
    return out


def native_probe_python(home):
    root = home.parent.parent if home.parent.name == 'profiles' else home
    candidates = sorted((root/'installs').glob('*/facts.json'), key=lambda p: p.stat().st_mtime, reverse=True)
    for facts in candidates:
        try:
            data = json.loads(facts.read_text(encoding='utf-8-sig'))
            environment = Path(data['packages']['venv']['environment'])
        except (OSError, ValueError, KeyError, TypeError):
            continue
        executable = environment/('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        if executable.is_file():
            return executable
    raise ValueError('No committed Hermes Python environment found')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['status', 'install', 'probe'])
    parser.add_argument('--hermes-home', type=Path, default=Path(os.environ.get('HERMES_HOME', '~/.hermes')).expanduser())
    parser.add_argument('--share-oauth', action='store_true', help='Explicitly share default workspace identity, after account-conflict checks and private backups')
    parser.add_argument('--service', choices=list(SERVICES), default='tinyfish')
    parser.add_argument('--hermes-source', type=Path)
    parser.add_argument('--read-test', action='store_true')
    args = parser.parse_args()
    os.environ['HERMES_HOME'] = str(args.hermes_home)
    logging.basicConfig(level=logging.ERROR)
    try:
        if args.action == 'status':
            result = status(args.hermes_home)
        elif args.action == 'install':
            result = install(args.hermes_home, args.share_oauth)
        else:
            if not args.hermes_source:
                root = args.hermes_home.parent.parent if args.hermes_home.parent.name == 'profiles' else args.hermes_home
                args.hermes_source = root/'hermes-agent'
            if importlib.util.find_spec('mcp') is None:
                executable = native_probe_python(args.hermes_home)
                if os.environ.get('MSSHI_SERVICE_NATIVE_PROBE') or Path(sys.executable).resolve() == executable.resolve():
                    raise ValueError('Native Hermes Python is missing its MCP dependency')
                child_env = dict(os.environ, MSSHI_SERVICE_NATIVE_PROBE='1', PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')
                command = [str(executable), '-B', '-X', 'utf8', str(Path(__file__).resolve()), *sys.argv[1:]]
                return subprocess.run(command, env=child_env, timeout=60).returncode
            result = probe(args.hermes_home, args.service, args.hermes_source, args.read_test)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.action == 'probe' and not (result.get('discovered') and result.get('authenticated')):
            return 2
    except Exception as error:
        print(json.dumps({'error_type': type(error).__name__, 'message': 'Service action failed safely; check configuration, account access, and the private receipt. No credentials printed.'}))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
