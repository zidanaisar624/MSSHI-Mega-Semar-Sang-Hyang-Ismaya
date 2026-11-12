"""Inspect/install native fail-closed Steel browsing without creating an API session."""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from urllib.parse import urlsplit

STEEL_COMMIT = "d8a1e39657d3e3deaa59da37e857be3f14b9dc5b"
STEEL_URL = "https://github.com/steel-dev/hermes-steel.git"


def yaml_reader(home):
    try:
        from ruamel.yaml import YAML
        return YAML()
    except ImportError:
        from msshi_runtime import yaml_module
        before = os.environ.get("HERMES_HOME")
        try:
            os.environ["HERMES_HOME"] = str(home)
            return yaml_module()()
        finally:
            if before is None:
                os.environ.pop("HERMES_HOME", None)
            else:
                os.environ["HERMES_HOME"] = before


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def managed_browser_settings(cfg):
    browser = cfg.get("browser") or {}
    steel = browser.get("steel") or {}
    return {"cloud_provider": browser.get("cloud_provider"),
            "use_real_profile": browser.get("use_real_profile"),
            "auto_local_for_private_urls": browser.get("auto_local_for_private_urls"),
            "steel": {k: steel.get(k) for k in ("use_proxy", "solve_captcha", "session_timeout")}}


def assess(steel_available, personal_account=False, transfer=False, approved=False, note=""):
    # Pure route helper; CLI readiness is measured from installation, never a user flag.
    if transfer:
        return {"route": "account-transfer-review", "allowed": False, "approval_required": True,
                "transfer_implemented": False, "action": "review_supported_method_then_separate_consent"}
    if personal_account:
        return {"route": "msshi_personal_browser", "allowed": bool(approved and note.strip()),
                "approval_required": True, "native_human_gate_required": True}
    return {"route": "hermes-steel" if steel_available else "steel-setup-required",
            "allowed": bool(steel_available), "native_budget_approval_required": True,
            "local_fallback": False, "network_tested": False}


def status(home):
    yaml = yaml_reader(home)
    cfg = yaml.load((home / "config.yaml").read_text(encoding="utf-8")) or {}
    browser = cfg.get("browser") or {}
    enabled = (cfg.get("plugins") or {}).get("enabled") or []
    found = {}
    for name in ("browser-steel", "msshi-steel-policy"):
        folder = home / "plugins" / name
        found[name] = bool((folder / "plugin.yaml").is_file() and (folder / "__init__.py").is_file()
                           and name in enabled)
    envkeys = {}
    if (home / ".env").is_file():
        for line in (home / ".env").read_text(encoding="utf-8").splitlines():
            k, sep, v = line.partition("=")
            if sep and k.strip() in {"STEEL_API_KEY", "STEEL_BASE_URL"}:
                envkeys[k.strip()] = bool(v.strip().strip("\"'"))
    key = envkeys.get("STEEL_API_KEY", False) or bool(os.environ.get("STEEL_API_KEY"))
    base = (browser.get("steel") or {}).get("base_url") or os.environ.get("STEEL_BASE_URL") or "https://api.steel.dev"
    try:
        host = urlsplit(str(base)).hostname
    except ValueError:
        host = None
    custom = bool(host and host.rstrip(".").lower() != "api.steel.dev")
    configured = browser.get("cloud_provider") == "steel" and all(found.values())
    return {"home": str(home), "preferred_provider": browser.get("cloud_provider"), "plugins": found,
            "credentials_present": bool(key), "custom_endpoint_configured": custom,
            "configured": configured, "ready_for_authorized_task": configured and (key or custom),
            "authenticated": "not_tested", "connected": False, "api_requests": 0,
            "network_tested": False, "auto_open_on_boot": False, "local_fallback": False,
            "personal_profile_copy": False, "steel_upstream_commit": STEEL_COMMIT}


