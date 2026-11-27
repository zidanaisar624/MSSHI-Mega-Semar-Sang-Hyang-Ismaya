#!/usr/bin/env python3
"""MSSHI Rp0 Meme Studio Helper for Kiki-Chii (v3.2.1).

Combines deterministic zero-key mechanics inspired by:
- dhruvmehra/makememe (MIT): memegen.link URL escaping & zero-key PNG URL builder
- edwinjhlee/awesome-meme (MIT): local Pillow Impact/CJK stroke text renderer & programmer template index
- csmoove530/meme-lord (MIT, clean local subset): 6-dimension weighted A/B HTML rating sheet (0 paid APIs)
- RiskAverseTech/createa-meme-skill (MIT): caption-craft word-count guard (2-6 words ideal)

Zero LLM calls, zero mandatory API keys, zero background daemons.
"""
from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path
import sys
import urllib.request

sys.dont_write_bytecode = True

MEMEGEN_BASE = "https://api.memegen.link"

# Curated offline template directory merging classic memegen.link IDs & awesome-meme programmer IDs
OFFLINE_TEMPLATES: tuple[dict[str, object], ...] = (
    {"id": "drake", "awesome_id": "drake-hotline-bling", "slots": 2, "tags": "choice contrast coding", "meaning": "Reject option 1, prefer option 2"},
    {"id": "db", "awesome_id": "distracted-boyfriend", "slots": 3, "tags": "temptation shiny-object coding", "meaning": "Distracted by new shiny thing over current commitment"},
    {"id": "fine", "awesome_id": "this-is-fine", "slots": 2, "tags": "crisis fire bug deploy", "meaning": "Everything is on fire while pretending it is fine"},
    {"id": "astronaut", "awesome_id": "always-has-been", "slots": 2, "tags": "realization truth architecture", "meaning": "Wait, it's all X? Always has been"},
    {"id": "cmm", "awesome_id": "change-my-mind", "slots": 1, "tags": "opinion debate hot-take", "meaning": "Controversial take inviting debate"},
    {"id": "gru", "awesome_id": "grus-plan", "slots": 4, "tags": "plan backfire bug", "meaning": "4-step plan where step 3 backfires"},
    {"id": "panik-kalm-panik", "awesome_id": "panik-kalm-panik", "slots": 3, "tags": "escalation plot-twist prod", "meaning": "Panic -> calm -> worse panic"},
    {"id": "rollsafe", "awesome_id": "roll-safe", "slots": 2, "tags": "ironic logic coding", "meaning": "Clever-sounding terrible logic"},
    {"id": "woman-cat", "awesome_id": "woman-yelling-cat", "slots": 2, "tags": "argument deadpan review", "meaning": "Emotional accusation vs unbothered cat"},
    {"id": "harold", "awesome_id": "hide-pain-harold", "slots": 2, "tags": "pain smile deadline thesis", "meaning": "Smiling politely through deep internal pain"},
    {"id": "brain", "awesome_id": "expanding-brain", "slots": 4, "tags": "escalation overengineering", "meaning": "4-tier increasingly absurd progression"},
    {"id": "ds", "awesome_id": "daily-struggle", "slots": 2, "tags": "dilemma choice", "meaning": "Sweating over two hard red buttons"},
    {"id": "success", "awesome_id": "success-kid", "slots": 2, "tags": "victory build-green", "meaning": "Small but genuine victory"},
    {"id": "mordor", "awesome_id": "one-does-not-simply", "slots": 2, "tags": "difficulty classic", "meaning": "One does not simply do X"},
    {"id": "doge", "awesome_id": "doge", "slots": 2, "tags": "ironic praise classic", "meaning": "Playful confusion or ironic praise"},
    {"id": "vim-exit", "awesome_id": "vim-exit", "slots": 2, "tags": "programmer coding vim", "meaning": "Trapped and unable to exit Vim"},
    {"id": "it-works-why", "awesome_id": "it-works-why", "slots": 2, "tags": "programmer coding mystery", "meaning": "Code works in prod and nobody knows why"},
    {"id": "wtf-per-minute", "awesome_id": "wtf-per-minute", "slots": 2, "tags": "programmer code-review quality", "meaning": "Code quality measured in WTFs/minute"},
    {"id": "monday-deploy", "awesome_id": "monday-deploy", "slots": 2, "tags": "programmer deploy devops", "meaning": "Deploying right before weekend/Monday chaos"},
    {"id": "stackoverflow-copy", "awesome_id": "stackoverflow-copy", "slots": 2, "tags": "programmer copy-paste", "meaning": "Shipping copy-pasted snippets"},
    {"id": "bug-feature", "awesome_id": "bug-feature", "slots": 2, "tags": "programmer product", "meaning": "It is not a bug, it is a feature"},
    {"id": "chill-guy", "awesome_id": "chill-guy", "slots": 2, "tags": "calm pressure deadline", "meaning": "Unbothered chill guy under pressure"},
)

