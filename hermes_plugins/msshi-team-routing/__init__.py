"""Native Hermes named-profile routing, bounded role policy and opt-in Coder KAT.

Registration and schema building perform local reads only; never dispatch a model turn.
The core owns all child lifecycle, credentials and named-profile scope.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Mapping
from urllib.parse import urlparse

from agent.delegation_provider import DelegationProvider, DelegationRouteError

PROFILE_ROLES = {
    "yukino": "early ideation; hand complex planning to shizuka",
    "shizuka": "coordinate only needed specialists and synthesize their evidence",
    "val": "literature, academic research, evidence and data; report to shizuka",
    "kiki-chii": "concept-first filmmaking, video, photography and creative work",
    "shikaku": "coding, debugging, architecture, web development and authorized security",
}
_ENV_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_RELEASE_ID_RE = re.compile(r"^(?:[0-9a-f]{24}|[0-9a-f]{64})$")
_FINDER_CACHE: dict[str, Any] = {}


def _home() -> Path:
    from hermes_constants import get_hermes_home
    return Path(get_hermes_home())


def _root() -> Path:
    from hermes_constants import get_default_hermes_root
    return Path(get_default_hermes_root())


def _profile() -> str:
    home, root = _home().absolute(), _root().absolute()
    return home.name if home.parent == root / "profiles" else "default"


def _live_profiles(root: Path) -> tuple[str, ...]:
    from hermes_constants import named_profile_is_live
    return tuple(name for name in _role_profiles(root).values()
                 if (name == "default" and root.is_dir()) or
                 (name != "default" and not (root / "profiles" / name).is_symlink()
                  and named_profile_is_live(root / "profiles" / name)))


def _role_profiles(root: Path) -> dict[str, str]:
    """Map roles to supported real native IDs; malformed layout fails to legacy named mode."""
    roles = {name: name for name in PROFILE_ROLES}
    path = root / "msshi-runtime" / "team-layout.json"
    if path.is_file() and not path.is_symlink() and not path.parent.is_symlink() and path.stat().st_size <= 65536:
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            expected = dict(roles)
            if data.get("default_bot") == "yukino":
                expected["yukino"] = "default"
            if data.get("schema") == 1 and data.get("roles") == expected:
                return expected
        except (OSError, ValueError, AttributeError):
            pass
    return roles



def _private_key(root: Path, key_name: str) -> str | None:
    """Resolve one Coder key (profile first); never merge any .env into the process."""
    paths = (root / "profiles" / "shikaku" / ".env", root / ".env")
    for index, path in enumerate(paths):
        if index == 1 and os.environ.get(key_name):
            return os.environ[key_name]
        if any(parent.is_symlink() for parent in (path, path.parent, path.parent.parent)):
            continue
        if not path.is_file() or path.stat().st_size > 1024 * 1024:
            continue
        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except (OSError, UnicodeError):
            continue
        for line in reversed(lines):
            line = line.strip()
            if line.startswith("export "):
                line = line[7:].lstrip()
            name, sep, raw = line.partition("=")
            if sep and name.strip() == key_name:
                raw = raw.strip()
                if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
                    raw = raw[1:-1]
                else:
                    raw = re.split(r"\s+#", raw, maxsplit=1)[0].rstrip()
                if raw:
                    return raw
    return os.environ.get(key_name) or None


def _kat_settings(root: Path, active_profile: str) -> dict[str, Any] | None:
    """Private opt-in is Coder-only, exact-model catalog checked, local and secret-free."""
    if active_profile != "shikaku":
        return None
    path = root / "msshi-private" / "coder" / "kat.json"
    if not path.is_file() or path.is_symlink() or path.stat().st_size > 64 * 1024:
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, ValueError):
        return None
    if not isinstance(data, dict) or data.get("schema") != 1 or data.get("enabled") is not True:
        return None
    if data.get("profile") != "shikaku" or data.get("provider") != "custom":
        return None
    model, key_name = data.get("model"), data.get("api_key_env")
    catalog = data.get("validated_model_catalog")
    if isinstance(catalog, dict):
        catalog = catalog.get("ids")
    if not isinstance(model, str) or not isinstance(catalog, list) or model not in catalog:
        return None
    if not isinstance(key_name, str) or not _ENV_RE.fullmatch(key_name) or not _private_key(root, key_name):
        return None
    endpoint = data.get("base_url")
    if not isinstance(endpoint, str):
        return None
    parsed = urlparse(endpoint)
    local = parsed.hostname in {"127.0.0.1", "localhost", "::1"}
    if (parsed.scheme not in ({"http", "https"} if local else {"https"}) or not parsed.hostname
            or parsed.username or parsed.password or parsed.query or parsed.fragment):
        return None
    return data


class MSSHITeamRouting(DelegationProvider):
    def __init__(self):
        # Native providers are profile-scoped and may outlive individual chats.
        # Read local readiness at each new schema build; core freezes that session's tools.
        self.root = _root()
        self.active_profile = _profile()

    @property
    def name(self) -> str:
        return "msshi-team"

    @property
    def display_name(self) -> str:
        return "MSSHI native bot handoffs"

    @property
    def summary(self) -> str:
        return "Use live native role profiles; ordinary subagents keep existing delegation model/provider."

    def task_parameters(self, config: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
        parameters = {}
        names = [name for name in _live_profiles(self.root) if name != self.active_profile]
        if names:
            parameters["profile"] = {"type": "string", "enum": names,
                "description": "Optional actual native teammate ID. default means Yukino only when selected in team layout. Omit for ordinary ephemeral delegation."}
        if _kat_settings(self.root, self.active_profile) is not None:
            parameters["execution"] = {"type": "string", "enum": ["configured", "kat"],
                "description": "Coder-only optional KAT subtask; configured keeps existing delegation routing."}
        return parameters

    def description(self, config: Mapping[str, Any]) -> str:
        return ("For a native teammate use profile only from the offered live enum. "
                "This loads that bot's own SOUL, skills, main model and credentials. "
                "Omitting profile preserves existing delegation routing. Prefer message_agent "
                "when this is native Bot Chat and that tool is actually available.")

    def route_task(self, task: Mapping[str, Any], config: Mapping[str, Any]) -> dict[str, Any]:
        target = task.get("profile")
        execution = task.get("execution", "configured")
        if execution not in ("configured", "kat"):
            raise DelegationRouteError("Unknown execution mode. No subagent was started.")
        if target is not None:
            if execution == "kat":
                raise DelegationRouteError("Named profiles use their own main model. Request KAT only from Shikaku without profile.")
            if target == self.active_profile or target not in _live_profiles(self.root):
                raise DelegationRouteError("Target is not a different live native profile. Refresh the session roster; no task was started.")
            return {"profile": target, "label": f"MSSHI {target}"}
        if execution == "kat":
            settings = _kat_settings(self.root, _profile())
            if settings is None:
                raise DelegationRouteError("KAT is not enabled and validated for this Coder session. Use configured routing.")
            return {"model": settings["model"], "provider": "custom", "base_url": settings["base_url"],
                    "api_key": _private_key(self.root, settings["api_key_env"]), "fallback_providers": [], "label": "Coder KAT opt-in"}
        # Exact default-backend pass-through: preserve delegation model/provider/reasoning/fallbacks.
        return {key: value for key, value in config.items() if key != "service_tier"}


def role_policy(session_info: Mapping[str, Any]) -> str:
    actual_profile = str(session_info.get("profile_name") or "default")
    roles = _role_profiles(_root())
    profile = next((role for role, actual in roles.items() if actual == actual_profile), "")
    if profile not in PROFILE_ROLES:
        own = ("Hermes default remains a neutral general assistant. Do not impersonate named MSSHI bots. "
               "For requests needing specialist work, hand off only relevant bounded portions to live teammates; "
               "use shizuka to coordinate complex work. Simple conversation needs no delegation. ")
    else:
        own = f"MSSHI native role {profile} (actual profile {actual_profile}): {PROFILE_ROLES[profile]}. "
    own += "Role-to-native-profile mapping: " + ", ".join(f"{role}={actual}" for role, actual in roles.items()) + ". "
    if profile in {"yukino", "shizuka"}:
        own += ("For work spanning specialties, delegate only needed portions to actual live named bots: "
                "yukino ideation, shizuka coordinator, val research, kiki-chii creative, shikaku coding. "
                "Simple conversation needs no delegation. Do not do all specialist work alone or wake everyone. ")
    elif profile in PROFILE_ROLES:
        own += "Stay within your specialty and return useful findings to shizuka when the task needs coordination. "
    return own + (
        "Use native message_agent only when exposed in Bot Chat (target/message/constraints/expecting/expects_reply); "
        "a queued acknowledgement is not completion. Finish the turn and await its notification. "
        "Otherwise use delegate_task profile only if offered by its current schema. An unnamed child is not a named teammate. "
        "Use only the current live roster/schema; never wake everyone or repeat completed research. "
        "Do not start credit-consuming chat/API verification without explicit authorization. "
        "Handoff: goal, output, context, limits/approval, evidence, blockers, next action. "
        "Received bot messages already carry a reply path: answer in your final response, do not send a second DM to reply. "
        "If a Bot Chat message needs no action, reply exactly: I don't need to do anything here. "
        "Never DM that no-action line or create reply loops. Human review is required between creative stages "
        "and before publishing/irreversible external actions. "
        "Core missions: (1) Tutor/Guru—use belajar-pemula (1 concept/turn, Socratic/Chalk/LearnLoop/CodeCoach-or-Shikaku) & OSSU CS via 'msshi ossu'; "
        "(2) Tasks/Skripsi/Tesis/Disertasi—delegate deep ID/global research only when needed to val (riset-mendalam-nusantara-global, evidence, holdout, timesfm-forecasting); "
        "(3) Content creation—kiki-chii leads concept-first visuals/video/slides (+ optional imagination-studio when enabled); "
        "(4) Coding—shikaku leads TDD, architecture, and authorized grim-prompter/claude-bughunter; "
        "(5) Daily companion/curhat & scheduling—yukino leads warm Main-only empathy, energy pacing, and agenda (0 extra bots). "
        "Cognitive loop: save tokens via Main-only on brief chats, lazy msshi-private/context-sources reads (1 file on demand), "
        "MSSHITrim JSON compaction, and concise caveman internal handoffs (keep user prose natural and citations/code exact). "
        "Skill finder: call msshi_find_skill (or 'msshi find') for active/teammate/archive skills (open 1). "
        "Learn continuously via offline msshi dream proposals and isolated harness2 Propose-Probe-Compose; never auto-promote. "
        "Preserve the user's main models and persona voice.")


def _safe_path(path: Path) -> bool:
    try:
        resolved = Path(os.path.abspath(path))
        if str(resolved).startswith(("\\\\", "//")):
            return False
        for p in (resolved, *resolved.parents):
            if os.path.lexists(p) and (p.is_symlink() or (getattr(p.lstat(), "st_file_attributes", 0) & 0x400)):
                return False
        return True
    except OSError:
        return False


def _locate_skill_finder_script(root: Path) -> Path | None:
    candidates: list[Path] = []
    here = Path(__file__).resolve()
    if len(here.parents) >= 3:
        candidates.append(here.parents[2] / "scripts" / "msshi_skill_finder.py")

    data_roots: list[Path] = []
    if env_home := (os.environ.get("MSSHI_HOME") or "").strip():
        data_roots.append(Path(env_home).expanduser())
    if os.name == "nt":
        data_roots.append(Path("D:/MSSHI"))
        if local_app := (os.environ.get("LOCALAPPDATA") or "").strip():
            data_roots.append(Path(local_app) / "MSSHI")
    data_roots.extend([Path.home() / ".local" / "share" / "msshi", Path.home() / ".msshi"])

    for dr in data_roots:
        state_file = dr / "state.json"
        if _safe_path(state_file) and state_file.is_file():
            try:
                state = json.loads(state_file.read_text(encoding="utf-8-sig"))
                rel_id = str(state.get("current") or "").strip()
                if _RELEASE_ID_RE.fullmatch(rel_id):
                    candidates.append(dr / "releases" / rel_id / "scripts" / "msshi_skill_finder.py")
            except (OSError, ValueError, AttributeError):
                pass

    candidates.append(root / "msshi-upstream" / "scripts" / "msshi_skill_finder.py")
    for cand in candidates:
        if _safe_path(cand) and cand.is_file():
            return cand
    return None


def _load_skill_finder(root: Path):
    script = _locate_skill_finder_script(root)
    if script is None:
        raise ValueError("MSSHI skill finder script not found in active release or upstream checkout.")
    key = str(script.resolve())
    cached = _FINDER_CACHE.get(key)
    if cached is not None:
        return cached
    scripts_dir = str(script.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    spec = importlib.util.spec_from_file_location("msshi_skill_finder_runtime", script)
    if not spec or not spec.loader:
        raise ValueError("Unable to load MSSHI skill finder module.")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _FINDER_CACHE[key] = mod
    return mod


def _find_skill_handler(args: Any = None, **kwargs: Any) -> str:
    payload = args if isinstance(args, dict) else kwargs
    try:
        root = _root()
        finder = _load_skill_finder(root)
        result = finder.handle_tool_call(payload, root, profile=_profile())
        return json.dumps(result, ensure_ascii=False)
    except ValueError as exc:
        return json.dumps({"ok": False, "error_class": "ValueError", "error": str(exc)}, ensure_ascii=False)
    except Exception as exc:
        return json.dumps(
            {"ok": False, "error_class": type(exc).__name__, "error": "Skill finder failed; inspect local logs."},
            ensure_ascii=False,
        )


def register(ctx) -> None:
    ctx.register_delegation_provider(MSSHITeamRouting())
    ctx.register_system_prompt_section("msshi.team-coordination", role_policy,
                                       position="after_memory", max_chars=2600)
    if hasattr(ctx, "register_tool"):
        description = (
            "Search active bot skills, specialist teammates, connected sources, and archived skill vaults "
            "(action='search'), or read 1 archived SKILL.md on demand (action='open'). 0 LLM calls; enforces "
            "specialist role ownership and archive confinement."
        )
        ctx.register_tool(
            name="msshi_find_skill",
            toolset="msshi-team-routing",
            description=description,
            schema={
                "name": "msshi_find_skill",
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["search", "open"],
                            "description": "search to find matching skills across 4 layers, or open to read 1 archived SKILL.md.",
                        },
                        "query": {
                            "type": "string",
                            "description": "Task description or keywords (required when action='search').",
                        },
                        "slug": {
                            "type": "string",
                            "description": "Archived skill slug to read (required when action='open').",
                        },
                        "top": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10,
                            "description": "Maximum matches per layer (default 5).",
                        },
                        "reindex": {
                            "type": "boolean",
                            "description": "Force rebuild of local archive index before searching (default false).",
                        },
                    },
                    "required": ["action"],
                    "additionalProperties": False,
                },
            },
            handler=_find_skill_handler,
        )
