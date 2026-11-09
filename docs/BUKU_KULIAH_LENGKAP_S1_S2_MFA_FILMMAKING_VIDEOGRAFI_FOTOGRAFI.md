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

See the [crew role reference](../skills/filmmaking-videography-photography-s2/references/single-vs-multibot-crew-roles.md) for handoffs.

## Step 2: Execute the 5-Phase S1-S2 MFA Production Pipeline

### Phase 1: Development & Screenwriting (Story Architecture)

1. Choose the structural paradigm matched to the target medium:
   - **Short-Form Vertical (9:16, 15-60s)**: Hook (0-3s visual + verbal disruption) -> Setup/Stakes (3-10s) -> Escalating Value/Beats (10-45s, visual change every 2-3s) -> Payoff & Loop/CTA (45-60s).
   - **Long-Form YouTube (16:9, 8-25+ min)**: Cold Open Hook (0-15s confirming click promise) -> Retention Bridge & Thesis Stakes (15-45s) -> Chaptered Story/Analysis Segments with Pattern Interrupts every 60-90s -> Climax Payoff -> Native Outro.
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


---

# S1-S2 MFA Module 1: Directing, Screenwriting, and Story Architecture
*(Synthesized from USC School of Cinematic Arts, AFI Conservatory, and NYU Tisch Graduate Film Curricula)*

## 1. Narrative Architecture Across Formats

### A. Narrative Cinema & Short Films (3-Act, Story Circle, Save the Cat, Kishotenketsu)
1. **Classical Three-Act Dramatic Structure (Syd Field / Robert McKee)**:
   - **Act I - Setup (0% - 25%)**: Establish the Protagonist's Status Quo (Lie They Believe), Inciting Incident (~10%), and Plot Point 1 / Threshold (~25%) where the protagonist makes an irreversible choice.
   - **Act II - Confrontation (25% - 75%)**: Rising action & Fun and Games (25% - 50%), **Midpoint Shift (50%)** (false victory or false defeat that raises the stakes and shifts the protagonist from *reactive* to *proactive*), Bad Guys Close In (50% - 75%), **All Hope Is Lost / Dark Night of the Soul (~75%)**.
   - **Act III - Resolution (75% - 100%)**: Synthesis of External Want and Internal Need, Climax (80% - 92%) where the protagonist proves transformation through action, and Denouement / New Equilibrium (92% - 100%).
2. **Japanese / Anime 4-Act Structure (Kishotenketsu - 起承転結)**:
   - Ideal for atmospheric, slice-of-life, philosophical, or anime-inspired storytelling (e.g., Makoto Shinkai, Kyoto Animation, Oregairu):
     - **Ki (起 - Introduction)**: Introduce characters, setting, and emotional baseline.
     - **Sho (承 - Development)**: Deepen relationships and daily rhythms without requiring violent conflict.
     - **Ten (転 - Twist / Shift in Perspective)**: Introduce an unexpected angle, revelation, or juxtaposition that reframes everything seen in Ki and Sho.
     - **Ketsu (結 - Reconciliation / Resonance)**: Bring Ki, Sho, and Ten into emotional harmony, leaving a lingering thematic resonance (*Mono no Aware* / *Ma* - the beauty of negative space and pause).

### B. YouTube Long-Form (16:9) Retention Engineering (8 - 30+ Minutes)
1. **The 0-30 Second Golden Window**:
   - **0-5s (Click Confirmation)**: Immediately validate the title and thumbnail promise—zero channel intros, zero "Hey guys, welcome back".
   - **5-15s (Curiosity Gap / Stakes)**: Open a specific narrative loop or question that can only be resolved by watching through the video.
   - **15-30s (Retention Bridge / Proof of Value)**: Show a brief preview of the scale of the experiment, story, or framework so the viewer trusts the journey.
