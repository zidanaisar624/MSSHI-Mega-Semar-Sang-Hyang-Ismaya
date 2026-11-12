# Install MSSHI for your agent · Panduan instalasi MSSHI

MSSHI bundles reusable Agent Skills and a public installer. Choose the route that fits your host. The installer can add the suite and prepare persona workspaces. Platform tools, connectors, credentials, and genuine multi-agent execution depend on your host.

## Install from an agent chat

Paste this message into Hermes Agent, OpenClaw, Claude Code, or Antigravity if the session can read the link and use a terminal on the target machine.

> Tolong baca https://raw.githubusercontent.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/main/INSTALL_FOR_AGENTS.md lalu instal dan konfigurasikan MSSHI untukku!

### Agent runbook

1. Confirm the target agent, profile or workspace, and desired scope. For a new public setup, offer Solo, Custom Multi-Bot, Selective Packs, and the MuZA five-role preset. Default to a Solo preview when no existing installation or role preference is evident. Respect the host's sandbox and existing authorization.
2. Use the canonical [MSSHI GitHub repository](https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya). Check `VERSION.json`, `LICENSE`, and the scripts for the selected route. Clone into a new or explicitly selected directory. Do not overwrite an existing checkout with local changes. If the user supplied a ZIP, inspect its contents and source before extracting to a separate directory.
3. From the checkout root, run `python scripts/check_release.py` to validate the package. Preview the requested setup with the direct installer. Specify `--target-dir` if the profile or target is ambiguous. Use `py -3` on Windows or `python3` on macOS/Linux if `python` is unavailable. For web-only hosts, use the upload path below instead of a local installer.
4. State the exact destination, scope, and anticipated changes. Apply the reviewed plan when covered by the user's request. Keep provider, model, credentials, existing `SOUL.md`, and `user_creative_dna.json` intact. Use the configured application's profile management UI or documented commands when a persona workspace needs linking.
5. Verify the actual files and, where available, the host's skill list. Report the version, path, count, and what still depends on host setup. Use a fresh session to refresh discovery. If shell, GitHub, attachments, or an install action is unavailable, give the matching manual route and say which step remains.
6. Keep upstream repositories separate from the installed skill folders. Download external references only when the user requests an update or upstream fetch. A downloaded repository needs its own review and setup before use. Keep paid jobs and app startup on demand.

### Connect apps in Hermes

If the user asks to connect apps, offer **Auto-Reconnect All** or **Pick apps**. Inspect the selected Hermes profile with `msshi connect --mode auto-reconnect --dry-run` or list targets with `msshi connect --catalog`. Apply the chosen scope. The bridge registers routes per profile and leaves app launching until an explicit task. Use Hermes native tools for MCP routes. If the global CLI is unavailable, the standalone bridge skill includes the same connector commands. [Connection guide](docs/CLI_ANYTHING_BRIDGE.md).

### Reviewable local setup

Requirements for the MSSHI installer are Python 3.10+ and Git for remote retrieval. From a terminal, clone the repository into a directory you choose, then open that directory. These commands preview the install without writing skills.

```sh
git clone https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya.git
cd MSSHI-Mega-Semar-Sang-Hyang-Ismaya
python scripts/check_release.py
python scripts/install_msshi.py --platform hermes --mode solo
```

For the last command, replace `hermes` with `openclaw`, `claude`, `codex`, or `antigravity` as appropriate. Add `--target-dir <path>` for a particular profile or workspace. Run it with `--apply` to install after reviewing the plan. The team modes create role workspaces. Connect those workspaces to your host's actual agents when the host supports that.

## Terminal and upload routes

### Hermes Agent

Install the collection into the selected Hermes environment with Skills CLI. Set the intended `HERMES_HOME` first if you use a nondefault profile.

```sh
npx skills add https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/tree/main/skills --global --agent hermes-agent
```

Hermes Tap registers the repository as a browsable source. Install entries from the tap after registering it.

```sh
hermes skills tap add zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya
hermes skills install zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/wise-judgment-and-sovereign-orchestrator
```

For the managed MSSHI CLI, use one of the following after reviewing the installer. Run `msshi setup` to choose a mode if the installer did not open the wizard.

```powershell
irm https://raw.githubusercontent.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/main/install.ps1 | iex
```

```sh
curl -fsSL https://raw.githubusercontent.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/main/install.sh | bash
```

[Hermes Agent skills documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/).

### OpenClaw

Install the master entrypoint as one shared skill. To install the individual skills, use the scoped Skills CLI command instead.

```sh
openclaw skills install git:zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya --global
npx skills add https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/tree/main/skills --global --agent openclaw
```

