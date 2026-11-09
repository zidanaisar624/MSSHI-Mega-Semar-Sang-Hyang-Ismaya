# App Update & ArtCraft MCP Autonomous Discovery Protocol

Use this reference when executing **Stage 1** of `auto-curiousity-for-film-making` to discover, inspect, and sandbox-test new features or updates in the 15 ArtCraft MCP applications, Blender 5.2+ MCP, FFmpeg, and external videography or photography tools.

## 1. Inspect the relevant creative tools

When a task calls for feature discovery, inspect only the relevant configured adapters. Use the current host's tool inventory and verified app version. Keep model and provider settings intact.

| Target App / Server | Local Path / Endpoint | Primary Videography & Photography Discovery Focus |
| :--- | :--- | :--- |
| **FilmCraft** (`filmcraft`) | `<artcraft-root>/apps/filmcraft` | New timeline track types, NLE transition modes, proxy codecs, EDL/XML export flags, and color LUT slots in `.fcproj`. |
| **EffectCraft** (`effectcraft`) | `<artcraft-root>/apps/effectcraft` | New procedural VFX nodes, particle emitters, optical flow / motion blur shaders, rotoscoping masks, and bezier keyframe easing modes in `.ecproj`. |
| **PhotoCraft** (`photocraft`) | `<artcraft-root>/apps/photocraft` | New RAW demosaicing algorithms, frequency separation filters, healing/inpainting tools, smart-object blend modes, and lens-distortion profiles. |
| **LightCraft** (`lightcraft`) | `<artcraft-root>/apps/lightcraft` | New color-grading wheels (Lift/Gamma/Gain/Offset), HSL qualifiers, film halation/grain emulation, tone-mapping curves, and batch LUT exporters. |
| **SoundCraft** (`soundcraft`) | `<artcraft-root>/apps/soundcraft` | New DSP effects, parametric EQ bands, sidechain compression envelopes, convolution reverb IRs, spectral de-noisers, and LUFS metering tools. |
| **DesignCraft / FigCraft / VectorCraft** | `<artcraft-root>/apps/...` | New kinetic typography presets, lower-third templates, storyboard frame generators, SVG path animators, and YouTube thumbnail layout grids. |
| **WordCraft / GridCraft / DeckCraft / PDFCraft** | `<artcraft-root>/apps/...` | New screenplay Fountain/AV-script formatters, call-sheet/budget formulas, pitch-deck slide layouts, and print-ready storyboard book exporters. |
| **CADCraft / SolidCraft** | `<artcraft-root>/apps/...` | New 3D set-design primitives, studio lighting rig dimensions, and camera dolly/crane mechanical geometry exports. |
| **CraftAnything** (`craft_anything`) | `<artcraft-root>/apps/craft_anything` | New cross-app orchestration macros and multi-app pipeline templates. |
| **Blender MCP** (`blender`) | Configured local endpoint | New Geometry Nodes, Compositor nodes, Cycles/EEVEE Next lighting shaders, AgX/Filmic color management views, and camera rig constraints. |
| **External Video/Photo CLI & Apps** | System PATH / Local Install | New `ffmpeg -filters` (e.g., `libplacebo`, `lut3d`, `afade`, `ebur128`), `opencv`, `darktable-cli`, `rawtherapee-cli`, `kdenlive`, or `davinci` scripts. |

## 2. Step-by-Step Introspection Workflow

1. **Enumerate Tools & Parameters (Schema Diffing)**:
   - Query the MCP server's tool list and inspect each tool's input schema (`properties`, `enum`, `default`, `description`).
   - Compare against `curiosity_ledger/app_capabilities_snapshot.json`.
   - For authorized inspection of a local install, set `ARTCRAFT_ROOT` to its location and run read-only commands:

     ```powershell
     # Check recent file modifications or updates in ArtCraft
     Get-ChildItem -LiteralPath $env:ARTCRAFT_ROOT -Recurse -File | Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-14) } | Select-Object FullName, LastWriteTime
     ```

     ```bash
     # Check newly available FFmpeg video and audio filters
     ffmpeg -hide_banner -filters | grep -E "lut|color|blend|blur|loudnorm|afade|acompressor"
     ```

2. **Formulate a Feature Hypothesis**:
   - State clearly what the new tool or parameter claims to do (e.g., *"EffectCraft added a `chromatic_aberration_radial` parameter with range `0.0` to `5.0`; hypothesis: simulates vintage anamorphic lens edge fringing without softening the center subject"*).

## 3. Safe Micro-Sandbox Testing Protocol (`Eksperimen Mikro Kotak Pasir`)

Before recommending or using a newly discovered feature in a real production, validate it in an isolated sandbox directory (`curiosity_ledger/sandbox_tests/`):

1. **Create a Standardized Test Asset**:
   - **Video/VFX Test**: A 2-second, 24fps (`48 frames`) 1080p clip containing a skin-tone subject chart (`60 IRE`), a grayscale step-wedge (`0-100 IRE`), and a moving edge target.
   - **Photo/Color Test**: A single 16-bit test frame with highlight roll-off, shadow detail, and portrait skin tones.
   - **Audio Test**: A 3-second voice stem (`-18 LUFS`) layered over a background ambient pad (`-30 LUFS`).

2. **Execute a 3-Point Parameter Sweep**:
   - Run the tool at **Low (20% of range)**, **Default (nominal)**, and **Extreme (90-100% of range)**.
   - Measure objective outcomes:
     - Does it clip highlights (`>100 IRE`) or crush shadows (`<0 IRE`)?
     - Does it shift skin tones off the Vectorscope skin-tone line?
     - Does it introduce audio true-peak clipping (`>-1.0 dBTP`)?
     - How many milliseconds per frame does it add to render time?

3. **Promote Verified Findings to the Curiosity Ledger**:
   - Record the optimal "Sweet Spot" parameter range (e.g., *"Sweet spot for `chromatic_aberration_radial` is `0.35 - 0.65`; values above `1.5` degrade subtitle readability"*) in `curiosity_ledger/artcraft_and_app_updates_log.md` and `curiosity_ledger/tested_recipes_registry.json`.
