# Changelog MSSHI

## v3.1.2 - 2026-11-17

- Added & refreshed 3 contextual upstream integrations (`75` bundled skills = `53` core + `22` wrappers, `64` external sources, `0` orphans):
  - Added **`rust-anything`** (`erkamyaman/rust-anything`, pin `584e6388`, MIT) scoped strictly to **Shikaku / Coder** (`skills/rust-anything/`, lazy markdown context cache via `msshi integrations source --name rust-anything`, separate Rust CLI/MCP runtime).
  - Added **`lemo-opuscar`** (`lemomo-ai/lemo-opuscar`, pin `f9e20429`, MIT code / CC BY-NC 4.0 docs with film-making permission / CC BY 4.0 demo media) scoped strictly to **Kiki-Chii** (`skills/lemo-opuscar/` — 100% original thin pointer wrapper, 0 bytes of CC-BY-NC docs or heavy media bundled in MIT repo; lazy text-only cache for all **15 categories / 99 code-driven film styles** with `--list`, `--query`, and on-demand `--skill <slug>`).
  - Upgraded **`claude-bughunter`** (`elementalsouls/Claude-BugHunter`, MIT code / CC-BY-4.0 content) pin from `0e70a021` → **`8258d297`** (adds 433 content-verified cited disclosed reports across 36 pattern libraries in `docs/disclosed-reports/`).
  - Hardened `_materialize_via_git()` in `scripts/msshi_context_sources.py` to clone temp bare repos onto the `HERMES_HOME` drive with `--filter=blob:limit=512k` (preventing system-drive exhaustion and skipping heavy media blobs).
- Upgraded **MSSHI Interaction System** (`hermes_plugins/msshi-interaction/` v0.2.0, `hermes_plugins/msshi-team-routing/` v3.1.2, `scripts/msshi_interaction.py`, `scripts/msshi_skill_finder.py`):
  - Separated dedicated interaction prompt protocol (`msshi.interaction-protocol`, `< 1800` chars) covering Tier 0 (`fast_main_only`), Type 1 Advisor (`yukino`/`shizuka`), Type 2 2-round Council with mandatory Main audit (`val`/`kiki-chii`/`shikaku`), Low-RAM sequential fallback, and both native layouts (`keep-hermes`, `yukino`).
  - Wired zero-LLM native in-process tool **`msshi_find_skill`** (`action=search|open`) across all 6 profiles including `default` via `msshi-team-routing` with strict `_SPECIALIST_ONLY` ownership checks, archive confinement, and mtime-validated in-process caching.
  - Added dead-PID **stale-lock detection & safe recovery (`recover_lock`)** that preserves audit trails and blocks silent retries of interrupted paid rounds (`INTERRUPTED` terminal state) while rejecting active/concurrent locks (`JOB_BUSY_ACTIVE`).
  - Added **session-isolated job summaries** (`active_jobs`, `completed_jobs`) in `msshi_interaction_status` with legacy job compatibility and explicit opt-in terminal retention (`14` days / keep `20`, `auto_prune_enabled: false`, `msshi interaction --prune-terminal`).
  - Added **structured compact Council dossiers** (`goal`, `constraints`, `evidence_refs`, `delta_since_round_1`, `open_risks`) preserving citations, URLs/DOIs, fenced code blocks, and approval rules verbatim while reducing Round 2 input bloat.