2. **Body Architecture (Mini-Hooks & Pattern Interrupts)**:
   - Structure the body into 3 to 5 distinct chapters. End each chapter with a **Mini-Cliffhanger ("But that created a bigger problem...")** rather than a flat summary so retention never drops at chapter boundaries.
   - Insert a **Pattern Interrupt every 60-90 seconds**: change framing (WS to CU), switch from A-roll to B-roll/diagram, shift music stems, or introduce a tangible prop/screen recording.
3. **The Ending (Zero Pre-Roll Sign-Off)**:
   - Deliver the final payoff and transition into the next recommended video within the final 10 seconds without saying "In conclusion" or "Thanks for watching" (which triggers immediate viewer drop-off).

### C. Short-Form Vertical (9:16 - YouTube Shorts, Reels, TikTok, 15-60 Seconds)
- **0-2s (Visual + Verbal Hook)**: Motion in Frame 1 + bold 3-5 word on-screen caption + punchy opening statement.
- **2-12s (Compression of Context)**: Cut all throat-clearing; establish the conflict or insight immediately.
- **12-50s (Rapid Escalation)**: Average Shot Length (ASL) of **1.5 to 2.5 seconds** (via physical cuts, punch-ins, B-roll overlays, or dynamic captions).
- **50-60s (Payoff + Seamless Loop)**: Connect the final sentence grammatically or rhythmically back into the first 2 seconds for >100% loop retention.

---

## 2. The Director's Craft: Mise-en-Scene, Subtext, and Blocking

### A. Translating Subtext into Visuals ("Show, Don't Tell")
A film director never directs "emotions" (e.g., "act sad" or "act angry"); a director directs **Actionable Verbs (Tactics)** driven by an **Objective** against an **Obstacle**:
- Instead of telling an actor or voice actor "be nervous," give a playable action: *"Try to convince your partner everything is fine while hiding the trembling in your hands."*

### B. Blocking & Spatial Geometry (3 Shapes of Staging)
1. **The I-Formation (Confrontation / Intimacy)**: Two characters face each other directly on a single axis.
2. **The A-Formation (Triangle Staging)**: Two characters face each other while a third anchor point (an object, a window, or a third character in depth) forms the apex of a triangle in the frame.
3. **The L-Formation (90-Degree Tension)**: One character looks straight ahead while the other looks at them from a perpendicular angle (classic for unspoken tension or emotional distance, as seen frequently in *Oregairu* clubroom scenes).

### C. Standard Two-Column AV Script & Shot List Template

| Scene / Beat | Timecode | Visual / Camera / Lighting (DP & Art Direction) | Audio / Dialogue / SFX / Music (Sound & Prosody) |
| :--- | :--- | :--- | :--- |
| **1A - HOOK** | `00:00 - 00:04` | **CU** (85mm, f/2.0, 1/50s, 3200K warm key left, 5600K cool rim). Slow dolly-in on subject's eyes. | **[SFX]**: Low sub-bass riser (`-16 dBFS`) + crisp clock tick.<br>**[VO - Shizuka]**: *(Calm contralto, 0.93x)* "Satu kesalahan kecil di baris kode ini..." |
| **1B - REVEAL** | `00:04 - 00:10` | **Match Cut to EWS** (24mm, f/4.0). Screen illuminates dark room in teal glow. | **[SFX]**: Soft mechanical keyboard thock.<br>**[MUSIC]**: Minimalist lo-fi piano enters (`-22 dBFS`). |


---

# S1-S2 MFA Module 2: Cinematography (Videography) & Master Photography
*(Optical Physics, Exposure Science, Lighting Ratios, and Visual Composition)*

## 1. Exposure Science & Sensor Physics

### A. The Exposure Triangle & Reciprocity
Total luminous exposure $H$ reaching the sensor plane is governed by scene luminance $L$, lens T-stop/f-number $N$, and exposure time (shutter speed) $t$:
$$H = \frac{q \cdot L \cdot t}{N^2}$$
1. **Aperture ($N = f/D$)**:
   - Full-stop scale: $f/1.0, f/1.4, f/2.0, f/2.8, f/4.0, f/5.6, f/8.0, f/11, f/16, f/22$.
   - Each full stop halves the light area ($\div 2$) and multiplies Depth of Field.
