---
name: wise-judgment-and-sovereign-orchestrator
description: Routes MSSHI tasks by intent and authorization, coordinates the MuZA five-bot preset, and applies local-first context handling, TokenShield v2.0 preflight, and on-demand integrations.
---

# Wise Judgment and Sovereign Orchestrator

Use this skill to choose a workflow, prepare a task handoff, or check whether a tool and budget can support a specific action.

## Routing

1. Confirm the requested outcome, permitted inputs, allowed actions, and acceptance criteria.
2. Use local deterministic work for file search, extraction, calculations, and checks where practical. Use reasoning with a bounded evidence packet for judgments and synthesis.
3. In MuZA mode, Yukino develops the initial idea and hands it to Shizuka. Shizuka delegates research to Val, creative production to Kiki-Chii, and coding or authorized security work to Shikaku. The specialists return evidence and artifacts. Shizuka translates Val's research for the user while preserving citations and uncertainty. With one agent, work through these roles sequentially.
4. A handoff contains the task, scope, allowed sources, output, evidence pointers, open questions, and permission limits. Check that the recipient can access any shared artifact.
5. Read the package's `configs/bot_role_and_skill_matrix.json` for assignments if available. Select only the skills needed. Treat external entries as references pending compatible setup, authorization, and current availability.

## Activation and budget

- Session instructions establish persona and project scope. Start connected apps only for the task that needs them (`auto_open_on_boot: false`).
- Keep `jev_model_routing: false`. Use a compatible Jev adapter for skill and passage selection if present. Preserve the host's provider and model choices.
- Use TokenShield v2.0 before paid automation with current balance and an estimated upper cost. From the package root:

  ```bash
  python skills/wise-judgment-and-sovereign-orchestrator/scripts/cli_anything_sovereign_hub.py --json token-audit --balance-usd 1.20 --estimated-cost-usd 0.10
  ```

  The CLI returns exit 2 for missing values or a projected balance under USD 1.00. Pause and report when data is missing or stale. TokenShield evaluates supplied values locally. Billing systems remain authoritative for actual usage.
- Use page-addressed chunks and compact context. Ask for a relevant excerpt or a local extraction when a document cannot be read.

## Specialist workflows

- **Academic.** See `references/phd-thesis-longcontext-goose-remotejobs.md` for the seven academic paths and five context layers. Val returns claims with evidence and limitations. Shizuka explains the implications.
- **Creative.** Kiki-Chii confirms the concept and output requirements before choosing a production stack. Apply user Creative DNA only with consent.
- **Engineering.** Shikaku proposes a small solution and verifies normal use. Goose, Playwright, Strix, and design tools are optional. Local static triage is one check alongside runtime and authorized security tests.
- **Incidents.** Alert the user before acting. Emergency automation requires prior explicit, time-bounded scope for local read-only checks. Ask before modifications, external testing, or out-of-scope actions. Report observations, actions, and pending decisions.

## References

- `references/dartmouth-ai70-human-judgment-framework.md` for deterministic-first decisions and human responsibility.
- `references/tokenshield-zero-cost-monitor.md` for the local reserve check.
- `references/phd-thesis-longcontext-goose-remotejobs.md` for academic work, evidence retrieval, Goose, and remote jobs.
- `references/cli-anything-ram-safe-bridge.md` for on-demand adapter selection.
- `references/antigravity-webdev-and-strix-cybersec.md` for optional engineering, design, and defensive security references.
