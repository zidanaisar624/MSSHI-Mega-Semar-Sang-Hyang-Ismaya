# MSSHI v3.1.1 - installation and routing repair

This patch preserves the README artwork and existing release history. The bundle contains **67 physical skills (51 core + 16 integration wrappers)** and **52 pinned upstream sources**. Fetching source does not install every runtime or prove an account is connected.

## Native Hermes profiles and teamwork

The five-bot preset installs `yukino`, `shizuka`, `val`, `kiki-chii` and `shikaku` as five named native profiles. Hermes default stays neutral. A targeted recovery clears only Yukino's obsolete deletion marker; existing conversations, SOUL, credentials, images and user customizations are retained. `--default-bot keep-hermes` also repairs duplicate Yukino presentation metadata on default.

The local `msshi-team-routing` plugin uses Hermes's supported delegation-provider and system-prompt-section APIs. Yukino handles initial ideation; Shizuka coordinates relevant specialists; Val researches; Kiki creates film/video/photo; Shikaku codes. It uses native Bot Chat messaging when the host actually exposes it, or named `delegate_task` routes when supported. It does not invent a profile argument for an unsupported backend. Existing custom backends are preserved and reported for review.

Ordinary delegation keeps existing model/provider/fallback values. A named handoff loads the destination profile's own model, persona, skills and credentials. Install/fixture tests do not launch paid turns. Restart the gateway and start a new conversation to rebuild session-stable tool schemas; retain old chats as history.

Profile changes have transactional receipts under `HERMES_ROOT/msshi-runtime/profile-receipts/`. The direct installer accepts `--rollback-receipt PATH --apply`; it reports conflicts rather than overwriting later user edits.

## Strict on-demand app ownership

| Bot | Native ArtCraft apps |
| --- | --- |
| Val | pdfcraft, gridcraft, wordcraft, deckcraft |
| Shikaku | craftanything, figcraft |
| Kiki | anicraft, filmcraft, effectcraft, soundcraft, photocraft, lightcraft, designcraft, figcraft, vectorcraft, cadcraft, solidcraft, materialcraft, texturecraft |
| Hermes default / Yukino / Shizuka | None |

Figcraft is the only shared ArtCraft route. Native CLI discovery supports custom Windows install roots. Routes require a task ticket and stay closed on startup. No desktop MCP server is re-enabled and no CraftAnything `setup --client hermes` command is run. GitLab/Tinyfish web MCP and user-selected non-ArtCraft companions keep their separate policies. BrightData remains disabled when no key is available.

Registry reconciliation now replaces obsolete policy-selected targets, respects explicit disable choices and synchronizes per-profile routes. A discovered executable, an enabled route and a successful task are separate facts.

## Repair a stale preservation baseline

```powershell
msshi runtime rebaseline --home "D:\HermesData"
```

This previews a snapshot and evidence diagnostics. Apply only with the returned snapshot:

```powershell
msshi runtime rebaseline --home "D:\HermesData" --apply --expected-snapshot SNAPSHOT_SHA
```

If historical evidence is missing/stale or LLM settings changed, the command additionally requires `--accept-current-llm-settings --reason "your explicit reason"`. Acceptance records the current state; it does not prove it equals an unverifiable old installation. The command edits neither config nor SOUL. A changed snapshot rejects the operation.

## Optional integrations and PDF delivery

- [Coder KAT](CODER_KAT.md): a real endpoint/key wizard, Coder-only gated execution, Dev/Pro distinction, metadata-only checks and no weight download.
- [Contextual sources](CONTEXTUAL_INTEGRATIONS.md): CareerOps/Remote Jobs/Matt Pocock for all five roles; rea-video for Kiki. Harness2 is assigned to all five. Source caches and runtime dependencies stay outside scanned skills.
- Client PDF: automatically copied to Downloads/MSSHI_Manuals by first-party bootstrap/setup/update/direct apply. Use `--pdf-dest` / `-PdfDest` or `MSSHI_PDF_DIR` for a chosen folder. `--no-pdf` / `-NoPdf` or `MSSHI_NO_PDF=1` opts out. Local copies are SHA256 checked; a differing existing guide is backed up.

No test in this patch certifies a provider-side $1 hard cap, universal token savings, model quality or every service's operational availability. Verify the specific task and inspect its output before relying on it.