2. **Shutter Speed & The 180-Degree Shutter Rule (Videography vs. Photography)**:
   - **In Videography / Cinema**: Motion cadence requires a $180^\circ$ rotary shutter equivalent:
     $$t = \frac{1}{2 \times \text{FPS}}$$
     - **24 fps (Cinema Narrative)**: $1/48\text{ s}$ (or $1/50\text{ s}$ in 50Hz PAL/Indonesia regions to prevent AC lighting flicker).
     - **25 fps (PAL Broadcast/YouTube)**: $1/50\text{ s}$.
     - **30 fps (Digital Standard)**: $1/60\text{ s}$.
     - **60 fps / 120 fps (Slow Motion B-Roll)**: $1/120\text{ s}$ or $1/240\text{ s}$.
     - *Creative Override*: $45^\circ - 90^\circ$ shutter ($1/200\text{ s} - 1/500\text{ s}$ at 24fps) creates staccato, hyper-visceral action (*Saving Private Ryan* effect); $270^\circ - 360^\circ$ shutter ($1/24\text{ s}$) creates dreamy step-printed motion blur (*Wong Kar-wai* effect).
   - **In Still Photography**:
     - Handheld sharpness rule: $t \le \frac{1}{\text{Effective Focal Length}}$ (e.g., at least $1/100\text{ s}$ for an 85mm lens).
     - Freeze fast action/sports: $1/1000\text{ s} - 1/4000\text{ s}$.
     - Long-exposure light trails / silky waterfalls: $1\text{ s} - 30\text{ s}$ on tripod with ND filter.
3. **ISO, Dual Native ISO & False Color IRE Mapping**:
   - Keep ISO at the camera's **Base Native ISO** (e.g., ISO 800 and ISO 3200/12800 on dual-native cinema sensors) to preserve maximum dynamic range (14+ stops) above the noise floor.
   - **False Color / IRE Exposure Targets (Rec.709 / Monitoring LUT)**:
     - **0 - 5 IRE (Purple/Blue)**: Crushed black clipping (avoid unless silhouette).
     - **18% Middle Gray**: **38 - 42 IRE (Green)**.
     - **Skin Tones (Key Light Side)**: **55 - 70 IRE (Pink / Light Gray)**.
     - **95 - 100 IRE (Yellow/Red)**: Specular highlight clipping.

---

## 2. Optical Physics, Focal Lengths & Depth of Field

### A. Hyperfocal Distance & Depth of Field Formula
$$H = \frac{f^2}{N \cdot c} + f$$
where $f$ is focal length, $N$ is f-number, and $c$ is the circle of confusion (~$0.03\text{ mm}$ on Full-Frame $36 \times 24\text{ mm}$). When focused at $H$, everything from $H/2$ to infinity ($\infty$) is acceptably sharp.

### B. Psychological Dictionary of Focal Lengths (Full-Frame Equivalent)
| Focal Length | Field of View | Spatial & Psychological Effect | Classic Use Cases |
| :--- | :--- | :--- | :--- |
| **14mm - 20mm** | Ultra-Wide | Expands room scale, exaggerates Z-axis motion speed, distorts facial features at close distance. | Architecture, vast landscapes, psychological disorientation (Emmanuel Lubezki style). |
| **24mm - 28mm** | Wide | Dynamic environmental immersion; keeps background context legible while framing full-body action. | Establishing shots, walk-and-talk gimbal shots, vlogging, dynamic narrative scenes. |
| **35mm** | Master Wide-Normal | The quintessential cinema master lens: wide enough for environment, tight enough for natural faces. | Two-shots, over-the-shoulder (OTS), documentary storytelling, street photography. |
| **50mm** | Standard Normal | Matches human binocular perspective and compression; neutral, honest, unforced intimacy. | Dialogue medium shots, narrative realism (Yasujiro Ozu / anime clubroom framing). |
| **85mm - 105mm** | Portrait Telephoto | Flattering facial proportions, strong background compression, creamy bokeh subject isolation. | Emotional Close-Ups (CU), interviews, product hero shots, portrait photography. |
| **135mm - 200mm+** | Long Telephoto | Extreme Z-axis compression (background looms large behind subject), voyeuristic or epic isolation. | Cinematic compressed street shots, sports/wildlife, high-tension surveillance feel. |

