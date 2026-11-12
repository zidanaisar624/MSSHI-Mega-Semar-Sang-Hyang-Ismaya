"""Offline guards for the deterministic-only Harness2 wrapper; no upstream models imported."""
import contextlib
import ctypes
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import msshi_harness2 as wrapper
import msshi_harness2_worker as worker


class Harness2Guards(unittest.TestCase):
    def test_output_cannot_touch_profiles_source_or_existing_directories(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            runtime = root / "msshi-private" / "harness2-runtime"
            for requested in (root / "profiles" / "val", root / "configs", root / "source", runtime):
                with self.assertRaises(ValueError):
                    wrapper.safe_output(runtime, requested)
            existing = runtime / "demo-runs" / "existing"
            existing.mkdir(parents=True)
            with self.assertRaises(FileExistsError):
                wrapper.safe_output(runtime, existing)
            new = runtime / "demo-runs" / "new"
            self.assertEqual(wrapper.safe_output(runtime, new), new)
            self.assertFalse(new.exists())

    def test_profile_home_maps_to_shared_root_and_configs_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertEqual(wrapper.root_home(root / "profiles" / "val"), root.resolve())
            with self.assertRaises(ValueError):
                wrapper.root_home(root / "configs")
            (root / ".git").mkdir()
            with self.assertRaises(ValueError):
                wrapper.root_home(root)

    def test_child_environment_does_not_inherit_credentials_or_agent_homes(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "synthetic-key", "GOOGLE_APPLICATION_CREDENTIALS": "synthetic-file", "HTTPS_PROXY": "synthetic-proxy", "CODEX_HOME": "synthetic-codex"}):
            env = wrapper.environment(Path(tempfile.gettempdir()) / "harness2-guard")
        for name in ("OPENAI_API_KEY", "GOOGLE_APPLICATION_CREDENTIALS", "HTTPS_PROXY", "CODEX_HOME"):
            self.assertNotIn(name, env)
        self.assertNotEqual(env["USERPROFILE"], os.environ.get("USERPROFILE"))

    def test_no_model_backed_verb_is_exposed(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                wrapper.main(["benchmark"])
        self.assertEqual(raised.exception.code, 2)
        self.assertTrue(wrapper.plan("test proposal")["proposal_only"])

    def test_ledger_guard_executes_allowed_bytes_and_rejects_altered_code(self):
        original = subprocess.Popen
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            script = root / "summarize.py"
            ledger = root / "ledger.csv"
            code = "print('allowed fixture')\n"
            script.write_text(code, encoding="utf-8")
            ledger.write_text("amount\n1\n", encoding="utf-8")
            try:
                guarded = worker.ledger_process_guard(root, {code})
                result = subprocess.run([sys.executable, str(script), str(ledger)], capture_output=True, text=True, check=True)
                self.assertEqual(result.stdout.strip(), "allowed fixture")
                script.write_text("raise RuntimeError('altered')\n", encoding="utf-8")
                with self.assertRaises(PermissionError):
                    guarded([sys.executable, str(script), str(ledger)])
                with self.assertRaises(PermissionError):
                    guarded(["gcloud", "auth", "list"])
            finally:
                subprocess.Popen = original

    @unittest.skipUnless(os.name == "nt", "Windows job-object descendant cleanup")
    def test_timeout_kills_parent_and_descendant(self):
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        kernel.WaitForSingleObject.restype = wintypes.DWORD
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "tmp").mkdir()
            ids = root / "pids.json"
            program = root / "parent.py"
            program.write_text("import json,os,subprocess,sys,time\nfrom pathlib import Path\nchild=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)'])\nPath(sys.argv[1]).write_text(json.dumps([os.getpid(),child.pid]))\ntime.sleep(60)\n", encoding="utf-8")
            with self.assertRaises(subprocess.TimeoutExpired):
                wrapper.owned_run([sys.executable, "-I", "-B", str(program), str(ids)], wrapper.environment(root), 3, cwd=root)
            self.assertTrue(ids.is_file(), "owned parent did not start its descendant")
            for pid in json.loads(ids.read_text()):
                handle = kernel.OpenProcess(0x100000, False, pid)
                if handle:
                    try:
                        self.assertEqual(kernel.WaitForSingleObject(handle, 5000), 0, f"orphan process {pid}")
                    finally:
                        kernel.CloseHandle(handle)
                else:
                    self.assertEqual(ctypes.get_last_error(), 87)


if __name__ == "__main__":
    unittest.main()
