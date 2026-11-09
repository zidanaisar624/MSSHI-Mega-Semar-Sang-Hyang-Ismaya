# Curiosity Ledger Schema & Seamless Handoff to `filmmaking-videography-photography-s2`

Use this reference when executing **Stage 3** and **Stage 4** of `auto-curiousity-for-film-making` to store self-learned discoveries and connect them seamlessly (`berkesinambungan`) with `filmmaking-videography-photography-s2`.

## 1. Local Knowledge Base Structure (`curiosity_ledger/`)

Maintain a structured directory so every autonomous discovery persists across sessions and can be loaded immediately during film or photo production:

```text
curiosity_ledger/
├── app_capabilities_snapshot.json       # Known tools, parameters, and versions across 15 ArtCraft apps + Blender + CLI
├── artcraft_and_app_updates_log.md      # Chronological log of newly discovered app features & sandbox test results
├── internet_trend_playbook.md           # Deconstructed viral & cinema trends using the 6-Layer Matrix
├── tested_recipes_registry.json         # Validated, ready-to-run Recipe Cards for filmmaking-videography-photography-s2
└── sandbox_tests/                       # Isolated 2-second test clips, test frames, and parameter sweep outputs
```

## 2. Standardized Cinematic Recipe Card Schema (`tested_recipes_registry.json`)

Every newly learned app feature or internet trend is saved as a structured Recipe Card:

```json
{
  "recipe_id": "trend_2026_warm_halation_booklight_intro",
  "title": "Warm 35mm Halation + Soft Book-Light Retention Hook",
  "source_type": "hybrid_trend_and_app_update",
  "energy_tier": "Tier 1 (Calm / Intimate) or Tier 2 (Balanced Narrative)",
  "target_formats": ["youtube_16_9", "shorts_9_16", "short_film"],
  "deconstruction_6_layers": {
    "pacing_asl_sec": 3.8,
    "j_cut_lead_frames": 8,
    "lens_mm": 35,
    "shutter_angle_deg": 180,
    "lighting_ratio": "2:1 Book Light (3400K Key + 4800K Soft Fill, Skin at 62 IRE)",
    "color_recipe": "Kodak 2383 curve + 4px Red-Orange Edge Halation + 8% Highlight Bloom",
    "vfx_motion": "Slow 1.00x to 1.06x cubic-bezier(0.22, 1.0, 0.36, 1.0) push-in over 3.8s",
    "audio_master": "-14 LUFS dialogue, -28 LUFS warm vinyl/room tone, -4dB sidechain ducking at 2.5kHz"
  },
  "artcraft_and_blender_execution": {
    "blender": "Set 35mm camera DOF F/2.0; place Area Light bounce + diffusion plane at 45 deg",
    "lightcraft": "Apply Halation radius=4.0, threshold=0.82; set Skin IRE target=62",
    "effectcraft": "Add scale keyframe 100% -> 106% with cubic-bezier(0.22, 1.0, 0.36, 1.0)",
    "filmcraft": "Insert 8-frame J-cut audio lead into Scene 1 track",
    "soundcraft": "Enable parametric sidechain ducking -4dB at 2500Hz; master limiter -1.0 dBTP / -14 LUFS"
  },
  "sandbox_verified": false,
  "notes": "Illustrative example. Verify the actual adapter parameters and output before use."
}
```

## 3. Bidirectional Continuity Protocol with `filmmaking-videography-photography-s2`

`auto-curiousity-for-film-making` and `filmmaking-videography-photography-s2` form a two-skill symbiotic system:

```text
[auto-curiousity-for-film-making]                    [filmmaking-videography-photography-s2]
  1. Detects new ArtCraft/Blender/App update  --->     Receives verified new tool parameters
  2. Reverse-engineers internet visual trend  --->     Applies 6-Layer Recipe Card in Phases 1-5
  3. Runs safe 2-sec sandbox verification     <---     Requests R&D when hitting a novel style/effect
```

### How 1 Bot vs 5 Bots Execute the Curiosity-to-Production Loop

#### Mode A: Single-Bot "One-Man Studio"
When a single bot handles an entire film, YouTube video, or photography project:
1. **Step 0 (Curiosity Check - 60 Seconds)**: Before starting Phase 1 of `filmmaking-videography-photography-s2`, the bot checks `curiosity_ledger/tested_recipes_registry.json` and runs a quick schema check if any ArtCraft/external tool was recently updated.
2. **Step 1-5 (Production Execution)**: The bot executes all 8 film crew roles in `filmmaking-videography-photography-s2`, embedding the selected Recipe Cards directly into the AV script, shot list, lighting diagram, color grade, and sound mix.
3. **Post-Project Retrospective**: Any new technique discovered during production is saved back into `curiosity_ledger/` for future projects.

#### Mode B: MuZA creative lead
Kiki-Chii owns the creative loop from Concepting First to experiments and production. Shikaku can verify a technical adapter or repair a tooling problem, Val can verify external evidence, and Yukino can help the user set pace. Shizuka coordinates handoffs and presents the result. Use host-supported delegation if available.

Keep the ledger local to the project. Store creative preference updates only when the user has approved the proposed change.
