# Internet Trend Deconstruction & Reverse-Engineering Matrix

Use this reference when executing **Stage 2** of `auto-curiousity-for-film-making` to study emerging videography, filmmaking, and photography trends from the internet (YouTube, Shorts, Reels, TikTok, Vimeo Staff Picks, film festivals, and photography communities) and convert them into exact technical parameters.

## 1. Proactive Internet Trend Scanning Queries

When running autonomous research or investigating a user-requested style, query current web sources using targeted technical search patterns rather than generic keywords:

- **YouTube Long-Form & Documentary Trends**:
  - `"YouTube retention editing" pacing J-cut L-cut sound design breakdown`
  - `"cinematic documentary" lighting setup book light false color IRE LUT workflow`
  - `"visual essay" motion graphics kinetic typography 3D camera projection breakdown`
- **Vertical Shorts / Reels / TikTok Visual Hooks**:
  - `"viral short form editing" 0-3 second visual hook speed ramp whip pan bezier curve`
  - `"seamless match cut" OR "masked transition" vertical video cinematography breakdown`
- **Cinema & Color Grading Aesthetics**:
  - `"film emulation" halation bloom grain Kodak 2383 AgX color grading node tree`
  - `"A24 cinematography" OR "festival short film" focal length lighting ratio shadow roll-off`
- **Photography & Thumbnail Engineering**:
  - `"high CTR YouTube thumbnail" color contrast complementary HSL depth separation`
  - `"editorial portrait photography" focal length lighting modifier color temperature recipe`

## 2. The 6-Layer Technical Reverse-Engineering Matrix

Every trend or reference work must be broken down into these 6 quantitative layers so `filmmaking-videography-photography-s2` can execute it deterministically:

| Layer | Technical Metrics to Extract | Target ArtCraft / Blender Execution Tool |
| :--- | :--- | :--- |
| **1. Hook & Pacing Math** | - **Hook Window**: What happens at `0.0s - 1.5s` and `1.5s - 3.0s`?<br>- **ASL (Average Shot Length)**: e.g., `1.2s` (fast montage), `3.5s` (modern YouTube), `8.5s` (contemplative cinema).<br>- **Audio-Visual Lead/Lag**: J-cut audio lead (`-6` to `-15` frames) or L-cut audio trail (`+6` to `+20` frames). | `wordcraft` (AV Script timing)<br>`filmcraft` (Timeline cut markers & J/L-cuts) |
| **2. Camera & Lens Optics** | - **Focal Length**: e.g., `16-24mm` (immersive dynamic perspective), `35mm` (natural narrative), `50mm` (human eye), `85-135mm` (intimate portrait compression).<br>- **Shutter Angle**: `180 deg` (`1/48s` at 24fps natural blur), `45-90 deg` (crisp action), or `360 deg` (`1/6s - 1/12s` Wong Kar-wai step-printing).<br>- **Camera Motion**: Static locked-off, slow dolly push-in (`0.05 m/s`), handheld micro-shake, or speed-ramped whip pan. | `blender` (3D camera previz & focal length)<br>`filmcraft` & `effectcraft` (Speed ramp & motion blur) |
| **3. Lighting & Exposure** | - **Key-to-Fill Ratio**: `2:1` (High-Key / Mommy ASMR soft warmth), `4:1` (Natural dramatic), `8:1+` (Low-Key Chiaroscuro / Noir).<br>- **Color Temp Contrast**: e.g., `3200K` warm practical key vs `5600K` cool moonlight/window fill.<br>- **IRE Placement**: Skin tones at `55-70 IRE`; specular highlights `<95 IRE`; shadows at `5-15 IRE`. | `blender` (3D Area/Spot lights & Kelvin setup)<br>`lightcraft` & `photocraft` (Exposure & False Color check) |
| **4. Color Science & Texture** | - **Primary Balance**: Lift (shadows), Gamma (midtones), Gain (highlights), Offset (global exposure).<br>- **Secondary HSL**: Hue rotation, saturation compression, luminance separation (e.g., teal shadows `195 deg` vs warm skin `32 deg`).<br>- **Optical Texture**: Halation radius (`2-8 px` red-orange glow on high-contrast edges), highlight bloom (`10-20%`), 35mm film grain (`ISO 400` organic texture). | `lightcraft` (LUT/CDL, HSL & Halation)<br>`photocraft` (Grading & texture layers) |
| **5. VFX & Motion Design** | - **Velocity Curve**: `cubic-bezier(0.85, 0.0, 0.15, 1.0)` for snappy whip-transitions; `cubic-bezier(0.25, 0.1, 0.25, 1.0)` for gentle cinematic eases.<br>- **Compositing**: Foreground walk-by mask wipe, 3D camera projection parallax on 2D stills, or subtle HUD/callout graphics. | `effectcraft` (Keyframes, masks, VFX nodes)<br>`designcraft` / `vectorcraft` / `figcraft` (Vector HUD & titles) |
| **6. Psychoacoustic Audio** | - **Transition SFX**: Low-pass whoosh (`120Hz - 2.5kHz`) peaked on the exact cut frame + subtle foley cloth/page rustle.<br>- **Emotional Weight**: Sub-drop (`40-65Hz`) on reveal moments; riser (`-24 dBFS` to `-9 dBFS` over 2s) before key payoff.<br>- **Loudness & Ducking**: Dialogue locked at `-14 LUFS` (web) with `-4 dB` sidechain ducking on music around `1-4 kHz`. | `soundcraft` (Multi-track SFX, EQ sidechain, LUFS master) |

## 3. Adapting Trends to User Persona & Comfort (Anti-Fatigue Filter)

Not every loud or hyper-edited internet trend fits every creator or audience. Always categorize deconstructed trends into three **Energy Tiers** in `curiosity_ledger/`:

1. **Tier 1 - Calm, Intimate & Cozy (Mommy ASMR / Contemplative / Educational Essay)**:
   - Longer ASL (`4.5s - 9.0s`), soft Book Light (`2:1` ratio, `3200K-4300K`), gentle `cubic-bezier(0.22, 1.0, 0.36, 1.0)` camera push-ins, warm halation, zero harsh jump-cuts, and clean, crisp close-mic voice audio (`-14 LUFS`, zero sibilance spike).
2. **Tier 2 - Balanced Narrative & High-Retention YouTube (Story-Driven / Tech & Creative Breakdown)**:
   - Medium ASL (`2.5s - 4.5s`), structured visual pattern interrupts every `45-60s`, clean 3D/diagram inserts from `blender` and `designcraft`, `4:1` dimensional lighting, and subtle J/L-cut conversational flow.
3. **Tier 3 - High-Energy Dynamic / Viral Shorts (Fast Montage / Showcase / Trailer)**:
   - Short ASL (`0.8s - 2.0s`), rhythmic beat-synced cuts, speed-ramped match cuts in `effectcraft`, bold kinetic typography, and punchy transient SFX in `soundcraft`.
