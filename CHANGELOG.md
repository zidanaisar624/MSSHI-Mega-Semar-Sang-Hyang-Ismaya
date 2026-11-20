# Changelog MSSHI

## v3.1.2 - 2026-11-17

- Finalized v3.1.2 release on `main` (and refreshed tag `v3.1.2`; cleaned up legacy merged branches `release/v3.1.0` and `feat/win10-4gb-lite-roadmap`): added Windows 10 4 GB RAM Light Build & Low-RAM mode (`msshi light`), deferred `MSSHITrim` desktop/runtime activation, Coder-scoped `grim-prompter` (read-only threat modeling) & `claude-bughunter` (authorized triage/validation, 83 skills), full `harness2` + `timesfm-forecasting` parity across Academic presets, the Zero-Orphan 5-Mission + 4-Pillar Cognitive Operating System (`msshi system status|route|cycle`, covering `69/69` bundled skills + `1` optional `rea`, `4/4` plugins, `53/53` upstreams, and `5/5` connection planes), Val & Shizuka exclusivity for thesis/journal-search skills, and shortened `muza-skripsi-template/SKILL.md` description to satisfy Hermes's 1024-char limit.
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