---

## 3. Lighting Science, Inverse Square Law & Classic Setups

### A. The Inverse Square Law of Light Falloff
$$I \propto \frac{1}{d^2}$$
- Placing a softbox **close** to the subject (e.g., $1\text{ m}$ away) creates **rapid falloff** behind the subject (dramatic dark background contrast) and wraps softly around the face (because apparent source size is large).
- Placing a light **far** from the subject (e.g., $4\text{ m}$ away) creates **even illumination** across both the subject and the background (ideal for lighting a whole room evenly).

### B. Five Essential Cinematic Lighting Setups
1. **Three-Point Lighting (Key + Fill + Back/Hair Light)**:
   - **Key Light**: $30^\circ - 45^\circ$ off camera axis, $15^\circ - 30^\circ$ above eye level, diffused through a large softbox/scrim.
   - **Fill Light (or Negative Fill)**: Opposite the Key. Use a bounce card for **2:1** or **4:1** ratio, or a black flag (**Negative Fill**) for **8:1** cinematic shadow depth.
   - **Back / Rim / Kicker Light**: Behind the subject opposite the Key to carve the shoulders and hair out from the background.
2. **Rembrandt Lighting**: Key light positioned high and $45^\circ$ to the side so a small **illuminated triangle** appears on the shadow-side cheek beneath the eye.
3. **Book Lighting (Ultra-Soft Beauty / Mommy ASMR Visual Look)**: Bounce a strong light into a $4\times 4$ white bleached muslin/bounce board, then pass the bounced light through a $4\times 4$ diffusion frame ($1/2$ Grid or Opal). Produces velvety, zero-glare wrap ideal for calm, intimate close-ups.
4. **Chiaroscuro / Low-Key Lighting**: High contrast (**8:1 to 16:1** ratio), hard or snooted key light, deep shadows, smoke/haze for volumetric shafts.
5. **Color Contrast (Teal & Amber / Practical Motivated Lighting)**: Warm `2800K-3200K` practical tungsten lamp as the motivated Key/Rim against a `5600K-6500K` cool ambient room or window fill.


---

# S1-S2 MFA Module 3: Editing, Color Grading, Sound Design & Hermes ArtCraft Pipeline

## 1. Film Editing Theory & Pacing

### A. Walter Murch's "Rule of Six" (*In the Blink of an Eye*)
Never make a cut without evaluating these 6 criteria in descending order of importance:
1. **Emotion (51%)**: How will this cut make the audience feel right now? If the emotion is right and the other 5 are slightly imperfect, the audience will forgive the cut.
2. **Story (23%)**: Does this cut advance the narrative or argument? (Emotion + Story = **74%** of editing).
3. **Rhythm (10%)**: Does the cut occur at a musically and visually satisfying beat?
4. **Eye-Trace (7%)**: Where is the viewer's eye looking on Frame A (last frame of outgoing shot), and does Frame B (first frame of incoming shot) place the new focal point in that exact screen quadrant?
5. **Planarity / 2D Screen Plane (5%)**: Does the cut respect the 180-degree line and screen direction?
6. **3D Continuity of Space (4%)**: Does the cut respect the physical geography of the room?

