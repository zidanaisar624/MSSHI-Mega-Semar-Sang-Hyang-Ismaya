"""Automatic local compression of eligible JSON tool results, with exact data checks.

Uses Hermes' supported transform_tool_result hook. No proxy, MCP, LLM call,
provider routing, user/system prompt rewriting, or background daemon is involved.
"""
from __future__ import annotations

import json
import os
from decimal import Decimal
from pathlib import Path
import shutil
import subprocess
import threading
from typing import Any


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("Ambiguous duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError("Non-finite JSON number")


def _parse(text):
    return json.loads(text, object_pairs_hook=_pairs, parse_constant=_reject_constant,
                      parse_float=Decimal)


def _canonical(value):
    # Type tags keep bool/int/decimal distinct. Decimal preserves every input
    # digit; binary float rounding must never make changed numbers look equal.
    if isinstance(value, dict):
        return ("object", tuple(sorted((key, _canonical(item)) for key, item in value.items())))
    if isinstance(value, list):
        return ("array", tuple(_canonical(item) for item in value))
    if isinstance(value, Decimal):
        return ("decimal", value)
    if value is None:
        return ("null",)
    if type(value) in (bool, int, str):
        return (type(value).__name__, value)
    raise ValueError("Unsupported JSON value")


def compress_result(result: Any, binary: str, *, status: str = "", min_chars: int = 2048,
                    max_chars: int = 262144, timeout: float = 3.0):
    """Return (replacement or None, privacy-safe metrics).

    A replacement is accepted only when both versions decode to exactly the same
    canonical JSON. Lossy text shortening, TOON conversion, duplicate keys, and
    truncated/invalid output are rejected. None leaves the original tool result.
    """
    metrics = {"outcome": "skipped", "input_bytes": 0, "output_bytes": 0, "saved_bytes": 0}
    if not isinstance(result, str) or not min_chars <= len(result) <= max_chars:
        return None, metrics
    if str(status).lower() in {"error", "failed", "failure", "cancelled", "timeout", "interrupted"}:
        return None, metrics
    try:
        original = _parse(result)
        if not isinstance(original, (dict, list)):
            return None, metrics
        if isinstance(original, dict) and (original.get("error") or original.get("success") is False):
            return None, metrics
        canonical = _canonical(original)
    except (ValueError, TypeError, RecursionError):
        return None, metrics
    before = len(result.encode("utf-8"))
    metrics.update(outcome="unchanged", input_bytes=before, output_bytes=before)
    command = str(Path(binary).expanduser()) if binary else shutil.which("llmtrim")
    if not command or not Path(command).is_file():
        metrics["outcome"] = "binary_missing"
        return None, metrics
    # This request-shaped envelope is processed locally by `compress`; it is
    # never sent to a model. Keep real provider/model settings out of this call.
    envelope = {"model": "msshi-local-compression", "messages": [
        {"role": "user", "content": "Preserve every data value exactly."},
        {"role": "tool", "tool_call_id": "msshi-local-tool", "content": result},
    ]}
    try:
        run = subprocess.run([command, "compress", "--provider", "openai"],
            input=json.dumps(envelope, ensure_ascii=False), capture_output=True, text=True,
            encoding="utf-8", errors="strict", timeout=timeout,
            env=dict(os.environ, LLMTRIM_PRESET="safe"),
            **({"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}))
        if run.returncode:
            metrics["outcome"] = "compressor_error"
            return None, metrics
        output = _parse(run.stdout)
        messages = output.get("messages", []) if isinstance(output, dict) else []
        matches = [row.get("content") for row in messages if isinstance(row, dict)
                   and row.get("role") == "tool" and row.get("tool_call_id") == "msshi-local-tool"]
        candidate = matches[-1] if len(matches) == 1 else None
        if not isinstance(candidate, str) or _canonical(_parse(candidate)) != canonical:
            metrics["outcome"] = "data_check_rejected"
            return None, metrics
        after = len(candidate.encode("utf-8"))
        if after >= before:
            return None, metrics
        metrics.update(outcome="compressed", output_bytes=after, saved_bytes=before-after)
        return candidate, metrics
    except (OSError, subprocess.SubprocessError, ValueError, TypeError, RecursionError):
        metrics["outcome"] = "compressor_error"
        return None, metrics


def register(ctx):
    lock = threading.RLock()

    def transform(tool_name: str = "", args: Any = None, result: Any = None,
                  status: str = "", **kwargs):
        if ctx.get_config("enabled", True) is False:
            return None
        # File contents, patches, skills, auth, and persona/config material must
        # retain their original presentation. Structured computation/search data
        # from other tools can be compacted after exact JSON data equality.
        name = str(tool_name).lower()
        if any(word in name for word in ("read_file", "write_file", "patch", "skill", "auth", "secret", "persona", "config")):
            return None
        try:
            replacement, metrics = compress_result(result, ctx.get_config("binary", ""), status=status,
                min_chars=max(256, int(ctx.get_config("min_chars", 2048))),
                max_chars=min(1048576, int(ctx.get_config("max_chars", 262144))),
                timeout=min(10.0, max(0.2, float(ctx.get_config("timeout_seconds", 3.0)))))
        except Exception:
            return None
        if metrics["input_bytes"]:
            # Only aggregate counts and byte sizes are persisted, never content,
            # filenames, tool arguments, session IDs, secrets, or transcripts.
            try:
                with lock:
                    totals = dict(ctx.state.get("metrics", default={}))
                    totals[metrics["outcome"]] = int(totals.get(metrics["outcome"], 0)) + 1
                    for field in ("input_bytes", "output_bytes", "saved_bytes"):
                        totals[field] = int(totals.get(field, 0)) + metrics[field]
                    totals["last_outcome"] = metrics["outcome"]
                    ctx.state.set("metrics", totals)
            except Exception:
                pass  # Diagnostics must not break a successful tool call.
        return replacement

    def status_json():
        return json.dumps({"plugin": "msshi-auto-trim", "enabled": ctx.get_config("enabled", True),
            "automatic": "eligible large JSON tool results only", "llm_calls": 0,
            "data_policy": "exact canonical JSON equality; otherwise original result",
            "metrics": ctx.state.get("metrics", default={})}, ensure_ascii=False, indent=2)

    def show_status(args):
        print(status_json())
        return 0

    def slash_status(raw_args: str = "", **kwargs):
        return status_json()

    ctx.register_hook("transform_tool_result", transform)
    ctx.register_cli_command("msshi-trim-status", "Show local automatic compression counters",
                             lambda parser: None, show_status)
    ctx.register_command("msshi-trim-status", slash_status,
                         description="Show automatic local JSON compression counters without a model call")
