"""Compress a JSON request locally with llmtrim; never send a model request."""
from __future__ import annotations
import argparse
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

MAX_BYTES = 16 * 1024 * 1024


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('Ambiguous duplicate JSON key')
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError('Non-finite JSON number')


def _parse(data):
    return json.loads(data, object_pairs_hook=_pairs, parse_float=Decimal,
                      parse_constant=_reject_constant)


def _canonical(value):
    if isinstance(value, dict):
        entries = []
        for key, child in value.items():
            # Only tool-result JSON text may be minified; all other request
            # strings, instructions, model IDs and tool IDs remain exact.
            if key == 'content' and value.get('role') == 'tool' and isinstance(child, str):
                try:
                    nested = _parse(child)
                    if isinstance(nested, (dict, list)):
                        entries.append((key, ('json-tool-content', _canonical(nested))))
                        continue
                except (ValueError, TypeError, RecursionError):
                    pass
            entries.append((key, _canonical(child)))
        return ('object', tuple(sorted(entries)))
    if isinstance(value, list):
        return ('array', tuple(_canonical(child) for child in value))
    if isinstance(value, Decimal):
        return ('decimal', value)
    if value is None:
        return ('null',)
    if type(value) in (str, int, bool):
        return (type(value).__name__, value)
    raise ValueError('Unsupported JSON type')


