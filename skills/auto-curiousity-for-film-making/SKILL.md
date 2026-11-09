---
name: auto-curiousity-for-film-making
description: Autonomous curiosity and continuous self-learning skill for filmmaking, videography, and photography. Proactively discovers, probes, and tests new features, tools, parameters, and updates across all 15 ArtCraft MCP applications (FilmCraft, EffectCraft, PhotoCraft, LightCraft, SoundCraft, DesignCraft, VectorCraft, FigCraft, WordCraft, GridCraft, DeckCraft, PDFCraft, CADCraft, SolidCraft, CraftAnything), Blender 5.2+ MCP, FFmpeg, and external creative apps, while scanning and reverse-engineering emerging internet cinematography, editing, color grading, and photography trends into executable workflows connected to filmmaking-videography-photography-s2. Use when exploring new app features, checking software updates, reverse-engineering viral YouTube/Shorts/TikTok/cinema visual trends, or running self-learning experiments.
---
# Auto-Curiousity for Film Making

An autonomous research, experimentation, and continuous self-learning skill that drives the agent to proactively explore new features in ArtCraft and external videography/photography applications, while continuously reverse-engineering emerging internet visual trends into ready-to-use production recipes for `filmmaking-videography-photography-s2`.

## When to Use

- When any ArtCraft MCP app (`filmcraft`, `effectcraft`, `photocraft`, `lightcraft`, `soundcraft`, `designcraft`, `vectorcraft`, `figcraft`, `wordcraft`, `gridcraft`, `deckcraft`, `pdfcraft`, `cadcraft`, `solidcraft`, `craft_anything`), Blender 5.2+ MCP, or external creative software receives an update, new plugin, or new tool schema.
- When encountering an unfamiliar tool, filter, node, shader, LUT slot, or CLI parameter in a videography, photography, 3D, or audio application.
- When the user shares or mentions a viral YouTube video, YouTube Short, TikTok/Reels edit, cinema scene, or photography style and wants the agent to figure out how it was made and how to recreate it.
- When running periodic or idle-time autonomous curiosity sweeps to keep the studio's visual, editing, color grading, and sound design techniques current with internet trends.
- Before kicking off a new project in `filmmaking-videography-photography-s2` when fresh visual hooks, transitions, lighting looks, or newly added ArtCraft features can elevate the production.

## Core Architecture: The 4-Stage Autonomous Curiosity Loop

Execute this 4-stage self-learning loop whenever exploring software updates or internet trends.

### Stage 1: App Update & Feature Discovery Engine (Eksplorasi Update Aplikasi)

Do not wait passively for documentation when an app updates or a new tool appears. Actively inspect and test the environment using a safe micro-sandbox workflow:

1. **Introspect Tool Schemas and Changelogs**:
   - Inspect tool descriptions and JSON schemas for ArtCraft and Blender adapters available on the current host.
   - Check local application directories, `git log`, `CHANGELOG.md`, `--help` outputs, Python module docstrings, and filter registries (such as `ffmpeg -filters`, Blender add-ons, or OpenCV/ImageMagick modules) to detect newly added or updated capabilities.
   - Read `references/app-update-and-artcraft-discovery.md` for exact introspection commands and ArtCraft MCP parameter-probing patterns.

2. **Compare Against Known Capability Snapshot**:
   - Diff discovered tools, parameters, and presets against `curiosity_ledger/app_capabilities_snapshot.json`.
   - Flag any new tool name, new parameter flag, expanded value range, or new file export format as a **Curiosity Target**.

3. **Run Safe Micro-Sandbox Experiments (Eksperimen Mikro Kotak Pasir)**:
   - Never test unfamiliar features directly on a live user project file (`.fcproj`, `.ecproj`, `.soundcraft`, `.blend`).
   - Generate a disposable 2-second test timeline or single test frame inside `curiosity_ledger/sandbox_tests/`.
   - Sweep the new parameter across 3 points (low, default, high), inspect the output metrics (histogram, RGB parade, LUFS loudness, render duration, visual artifacts), and record what the parameter actually does in practice.

### Stage 2: Internet Trend & Visual Culture Horizon Scanner (Pemindai Tren Internet)

Continuously study why top-performing videos and photographs work on the internet and in cinema, then translate those observations into technical parameters:

1. **Scan High-Signal Visual Domains**:
   - Monitor emerging patterns across four domains: **YouTube Long-Form (16:9)** (retention editing, documentary storytelling, educational explainers), **Vertical Shorts / Reels / TikTok (9:16)** (0-3s visual hooks, speed-ramp transitions, kinetic typography), **Festival & Indie Cinema** (Sundance, Cannes, Vimeo Staff Picks, A24 lighting and color aesthetics), and **Contemporary Photography** (editorial lighting, film-stock emulation, optical lens character).