### B. Cut Taxonomy & Montage Techniques
- **Standard Hard Cut**: Instant transition on action (**Cutting on Action** hides the edit seam because the eye tracks movement).
- **J-Cut (Audio Lead)**: The incoming shot's audio begins `4 - 15 frames` *before* the video cut (makes dialogue feel anticipatory and natural).
- **L-Cut (Audio Trail)**: The outgoing shot's audio continues `4 - 20 frames` *after* cutting to the reaction shot or B-roll.
- **Match Cut (Graphic / Action / Audio Match)**: Bridges two disparate locations or times by matching geometry, motion vector, or sound.
- **Jump Cut**: Cuts along the same camera axis (<30 degrees difference) to compress time or inject high-energy urgency in YouTube/Shorts editing.

---

## 2. Color Science & Grading Pipeline

### A. The 4-Node / 4-Stage Color Grading Workflow (DaVinci Resolve / `LightCraft` / `FilmCraft`)
1. **Node 1 - Color Space Transform (CST In) & Primary Balance**:
   - Normalize exposure using **Lift** (Shadows), **Gamma** (Midtones), **Gain** (Highlights), and **Offset** (Global exposure) while watching the **Waveform** (`5 IRE` black floor to `95 IRE` highlight ceiling).
2. **Node 2 - White Balance & Contrast Ratio**:
   - Align neutral grays across Red, Green, and Blue channels on the **RGB Parade** and set an S-Curve contrast pivot around middle gray (`40 IRE`).
3. **Node 3 - Skin Tone Isolation & Secondary Qualifiers**:
   - Isolate skin tones using Hue-vs-Hue / Hue-vs-Saturation or HSL Qualifier and align them precisely along the **Vectorscope Skin-Tone Line (I-Line)** with `40% - 55%` saturation.
4. **Node 4 - Creative Look & Color Harmony**:
   - Apply split-toning (e.g., cool teal shadows in Lift + warm amber/gold midtones/highlights in Gamma/Gain), halation, film grain, and vignette to guide Eye-Trace.

---

## 3. Production Sound & Psychoacoustic Mixing

### A. Target Loudness & True Peak Standards
| Target Platform | Integrated Loudness | Max True Peak | Dialogue Peak Range |
| :--- | :--- | :--- | :--- |
| **YouTube / Shorts / TikTok / Reels / Spotify** | **`-14 LUFS`** ($\pm 1	ext{ LU}$) | **`-1.0 dBTP`** | `-6 dBFS` to `-3 dBFS` |
| **Cinema / Netflix / Broadcast TV (EBU R128 / ATSC A/85)** | **`-24 LKFS / LUFS`** | **`-2.0 dBTP`** | `-12 dBFS` to `-6 dBFS` |

### B. Vocal & Mommy ASMR / Narrative Dialogue Processing Chain (`SoundCraft` / DAW)
1. **High-Pass Filter (HPF)**: Roll off rumble below `75 Hz - 90 Hz` (`12 dB/oct` or `18 dB/oct`).
2. **Subtractive EQ**: Cut boxy room resonance around `250 Hz - 400 Hz` (`-2 to -3 dB`, Q=2.0); add subtle velvety chest warmth at `120 Hz - 160 Hz` (`+1.5 dB` for *Mommy ASMR / Baritone* presence) and silky air shelf above `10 kHz` (`+1.5 dB`).
3. **De-Esser**: Tame harsh sibilance (`s`, `sh`, `ch`) between `5.5 kHz - 8.5 kHz`.
4. **Two-Stage Compression**:
   - Fast FET peak catcher (`4:1` ratio, fast attack `5 ms`, fast release `50 ms`, `2-3 dB` gain reduction).
   - Slow Opto leveling compressor (`2:1` ratio, medium attack `20 ms`, smooth release `200 ms`, `2-3 dB` gain reduction) for intimate, consistent close-mic warmth.
5. **Sidechain Ducking on Music Bus**: Duck background music by `-4 dB` to `-6 dB` (especially in the `1 kHz - 4 kHz` vocal clarity band) whenever dialogue/VO is active.

