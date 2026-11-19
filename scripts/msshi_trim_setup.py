"""Install MSSHITrim's native hook and a pinned local-only llmtrim CLI.

No upstream setup command, TLS certificate, proxy, daemon, login service,
model, provider, API key, prompt capture, or model request is configured here.
Only a selected install may download a checksum-pinned release archive.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tarfile
import time
import urllib.request
import zipfile

import msshi_hermes_profiles as profiles

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = 'msshi-auto-trim'  # Stable ID; never enable a second compression hook.
DISPLAY_NAME = 'MSSHITrim'
VERSION = '0.13.8'
SOURCE_REVISION = '7dce1a46c55195f16b2e36cc675581b5ad7006e9'
FILES = ('__init__.py', 'plugin.yaml', 'README.md', 'json-only.toml')
OWNER = 'msshi-trim-cli-v1'
MAX_ARCHIVE = 64 * 1024 * 1024
MAX_BINARY = 96 * 1024 * 1024
# Published GitHub release asset digests; the downloaded payload must match.
ASSETS = {
    ('windows','x86_64'): ('llmtrim-x86_64-pc-windows-msvc.zip', 'd1b5c632fedcdbf6e1d7606faa6aaa5c2471dfca43d56e410c4b295c18a25df1'),
    ('windows','aarch64'): ('llmtrim-aarch64-pc-windows-msvc.zip', 'fbeee6d43056a078538f9855cf2312b242d55241d8421221f168d31b71bf86cf'),
    ('darwin','x86_64'): ('llmtrim-x86_64-apple-darwin.tar.gz', 'd6af9709e554051ee781473f0258a85308d8667e11cf8ce867e8dee42d6c362f'),
    ('darwin','aarch64'): ('llmtrim-aarch64-apple-darwin.tar.gz', '82e95264b35d1ef49acbfdec9414f3519adfd07fb6c41b2c41bcad492b50fede'),
    ('linux','x86_64'): ('llmtrim-x86_64-unknown-linux-musl.tar.gz', '812d092460dbf880910b46b7ebac686ef0bfdae201006391cb8d8b1144731ca8'),
    ('linux','aarch64'): ('llmtrim-aarch64-unknown-linux-gnu.tar.gz', '4f421db37334afd57f0b5b46fddef47a69724ec446de14621b0528a39ae0a713'),
}
# Reviewed previous MSSHI 0.1.0 plugin files may be upgraded. Unknown edits stay.
LEGACY_FILES = {
    '__init__.py': '10b3134c2b5bca3251c41390973c640229a86abd0c9bcb4bee96539c1ad84a4c',
    'plugin.yaml': '5ba70ee9c675cb138271261083621647e8a06254321d4768de79456596e31183',
    'README.md': '453552b4911d64ddad630888fc1b3002bbf338d49db2e820c497bf0f25b99471',
    'json-only.toml': '9bc3fc752dea3ec1556695f67c65c607941c7385733361fcd8b4ee7e86af8e64',
}
LEGACY_NORMALIZED = {
    '__init__.py': '0b4d82f2447602efb09ee6fc95ad0756a7617094accf61a4c8796f0e3d2ad388',
    'plugin.yaml': 'db77808e64b310ca03c9d0b0def65711bce108c43d53d51ade51b2e5357076f9',
    'README.md': '7a02f9d70eacd67df531625afe99d1e559680b197712952bf54c0c2be2fc7018',
    'json-only.toml': 'ee68a00a21f5f1655bc7223b10ca1d75d107abf662038d7afcab0db8d765af61',
}
WINDOWS_X64_BINARY_SHA256 = 'd7703c7b0710c3c06a8846d1c0ed4009c671a880d699449c803848da3f3c3eab'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def checked(path):
    raw = str(path)
    if raw.startswith(('\\\\', '//')) or '\x00' in raw:
        raise ValueError('Local paths without UNC or NUL are required')
    path = Path(os.path.abspath(Path(path).expanduser()))
    for item in (path, *path.parents):
        if os.path.lexists(item) and (item.is_symlink() or getattr(item.lstat(),'st_file_attributes',0) & 0x400):
            raise ValueError('MSSHITrim paths must not cross links or junctions')
    return path


def host_target():
    system = platform.system().lower()
    arch = platform.machine().lower()
    arch = {'amd64':'x86_64','x64':'x86_64','arm64':'aarch64'}.get(arch,arch)
    return system,arch


def fetch_archive(url):
    request = urllib.request.Request(url, headers={'User-Agent':'MSSHITrim-pinned-install/1'})
    deadline=time.monotonic()+120
    with urllib.request.urlopen(request, timeout=15) as response:
        if not response.geturl().startswith('https://'):
            raise ValueError('Release redirect did not remain HTTPS')
        size = response.headers.get('Content-Length')
        if size and int(size) > MAX_ARCHIVE:
            raise ValueError('Release archive exceeds the download bound')
        chunks=[];total=0
        read_chunk=getattr(response,'read1',response.read)
        while True:
            if time.monotonic()>deadline:
                raise ValueError('Pinned runtime download exceeded the two-minute install limit')
            chunk=read_chunk(min(65536,MAX_ARCHIVE+1-total))
            if not chunk:
                break
            chunks.append(chunk);total+=len(chunk)
            if total>MAX_ARCHIVE:
                raise ValueError('Release archive exceeds the download bound')
        data=b''.join(chunks)
    if len(data)>MAX_ARCHIVE:
        raise ValueError('Release archive exceeds the download bound')
    return data


def extract_binary(archive, asset, expected_sha):
    """Read only one ordinary named binary; never extract an archive to disk."""
    if sha(archive) != expected_sha:
        raise ValueError('Pinned llmtrim release archive checksum mismatch')
    wanted = 'llmtrim.exe' if asset.endswith('.zip') else 'llmtrim'
    found=[]
    if asset.endswith('.zip'):
        with zipfile.ZipFile(io.BytesIO(archive)) as source:
            for info in source.infolist():
                if Path(info.filename).name != wanted:
                    continue
                if info.is_dir() or info.file_size>MAX_BINARY or ((info.external_attr>>16)&0o170000)==0o120000:
                    raise ValueError('Unexpected llmtrim archive member')
                found.append(source.read(info))
    else:
        with tarfile.open(fileobj=io.BytesIO(archive),mode='r:gz') as source:
            for info in source.getmembers():
                if Path(info.name).name != wanted:
                    continue
                if not info.isfile() or info.size>MAX_BINARY:
                    raise ValueError('Unexpected llmtrim archive member')
                stream=source.extractfile(info)
                if stream is None:
                    raise ValueError('Could not read llmtrim binary member')
                found.append(stream.read(MAX_BINARY+1))
    if len(found)!=1 or not found[0] or len(found[0])>MAX_BINARY:
        raise ValueError('Expected exactly one bounded llmtrim executable')
    return found[0]


def probe(binary):
    result=subprocess.run([str(binary),'--version'],capture_output=True,text=True,timeout=8,
        env=dict(os.environ, LLMTRIM_NO_UPDATE_CHECK='1', LLMTRIM_CAPTURE_MAX_MB='0'),
        **({'creationflags':subprocess.CREATE_NO_WINDOW} if os.name=='nt' else {}))
    if result.returncode or result.stdout.strip()!=f'llmtrim {VERSION}':
        raise ValueError('Existing llmtrim version is not the pinned compatible release')


def binary_plan(home, *, allow_download=False, target=None):
    target=target or host_target()
    if target not in ASSETS:
        return None,{}, {'status':'pending_unsupported_platform','platform':'/'.join(target)}
    asset,archive_sha=ASSETS[target]
    directory=home/'tools/llmtrim'
    binary=checked(directory/('llmtrim.exe' if target[0]=='windows' else 'llmtrim'))
    marker=checked(directory/'msshi-provenance.json')
    metadata={'managed_by':OWNER,'version':VERSION,'repository':'https://github.com/fkiene/llmtrim',
        'source_revision':SOURCE_REVISION,'asset':asset,'archive_sha256':archive_sha,
        'license':'MPL-2.0','setup_proxy_ca_daemon':False}
    if binary.is_file():
        actual_sha=sha(binary.read_bytes())
        prior=json.loads(marker.read_bytes()) if marker.is_file() else {}
        known=(target==('windows','x86_64') and actual_sha==WINDOWS_X64_BINARY_SHA256)
        known=known or (prior.get('managed_by')==OWNER and prior.get('archive_sha256')==archive_sha
                        and prior.get('binary_sha256')==actual_sha)
        if not known:
            return None,{}, {'status':'pending_existing_unverified_binary_preserved','binary_present':True}
        try:
            probe(binary)
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            return None,{}, {'status':'pending_verified_binary_probe_failed','reason':type(error).__name__}
        metadata['binary_sha256']=actual_sha
        changes={} if marker.is_file() and marker.read_bytes()==encode(metadata) else {marker:encode(metadata)}
        return binary,changes,{'status':'verified_existing','version':VERSION,'binary_sha256':actual_sha,'downloaded':False}
    if not allow_download:
        return None,{}, {'status':'pending_binary_download','version':VERSION,'asset':asset,'archive_sha256':archive_sha}
    archive=fetch_archive('https://github.com/fkiene/llmtrim/releases/download/v'+VERSION+'/'+asset)
    data=extract_binary(archive,asset,archive_sha)
    metadata['binary_sha256']=sha(data)
    return binary,{binary:data,marker:encode(metadata)}, {'status':'verified_release_download','version':VERSION,
        'asset':asset,'archive_sha256':archive_sha,'binary_sha256':sha(data),'downloaded':True}


def profile_dirs(home, selected=None):
    roots={'default':home}
    parent=home/'profiles'
    if parent.is_dir():
        for folder in sorted(parent.iterdir()):
            if folder.name=='default' or not profiles.PROFILE_ID_RE.fullmatch(folder.name):
                continue
            checked(folder)
            if folder.is_dir() and any((folder/name).is_file() for name in ('config.yaml','profile.yaml','SOUL.md')):
                roots[folder.name]=folder
    if selected is not None:
        missing=set(selected)-set(roots)
        if missing:
            raise ValueError('Unknown selected Hermes profile')
        roots={name:roots[name] for name in dict.fromkeys(selected)}
    return roots


def enable_config(original, binary, *, force_enable=False):
    before=profiles.load_yaml_mapping(original)
    after=deepcopy(before)
    plugins=after.get('plugins') or {}
    if not isinstance(plugins,dict):
        raise ValueError('Existing plugins configuration needs manual review')
    enabled=plugins.get('enabled') or []
    disabled=plugins.get('disabled') or []
    if not isinstance(enabled,list) or not isinstance(disabled,list):
        raise ValueError('Existing native plugin enable/disable schema needs review')
    entries=plugins.get('entries') or {}
    entry=deepcopy(entries.get(PLUGIN) or {})
    settings=entry.get('settings') or {}
    explicitly_off=PLUGIN in disabled or settings.get('enabled') is False
    if explicitly_off and not force_enable:
        return original,'preserved_explicit_disable'
    if binary is None:
        return original,'pending_binary'
    settings=deepcopy(settings)
    # Keep a user's compatible binary choice only when it is the verified binary.
    if settings.get('binary') and checked(settings['binary'])!=checked(binary):
        return original,'preserved_custom_binary_setting'
    settings.update(enabled=True,binary=str(binary))
    for key,value in [('min_chars',2048),('max_chars',262144),('timeout_seconds',3.0)]:
        settings.setdefault(key,value)
    entry['settings']=settings
    entries=deepcopy(entries);entries[PLUGIN]=entry
    plugins=deepcopy(plugins);plugins['entries']=entries
    plugins['enabled']=list(dict.fromkeys([*enabled,PLUGIN]))
    plugins['disabled']=[name for name in disabled if name!=PLUGIN]
    after['plugins']=plugins
    if after==before:
        return original,'enabled_unchanged'
    rendered=profiles._replace_yaml_section_bytes(original,'plugins',plugins)
    if profiles.load_yaml_mapping(rendered)!=after:
        raise ValueError('Narrow native plugin configuration edit could not be verified')
    if any(before.get(key)!=after.get(key) for key in set(before)|set(after) if key!='plugins'):
        raise ValueError('A non-plugin setting changed')
    return rendered,'enabled'


def managed_plugin_file(current, incoming, filename):
    """Recognize this release or the reviewed predecessor, including Git EOLs."""
    return (sha(current) in {sha(incoming),LEGACY_FILES[filename]}
            or sha(current.replace(b'\r\n',b'\n')) in {
                sha(incoming.replace(b'\r\n',b'\n')),LEGACY_NORMALIZED[filename]})


def install(home, *, source_root=ROOT, selected=None, apply=False, allow_download=False,
            force_enable=False):
    home=checked(home);source_root=checked(source_root)
    plugin_source=checked(source_root/'hermes_plugins'/PLUGIN)
    incoming={name:checked(plugin_source/name).read_bytes() for name in FILES}
    roots=profile_dirs(home,selected)
    binary,binary_changes,binary_result=binary_plan(home,allow_download=allow_download and apply)
    changes=dict(binary_changes)
    rows=[]
    for name,folder in roots.items():
        row={'profile':name,'status':'pending_native_profile','plugin_id':PLUGIN}
        if not folder.is_dir():
            rows.append(row);continue
        blocked=False
        for filename,data in incoming.items():
            path=checked(folder/'plugins'/PLUGIN/filename)
            if path.is_file():
                current=path.read_bytes()
                if not managed_plugin_file(current,data,filename):
                    blocked=True;break
        if blocked:
            row['status']='preserved_custom_plugin_files';rows.append(row);continue
        config=checked(folder/'config.yaml')
        original=config.read_bytes() if config.is_file() else None
        updated,state=enable_config(original,binary,force_enable=force_enable) if original is not None else (None,'deferred_until_native_config')
        row['status']=state
        if state.startswith('preserved_'):
            rows.append(row);continue
        for filename,data in incoming.items():
            path=checked(folder/'plugins'/PLUGIN/filename)
            if not path.is_file() or path.read_bytes()!=data:
                changes[path]=data
        if original is not None and updated!=original:
            changes[config]=updated
        rows.append(row)
    result={'display_name':DISPLAY_NAME,'plugin_id':PLUGIN,'applied':False,
        'automatic_scope':'eligible large JSON tool results with exact canonical data equality',
        'binary':binary_result,'profiles':rows,'files_planned':len(changes),'receipt':None,
        'model_calls':0,'proxy_ca_daemon_changes':False,'provider_model_or_key_changes':False,
        'cost_savings_measured':False}
    if not apply or not changes:
        return result
    original_hashes={path:sha(path.read_bytes()) if path.is_file() else None for path in changes}
    tx=profiles.ProfileTransaction(home)
    try:
        for path,data in changes.items():
            checked(path)
            if (sha(path.read_bytes()) if path.is_file() else None)!=original_hashes[path]:
                raise ValueError('Concurrent file edit; installation cancelled')
            tx.write(path,data,0o700 if path==binary else 0o600)
        if binary is not None and binary in changes:
            probe(binary)
        result['receipt']=tx.commit();result['applied']=True
    except Exception:
        tx.rollback();raise
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home',type=Path,help='Hermes data root; otherwise detect the existing local installation')
    parser.add_argument('--source',type=Path,default=ROOT)
    parser.add_argument('--profiles',default='all',help='all or comma-separated real profile IDs')
    parser.add_argument('--apply',action='store_true',help='Write plugin files/configuration with rollback receipt')
    parser.add_argument('--download-runtime',action='store_true',help='Allow a pinned release download, only with --apply')
    parser.add_argument('--force-enable',action='store_true',help='Explicitly re-enable this plugin if the user previously disabled it')
    args=parser.parse_args(argv)
    args.home=profiles.resolve_hermes_home(args.home)
    names=None if args.profiles=='all' else [x.strip() for x in args.profiles.split(',') if x.strip()]
    try:
        result=install(args.home,source_root=args.source,selected=names,apply=args.apply,
            allow_download=args.download_runtime,force_enable=args.force_enable)
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0
    except (OSError,ValueError,subprocess.SubprocessError,zipfile.BadZipFile,tarfile.TarError) as error:
        parser.exit(1,f'MSSHITrim: {error}\n')


if __name__=='__main__':
    raise SystemExit(main())
