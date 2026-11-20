---
name: sharewise
description: Safe privacy check before sharing photos or videos with Sharewise across all bots: report yes/no metadata risks only (GPS, time, device, IDs, owner, thumbnails, edit history, video face data), build local review pages, and create verified clean copies with pixel redaction. Local-only, zero network, originals untouched.
---

# Sharewise — Privacy Inspection & Clean Copies Before Sharing (All Bots)

Upstream: `https://github.com/ardianreffa/sharewise` (MIT, Copyright 2026 ardianreffa, pin `dd82698f253a29fe6eb53a8c36d4b51b11a289a9`) · Hermes Marketplace: `https://hermes-agent.nousresearch.com/marketplace/sharewise`.

Sharewise operates strictly locally (`0` network calls, originals never modified) under **Wall T1**: it reports **yes/no counts only** — never leaking exact coordinates, timestamps, device IDs, owner names, or OCR strings to the LLM.

## Mandatory Rules
1. **Take the folder literally.** Use the exact folder named by the user; never widen or add `include_subfolders=true` unless explicitly asked. Respect all path and local vault guardrails.
2. **Inspect first (`sharewise_check`)**: report findings in plain language using yes/no counts only (never guess or invent values).
3. **Offer local review (`sharewise_review`)** when photos contain faces, people, street signs, house numbers, or license plates. Share the local HTML review page paths so the user can toggle/draw areas and paste back their `SW1.`/`SW2.` selection codes.
4. **Create clean copies (`sharewise_share`) only when the user asks in the current message**:
   - Pass user-pasted selection codes verbatim (never disable user-selected redactions).
   - Keep `keep=[]` by default (strip all metadata except copyright). Keeping `location` triggers Hermes' `pre_tool_call` approval gate — warn the user why location metadata is risky.
   - Only call `sharewise_look` on finished clean copies (never originals) when the user explicitly asks for a visual double-check, noting that `sharewise_look` sends downsized clean copies to the model provider.

## Platform Honesty (Windows vs macOS/Linux)
- **macOS**: full metadata check, on-device Apple Vision auto-detection (faces, people, street names, house numbers, license plates), manual review page, and clean redacted copies.
- **Windows & Linux**: `sharewise_check` (photo/video metadata audit), `sharewise_review` (local HTML review page where users draw redaction boxes by hand), and `sharewise_share` (verified clean copies + pixel rebuild) all work inside subfolders of the user's home directory; automatic Apple Vision detection is macOS-only, and non-home drives (e.g., `D:\`) are refused by upstream `guard.py`.
- Requires `Pillow` + `numpy` (+ `pillow-heif` for `.heic`/`.heif`). Never modifies originals or provider/model/`SOUL.md`.
