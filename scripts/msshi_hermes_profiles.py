"""Adaptive Hermes Desktop profile synchronization for MSSHI (before, during, and after Hermes runs)."""
from __future__ import annotations

import ctypes
import hashlib
import importlib.util
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid

PROFILE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
NO_BUNDLED_SKILLS_MARKER = ".no-bundled-skills"
STOCK_HERMES_SOUL_PREFIX = "You are Hermes Agent, built by Nous Research."
STOCK_HERMES_SOUL = (
    "You are Hermes Agent, built by Nous Research. Be direct: match the length of your reply to the weight of "
    "the ask — a one-line question gets a one-line answer, and finished work gets a short report of what "
    "changed, what's verified, and what's left, never a replay of the process. No filler (\"Great question,\" "
    "\"I'd be happy to\"), no restating the request back, no re-summarizing what you already said, no narrating "
    "tool calls the user can see. Plain claims over adjectives; when unsure, say so plainly. Agree because it's "
    "right, not because the user said it. Depth is earned — give it when the user asks for detail, teaches, or "
    "the stakes demand it, not by default."
)
_PLACEHOLDER_ENV = "# Per-profile secrets for this Hermes profile.\n"
_HERMES_PROFILE_DIRS = ("memories", "sessions", "skills", "skins", "logs", "plans", "workspace", "cron", "home")
_STRONG_HERMES_MARKERS = ("config.yaml", "state.db", "hermes-agent", "auth.json", ".env")
_ALL_HERMES_MARKERS = (*_STRONG_HERMES_MARKERS, "profiles", "skills")
_NON_COPY_ENV_PREFIXES = (
    "TELEGRAM_", "DISCORD_", "EMAIL_", "SLACK_", "WHATSAPP_", "SIGNAL_",
    "FEISHU_", "LARK_", "MATRIX_", "WECOM_", "QQ_", "DINGTALK_", "TWILIO_",
    "SMS_", "GATEWAY_RELAY_", "HOME_ASSISTANT_",
    "GMAIL_", "GOOGLE_CLIENT_", "GOOGLE_OAUTH_", "GCAL_", "GDRIVE_", "OAUTH_",
    "ZOOM_", "YOUTUBE_", "NOTEBOOKLM_", "NEXTCLOUD_", "DROPBOX_",
)
_NON_COPY_ENV_EXACT = {
    "GATEWAY_ALLOW_ALL_USERS",
    "GATEWAY_ALLOWED_USERS",
    "HOME_CHANNEL",
    "ALLOWED_USERS",
    "HERMES_DASHBOARD_SESSION_TOKEN",
    "HERMES_HOME", "HERMES_PROFILE", "HERMES_DEFAULT_HOME", "MSSHI_HOME",
    "TERMINAL_CWD", "PYTHONPATH", "PYTHONHOME",
}
_YAML_AMBIGUOUS = re.compile(r"^(?:true|false|yes|no|on|off|null|~|[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)$", re.I)
TEAM_ROLE_IDS = ("yukino", "shizuka", "val", "kiki-chii", "shikaku")


def team_role_profiles(hermes_home: Path) -> dict[str, str]:
    """Logical roles mapped to real native IDs, never a synthetic Desktop roster."""
    path = hermes_home / "msshi-runtime" / "team-layout.json"
    if path.is_file() and not path.is_symlink() and path.stat().st_size <= 65536:
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            expected = {name: name for name in TEAM_ROLE_IDS}
            if data.get("default_bot") == "yukino":
                expected["yukino"] = "default"
            if data.get("schema") == 1 and data.get("roles") == expected:
                return expected
        except (OSError, ValueError, AttributeError):
            pass
    return {name: name for name in TEAM_ROLE_IDS}


def resolve_default_bot(hermes_home: Path, requested: str = "auto") -> str:
    """Fresh/stock installs use actual default as Yukino; existing choices are retained."""
    if requested not in {"auto", "yukino", "keep-hermes"}:
        raise ValueError(f"Unknown default bot mode: {requested}")
    if requested != "auto":
        return requested
    layout = hermes_home / "msshi-runtime" / "team-layout.json"
    if layout.is_file() and not layout.is_symlink():
        return "yukino" if team_role_profiles(hermes_home)["yukino"] == "default" else "keep-hermes"
    # A legacy named roster is an existing user choice, including deleted profiles.
    if live_named_profiles(hermes_home) or any((hermes_home / "profiles" / name).exists() for name in TEAM_ROLE_IDS):
        return "keep-hermes"
    meta = load_yaml_mapping(hermes_home / "profile.yaml") if (hermes_home / "profile.yaml").is_file() else {}
    generic = {"", "hermes", "default", "yukino", "yukino yukinoshita"}
    ui = meta.get("ui_meta") if isinstance(meta.get("ui_meta"), dict) else {}
    bots = ui.get("hermes-bots") if isinstance(ui.get("hermes-bots"), dict) else {}
    if any(str(value or "").strip().lower() not in generic for value in (meta.get("display_name"), bots.get("title"))):
        return "keep-hermes"
    if not is_stock_hermes_soul(hermes_home / "SOUL.md"):
        # Older releases could already have adopted default as Yukino.
        return "yukino" if str(meta.get("display_name", "")).lower() in {"yukino", "yukino yukinoshita"} else "keep-hermes"
    return "yukino"


def record_team_layout(hermes_home: Path, default_bot: str, *, transaction=None) -> Path:
    mode = resolve_default_bot(hermes_home, default_bot)
    roles = {name: ("default" if name == "yukino" and mode == "yukino" else name) for name in TEAM_ROLE_IDS}
    path = _confined(hermes_home, hermes_home / "msshi-runtime" / "team-layout.json")
    content = (json.dumps({"schema": 1, "default_bot": mode, "roles": roles}, indent=2) + "\n").encode()
    if transaction is not None:
        transaction.write(path, content)
    elif not path.is_file() or path.read_bytes() != content:
        _atomic_write_bytes(path, content)
    return path


def hide_legacy_named_yukino(hermes_home: Path, *, transaction=None) -> dict:
    """Explicit default-Yukino switch: hide the old alias without deleting user data."""
    if team_role_profiles(hermes_home)["yukino"] != "default":
        raise ValueError("Record the default-Yukino layout before hiding its legacy alias")
    folder = _confined(hermes_home, hermes_home / "profiles" / "yukino")
    if not folder.is_dir():
        return {"hidden": False, "reason": "no_legacy_named_yukino", "receipt": None}
    tx = transaction or ProfileTransaction(hermes_home)
    marker = _confined(hermes_home, hermes_home / "profiles" / ".deleted" / "yukino")
    changed = False if marker.exists() else tx.write(marker, b"MSSHI: Yukino role now uses native default; all named profile data preserved.\n")
    # Native active_profile is a plain ID file. Repoint only this alias; never configs.
    active = hermes_home / "active_profile"
    if active.is_file() and active.read_text(encoding="utf-8-sig").strip() == "yukino":
        tx.write(active, b"default\n")
    return {"hidden": True, "changed": changed, "tombstone": str(marker),
            "receipt": tx.commit() if transaction is None else None}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def valid_profile_id(name: str) -> bool:
    return bool(name and PROFILE_ID_RE.fullmatch(name))


def normalize_hermes_root(value: str | Path) -> Path:
    resolved = Path(value).expanduser().absolute()
    if resolved.parent.name.lower() == "profiles" and resolved.parent.parent != resolved.parent:
        return resolved.parent.parent
    return resolved


def resolve_target_hermes_home(target: str | Path) -> Path:
    resolved = Path(target).expanduser().absolute()
    if resolved.name.lower() in {"profiles", "skills"}:
        return resolved.parent
    return normalize_hermes_root(resolved)


def _read_windows_registry_hermes_home() -> str | None:
    if os.name != "nt" or os.environ.get("MSSHI_IGNORE_REGISTRY_HERMES_HOME"):
        return None
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, "HERMES_HOME")
        cleaned = str(value or "").strip()
        return cleaned or None
    except OSError:
        return None


