"""Fail-closed Steel routing using Hermes' supported execution middleware.

No core edits, MCP registration, startup network request, or personal-profile copy.
Each browser_exec batch owns one remote session and releases it in finally.
"""
from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path
import sys
import uuid


def result(**value):
    return json.dumps(value, ensure_ascii=False)


def _provider(home):
    """Load the pinned official provider, with Hermes' profile-scoped secret API."""
    root = Path(home) / "plugins" / "browser-steel"
    name = "_msshi_official_steel_" + hashlib.sha256(str(root).encode()).hexdigest()[:16]
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, root / "__init__.py",
                                                    submodule_search_locations=[str(root)])
        if spec is None or spec.loader is None:
            raise RuntimeError("Official browser-steel source is missing")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    from importlib import import_module
    official = import_module(name + ".provider")
    settings = import_module(name + ".config")
    settings.set_session_override("use_proxy", False)
    settings.set_session_override("solve_captcha", False)
    from agent.secret_scope import get_secret

    class ScopedSteel(official.SteelBrowserProvider):
        def _api_key(self):
            key = (get_secret("STEEL_API_KEY") or "").strip()
            if key:
                return key
            if official.is_default_cloud_url():
                raise ValueError("STEEL_API_KEY belum tersedia pada profil ini; masukkan lewat .env privat Hermes.")
            return None

    return ScopedSteel()


def _drive(cdp, code, timeout_s, task_id, runner=None):
    """A child-only explicit CDP bypasses the native cloud-to-local fallback."""
    from tools import browser_use_cli as native
    from tools.browser_harness_dirs import fit_default_socket_dir
    cmd = native._find_cli()
    if not cmd:
        raise RuntimeError("browser-harness is not installed in this Hermes runtime")
    env = native._base_subprocess_env()
    for name in ("BU_CDP_URL", "BROWSER_CDP_URL", "BU_AUTOSPAWN", "BU_BROWSER_ID",
                 "BROWSER_USE_API_KEY"):
        env.pop(name, None)
    env["BU_CDP_WS"] = cdp
    env["BU_NAME"] = "msshi-steel-" + uuid.uuid4().hex[:20]
    env["BH_TELEMETRY"] = "0"
    env["ANONYMIZED_TELEMETRY"] = "false"
    workspace = native._workspace_dir(task_id)
    if workspace:
        env["BH_AGENT_WORKSPACE"] = workspace
    fit_default_socket_dir(env)
    run = runner or native._run_cli_killing_process_group
    try:
        proc = run(cmd, code, env, max(5, min(int(timeout_s), 180)))
        from agent.redact import redact_sensitive_text
        return {"ok": proc.returncode == 0, "stdout": redact_sensitive_text(proc.stdout[-64000:]),
                "stderr": redact_sensitive_text(proc.stderr[-4000:]), "session_persistence": "one_batch"}
    finally:
        # The UUID daemon belongs only to this call. Never stop shared/user daemons.
        try:
            run(cmd + ["--reload"], "", env, 10)
        except Exception:
            pass  # remote release below and server hard timeout still apply


def steel_exec(args, *, home, task_id="", provider_factory=None, driver=None):
    if args.get("local"):
        return result(error="Untuk akun personal gunakan msshi_personal_browser dengan persetujuan berscope. Tidak ada penyalinan profil otomatis.")
    code = args.get("code", "")
    if not isinstance(code, str) or not code.strip():
        return result(error="Pass a nonempty browser Python code batch.")
    provider = None
    session_id = None
    answer = {}
    try:
        # Version guard: refuse before a billable create if the harness API changed.
        from tools import browser_use_cli as native
        if not all(callable(getattr(native, n, None)) for n in
                   ("_find_cli", "_base_subprocess_env", "_run_cli_killing_process_group")) or not native._find_cli():
            return result(error="Unsupported Hermes browser-harness API; update MSSHI adapter first.", local_fallback=False)
        provider = (provider_factory or _provider)(home)
        provider._api_key()  # cheap configuration check; no network
        info = provider.create_session("msshi_" + str(task_id or "task"))
        session_id = info.get("bb_session_id")
        cdp = info.get("cdp_url")
        if not session_id or not isinstance(cdp, str) or not cdp.startswith(("ws://", "wss://")):
            raise RuntimeError("Steel returned invalid session metadata")
        answer = (driver or _drive)(cdp, code, args.get("timeout_s", 90), task_id)
        answer.update(backend="steel", local_fallback=False)
        if info.get("session_viewer_url"):
            answer["viewer"] = info["session_viewer_url"]
    except Exception as exc:
        # Never let middleware error handling proceed to the original local-fallback tool.
        answer = {"error": "Steel task failed: " + type(exc).__name__,
                  "setup_hint": "Check private STEEL_API_KEY, endpoint and service quota; no local browser was launched.",
                  "backend": "steel", "local_fallback": False, "connected": False}
    finally:
        if provider is not None and session_id:
            try:
                answer["remote_session_released"] = bool(provider.close_session(session_id))
            except Exception:
                answer["remote_session_released"] = False
    return result(**answer)


