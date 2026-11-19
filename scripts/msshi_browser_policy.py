"""Read legacy browser configuration; Steel enrollment has been retired.

This compatibility helper never installs a provider, opens a browser, reads API
keys, or makes a network request. New browser intent lives in
``msshi browser --browser chrome|edge|firefox|none``.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def assess(steel_available=False, personal_account=False, transfer=False, approved=False, note=''):
    return {'route': 'manual_user_browser', 'allowed': False,
            'legacy_steel_retired': True, 'automatic_browser_launch': False,
            'account_transfer': False, 'network_tested': False,
            'action': 'Choose a browser with msshi browser; log in manually in Hermes.'}


def status(home):
    home = Path(home)
    config_file = home / 'config.yaml'
    cfg = {}
    if config_file.is_file():
        from msshi_runtime import yaml_read
        cfg = yaml_read(config_file.read_bytes())
    enabled = (cfg.get('plugins') or {}).get('enabled') or []
    found = {name: name in enabled for name in ('browser-steel', 'msshi-steel-policy')}
    return {'home': str(home), 'status': 'legacy_steel_retired',
            'config_present': config_file.is_file(),
            'preferred_provider': (cfg.get('browser') or {}).get('cloud_provider'),
            'plugins': found, 'configured': any(found.values()),
            'ready_for_authorized_task': False, 'connected': False,
            'credentials_present': 'not_inspected', 'credentials_read_or_written': False,
            'authenticated': 'not_tested', 'api_requests': 0, 'network_tested': False,
            'auto_open_on_boot': False, 'personal_profile_copy': False,
            'note': 'Legacy entries are observed only; this helper does not enable them.'}


def install(home, source_root=None, steel_source=None):
    return {'status': 'legacy_steel_action_retired', 'changed': False,
            'installed': False, 'network_requests': 0, 'credentials_read_or_written': False,
            'message': 'Steel setup is retired. Use msshi browser --browser chrome|edge|firefox|none; sign in manually.'}


def rollback(home, receipt_file):
    from install_msshi import reject_links
    reject_links(home)
    reject_links(receipt_file)
    receipt_file = receipt_file.resolve(strict=True)
    base = home.resolve(strict=True)
    if not receipt_file.is_relative_to(base / "msshi-runtime" / "backups"):
        raise ValueError("Rollback receipt must be under this profile's MSSHI backups")
    receipt = json.loads(receipt_file.read_text(encoding="utf-8-sig"))
    if receipt.get("purpose") != "Strict Steel browser policy":
        raise ValueError("Not a Steel policy receipt")
    checked = []
    for item in receipt.get("entries", []):
        target = Path(item["target"])
        reject_links(target)
        resolved = target.resolve()
        allowed = {base / "config.yaml", base / "msshi-private" / "steel-install-managed.json"}
        plugin_file = any(resolved.parent == base / "plugins" / name for name in
                          ("browser-steel", "msshi-steel-policy"))
        if resolved not in allowed and not plugin_file:
            raise ValueError("Unexpected rollback target")
        if target.exists() and sha(target) != item.get("after_sha256"):
            raise ValueError("Local file changed after installation; preserved: " + str(target))
        backup = Path(item["backup"]).resolve(strict=True) if item.get("existed") else None
        if backup:
            reject_links(backup)
        if backup and (backup.parent != receipt_file.parent or sha(backup) != item.get("before_sha256")):
            raise ValueError("Backup provenance mismatch")
        checked.append((target, backup))
    for target, backup in checked:
        if backup:
            shutil.copy2(backup, target)
        elif target.is_file():
            target.unlink()
    return {"rolled_back": True, "receipt": str(receipt_file), "files": len(checked), "api_requests": 0}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hermes-home', type=Path, default=Path(os.environ.get('HERMES_HOME', str(Path.home() / '.hermes'))))
    parser.add_argument('--status', action='store_true')
    parser.add_argument('--install', action='store_true', help='Retired compatibility no-op; no plugin or account is installed.')
    parser.add_argument('--rollback', type=Path, help='Restore a verified historical Steel receipt; explicit action only.')
    parser.add_argument('--steel-source', type=Path, help=argparse.SUPPRESS)
    for flag in ('steel-ready', 'personal-account', 'account-transfer', 'approved'):
        parser.add_argument('--' + flag, action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--approval-note', default='', help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        if args.rollback:
            answer = rollback(args.hermes_home, args.rollback)
        elif any((args.install, args.steel_source, args.steel_ready, args.personal_account,
                  args.account_transfer, args.approved, args.approval_note)):
            answer = install(args.hermes_home)
        else:
            answer = status(args.hermes_home)
        print(json.dumps(answer, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, TypeError) as error:
        print(json.dumps({'error_type': type(error).__name__, 'changed': False,
                          'message': 'Legacy browser action could not be completed; review the local receipt.'}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
