"""Native Hermes named-profile routing, bounded role policy and opt-in Coder KAT.

Registration and schema building perform local reads only; never dispatch a model turn.
The core owns all child lifecycle, credentials and named-profile scope.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
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
    return tuple(name for name in PROFILE_ROLES
                 if not (root / "profiles" / name).is_symlink()
                 and named_profile_is_live(root / "profiles" / name))



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
        # Session-stable schema; route_task rechecks the target before core builds a child.
        self.root = _root()
        self.active_profile = _profile()
        self.profiles = _live_profiles(self.root)
        self.kat_available = _kat_settings(self.root, self.active_profile) is not None

    @property
    def name(self) -> str:
        return "msshi-team"

    @property
    def display_name(self) -> str:
        return "MSSHI named bot handoffs"

    @property
    def summary(self) -> str:
        return "Use live named profiles; ordinary subagents keep existing delegation model/provider."

    def task_parameters(self, config: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
        parameters = {}
        names = [name for name in self.profiles if name != self.active_profile]
        if names:
            parameters["profile"] = {"type": "string", "enum": names,
                "description": "Optional actual named specialist. Omit for ordinary ephemeral delegation."}
        if self.kat_available:
            parameters["execution"] = {"type": "string", "enum": ["configured", "kat"],
                "description": "Coder-only optional KAT subtask; configured keeps existing delegation routing."}
        return parameters

    def description(self, config: Mapping[str, Any]) -> str:
        return ("For a named specialist use profile only from the offered live enum. "
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
            if target == self.active_profile or target not in self.profiles or target not in _live_profiles(self.root):
                raise DelegationRouteError("Target is not a different live named profile. Refresh the session roster; no task was started.")
            return {"profile": target, "label": f"MSSHI {target}"}
        if execution == "kat":
            settings = _kat_settings(self.root, _profile())
            if not self.kat_available or settings is None:
                raise DelegationRouteError("KAT is not enabled and validated for this Coder session. Use configured routing.")
            return {"model": settings["model"], "provider": "custom", "base_url": settings["base_url"],
                    "api_key": _private_key(self.root, settings["api_key_env"]), "fallback_providers": [], "label": "Coder KAT opt-in"}
        # Exact default-backend pass-through: preserve delegation model/provider/reasoning/fallbacks.
        return {key: value for key, value in config.items() if key != "service_tier"}


def role_policy(session_info: Mapping[str, Any]) -> str:
    profile = str(session_info.get("profile_name") or "default")
    if profile not in PROFILE_ROLES:
        return "Hermes default remains a neutral general assistant. Do not impersonate named MSSHI bots."
    own = f"MSSHI native role {profile}: {PROFILE_ROLES[profile]}. "
    if profile in {"yukino", "shizuka"}:
        own += ("For work spanning specialties, delegate only needed portions to actual live named bots: "
                "yukino ideation, shizuka coordinator, val research, kiki-chii creative, shikaku coding. "
                "Simple conversation needs no delegation. Do not do all specialist work alone or wake everyone. ")
    else:
        own += "Stay within your specialty and return useful findings to shizuka when the task needs coordination. "
    return own + (
        "Use native message_agent only when exposed in Bot Chat (target/message/constraints/expecting/expects_reply); "
        "a queued acknowledgement is not completion. Finish the turn and await its notification. "
        "Otherwise use delegate_task profile only if offered by its current schema. An unnamed child is not a named teammate. "
        "Handoff: goal, output, context, limits/approval, evidence, blockers, next action. "
        "Received bot messages already carry a reply path: answer in your final response, do not send a second DM to reply. "
        "If a Bot Chat message needs no action, reply exactly: I don't need to do anything here. "
        "Never DM that no-action line or create reply loops. Human review is required between creative stages "
        "and before publishing/irreversible external actions. Preserve the user's main models and persona voice.")


def register(ctx) -> None:
    ctx.register_delegation_provider(MSSHITeamRouting())
    ctx.register_system_prompt_section("msshi.team-coordination", role_policy,
                                       position="after_memory", max_chars=2600)