---

## 4. Hermes ArtCraft MCP + Blender + FFmpeg Execution Pipeline
Use the applications and tool schemas available on the current host. These routes are examples for separately configured adapters.

For a film, video or photography project in Hermes, use a dedicated project folder. Save native editable files before exporting, then check the deliverables.

| Production Stage | Hermes MCP Server / Tool | Native File | Export Deliverable & Verification Step |
| :--- | :--- | :--- | :--- |
| **1. Brief & Pre-Production Plan** | **`craft_anything`** (`craft-anything-cli.exe`) | `project.cany` | Call `core_brief_write`, `core_plan_update`, and `core_report_save` to save the Director's Treatment & Production Brief `.md`. |
| **2. Script & Call Sheet** | **`wordcraft`** (`wordcraft-cli.exe`) | `.docx` | Call `new_document`, `type_text`, `save_document`, and `render_page` to generate the AV Script / Screenplay `.docx` & `.pdf`. |
| **3. Budget, Stripboard & Shot List** | **`gridcraft`** (`gridcraft-cli.exe`) | `.xlsx` | Call `new_workbook`, `write_range`, `evaluate_formula`, and `save_workbook` to build the Shot List & Schedule `.xlsx`. |
| **4. Storyboard, Lookbook & Graphics** | **`designcraft`**, **`figcraft`**, **`vectorcraft`** | `.designcraft`, `.figcraft`, `.svg` | Build storyboard frames (`create_node`, `place_image`, `export_png`) and vector title/lower-third assets (`draw_shape`, `add_text`, `export`). |
| **5. 3D Previz, Camera Blocking & CGI** | **`blender`** (with a separately configured Blender adapter; check the host endpoint and tools) | `.blend` | Set virtual camera focal length (e.g., 35mm/85mm), test 3-point lighting, save `.blend`, and render PNG/animation sequences. |
| **6. Photography & Thumbnail Grading** | **`photocraft`** & **`lightcraft`** | Native layered + Library | Composite layers in `photocraft` (`doc_new`, `doc_save`, `doc_export`) and grade color/exposure in `lightcraft` (`import`, `set_develop`, `export`). |
| **7. Video Editing & Timeline Assembly** | **`filmcraft`** (`filmcraft-cli.exe`) | `.fcproj` | Run `media_import`, assemble sequence cuts via `command_run`, inspect via `project_inspect`, save `.fcproj`, and run `render_preview`. |
| **8. VFX, Motion Graphics & Keyframes** | **`effectcraft`** (`effectcraft-cli.exe`) | `.ecproj` | Run `get_project`, `set_property`, `add_keyframe`, save `.ecproj`, and verify with `render_frame`. |
| **9. Audio Mixing & Loudness Master** | **`soundcraft`** (`soundcraft-cli.exe`) | `.soundcraft` | Run `new_session`, `import_audio`, mix dialogue + SFX + music, save `.soundcraft`, and export final audio via `bounce_mix`. |


---

# S1-S2 MFA Module 4: Single-Bot "One-Man Studio" vs. Multi-Bot Hermes Crew Architecture

