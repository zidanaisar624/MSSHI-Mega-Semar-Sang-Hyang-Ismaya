---
name: filmmaking-videography-photography-s2
description: Filmmaking, videography and photography workflows for solo or team projects, with optional ArtCraft and Blender adapters.
---

# Filmmaking, Directing, Videography, and Photography (S1-S2 MFA Curriculum)

Use this practical reference for film directing, screenwriting, cinematography (videography), still photography, editing, color grading, sound design, and production management across short-form vertical media (YouTube Shorts, Reels, TikTok), long-form YouTube videos (documentaries, video essays, tutorials), and narrative cinema.

## When to Use

- The user asks to plan, write, direct, shoot, edit, color-grade, or produce a short film, feature film, YouTube video, documentary, commercial, or social media video.
- The user wants a single bot to act as a complete "One-Man Film Studio" (handling all roles from Director and DP to Editor) or wants multiple bots (Shizuka, Kiki-Chii, Shikaku, Val, Yukino) to divide film crew departments.
- The user needs technical guidance on videography or photography (exposure triangle, lenses, lighting setups, composition, color science, camera movement, or audio engineering).
- The user wants to execute a media production workflow in Hermes using ArtCraft MCP servers (`filmcraft`, `effectcraft`, `photocraft`, `lightcraft`, `soundcraft`, `designcraft`, `vectorcraft`, `figcraft`, `deckcraft`, `wordcraft`, `gridcraft`, `craft_anything`), Blender MCP, or FFmpeg.

## Step 1: Select Crew Operating Mode (Single-Bot vs. Multi-Bot Crew)

Determine whether the project runs in **Mode A (Single-Bot Full-Stack Filmmaker)** or **Mode B (Multi-Bot Studio Crew)**:

1. **Mode A - Single-Bot "One-Man Studio" (1 Bot = All 8 Crew Roles)**:
   - One bot sequentially executes all 8 department heads: (1) Executive/Line Producer, (2) Screenwriter, (3) Film Director, (4) Director of Photography (DP) / Master Photographer, (5) Production Designer / Gaffer, (6) Lead Editor, (7) Colorist & VFX Supervisor, and (8) Sound Designer / Re-Recording Mixer.

2. **Mode B - MuZA Studio Crew**:
   - **Shizuka Hiratsuka (Coordinator)**: Sets scope, aligns handoffs, synthesizes findings, and brings decisions to the user.
   - **Kiki-Chii (Creative Lead)**: Owns the creative brief, direction, script, photography, editing, effects, audio and preview, with user review before finalization.
   - **Shikaku Nara (Technical Support)**: Handles approved code, rendering automation and integration checks as needed.
   - **Val (Research)**: Checks evidence and source material, then shares findings and uncertainty with Shizuka.
   - **Yukino Yukinoshita (Ideation and Pacing)**: Helps shape an initial brief and user-selected production pacing.

See the [crew role reference](references/single-vs-multibot-crew-roles.md) for handoffs.

## Step 2: Execute the 5-Phase S1-S2 MFA Production Pipeline

### Phase 1: Development & Screenwriting (Story Architecture)

1. Choose the structural paradigm matched to the target medium:
   - **Short-Form Vertical (9:16, 15-60s)**: Hook (0-3s visual + verbal disruption) -> Setup/Stakes (3-10s) -> Escalating Value/Beats (10-45s, visual change every 2-3s) -> Payoff & Loop/CTA (45-60s).
   - **Long-Form YouTube (16:9; preset Kiki-Chii 10–40 min)**: Cold Open Hook (0-15s confirming click promise) -> Retention Bridge & Thesis Stakes (15-45s) -> Chaptered Story/Analysis Segments with Pattern Interrupts every 60-90s -> Climax Payoff -> Native Outro.
   - **Alur produksi 10–40 menit**: Susun outline bab dan target durasi, buat naskah serta rough cut per segmen, review dengan timecode, lalu cek durasi total, kontinuitas, audio dan subtitle di timeline master sebelum meminta persetujuan ekspor.
   - **Narrative Cinema / Anime Short or Feature**: 3-Act Structure (Setup, Confrontation, Resolution), Dan Harmon's 8-Step Story Circle, Blake Snyder's 15 Beats, or 4-Act Japanese **Kishotenketsu** (Ki: Introduction, Sho: Development, Ten: Twist/Subversion, Ketsu: Reconciliation).
2. Draft the script in **Fountain Screenplay Format** (for narrative film, 1 page = ~1 minute screen time) or **Two-Column Audio/Visual (AV) Script** (Left column: Spoken Dialogue/VO + SFX/Music at ~130-150 WPM; Right column: Shot Size, Camera Movement, B-Roll, and Text On-Screen).

See `references/mfa-directing-screenwriting.md` for full lecture notes and templates.

