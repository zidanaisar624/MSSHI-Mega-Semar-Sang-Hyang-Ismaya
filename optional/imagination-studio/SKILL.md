---
name: imagination-studio
description: Optional Kiki-Chii local AI film studio & Slate workflow bridge for Imagination Studio (by Keys & Sam Wasserman / TensorFold). Collaborates with filmmaking-videography-photography-s2 when enabled: turns approved MFA concepts & shot lists into Slate setups and queues stills, clips with sound, voice, music, and SFX via the Hermes plugin or stdio MCP (127.0.0.1:7870) after checking memory headroom.
---

# Imagination Studio Bridge for Kiki-Chii (Optional Filmmaker Partner)

This **optional** MSSHI integration belongs to **Kiki-Chii (Content Creator / Filmmaker)** (`public_default: false`). It activates only when explicitly selected during setup (`--with-imagination-studio`) or enabled via `msshi optional enable imagination-studio`.

Upstream references:
- Repository: `https://github.com/Keys-Wasserman/Imagination-Studio-by-keys-Wasserman` (Apache-2.0; attribution: **Keys (`github.com/drowzeys`)** & **Sam Wasserman / Wasserman Productions (`wassermanproductions.com`)**).
- Hermes Plugin Listing: `https://hermeswatcher.com/plugins/imagination-studio` (requires Hermes `>= 0.22.7`, localhost HTTP-only `http://127.0.0.1:7870`, zero external telemetry).

## Mandatory Collaboration With `filmmaking-videography-photography-s2`

Never jump straight into rendering. Always run **Kiki-Chii's Filmmaker pipeline** hand-in-hand with Imagination Studio:

1. **Phase 1 — Concepting First (`filmmaking-videography-photography-s2`)**:
   - Lock **Core Emotion (51%)**, **Story (23%)**, aspect ratio (`16:9` / `9:16` / `2.39:1`), Fountain/AV script, and human-approved concept direction before opening any studio queue.
2. **Phase 2 — Slate Pre-Production & Shot Coverage**:
   - Translate the approved Master Shot List into **Imagination Studio's Slate workflow** (setups, coverage plans, character/location continuity, seed control).
   - *Hardware note*: Slate planning, project organization, imports, and media browsing require **no heavy local model downloads**.
3. **Phase 3 — Memory Headroom Check & Queue-Only Generation**:
   - **Always check local headroom first** before queueing any render or starting another local model:
     - Via CLI helper: `msshi studio status --probe` (read-only loopback `GET /api/memory` & `GET /api/jobs` on `127.0.0.1:7870`)
     - Via Hermes plugin: `studio_status` / via Studio MCP (`mcp/studio-mcp.py`): `memory_status`
   - **Queue every asset strictly through Imagination Studio** — NEVER run standalone render scripts (`scripts/*.sh`, `spark/*.py`, separate ComfyUI) that bypass the Studio memory floor:
     - **Hermes Official Plugin tools**: `studio_picture` (FLUX3-K / Qwen-Image-2.1), `studio_clip` (MiniMax H3 / FastH3 video with sound), `studio_voice` (Fish Audio Drama 3), `studio_song` (MiniMax Music 3), `studio_sound` (Stable Audio Open / MMAudio SFX), `studio_job`, `studio_jobs`, `studio_cancel`, `studio_library`.
     - **Stdio MCP tools (`mcp/studio-mcp.py`)**: `queue_still`, `queue_clip`, `queue_voice`, `queue_song`, `queue_sound`, `queue_edit`, `wait_for_jobs`.
4. **Phase 4–5 — Post-Production Handoff Back to Filmmaker**:
   - Retrieve finished assets from `HERMES_HOME/plugin-data/imagination-studio/outputs` (plugin) or `$STUDIO_URL/files/<path>` (MCP/HTTP).
   - Hand off into `filmmaking-videography-photography-s2` Phase 4–5: assemble & cut by Walter Murch's Rule of Six in `filmcraft`, composite in `effectcraft`, color-grade in `lightcraft`/`photocraft` (ACES/Rec.709), mix audio to `-14 LUFS` (YouTube/Social) or `-24 LKFS` (Cinema) in `soundcraft`, or import 3D camera/pose templates into `blender`.
   - Always pause for **human review** before final export or publishing.

## Hardware, Licensing & Low-RAM Honesty

- **Local GPU generation is heavy**: Full native Imagination Studio models target high-RAM Apple Silicon Macs, NVIDIA DGX Spark, or Windows RTX Spark systems (128 GiB RAM for full local model suites; below 128 GiB, Studio gates unverified recipes via *Machine -> Feature checks*).
- **On 4–16 GB RAM laptops (including Windows 10 Low-RAM mode)**:
  - Use Imagination Studio for **Slate planning/organization** only, OR route heavy renders to a user-owned remote **ComfyUI PC over SSH** / **Comfy Cloud** (`STUDIO_COMFY_URL`, user's own account), OR seamlessly fall back to `filmmaking-videography-photography-s2` native stack (`ArtCraft`, `Blender`, `Motion-as-Code`, `brag`, `Higgsfield`).
- **Separate model licenses**: Imagination Studio code is Apache-2.0 and ships **zero weights**. Optional model weights users download inside Studio (e.g., Qwen-Image-2.1, FLUX3-K, MiniMax H3) carry their own non-commercial/community/territory license terms.

## Setup & Guardrails

- Inspect readiness safely (0 LLM calls, 0 network calls by default):
  ```text
  msshi studio status
  msshi studio plan --concept "Short film cyber-noir 60 detik" --format short
  ```
- Optional separate user installations (never executed automatically by MSSHI):
  1. Install the Hermes plugin (`hermes >= 0.22.7`): `hermes plugins install imagination-studio` then `hermes plugins enable imagination-studio`.
  2. Or connect stdio MCP `mcp/studio-mcp.py` pointing to `STUDIO_URL=http://127.0.0.1:7870`.
  3. Install & start Imagination Studio separately from `Keys-Wasserman/Imagination-Studio-by-keys-Wasserman`.
- **Guardrails**: Never auto-start Imagination Studio on boot (`auto_open_on_boot: false`), never download model weights silently, never modify the user's Hermes provider/model/endpoint/API keys/`SOUL.md`, and respect private vault boundaries.
