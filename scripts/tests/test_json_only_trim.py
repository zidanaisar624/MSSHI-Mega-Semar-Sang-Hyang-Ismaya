"""Local deterministic compaction checks; optional installed binary never calls a model."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


hook = load('trim_test_hook', ROOT / 'hermes_plugins/msshi-auto-trim/__init__.py')
wrapper = load('trim_test_wrapper', ROOT / 'scripts/msshi_llmtrim.py')


class JsonOnlyTrimTests(unittest.TestCase):
    def setUp(self):
        self.data = {'rows': [{'id': i, 'value': i * 10, 'label': 'retained exact string', 'enabled': True} for i in range(100)]}
        self.text = json.dumps(self.data, indent=4)

    def test_toml_copies_match_and_disable_structural_rewrites(self):
        canonical = (ROOT / 'hermes_plugins/msshi-auto-trim/json-only.toml').read_bytes()
        self.assertEqual(canonical, (ROOT / 'scripts/msshi_llmtrim_json_only.toml').read_bytes())
        self.assertIn(b'serialize = false', canonical)
        self.assertIn(b'dedup = false', canonical)
        self.assertNotIn(b'preset =', canonical)

    def test_hook_pins_child_config_without_mutating_parent_env(self):
        compact = json.dumps(self.data, separators=(',', ':'))
        output = json.dumps({'messages': [{'role': 'tool', 'tool_call_id': 'msshi-local-tool', 'content': compact}]})
        def fake_run(command, **kwargs):
            self.assertNotIn('LLMTRIM_PRESET', kwargs['env'])
            self.assertTrue(kwargs['env']['LLMTRIM_CONFIG'].endswith('json-only.toml'))
            self.assertEqual('0', kwargs['env']['LLMTRIM_CAPTURE_MAX_MB'])
            return subprocess.CompletedProcess(command, 0, output, '')
        with mock.patch.dict(os.environ, {'LLMTRIM_PRESET': 'safe', 'LLMTRIM_CONFIG': 'user-custom.toml'}), mock.patch.object(hook.subprocess, 'run', side_effect=fake_run):
            result, metrics = hook.compress_result(self.text, __file__)
            self.assertEqual('safe', os.environ['LLMTRIM_PRESET'])
            self.assertEqual('user-custom.toml', os.environ['LLMTRIM_CONFIG'])
        self.assertEqual('compressed', metrics['outcome'])
        self.assertEqual(self.data, json.loads(result))

    def test_safe_preset_toon_shape_is_rejected(self):
        # Upstream safe may replace an array with a TOON string: reversible
        # encoding, but not the exact JSON structure required by this adapter.
        altered = json.dumps({'rows': '[100]{id,value,label,enabled}:\n  0,0,label,true'})
        output = json.dumps({'messages': [{'role': 'tool', 'tool_call_id': 'msshi-local-tool', 'content': altered}]})
        with mock.patch.object(hook.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, output, '')):
            result, metrics = hook.compress_result(self.text, __file__)
        self.assertIsNone(result)
        self.assertEqual('data_check_rejected', metrics['outcome'])

    def test_hook_errors_and_duplicate_keys_do_not_invoke_binary(self):
        with mock.patch.object(hook.subprocess, 'run') as run:
            self.assertIsNone(hook.compress_result(self.text, __file__, status='error')[0])
            self.assertIsNone(hook.compress_result('{"x":1,"x":2}' + ' ' * 3000, __file__)[0])
            run.assert_not_called()

    def test_wrapper_rejects_changed_data_and_returns_original(self):
        payload = json.dumps({'model': 'unchanged', 'messages': [{'role': 'tool', 'content': self.text}]}).encode()
        bad = json.dumps({'model': 'CHANGED', 'messages': [{'role': 'tool', 'content': '{}'}]}).encode()
        with mock.patch.object(wrapper.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, bad, b'')):
            self.assertEqual(payload, wrapper.compress(payload, __file__, 'openai'))
        with mock.patch.object(wrapper.subprocess, 'run', side_effect=subprocess.TimeoutExpired('binary', 1)):
            self.assertEqual(payload, wrapper.compress(payload, __file__, 'openai'))

    def test_wrapper_accepts_only_smaller_equivalent_tool_json(self):
        payload = json.dumps({'model': 'unchanged', 'messages': [{'role': 'tool', 'content': self.text}]}).encode()
        compact = json.dumps({'model': 'unchanged', 'messages': [{'role': 'tool', 'content': json.dumps(self.data, separators=(',', ':'))}]}, separators=(',', ':')).encode()
        with mock.patch.object(wrapper.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, compact, b'')):
            self.assertEqual(compact, wrapper.compress(payload, __file__, 'openai'))

    @unittest.skipUnless(os.environ.get('MSSHI_TEST_LLMTRIM_BINARY'), 'Set MSSHI_TEST_LLMTRIM_BINARY for synthetic local-binary test')
    def test_real_binary_exact_json_savings_and_safe_regression(self):
        binary = os.environ['MSSHI_TEST_LLMTRIM_BINARY']
        with tempfile.TemporaryDirectory(prefix='msshi-trim-fixture-') as td:
            env = {'LLMTRIM_DB_PATH': str(Path(td) / 'synthetic-only.db'), 'LLMTRIM_PRESET': 'safe', 'LLMTRIM_NO_UPDATE_CHECK': '1', 'LLMTRIM_CAPTURE_MAX_MB': '0'}
            with mock.patch.dict(os.environ, env):
                result, metrics = hook.compress_result(self.text, binary)
                self.assertEqual('compressed', metrics['outcome'])
                self.assertEqual(hook._canonical(hook._parse(self.text)), hook._canonical(hook._parse(result)))
                self.assertGreater(metrics['saved_bytes'], 0)
                payload = json.dumps({'model': 'msshi-local-compression', 'messages': [{'role': 'tool', 'tool_call_id': 'fixture', 'content': self.text}]}).encode()
                compact = wrapper.compress(payload, binary, 'openai')
                self.assertLess(len(compact), len(payload))
                self.assertEqual(wrapper._canonical(wrapper._parse(payload)), wrapper._canonical(wrapper._parse(compact)))
                # Demonstrate why the former 'safe' preset was rejected.
                raw = subprocess.run([binary, 'compress', '--provider', 'openai'], input=payload, capture_output=True, timeout=15)
                self.assertEqual(0, raw.returncode)
                old = next(row['content'] for row in json.loads(raw.stdout)['messages'] if row.get('role') == 'tool')
                self.assertIsInstance(json.loads(old)['rows'], str)


if __name__ == '__main__':
    unittest.main()