### Phase 2: Pre-Production & Directing (Mise-en-Scene, Coverage & Scheduling)

1. Translate subtext into physical staging (**Blocking & Mise-en-Scene**): define character objectives, obstacles, tactics, and spatial power dynamics (vertical height, proximity, depth).
2. Build the **Master Shot List & Coverage Plan**:
   - Establish geography with an Establishing / Wide Shot (EWS/WS), anchor conversation with Medium Shots (MS) and Over-the-Shoulder (OTS), and reserve Close-Ups (CU/ECU) for emotional turning points.
   - Maintain the **180-Degree Axis of Action Rule** and **30-Degree Camera Angle Rule** so cuts never jar spatial orientation unless deliberately signaling psychological disorientation.
3. Lock the **Shooting Schedule (1st AD Stripboard)**: group shots by location, lighting direction, and lens size rather than chronological script order to minimize setup turnaround.

### Phase 3: Cinematography (Videography) & Master Photography

Apply rigorous optical and photographic physics to every frame (real camera, Blender 3D camera, or AI visual prompt):

1. **Exposure Triangle & Motion Physics**:
   - **Aperture (f-stop)**: Controls Depth of Field (DoF) and light intake ($f/1.4 - f/2.8$ for shallow subject isolation; $f/5.6 - f/11$ for deep sharpness).
   - **Shutter Speed & 180-Degree Rule**: In videography, lock shutter angle to $180^\circ$ where $\text{Shutter Speed} = \frac{1}{2 \times \text{FPS}}$ (e.g., $24\text{ fps} \rightarrow 1/48\text{s}$ or $1/50\text{s}$; $60\text{ fps} \rightarrow 1/120\text{s}$) for natural motion blur. Use Neutral Density (ND) filters outdoors rather than cranking shutter speed.
   - **ISO & Dynamic Range**: Expose at the sensor's Native / Dual-Native ISO to maximize dynamic range and signal-to-noise ratio (SNR). Place Caucasian/Asian skin tones around **60-70 IRE** on False Color / Zebra meters; protect highlights in Log profiles (S-Log3, C-Log, V-Log, ARRI LogC).
2. **Optics & Focal Length Psychology**:
   - **14mm-24mm (Ultra-Wide/Wide)**: Expands space, exaggerates depth and movement, creates dynamic tension or claustrophobic distortion up close.
   - **35mm-50mm (Standard/Natural Human Vision)**: Grounded documentary intimacy and natural perspective (`35mm` environmental portrait; `50mm` classic human eye).
   - **85mm-135mm+ (Telephoto)**: Compresses background distance, isolates the subject with creamy bokeh, and intensifies emotional focus.
3. **Lighting Design & Inverse Square Law ($I \propto 1/d^2$)**:
   - Design **Motivated Lighting**: every Key Light, Fill Light, and Back/Rim (Hair) Light must have a believable diegetic source (window, lamp, street neon, monitor glow).
   - Control **Lighting Ratios**: **2:1** (High-Key, beauty, upbeat YouTube), **4:1** (Natural dramatic narrative, Rembrandt triangle), **8:1+** (Low-Key, Film Noir, Chiaroscuro tension).
   - Balance **Color Temperature (Kelvin)**: Warm Tungsten/Candlelight (`2700K-3200K`) vs. Daylight (`5600K`) vs. Cool Shade/Moonlight (`6500K-8000K`). Use mixed color temperatures (e.g., `3200K` warm key against `5600K` cool background fill) for instant cinematic color separation.

See `references/mfa-cinematography-photography.md` for full mathematical formulas and lighting diagrams.

### Phase 4: Post-Production (Editing, Color Grading, VFX & Sound Design)

1. **Film Editing - Walter Murch's Rule of Six**:
   Evaluate every cut in strict priority order:
   - (1) **Emotion (51%)**: Does the cut serve the emotional truth of the moment?
   - (2) **Story (23%)**: Does the cut advance the narrative or thesis?
   - (3) **Rhythm (10%)**: Does the cut happen at the right musical/cadence beat?
   - (4) **Eye-Trace (7%)**: Does the viewer's focus land cleanly on the next frame's point of interest?
   - (5) **2D Plane of Screen (5%)**: Does the cut respect screen direction and axis?
   - (6) **3D Space of Action (4%)**: Does the cut preserve physical room continuity?
2. **J-Cuts, L-Cuts & Montage**:
   - Lead audio by 4-15 frames before the video cut (**J-Cut**) or trail audio into the next shot (**L-Cut**) so dialogue and transitions breathe naturally.
3. **Color Correction & Color Grading**:
   - Transform Log footage to Working Color Space (**ACEScct / DaVinci Wide Gamut**), balance exposure on the **Waveform** (0-100 IRE), neutralize white balance on the **RGB Parade**, align skin tones along the **Vectorscope Skin-Tone Line**, apply creative look/palette, and output to **Rec.709 (Gamma 2.4)**.