2. **Deconstruct Trends Across 6 Technical Layers**:
   - Break every observed trend down into reproducible numbers rather than vague adjectives. Read `references/internet-trend-deconstruction.md` for the full 6-layer deconstruction matrix:
     - **Layer 1 - Pacing & Retention Math**: Average Shot Length (ASL) in seconds, hook cut cadence in the first 3 to 15 seconds, J-cut/L-cut frame offsets, and pattern-interrupt intervals.
     - **Layer 2 - Camera & Lens Physics**: Focal length equivalent (mm), aperture/T-stop depth-of-field profile, shutter angle (`180-degree` vs staccato `45-90 degree` or dreamy `360-degree` step-printing), and camera motion curves.
     - **Layer 3 - Lighting & Exposure Ratio**: Key-to-Fill contrast ratio (`2:1`, `4:1`, `8:1`), color temperature separation (Kelvin warm/cool contrast), diffusion method (Book Light, China Ball, hard fresnel), and False Color IRE skin-tone placement (`55-70 IRE`).
     - **Layer 4 - Color Science & Look Recipe**: Lift/Gamma/Gain balance, HSL secondary shifts, halation, bloom, film grain size/strength, and LUT/CDL transfer curves.
     - **Layer 5 - VFX, Motion Graphics & 3D Integration**: Keyframe velocity easing (`cubic-bezier`), masking/rotoscoping transitions, 3D camera projection in Blender, and kinetic typography hierarchy.
     - **Layer 6 - Psychoacoustic Sound Layering**: Sub-bass drops, risers, whooshes, foley texture, dialogue sidechain ducking, and integrated loudness target (`-14 LUFS` web / `-24 LKFS` cinema).

### Stage 3: Recipe Synthesis & Persistent Memory (`curiosity_ledger/`)

Convert every verified app discovery and deconstructed internet trend into a reusable **Cinematic Recipe Card** stored in `curiosity_ledger/`:

1. **Log the Discovery**:
   - Append new app capabilities to `curiosity_ledger/artcraft_and_app_updates_log.md`.
   - Append newly deconstructed internet trends to `curiosity_ledger/internet_trend_playbook.md`.
   - Save machine-readable presets to `curiosity_ledger/tested_recipes_registry.json`.

2. **Map Every Recipe to Concrete Tools**:
   - Translate the technique into exact step-by-step tool calls for **ArtCraft MCP** (`filmcraft`, `effectcraft`, `photocraft`, `lightcraft`, `soundcraft`, `designcraft`, `vectorcraft`, `figcraft`), **Blender 5.2+ MCP**, or external CLI/NLE tools so any bot can execute it immediately.

### Stage 4: Seamless Continuity with `filmmaking-videography-photography-s2`

This skill is modular and standalone, yet operates in a continuous feedback loop (`berkesinambungan`) with `filmmaking-videography-photography-s2`:

1. **Pre-Production Injection (Curiosity -> Production)**:
   - When `filmmaking-videography-photography-s2` starts Phase 1 (Story & Visual Development) or Phase 2 (Cinematography & Photography), supply the top 2 to 3 newly discovered ArtCraft features or trending visual/editing recipes from `curiosity_ledger/` that fit the project's mood and platform.

2. **On-Demand R&D Escalation (Production -> Curiosity)**:
   - Whenever `filmmaking-videography-photography-s2` encounters a novel creative request, an unfamiliar app update, or a request to replicate a trending style, trigger `auto-curiousity-for-film-making` to research, sandbox-test, and return a verified execution recipe.

3. **Support Both Single-Bot and Multi-Bot Studio Modes**:
   - **Mode A (Single-Bot One-Man Studio)**: A single Hermes bot runs the curiosity loop first (discovering tools/trends and testing in sandbox) before switching into the 8 production crew roles in `filmmaking-videography-photography-s2`.
   - **Mode B (Multi-Bot 5-Bot Studio Crew)**: Coordinate curiosity across the 5 Hermes personas as detailed in `references/curiosity-sandbox-and-handoff.md`:
     - **Kiki-Chii**: Leads visual trend hunting, photography/color grading experiments (`photocraft`, `lightcraft`, `designcraft`), and creative style remixing with warm, energetic enthusiasm.
     - **Shikaku Nara**: Leads technical MCP schema introspection, app changelog diffs, Blender Python/3D node testing, FFmpeg filter sweeps, and `filmcraft`/`effectcraft`/`soundcraft` pipeline benchmarks.
     - **Shizuka Hiratsuka**: Evaluates how newly discovered trends and tools serve narrative structure, pacing psychology, and emotional resonance before adopting them.
     - **Val**: Curates and indexes the `curiosity_ledger/` documentation, citations, and comparative test logs.
     - **Yukino Yukinoshita**: Manages the curiosity schedule and ensures exploration remains calm, structured, and pressure-free (applying 6 Dimensions of Parenting and GAD/MDD support).

## Reference Modules

Load these bundled reference files via `get_skill_resources` when executing specific stages:

- `references/app-update-and-artcraft-discovery.md` - Protocol for inspecting ArtCraft MCP updates, Blender 5.2+ MCP schemas, external video/photo app changelogs, and running safe micro-sandbox tests.
- `references/internet-trend-deconstruction.md` - Complete 6-Layer Reverse-Engineering system for turning viral YouTube, Shorts/Reels/TikTok, Cinema, and Photography trends into exact technical numbers and ArtCraft commands.
- `references/curiosity-sandbox-and-handoff.md` - Schema for `curiosity_ledger/`, Recipe Card templates, and the bidirectional handoff protocol with `filmmaking-videography-photography-s2` across 1-Bot and 5-Bot modes.

## Gotchas

- **Never overwrite live project files during curiosity testing**: Always run feature probes in `curiosity_ledger/sandbox_tests/` on synthetic or copy assets before applying a new feature to a user's active film or photo project.
- **Never adopt a trend blindly without narrative alignment**: A fast whip-pan or hyper-cut transition that works for a 15-second gaming Short can ruin an intimate cinematic short film or Mommy ASMR video; always filter trend recipes through the project's target emotion and pacing in `filmmaking-videography-photography-s2`.
- **Never alter existing provider or model settings during tool exploration**: Exploring new ArtCraft MCP tools or external creative software must never modify the user's locked LLM `provider` or `model` configurations (Main Agent, Sub-Agent, or MoA).


## 6. Concept-First Workflow, Motion-Graphics-as-Code & User-Adaptive Evolution

Whenever the user asks to create a video, film, promo, or visual piece, strictly follow this 3-stage adaptive workflow:

### Stage A: Concepting First (Co-Creation with the Filmmaker)
1. **Never jump straight into rendering or opening heavy apps**: First, the Filmmaker persona engages the user in an interactive **Concepting Session**:
   - Clarify the **Core Emotion** (Walter Murch's 51% rule), **Target Platform & Aspect Ratio** (`16:9` YouTube, `9:16` Shorts/Reels/TikTok, or `2.39:1` Cinema), **3-Second Visual Hook**, and **Visual/Audio Tone**.
   - Present 2 to 3 concise concept directions and lock in the user's choice before touching any production tool.

### Stage B: Concept-Driven Skill & Tool Selector (Motion-as-Code + ArtCraft + Blender)
Once the concept is approved, choose a production stack from the ArtCraft, Blender, and four motion references that are available and fit the brief:

| Approved Concept Type | Primary Skills & Repositories Invoked | Execution Engine |
| :--- | :--- | :--- |
| **1. Launch Video, SaaS/Product Promo, or Animated Data Charts** | [`remotion-dev/skills`](https://github.com/remotion-dev/skills) + [`charlie947/motion-graphics-skills`](https://github.com/charlie947/motion-graphics-skills) | React/TypeScript programmatic frame rendering (`Remotion` + 15 launch-grade motion-as-code skills) -> `soundcraft` (`-14 LUFS`). |
| **2. Dynamic B-Roll, Kinetic Typography & Explainer Sequences** | [`Barty-Bart/motion-graphics`](https://github.com/Barty-Bart/motion-graphics) + [`bangtutorial/bang-motion`](https://github.com/bangtutorial/bang-motion) | Browser-native HTML/CSS/Canvas motion sequences (`index.html` playing like 60fps video) + `effectcraft` compositing. |
| **3. Narrative Short/Feature Film, Documentary, or Cinematic Vlog** | `filmmaking-videography-photography-s2` + `auto-curiousity-for-film-making` | `wordcraft` (AV/Fountain script) -> `blender` (3D camera/lighting previz) -> `lightcraft`/`photocraft` (4-Node ACES grade) -> `filmcraft` (`.fcproj`) -> `soundcraft`. |

### Stage C: Dual Evolution Engine (GitHub Updates + User-Adaptive DNA Over Time)
The filmmaking and curiosity system evolves along two independent axes:
1. **External Evolution (Internet Trends & GitHub Updates)**: Continuously learns new app features and internet visual trends via `auto-curiousity-for-film-making` and pulls repository updates via `msshi-update`.
2. **User-directed Creative DNA (`curiosity_ledger/user_creative_dna.json`)**:
   - Copy the package's empty `configs/user_creative_dna.json` template to a private project directory. Use the preferences the user has provided.
   - If the user opts in, suggest changes after a project. Save a preference only when they approve that change.

### Stage D: Higgsfield AI Model Catalog & Virality Predictor Probing (`higgsfield-ai/skills`)
Proactively tracks new models, motion presets, and photoshoot modes in [`higgsfield-ai/skills`](https://github.com/higgsfield-ai/skills) (`higgsfield model list / workflow list`, `Seedance 2.5`, `Veo 3.1`, `Kling 3.0`, `GPT Image 2.6`, `Nano Banana Pro 4K`, `Soul V2`, and `Virality Predictor`) and feeds verified prompt/camera recipes directly into **Kiki-Chii's** unified `filmmaking-videography-photography-s2` pipeline.
