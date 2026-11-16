# MSSHI v3.1.2 - safe setup, collaboration and optional runtimes

The release retains the existing artwork and Git history. It ships 67 physical skills (51 core and 16 wrappers), with 52 pinned upstream sources. The MuZA preset describes five roles; it never establishes the user's name as MuZA.

## Fresh installs versus an existing team

- Fresh `muza-preset` setup with `--default-bot auto`: the actual Hermes `default` profile becomes Yukino, with four named specialists. There is no model/profile swap.
- An existing named Yukino/team layout: `auto` retains it, including the neutral default assistant. No existing bot is automatically hidden or moved.
- `--default-bot keep-hermes`: neutral default plus five named profiles.
- `--default-bot yukino`: explicit layout conversion only, with receipts. Existing history remains in place. Custom SOUL, model/provider settings and credentials are not transferred to another profile.

The private role-to-profile map lets specialists find Yukino whether its actual profile ID is `default` or `yukino`. The native delegation provider supports both directions. Setup before Hermes configuration queues profiles; reconciliation after configuration activates the supported local team plugin. Repeating setup is idempotent. Tests cover fresh, pending, existing and rollback paths without dispatching a model.

## Personalization and teamwork

All public persona templates ask for a preferred user name only when unknown, retain the supplied spelling and share an agreed name in handoffs. Existing private persona text is preserved. [The SOUL-only helper](COLLABORATION_AND_NAMES.md) adds managed naming blocks and optional detailed Coder/Kiki collaboration protocols, with exact backups and conflict-aware rollback.

Simple tasks need no extra agents. Cross-specialty work uses only the necessary teammates. The configured models remain authoritative. Tool registration proves a route exists; it is not a completed paid collaboration test. Obsidian notes remain drafts until the user separately authorizes a destination and write action.

## Optional means optional

KAT is OFF by default, including the MuZA preset. Neither setup nor this patch downloads model weights. The unattended Windows wizard no longer mistakes an inherited console for consent to prompt. Public Coder options remain available for adequately equipped users.

CareerOps source validation now follows the pinned repository's actual layout. A matching partial cache resumes after Git blob-hash validation; a mismatching file is preserved and rejected. Runtime dependencies remain an explicit step outside scanned skills. Goose installation is separate from configuring a provider or running a task.

Desktop applications continue to use guarded, task-triggered native CLI routes. They are not opened on startup. LLMtrim may automatically compact eligible large JSON tool results; unchanged/error/unsupported data is retained. Hersona is a local CLI companion, not a replacement for a profile's SOUL. Missing external accounts, executable dependencies and model endpoints are reported rather than treated as ready.

The versioned client PDF is copied automatically by first-party installation/update unless opted out. Private presets, recovery copies, credentials and private audit reports do not belong in this public repository.
