# MSSHI native team routing

Hermes installs this local backend as `msshi-team-routing` and selects `delegation.backend: msshi-team` only when the existing backend is unset/default. Custom backends remain untouched. Ordinary unnamed delegation passes through the user's existing delegation model/provider/reasoning/fallback settings. A task selecting the optional `profile` enum uses the real named bot's identity, skills and primary credentials via Hermes core.

Native Bot Chat `message_agent` remains preferred. This plugin does not invoke it, dispatch tasks, open apps, contact endpoints, or make model calls at install/startup. The bounded supported `register_system_prompt_section` API supplies role coordination to new session prompts regardless of cwd. Existing session prompts must be refreshed by starting a new session; a gateway restart reloads plugin discovery. AGENTS files remain a portable fallback.

Optional KAT is offered only to a running Shikaku session with a private, validated local opt-in. It is never applied to another bot or the primary model. No private config or keys belong in this repository.
