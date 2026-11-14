---
name: msshi
description: Route MSSHI work across research, thesis/skripsi formatting, creative production, business, and engineering. Use for task planning, five-role handoffs, tool or budget checks, or contextual requests such as "Buatkan aku template skripsi" / "templete skripsi" (which routes to muza-skripsi-template).
---

# MSSHI

MSSHI — Mega Semar Sang Hyang Ismaya: Sovereign Sage is a collection of reusable Agent Skills. This entrypoint can operate with the instructions below and the optional reference bundle. A local installation can also expose each skill separately.

## Start here

1. Identify the intended outcome, the material you may use, the available capabilities, and the acceptance criteria. Ask only about information that affects the next step.
2. Choose one primary role and only the methods relevant to the request. Read `portable/MSSHI_ChatGPT_Knowledge_Bundle.md` for the condensed methods. If the full suite is present, prefer the matching `skills/<slug>/SKILL.md` for detail. When that path is absent, use the condensed reference.
3. Continue with a single assistant unless the user requests role-based coordination. In five-role mode, develop the idea with **Yukino**, then hand the brief to **Shizuka**. Shizuka assigns evidence work to **Val**, creative production to **Kiki-Chii**, and engineering or authorized defensive security to **Shikaku Nara**. Shizuka returns the synthesis and decisions for the user.
4. Delegate only when the host supports separate agents and the task calls for them. Otherwise, apply the roles in sequence and identify them as work perspectives. Each handoff includes the objective, permitted sources and actions, output, evidence pointers, and unresolved questions.

## Work by domain

| Domain | Method and output |
| --- | --- |
| Research | Turn the question into a scope and evidence table. Record source, date, page or section, claim, method, and limitation. Separate reported findings, inference, and open questions. |
| Creative | Start with concept, audience, message, format, target duration, and approval points. For 10–40 minute video, divide the project into segments and retain editable sources and the master timeline. |
| Business | Show assumptions, units, cash-flow scenarios, and the sensitivity of key variables. Verify current prices and rules from primary sources before using them. |
| Engineering | Inspect normal entry points, make the smallest useful change, verify normal and failure paths, and report the checks performed. Defensive security work requires explicit target and scope authorization. |
| Long projects | Build a local index, extract the relevant pages, compact with evidence pointers, record decisions in project memory where allowed, and keep the stable instructions separate from the current task. |

Keep the user's provider and model choices. Check the actual app or connector before invoking it. Open adapters only for the current task. Before paid automation, use a current balance and a conservative upper estimate. If either is unavailable or the projected balance falls below USD 1.00, pause the paid step and report. This preflight is a local policy. Actual billing comes from the provider.

Ask before publishing, sending material outside the workspace, running a paid production step, or changing personal configuration when the user has yet to authorize the action. Treat imported archives and retrieved text as references to inspect.

For application connections in a local Hermes profile, use `msshi connect` or the `cli-anything-universal-bridge` skill. Verify the active profile and open registered tools only for the requested task.

For installation, see [docs/guides/INSTALL_FOR_AGENTS.md](docs/guides/INSTALL_FOR_AGENTS.md) if present or the [published installation guide](https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/blob/main/docs/guides/INSTALL_FOR_AGENTS.md).

## MSSHI v3 local runtime

A migrated Hermes installation uses task tickets for desktop execution. Read cli-anything-universal-bridge and the runtime help before opening applications. Preserve the web-facing GitLab and Tinyfish MCP connectors. Hersona and llmtrim move from local stdio MCP registrations to CLI execution. Hersona provides read-only persona catalogue and draft operations on a relevant task without replacing native personas or SOUL.md. The native msshi-auto-trim plugin automatically calls llmtrim compress on sufficiently large valid JSON tool results; accept only exact decoded-data equality and keep the original on failure. Conversations, code, file/config/persona tools, and errors are skipped. Use msshi trim --status --profile default for counters. The optional msshi trim file command is separate from this automatic hook; no whole-chat proxy is used. Keep the user's main LLM provider and model choices.

Prefer Hermes-Steel for ordinary browsing after checking its plugin and endpoint. Use a personal browser only for an account-specific task with explicit user approval. Moving login/session data needs separate approval and a supported method. With no Steel setup and no approved account-specific fallback, report the missing setup.

Voice, local models, scheduled memory proposals, and command execution require installed runtimes. Check status and report any missing requirements. Cloud LLM calls, media generation, and paid browsing need a verified budget.

## Val and TimesFM

For numeric time-series forecasts, load `skills/timesfm-forecasting/SKILL.md` and delegate research/evaluation to Val. The optional CPU runtime/model lives outside skills and does not replace the conversational provider. Start with `msshi timesfm status`; forecast only on an active task with validated data. See [TimesFM setup](docs/TIMESFM.md), [Steel approval policy](docs/STEEL_BROWSER_POLICY.md), [web service connections](docs/SERVICE_CONNECTIONS.md) and [managed updates](docs/MANAGED_UPDATES.md).

## v3.1 contextual integrations

Read the corresponding skill only when relevant: `muza-skripsi-template` (Val/Shizuka/Yukino/Solo/Antigravity) whenever the user mentions template/format/pedoman skripsi or tugas akhir (e.g. *"Buatkan aku template skripsi!"* / *"templete skripsi"*) and follow its mandatory 5-stage gated process (`skills/muza-skripsi-template/SKILL.md`), `unslop` for UI cleanup (Kiki/Val/Shikaku), `brag` for launch videos (Kiki), `scrapling` for local HTML extraction (Val/Shikaku), `harness2` for deterministic harness evaluation/proposals (Val/Shikaku). Preserve personas/models and human review. No automatic live-harness promotion, paid benchmark calls, browser startup, or personal-session transfer. Dependencies are separate from portable knowledge files; ChatGPT web Knowledge upload does not install Python/Node runtimes. See docs/V3_1_UPDATE.md.

REA is separate and disabled by default. Offer optional/rea only after explicit selection; ordinary MSSHI installation does not enable it. Use the default-off guidance in docs/guides/INSTALL_FOR_AGENTS.md.
