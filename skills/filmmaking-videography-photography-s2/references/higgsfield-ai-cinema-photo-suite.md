# Higgsfield AI Unified Filmmaking, Videography & Photography Suite (`higgsfield-ai/skills`)

Source Repository: [`https://github.com/higgsfield-ai/skills`](https://github.com/higgsfield-ai/skills)

This reference fuses all 9 official **Higgsfield AI Skills** directly into **MSSHI — Mega Semar Sang Hyang Ismaya: Sovereign Sage** so that **Filmmaking, Videography, and Photography** operate as **one unified skill** under **Kiki-Chii (Total Creative Specialist)**.

## 1. Unified Capability Matrix (9 Higgsfield Skills + MFA Cinematography/Photography + ArtCraft/Blender)

| Higgsfield Skill Module | CLI / Skill Invocation | Unified Role in Filmmaking, Videography & Photography |
| :--- | :--- | :--- |
| **`higgsfield-generate`** | `/higgsfield:higgsfield-generate` | Multi-model AI Cinema, Videography, Photography, 3D & Audio generation across 30+ engines (**Seedance 2.5**, **Veo 3.1**, **Kling 3.0**, **Soul V2**, **Nano Banana 2**, **GPT Image 2.6** with native GIF/SVG, **Flux 2**, **Seed Audio 1.0**). Includes **Marketing Studio** (9 commercial/UGC video modes) and **Virality Predictor** (`brain_activity` hook/retention scoring). |
| **`higgsfield-soul-id`** | `/higgsfield:higgsfield-soul-id` | Trains a reusable, face-faithful **Soul Character Identity** from 5–20 reference photos (`--soul-id`), ensuring 100% actor/character continuity across multi-scene films, vlogs, and photo shoots. |
| **`higgsfield-product-photoshoot`** | `/higgsfield:higgsfield-product-photoshoot` | Master Commercial & Editorial Photography engine with 10 specialized modes (`product_shot`, `lifestyle_scene`, `closeup_product_with_person`, `moodboard_pin`, `hero_banner`, `social_carousel`, `ad_creative_pack`, `virtual_model_tryout`, `conceptual_product`, `restyle`). |
| **`higgsfield-brandkit`** | `/higgsfield:higgsfield-brandkit` | Builds complete visual identity systems: editable **Recraft SVG** logos, approved color palettes, typography, mockups, packaging, social graphics, and canonical PPTX/PDF brandbooks. |
| **`higgsfield-marketplace-cards`** | `/higgsfield:higgsfield-marketplace-cards` | Generates compliant e-commerce/marketplace main product photos, secondary lifestyle angles, and A+ visual story modules. |
| **`higgsfield-faceless-video`** | `/higgsfield:higgsfield-faceless-video` | End-to-end production for faceless documentaries, video essays, stories, and music videos (generates `Seed Audio` narration first, synthesizes matched visual scenes, and assembles locally). |
| **`higgsfield-video-explainer`** | `/higgsfield:higgsfield-video-explainer` | Builds matched 10-second visual explainer blocks synchronized to voiceover narration and motion graphics. |
| **`higgsfield-youtube-thumbnail`** | `/higgsfield:higgsfield-youtube-thumbnail` | High-CTR 4K YouTube thumbnails (`Nano Banana Pro 4K`) and 9:16 vertical covers (Shorts/Reels/TikTok) with face/logo identity preservation, controlled variants, and Seedream visual tweaks. |
| **`higgsfield-websites`** | `/higgsfield:higgsfield-websites` | Chains with `higgsfield-generate` (and **Shikaku Nara's** Antigravity WebDev stack) to embed bespoke hero video loops, interactive 3D/shader visuals, and playable browser games (`--type game`) into React 19 + TanStack Start web apps. |

## 2. How Kiki-Chii Chains Higgsfield AI + Motion Graphics + ArtCraft MCP + Blender

1. **Stage 1 — Concepting & Virality Pre-Check (Concept-First Rule)**:
   - **Kiki-Chii** always begins by co-designing the **Concept, Emotional Arc (Walter Murch 51% Emotion), Optical Look (Focal Length & Lighting Ratio), and 0–3s Hook** with the user.
2. **Stage 2 — Unified Photography & Visual Identity (`Soul ID` + `Product Photoshoot` + `PhotoCraft`/`LightCraft`)**:
   - Lock character/actor consistency via `higgsfield-soul-id` (`--soul-id`).
   - Generate or shoot raw plates using `higgsfield-product-photoshoot` (10 modes) or `higgsfield-generate` (`GPT Image 2.6` / `Soul V2`), then refine 16-bit color grading, skin-tone IRE (`55–70 IRE`), and halation in `lightcraft` and `photocraft`.
3. **Stage 3 — Unified Cinematography, Motion-Graphics-as-Code & Video Assembly**:
   - **Cinematic Shots**: Direct camera motion and physics-heavy scenes via `Seedance 2.5` (`--mode omni_reference --start-image`), `Veo 3.1`, `Kling 3.0`, or 3D camera previz in `blender`.
   - **Programmatic Motion Graphics**: Layer kinetic typography, data charts, and UI motion via [`remotion-dev/skills`](https://github.com/remotion-dev/skills), [`charlie947/motion-graphics-skills`](https://github.com/charlie947/motion-graphics-skills), [`Barty-Bart/motion-graphics`](https://github.com/Barty-Bart/motion-graphics), and [`bangtutorial/bang-motion`](https://github.com/bangtutorial/bang-motion).
   - **Timeline, VFX & Audio Mastering**: Assemble in `filmcraft` (`.fcproj`) and `effectcraft` (`.ecproj`), master audio in `soundcraft` (`-14 LUFS`), score retention with Higgsfield **Virality Predictor** (`brain_activity`), and generate the final cover with `higgsfield-youtube-thumbnail`.
