#!/usr/bin/env python3
"""Read historical web MCP registration; automatic enrollment is retired.

Accounts, OAuth tokens and configuration are preserved. Connect each service
yourself in Hermes when needed. This helper never authenticates, shares a token,
launches a browser, probes a remote server or changes model/provider settings.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path

SERVICES = {
    'gitlab': {'url': 'https://gitlab.com/api/v4/mcp'},
    'tinyfish': {'url': 'https://agent.tinyfish.ai/mcp'},
    'brightdata_public': {'url': ''},
}


def config(data):
    from msshi_runtime import yaml_read
    return yaml_read(data)


def homes(root):
    root = Path(root)
    result = {'default': root}
    profiles = root / 'profiles'
    if profiles.is_dir():
        for folder in sorted(profiles.iterdir()):
            if (folder.is_dir() and not folder.name.startswith('.') and not folder.is_symlink()
                    and not (getattr(folder.lstat(), 'st_file_attributes', 0) & 0x400)
                    and (folder / 'config.yaml').is_file()):
                result[folder.name] = folder
    return result


def status(root):
    output = {}
    for name, home in homes(root).items():
        cfg_file = home / 'config.yaml'
        directory = home / 'mcp-tokens'
        if not cfg_file.is_file():
            output[name] = {
                'credential_directory': str(directory.resolve()),
                'config_present': False,
                'services': {
                    service: {
                        'registered': False, 'enabled': False, 'endpoint_matches': False,
                        'cached_oauth': (directory / f'{service}.json').is_file(),
                        'discovery': 'pending Hermes config.yaml initialization',
                        'authentication': 'not tested by status',
                    } for service in SERVICES
                },
            }
            continue
        c = config(cfg_file.read_bytes())
        output[name] = {'credential_directory': str(directory.resolve()), 'config_present': True, 'services': {}}
        for service in SERVICES:
            item = (c.get('mcp_servers') or {}).get(service)
            output[name]['services'][service] = {
                'registered': bool(item), 'enabled': bool(item and item.get('enabled', True)),
                'endpoint_matches': bool(item and item.get('url') == SERVICES[service]['url']),
                'cached_oauth': (directory/f'{service}.json').is_file(),
                'discovery': 'not tested by status', 'authentication': 'not tested by status',
            }
    return output


def install(root, share_oauth=False):
    return {'status': 'manual_user_setup', 'changed': False,
            'external_services_installed': False, 'credentials_read_or_written': False,
            'oauth_shared': False, 'network_requests': 0,
            'message': 'Automatic service setup is retired. Connect services yourself in Hermes; existing accounts and credentials were preserved.'}


def probe(home, service, source=None, read_test=False):
    return {'status': 'manual_user_setup', 'changed': False, 'service': service,
            'discovered': False, 'authenticated': False, 'network_requests': 0,
            'credentials_read_or_written': False,
            'message': 'Remote probing is retired here. Use the connector controls in Hermes after your own login.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['status', 'install', 'probe'])
    parser.add_argument('--hermes-home', type=Path, default=Path(os.environ.get('HERMES_HOME', '~/.hermes')).expanduser())
    parser.add_argument('--share-oauth', action='store_true', help='Retired no-op; credentials are never shared.')
    parser.add_argument('--service', choices=list(SERVICES), default='tinyfish')
    parser.add_argument('--hermes-source', type=Path, help=argparse.SUPPRESS)
    parser.add_argument('--read-test', action='store_true', help='Retired no-op; no network request is made.')
    args = parser.parse_args(argv)
    try:
        if args.action == 'status':
            result = status(args.hermes_home)
        elif args.action == 'install':
            result = install(args.hermes_home, args.share_oauth)
        else:
            result = probe(args.hermes_home, args.service)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, TypeError) as error:
        print(json.dumps({'error_type': type(error).__name__, 'changed': False,
                          'message': 'Local service status could not be read; no account was accessed.'}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
