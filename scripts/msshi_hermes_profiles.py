"""Adaptive Hermes Desktop profile synchronization for MSSHI (before, during, and after Hermes runs)."""
from __future__ import annotations

import ctypes
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

PROFILE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
NO_BUNDLED_SKILLS_MARKER = ".no-bundled-skills"
STOCK_HERMES_SOUL_PREFIX = "You are Hermes Agent, built by Nous Research."
_PLACEHOLDER_ENV = "# Per-profile secrets for this Hermes profile.\n"
_HERMES_PROFILE_DIRS = ("memories", "sessions", "skills", "skins", "logs", "plans", "workspace", "cron", "home")
_STRONG_HERMES_MARKERS = ("config.yaml", "state.db", "hermes-agent", "auth.json", ".env")
_ALL_HERMES_MARKERS = (*_STRONG_HERMES_MARKERS, "profiles", "skills")
_NON_COPY_ENV_PREFIXES = (
    "TELEGRAM_", "DISCORD_", "EMAIL_", "SLACK_", "WHATSAPP_", "SIGNAL_",
    "FEISHU_", "LARK_", "MATRIX_", "WECOM_", "QQ_", "DINGTALK_", "TWILIO_",
    "SMS_", "GATEWAY_RELAY_", "HOME_ASSISTANT_",
)
_NON_COPY_ENV_EXACT = {
    "GATEWAY_ALLOW_ALL_USERS",
    "GATEWAY_ALLOWED_USERS",
    "HOME_CHANNEL",
    "ALLOWED_USERS",
    "HERMES_DASHBOARD_SESSION_TOKEN",
}
_YAML_AMBIGUOUS = re.compile(r"^(?:true|false|yes|no|on|off|null|~|[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)$", re.I)


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
    if not probe_write:
        return True
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
        candidates = [c for c in (d_root, local_app_data / f"hermes{suffix}", user_home / "HermesData", user_home / f".hermes{suffix}") if c is not None]
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
        return (local_app_data / f"hermes{suffix}").absolute()
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
        elif idx < len(tokens) and tokens[idx][0] > indent:
            child_indent = tokens[idx][0]
            mapping[key], idx = _parse_yaml_block(tokens, idx, child_indent)
        else:
            mapping[key] = {}
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


def clone_safe_env_text(root_env_path: Path) -> str:
    if not root_env_path.is_file():
        return _PLACEHOLDER_ENV
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
        if lhs and not is_channel_env_key(lhs):
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
    return text.startswith(STOCK_HERMES_SOUL_PREFIX) and len(text) <= 900


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


def sync_hermes_profile(
    hermes_home: Path,
    bot_id: str,
    label: str,
    soul_text: str,
    agents_text: str,
    skill_copies: list[tuple[Path, Path]],
    *,
    description: str = "",
    update_display_names: bool = False,
    as_default: bool = False,
    update_stock_soul: bool = True,
    copy_fn=None,
) -> dict[str, object]:
    """Create or safely update one Hermes profile without clobbering state, sessions, or user model config."""
    if not valid_profile_id(bot_id):
        raise ValueError(f"ID bot tidak valid untuk Hermes profile: {bot_id!r}")
    if as_default:
        target_dir = hermes_home
        if target_dir.is_symlink():
            raise ValueError(f"Menolak menulis melalui symlink profile: {target_dir}")
        target_dir.mkdir(parents=True, exist_ok=True)
        is_new = False
        stage_dir = target_dir
        seed = {}
        safe_env = _PLACEHOLDER_ENV
    else:
        profiles_root = hermes_home / "profiles"
        profiles_root.mkdir(parents=True, exist_ok=True)
        if os.name != "nt":
            try:
                os.chmod(profiles_root, 0o700)
            except OSError:
                pass
        tombstone = profiles_root / ".deleted" / bot_id
        if tombstone.exists() or tombstone.is_symlink():
            tombstone.unlink(missing_ok=True)

        target_dir = profiles_root / bot_id
        if target_dir.is_symlink():
            raise ValueError(f"Menolak menulis melalui symlink profile: {target_dir}")
        seed = launch_model_seed_from_home(hermes_home)
        safe_env = clone_safe_env_text(hermes_home / ".env")
        is_new = not target_dir.exists()
        stage_dir = profiles_root / f".{bot_id}.staging-{os.getpid()}" if is_new else target_dir
        if is_new:
            if stage_dir.exists():
                shutil.rmtree(stage_dir, ignore_errors=True)
            stage_dir.mkdir(parents=True, exist_ok=True)

    try:
        _ensure_profile_subdirs(stage_dir, write_no_bundled_marker=not as_default)
        meta_path = stage_dir / "profile.yaml"
        existing_meta = load_yaml_mapping(meta_path) if meta_path.is_file() else {}
        new_meta = _build_profile_meta(
            existing_meta, label, description, update_display_names,
            replace_generic_names=as_default,
        )
        if not meta_path.is_file() or new_meta != existing_meta:
            _atomic_write_text(meta_path, dump_yaml(new_meta))

        soul_path = stage_dir / "SOUL.md"
        if not soul_path.exists():
            _atomic_write_text(soul_path, soul_text.rstrip() + "\n")
        elif as_default and update_stock_soul and is_stock_hermes_soul(soul_path):
            _backup_default_file(hermes_home, soul_path)
            _atomic_write_text(soul_path, soul_text.rstrip() + "\n")
        agents_path = stage_dir / "AGENTS.md"
        if not agents_path.exists():
            _atomic_write_text(agents_path, agents_text.rstrip() + "\n")

        seeded_config = False
        seeded_env = False
        if not as_default:
            cfg_path = stage_dir / "config.yaml"
            if not cfg_path.exists() and seed:
                _atomic_write_text(cfg_path, dump_yaml(seed))
                seeded_config = True

            env_path = stage_dir / ".env"
            if _env_is_placeholder(env_path) and (not env_path.exists() or safe_env != _PLACEHOLDER_ENV):
                _atomic_write_text(env_path, safe_env, mode=0o600)
                seeded_env = safe_env != _PLACEHOLDER_ENV

        skills_installed = 0
        for src, dst in skill_copies:
            rel_dst = stage_dir / dst.relative_to(target_dir) if is_new and dst.is_relative_to(target_dir) else dst
            if not rel_dst.exists():
                if copy_fn is not None:
                    copy_fn(src, rel_dst)
                else:
                    shutil.copytree(src, rel_dst)
                skills_installed += 1

        if os.name != "nt":
            try:
                os.chmod(stage_dir, 0o700)
            except OSError:
                pass
        if is_new:
            _rename_with_retry(stage_dir, target_dir)
    except Exception:
        if is_new and stage_dir.exists():
            shutil.rmtree(stage_dir, ignore_errors=True)
        raise

    return {
        "bot_id": "default" if as_default else bot_id,
        "role_id": bot_id,
        "as_default": as_default,
        "path": str(target_dir),
        "created": is_new,
        "display_name": new_meta["display_name"],
        "seeded_config": seeded_config,
        "seeded_env": seeded_env,
        "skills_installed": skills_installed,
    }