def persist_windows_hermes_home(home: Path) -> bool:
    """Persist HERMES_HOME into HKCU\\Environment so Hermes Desktop & CLI find D:\\HermesData."""
    if os.name != "nt" or os.environ.get("MSSHI_IGNORE_REGISTRY_HERMES_HOME"):
        return False
    try:
        import winreg
        existing = _read_windows_registry_hermes_home()
        if existing:
            return False
        target = str(home)
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "HERMES_HOME", 0, winreg.REG_SZ, target)
        os.environ["HERMES_HOME"] = target
        try:
            ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001A, 0, "Environment", 0x0002, 1000, None)
        except Exception:
            pass
        return True
    except OSError:
        return False


def has_writable_drive_d(probe_write: bool = False, env: dict[str, str] | None = None) -> bool:
    if os.name != "nt":
        return False
    environ = env if env is not None else os.environ
    drive_spec = environ.get("MSSHI_WINDOWS_D_DRIVE", "D:/")
    if not drive_spec:
        return False
    drive = Path(drive_spec)
    if not drive.exists():
        return False
    if "MSSHI_WINDOWS_D_DRIVE" not in environ:
        try:
            drive_type = ctypes.windll.kernel32.GetDriveTypeW("D:\\")
            if drive_type not in (2, 3, 4):
                return False
        except Exception:
            return False
    try:
        minimum = max(0, int(environ.get('MSSHI_MIN_FREE_GIB', '2'))) * 2**30
        if shutil.disk_usage(drive).free < minimum:
            return False
    except (OSError, ValueError):
        return False
    if not probe_write:
        return os.access(drive, os.W_OK)
    hermes_d = Path(environ.get("MSSHI_WINDOWS_D_ROOT") or (drive / "HermesData"))
    probe_dir = hermes_d if hermes_d.is_dir() else drive
    probe = probe_dir / f".msshi-probe-{os.getpid()}"
    try:
        probe.write_text("", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def is_hermes_dir(path: Path, strict: bool = False) -> bool:
    if not path.is_dir() or path.is_symlink():
        return False
    markers = _STRONG_HERMES_MARKERS if strict else _ALL_HERMES_MARKERS
    return any((path / marker).exists() for marker in markers)


def is_hermes_initialized(home: Path) -> bool:
    return any((home / name).is_file() for name in ("config.yaml", ".env", "state.db"))


def resolve_hermes_home(
    explicit: str | Path | None = None,
    *,
    env: dict[str, str] | None = None,
    create_adaptive: bool = False,
    persist_windows_env: bool = False,
) -> Path:
    """Resolve Hermes home consistently before, during, and after Hermes opens (adaptive C:/D:)."""
    if explicit is not None and str(explicit).strip():
        return normalize_hermes_root(explicit)
    environ = env if env is not None else os.environ
    if val := (environ.get("HERMES_HOME") or "").strip():
        return normalize_hermes_root(val)
    if val := (environ.get("HERMES_DESKTOP_USER_DATA_DIR") or "").strip():
        return Path(val).expanduser().absolute() / "hermes-home"
    if not environ.get("MSSHI_IGNORE_REGISTRY_HERMES_HOME") and os.name == "nt" and "HERMES_HOME" not in environ:
        if reg := _read_windows_registry_hermes_home():
            return normalize_hermes_root(reg)

    suffix = environ.get("HERMES_DATA_DIR_SUFFIX", "")
    user_home = Path(environ.get("USERPROFILE") or environ.get("HOME") or str(Path.home())).expanduser()
    if os.name == "nt":
        local_app_data = Path((environ.get("LOCALAPPDATA") or "").strip() or (user_home / "AppData" / "Local")).expanduser()
        d_drive = environ.get("MSSHI_WINDOWS_D_DRIVE", "D:/")
        d_root = Path(environ["MSSHI_WINDOWS_D_ROOT"]) if environ.get("MSSHI_WINDOWS_D_ROOT") else (
            Path(d_drive) / "HermesData" if d_drive else None
        )
        candidates = [c for c in (d_root, local_app_data / "HermesData", local_app_data / f"hermes{suffix}", user_home / "HermesData", user_home / f".hermes{suffix}") if c is not None]
    else:
        candidates = [user_home / f".hermes{suffix}", user_home / "HermesData"]

    for strict in (True, False):
        for candidate in candidates:
            if is_hermes_dir(candidate, strict=strict):
                return candidate.absolute()

    if os.name == "nt":
        if not suffix and has_writable_drive_d(probe_write=create_adaptive, env=environ) and d_root is not None:
            chosen = d_root.absolute()
            if create_adaptive and persist_windows_env and env is None and not environ.get("MSSHI_IGNORE_REGISTRY_HERMES_HOME"):
                chosen.mkdir(parents=True, exist_ok=True)
                persist_windows_hermes_home(chosen)
            return chosen
        chosen = (local_app_data / (f"hermes{suffix}" if suffix else "HermesData")).absolute()
        if create_adaptive and persist_windows_env and env is None and not environ.get("MSSHI_IGNORE_REGISTRY_HERMES_HOME"):
            chosen.mkdir(parents=True, exist_ok=True)
            persist_windows_hermes_home(chosen)
        return chosen
    return (user_home / f".hermes{suffix}").absolute()


def _strip_inline_comment(text: str) -> str:
    quote = None
    escaped = False
    for index, ch in enumerate(text):
        if escaped:
            escaped = False
            continue
        if quote == '"' and ch == "\\":
            escaped = True
            continue
        if ch in ('"', "'"):
            if quote is None:
                quote = ch
            elif quote == ch:
                quote = None
        elif ch == "#" and quote is None and (index == 0 or text[index - 1].isspace()):
            return text[:index].rstrip()
    return text.rstrip()


def _parse_scalar(raw: str):
    value = raw.strip()
    if not value or value in {"~", "null", "Null", "NULL"}:
        return None
    if value in {"true", "True", "TRUE"}:
        return True
    if value in {"false", "False", "FALSE"}:
        return False
    if value == "{}":
        return {}
    if value == "[]":
        return []
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
    if len(value) >= 2 and value[0] == "'" and value[-1] == "'":
        return value[1:-1].replace("''", "'")
    if re.fullmatch(r"[+-]?\d+", value):
        try:
            return int(value)
        except ValueError:
            return value
    if re.fullmatch(r"[+-]?(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?", value):
        try:
            return float(value)
        except ValueError:
            return value
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(part) for part in inner.split(",")]
    return value


def _split_key_value(line: str) -> tuple[str, str | None] | None:
    quote = None
    escaped = False
    for index, ch in enumerate(line):
        if escaped:
            escaped = False
            continue
        if quote == '"' and ch == "\\":
            escaped = True
            continue
        if ch in ('"', "'"):
            if quote is None:
                quote = ch
            elif quote == ch:
                quote = None
        elif ch == ":" and quote is None:
            if index + 1 == len(line) or line[index + 1].isspace():
                key_raw = line[:index].strip()
                key = str(_parse_scalar(key_raw))
                rest = line[index + 1:].strip()
                return key, (rest if rest else None)
    return None


def _tokenize_yaml_lines(text: str) -> list[tuple[int, str]]:
    tokens: list[tuple[int, str]] = []
    for raw_line in text.lstrip("\ufeff").splitlines():
        stripped = _strip_inline_comment(raw_line)
        if not stripped.strip():
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        tokens.append((indent, stripped.strip()))
    return tokens


