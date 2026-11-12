import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

path = Path(__file__).resolve().parents[1] / "hermes_plugins" / "msshi-steel-policy" / "__init__.py"
if not path.is_file():
    path = Path(__file__).with_name("policy_plugin.py")
spec = importlib.util.spec_from_file_location("msshi_steel_test", path)
plugin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plugin)


class Provider:
    def __init__(self, fail=False):
        self.closed = []
        self.fail = fail
    def _api_key(self):
        return "synthetic-not-a-secret"
    def create_session(self, task):
        if self.fail:
            raise RuntimeError("synthetic quota failure")
        return {"bb_session_id": "owned-session", "cdp_url": "wss://synthetic.invalid/", "session_viewer_url": "https://synthetic.invalid/viewer"}
    def close_session(self, sid):
        self.closed.append(sid)
        return True


class Tests(unittest.TestCase):
    def setUp(self):
        native = ModuleType("tools.browser_use_cli")
        native._find_cli = lambda: ["synthetic-python", "-m", "browser_harness.run"]
        native._base_subprocess_env = lambda: {"BU_CDP_URL": "http://personal.invalid", "BU_AUTOSPAWN": "1", "BROWSER_USE_API_KEY": "synthetic"}
        native._run_cli_killing_process_group = lambda *a: None
        native._workspace_dir = lambda _: None
        tools = ModuleType("tools")
        tools.browser_use_cli = native
        dirs = ModuleType("tools.browser_harness_dirs")
        dirs.fit_default_socket_dir = lambda _: None
        redact = ModuleType("agent.redact")
        redact.redact_sensitive_text = lambda text: text
        agent = ModuleType("agent")
        agent.redact = redact
        self.scope = patch.dict(sys.modules, {"tools": tools, "tools.browser_use_cli": native,
                    "tools.browser_harness_dirs": dirs, "agent": agent, "agent.redact": redact})
        self.scope.start()
        self.addCleanup(self.scope.stop)

    def test_native_personal_copy_always_blocked(self):
        self.assertEqual(plugin.pre_tool_call("browser_exec", {"local": True})["action"], "block")

    def test_personal_needs_all_scope_and_real_gate(self):
        self.assertEqual(plugin.pre_tool_call("msshi_personal_browser", {"site": "example.org"})["action"], "block")
        args = dict.fromkeys(("site", "account", "purpose", "access", "duration", "code"), "synthetic")
        self.assertEqual(plugin.pre_tool_call("msshi_personal_browser", args)["action"], "approve")

    def test_public_native_approval_not_boolean_claim(self):
        decision = plugin.pre_tool_call("browser_exec", {"code": "print(1)", "approved": True})
        self.assertEqual(decision["action"], "approve")

    def test_provider_failure_never_runs_driver(self):
        called = []
        answer = json.loads(plugin.steel_exec({"code": "print(1)"}, home="fixture", provider_factory=lambda _: Provider(True), driver=lambda *a: called.append(a)))
        self.assertFalse(answer["connected"])
        self.assertFalse(answer["local_fallback"])
        self.assertEqual(called, [])

    def test_driver_failure_releases_only_owned_session(self):
        provider = Provider()
        def fail(*args):
            raise TimeoutError("fixture timeout")
        answer = json.loads(plugin.steel_exec({"code": "print(1)"}, home="fixture", provider_factory=lambda _: provider, driver=fail))
        self.assertEqual(provider.closed, ["owned-session"])
        self.assertTrue(answer["remote_session_released"])
        self.assertFalse(answer["local_fallback"])

    def test_normal_batch_releases_and_returns_backend(self):
        provider = Provider()
        answer = json.loads(plugin.steel_exec({"code": "print(1)"}, home="fixture", provider_factory=lambda _: provider, driver=lambda *a: {"ok": True, "stdout": "1"}))
        self.assertEqual(answer["backend"], "steel")
        self.assertTrue(answer["remote_session_released"])
        self.assertEqual(provider.closed, ["owned-session"])

    def test_unrelated_tool_untouched(self):
        self.assertIsNone(plugin.pre_tool_call("mcp__gitlab__get_project", {}))

    def test_child_cdp_only_and_daemon_cleanup(self):
        calls = []
        def run(cmd, code, env, timeout):
            calls.append((cmd, dict(env)))
            return SimpleNamespace(returncode=0, stdout="synthetic", stderr="")
        answer = plugin._drive("wss://steel.invalid/", "print(1)", 90, "test", runner=run)
        self.assertTrue(answer["ok"])
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[1][0][-1], "--reload")
        for _, env in calls:
            self.assertEqual(env["BU_CDP_WS"], "wss://steel.invalid/")
            self.assertNotIn("BU_CDP_URL", env)
            self.assertNotIn("BU_AUTOSPAWN", env)
            self.assertNotIn("BROWSER_USE_API_KEY", env)
            self.assertTrue(env["BU_NAME"].startswith("msshi-steel-"))


if __name__ == "__main__":
    unittest.main()
