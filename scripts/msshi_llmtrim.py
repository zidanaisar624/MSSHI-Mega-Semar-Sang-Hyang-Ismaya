"""Compress a JSON request locally with llmtrim; never send a model request."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

MAX_BYTES = 16 * 1024 * 1024

def compress(payload: bytes, binary: str, provider: str | None = None) -> bytes:
    if len(payload) > MAX_BYTES:
        raise ValueError('Input exceeds the 16 MiB local limit')
    json.loads(payload)
    command = [binary, 'compress']
    if provider:
        command += ['--provider', provider]
    result = subprocess.run(command, input=payload, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env={**os.environ, 'LLMTRIM_PRESET':'safe', 'PYTHONUTF8':'1'}, timeout=30,
        **({'creationflags':subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {}))
    if result.returncode:
        # Do not leak the supplied payload or possible credentials through error messages.
        raise ValueError('Local llmtrim compression failed; original input was retained')
    json.loads(result.stdout)
    return result.stdout

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home',type=Path,default=Path(os.environ.get('HERMES_HOME',str(Path.home()/'.hermes'))))
    parser.add_argument('--binary',type=Path)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--input',type=Path,help='Provider-shaped JSON request; local file only')
    action.add_argument('--status',action='store_true',help='Read only aggregate automatic hook counters')
    parser.add_argument('--profile',default='default',help='Hermes profile ID for status')
    parser.add_argument('--output',type=Path,help='Output file; defaults to stdout. Must differ from input.')
    parser.add_argument('--provider',choices=('openai','anthropic','google','gemini'),default='openai',
        help='Input JSON format, default OpenAI-compatible; does not change any Hermes provider setting')
    args = parser.parse_args(argv)
    try:
        if args.status:
            if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,95}',args.profile):
                raise ValueError('Invalid profile ID')
            root = args.home.expanduser().absolute()
            root = root.parent.parent if root.parent.name.casefold() == 'profiles' else root
            profile = root if args.profile == 'default' else root/'profiles'/args.profile
            states = list((profile/'plugin-data').glob('agent-plugin-msshi-auto-trim-*/state.json'))
            if len(states)>1:
                raise ValueError('Multiple plugin namespaces found; inspect native plugin status')
            metrics = json.loads(states[0].read_text(encoding='utf-8')).get('metrics',{}) if states else {}
            fields = {'compressed','skipped','unchanged','data_check_rejected','binary_missing',
                      'compressor_error','input_bytes','output_bytes','saved_bytes'}
            safe_metrics = {key:value for key,value in metrics.items() if key in fields and isinstance(value,int)}
            print(json.dumps({'profile':args.profile,'plugin_installed':(profile/'plugins/msshi-auto-trim/plugin.yaml').is_file(),
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
            print(json.dumps({'success':True,'local_only':True,'preset':'safe','llm_calls':0,
                'input_bytes':len(payload),'output_bytes':len(result),'output':str(args.output),
                'input_sha256':hashlib.sha256(payload).hexdigest(),'output_sha256':hashlib.sha256(result).hexdigest()},indent=2))
        else:
            sys.stdout.buffer.write(result)
        return 0
    except (OSError,ValueError,subprocess.SubprocessError) as error:
        parser.exit(1,f'msshi trim: {error}\n')

if __name__ == '__main__':
    raise SystemExit(main())