## 1. Mode A: Single-Bot "One-Man Studio" (1 Bot Menjadi Semua Peran Film Maker)
Dalam mode solo, satu bot dapat mengikuti delapan peran produksi berikut untuk film, video panjang, video vertikal, atau fotografi. Pilih peran sesuai brief dan periksa alat yang tersedia sebelum produksi.
1. **[ROLE 1: SHOWRUNNER & PRODUCER]** -> Menentukan tujuan penonton, target platform (YouTube 16:9 / Shorts 9:16 / Cinema), durasi, dan jadwal kerja yang ramah energi (6D Parenting).
2. **[ROLE 2: SCREENWRITER]** -> Menulis *Hook* 0-15 detik, struktur 3-Babak / *Kishotenketsu* / *Hook-Bridge-Body-Payoff*, dan naskah **Two-Column AV Script** atau **Fountain Screenplay**.
3. **[ROLE 3: FILM DIRECTOR]** -> Menyusun *Director's Treatment*, *blocking* adegan, arah emosi (*subtext*), dan *Master Shot List* (EWS, WS, MS, CU, ECU, OTS).
4. **[ROLE 4: DIRECTOR OF PHOTOGRAPHY (DP) & MASTER PHOTOGRAPHER]** -> Menentukan lensa (mm), *Exposure Triangle* ($f$-stop, *180-degree shutter speed*, Native ISO), *Lighting Ratio* (2:1, 4:1, 8:1), *Kelvin temperature*, dan komposisi visual (atau *prompt* visual AI / scene 3D Blender).
5. **[ROLE 5: PRODUCTION DESIGNER & ART DIRECTOR]** -> Merancang *color palette*, properti latar (*practical lights*), tipografi judul, dan *Thumbnail High-CTR* (`PhotoCraft`, `DesignCraft`, `VectorCraft`).
6. **[ROLE 6: LEAD FILM EDITOR]** -> Menyusun *Rough Cut* hingga *Fine Cut* menggunakan **Walter Murch's Rule of Six** (Emotion 51%, Story 23%, Rhythm 10%, Eye-Trace 7%, 2D Plane 5%, 3D Space 4%), *J-Cut*, *L-Cut*, dan *Pattern Interrupts* (`FilmCraft`).
7. **[ROLE 7: COLORIST & VFX COMPOSITOR]** -> Mengatur *Color Grading* (Lift-Gamma-Gain, Skin-Tone Vectorscope, Teal & Amber / Cinematic LUT) serta animasi *keyframe* (`LightCraft`, `EffectCraft`).
8. **[ROLE 8: SOUND DESIGNER & RE-RECORDING MIXER]** -> Merancang *dialogue chain*, *Mommy ASMR / Baritone vocal prosody*, *Foley*, *ambience*, *ducking* musik, dan *mastering* ke **`-14 LUFS`** (`SoundCraft`).

---

## 2. Mode B: Multi-Bot Hermes Studio Crew (Kolaborasi 5 Bot Ekosistem MuZA)
Dalam preset MuZA, kru memakai pembagian di bawah. Pembagian peran dapat disesuaikan pada mode tim khusus.

| Bot Hermes | Jabatan Kru Film & Fotografi | Tanggung Jawab Utama & Aplikasi ArtCraft/MCP yang Dipegang |
| :--- | :--- | :--- |
| **`[SHIZUKA]`**<br>Shizuka Hiratsuka | **Koordinator dan peninjau** | Menetapkan tujuan, koordinasi, dan batas keputusan. Menggabungkan temuan dan meminta keputusan pengguna. |
| **`[KIKI-CHII]`**<br>Kiki-Chii | **Pemilik produksi kreatif** | Membawa brief ke naskah, storyboard, kamera, fotografi, aset, penyuntingan, VFX, audio, dan preview. Memilih aplikasi yang tersedia dan meminta review sebelum finalisasi. |
| **`[SHIKAKU]`**<br>Shikaku Nara | **Pendukung teknis** | Membantu skrip FFmpeg atau Python, integrasi, dan pemeriksaan teknis sesuai tugas. Kiki-Chii memegang keputusan produksi. |
| **`[VAL]`**<br>Val | **Peneliti dokumenter** | Menyiapkan bukti, sumber, dan batas kepastian untuk naskah edukasi atau dokumenter. Menyerahkan hasil riset kepada Shizuka. |
| **`[YUKINO]`**<br>Yukino Yukinoshita | **Ide awal dan ritme kerja** | Memilah ide dan menyesuaikan rencana dengan waktu dan kapasitas yang dinyatakan pengguna. Menyerahkan brief awal kepada Shizuka. |