WEIGHTS = {
    "concept": 0.30,
    "quality": 0.25,
    "meme_fit": 0.20,
    "consistency": 0.15,
    "speed": 0.05,
    "cost": 0.05,
}

LATIN_FONTS = (
    r"C:\Windows\Fonts\impact.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    "/System/Library/Fonts/Supplemental/Impact.ttf",
    "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
)

CJK_FONTS = (
    r"C:\Windows\Fonts\msyhbd.ttc",
    r"C:\Windows\Fonts\msgothic.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
)


def escape_memegen(text: str) -> str:
    """Escape a caption line according to memegen.link URL rules."""
    if not text or not text.strip():
        return "_"
    out = text.strip()
    out = out.replace("_", "__")
    out = out.replace("-", "--")
    out = out.replace(" ", "_")
    out = out.replace("\n", "~n")
    out = out.replace("?", "~q")
    out = out.replace("&", "~a")
    out = out.replace("%", "~p")
    out = out.replace("#", "~h")
    out = out.replace("/", "~s")
    out = out.replace("\\", "~b")
    out = out.replace("<", "~l")
    out = out.replace(">", "~g")
    out = out.replace('"', "''")
    return out


def build_memegen_url(template: str, lines: list[str], ext: str = "png") -> str:
    slug = template.strip().strip("/")
    escaped = "/".join(escape_memegen(line) for line in (lines or ["_"]))
    clean_ext = ext.lstrip(".").lower() or "png"
    return f"{MEMEGEN_BASE}/images/{slug}/{escaped}.{clean_ext}"


def caption_lint(lines: list[str]) -> list[str]:
    warnings: list[str] = []
    for idx, line in enumerate(lines, start=1):
        words = [w for w in line.strip().split() if w]
        if len(words) > 10:
            warnings.append(f"Line {idx} has {len(words)} words (caption-craft target is 2-6 words, max 10).")
    return warnings


def has_cjk(text: str) -> bool:
    for ch in text:
        cp = ord(ch)
        if (0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF or 0x3000 <= cp <= 0x30FF or 0xAC00 <= cp <= 0xD7AF):
            return True
    return False