- Added **Automatic Cross-Bot 4-Layer Lazy Skill Finder** (`msshi find "<task>"`, `msshi find --open <slug>`, `msshi find --reindex` in `scripts/msshi_skill_finder.py`, wired into `scripts/msshi_cli.py` and `hermes_plugins/msshi-team-routing/`): allows any bot (`default`, `yukino`, `shizuka`, `val`, `kiki-chii`, `shikaku`) to answer natural questions like *"Saya mau mengerjakan X, apakah ada skill yang bisa membantu?"* with `0` LLM calls by checking (1) active skills on the current bot, (2) specialist teammate skills with strict ownership delegation, (3) connected sources/OSSU, and (4) indexed local archived vaults (`msshi-private/archived-skill-imports/`, reading 1 `SKILL.md` on demand).
- Added **Mode Belajar Pemula Total** (`skills/belajar-pemula/` across all bots + `msshi learn status|start|install`, vendored MIT `hermes_plugins/chalk/` without large `docs/*.png`, opt-in direct upstream AGPL-3.0 `LearnLoop` installer via `--with-learnloop` never vendored in the MIT repo, pinned MIT `CodeCoach` Linux/WSL2 installer with honest Windows fallback to Shikaku).
- Added original **Val-only Indonesian + Global Deep Research Skill** (`skills/riset-mendalam-nusantara-global/` with 6 lazy `references/` files): combines a 10-stage adaptive pipeline (Quick/Standard/Deep, adequacy gate, devil's advocate, claim & citation audit, quality gate) inspired by MIT `hermes-researcher` with 100% original Indonesian (Bab I–V, SINTA 1–6, Garuda, RAMA, Neliti, EYD V) and Global (Scopus/WoS, PRISMA 2020, CONSORT/STROBE/COREQ, DOI) methodology — 0 bytes copied from unlicensed sources, Persian/Iran/arts excluded.
- Added **`msshi upstreams check|integrity|install-ponytail`** (`scripts/msshi_upstreams.py`): read-only GitHub upstream update checker (never auto-applies), Caveman/Ponytail offline integrity audit, and pinned MIT Ponytail installer for Shikaku; added permanent verified bare-git fallback for all `msshi_context_sources.py` sources, `msshi ossu fetch --refresh`, and read-only `connections` + OSSU + TimesFM summary in `msshi doctor` (`73` bundled skills, `7` repo plugins, `62` upstreams, `6` connections, `0` orphans).
- Connected **OSSU Open-Source Computer Science University** (`ossu/computer-science`, portal `https://cs.ossu.dev`, pin `8f8272b1`, MIT) via dedicated CLI & Hermes connector `msshi ossu` (`scripts/msshi_ossu.py` — `status`, `roadmap`, `courses`, `open`, `guides`, `fetch`), `connections_and_bridges_registry` (`6` connection planes), `msshi-team-routing`, and pinned local curriculum cache (`msshi-private/context-sources/ossu-computer-science/`). Modeled strictly as a connected Open-Source CS University (NOT a bot skill) so students can open CS fundamentals directly (`Intro CS -> Core CS -> Advanced CS -> Final Project`, 15 tracks / 63 courses) and study via Hermes.
- Added audited MIT Hermes plugins & skills **Spacewise** (`ardianreffa/spacewise`, pin `8e4f39aa`) and **Sharewise** (`ardianreffa/sharewise`, pin `dd82698f`) for **all bots in all presets** (`muza-preset`, `academic-mahasiswa`, `academic-dosen`, `solo`, `selective`, `custom-bots`) via `hermes_plugins/{spacewise,sharewise}`, `skills/{spacewise,sharewise}`, and automatic activation in `install_wise_plugins` (`71` bundled skills, `6` repo plugins, `56` upstreams, `0` orphans, `0` network calls).
- Added optional **Imagination Studio** bridge (`optional/imagination-studio`, `public_default: false`, scoped to **Kiki-Chii / Content Creator**, `msshi setup --with-imagination-studio`, `msshi optional enable imagination-studio`, and `msshi studio status|plan`), pinned to `Keys-Wasserman/Imagination-Studio-by-keys-Wasserman` (`16f00b46`, Apache-2.0 with NOTICE attribution) and wired into `filmmaking-videography-photography-s2` Stage E for seamless Filmmaker × Slate/Studio queue collaboration when installed (`54` external sources, `2` optional wrappers).
- Finalized v3.1.2 release on `main` (and refreshed tag `v3.1.2`; cleaned up legacy merged branches `release/v3.1.0` and `feat/win10-4gb-lite-roadmap`): added Windows 10 4 GB RAM Light Build & Low-RAM mode (`msshi light`), deferred `MSSHITrim` desktop/runtime activation, Coder-scoped `grim-prompter` (read-only threat modeling) & `claude-bughunter` (authorized triage/validation, 83 skills), full `harness2` + `timesfm-forecasting` parity across Academic presets, the Zero-Orphan 5-Mission + 4-Pillar Cognitive Operating System (`msshi system status|route|cycle`, covering `69/69` bundled skills + `2` optional wrappers, `4/4` plugins, `54/54` upstreams, and `5/5` connection planes), Val & Shizuka exclusivity for thesis/journal-search skills, and shortened `muza-skripsi-template/SKILL.md` description to satisfy Hermes's 1024-char limit.
- Post-tag audit correction: initialize role mapping in profile-mode aggregate audit; cover both existing named Yukino and fresh default Yukino without touching models or installed profiles.
- Fresh installs use actual default Yukino plus four specialists; existing named teams remain unchanged. Role mapping, delayed activation and all-direction handoffs are covered by offline fixtures. Curated upstream, Dreaming and voice selection also follow that mapping.
- Use controlled JSON-only LLMtrim configuration after real-binary tests exposed TOON type changes in the upstream safe preset. Preserve exact data and fail open; no proxy or provider setting changes.
- Complete missing Git revision metadata: all 49 Git sources are commit-pinned; model cards honor available revisions and non-Git registry/card limitations are explicit. Publish the complete 52-source/67-skill activation audit.
- Add portable user-address rules to all five persona templates and combined Main/Sub-Agent/MoA/contract/review protocols for Coder and Kiki. An explicit, receipt-backed SOUL helper preserves private persona bytes and refuses implicit Obsidian writes.

- Honor unattended Windows setup even when the process inherits a console; KAT is optional/default OFF, including the MuZA preset. No local weight download or main-model change.
- Fix CareerOps source checks for its actual upstream layout (no root npm lock), resume only Git-blob-verified partial downloads, and record an explicit locally resolved dependency lock when runtime setup is requested.
- Preserve prior v3.1.1 history and tag; this patch includes the Windows issue found during live installation. Update the client handbook and automatic PDF channel accordingly.

## v3.1.1 - 2026-11-16

- Ensure unattended `setup --yes --kat-mode ...` never prompts even when a Windows child inherits a console; defer KAT until Coder config exists.

- Repair five native Hermes profiles: named Yukino, neutral default, targeted deletion-marker recovery, transactional receipts and conflict-aware rollback. Preserve primary/MoA/delegation models, SOUL and credentials.
- Add native profile-aware delegation and bounded system prompt coordination. Existing custom backends are preserved; no model turns run during setup.
- Reconcile CLI-Anything registries with strict ArtCraft ownership (Val 4 / Shikaku 2 / Kiki 13), native app discovery including Anicraft, and persistent disabled routes. Add snapshot-guarded runtime rebaseline with explicit acceptance of stale historical evidence.
- Replace preference-only KAT setup with an optional Coder endpoint/key wizard, metadata-only catalog checks and gated native delegation. Distinguish open-weight Dev from official StreamLake Pro; no large model download or primary-model replacement.
- Bundle CareerOps, Remote Jobs and Matt Pocock context wrappers for all five roles; rea-video for Kiki. Harness2 is available to all five. Total: 67 bundled skills (51 core + 16 wrappers), 52 pinned sources.
- Automatically deliver the verified client PDF on bootstrap, setup, update and direct apply; support explicit destination/opt-out and back up a differing existing file.

## v3.1.0 - 2026-11-14

- Added **MuZA Skripsi Starter v1.1 (Drag-and-Drop Edition)**: bundled `skills/muza-skripsi-template/` (11 files: `SKILL.md` with 5-stage contextual & explicit workflow gate, `campus_lookup.py`, `extract_guideline.py`, `build_template.py`, `spec_schema.md`, `example_spec.json`, 5 methodology presets), Colab notebooks (`notebooks/skripsi/MuZA_Search.ipynb` & `MuZA_Skripsi_Builder.ipynb`), `MULAI_SKRIPSI_DRAG_AND_DROP.bat`, `msshi skripsi`, and `msshi doctor`.
- Expanded the default bundle to 63 skills (51 core + 12 wrappers) and 49 pinned source references, with separate licenses and runtime prerequisites.
- Added curated `assets/visuals/`, `docs/pdf-guides/Panduan_Master_MSSHI_v3.1.0.pdf`, `configs/github_about.txt`, and Mesin Ke-8 in `docs/TUJUH_MESIN_AKADEMIK.md`.
- Clarified terminal setup, pack/skill, optional REA/KAT and app choices with bilingual function/prerequisite help, a read-only `msshi choices` command, and a complete choice guide. Version and activation defaults remain unchanged.
- Added 3-timing automatic Hermes Desktop bot profile provisioning (before, during, and after opening Hermes) via `scripts/msshi_hermes_profiles.py`, adaptive Windows `D:\HermesData` vs `%LOCALAPPDATA%\hermes` resolution, pure-Python YAML fallback (`PureYamlCompat`) in `msshi_runtime.py`, custom display-name updates (`--update-display-names`), and non-interactive `-Mode`/`-Yes` flags in `install.ps1`/`install.sh`/`msshi setup`.
- Added four standard contextual wrappers: Unslop UI improvement (Kiki/Val/Shikaku), BRAG launch video (Kiki), Scrapling local HTML parser (Val/Shikaku), and Harness² deterministic harness evaluation (Val/Shikaku).
- Added REA as a separate default-off opt-in for public installs; MuZA explicitly enables it for Coder.
- Kept live persona/model routing and v3.0 browser/MCP safeguards; no automatic model-backed benchmarks or live harness promotion.
- Added standalone runtime commands, local guard tests, updated role documentation, and a visual integration map.


## v3.0.0 - 2026-11-12

- Added Val's TimesFM 2.5 local numeric forecasting wrapper; 58 bundled skills and 45 external sources. Heavy model files stay outside skill scanner roots.
- Installed task-scoped Steel browser routing with no silent local fallback, separate scoped personal-browser approval, and no automatic cookie/profile transfer. Cloud credentials remain required.
- Added GitLab/Tinyfish setup, safe discovery/auth reporting and same-user shared OAuth cache support across five native profiles; no desktop MCPs restored.
- Added hash/provenance-based enrollment of existing MSSHI skills, shared-junction updates, custom-content preservation and retarget detection.
- Preserved the software-rendering Desktop launcher, automatic lossless JSON Llmtrim hook, native Hersona CLI, voice runtime, protected LLM routing, and BrightData-off choice.


## 3.0.0 — 2026-11-11

- Added protected Hermes profile migration, on-demand desktop task tickets, hardware tiers, and local runtime audit.
- Added Desktop recovery for the Windows pending-update startup loop and local Chrome Remotion launch handling.
- Added Caveman, Hyperframes, UI UX Pro Max, Anthropic skills, OmniVoice, pinned Dreaming, and optional KAT source entries.
- Added beginner and update launchers, task-scoped application execution, and expanded source notices.
- Added voice persona settings and zero-LLM local Dreaming proposals with explicit runtime readiness reports.


## 2.1.0 — 2026-11-10

- Added bilingual quick starts, agent-chat installation instructions, a root entrypoint, and portable Claude and ChatGPT materials.
- Added the user-level `msshi` CLI for version checks, managed updates, selective installs, four setup modes, and the `msshi connect` application menu.
- Added a standalone CLI-Anything bridge skill for all five presets and public setup modes. Routes are scoped to the active Hermes profile and apps launch only on request.
- Retained the 50 Stage 1 skills and added seven physical integration wrappers. The corrected filmmaking curiosity slug is accepted as an alias.
- Added real upstream cache refresh for the 35 Git repositories, one model-card source, and one registry in the manifest.
- Recorded MuZA, Google Gemini, and OpenAI ChatGPT collaboration credits and regenerated the five-role audit.

## 2.1.0-stage1.2 — 2026-11-09

- Initial Stage 1 release under the MIT License.
- Included 50 bundled skills, six packs, five persona templates, and 37 external source references.

## [3.2.0] - 2026-11-24

### Added
- **`anti-slop` Promoted to Bundled Across All 5 Bots (`skills/anti-slop/SKILL.md`)**: Promoted `miqdadbadjuber/anti-slop` (MIT) to a bundled pre-output quality gate across `yukino`, `shizuka`, `val`, `kiki-chii`, and `shikaku` in `muza-preset`, `academic-mahasiswa`, `academic-dosen`, `solo`, and `light` builds while preserving citations and user Voice Cards.
- **`modern-web-guidance` for Coder (`skills/modern-web-guidance/SKILL.md`)**: Bundled Baseline modern web platform guidance (`GoogleChrome/modern-web-guidance`, Apache-2.0) strictly for Coder (`shikaku` / `Sir. Robot`) across all presets with Coder.
- **Coder Code-Review & Deterministic AST/Dead-Code Triad (`open-code-review` + `ast-grep` + `knip`)**:
  - `skills/open-code-review/SKILL.md` (`alibaba/open-code-review`, Apache-2.0, CLI `ocr`): Hybrid deterministic + line-level verified diff/commit/PR review for Coder across all presets with Coder.
  - `skills/ast-grep/SKILL.md` (`ast-grep/ast-grep`, MIT, CLI `sg`): Zero-token Tree-sitter AST structural search, lint, and safe multi-file codemod companion for Coder.
  - `skills/knip/SKILL.md` (`webpro-nl/knip`, ISC): Zero-token unused-files, unused-exports/types, and unused-dependencies detector for JS/TS and monorepos on Coder.
- **Opt-In 3D & GPU Render Modules for Kiki-Chii (`public_default: false`)**:
  - `optional/mcp-for-blender/SKILL.md` (`ahujasid/mcp-for-blender`, MIT, `--with-blender-mcp` / `msshi optional enable mcp-for-blender`, `auto_open_on_boot: false`).
  - `optional/raea/SKILL.md` (`shinyobjectz/raea`, FSL-1.1-ALv2, `--with-raea` / `msshi optional enable raea`, 0 upstream bytes vendored in MIT repo; supports both direct React/TS + Bevy GPU rendering and hybrid `.glb`/`.gltf` finishing from `mcp-for-blender`).

### Changed
- **Disconnected `blender` / `blender-cli` from `CLI-Anything`**: Removed Blender-specific native-CLI harness routes from `cli-anything-universal-bridge` and `DISABLED_MCP` (keeping all other 46 CLI-Anything routes untouched) so opt-in `mcp-for-blender` operates cleanly without migration removal.
- **`lemo-opuscar` Moved to Opt-In in `MSSHI Core v3.2.0` (`optional/lemo-opuscar/SKILL.md`, `--with-lemo-opuscar`)**: Keeps core installs lean while `hermes-mfa-filmmaking-and-agent-skills` installs `lemo-opuscar` automatically by default.
- **Rust Anti-Bug Guardrail (Hot-Path Only)**: Added explicit language-selection discipline to `skills/rust-anything/SKILL.md` and all Coder (`shikaku`) personas.