def record_pending_bots(hermes_home: Path, entries: list[dict[str, str]], mode: str) -> Path:
    manifest_path = hermes_home / "msshi-runtime" / "pending-bots.json"
    existing = {}
    if manifest_path.is_file():
        try:
            existing = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            existing = {}
    bots = dict(existing.get("bots") or {})
    for row in entries:
        bot_id = row["bot_id"]
        bots[bot_id] = {
            "bot_id": bot_id,
            "display_name": row.get("label") or bot_id,
            "description": row.get("description") or "",
            "mode": mode,
            "updated_at": utc_now(),
        }
    payload = {
        "version": 1,
        "mode": mode,
        "updated_at": utc_now(),
        "hermes_initialized": is_hermes_initialized(hermes_home),
        "bots": bots,
    }
    _atomic_write_text(manifest_path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return manifest_path


def sync_pending_profile_configs(hermes_home: Path) -> dict[str, object]:
    """Backfill model config & non-channel .env for pre-staged bots once Hermes opens/configures."""
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
        if _env_is_placeholder(env_file) and (not env_file.exists() or safe_env != _PLACEHOLDER_ENV):
            _atomic_write_text(env_file, safe_env, mode=0o600)
            if safe_env != _PLACEHOLDER_ENV:
                seeded_envs.append(bot_id)
        meta_path = pdir / "profile.yaml"
        if not meta_path.is_file():
            info = (pending_data.get("bots") or {}).get(bot_id, {})
            meta = _build_profile_meta({}, str(info.get("display_name") or bot_id), str(info.get("description") or ""), True)
            _atomic_write_text(meta_path, dump_yaml(meta))

    default_pending = (pending_data.get("bots") or {}).get("default")
    if isinstance(default_pending, dict) and not hermes_home.is_symlink():
        default_meta_path = hermes_home / "profile.yaml"
        if not default_meta_path.is_file():
            meta = _build_profile_meta(
                {},
                str(default_pending.get("display_name") or "Yukino Yukinoshita"),
                str(default_pending.get("description") or ""),
                True,
                replace_generic_names=True,
            )
            _atomic_write_text(default_meta_path, dump_yaml(meta))

    if pending_path.is_file():
        pending_data["hermes_initialized"] = is_hermes_initialized(hermes_home)
        pending_data["last_backfill_at"] = utc_now()
        _atomic_write_text(pending_path, json.dumps(pending_data, indent=2, ensure_ascii=False) + "\n")

    return {
        "hermes_home": str(hermes_home),
        "initialized": is_hermes_initialized(hermes_home),
        "has_model_seed": bool(seed),
        "seeded_configs": seeded_configs,
        "seeded_envs": seeded_envs,
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
    candidates = [
        agent_dir / ".venv" / "Scripts" / "python.exe",
        agent_dir / ".venv" / "bin" / "python",
        agent_dir / ".venv" / "bin" / "python3",
    ]
    for candidate in candidates:
        if candidate.is_file():
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
            return {
                "running": True,
                "notified": proc.returncode == 0,
                "stdout": proc.stdout.strip(),
                "returncode": proc.returncode,
            }
        except (OSError, subprocess.SubprocessError) as error:
            return {"running": True, "notified": False, "error": str(error)}
    return {"running": True, "notified": False, "reason": "rescan_helper_unavailable"}