def pre_tool_call(tool_name, args=None, **kw):
    args = args or {}
    if tool_name == "browser_exec":
        if args.get("local"):
            return {"action": "block", "message": "Use msshi_personal_browser for scoped personal-account approval; native local/profile-copy route is disabled."}
        return {"action": "approve", "message": "Izinkan satu batch browsing Steel untuk tugas ini? Sesi memakai kuota/biaya akun Steel, tanpa proxy/CAPTCHA berbayar dan tanpa akun personal. Sesi akan dilepas setelah batch.",
                "rule_key": "msshi-steel-" + str(kw.get("tool_call_id") or uuid.uuid4().hex)}
    if tool_name == "msshi_personal_browser":
        fields = ("site", "account", "purpose", "access", "duration", "code")
        if any(not isinstance(args.get(k), str) or not args[k].strip() for k in fields):
            return {"action": "block", "message": "Specify site, account, purpose, access, duration and code before requesting personal-browser consent."}
        scope = {k: args[k] for k in fields if k != "code"}
        return {"action": "approve", "message": "Persetujuan akses sesi personal yang sudah terhubung (tanpa menyalin cookie/profil): " + json.dumps(scope, ensure_ascii=False),
                "rule_key": "msshi-personal-" + str(kw.get("tool_call_id") or uuid.uuid4().hex)}
    if tool_name.startswith("browser_") and tool_name != "browser_exec":
        return {"action": "block", "message": "MSSHI strict route: use browser_exec (Steel) or msshi_personal_browser (scoped approval). Native cloud/local fallback is disabled."}
    if tool_name in {"steel_scrape", "steel_session_options"}:
        return {"action": "block", "message": "Use strict browser_exec; direct scrape/paid proxy and CAPTCHA options are disabled by MSSHI's current no-credit-test policy."}


def personal_exec(args, task_id="", **kw):
    try:
        # Only an existing operator-attached endpoint. Never discover/launch/copy Chrome.
        from tools.browser_session_cdp import get_cdp_override
        from tools.browser_session_cdp import resolve_cdp_override
        endpoint = get_cdp_override()
        if not endpoint:
            return result(error="No existing personal-browser CDP is attached. After scoped consent, attach manually with /browser connect. No browser was opened or copied.")
        cdp = resolve_cdp_override(endpoint)
        return result(backend="approved-personal-cdp", **_drive(cdp, args["code"], args.get("timeout_s", 90), task_id))
    except Exception as exc:
        return result(error="Personal browser unavailable: " + type(exc).__name__)


def register(ctx):
    home = str(Path(ctx.manifest.path).parent.parent)
    def gate(tool_name, args=None, **kw):
        if tool_name == "browser_exec" and not (args or {}).get("local"):
            try:
                _provider(home)._api_key()
            except Exception:
                return {"action": "block", "message": "Steel belum siap: masukkan STEEL_API_KEY melalui .env privat profil atau konfigurasi endpoint resmi. Tidak ada sesi, kuota, atau fallback Chrome yang dipakai."}
        return pre_tool_call(tool_name, args, **kw)
    ctx.register_hook("pre_tool_call", gate)

    def execute(tool_name, args, next_call, task_id="", **kw):
        if tool_name == "browser_exec":
            return steel_exec(args, home=home, task_id=task_id)
        return next_call(args)

    ctx.register_middleware("tool_execution", execute)
    props = {k: {"type": "string"} for k in ("site", "account", "purpose", "access", "duration", "code")}
    ctx.register_tool(name="msshi_personal_browser", toolset="browser", schema={
        "name": "msshi_personal_browser", "description": "Use an already attached personal browser only after fresh scoped human approval; no profile/cookie copying. Explain site/account/purpose/access/duration first.",
        "parameters": {"type": "object", "properties": props, "required": list(props)}},
        handler=personal_exec, requires_env=[])
    ctx.register_system_prompt_section("msshi.browser", "Use browser_exec for general browsing via Steel. Each call is a fresh remote session: batch all steps for one subtask into that call; do not assume tabs persist. Missing Steel credentials or errors stop the task; never switch to local Chrome. For accounts already logged in locally, explain scope and use msshi_personal_browser's human approval. Session transfer/login setup requires separate user consent; never extract cookies/passwords/profile. Do not call paid proxy/CAPTCHA or direct steel_scrape.", max_chars=1200)
