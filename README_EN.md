[🇮🇩 Bahasa Indonesia](./README.md) | [🌐 English](./README_EN.md)

# MSSHI — Mega Semar Sang Hyang Ismaya: Sovereign Sage

[![MuZA × Google Gemini × OpenAI ChatGPT](https://img.shields.io/badge/Project%20credits-MuZA%20%C3%97%20Gemini%20%C3%97%20ChatGPT-5648b3)](docs/PROVENANCE.md#kredit-kolaborasi)

**MSSHI v2.1 is a cross-platform Multi-Agent Skill Suite & Persona Framework.** It includes 50 core `SKILL.md` folders, seven integration wrappers, solo and team presets, and an optional installation CLI. Claude Code can load it as a plugin. ChatGPT web uses portable instructions and reference material. External apps, accounts, models, and credits are set up through their respective services.

## 🚀 30-Second Quick Start (Choose Your Agent)

**Start in your agent's chat.** Paste this into Hermes Agent, OpenClaw, Claude Code, or Antigravity with access to the web, a terminal, and the local skill directory.

> Read https://raw.githubusercontent.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/main/INSTALL_FOR_AGENTS.md, then install and configure MSSHI for me!

| Agent | How to start |
| --- | --- |
| Hermes Agent | `npx skills add https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/tree/main/skills --global --agent hermes-agent`. Or register the catalogue with `hermes skills tap add zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya`, then choose the skills to install. |
| OpenClaw | `openclaw skills install git:zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya --global` installs the entrypoint. For the complete set, use `npx skills add https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/tree/main/skills --global --agent openclaw`. |
| Claude Code | `/plugin marketplace add zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya`, then `/plugin install msshi@msshi-marketplace`. Alternatively, run `npx skills add https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/tree/main/skills --global --agent claude-code`. |
| Claude.ai Web/Desktop | Open **Customize → Skills → + → Upload a skill** and upload the [MSSHI Skill ZIP](portable/msshi.zip). |
| ChatGPT Projects / Custom GPT | Upload the [Knowledge Bundle](portable/MSSHI_ChatGPT_Knowledge_Bundle.md) and paste the [Instructions](portable/CHATGPT_CUSTOM_INSTRUCTIONS.md) into a Project or Custom GPT. |
| Codex CLI | `npx skills add https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/tree/main/skills --global --agent codex` |
| Google Antigravity IDE | `msshi setup --platform antigravity` after installing the CLI. [Skills CLI option and IDE path](INSTALL_FOR_AGENTS.md#google-antigravity-ide). |

**Windows PowerShell**

```powershell
irm https://raw.githubusercontent.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/main/install.ps1 | iex
```

**macOS/Linux**

```bash
curl -fsSL https://raw.githubusercontent.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/main/install.sh | bash
```

The PowerShell or Bash installer adds `msshi` for the current user and opens the setup wizard. Install Git and Python 3.10+ first. Open a new terminal if the command is missing. `npx` requires Node.js 22.20+ and npm. The `main` URLs serve v2.1 after these changes are published.

`msshi check` or `msshi status` compares versions, shows the changelog, and summarizes app routes. `msshi update` updates managed installations and the 37-source cache. `msshi select` chooses packs or skills. `msshi connect` opens the app menu. `msshi setup` opens the four setup modes.

[Agent chat guide](INSTALL_FOR_AGENTS.md) · [Platform and OpenClaw ZIP routes](docs/platforms.md) · [CLI and recovery](docs/CLI.md) · [CLI-Anything application routes](docs/CLI_ANYTHING_BRIDGE.md)

![MSSHI core skills, packs, and the five MuZA roles](assets/msshi-hero-banner.svg)

## 1. Choose a setup mode

![Four setup options with preview, target review, and apply steps](assets/msshi-setup-map.svg)

| Mode | Result |
| --- | --- |
| Solo 1-Bot | All 50 core skills and seven wrappers in a single skill directory. |
| Custom Multi-Bot | Name your bots and assign skills per workspace. |
| Selective Packs | Choose from `core`, `filmmaking`, `business`, `thesis`, `webdev`, and `cybersec`. |
| MuZA 5-Bot Preset | Export the five role workspaces, skills, and editable persona instructions. |

Team exports contain `SOUL.md`, `AGENTS.md`, and `skills/` for each role. Attach those files to the corresponding host profiles. A host with delegation can route work between agents. Other hosts can switch roles within one session or use a written handoff. [Setup and customization guide](PANDUAN_KUSTOMISASI_USER_PUBLIK.md) · [Platform routes](docs/platforms.md).

## 2. Work with the five roles

![How the five roles hand off work and return to the user for review](assets/msshi-architecture-map.svg)

| Role | Responsibility | Reviewable output |
| --- | --- | --- |
| **Yukino Yukinoshita** | Early brainstorming and idea intake | Brief and next-step choices for Shizuka |
| **Sensei Shizuka Hiratsuka** | Directs the team and communicates Val's findings | Synthesized decisions, evidence, and open questions |
| **Val** | Research, literature, and data across undergraduate, graduate, and doctoral work | Source notes, methods, and limitations |
| **Kiki-Chii** | Film, video, photography, motion graphics, audio, and finishing | Storyboard, editable project, and previews |
| **Shikaku Nara** | Coding, vibecoding, web development, and authorized security work | Changes, tests, and remaining risks |

Start with the user's goal and scope. Share the brief, supporting evidence, decisions, and review points when handing off. [MuZA handoff example](docs/ALUR_PRESET_MUZA.md).

## 3. Produce with Kiki-Chii

![Concept, editable drafts, and review for short-form and 10–40 minute projects](assets/msshi-workflow-diagrams.svg)

Use **Concepting First** to align audience, message, duration, style, deliverables, and budget. Create an editable first draft and review it before selecting effects or finishing. For a 10–40 minute video, plan a duration per chapter and keep each scene, audio stem, and source file in a layout that can join a master timeline. Review cuts by timecode. Check continuity, sound, captions, and runtime before final export. Record approved preferences in a private `user_creative_dna.json`. [Creative workflow](docs/ALUR_PRESET_MUZA.md#concepting-first-dan-creative-dna).

## 4. Research and academic work

![Seven academic workflows with concrete outputs](assets/msshi-academic-map.svg)

Choose the workflow that addresses the current obstacle. For a novelty claim, compare the closest studies and document the evidence. For revision, link each reviewer comment to a specific change and verification step. Verify quotations, pages, and numbers before use. [Seven academic workflows](docs/TUJUH_MESIN_AKADEMIK.md).

## 5. Manage long project context

![Five context layers from local indexing to the model evidence packet](assets/msshi-context-layers.svg)

Index the available sources, extract text with page references, select evidence, keep project notes, and set a context budget. Preserve identifiers such as `methods-v2#p12:par3` so a reader can open the original. Context capacity and costs depend on the chosen model and host. [Five context layers](docs/LIMA_LAPIS_KONTEKS.md).

## 6. Integrations, updates, and cost

![What is bundled, what runs locally, and what needs an account](assets/msshi-integration-map.svg)

| Layer | Included or required |
| --- | --- |
| Bundled | Skills, wrappers, personas, installer, CLI, and optional local catalogue API. |
| Local dependencies | Configure apps and adapters such as Blender, ArtCraft MCP, OCR, and CLI-Anything. |
| Account-backed services | Use your own access for Higgsfield, Gemini Notebook, and other services. Their quotas and terms apply. |

The upstream refresh caches 37 sources (35 Git repositories, one model-card source, and one registry). Use the appropriate runtime guide to activate an external integration. TokenShield can evaluate a USD 1.00 reserve using an observed balance and an estimated cost. It relies on those inputs. The CLI-Anything Universal Bridge registers detected or selected routes. Open desktop and web targets with `--open` and invoke installed harnesses with `--run` for an explicit task. Hermes calls native MCP tools for MCP routes. [Connection guide](docs/CLI_ANYTHING_BRIDGE.md). Provider and model choices stay with the user. [Integration inventory](docs/INTEGRASI.md) · [CLI, backups, and recovery](docs/CLI.md).

## 7. Audit and customize

The preset assigns all 50 original skills across the five roles and includes the seven v2.1 wrappers. All five get English/Indonesian Humanizer, OCR, and the universal bridge. Kiki-Chii gets Higgsfield and Motion Graphics Suite. Shikaku gets Antigravity WebDev/Cybersec. The historical folder slug `auto-curiousity-for-film-making` remains available, and MSSHI selection also accepts `auto-curiosity-for-film-making`. [Full per-bot audit](docs/AUDIT_SKILLS_PER_BOT.md) · [Editable matrix](configs/bot_role_and_skill_matrix.json).

## Collaboration credits

- **Muhammad Zidan Aisar (MuZA)** — Creator, System Visionary & Chief Architect.
- **Google Gemini** — Co-Architect for S1–S2–Ph.D. curriculum research, the 50-skill and 37-source synthesis, CLI-Anything and TokenShield architecture, and the five-bot command topology.
- **OpenAI ChatGPT** — Co-Architect for SVG visual engineering, Stage 1 and Stage 2 repository packaging, upstream manifests, and cross-platform schema design.

These credits record contributions to the project. [Provenance and attribution scope](docs/PROVENANCE.md).

## License

The [MIT License](LICENSE) covers original MSSHI materials within the rights of the contributors. Third-party materials, characters, brands, runtimes, and services are subject to their respective terms. [Release checks](docs/STATUS_PUBLIKASI.md) · [Source and rights notes](docs/PROVENANCE.md).