def install(home, source_root, steel_source=None):
    from install_msshi import reject_links
    reject_links(home)
    reject_links(home / "config.yaml")
    if not (home / "config.yaml").is_file():
        raise ValueError("Existing Hermes config.yaml required")
    own = source_root / "hermes_plugins" / "msshi-steel-policy"
    if not (own / "plugin.yaml").is_file():
        raise ValueError("MSSHI policy plugin missing from release")
    if steel_source is None:
        steel_source = home / "msshi-private" / "steel-source"
        if not steel_source.exists():
            subprocess.run(["git", "clone", STEEL_URL, str(steel_source)], check=True, timeout=120)
        subprocess.run(["git", "-C", str(steel_source), "fetch", "origin", STEEL_COMMIT], check=True, timeout=120)
        subprocess.run(["git", "-C", str(steel_source), "checkout", "--detach", STEEL_COMMIT], check=True, timeout=30)
    actual = subprocess.check_output(["git", "-C", str(steel_source), "rev-parse", "HEAD"], text=True).strip()
    if actual != STEEL_COMMIT:
        raise ValueError("Official Steel source does not match reviewed pinned commit")
    if subprocess.run(["git", "-C", str(steel_source), "diff", "--quiet", "HEAD", "--",
                       "__init__.py", "provider.py", "config.py", "scrape_tool.py", "session_note.py",
                       "session_options.py", "plugin.yaml", "LICENSE"], capture_output=True).returncode:
        raise ValueError("Reviewed Steel source files were modified locally; preserved and refused")
    files = {}
    for name in ("__init__.py", "provider.py", "config.py", "scrape_tool.py", "session_note.py",
                 "session_options.py", "plugin.yaml", "LICENSE"):
        files[home / "plugins" / "browser-steel" / name] = (steel_source / name).read_bytes()
    # The official scrape_tool imports a helper absent from stable Hermes.
    # Scrape/options are blocked anyway. Keep provider registration on this host.
    entrypoint = home / "plugins" / "browser-steel" / "__init__.py"
    marker = "    from .provider import SteelBrowserProvider\n"
    original_entrypoint = files[entrypoint].decode("utf-8").replace("\r\n", "\n")
    if original_entrypoint.count(marker) != 1:
        raise ValueError("Reviewed Steel entrypoint changed; refuse compatibility adaptation")
    compatible = marker + ("    try:\n"
        "        from tools.url_safety import sensitive_query_param_name\n"
        "    except ImportError:\n"
        "        # MSSHI compatibility: provider-only registration on this Hermes.\n"
        "        ctx.register_browser_provider(SteelBrowserProvider())\n"
        "        return\n")
    files[entrypoint] = original_entrypoint.replace(marker, compatible).encode("utf-8")
    for path in own.iterdir():
        if path.is_file() and path.suffix in {".py", ".yaml", ".md"}:
            files[home / "plugins" / "msshi-steel-policy" / path.name] = path.read_bytes()
    ownership = home / "msshi-private" / "steel-install-managed.json"
    reject_links(ownership)
    previous = json.loads(ownership.read_text()) if ownership.exists() else {}
    for target, data in files.items():
        reject_links(target)
        if target.exists() and target.read_bytes() != data and previous.get(str(target)) != sha(target):
            raise ValueError("Refusing to overwrite unowned/customized plugin file: " + str(target))
    yaml = yaml_reader(home)
    cfgpath = home / "config.yaml"
    cfg = yaml.load(cfgpath.read_text(encoding="utf-8"))
    original = copy.deepcopy(cfg)
    desired_browser = {"cloud_provider": "steel", "use_real_profile": False,
                       "auto_local_for_private_urls": False,
                       "steel": {"use_proxy": False, "solve_captcha": False, "session_timeout": 180000}}
    if previous:
        baseline_browser = previous.get("_browser_settings", desired_browser)
        if managed_browser_settings(cfg) != baseline_browser:
            raise ValueError("Managed browser settings were customized after installation; preserved. Review them before reinstalling.")
    plugins = cfg.setdefault("plugins", {})
    if plugins.get("isolation", "in_process") != "in_process":
        raise ValueError("Strict Steel middleware requires native plugins.isolation: in_process; current custom host isolation was preserved")
    enabled = plugins.setdefault("enabled", [])
    for name in ("browser-steel", "msshi-steel-policy"):
        if name not in enabled:
            enabled.append(name)
        if name in plugins.get("disabled", []):
            plugins["disabled"].remove(name)
    browser = cfg.setdefault("browser", {})
    browser["cloud_provider"] = "steel"
    browser["use_real_profile"] = False
    browser["auto_local_for_private_urls"] = False
    steel = browser.setdefault("steel", {})
    steel.update({"use_proxy": False, "solve_captcha": False, "session_timeout": 180000})
    from io import StringIO
    buffer = StringIO()
    yaml.dump(cfg, buffer)
    protected_before = {k: v for k, v in original.items() if k not in {"browser", "plugins"}}
    protected_after = {k: v for k, v in cfg.items() if k not in {"browser", "plugins"}}
    if protected_before != protected_after:
        raise ValueError("Non-browser/plugin settings changed; refusing install")
    files[cfgpath] = buffer.getvalue().encode("utf-8")
    files[ownership] = json.dumps({**{str(p): hashlib.sha256(data).hexdigest()
                                  for p, data in files.items() if p != cfgpath},
                                  "_browser_settings": managed_browser_settings(cfg)}, indent=2).encode("utf-8")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S-%fZ")
    receipt_dir = home / "msshi-runtime" / "backups" / (stamp + "-steel")
    receipt_dir.mkdir(parents=True, exist_ok=False)
    receipt = {"schema": 1, "home": str(home), "purpose": "Strict Steel browser policy", "entries": []}
    for index, target in enumerate(files):
        item = {"target": str(target), "existed": target.exists()}
        if target.exists():
            backup = receipt_dir / (str(index) + ".bak")
            shutil.copy2(target, backup)
            item.update(backup=str(backup), before_sha256=sha(target))
        receipt["entries"].append(item)
    (receipt_dir / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    applied = []
    try:
        for target, data in files.items():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            applied.append(target)
    except Exception:
        for item in reversed(receipt["entries"]):
            target = Path(item["target"])
            if target not in applied:
                continue
            if item["existed"]:
                shutil.copy2(item["backup"], target)
            elif target.is_file():
                target.unlink()
        raise
    receipt["entries"] = [{**item, "after_sha256": sha(item["target"])} for item in receipt["entries"]]
    (receipt_dir / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return {"receipt": str(receipt_dir / "receipt.json"), **status(home)}


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
    parser.add_argument("--hermes-home", type=Path, default=Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))))
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--install", action="store_true", help="Install native official plugin + strict routing; no API session/key prompt.")
    parser.add_argument("--rollback", type=Path, help="Restore this profile's Steel receipt; refuse files customized after install.")
    parser.add_argument("--steel-source", type=Path, help="Existing checkout at the reviewed pinned Steel commit")
    parser.add_argument("--steel-ready", action="store_true", help="Deprecated; ignored. Readiness is inspected locally.")
    parser.add_argument("--personal-account", action="store_true")
    parser.add_argument("--account-transfer", action="store_true")
    parser.add_argument("--approved", action="store_true")
    parser.add_argument("--approval-note", default="")
    args = parser.parse_args(argv)
    try:
        if args.rollback:
            print(json.dumps(rollback(args.hermes_home, args.rollback), indent=2))
            return 0
        observed = install(args.hermes_home, Path(__file__).resolve().parents[1], args.steel_source) if args.install else status(args.hermes_home)
        answer = {**observed, "decision": assess(observed["ready_for_authorized_task"], args.personal_account,
                    args.account_transfer, args.approved, args.approval_note)}
        if args.steel_ready:
            answer["deprecated_flag_ignored"] = True
        print(json.dumps(answer, ensure_ascii=False, indent=2))
        return 0 if args.status or args.install or answer["decision"]["allowed"] else 2
    except Exception as exc:
        print(json.dumps({"error": type(exc).__name__, "detail": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