def compress(payload: bytes, binary: str, provider: str | None = None) -> bytes:
    if len(payload) > MAX_BYTES:
        raise ValueError('Input exceeds the 16 MiB local limit')
    parsed = _parse(payload)
    if isinstance(parsed, dict):
        if parsed.get('error') or parsed.get('success') is False:
            return payload
        for row in parsed.get('messages', []):
            if isinstance(row, dict) and row.get('role') == 'tool' and isinstance(row.get('content'), str):
                try:
                    content = _parse(row['content'])
                    if isinstance(content, dict) and (content.get('error') or content.get('success') is False):
                        return payload
                except (ValueError, TypeError, RecursionError):
                    pass
    original = _canonical(parsed)
    config = Path(__file__).with_name('msshi_llmtrim_json_only.toml')
    if not config.is_file():
        return payload
    child_env = dict(os.environ, PYTHONUTF8='1', LLMTRIM_CONFIG=str(config),
                     LLMTRIM_NO_UPDATE_CHECK='1', LLMTRIM_CAPTURE_MAX_MB='0')
    child_env.pop('LLMTRIM_PRESET', None)
    command = [binary, 'compress']
    if provider:
        command += ['--provider', provider]
    try:
        result = subprocess.run(command, input=payload, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=child_env, timeout=30,
            **({'creationflags':subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {}))
        if (result.returncode or len(result.stdout) >= len(payload)
                or _canonical(_parse(result.stdout)) != original):
            return payload
        return result.stdout
    except (OSError, subprocess.SubprocessError, ValueError, TypeError, RecursionError):
        # Fail open without printing supplied data, credentials or stderr.
        return payload

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home',type=Path,help='Hermes data root; otherwise detect the existing local installation')
    parser.add_argument('--binary',type=Path)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--input',type=Path,help='Provider-shaped JSON request; local file only')
    action.add_argument('--status',action='store_true',help='Read only aggregate automatic hook counters')
    action.add_argument('--install',action='store_true',help='Prepare/enable MSSHITrim on native profiles; preview until --apply')
    parser.add_argument('--profile',default='default',help='Hermes profile ID for status')
    parser.add_argument('--profiles',default='all',help='Installation only: all or comma-separated real profile IDs')
    parser.add_argument('--apply',action='store_true',help='Installation only: apply with rollback receipt')
    parser.add_argument('--download-runtime',action='store_true',help='Installation only: allow checksum-pinned CLI download')
    parser.add_argument('--force-enable',action='store_true',help='Installation only: explicitly override a previous trim disable')
    parser.add_argument('--output',type=Path,help='Output file; defaults to stdout. Must differ from input.')
    parser.add_argument('--provider',choices=('openai','anthropic','google','gemini'),default='openai',
        help='Input JSON format, default OpenAI-compatible; does not change any Hermes provider setting')
    args = parser.parse_args(argv)
    try:
        if args.home is None:
            try:
                import msshi_hermes_profiles as profiles
                args.home=profiles.resolve_hermes_home()
            except ImportError:
                args.home=Path(os.environ.get('HERMES_HOME',str(Path.home()/'.hermes')))
        if args.install:
            try:
                import msshi_trim_setup
            except ImportError:
                raise ValueError('Use the global msshi trim --install command from a complete MSSHI installation')
            command=['--home',str(args.home),'--profiles',args.profiles]
            if args.apply: command.append('--apply')
            if args.download_runtime: command.append('--download-runtime')
            if args.force_enable: command.append('--force-enable')
            return msshi_trim_setup.main(command)
        if args.status:
            if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,95}',args.profile):
                raise ValueError('Invalid profile ID')
            root = args.home.expanduser().absolute()
            root = root.parent.parent if root.parent.name.casefold() == 'profiles' else root
            profile = root if args.profile == 'default' else root/'profiles'/args.profile
            plugin_config = {}
            try:
                import msshi_hermes_profiles as profiles
                config_file = profile/'config.yaml'
                cfg = profiles.load_yaml_mapping(config_file.read_bytes()) if config_file.is_file() else {}
                plugin_config = cfg.get('plugins') or {}
            except (ImportError, OSError, ValueError):
                plugin_config = {}
            settings = ((plugin_config.get('entries') or {}).get('msshi-auto-trim') or {}).get('settings') or {}
            enabled = ('msshi-auto-trim' in (plugin_config.get('enabled') or [])
                       and 'msshi-auto-trim' not in (plugin_config.get('disabled') or [])
                       and settings.get('enabled', True) is not False)
            binary_path = Path(settings['binary']) if settings.get('binary') else None
            if binary_path is None:
                binary_path = next((path for path in (root/'tools/llmtrim/llmtrim.exe', root/'tools/llmtrim/llmtrim') if path.is_file()), None)
                found_on_path = shutil.which('llmtrim') if binary_path is None else None
                binary_path = Path(found_on_path) if found_on_path else binary_path
            runtime_present = binary_path is not None and binary_path.is_file()
            runtime_verified = False
            if runtime_present:
                provenance = binary_path.with_name('msshi-provenance.json')
                if provenance.is_file() and provenance.stat().st_size < 16384:
                    record = json.loads(provenance.read_bytes())
                    runtime_verified = (record.get('managed_by') == 'msshi-trim-cli-v1'
                        and record.get('binary_sha256') == hashlib.sha256(binary_path.read_bytes()).hexdigest())
            states = list((profile/'plugin-data').glob('agent-plugin-msshi-auto-trim-*/state.json'))
            if len(states)>1:
                raise ValueError('Multiple plugin namespaces found; inspect native plugin status')
            metrics = json.loads(states[0].read_text(encoding='utf-8')).get('metrics',{}) if states else {}
            fields = {'compressed','skipped','unchanged','data_check_rejected','binary_missing',
                      'compressor_error','input_bytes','output_bytes','saved_bytes'}
            safe_metrics = {key:value for key,value in metrics.items() if key in fields and isinstance(value,int)}
            print(json.dumps({'display_name':'MSSHITrim','plugin_id':'msshi-auto-trim',
                'profile':args.profile,'plugin_installed':(profile/'plugins/msshi-auto-trim/plugin.yaml').is_file(),
                'plugin_enabled':enabled,'runtime_present':runtime_present,
                'runtime_hash_matches_installer_record':runtime_verified,
                'scope':'automatic eligible large JSON tool results; not all conversation',
                'state_recorded':bool(states),'metrics':safe_metrics,'llm_calls_for_status':0},indent=2))
            return 0
        binary = args.binary or next((path for path in (args.home/'tools/llmtrim/llmtrim.exe', args.home/'tools/llmtrim/llmtrim') if path.is_file()),None)
        binary = str(binary) if binary else shutil.which('llmtrim')
        if not binary or not Path(binary).is_file():
            raise ValueError('llmtrim executable not found; no compression was applied')
        if args.input.stat().st_size > MAX_BYTES:
            raise ValueError('Input exceeds the 16 MiB local limit')
        if args.output and args.output.resolve() == args.input.resolve():
            raise ValueError('Keep the original input; choose a different output path')
        payload = args.input.read_bytes()
        result = compress(payload,binary,args.provider)
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True)
            with args.output.open('xb') as stream:
                stream.write(result)
            print(json.dumps({'success':True,'local_only':True,'policy':'json-only','unchanged':result==payload,'llm_calls':0,
                'input_bytes':len(payload),'output_bytes':len(result),'output':str(args.output),
                'input_sha256':hashlib.sha256(payload).hexdigest(),'output_sha256':hashlib.sha256(result).hexdigest()},indent=2))
        else:
            sys.stdout.buffer.write(result)
        return 0
    except (OSError,ValueError,subprocess.SubprocessError) as error:
        parser.exit(1,f'msshi trim: {error}\n')

if __name__ == '__main__':
    raise SystemExit(main())
