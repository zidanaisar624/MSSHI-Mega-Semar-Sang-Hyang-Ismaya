---
name: spacewise
description: Safe local storage cleanup with Spacewise across all bots: scan one exact named folder for duplicates, leftover installers, similar/blurry photos, and large files; preview locally; move only user-approved categories to Trash (undoable). Local-only, zero network, human approval required.
---

# Spacewise — Safe Local Storage Cleanup (All Bots)

Upstream: `https://github.com/ardianreffa/spacewise` (MIT, Copyright 2026 ardianreffa, pin `8e4f39aa49d9ad31e5972a67f886434c59dbc988`) · Hermes Marketplace: `https://hermes-agent.nousresearch.com/marketplace/spacewise`.

Spacewise scans and enforces boundaries locally (`0` network calls); you translate findings clearly; **the user decides**.

## Mandatory Rules
1. **Take the folder literally.** Use the exact folder the user named. Never guess, widen, or add `include_subfolders=true` unless explicitly asked. If the request is vague (*"bersihkan foto"*), ask which folder first.
2. **Respect refusals & vault rules.** If Spacewise or a local vault guardrail refuses a folder (OS/system/hidden/locked/library/private vault), report the exact reason and ask the user — never work around it.
3. **Report `scanned_exactly` and the 3 tiers with exact numbers:**
   - **Green**: exact duplicates (one copy always stays) and leftover installers.
   - **Amber**: similar photos (sharpest stays) and blurry/near-black photos — advise the user to inspect visually before deciding.
   - **Grey**: large videos, screenshots, and other large files — reported only, never moved or recommended for removal.
4. **Preview first**: offer `spacewise_preview` and share the local preview page path.
5. **Move only on explicit current-turn approval**: call `spacewise_trash` only for categories the user explicitly names in the current message (protected by Hermes `pre_tool_call` approval prompt). Mention `spacewise_undo` after any move.

## Platform Honesty (Windows vs macOS/Linux)
- **macOS & Linux**: full workflow (`spacewise_scan`, `spacewise_preview`, `spacewise_trash`, `spacewise_undo`) inside home subfolders and mounted external drives.
- **Windows**: `spacewise_scan` and `spacewise_preview` work inside subfolders of the user's home directory (`C:\Users\<user>\...`). Moving files to the Recycle Bin (`spacewise_trash`/`spacewise_undo`) is macOS/Linux-only in upstream Spacewise (reports honestly without deleting), and non-home drives (e.g., `D:\`) are refused by upstream `guard.py`.
- Requires `Pillow` (+ `pillow-heif` for `.heic`/`.heif`). Never modifies provider/model/`SOUL.md`.