For Telegram, Discord, or Web chat, attach [msshi.zip](portable/msshi.zip) and type **install this skill** if your OpenClaw agent can read that attachment and is authorized to install it. A GitHub source ZIP can also be used by an agent that can extract and inspect the repository. ZIP handling depends on the channel and Gateway permissions. If chat cannot install it, use **Plugins → Skills → Import** in the Control UI for an identified Gateway profile. The compact ZIP is one master skill with a method reference. An identified operator can also run `openclaw skills library import ./msshi.zip --slug msshi`. For a local shared install without the library, extract the ZIP and run `openclaw skills install ./msshi --global` from the parent folder. Use `openclaw skills list` on the intended Gateway to verify file-backed discovery. [OpenClaw Skills CLI](https://docs.openclaw.ai/cli/skills) · [OpenClaw skill scopes and imports](https://docs.openclaw.ai/tools/skills).

### Claude Code

In a Claude Code session, add the marketplace and then select its plugin.

```text
/plugin marketplace add zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya
/plugin install msshi@msshi-marketplace
```

Alternatively, install the individual skills from a terminal.

```sh
npx skills add https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/tree/main/skills --global --agent claude-code
```

[Claude Code marketplaces](https://code.claude.com/docs/en/plugin-marketplaces).

### Claude.ai web or Claude Desktop chat

Download [msshi.zip](portable/msshi.zip). In Claude, go to **Customize → Skills → + → Upload a skill** and select that ZIP. Enable **Code execution and file creation** if Claude requires it for custom skills on your account. If you already used **Code → Download ZIP** on GitHub, extract it and upload `portable/msshi.zip` from inside. The compact ZIP has the required `msshi/SKILL.md` layout and a readable reference, with the folder matching its frontmatter name. [Claude custom skill packaging](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills).

### ChatGPT web or desktop

For a **ChatGPT Project**, upload [MSSHI_ChatGPT_Knowledge_Bundle.md](portable/MSSHI_ChatGPT_Knowledge_Bundle.md) under **Sources**, and paste one mode from [CHATGPT_CUSTOM_INSTRUCTIONS.md](portable/CHATGPT_CUSTOM_INSTRUCTIONS.md) into **Project instructions**. In a **Custom GPT** editor, where available, use **Knowledge** and **Instructions** for the same two parts. Five Persona mode applies five roles within a conversation. Actual delegation needs a host that supports separate agents and exposes their tools. [ChatGPT Projects](https://learn.chatgpt.com/docs/projects) · [Custom GPT knowledge and instructions](https://learn.chatgpt.com/docs/migrate-custom-gpts).

### Codex CLI

```sh
npx skills add https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/tree/main/skills --global --agent codex
```

The normal user-wide Codex skills directory is `~/.agents/skills/`. Use a new session to check skill discovery. [OpenAI skill installation paths](https://developers.openai.com/api/reference/cli).

### Google Antigravity IDE

After installing the MSSHI CLI, use its Antigravity setup route.

```sh
msshi setup --platform antigravity
```

From a local checkout, preview with `python scripts/install_msshi.py --platform antigravity --mode solo` and add `--apply` to install. For manual installation, copy each selected `skills/<slug>/` directory into `~/.gemini/config/skills/` (Windows `%USERPROFILE%\.gemini\config\skills\`). In Antigravity, check **Customizations → Skills & Rules**. [Google Antigravity skills](https://antigravity.google/docs/skills?app=antigravity-ide).

The following Skills CLI route requires a release that uses `~/.gemini/config/skills/` for global Antigravity skills. The npm 1.7.6 release uses the shared `~/.agents/skills/` root, while the fix is on the Skills CLI main branch. Verify the destination before choosing this route. [Published 1.7.6 configuration](https://github.com/vercel-labs/skills/blob/7a5e920bead4b1039a6d6df5d7e1163b7b09423a/src/agents.ts#L96-L115) · [Current Skills CLI source](https://github.com/vercel-labs/skills/blob/main/src/agents.ts).

```sh
npx skills add https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/tree/main/skills --global --agent antigravity
```

### Master entrypoint and full collection

Skills CLI requires Node.js 22.20 or newer. A plain `npx skills add zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya --global --agent <agent>` selects the root `msshi` skill. The `/tree/main/skills` URLs above target the collection so you can select individual entries. Add `--skill '*'` if you want every entry in that scope. For the agent identifiers and discovery behavior, see [supported agents](https://github.com/vercel-labs/skills/blob/main/docs/agents.md) and [Skills CLI discovery](https://github.com/vercel-labs/skills/blob/main/src/skills.ts).

## Check and maintain an MSSHI-managed installation

| Command | What it does |
| --- | --- |
| `msshi setup` | Select one of the four public modes and preview the target before installation. |
| `msshi check` or `msshi status` | Compare the active MSSHI package version with GitHub `VERSION.json` and show the changelog. Individual installed skills may differ after a selective update. |
| `msshi update` | Refresh the managed suite and fetch upstream references. Preserve local customizations and keep backups of applicable persona and Creative DNA files. |
| `msshi connect` | Discover and register lazy application routes for the chosen Hermes profile. |
| `msshi select` | Choose packs or individual skills and review the change before applying. |

Choose one installation manager per destination. Native marketplaces and Skills CLI track their own installs, while MSSHI tracks the targets registered with its setup or selection wizard. If you have custom skill files in a destination, preserve a copy before reinstalling there with Skills CLI.

## REA is optional and OFF by default

The REA wrapper lives in `optional/rea`, outside the standard `skills` directory. Do not interpret a request to install MSSHI or all standard packs as permission to enable REA. Offer it as a separate default-No choice; use `--with-rea` or `msshi optional enable rea --target-dir ...` only after the user explicitly selects it. Runtime setup never authorizes MCP/global agent registration, model changes, personal browser sessions, or paid native engines.
