"""Optional Coder-only KAT endpoint setup. Metadata probes never generate tokens."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import getpass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

sys.dont_write_bytecode = True
MODEL = 'Kwaipilot/KAT-Coder-V2.5-Dev'
ENV_NAME = 'MSSHI_KAT_API_KEY'
PRESETS = {
    'exact-dev': {'model': MODEL, 'base_url': None, 'source_variant': 'dev',
        'source': 'https://huggingface.co/Kwaipilot/KAT-Coder-V2.5-Dev',
        'note': 'Exact open-weight Dev. Supply a server that actually serves it; no public endpoint is implied.'},
    'streamlake-payg': {'model': 'kat-coder-pro-v2.5',
        'base_url': 'https://vanchin.streamlake.ai/api/gateway/v1/endpoints',
        'source_variant': 'pro-2.5', 'documented_models': ['kat-coder-pro-v2.5'],
        'source': 'https://www.streamlake.ai/document/DOC/mg6k6nlp8j6qxicx4c9',
        'note': 'Official pay-as-you-go Pro v2.5, a different variant from open-weight Dev. Needs a StreamLake key and account billing.'},
    'custom': {'model': MODEL, 'base_url': None, 'source_variant': 'dev',
        'source': 'user-selected OpenAI-compatible deployment',
        'note': 'Explicit custom deployment. Model must be present in its metadata catalog.'},
}


def checked(value):
    path = Path(os.path.abspath(Path(value).expanduser()))
    for item in (path, *path.parents):
        if os.path.lexists(item) and (item.is_symlink() or getattr(item.lstat(), 'st_file_attributes', 0) & 0x400):
            raise ValueError('Refusing linked Coder configuration path')
    return path


def root_home(value):
    path = checked(value)
    return path.parent.parent if path.parent.name == 'profiles' else path


def state_path(home):
    return home / 'msshi-private/coder/kat.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def atomic(path, data):
    path = checked(path); path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.msshi-kat-', delete=False) as handle:
        temp = Path(handle.name); handle.write(data)
    try:
        os.replace(temp, path)
    finally:
        if temp.exists(): temp.unlink()


def encode(data):
    return (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def env_values(path):
    if not path.is_file(): return {}
    checked(path)
    result = {}
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        match = re.match(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$', line)
        if match:
            value = match[2]
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}: value = value[1:-1]
            result[match[1]] = value
    return result


def key_for(home, name):
    if not re.fullmatch(r'[A-Z_][A-Z0-9_]{1,95}', name or ''):
        raise ValueError('API key reference must be an environment variable name')
    return (env_values(home / 'profiles/shikaku/.env').get(name)
            or os.environ.get(name) or env_values(home / '.env').get(name) or '')


def endpoint(value):
    if not value: return None
    value = value.strip().rstrip('/')
    parsed = urlparse(value)
    local = parsed.hostname in {'127.0.0.1', 'localhost', '::1'}
    if (parsed.scheme not in ({'http', 'https'} if local else {'https'}) or not parsed.hostname
            or parsed.username or parsed.password or parsed.query or parsed.fragment):
        raise ValueError('Use HTTPS without embedded credentials/query; HTTP is allowed only for localhost')
    return value


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs): return None


def model_catalog(base_url, key=''):
    """GET metadata only. No redirect, POST, chat/completions, or fallback model."""
    url = endpoint(base_url) + '/models'
    headers = {'User-Agent': 'MSSHI KAT metadata check', 'Accept': 'application/json'}
    if key: headers['Authorization'] = 'Bearer ' + key
    try:
        with build_opener(NoRedirect()).open(Request(url, headers=headers, method='GET'), timeout=20) as response:
            payload = response.read(16*1024*1024 + 1)
        if len(payload) > 16*1024*1024: raise ValueError('Model catalog exceeds limit')
        data = json.loads(payload.decode('utf-8-sig'))
        models = data.get('data', [])
        if not isinstance(models, list): raise ValueError('Invalid model catalog')
        ids = [row['id'] for row in models if isinstance(row, dict) and isinstance(row.get('id'), str)
               and re.fullmatch(r'[A-Za-z0-9_.:/@+\-]{1,200}', row['id'])]
        return {'ok': True, 'ids': ids, 'kind': 'GET /models', 'inference_calls': 0}
    except HTTPError as error:
        return {'ok': False, 'ids': [], 'http_status': error.code, 'inference_calls': 0}
    except (OSError, ValueError) as error:
        return {'ok': False, 'ids': [], 'error': type(error).__name__, 'inference_calls': 0}


def routing_ready(home):
    """Feature detection only; never imports a provider or starts an agent."""
    config = home / 'profiles/shikaku/config.yaml'
    plugin = home / 'profiles/shikaku/plugins/msshi-team-routing/plugin.yaml'
    if not config.is_file() or not plugin.is_file(): return False
    from msshi_hermes_profiles import load_yaml_mapping
    data = load_yaml_mapping(config)
    backend = str((data.get('delegation') or {}).get('backend') or '')
    return backend in {'msshi-team-routing', 'msshi-team'}


def goose_status(home):
    """Find the separately installed agent; never start/configure it during status."""
    binary = shutil.which('goose')
    receipt = home / 'msshi-private/coder/goose/installation.json'
    version = None
    if not binary and receipt.is_file():
        checked(receipt)
        data = read(receipt)
        candidate = checked(Path(data.get('binary', '')))
        if candidate.is_relative_to(receipt.parent) and candidate.is_file():
            binary, version = str(candidate), data.get('version')
    return {'cli_available': bool(binary), 'binary': binary, 'version': version,
            'kind': 'external agent, not a model ID', 'auto_start': False,
            'inference_tested': False, 'provider_configuration': 'separate explicit setup'}


def status(home):
    path = state_path(home)
    data = read(path) if path.is_file() else {'schema': 1, 'enabled': False, 'status': 'not_configured', 'profile': 'shikaku'}
    public_fields = {'schema', 'enabled', 'status', 'profile', 'preset', 'source_variant',
                     'requested_model', 'model', 'provider', 'base_url', 'api_key_env',
                     'validated_model_catalog', 'catalog_evidence', 'credential_status',
                     'source', 'variant_note', 'auto_open_on_boot', 'max_concurrent',
                     'inference_tested', 'updated_utc'}
    safe = {key: value for key, value in data.items() if key in public_fields}
    name = data.get('api_key_env', ENV_NAME)
    safe.update(api_key_present=bool(key_for(home, name)), routing_ready=routing_ready(home),
                auto_open_on_boot=False, main_model_changed=False, inference_tested=False,
                goose=goose_status(home))
    safe['ready_for_requested_task'] = bool(data.get('enabled') and safe['api_key_present'] and safe['routing_ready']
        and data.get('model') in data.get('validated_model_catalog', []))
    return safe


def configure(home, *, preset='exact-dev', base_url=None, model=None, api_key_env=ENV_NAME,
              probe=False, activate=False, read_key=False, accept_documented_model=False):
    profile = home / 'profiles/shikaku'
    if not (profile / 'config.yaml').is_file():
        raise ValueError('Set up the named Coder profile shikaku first')
    selected = PRESETS[preset]
    base_url = endpoint(base_url or selected.get('base_url'))
    model = (model or selected['model']).strip()
    if not re.fullmatch(r'[A-Za-z0-9_.:/@+\-]{1,200}', model): raise ValueError('Invalid KAT model ID')
    if not re.fullmatch(r'[A-Z_][A-Z0-9_]{1,95}', api_key_env): raise ValueError('Invalid key environment variable name')
    if read_key:
        if not sys.stdin.isatty(): raise ValueError('Secret input requires an interactive terminal')
        secret = getpass.getpass('KAT API key (hidden; do not paste it in chat): ').strip()
        if not secret or any(char in secret for char in '\r\n\"\x27'): raise ValueError('Invalid secret input')
        env_file = checked(profile / '.env')
        old = env_file.read_bytes() if env_file.exists() else b''
        text = old.decode('utf-8-sig')
        pattern = re.compile(r'^\s*' + re.escape(api_key_env) + r'\s*=.*$', re.M)
        replacement = api_key_env + '="' + secret + '"'
        updated = pattern.sub(lambda _: replacement, text) if pattern.search(text) else text.rstrip() + '\n' + replacement + '\n'
        if old:
            backup = home / 'msshi-private/coder/backups' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.env.bak')
            atomic(backup, old)
        atomic(env_file, updated.encode('utf-8-sig' if old.startswith(b'\xef\xbb\xbf') else 'utf-8'))
    key = key_for(home, api_key_env)
    evidence = model_catalog(base_url, key) if probe and base_url else {'ok': False, 'ids': [], 'inference_calls': 0}
    validated = [model] if evidence.get('ok') and model in evidence['ids'] else []
    evidence_kind = 'authenticated_metadata' if evidence.get('ok') and key else 'metadata' if evidence.get('ok') else 'not_verified'
    if (accept_documented_model and preset == 'streamlake-payg' and base_url == selected['base_url']
            and model in selected.get('documented_models', [])):
        validated = [model]
        evidence_kind = 'official_documentation_explicitly_accepted'
    reason = ('needs_endpoint' if not base_url else 'needs_api_key' if not key else
              'needs_model_catalog' if model not in validated else 'needs_native_team_routing' if not routing_ready(home) else
              'configured_not_inference_tested' if activate else 'prepared_not_enabled')
    enabled = bool(activate and reason == 'configured_not_inference_tested')
    data = {'schema': 1, 'profile': 'shikaku', 'preset': preset, 'source_variant': selected['source_variant'],
            'requested_model': MODEL, 'model': model, 'provider': 'custom', 'base_url': base_url,
            'api_key_env': api_key_env, 'enabled': enabled, 'status': reason,
            'validated_model_catalog': validated, 'catalog_evidence': evidence_kind,
            'credential_status': 'present_not_inference_tested' if key else 'missing',
            'source': selected['source'], 'variant_note': selected['note'],
            'auto_open_on_boot': False, 'max_concurrent': 1, 'inference_tested': False,
            'updated_utc': datetime.now(timezone.utc).isoformat()}
    current = state_path(home)
    if current.exists():
        backup = current.parent / 'backups' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json')
        atomic(backup, current.read_bytes())
    atomic(current, encode(data))
    return status(home)


def wizard(home, mode='cloud'):
    if mode == 'skip':
        data = status(home);data.update(enabled=False, status='disabled_by_user')
        atomic(state_path(home), encode({k:v for k,v in data.items() if k not in {'api_key_present','ready_for_requested_task','goose','routing_ready'}}))
        return status(home)
    if not sys.stdin.isatty(): return configure(home)
    print('KAT is optional for Coder only; primary and existing sub-agent models stay unchanged.')
    print('1. Exact Dev: your OpenAI-compatible deployment URL (no hosted URL is bundled).')
    print('2. Official StreamLake Pro v2.5 API: different variant; needs its own key/billing.')
    print('3. Skip and preserve the current KAT state.')
    choice = input('KAT endpoint [3]: ').strip() or '3'
    if choice == '3': return status(home)
    if choice not in {'1','2'}: raise ValueError('Choose 1, 2 or 3')
    preset = 'exact-dev' if choice == '1' else 'streamlake-payg'
    selected = PRESETS[preset]
    base = input('Deployment base URL: ').strip() if choice == '1' else selected['base_url']
    model = input(f'Model ID [{selected["model"]}]: ').strip() or selected['model']
    have_key = bool(key_for(home, ENV_NAME))
    read_secret = not have_key and (input('Enter the KAT key privately now? [y/N]: ').strip().lower() in {'y','yes','ya'})
    return configure(home, preset=preset, base_url=base, model=model, probe=True, activate=True,
                     read_key=read_secret, accept_documented_model=choice == '2')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', '--hermes-home', dest='home', type=Path,
                        default=Path(os.environ.get('HERMES_HOME') or Path.home()/'.hermes'))
    parser.add_argument('--mode', choices=('status','skip','cloud','light','ideal'), help='Legacy KAT mode; selected setup performs the endpoint wizard.')
    sub = parser.add_subparsers(dest='action')
    sub.add_parser('status', help='Read optional Coder KAT/Goose readiness without an API call.')
    sub.add_parser('presets', help='Show verified endpoint choices and model variant differences.')
    sub.add_parser('wizard', help='Configure the optional Coder endpoint and hidden credential input.')
    sub.add_parser('disable', help='Disable only KAT routing; keep primary models and saved settings.')
    conf = sub.add_parser('configure', help='Prepare or activate KAT with explicit endpoint credentials and catalog evidence.')
    conf.add_argument('--preset', choices=tuple(PRESETS), default='exact-dev')
    conf.add_argument('--base-url')
    conf.add_argument('--model')
    conf.add_argument('--api-key-env', default=ENV_NAME)
    conf.add_argument('--read-key', action='store_true', help='Read the key from a hidden interactive prompt, never a CLI argument.')
    conf.add_argument('--probe', action='store_true', help='GET /models only; no inference request.')
    conf.add_argument('--activate', action='store_true', help='Enable only if model evidence, key and native routing are ready.')
    conf.add_argument('--accept-documented-model', action='store_true', help='Use the exact official StreamLake preset model ID from its documentation.')
    args = parser.parse_args(argv)
    try:
        home = root_home(args.home)
        if args.mode: result = status(home) if args.mode == 'status' else wizard(home, args.mode)
        elif args.action in {None,'status'}: result = status(home)
        elif args.action == 'presets': result = {'presets': PRESETS, 'primary_models_changed': False}
        elif args.action == 'wizard': result = wizard(home)
        elif args.action == 'disable': result = wizard(home, 'skip')
        else:
            result = configure(home, preset=args.preset, base_url=args.base_url, model=args.model,
                api_key_env=args.api_key_env, probe=args.probe, activate=args.activate, read_key=args.read_key,
                accept_documented_model=args.accept_documented_model)
        print(json.dumps(result, ensure_ascii=False, indent=2));return 0
    except (OSError,ValueError,KeyError,TypeError) as error:
        parser.exit(1, f'msshi coder: {type(error).__name__}: {error}\n')


if __name__ == '__main__': raise SystemExit(main())