def _parse_yaml_block(tokens: list[tuple[int, str]], idx: int, indent: int):
    if idx >= len(tokens):
        return {}, idx
    if tokens[idx][1].startswith("- ") or tokens[idx][1] == "-":
        items = []
        while idx < len(tokens) and tokens[idx][0] == indent and (tokens[idx][1].startswith("- ") or tokens[idx][1] == "-"):
            content = tokens[idx][1][1:].strip()
            idx += 1
            if not content:
                if idx < len(tokens) and tokens[idx][0] > indent:
                    val, idx = _parse_yaml_block(tokens, idx, tokens[idx][0])
                    items.append(val)
                else:
                    items.append(None)
                continue
            kv = _split_key_value(content)
            if kv is not None:
                key, rest = kv
                entry: dict[str, object] = {}
                if rest is not None:
                    entry[key] = _parse_scalar(rest)
                elif idx < len(tokens) and tokens[idx][0] > indent:
                    entry[key], idx = _parse_yaml_block(tokens, idx, tokens[idx][0])
                else:
                    entry[key] = None
                if idx < len(tokens) and tokens[idx][0] > indent:
                    extra, idx = _parse_yaml_block(tokens, idx, tokens[idx][0])
                    if isinstance(extra, dict):
                        entry.update(extra)
                items.append(entry)
            else:
                items.append(_parse_scalar(content))
        return items, idx

    mapping: dict[str, object] = {}
    while idx < len(tokens) and tokens[idx][0] == indent:
        text = tokens[idx][1]
        if text.startswith("- ") or text == "-":
            break
        kv = _split_key_value(text)
        if kv is None:
            idx += 1
            continue
        key, rest = kv
        idx += 1
        if rest is not None:
            mapping[key] = _parse_scalar(rest)
        elif idx < len(tokens) and (tokens[idx][0] > indent or (
            tokens[idx][0] == indent and (tokens[idx][1].startswith("- ") or tokens[idx][1] == "-")
        )):
            # YAML permits an unindented sequence directly beneath a mapping key.
            # Native Hermes/PyYAML configurations use this for plugin and MoA lists.
            child_indent = tokens[idx][0]
            mapping[key], idx = _parse_yaml_block(tokens, idx, child_indent)
        else:
            mapping[key] = None
    return mapping, idx


def load_yaml_mapping(raw: str | bytes | Path) -> dict:
    text = raw.read_text(encoding="utf-8-sig") if isinstance(raw, Path) else (
        raw.decode("utf-8-sig") if isinstance(raw, (bytes, bytearray)) else str(raw)
    )
    if not text.strip():
        return {}
    try:
        import yaml  # type: ignore
        parsed = yaml.safe_load(text) or {}
        return parsed if isinstance(parsed, dict) else {}
    except ImportError:
        pass
    try:
        from ruamel.yaml import YAML  # type: ignore
        parsed = YAML(typ="safe").load(text) or {}
        return parsed if isinstance(parsed, dict) else {}
    except ImportError:
        pass
    tokens = _tokenize_yaml_lines(text)
    if not tokens:
        return {}
    parsed, _ = _parse_yaml_block(tokens, 0, tokens[0][0])
    return parsed if isinstance(parsed, dict) else {}


def _dump_scalar(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if (
        not text
        or text != text.strip()
        or _YAML_AMBIGUOUS.match(text)
        or any(ch in text for ch in ("\n", "\r", "\t", '"', "#"))
        or ": " in text
        or text.endswith(":")
        or text[0] in "-?:,[]{}#&*!|>'\"%@`"
    ):
        return json.dumps(text, ensure_ascii=False)
    return text


def _dump_yaml_lines(value, indent: int = 0) -> list[str]:
    pad = " " * indent
    lines: list[str] = []
    if isinstance(value, dict):
        if not value:
            return [f"{pad}{{}}"]
        for key, item in value.items():
            key_text = _dump_scalar(str(key))
            if isinstance(item, dict) and item:
                lines.append(f"{pad}{key_text}:")
                lines.extend(_dump_yaml_lines(item, indent + 2))
            elif isinstance(item, list) and item:
                lines.append(f"{pad}{key_text}:")
                lines.extend(_dump_yaml_lines(item, indent + 2))
            elif isinstance(item, dict):
                lines.append(f"{pad}{key_text}: {{}}")
            elif isinstance(item, list):
                lines.append(f"{pad}{key_text}: []")
            else:
                lines.append(f"{pad}{key_text}: {_dump_scalar(item)}")
        return lines
    if isinstance(value, list):
        if not value:
            return [f"{pad}[]"]
        for item in value:
            if isinstance(item, dict) and item:
                sub = _dump_yaml_lines(item, indent + 2)
                first = sub[0][indent + 2:]
                lines.append(f"{pad}- {first}")
                lines.extend(sub[1:])
            elif isinstance(item, list) and item:
                lines.append(f"{pad}-")
                lines.extend(_dump_yaml_lines(item, indent + 2))
            else:
                lines.append(f"{pad}- {_dump_scalar(item)}")
        return lines
    return [f"{pad}{_dump_scalar(value)}"]


def dump_yaml(data: dict) -> str:
    return "\n".join(_dump_yaml_lines(data)) + "\n"


class PureYamlCompat:
    """Minimal ruamel.yaml.YAML-compatible wrapper backed by PyYAML or pure Python."""

    def __init__(self, *, typ: str | None = None, pure: bool = False):
        self.typ = typ
        self.pure = pure
        self.preserve_quotes = False
        self.default_flow_style = False
        self.width = 4096

    def load(self, stream):
        raw = stream.read() if hasattr(stream, "read") else stream
        if isinstance(raw, (bytes, bytearray)):
            text = raw.decode("utf-8-sig")
        elif raw is None:
            text = ""
        else:
            text = str(raw)
        if not text.strip():
            return None
        try:
            import yaml  # type: ignore
            return yaml.safe_load(text)
        except ImportError:
            pass
        tokens = _tokenize_yaml_lines(text)
        if not tokens:
            return None
        first = tokens[0][1]
        if first.startswith("- ") or first == "-" or _split_key_value(first) is not None:
            parsed, _ = _parse_yaml_block(tokens, 0, tokens[0][0])
            return parsed
        return _parse_scalar(first)

    def dump(self, data, stream=None):
        if isinstance(data, dict):
            rendered = dump_yaml(data)
        elif isinstance(data, list):
            rendered = "\n".join(_dump_yaml_lines(data)) + "\n"
        else:
            rendered = _dump_scalar(data) + "\n"
        if stream is None:
            return rendered
        if isinstance(stream, Path):
            stream.write_text(rendered, encoding="utf-8")
            return None
        stream.write(rendered)
        return None


def _custom_provider_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9._-]+", "-", name.strip().lower()).strip("-")


def launch_model_seed(source_cfg: dict) -> dict:
    """Copy default profile model + referenced provider/custom_provider only (never channels/gateway)."""
    if not isinstance(source_cfg, dict) or not source_cfg.get("model"):
        return {}
    seed: dict[str, object] = {"model": source_cfg["model"]}
    model_cfg = source_cfg["model"]
    provider = model_cfg.get("provider") if isinstance(model_cfg, dict) else None
    provider = provider.strip() if isinstance(provider, str) else ""
    if not provider:
        return seed
    providers = source_cfg.get("providers")
    if isinstance(providers, dict) and provider in providers:
        seed["providers"] = {provider: providers[provider]}
    custom = source_cfg.get("custom_providers")
    if isinstance(custom, list):
        matches = []
        for entry in custom:
            if not isinstance(entry, dict):
                continue
            raw_name = str(entry.get("name") or "").strip()
            slug = _custom_provider_slug(raw_name)
            if provider == raw_name or (slug and provider == f"custom:{slug}"):
                matches.append(entry)
        if matches:
            seed["custom_providers"] = matches
    return seed


def launch_model_seed_from_home(hermes_home: Path) -> dict:
    cfg_path = hermes_home / "config.yaml"
    if not cfg_path.is_file():
        return {}
    try:
        return launch_model_seed(load_yaml_mapping(cfg_path))
    except OSError:
        return {}


def is_channel_env_key(key: str) -> bool:
    upper = key.strip().upper()
    return upper in _NON_COPY_ENV_EXACT or any(upper.startswith(prefix) for prefix in _NON_COPY_ENV_PREFIXES)