def _load_font(size: int, prefer_cjk: bool):
    from PIL import ImageFont

    candidates = CJK_FONTS + LATIN_FONTS if prefer_cjk else LATIN_FONTS
    for candidate in candidates:
        if os.path.isfile(candidate):
            try:
                return ImageFont.truetype(candidate, size)
            except Exception:
                continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def render_local_meme(
    output_path: Path,
    image_path: Path | None = None,
    canvas: str | None = None,
    top_text: str = "",
    bottom_text: str = "",
) -> dict[str, object]:
    from PIL import Image, ImageDraw

    if image_path is not None:
        img = Image.open(image_path).convert("RGB")
    else:
        raw_size = (canvas or "800x600").lower().split("x", 1)
        w, h = int(raw_size[0]), int(raw_size[1])
        img = Image.new("RGB", (w, h), (28, 32, 42))

    w, h = img.size
    draw = ImageDraw.Draw(img)
    base_size = max(22, min(64, w // 14))
    stroke = max(2, base_size // 10)

    def _draw_band(text: str, y_center: int) -> None:
        if not text.strip():
            return
        label = text.strip() if has_cjk(text) else text.strip().upper()
        font = _load_font(base_size, prefer_cjk=has_cjk(label))
        draw.text(
            (w // 2, y_center),
            label,
            font=font,
            fill="white",
            stroke_width=stroke,
            stroke_fill="black",
            anchor="mm",
        )

    _draw_band(top_text, max(base_size, int(h * 0.11)))
    _draw_band(bottom_text, min(h - base_size, int(h * 0.89)))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    return {
        "ok": True,
        "output": str(output_path),
        "size": [w, h],
        "warnings": caption_lint([t for t in (top_text, bottom_text) if t]),
    }


def composite_score(scores: dict[str, float]) -> float:
    return round(sum(float(scores.get(k, 8.0)) * w for k, w in WEIGHTS.items()), 2)


def generate_ab_html(title: str, candidates: list[dict[str, object]], output_path: Path) -> Path:
    cards = []
    for idx, item in enumerate(candidates, start=1):
        label = html.escape(str(item.get("label", f"Candidate {idx}")))
        src = html.escape(str(item.get("image", "")))
        pattern = html.escape(str(item.get("pattern", "Ironic Contrast")))
        sc = item.get("scores") if isinstance(item.get("scores"), dict) else {}
        default_scores = {
            "concept": float(sc.get("concept", 8.5)),
            "quality": float(sc.get("quality", 8.5)),
            "meme_fit": float(sc.get("meme_fit", 8.5)),
            "consistency": float(sc.get("consistency", 8.5)),
            "speed": float(sc.get("speed", 9.5)),
            "cost": float(sc.get("cost", 10.0)),
        }
        total = composite_score(default_scores)
        cards.append(
            f"<section class='card'><h2>#{idx} {label}</h2>"
            f"<p class='meta'>Pattern: <strong>{pattern}</strong> | Composite: <strong>{total}/10</strong> (Rp0)</p>"
            f"{f'<img src=\"{src}\" alt=\"{label}\">' if src else ''}"
            f"<ul>"
            + "".join(f"<li><code>{k}</code> ({int(WEIGHTS[k]*100)}%): {v}</li>" for k, v in default_scores.items())
            + "</ul></section>"
        )
    doc = (
        "<!doctype html><html lang='id'><head><meta charset='utf-8'>"
        f"<title>{html.escape(title)}</title>"
        "<style>body{font-family:system-ui,sans-serif;background:#0f172a;color:#f8fafc;margin:24px}"
        ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}"
        ".card{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:16px}"
        "img{max-width:100%;border-radius:8px;margin:8px 0}.meta{color:#38bdf8;font-size:.9rem}</style>"
        f"</head><body><h1>{html.escape(title)}</h1>"
        "<p>Rubrik 6 Dimensi (30% Concept, 25% Quality, 20% Meme Fit, 15% Consistency, 5% Speed, 5% Cost).</p>"
        f"<div class='grid'>{''.join(cards)}</div></body></html>"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(doc, encoding="utf-8")
    return output_path


def search_templates(query: str = "") -> list[dict[str, object]]:
    q = query.strip().lower()
    if not q:
        return [dict(row) for row in OFFLINE_TEMPLATES]
    return [
        dict(row)
        for row in OFFLINE_TEMPLATES
        if q in str(row["id"]).lower()
        or q in str(row["awesome_id"]).lower()
        or q in str(row["tags"]).lower()
        or q in str(row["meaning"]).lower()
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MSSHI Kiki-Chii Rp0 Meme Studio Helper")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_esc = sub.add_parser("escape", help="Escape text for memegen.link URL")
    p_esc.add_argument("text")

    p_tpl = sub.add_parser("templates", help="Search curated offline meme templates (0 network)")
    p_tpl.add_argument("--query", default="")

    p_url = sub.add_parser("url", help="Build zero-key memegen.link PNG URL")
    p_url.add_argument("template")
    p_url.add_argument("lines", nargs="+")
    p_url.add_argument("--ext", default="png")
    p_url.add_argument("--download", default="")

    p_loc = sub.add_parser("render-local", help="Render classic Impact stroke text onto local image/canvas via Pillow")
    p_loc.add_argument("--image", default="")
    p_loc.add_argument("--canvas", default="800x600")
    p_loc.add_argument("--top", default="")
    p_loc.add_argument("--bottom", default="")
    p_loc.add_argument("--output", required=True)

    p_ab = sub.add_parser("ab-rate-html", help="Generate offline 6-dimension A/B meme comparison HTML")
    p_ab.add_argument("--title", default="Kiki-Chii Meme A/B Evaluation")
    p_ab.add_argument("--candidate", action="append", default=[], help="Format: Label:image_path:Pattern")
    p_ab.add_argument("--output", required=True)

    args = parser.parse_args(argv)
    if args.cmd == "escape":
        print(escape_memegen(args.text))
        return 0
    if args.cmd == "templates":
        rows = search_templates(args.query)
        print(json.dumps({"count": len(rows), "templates": rows}, ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "url":
        url = build_memegen_url(args.template, args.lines, args.ext)
        payload: dict[str, object] = {"url": url, "warnings": caption_lint(args.lines)}
        if args.download:
            dest = Path(args.download)
            dest.parent.mkdir(parents=True, exist_ok=True)
            req = urllib.request.Request(url, headers={"User-Agent": "MSSHI-MemeStudio/3.2.1"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                dest.write_bytes(resp.read())
            payload["downloaded"] = str(dest)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "render-local":
        img_p = Path(args.image) if args.image else None
        res = render_local_meme(Path(args.output), img_p, args.canvas, args.top, args.bottom)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "ab-rate-html":
        parsed = []
        for raw in args.candidate:
            parts = (raw.split(":", 2) + ["", ""])[:3]
            parsed.append({"label": parts[0] or "Candidate", "image": parts[1], "pattern": parts[2] or "Ironic Contrast"})
        out = generate_ab_html(args.title, parsed, Path(args.output))
        print(json.dumps({"ok": True, "output": str(out), "candidates": len(parsed)}, ensure_ascii=False, indent=2))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