4. **Sound Design & Loudness Mastering**:
   - Layer **Dialogue/VO** (centered, high-pass filter at `80-100 Hz`, gentle 3:1 compression, de-esser, peaking at `-6 dBFS` to `-3 dBFS`), **Room Tone / Ambience** (`-30` to `-24 dBFS`), **Foley & SFX** (`-18` to `-10 dBFS`), and **Music Score** (ducked to `-24` to `-18 dBFS` under voice).
   - Master integrated loudness to **`-14 LUFS` (`-1.0 dBTP` True Peak)** for YouTube/Social Platforms or **`-24 LKFS` (`-2.0 dBTP`)** for Cinema/Broadcast.

### Phase 5: Hermes ArtCraft & Blender Cross-App Execution

When executing inside Hermes on Windows (`D:\HermesData`), chain the local MCP servers using explicit saved files in a dedicated project subfolder:

1. **`craft_anything`** (`project.cany`): Write the creative brief, research evidence, and production plan (`core_brief_write`, `core_plan_update`, `core_report_save`).
2. **`wordcraft`** (`.docx`/`.pdf`) & **`gridcraft`** (`.xlsx`): Generate the Fountain/AV Script, Call Sheet, Shot List, and Budget (`new_document`, `new_workbook`, `write_range`).
3. **`designcraft`** (`.designcraft`) / **`figcraft`** (`.figcraft`) / **`vectorcraft`** (`.svg`): Build storyboards, moodboards, title cards, and lower-thirds.
4. **`blender`** (`.blend`): Build 3D camera pre-visualization (previz), test lens focal lengths (24mm/35mm/50mm/85mm), simulate 3-point lighting, and render 3D sequences.
5. **`photocraft`** & **`lightcraft`**: Composite thumbnails/stills (`doc_new`, `doc_save`, `doc_export`) and develop/color-grade photo libraries (`import`, `set_develop`, `export`).
6. **`filmcraft`** (`.fcproj`), **`effectcraft`** (`.ecproj`), & **`soundcraft`** (`.soundcraft`): Import media (`media_import`), assemble timeline sequences, animate keyframes (`add_keyframe`, `render_frame`), mix audio (`import_audio`, `bounce_mix`), and render final preview/export (`render_preview`).

See `references/mfa-editing-color-sound-artcraft.md` for complete ArtCraft MCP command workflows.

## Gotchas

- Never sacrifice **Emotion (51%)** and **Story (23%)** for flashy transitions or unmotivated camera movement.
- In `lightcraft`, only one process can hold an active library lock at a time; close GUI locks before running CLI MCP operations.
- Always save native project files (`.fcproj`, `.ecproj`, `.soundcraft`, `.designcraft`, `.blend`) alongside exported deliverables (`.mp4`, `.png`, `.wav`, `.pdf`) so edits can be resumed without starting from scratch.


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

### Stage D: Unified Higgsfield AI Cinema, Videography & Photography Pipeline (`higgsfield-ai/skills`)
All filmmaking, videography, and photography workflows are unified into a single skill integrating [`higgsfield-ai/skills`](https://github.com/higgsfield-ai/skills) alongside ArtCraft MCP, Blender 5.2+, and the 4 Motion-Graphics-as-Code repositories. See `references/higgsfield-ai-cinema-photo-suite.md`:
- **AI Cinema & Videography (`higgsfield-generate` + `higgsfield-faceless-video` + `higgsfield-video-explainer`)**: Directs 30+ generative engines (`Seedance 2.5` with `omni_reference`, `Veo 3.1`, `Kling 3.0`, `Seed Audio 1.0`), 9 **Marketing Studio** commercial/UGC modes, and **Virality Predictor** (`brain_activity`) hook/retention scoring.
- **Character & Actor Continuity (`higgsfield-soul-id`)**: Trains reusable face-faithful identity tokens (`--soul-id`) so characters stay consistent across every frame and camera angle.
- **Master Still Photography & Brand Visuals (`higgsfield-product-photoshoot` + `higgsfield-brandkit` + `higgsfield-marketplace-cards` + `higgsfield-youtube-thumbnail`)**: Combines MFA optical physics (Exposure Triangle, 24mm/35mm/50mm/85mm lenses, Rembrandt/Book lighting, ACES/Rec.709 grading in `LightCraft`/`PhotoCraft`) with 10 commercial photoshoot modes, Recraft SVG brandkits, and 4K YouTube/Shorts thumbnails (`Nano Banana Pro 4K`).
- **Kiki-Chii Total Creative Command (MuZA Ecosystem Default)**: In the MuZA preset, **Kiki-Chii** leads the combined creative workflow. Start with **Concepting First**, then choose the tools that are available. Apply project Creative DNA with the user's permission.