def model_env_keys(source_cfg: dict) -> set[str]:
    """Only locally configured active model authentication, never account/channel tokens."""
    seed = launch_model_seed(source_cfg)
    model = seed.get('model') if isinstance(seed.get('model'), dict) else {}
    provider = str(model.get('provider') or '').lower()
    standard = {
        'openai': {'OPENAI_API_KEY'}, 'anthropic': {'ANTHROPIC_API_KEY'},
        'openrouter': {'OPENROUTER_API_KEY'}, 'nous': {'NOUS_API_KEY'},
        'gemini': {'GEMINI_API_KEY', 'GOOGLE_API_KEY'}, 'google': {'GEMINI_API_KEY', 'GOOGLE_API_KEY'},
        'groq': {'GROQ_API_KEY'}, 'deepseek': {'DEEPSEEK_API_KEY'},
        'mistral': {'MISTRAL_API_KEY'}, 'together': {'TOGETHER_API_KEY'},
        'xai': {'XAI_API_KEY'}, 'fireworks': {'FIREWORKS_API_KEY'},
    }
    keys = set(standard.get(provider, ()))
    env_name = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
    def walk(value):
        if isinstance(value, dict):
            for name, item in value.items():
                if name in {'key_env', 'api_key_env', 'api_key_env_var'} and isinstance(item, str) and env_name.fullmatch(item):
                    keys.add(item)
                elif name in {'api_key', 'key'} and isinstance(item, str):
                    match = re.fullmatch(r'\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)', item)
                    if match:
                        keys.add(next(x for x in match.groups() if x))
                if isinstance(item, (dict, list)):
                    walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)
    walk(seed)
    return {key for key in keys if not is_channel_env_key(key)}


def clone_safe_env_text(root_env_path: Path) -> str:
    if not root_env_path.is_file():
        return _PLACEHOLDER_ENV
    cfg_path = root_env_path.parent / 'config.yaml'
    allowed = model_env_keys(load_yaml_mapping(cfg_path)) if cfg_path.is_file() else set()
    kept: list[str] = []
    try:
        lines = root_env_path.read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        return _PLACEHOLDER_ENV
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        lhs = stripped.split("=", 1)[0].strip()
        if lhs.startswith("export "):
            lhs = lhs[7:].strip()
        if lhs in allowed and not is_channel_env_key(lhs):
            kept.append(line)
    if not kept:
        return _PLACEHOLDER_ENV
    return "\n".join(kept) + "\n"


def _env_is_placeholder(env_path: Path) -> bool:
    if not env_path.is_file():
        return True
    try:
        for line in env_path.read_text(encoding="utf-8-sig").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                return False
        return True
    except OSError:
        return False


