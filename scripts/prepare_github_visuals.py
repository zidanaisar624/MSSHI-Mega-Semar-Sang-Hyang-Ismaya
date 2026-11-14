#!/usr/bin/env python3
"""Curate and standardize MSSHI GitHub README visuals into uniform Cyber-Noir frames."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]


def _ensure_pil_on_path() -> None:
    try:
        import PIL  # noqa: F401
        return
    except ImportError:
        pass
    for cand in (
        Path("D:/HermesData/skripsi-pylibs"),
        Path.home() / "HermesData" / "skripsi-pylibs",
    ):
        if cand.is_dir() and str(cand) not in sys.path:
            sys.path.insert(0, str(cand))


_ensure_pil_on_path()

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps  # noqa: E402


BG_DARK = (11, 15, 23, 255)      # #0B0F17
BG_CARD = (17, 24, 39, 255)      # #111827
CYAN = (44, 232, 198, 255)       # #2CE8C6
ORANGE = (255, 107, 26, 255)     # #FF6B1A
PURPLE = (139, 92, 246, 255)     # #8B5CF6
EMERALD = (16, 185, 129, 255)    # #10B981
AMBER = (245, 158, 11, 255)      # #F59E0B
RED = (239, 68, 68, 255)         # #EF4444
SLATE_BORDER = (30, 41, 59, 255) # #1E293B


def hex_to_rgba(color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    c = color.lstrip("#")
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), alpha)


def load_font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = []
    if mono:
        candidates = [
            "C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        ]
    elif bold:
        candidates = [
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    else:
        candidates = [
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for path in candidates:
        if Path(path).is_file():
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def open_rgba(src: Path) -> Image.Image:
    with Image.open(src) as img:
        transposed = ImageOps.exif_transpose(img)
        return transposed.convert("RGBA")


def has_meaningful_alpha(img: Image.Image) -> bool:
    if "A" not in img.getbands():
        return False
    extrema = img.getchannel("A").getextrema()
    return extrema[0] < 245


def rounded_mask(size: tuple[int, int], radius: int, scale: int = 4) -> Image.Image:
    w, h = size
    big = Image.new("L", (w * scale, h * scale), 0)
    draw = ImageDraw.Draw(big)
    draw.rounded_rectangle((0, 0, w * scale - 1, h * scale - 1), radius=radius * scale, fill=255)
    return big.resize(size, Image.Resampling.LANCZOS)


def apply_rounded_frame(canvas: Image.Image, radius: int, border_hex: str, border_w: int) -> Image.Image:
    w, h = canvas.size
    mask = rounded_mask((w, h), radius)
    framed = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    framed.paste(canvas, (0, 0), mask)
    if border_w > 0:
        scale = 4
        overlay = Image.new("RGBA", (w * scale, h * scale), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        inset = border_w * scale // 2
        draw.rounded_rectangle(
            (inset, inset, w * scale - 1 - inset, h * scale - 1 - inset),
            radius=max(4, radius - border_w // 2) * scale,
            outline=hex_to_rgba(border_hex),
            width=border_w * scale,
        )
        overlay_small = overlay.resize((w, h), Image.Resampling.LANCZOS)
        framed = Image.alpha_composite(framed, overlay_small)
    return framed


def save_png(img: Image.Image, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst, format="PNG", optimize=True)


def make_square_avatar(
    src: Path,
    dst: Path,
    size: tuple[int, int] = (320, 320),
    radius: int = 32,
    border_hex: str = "#2CE8C6",
    border_w: int = 4,
    centering: tuple[float, float] = (0.5, 0.22),
) -> None:
    raw = open_rgba(src)
    base = Image.new("RGBA", size, BG_DARK)
    if has_meaningful_alpha(raw):
        fitted = ImageOps.contain(raw, (size[0] - 24, size[1] - 24), Image.Resampling.LANCZOS)
        base.paste(fitted, ((size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2), fitted)
    else:
        fitted = ImageOps.fit(raw, size, Image.Resampling.LANCZOS, centering=centering)
        base = fitted
    # Subtle dark bottom glow for sleek depth
    grad = Image.new("RGBA", size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grad)
    for y in range(size[1] - 56, size[1]):
        alpha = int(85 * (y - (size[1] - 56)) / 56)
        gdraw.line([(0, y), (size[0], y)], fill=(11, 15, 23, alpha))
    base = Image.alpha_composite(base, grad)
    out = apply_rounded_frame(base, radius=radius, border_hex=border_hex, border_w=border_w)
    save_png(out, dst)


def make_vertical_character_card(
    src: Path,
    dst: Path,
    size: tuple[int, int] = (540, 960),
    radius: int = 24,
    border_hex: str = "#FF6B1A",
    border_w: int = 4,
) -> None:
    w, h = size
    bg = Image.new("RGBA", size, BG_DARK)
    draw = ImageDraw.Draw(bg)
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(11 + 10 * (1 - abs(t - 0.45)))
        g = int(15 + 14 * (1 - abs(t - 0.45)))
        b = int(23 + 22 * (1 - abs(t - 0.45)))
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # Subtle cyber grid lines
    for x in range(0, w, 36):
        draw.line([(x, 0), (x, h)], fill=(44, 232, 198, 14), width=1)
    for y in range(0, h, 36):
        draw.line([(0, y), (w, y)], fill=(44, 232, 198, 14), width=1)

    # Radial warm rim glow behind skeleton silhouette
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((70, 140, w - 70, h - 180), fill=(255, 107, 26, 48))
    gd.ellipse((110, 220, w - 110, h - 220), fill=(44, 232, 198, 36))
    glow = glow.filter(ImageFilter.GaussianBlur(42))
    bg = Image.alpha_composite(bg, glow)

    char = open_rgba(src)
    fitted = ImageOps.contain(char, (w - 44, h - 48), Image.Resampling.LANCZOS)
    cx = (w - fitted.width) // 2
    cy = (h - fitted.height) // 2
    bg.paste(fitted, (cx, cy), fitted)

    out = apply_rounded_frame(bg, radius=radius, border_hex=border_hex, border_w=border_w)
    save_png(out, dst)


def make_hero_banner(
    src: Path,
    dst: Path,
    size: tuple[int, int] = (1280, 420),
    radius: int = 24,
) -> None:
    w, h = size
    raw = open_rgba(src)
    bg = ImageOps.fit(raw, size, Image.Resampling.LANCZOS, centering=(0.55, 0.36))

    # Left dark gradient scrim so editorial typography stays 100% legible over keyart
    scrim = Image.new("RGBA", size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(scrim)
    for x in range(w):
        ratio = x / w
        if ratio < 0.56:
            alpha = int(218 - ratio * 150)
        else:
            alpha = max(35, int(134 - (ratio - 0.56) * 210))
        sdraw.line([(x, 0), (x, h)], fill=(11, 15, 23, alpha))
    canvas = Image.alpha_composite(bg, scrim)

    # Bottom subtle tint bar
    bgrad = Image.new("RGBA", size, (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(bgrad)
    for y in range(h - 90, h):
        a = int(145 * (y - (h - 90)) / 90)
        bdraw.line([(0, y), (w, y)], fill=(11, 15, 23, a))
    canvas = Image.alpha_composite(canvas, bgrad)

    draw = ImageDraw.Draw(canvas)
    f_badge = load_font(18, bold=True, mono=True)
    f_title = load_font(60, bold=True)
    f_sub = load_font(23, bold=True)
    f_meta = load_font(19, bold=False, mono=True)

    # Top pill badge (measured dynamically)
    badge_txt = "HERMES ULTIMATE OPTIMIZER · SOVEREIGN SUITE"
    pill_w = int(draw.textlength(badge_txt, font=f_badge)) + 36
    pill_box = (48, 48, 48 + pill_w, 88)
    draw.rounded_rectangle(pill_box, radius=18, fill=(17, 24, 39, 230), outline=CYAN, width=2)
    draw.text((66, 56), badge_txt, font=f_badge, fill=CYAN)

    # Accent vertical bar + Headline
    draw.rounded_rectangle((48, 114, 56, 250), radius=4, fill=ORANGE)
    draw.text((76, 108), "MSSHI v3.1.0", font=f_title, fill=(248, 250, 252, 255))
    draw.text((78, 182), "Mega Semar Sang Hyang Ismaya", font=f_sub, fill=(226, 232, 240, 255))
    draw.text(
        (78, 218),
        "63 Bundled Skills · 49 Upstreams · 5 MuZA Bots · Skripsi v1.1",
        font=f_meta,
        fill=AMBER,
    )

    # Bottom feature chips
    chips = [
        ("CLI-Anything 4GB RAM", CYAN),
        ("$1 Zero-Waste Shield", EMERALD),
        ("MuZA Skripsi Drag-and-Drop", ORANGE),
        ("Drive C:/D: Adaptif", PURPLE),
    ]
    x_cur = 48
    for label, color in chips:
        tw = int(draw.textlength(label, font=f_badge))
        cw = tw + 28
        draw.rounded_rectangle((x_cur, 320, x_cur + cw, 360), radius=12, fill=(15, 23, 42, 235), outline=color, width=2)
        draw.text((x_cur + 14, 329), label, font=f_badge, fill=(241, 245, 249, 255))
        x_cur += cw + 14

    # Dual-tone gradient neon border (Cyan -> Orange)
    mask = rounded_mask(size, radius)
    framed = Image.new("RGBA", size, (0, 0, 0, 0))
    framed.paste(canvas, (0, 0), mask)

    border_strip = Image.new("RGBA", size, (0, 0, 0, 0))
    bs_draw = ImageDraw.Draw(border_strip)
    for x in range(w):
        t = x / max(1, w - 1)
        r = int(44 * (1 - t) + 255 * t)
        g = int(232 * (1 - t) + 107 * t)
        b = int(198 * (1 - t) + 26 * t)
        bs_draw.line([(x, 0), (x, h)], fill=(r, g, b, 255))

    stroke_mask = Image.new("L", (w * 2, h * 2), 0)
    sm_draw = ImageDraw.Draw(stroke_mask)
    sm_draw.rounded_rectangle((4, 4, w * 2 - 5, h * 2 - 5), radius=radius * 2, outline=255, width=8)
    stroke_small = stroke_mask.resize(size, Image.Resampling.LANCZOS)
    framed.paste(border_strip, (0, 0), stroke_small)
    save_png(framed, dst)


def make_uniform_meme_panel(
    src: Path,
    dst: Path,
    size: tuple[int, int] = (640, 400),
    radius: int = 20,
    border_hex: str = "#1E293B",
    border_w: int = 3,
    rotate_deg: int = 0,
) -> None:
    w, h = size
    raw = open_rgba(src)
    if rotate_deg:
        raw = raw.rotate(rotate_deg, expand=True)
    base = Image.new("RGBA", size, BG_DARK)

    if has_meaningful_alpha(raw):
        # Soft radial contrast card so dark characters on transparent PNGs remain crisp
        glow = Image.new("RGBA", size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse((70, 20, w - 70, h - 20), fill=(30, 41, 59, 240))
        gd.ellipse((150, 50, w - 150, h - 50), fill=(51, 65, 85, 220))
        glow = glow.filter(ImageFilter.GaussianBlur(28))
        base = Image.alpha_composite(base, glow)
        draw = ImageDraw.Draw(base)
        for gx in range(0, w, 32):
            draw.line([(gx, 0), (gx, h)], fill=(44, 232, 198, 12), width=1)
        for gy in range(0, h, 32):
            draw.line([(0, gy), (w, gy)], fill=(44, 232, 198, 12), width=1)
        inner = ImageOps.contain(raw, (w - 40, h - 42), Image.Resampling.LANCZOS)
    else:
        blur_bg = ImageOps.fit(raw, size, Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(18))
        dim = Image.new("RGBA", size, (11, 15, 23, 155))
        base = Image.alpha_composite(blur_bg, dim)
        inner = ImageOps.contain(raw, (w - 28, h - 24), Image.Resampling.LANCZOS)

    px = (w - inner.width) // 2
    py = (h - inner.height) // 2

    if not has_meaningful_alpha(raw):
        # Subtle inner rounded frame shadow around contained photo
        shadow = Image.new("RGBA", size, (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(shadow)
        sdraw.rounded_rectangle((px - 3, py - 3, px + inner.width + 3, py + inner.height + 3), radius=10, fill=(0, 0, 0, 140))
        shadow = shadow.filter(ImageFilter.GaussianBlur(6))
        base = Image.alpha_composite(base, shadow)

    base.paste(inner, (px, py), inner)
    out = apply_rounded_frame(base, radius=radius, border_hex=border_hex, border_w=border_w)
    save_png(out, dst)


def make_widescreen_showcase(
    src: Path,
    dst: Path,
    size: tuple[int, int] = (1280, 720),
    radius: int = 22,
    border_hex: str = "#8B5CF6",
    border_w: int = 4,
) -> None:
    make_uniform_meme_panel(src, dst, size=size, radius=radius, border_hex=border_hex, border_w=border_w)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_jobs(
    repo_root: Path,
    hermes_dir: Path,
    meme_dir: Path,
    pp_dir: Path,
    archive_dir: Path | None,
) -> list[dict[str, Any]]:
    def find_first(candidates: list[Path]) -> Path | None:
        for p in candidates:
            if p.is_file():
                return p
        return None

    fullbody = find_first([
        *( [archive_dir / "Arsip_Pribadi_MuZA_Jangan_Dihapus" / "Proyek_Aktif_Nov_2026" / "detective_skull_fullbody_clean.png"] if archive_dir else [] ),
        repo_root.parent / "03_Arsip_Visual_dan_Laporan_PDF" / "Arsip_Pribadi_MuZA_Jangan_Dihapus" / "Proyek_Aktif_Nov_2026" / "detective_skull_fullbody_clean.png",
        repo_root.parent / "03_Aset_Visual_dan_Dokumen_MuZA" / "Arsip_Pribadi_MuZA_Jangan_Dihapus" / "Proyek_Aktif_Nov_2026" / "detective_skull_fullbody_clean.png",
        repo_root / "assets" / "pp-tiktok" / "hero-sovereign-orchestrator.jpg",
    ])
    kikichii = find_first([
        repo_root / "assets" / "pp-tiktok" / "kiki-chii-panic.jpg",
        pp_dir / "11" / "kiki-chii-panic.jpg",
    ])
    hero_bg = find_first([
        hermes_dir / "Paket Usil" / "hermes-mfa-filmmaking-and-agent-skills" / "assets" / "cinematic-studio" / "16_original_keyart_studio_research.jpg",
        repo_root / "assets" / "visuals" / "studio-keyart-research.jpg",
    ])
    showcase_src = find_first([
        hermes_dir / "Paket Usil" / "hermes-mfa-filmmaking-and-agent-skills" / "assets" / "cinematic-studio" / "05_auto_curiousity_loop.png",
        repo_root / "assets" / "visuals" / "auto-curiosity-loop.png",
    ])
    showcase_conv = find_first([
        hermes_dir / "Paket Usil" / "hermes-mfa-filmmaking-and-agent-skills" / "assets" / "cinematic-studio" / "15_original_keyart_creative_convergence.jpg",
        repo_root / "assets" / "visuals" / "creative-convergence-keyart.jpg",
    ])

    return [
        {"id": "hero-muza-banner", "fn": "hero", "src": hero_bg, "collection": "hermes_ai", "out": "assets/avatars/hero-muza-banner.png", "border": "#2CE8C6", "purpose": "Hero Banner Utama MSSHI v3.1.0"},
        {"id": "muza-noir-fullbody", "fn": "vertical", "src": fullbody, "collection": "archive_local", "out": "assets/avatars/muza-noir-fullbody.png", "border": "#FF6B1A", "purpose": "Karakter Full-Body Noir Sovereign Architect"},
        {"id": "bot-01-yukino", "fn": "square", "src": hermes_dir / "Yukino Yukinoshita.jpg", "collection": "hermes_ai", "out": "assets/avatars/bot-01-yukino.png", "border": "#2CE8C6", "centering": (0.5, 0.22), "purpose": "Avatar Bot 01 — Yukino Yukinoshita"},
        {"id": "bot-02-shizuka", "fn": "square", "src": hermes_dir / "download.jpg", "collection": "hermes_ai", "out": "assets/avatars/bot-02-shizuka.png", "border": "#8B5CF6", "centering": (0.5, 0.24), "purpose": "Avatar Bot 02 — Sensei Shizuka Hiratsuka"},
        {"id": "bot-03-val", "fn": "square", "src": hermes_dir / "download (1).jpg", "collection": "hermes_ai", "out": "assets/avatars/bot-03-val.png", "border": "#F59E0B", "centering": (0.5, 0.20), "purpose": "Avatar Bot 03 — Val Academic Engine"},
        {"id": "bot-04-kikichii", "fn": "square", "src": kikichii, "collection": "pp_tiktok", "out": "assets/avatars/bot-04-kikichii.png", "border": "#FF6B1A", "centering": (0.5, 0.25), "purpose": "Avatar Bot 04 — Kiki-Chii Creative Director"},
        {"id": "bot-05-shikaku", "fn": "square", "src": hermes_dir / "Shikaku nara.jpg", "collection": "hermes_ai", "out": "assets/avatars/bot-05-shikaku.png", "border": "#10B981", "centering": (0.5, 0.22), "purpose": "Avatar Bot 05 — Shikaku Nara Principal Architect"},
        {"id": "showcase-hermes-ecosystem", "fn": "showcase", "src": showcase_src, "collection": "hermes_ai", "out": "assets/showcases/showcase-hermes-ecosystem.png", "border": "#8B5CF6", "purpose": "Showcase Auto-Curiosity Loop & Creative Architecture"},
        {"id": "showcase-creative-convergence", "fn": "showcase", "src": showcase_conv, "collection": "hermes_ai", "out": "assets/showcases/showcase-creative-convergence.png", "border": "#2CE8C6", "purpose": "Showcase Creative Convergence & Sovereign Team"},
        {"id": "meme-01-era-v1", "fn": "meme", "src": hermes_dir / "The Code Is Watching You(Edited).png", "collection": "hermes_ai", "out": "assets/memes/meme-01-era-v1.png", "border": "#EF4444", "purpose": "Panel 1 Komik Evolusi — Era v1.0 & Overheat 22 MCP"},
        {"id": "meme-02-era-v2", "fn": "meme", "src": meme_dir / "1000127102.jpg", "collection": "meme_reaction", "out": "assets/memes/meme-02-era-v2.png", "border": "#1E293B", "purpose": "Panel 2 Komik Evolusi — Era v2.0 Hydrogen vs Coughing Baby"},
        {"id": "meme-03-era-v30", "fn": "meme", "src": meme_dir / "1056516393853577230.jpg", "collection": "meme_reaction", "out": "assets/memes/meme-03-era-v30.png", "border": "#1E293B", "purpose": "Panel 3 Komik Evolusi — Era v3.0 Blissful Sunlight Dog (RAM 4GB Lega)"},
        {"id": "meme-04-era-v31", "fn": "meme", "src": pp_dir / "19" / "ChatGPT Image Oct 18, 2026, 12_18_06 PM.png", "collection": "pp_tiktok", "out": "assets/memes/meme-04-era-v31.png", "border": "#1E293B", "purpose": "Panel 4 Komik Evolusi — Era v3.1.0 Santai Taking It Easy"},
        {"id": "meme-05-skripsi-drop", "fn": "meme", "src": hermes_dir / "download (10).jpg", "collection": "hermes_ai", "out": "assets/memes/meme-05-skripsi-drop.png", "border": "#2CE8C6", "rotate_deg": -90, "purpose": "Meme Mahasiswa Pusing Skripsi Sebelum MuZA Drag-and-Drop"},
        {"id": "meme-06-budget-dan-cdrive", "fn": "meme", "src": meme_dir / "_trgny080-7339489384661536032-slide__1_-removebg-preview (1).png", "collection": "meme_reaction", "out": "assets/memes/meme-06-budget-dan-cdrive.png", "border": "#FF6B1A", "purpose": "Meme Pasrah Kuota Tipis $1 & Laptop Drive C:"},
        {"id": "gallery-extra-01", "fn": "meme", "src": hermes_dir / "download (7).jpg", "collection": "hermes_ai", "out": "assets/memes/gallery-extra-01.png", "border": "#334155", "purpose": "Extra Meme 01 — Deep Thinking Mode di Depan Kode"},
        {"id": "gallery-extra-02", "fn": "meme", "src": meme_dir / "973692381954724340.jpg", "collection": "meme_reaction", "out": "assets/memes/gallery-extra-02.png", "border": "#334155", "purpose": "Extra Meme 02 — Kucing Pusing Kontemplasi Spesifikasi"},
        {"id": "gallery-extra-03", "fn": "meme", "src": hermes_dir / "download (2).jpg", "collection": "hermes_ai", "out": "assets/memes/gallery-extra-03.png", "border": "#334155", "purpose": "Extra Meme 03 — Vibecoding Mode di Laptop Spek Pas-pasan"},
        {"id": "gallery-extra-04", "fn": "meme", "src": pp_dir / "19" / "ChatGPT Image Oct 18, 2026, 12_19_04 PM.png", "collection": "pp_tiktok", "out": "assets/memes/gallery-extra-04.png", "border": "#334155", "purpose": "Extra Meme 04 — Cozy Chaos Engineering"},
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Standardize curated visual assets for MSSHI GitHub README.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--hermes-dir", type=Path, default=Path(os.environ.get("MSSHI_ASSETS_HERMES_DIR", ".")))
    parser.add_argument("--meme-dir", type=Path, default=Path(os.environ.get("MSSHI_ASSETS_MEME_DIR", ".")))
    parser.add_argument("--pp-dir", type=Path, default=Path(os.environ.get("MSSHI_ASSETS_PP_DIR", ".")))
    parser.add_argument("--archive-dir", type=Path, default=None)
    parser.add_argument("--local-archive-copy", type=Path, default=None, help="Optional outside-repo archive dir for processed PNG copies.")
    parser.add_argument("--local-manifest-out", type=Path, default=None, help="Optional outside-repo JSON storing local source paths.")
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    jobs = build_jobs(
        repo_root,
        args.hermes_dir.expanduser(),
        args.meme_dir.expanduser(),
        args.pp_dir.expanduser(),
        args.archive_dir.expanduser() if args.archive_dir else None,
    )

    portable_items: list[dict[str, Any]] = []
    local_items: list[dict[str, Any]] = []
    missing: list[str] = []

    for job in jobs:
        src: Path | None = job["src"]
        dst = repo_root / job["out"]
        if src is None or not src.is_file():
            missing.append(f"{job['id']} -> {src}")
            continue
        fn = job["fn"]
        if fn == "square":
            make_square_avatar(src, dst, border_hex=job["border"], centering=job.get("centering", (0.5, 0.22)))
        elif fn == "vertical":
            make_vertical_character_card(src, dst, border_hex=job["border"])
        elif fn == "hero":
            make_hero_banner(src, dst)
        elif fn == "meme":
            make_uniform_meme_panel(src, dst, border_hex=job["border"], rotate_deg=job.get("rotate_deg", 0))
        elif fn == "showcase":
            make_widescreen_showcase(src, dst, border_hex=job["border"])

        with Image.open(dst) as rendered:
            width, height = rendered.size

        if args.local_archive_copy:
            copy_target = args.local_archive_copy / Path(job["out"]).name
            copy_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dst, copy_target)

        portable_entry = {
            "id": job["id"],
            "output": job["out"],
            "canvas_type": fn,
            "width": width,
            "height": height,
            "border_hex": job["border"],
            "source_collection": job["collection"],
            "source_filename": src.name,
            "purpose": job["purpose"],
            "size_bytes": dst.stat().st_size,
            "sha256": sha256_file(dst),
        }
        portable_items.append(portable_entry)
        local_items.append({**portable_entry, "local_source_path": str(src)})
        print(f"OK [{fn:8s}] {job['out']} ({width}x{height}, {dst.stat().st_size // 1024} KiB) <- {src.name}")

    manifest_path = repo_root / "configs" / "visual_assets_manifest.json"
    manifest_payload = {
        "schema_version": 1,
        "theme": "Cyber-Noir Editorial Comic (Dual-Tone Cyan #2CE8C6 + Orange #FF6B1A on #0B0F17)",
        "total_standardized_assets": len(portable_items),
        "canvases": {
            "square_avatar": "320x320 rounded 32px, 4px neon character border",
            "vertical_character": "540x960 rounded 24px, #FF6B1A 4px border on #0B0F17 rim-glow backdrop",
            "hero_banner": "1280x420 rounded 24px, dual-tone Cyan-to-Orange gradient border",
            "uniform_meme_panel": "640x400 (16:10) rounded 20px, contain-fit with blurred dark backdrop",
            "widescreen_showcase": "1280x720 (16:9) rounded 22px, 4px accent border",
        },
        "assets": portable_items,
    }
    manifest_path.write_text(json.dumps(manifest_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"WROTE_MANIFEST: {manifest_path} ({len(portable_items)} items)")

    if args.local_manifest_out:
        args.local_manifest_out.parent.mkdir(parents=True, exist_ok=True)
        args.local_manifest_out.write_text(
            json.dumps({"items": local_items, "missing": missing}, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"WROTE_LOCAL_MANIFEST: {args.local_manifest_out}")

    if missing:
        print("MISSING_SOURCES:")
        for item in missing:
            print(" ", item)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
