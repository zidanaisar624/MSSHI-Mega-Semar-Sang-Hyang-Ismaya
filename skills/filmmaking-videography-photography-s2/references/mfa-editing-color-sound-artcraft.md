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