def _atomic_write_text(path: Path, text: str, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / f".{path.name}.tmp-{os.getpid()}"
    try:
        tmp.write_text(text, encoding="utf-8")
        if mode is not None and os.name != "nt":
            os.chmod(tmp, mode)
        for attempt in range(5):
            try:
                tmp.replace(path)
                break
            except PermissionError:
                if attempt == 4:
                    raise
                time.sleep(0.05)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def _rename_with_retry(src: Path, dst: Path) -> None:
    for attempt in range(6):
        try:
            src.replace(dst)
            return
        except PermissionError:
            if attempt == 5:
                raise
            time.sleep(0.05 * (attempt + 1))


def _ensure_profile_subdirs(profile_dir: Path, *, write_no_bundled_marker: bool = True) -> None:
    for subdir in _HERMES_PROFILE_DIRS:
        (profile_dir / subdir).mkdir(parents=True, exist_ok=True)
    if write_no_bundled_marker:
        marker = profile_dir / NO_BUNDLED_SKILLS_MARKER
        if not marker.exists():
            marker.write_text("", encoding="utf-8")


def is_stock_hermes_soul(path: Path) -> bool:
    """Return True when SOUL.md is missing, empty, or matches Hermes' unedited stock prompt."""
    if not path.exists():
        return True
    if path.is_symlink() or not path.is_file():
        return False
    try:
        if path.stat().st_size > 2048:
            return False
        text = path.read_text(encoding="utf-8-sig").strip()
    except (OSError, UnicodeDecodeError):
        return False
    if not text:
        return True
    # Exact known native templates only: sharing the introduction is NOT permission
    # to replace a user's customized persona.
    return text in {STOCK_HERMES_SOUL, STOCK_HERMES_SOUL.replace("—", "--")}


def _backup_default_file(hermes_home: Path, path: Path) -> Path | None:
    if not path.is_file() or path.is_symlink():
        return None
    backups_dir = hermes_home / "backups"
    if backups_dir.is_symlink():
        return None
    backups_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    backup_path = backups_dir / f"{path.name}.pre-msshi-{stamp}.bak"
    shutil.copy2(path, backup_path)
    return backup_path


def _build_profile_meta(
    existing: dict,
    label: str,
    description: str,
    update_display_names: bool,
    *,
    replace_generic_names: bool = False,
) -> dict:
    meta = dict(existing) if isinstance(existing, dict) else {}
    if description and (update_display_names or not meta.get("description")):
        meta["description"] = description
    meta.setdefault("description_auto", False)
    raw_display = str(meta.get("display_name") or "").strip()
    replace_display = update_display_names or (not raw_display) or (
        replace_generic_names and raw_display.lower() in {"hermes", "default"}
    )
    target_label = label if replace_display else str(meta["display_name"])
    meta["display_name"] = target_label
    ui_meta = dict(meta.get("ui_meta") or {}) if isinstance(meta.get("ui_meta"), dict) else {}
    bots_ui = dict(ui_meta.get("hermes-bots") or {}) if isinstance(ui_meta.get("hermes-bots"), dict) else {}
    current_title = bots_ui.get("title")
    raw_title = str(current_title or "").strip()
    replace_title = update_display_names or (not raw_title) or (
        replace_generic_names and raw_title.lower() in {"hermes", "default"}
    )
    new_title = target_label if replace_title else current_title
    bots_ui["title"] = new_title
    ui_meta["hermes-bots"] = bots_ui
    meta["ui_meta"] = ui_meta
    revs = dict(meta.get("_ui_meta_revisions") or {}) if isinstance(meta.get("_ui_meta_revisions"), dict) else {}
    if current_title and new_title != current_title:
        revs["hermes-bots"] = int(revs.get("hermes-bots") or 0) + 1
    else:
        revs.setdefault("hermes-bots", 1)
    meta["_ui_meta_revisions"] = revs
    return meta


# The receipts contain local credential backups. Never publish this directory.
_POLICY_START = "<!-- MSSHI:MANAGED-COORDINATION:START -->"
_POLICY_END = "<!-- MSSHI:MANAGED-COORDINATION:END -->"
_IDENTITY_MARKERS = ("config.yaml", ".env", "SOUL.md", "profile.yaml", "auth.json", "state.db")


def _confined(root: Path, path: Path) -> Path:
    root, path = root.absolute(), path.absolute()
    if not path.is_relative_to(root):
        raise ValueError(f"Path outside Hermes root: {path}")
    check = path
    while check != root.parent:
        if check.is_symlink():
            raise ValueError(f"Refusing profile symlink: {check}")
        if check == root:
            break
        check = check.parent
    return path


def _fingerprint(path: Path, kind: str = "file") -> str | None:
    if not path.exists():
        return None
    if path.is_symlink():
        raise ValueError(f"Refusing profile symlink: {path}")
    if kind == "file":
        return hashlib.sha256(path.read_bytes()).hexdigest()
    digest = hashlib.sha256()
    for child in sorted(path.rglob("*")):
        if child.is_symlink():
            raise ValueError(f"Refusing symlink inside profile tree: {child}")
        digest.update(child.relative_to(path).as_posix().encode("utf-8"))
        digest.update(b"/" if child.is_dir() else bytes.fromhex(_fingerprint(child)))
    return digest.hexdigest()


def _atomic_write_bytes(path: Path, content: bytes, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp-{uuid.uuid4().hex}")
    try:
        tmp.write_bytes(content)
        if mode is not None and os.name != "nt":
            os.chmod(tmp, mode)
        _rename_with_retry(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


class ProfileTransaction:
    """Local, lazy receipt. Existing identity/config/secrets are never rewritten by sync.

    Changed metadata, context files and selected tombstones are backed up before writes.
    Rollback only restores a path if its installed fingerprint still matches: later user
    changes become conflicts instead of being overwritten. New trees are quarantined.
    """
    def __init__(self, hermes_home: Path):
        self.home = hermes_home.absolute()
        self.folder = self.home / "msshi-runtime" / "profile-receipts" / (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-" + uuid.uuid4().hex[:8])
        self.receipt = self.folder / "receipt.json"
        self.entries: dict[str, dict] = {}
        self.state = "applying"

    def _save(self) -> None:
        _confined(self.home, self.receipt)
        self.folder.mkdir(parents=True, exist_ok=True)
        if os.name != "nt":
            os.chmod(self.folder, 0o700)
        payload = {"version": 1, "hermes_home": str(self.home), "state": self.state,
                   "updated_at": utc_now(), "entries": list(self.entries.values())}
        _atomic_write_text(self.receipt, json.dumps(payload, indent=2, ensure_ascii=False) + "\n", mode=0o600)

    def capture(self, path: Path, kind: str = "file") -> dict:
        path = _confined(self.home, path)
        key = str(path)
        if key in self.entries:
            return self.entries[key]
        before = _fingerprint(path, kind)
        entry = {"path": key, "kind": kind, "before_sha256": before, "after_sha256": before}
        if kind == "file" and before is not None:
            self.folder.mkdir(parents=True, exist_ok=True)
            backup = self.folder / (f"{len(self.entries):04d}.bak")
            _atomic_write_bytes(backup, path.read_bytes(), mode=0o600)
            entry["backup"] = backup.name
        elif kind == "tree" and before is not None:
            raise ValueError("Only newly created trees can be tracked as a tree")
        self.entries[key] = entry
        self._save()
        return entry

    def mark(self, path: Path) -> None:
        entry = self.entries[str(path.absolute())]
        entry["after_sha256"] = _fingerprint(path, entry["kind"])
        self._save()

    def write(self, path: Path, content: bytes, mode: int | None = None) -> bool:
        _confined(self.home, path)
        if path.is_file() and path.read_bytes() == content:
            return False
        self.capture(path)
        _atomic_write_bytes(path, content, mode)
        self.mark(path)
        return True

    def commit(self) -> str | None:
        if not self.entries:
            return None
        self.state = "applied"
        self._save()
        return str(self.receipt)

    def rollback(self) -> dict:
        if not self.entries:
            return {"state": "unchanged", "restored": [], "conflicts": []}
        # A failed copy may have left its own new tree partly written.
        for entry in self.entries.values():
            if entry["kind"] == "tree" and entry["before_sha256"] is None and entry["after_sha256"] is None:
                entry["after_sha256"] = _fingerprint(Path(entry["path"]), "tree")
        self._save()
        return rollback_profile_receipt(self.receipt, expected_home=self.home)


def rollback_profile_receipt(receipt: Path, *, expected_home: Path | None = None) -> dict:
    receipt = receipt.absolute()
    payload = json.loads(receipt.read_text(encoding="utf-8-sig"))
    home = Path(payload["hermes_home"]).absolute()
    if expected_home is not None and home != expected_home.absolute():
        raise ValueError("Rollback receipt belongs to another Hermes root")
    _confined(home / "msshi-runtime" / "profile-receipts", receipt)
    restored, conflicts = [], []
    initial = {row["path"]: _fingerprint(_confined(home, Path(row["path"])), row["kind"])
               for row in payload.get("entries", []) if not row.get("rolled_back")}
    for row in reversed(payload.get("entries", [])):
        if row.get("rolled_back"):
            continue
        path = _confined(home, Path(row["path"]))
        if initial[row["path"]] != row.get("after_sha256"):
            conflicts.append(str(path))
            continue
        if row.get("before_sha256") is not None:
            backup = receipt.parent / str(row["backup"])
            if backup.parent != receipt.parent or _fingerprint(backup) != row["before_sha256"]:
                raise ValueError("Invalid profile backup")
            _atomic_write_bytes(path, backup.read_bytes(), mode=0o600)
        elif path.exists():
            if row["kind"] == "tree":
                quarantine = receipt.parent / "quarantine" / f"{len(restored):04d}-{path.name}"
                quarantine.parent.mkdir(parents=True, exist_ok=True)
                _rename_with_retry(path, quarantine)
            else:
                path.unlink()
        row["rolled_back"] = True
        restored.append(str(path))
    payload["state"] = "rollback_conflicts" if conflicts else "rolled_back"
    payload["rollback"] = {"at": utc_now(), "restored": restored, "conflicts": conflicts}
    _atomic_write_text(receipt, json.dumps(payload, indent=2, ensure_ascii=False) + "\n", mode=0o600)
    return {"state": payload["state"], "receipt": str(receipt), "restored": restored, "conflicts": conflicts}


def coordination_policy(bot_id: str) -> str:
    return f"""{_POLICY_START}
## MSSHI role coordination (active logical role: {bot_id}; use installed native mapping)
The native default can represent Yukino when team-layout.json selects that layout;
otherwise default remains a neutral Hermes assistant. Resolve roles to actual native IDs
using msshi-runtime/team-layout.json and the live roster; never invent a profile. Roles:
- yukino: receive ideas, discuss early concepts, then hand off complex planning to shizuka.
- shizuka: coordinate the plan and synthesize specialist results for the user.
- val: literature, evidence, data, academic research; send findings to shizuka.
- kiki-chii: concept-first filmmaking, video, photography and creative production.
- shikaku: coding, debugging, architecture, web development and authorized security work.
For a task spanning specialties, yukino/shizuka should delegate only the relevant work to
real, live named profiles. Simple conversation may be answered directly. Never wake all
bots for every question, delegate to yourself, or substitute an unnamed ephemeral child
for a named specialist without explaining the limitation.
Use message_agent only when the current native Bot Chat exposes that tool; its actual
fields are target, message, constraints, expecting and expects_reply. Send a composed,
scoped request, then finish the turn and wait for its completion notification. A queued
acknowledgement is not completed work. Do not invent a bot_relay roster or tool names.
Outside Bot Chat, use delegate_task with an explicit named profile only if the current
native delegation provider advertises that parameter in the live tool schema. Otherwise
explain that named-bot handoff is unavailable in this session; do not pretend it happened.
Handoff format: goal; required output; relevant context; limits/approval; evidence; blockers;
next action. Return only useful results to the coordinator. A received bot message already
has a transport reply path: put the reply in the final response, never send a second DM
merely to reply. For a Bot Chat turn requiring no action, say exactly:
I don't need to do anything here.
Do not send that no-action response as a new message or create a reply loop. Human review
is required between creative stages and before publishing or irreversible external actions.
This policy does not change provider/model, credentials, SOUL.md or the user's role voices.
{_POLICY_END}"""


def _managed_agents_bytes(existing: bytes, policy: str, initial: str = "") -> bytes:
    block = policy.encode("utf-8")
    start, end = _POLICY_START.encode(), _POLICY_END.encode()
    if start in existing:
        if existing.count(start) != 1 or existing.count(end) != 1:
            raise ValueError("Ambiguous MSSHI coordination markers; preserve file for manual review")
        left = existing.index(start)
        right = existing.index(end, left) + len(end)
        return existing[:left] + block + existing[right:]
    if end in existing:
        raise ValueError("Unpaired MSSHI coordination marker")
    content = existing or (initial.rstrip() + "\n").encode("utf-8")
    return content + (b"\n\n" if content and not content.endswith(b"\n\n") else b"") + block + b"\n"


def _restore_selected_profile(hermes_home: Path, target_dir: Path, tx: ProfileTransaction) -> str | None:
    tombstone = _confined(hermes_home, target_dir.parent / ".deleted" / target_dir.name)
    if not tombstone.exists():
        return None
    if not tombstone.is_file():
        raise ValueError(f"Invalid profile tombstone: {tombstone}")
    tx.capture(tombstone)
    source = hermes_home / "hermes-agent" / "hermes_constants.py"
    method = "hermes-compatible-selected-tombstone"
    if source.is_file() and not source.is_symlink():
        spec = importlib.util.spec_from_file_location("_msshi_native_hermes_constants", source)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if Path(module.profile_tombstone_path(target_dir)).absolute() != tombstone.absolute():
            raise ValueError("Native Hermes tombstone convention differs; refusing restore")
        module.clear_named_profile_deleted(target_dir)
        method = "hermes_constants.clear_named_profile_deleted"
    else:
        tombstone.unlink()
    tx.mark(tombstone)
    return method


def live_named_profiles(hermes_home: Path) -> dict[str, Path]:
    """Native identity/tombstone conventions, no process, plugin or model execution."""
    result = {}
    profiles = hermes_home / "profiles"
    if not profiles.is_dir() or profiles.is_symlink():
        return result
    for path in profiles.iterdir():
        if not valid_profile_id(path.name) or not path.is_dir() or path.is_symlink():
            continue
        if (profiles / ".deleted" / path.name).exists():
            continue
        if any((path / name).is_file() for name in _IDENTITY_MARKERS):
            result[path.name] = path
    return result


def validate_named_profile_target(hermes_home: Path, source: str, target: str) -> Path:
    """Validate local dispatch authority for structural/mock tests; never dispatch a turn."""
    if source == target:
        raise ValueError("Refusing self delegation")
    profiles = live_named_profiles(hermes_home)
    if target not in profiles:
        raise ValueError(f"Target is not a live native named profile: {target}")
    return profiles[target]


def restore_neutral_default(hermes_home: Path, *, transaction: ProfileTransaction | None = None) -> dict:
    """Explicit keep-hermes repair of duplicate Yukino presentation only, never identity/config."""
    tx = transaction or ProfileTransaction(hermes_home)
    meta_path = _confined(hermes_home, hermes_home / "profile.yaml")
    meta = load_yaml_mapping(meta_path) if meta_path.is_file() else {}
    ui = dict(meta.get("ui_meta") or {})
    bots = dict(ui.get("hermes-bots") or {})
    duplicate = {"yukino", "yukino yukinoshita"}
    changed = False
    if str(meta.get("display_name") or "").strip().lower() in duplicate:
        meta["display_name"] = "Hermes"
        changed = True
    if str(bots.get("title") or "").strip().lower() in duplicate:
        bots["title"] = "Hermes"
        ui["hermes-bots"] = bots
        meta["ui_meta"] = ui
        revisions = dict(meta.get("_ui_meta_revisions") or {})
        revisions["hermes-bots"] = int(revisions.get("hermes-bots") or 0) + 1
        meta["_ui_meta_revisions"] = revisions
        changed = True
    if changed:
        # This explicit duplicate-persona repair also clears its stale role description.
        # Visuals/section placement stay intact; SOUL/config are never touched.
        meta["description"] = "Asisten Hermes umum"
        meta["description_auto"] = False
        tx.write(meta_path, dump_yaml(meta).encode("utf-8"))
    return {"changed": changed, "path": str(meta_path), "receipt": tx.commit() if transaction is None else None}


def sync_hermes_profile(
    hermes_home: Path, bot_id: str, label: str, soul_text: str, agents_text: str,
    skill_copies: list[tuple[Path, Path]], *, description: str = "",
    update_display_names: bool = False, as_default: bool = False,
    update_stock_soul: bool = False, copy_fn=None,
    transaction: ProfileTransaction | None = None,
) -> dict[str, object]:
    """Provision a real native profile, preserving customized SOUL and config/.env.

    as_default=True adopts root/default as Yukino. Only an absent/stock SOUL is replaced;
    restoring an existing personal SOUL is a separate explicit private-preset operation.
    No profile configuration, credential or history is moved to or from default.
    """
    if not valid_profile_id(bot_id) or bot_id == "default":
        raise ValueError(f"Invalid named Hermes profile ID: {bot_id!r}")
    if as_default and bot_id != "yukino":
        raise ValueError("Only Yukino may use the MuZA preset's native default profile")
    hermes_home = hermes_home.absolute()
    target_dir = _confined(hermes_home, hermes_home if as_default else hermes_home / "profiles" / bot_id)
    if target_dir.exists() and not target_dir.is_dir():
        raise ValueError(f"Profile target is not a directory: {target_dir}")
    tx = transaction or ProfileTransaction(hermes_home)
    own_transaction = transaction is None
    # Never stage/move the infrastructure root as though it were a named profile.
    is_new = not target_dir.exists() and not as_default
    if as_default:
        target_dir.mkdir(parents=True, exist_ok=True)
    stage_dir = target_dir.parent / f".{bot_id}.staging-{uuid.uuid4().hex}" if is_new else target_dir
    stage_dir = _confined(hermes_home, stage_dir)
    seeded_config = seeded_env = False
    skills_installed = 0
    try:
        if is_new:
            target_dir.parent.mkdir(parents=True, exist_ok=True)
            stage_dir.mkdir(mode=0o700)
            tx.capture(target_dir, "tree")
        # Track only newly created subdirectories for an existing profile.
        for name in _HERMES_PROFILE_DIRS:
            path = stage_dir / name
            _confined(hermes_home, path)
            if not path.exists():
                if not is_new:
                    tx.capture(path, "tree")
                path.mkdir()
                if not is_new:
                    tx.mark(path)
        def write(path: Path, data: bytes, mode: int | None = None):
            if is_new:
                _atomic_write_bytes(path, data, mode)
            else:
                tx.write(path, data, mode)
        marker = stage_dir / NO_BUNDLED_SKILLS_MARKER
        if not marker.exists():
            write(marker, b"")
        meta_path = stage_dir / "profile.yaml"
        existing_meta = load_yaml_mapping(meta_path) if meta_path.is_file() else {}
        new_meta = _build_profile_meta(existing_meta, label, description, update_display_names or as_default)
        if not meta_path.is_file() or new_meta != existing_meta:
            write(meta_path, dump_yaml(new_meta).encode("utf-8"))
        soul_path = stage_dir / "SOUL.md"
        stock_replaced = as_default and soul_path.exists() and is_stock_hermes_soul(soul_path)
        custom_soul_preserved = as_default and soul_path.exists() and not stock_replaced
        if not soul_path.exists() or stock_replaced:
            write(soul_path, (soul_text.rstrip() + "\n").encode("utf-8"))
        policy = coordination_policy(bot_id)
        for agents_path in (stage_dir / "AGENTS.md", stage_dir / "workspace" / "AGENTS.md"):
            old = agents_path.read_bytes() if agents_path.exists() else b""
            new = _managed_agents_bytes(old, policy, agents_text)
            if new != old:
                write(agents_path, new)
        config_path = stage_dir / "config.yaml"
        if not config_path.exists():
            seed = launch_model_seed_from_home(hermes_home)
            if seed:
                write(config_path, dump_yaml(seed).encode("utf-8"))
                seeded_config = True
        env_path = stage_dir / ".env"
        if not env_path.exists():
            safe_env = clone_safe_env_text(hermes_home / ".env")
            write(env_path, safe_env.encode("utf-8"), 0o600)
            seeded_env = safe_env != _PLACEHOLDER_ENV
        for src, dst in skill_copies:
            dst = _confined(target_dir / "skills", dst)
            actual_dst = stage_dir / dst.relative_to(target_dir)
            _confined(hermes_home, actual_dst)
            if not actual_dst.exists():
                if not is_new:
                    tx.capture(actual_dst, "tree")
                (copy_fn or shutil.copytree)(src, actual_dst)
                if not is_new:
                    tx.mark(actual_dst)
                skills_installed += 1
        if is_new:
            _rename_with_retry(stage_dir, target_dir)
            tx.mark(target_dir)
        restored = None if as_default else _restore_selected_profile(hermes_home, target_dir, tx)
        # Include final descendant changes in newly created parent-directory receipts.
        for row in tx.entries.values():
            if row["kind"] == "tree" and row["before_sha256"] is None:
                tx.mark(Path(row["path"]))
        receipt = tx.commit() if own_transaction else None
    except Exception:
        if is_new and stage_dir.exists():
            # Only this invocation's randomly named, confined staging tree is removed.
            _confined(target_dir.parent, stage_dir)
            shutil.rmtree(stage_dir)
        if own_transaction:
            tx.rollback()
        raise
    return {"bot_id": "default" if as_default else bot_id, "role_id": bot_id, "as_default": as_default, "path": str(target_dir),
            "created": is_new, "display_name": new_meta["display_name"],
            "seeded_config": seeded_config, "seeded_env": seeded_env,
            "skills_installed": skills_installed, "restored_tombstone": restored,
            "stock_soul_replaced": stock_replaced,
            "custom_soul_preserved": bool(custom_soul_preserved),
            "receipt": receipt, "context_policy": "profile/workspace AGENTS; loaded only when native cwd discovery reaches them"}



def _replace_yaml_section_bytes(raw: bytes, key: str, section: dict) -> bytes:
    """Change one top-level section, keeping all unrelated source text byte-identical.

    Refuse exotic/non-mapping YAML when a narrow rewrite cannot be proven equivalent.
    Existing model/provider/MoA values inside delegation are copied verbatim as values.
    """
    text = raw.decode("utf-8-sig")
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines(keepends=True)
    pattern = re.compile(r"^(?:" + re.escape(key) + r"|'" + re.escape(key) + r"'|\"" + re.escape(key) + r"\")\s*:")
    hits = [index for index, line in enumerate(lines) if pattern.match(line)]
    if len(hits) > 1:
        raise ValueError(f"Duplicate YAML section {key}; refusing automatic plugin activation")
    rendered = dump_yaml({key: section}).replace("\r\n", "\n").replace("\n", newline)
    if hits:
        start = hits[0]
        end = start + 1
        while end < len(lines):
            line = lines[end]
            if line.strip() and not line[0].isspace() and not line.startswith("#"):
                break
            end += 1
        return bom + ("".join(lines[:start]) + rendered + "".join(lines[end:])).encode("utf-8")
    if text.strip() and not text.endswith(("\n", "\r")):
        text += newline
    return bom + (text + rendered).encode("utf-8")


def _activate_team_config(path: Path, tx: ProfileTransaction) -> dict:
    if not path.is_file():
        return {"active": False, "reason": "config_missing"}
    before = load_yaml_mapping(path)
    plugins = before.get("plugins") or {}
    delegation = before.get("delegation") or {}
    if not isinstance(plugins, dict) or not isinstance(delegation, dict):
        return {"active": False, "reason": "non_mapping_plugin_or_delegation_config"}
    disabled = plugins.get("disabled") or []
    enabled = plugins.get("enabled")
    if not isinstance(disabled, list) or (enabled is not None and not isinstance(enabled, list)):
        return {"active": False, "reason": "custom_plugin_policy_requires_review"}
    if "msshi-team-routing" in disabled:
        return {"active": False, "reason": "explicitly_disabled_by_user"}
    old_backend = delegation.get("backend") or "default"
    # An explicitly selected default backend is still a user's choice. Only
    # absent backend settings may opt into MSSHI during preset provisioning.
    # The key itself is the persistent preference marker across later syncs.
    change_backend = 'backend' not in delegation or str(old_backend).strip().lower() == "msshi-team"
    expected = dict(before)
    expected_plugins = dict(plugins)
    expected_plugins["enabled"] = list(enabled or [])
    if "msshi-team-routing" not in expected_plugins["enabled"]:
        expected_plugins["enabled"].append("msshi-team-routing")
    expected["plugins"] = expected_plugins
    if change_backend:
        expected_delegation = dict(delegation)
        expected_delegation["backend"] = "msshi-team"
        expected["delegation"] = expected_delegation
    else:
        expected_delegation = delegation
    raw = path.read_bytes()
    if expected_plugins != plugins:
        raw = _replace_yaml_section_bytes(raw, "plugins", expected_plugins)
    if expected_delegation != delegation:
        raw = _replace_yaml_section_bytes(raw, "delegation", expected_delegation)
    # Validate proposed bytes in memory; no interpreter, secret resolver or API is run.
    after = load_yaml_mapping(raw)
    if after != expected:
        raise ValueError(f"Cannot prove narrow config edit preserves routing at {path}")
    changed = tx.write(path, raw, 0o600)
    return {"active": True, "backend": "msshi-team" if change_backend else "custom_backend_preserved",
            "backend_preference": "explicit_config_preserved" if not change_backend else "msshi_backend_selected",
            "named_profile_delegate_backend_selected": (after.get("delegation") or {}).get("backend") == "msshi-team",
            "changed": changed, "main_model_provider_preserved": before.get("model") == after.get("model")
            and before.get("provider") == after.get("provider"),
            "delegation_routing_preserved": {k: v for k, v in delegation.items() if k != "backend"}
            == {k: v for k, v in (after.get("delegation") or {}).items() if k != "backend"}}


def install_team_routing_plugin(
    hermes_home: Path, repo_source: Path, *, profile_ids: tuple[str, ...] =
    ("yukino", "shizuka", "val", "kiki-chii", "shikaku"),
    transaction: ProfileTransaction | None = None,
) -> dict:
    """Stage the native plugin; choose MSSHI backend only when no backend was set.

    Plugin activation changes plugins.enabled/delegation.backend only (backed up). Existing
    explicit backends (including default), primary model/provider, auxiliary/MoA, SOUL
    and credential files are never changed. Named delegation needs its current schema;
    native Bot Chat message_agent remains available independently of backend selection.
    """
    hermes_home = hermes_home.absolute()
    source = repo_source / "hermes_plugins" / "msshi-team-routing"
    if not (source / "plugin.yaml").is_file() or not (source / "__init__.py").is_file():
        raise ValueError("MSSHI team-routing plugin source is missing")
    native_context = hermes_home / "hermes-agent" / "hermes_cli" / "plugins_context.py"
    if native_context.is_file():
        text = native_context.read_text(encoding="utf-8")
        if "def register_delegation_provider(" not in text or "def register_system_prompt_section(" not in text:
            return {"installed": False, "reason": "native_hermes_plugin_api_unsupported"}
    elif (hermes_home / "hermes-agent").exists():
        return {"installed": False, "reason": "native_hermes_plugin_api_unconfirmed"}
    tx = transaction or ProfileTransaction(hermes_home)
    rows = {}
    try:
        homes = [("default", hermes_home)]
        live = live_named_profiles(hermes_home)
        homes.extend((name, live[name]) for name in profile_ids if name in live)
        for name, home in homes:
            folder = _confined(hermes_home, home / "plugins" / "msshi-team-routing")
            for filename in ("plugin.yaml", "__init__.py", "README.md"):
                src = source / filename
                if src.is_symlink():
                    raise ValueError("Refusing plugin source symlink")
                tx.write(folder / filename, src.read_bytes())
            rows[name] = _activate_team_config(home / "config.yaml", tx)
        receipt = tx.commit() if transaction is None else None
    except Exception:
        if transaction is None:
            tx.rollback()
        raise
    return {"installed": True, "profiles": rows, "receipt": receipt,
            "restart_required": True, "new_session_prompt_required": True,
            "network_or_llm_calls": 0}

def record_pending_bots(hermes_home: Path, entries: list[dict[str, str]], mode: str, *, transaction: ProfileTransaction | None = None) -> Path:
    manifest_path = hermes_home / "msshi-runtime" / "pending-bots.json"
    existing = {}
    if manifest_path.is_file():
        try:
            existing = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            existing = {}
    bots = dict(existing.get("bots") or {})
    # Pending IDs are actual native profiles; no synthetic profiles/default folder.
    if mode in {"muza-preset", "academic-mahasiswa", "academic-dosen"}:
        bots.pop("yukino" if any(row["bot_id"] == "default" for row in entries) else "default", None)
    for row in entries:
        bot_id = row["bot_id"]
        bots[bot_id] = {
            "bot_id": bot_id,
            "display_name": row.get("label") or bot_id,
            "description": row.get("description") or "",
            "mode": mode,
        }
    payload = {
        "version": 1,
        "mode": mode,
        "hermes_initialized": is_hermes_initialized(hermes_home),
        "bots": bots,
    }
    content = (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if transaction is not None:
        transaction.write(manifest_path, content)
    elif not manifest_path.is_file() or manifest_path.read_bytes() != content:
        _atomic_write_bytes(manifest_path, content)
    return manifest_path


def sync_pending_profile_configs(hermes_home: Path) -> dict[str, object]:
    """Backfill the user's active model and required keys for enrolled pre-staged bots only."""
    if not hermes_home.is_dir():
        return {"hermes_home": str(hermes_home), "initialized": False, "seeded_configs": [], "seeded_envs": []}
    seed = launch_model_seed_from_home(hermes_home)
    safe_env = clone_safe_env_text(hermes_home / ".env")
    profiles_dir = hermes_home / "profiles"
    pending_path = hermes_home / "msshi-runtime" / "pending-bots.json"
    pending_data: dict = {}
    if pending_path.is_file():
        try:
            pending_data = json.loads(pending_path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            pending_data = {}

    candidate_names: set[str] = set()
    if profiles_dir.is_dir():
        for folder in profiles_dir.iterdir():
            if not folder.is_dir() or folder.is_symlink() or folder.name.startswith("."):
                continue
            if not valid_profile_id(folder.name):
                continue
            if (folder / "profile.yaml").is_file() or (folder / "SOUL.md").is_file():
                candidate_names.add(folder.name)
    for bot_id in (pending_data.get("bots") or {}):
        if valid_profile_id(bot_id) and (profiles_dir / bot_id).is_dir():
            candidate_names.add(bot_id)

    seeded_configs: list[str] = []
    seeded_envs: list[str] = []
    for bot_id in sorted(candidate_names):
        if (profiles_dir / ".deleted" / bot_id).exists():
            continue
        pdir = profiles_dir / bot_id
        if not pdir.is_dir() or pdir.is_symlink():
            continue
        _ensure_profile_subdirs(pdir)
        cfg = pdir / "config.yaml"
        if not cfg.exists() and seed:
            _atomic_write_text(cfg, dump_yaml(seed))
            seeded_configs.append(bot_id)
        env_file = pdir / ".env"
        managed_empty_env = (bot_id in (pending_data.get('bots') or {}) and env_file.is_file()
                             and env_file.read_bytes() in {_PLACEHOLDER_ENV.encode('utf-8'), _PLACEHOLDER_ENV.replace('\n', '\r\n').encode('utf-8')})
        if not env_file.exists() or (managed_empty_env and safe_env != _PLACEHOLDER_ENV):
            _atomic_write_text(env_file, safe_env, mode=0o600)
            if safe_env != _PLACEHOLDER_ENV:
                seeded_envs.append(bot_id)
        meta_path = pdir / "profile.yaml"
        if not meta_path.is_file():
            info = (pending_data.get("bots") or {}).get(bot_id, {})
            meta = _build_profile_meta({}, str(info.get("display_name") or bot_id), str(info.get("description") or ""), True)
            _atomic_write_text(meta_path, dump_yaml(meta))

    # Backfill configuration only; never rewrite the chosen default persona/layout.
    if pending_path.is_file():
        pending_data["hermes_initialized"] = is_hermes_initialized(hermes_home)
        pending_data["last_backfill_at"] = utc_now()
        _atomic_write_text(pending_path, json.dumps(pending_data, indent=2, ensure_ascii=False) + "\n")

    # Pre-Hermes staging has no config yet. Activate the already-staged native
    # plugin after the user's own configuration appears, respecting disabled/custom policies.
    routing_tx = ProfileTransaction(hermes_home)
    routing_rows = {}
    try:
        homes = [("default", hermes_home), *live_named_profiles(hermes_home).items()]
        for profile_id, pdir in homes:
            plugin = pdir / "plugins" / "msshi-team-routing"
            if (plugin / "plugin.yaml").is_file() and (plugin / "__init__.py").is_file():
                routing_rows[profile_id] = _activate_team_config(pdir / "config.yaml", routing_tx)
        routing_receipt = routing_tx.commit()
    except Exception:
        routing_tx.rollback()
        raise

    return {
        "hermes_home": str(hermes_home),
        "initialized": is_hermes_initialized(hermes_home),
        "has_model_seed": bool(seed),
        "seeded_configs": seeded_configs,
        "seeded_envs": seeded_envs,
        "team_routing": routing_rows,
        "team_routing_receipt": routing_receipt,
    }


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        if os.name == "nt":
            handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
            if not handle:
                return False
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _gateway_is_running(hermes_home: Path) -> bool:
    state_file = hermes_home / "gateway_state.json"
    if not state_file.is_file():
        return False
    try:
        state = json.loads(state_file.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return False
    if state.get("gateway_state") != "running":
        return False
    pid = state.get("gateway_pid") or state.get("pid")
    return True if not isinstance(pid, int) else _pid_alive(pid)


def _find_hermes_python(hermes_home: Path) -> Path | None:
    agent_dir = hermes_home / "hermes-agent"
    if not agent_dir.is_dir():
        return None
    candidates = [agent_dir / ".venv" / "Scripts" / "python.exe",
                  agent_dir / ".venv" / "bin" / "python", agent_dir / ".venv" / "bin" / "python3"]
    # uv tool installs keep Python beside HermesData/tools rather than source/.venv.
    # Read the launcher's bounded shebang; do not execute arbitrary candidates to probe.
    launcher = hermes_home / "bin" / "hermes.exe"
    if launcher.is_file() and not launcher.is_symlink():
        with launcher.open("rb") as handle:
            header = handle.read(1024 * 1024)
        for line in re.findall(rb"#!([^\r\n]+)", header):
            decoded = line.decode("utf-8", errors="ignore").strip()
            match = re.match(r'"([^"\r\n]+python(?:[0-9.]*)?\.exe)"|(.+?python(?:[0-9.]*)?\.exe)(?:\s|$)', decoded, re.I)
            if match:
                candidate = Path(match.group(1) or match.group(2))
                if candidate.absolute().is_relative_to(hermes_home.absolute()):
                    candidates.append(candidate)
    tools = hermes_home / "tools"
    if tools.is_dir() and not tools.is_symlink():
        candidates.extend(sorted(tools.glob("python-*/python.exe"), reverse=True))
    for candidate in candidates:
        if candidate.is_file() and not candidate.is_symlink():
            return candidate
    return None


def notify_live_multiplexer(hermes_home: Path) -> dict[str, object]:
    """If Hermes gateway is currently live, trigger multiplexer rescan without blocking offline installs."""
    if not _gateway_is_running(hermes_home):
        return {"running": False, "notified": False}
    agent_dir = hermes_home / "hermes-agent"
    python_exe = _find_hermes_python(hermes_home)
    if python_exe and (agent_dir / "gateway" / "control_socket.py").is_file():
        code = (
            "import json, os; from pathlib import Path; "
            "from gateway.control_socket import rescan_gateway_profiles; "
            "print(json.dumps(rescan_gateway_profiles(Path(os.environ['HERMES_HOME']), timeout=6.0) or {}))"
        )
        env = {**os.environ, "HERMES_HOME": str(hermes_home), "PYTHONDONTWRITEBYTECODE": "1"}
        try:
            proc = subprocess.run(
                [str(python_exe), "-c", code],
                cwd=agent_dir,
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=10,
                check=False,
            )
            try:
                response = json.loads(proc.stdout.strip().splitlines()[-1]) if proc.stdout.strip() else {}
            except (ValueError, IndexError):
                response = {}
            return {
                "running": True,
                "notified": proc.returncode == 0 and isinstance(response, dict) and isinstance(response.get("served_profiles"), list) and not response.get("error"),
                "response": response,
                "returncode": proc.returncode,
            }
        except (OSError, subprocess.SubprocessError) as error:
            return {"running": True, "notified": False, "error": str(error)}
    return {"running": True, "notified": False, "reason": "rescan_helper_unavailable"}
