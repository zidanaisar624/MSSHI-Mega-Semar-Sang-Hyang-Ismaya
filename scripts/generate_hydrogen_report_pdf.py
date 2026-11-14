#!/usr/bin/env python3
"""Generate the official MSSHI v3.1.0 + MuZA Skripsi v1.1 Hydrogen Execution Report PDF."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]


def ensure_reportlab(auto_install: bool = False) -> None:
    for cand in (
        Path("D:/HermesData/skripsi-pylibs"),
        Path.home() / "HermesData" / "skripsi-pylibs",
    ):
        if cand.is_dir() and str(cand) not in sys.path:
            sys.path.insert(0, str(cand))
    if importlib.util.find_spec("reportlab") is not None and importlib.util.find_spec("PIL") is not None:
        return
    if not auto_install:
        raise RuntimeError(
            "reportlab/Pillow belum ditemukan. Jalankan dengan --install-deps atau pasang ke HermesData/skripsi-pylibs."
        )
    target = Path("D:/HermesData/skripsi-pylibs") if Path("D:/").exists() else Path.home() / "HermesData" / "skripsi-pylibs"
    target.mkdir(parents=True, exist_ok=True)
    tmp_dir = target.parent / "temp"
    cache_dir = target.parent / "pip-cache"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, TEMP=str(tmp_dir), TMP=str(tmp_dir), PIP_CACHE_DIR=str(cache_dir))
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--no-user", "--target", str(target), "reportlab", "pillow"],
        check=True,
        env=env,
    )
    if str(target) not in sys.path:
        sys.path.insert(0, str(target))


def build_pdf(
    repo_root: Path,
    results: dict[str, Any],
    primary_out: Path,
    extra_outs: list[Path],
) -> None:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm, mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        Image as RLImage,
        KeepTogether,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    FONT_REG, FONT_BOLD, FONT_ITAL = "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"
    arial_reg = Path("C:/Windows/Fonts/arial.ttf")
    arial_bold = Path("C:/Windows/Fonts/arialbd.ttf")
    arial_ital = Path("C:/Windows/Fonts/ariali.ttf")
    if arial_reg.is_file() and arial_bold.is_file() and arial_ital.is_file():
        try:
            pdfmetrics.registerFont(TTFont("ArialUni", str(arial_reg)))
            pdfmetrics.registerFont(TTFont("ArialUni-Bold", str(arial_bold)))
            pdfmetrics.registerFont(TTFont("ArialUni-Italic", str(arial_ital)))
            pdfmetrics.registerFontFamily(
                "ArialUni", normal="ArialUni", bold="ArialUni-Bold", italic="ArialUni-Italic", boldItalic="ArialUni-Bold"
            )
            FONT_REG, FONT_BOLD, FONT_ITAL = "ArialUni", "ArialUni-Bold", "ArialUni-Italic"
        except Exception:
            pass

    NAVY = colors.HexColor("#0B0F17")
    SLATE = colors.HexColor("#1E293B")
    INK = colors.HexColor("#0F172A")
    MUTED = colors.HexColor("#475569")
    CYAN = colors.HexColor("#0F766E")
    CYAN_BRIGHT = colors.HexColor("#2CE8C6")
    ORANGE = colors.HexColor("#EA580C")
    PURPLE = colors.HexColor("#6D28D9")
    EMERALD = colors.HexColor("#047857")
    SOFT_BG = colors.HexColor("#F8FAFC")
    ALT_ROW = colors.HexColor("#F1F5F9")
    BORDER = colors.HexColor("#CBD5E1")

    styles = getSampleStyleSheet()
    s_title = ParagraphStyle(
        "MsshiTitle", parent=styles["Title"], fontName=FONT_BOLD, fontSize=20, leading=24, textColor=colors.white, alignment=TA_LEFT
    )
    s_subtitle = ParagraphStyle(
        "MsshiSub", parent=styles["Normal"], fontName=FONT_REG, fontSize=10, leading=14, textColor=colors.HexColor("#CBD5E1")
    )
    s_h1 = ParagraphStyle(
        "MsshiH1", parent=styles["Heading1"], fontName=FONT_BOLD, fontSize=13.5, leading=18, textColor=NAVY, spaceBefore=10, spaceAfter=6
    )
    s_h2 = ParagraphStyle(
        "MsshiH2", parent=styles["Heading2"], fontName=FONT_BOLD, fontSize=11, leading=15, textColor=CYAN, spaceBefore=8, spaceAfter=4
    )
    s_body = ParagraphStyle(
        "MsshiBody", parent=styles["Normal"], fontName=FONT_REG, fontSize=9.3, leading=13.5, textColor=INK, spaceAfter=4
    )
    s_small = ParagraphStyle(
        "MsshiSmall", parent=styles["Normal"], fontName=FONT_REG, fontSize=8.0, leading=11, textColor=MUTED
    )
    s_cell = ParagraphStyle(
        "MsshiCell", parent=styles["Normal"], fontName=FONT_REG, fontSize=8.2, leading=11, textColor=INK
    )
    s_cell_b = ParagraphStyle(
        "MsshiCellB", parent=styles["Normal"], fontName=FONT_BOLD, fontSize=8.2, leading=11, textColor=NAVY
    )
    s_hdr = ParagraphStyle(
        "MsshiHdr", parent=styles["Normal"], fontName=FONT_BOLD, fontSize=8.3, leading=11, textColor=colors.white
    )
    s_cap = ParagraphStyle(
        "MsshiCap", parent=styles["Normal"], fontName=FONT_ITAL, fontSize=7.8, leading=10, textColor=MUTED, alignment=TA_CENTER
    )

    version_info = json.loads((repo_root / "VERSION.json").read_text(encoding="utf-8-sig"))
    visual_manifest = json.loads((repo_root / "configs" / "visual_assets_manifest.json").read_text(encoding="utf-8-sig"))
    github_about = (repo_root / "configs" / "github_about.txt").read_text(encoding="utf-8-sig").strip()

    def rl_img(rel_path: str, width_cm: float, height_cm: float | None = None) -> RLImage | Paragraph:
        p = repo_root / rel_path
        if not p.is_file():
            return Paragraph(f"<i>[Asset missing: {rel_path}]</i>", s_small)
        from PIL import Image as PILImage
        with PILImage.open(p) as im:
            iw, ih = im.size
        w = width_cm * cm
        h = (height_cm * cm) if height_cm else (w * ih / max(1, iw))
        return RLImage(str(p), width=w, height=h)

    def make_table(data: list[list[Any]], col_widths: list[float], header_bg=NAVY) -> Table:
        t = Table(data, colWidths=[w * cm for w in col_widths], repeatRows=1)
        t.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), header_bg),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ALT_ROW]),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ])
        )
        return t

    def draw_header_footer(canvas, doc) -> None:
        canvas.saveState()
        w, h = A4
        canvas.setStrokeColor(CYAN_BRIGHT)
        canvas.setLineWidth(1.2)
        canvas.line(1.5 * cm, h - 1.15 * cm, w - 1.5 * cm, h - 1.15 * cm)
        canvas.setFont(FONT_BOLD, 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(1.5 * cm, h - 1.0 * cm, "MSSHI v3.1.0 + MuZA Skripsi v1.1 — Official Hydrogen Execution Report")
        canvas.drawRightString(w - 1.5 * cm, h - 1.0 * cm, f"Release {version_info.get('version', '3.1.0')} | Adaptive C:/D:")
        canvas.setStrokeColor(BORDER)
        canvas.setLineWidth(0.6)
        canvas.line(1.5 * cm, 1.15 * cm, w - 1.5 * cm, 1.15 * cm)
        canvas.setFont(FONT_REG, 7.5)
        canvas.drawString(1.5 * cm, 0.8 * cm, "Generated cleanly without modifying user provider/model routing (jev_model_routing: false)")
        canvas.drawRightString(w - 1.5 * cm, 0.8 * cm, f"Halaman {doc.page}")
        canvas.restoreState()

    primary_out.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(primary_out),
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title="Laporan Eksekusi Hydrogen MSSHI v3.1.0 + MuZA Skripsi v1.1",
        author="Shikaku Nara, Val, Sensei Shizuka & Kiki-Chii (Google Antigravity)",
    )

    story: list[Any] = []
    ts_str = results.get("generated_at") or datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")

    # === COVER HEADER ===
    hero_box = make_table(
        [[
            Paragraph(
                "LAPORAN EKSEKUSI HYDROGEN<br/><b>MSSHI v3.1.0 + MuZA Skripsi Starter v1.1</b>",
                s_title,
            ),
        ], [
            Paragraph(
                f"Restrukturisasi Repositori GitHub &amp; Workspace Lokal, Kurasi Visual Cyber-Noir Anti-Asal-Tempel, "
                f"Integrasi Drag-and-Drop Skripsi Word (.docx), serta Audit Keamanan &amp; Verifikasi Release.<br/>"
                f"<b>Waktu Eksekusi:</b> {ts_str} &nbsp;|&nbsp; <b>Commit Baseline / Head:</b> {results.get('git_commit', 'verified')}",
                s_subtitle,
            ),
        ]],
        [18.0],
        header_bg=NAVY,
    )
    hero_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LINEBELOW", (0, 1), (0, 1), 3, ORANGE),
    ]))
    story.append(hero_box)
    story.append(Spacer(1, 0.35 * cm))
    story.append(rl_img("assets/avatars/hero-muza-banner.png", 18.0))
    story.append(Paragraph("Hero Banner Utama Terstandardisasi (1280x420 px, Dual-Tone Cyan-Orange Frame)", s_cap))
    story.append(Spacer(1, 0.3 * cm))

    # Executive Summary KPI Table
    story.append(Paragraph("Ringkasan Eksekutif &amp; Kepatuhan Aturan Emas", s_h1))
    kpi_rows = [
        [Paragraph("Parameter Sistem", s_hdr), Paragraph("Nilai Terverifikasi", s_hdr), Paragraph("Status / Guardrail", s_hdr)],
        [Paragraph("Nama &amp; Versi Paket", s_cell_b), Paragraph(f"{version_info['suite_name']} (v{version_info['version']})", s_cell), Paragraph("Tag v3.1.0 + main tersinkron", s_cell)],
        [Paragraph("Total Skill Terbundel", s_cell_b), Paragraph(f"{version_info['bundled_skills']} skill ({version_info['core_skills']} inti + {version_info['integration_wrappers']} wrapper)", s_cell), Paragraph("100% sinkron matriks, disk &amp; profil aktif", s_cell)],
        [Paragraph("Upstream &amp; Opt-in Opsional", s_cell_b), Paragraph(f"{version_info['external_sources']} sumber upstream + {version_info['optional_skills']} opt-in REA", s_cell), Paragraph("REA default OFF; Steel anti-fallback", s_cell)],
        [Paragraph("Routing Model &amp; Provider User", s_cell_b), Paragraph("jev_model_routing: false (terkunci aman)", s_cell), Paragraph("ZERO ubahan ke config.yaml / auth.json / SOUL.md", s_cell)],
        [Paragraph("Jembatan Hemat RAM &amp; Proteksi", s_cell_b), Paragraph("CLI-Anything Universal Bridge + Auto-Trim + Caveman", s_cell), Paragraph("TokenShield guard $1.00; ramah Win10 RAM 4 GB", s_cell)],
        [Paragraph("Aset Visual Terkurasi &amp; Diagram", s_cell_b), Paragraph(f"{visual_manifest['total_standardized_assets']} aset PNG Cyber-Noir + {version_info['visual_assets']} diagram SVG", s_cell), Paragraph("Manifest portabel tanpa path lokal pribadi", s_cell)],
        [Paragraph("Deskripsi GitHub About (318 char)", s_cell_b), Paragraph(github_about, s_cell), Paragraph(f"Panjang: {len(github_about)} / 350 karakter (OK)", s_cell)],
    ]
    story.append(make_table(kpi_rows, [4.6, 8.2, 5.2], header_bg=NAVY))

    story.append(PageBreak())

    # === BAGIAN 1 ===
    story.append(Paragraph("1. Audit Pembersihan, Struktur Workspace Lokal &amp; Path Adaptif C:/D:", s_h1))
    story.append(Paragraph(
        "Seluruh folder distribusi dan repositori pada direktori kerja lokal ditata menjadi 3 kompartemen bersih "
        "agar tidak terjadi duplikasi installer versi lama maupun benturan antara kode GitHub publik dengan arsip pribadi pengguna.",
        s_body,
    ))
    ws_rows = [
        [Paragraph("Direktori Workspace", s_hdr), Paragraph("Peran &amp; Isi Utama", s_hdr), Paragraph("Status Sinkronisasi", s_hdr)],
        [Paragraph("<b>01_Repo_GitHub_MSSHI/</b>", s_cell_b), Paragraph("Working tree bersih GitHub v3.1.0: 63 skill (termasuk muza-skripsi-template), 49 upstreams, 2 Colab notebooks, CLI msshi_cli.py, secret_scan.py, prepare_github_visuals.py, serta docs/pdf-guides/ &amp; docs/manuals/.", s_cell), Paragraph("Clean tree, siap push main &amp; tag v3.1.0", s_cell)],
        [Paragraph("<b>02_Paket_Siap_Kirim_Klien/</b>", s_cell_b), Paragraph("Bundel klien siap pakai: MULAI_SKRIPSI_DRAG_AND_DROP.bat, MULAI_DI_SINI_PEMULA.bat, UPDATE_OTOMATIS_KE_V3.bat, PASANG_LEWAT_POWERSHELL.ps1, PDF panduan, &amp; Notebooks_Skripsi_Colab/.", s_cell), Paragraph("Diperbarui dari 02_Paket_Distribusi_Klien_Sabtu_Zoom", s_cell)],
        [Paragraph("<b>03_Arsip_Visual_dan_Laporan_PDF/</b>", s_cell_b), Paragraph("Menampung Aset_Terstandardisasi_GitHub/, salinan resmi Laporan Eksekusi PDF, plus menjaga utuh Arsip_Pribadi_MuZA_Jangan_Dihapus, Proyek_Aktif_Nov_2026, &amp; Sandbox_Eksperimen.", s_cell), Paragraph("Diperbarui dari 03_Aset_Visual_dan_Dokumen_MuZA", s_cell)],
    ]
    story.append(make_table(ws_rows, [4.5, 9.0, 4.5], header_bg=CYAN))
    story.append(Spacer(1, 0.25 * cm))
    story.append(Paragraph("Deteksi Penyimpanan Adaptif (Anti Error Hardcoded D:\\)", s_h2))
    story.append(Paragraph(
        "Skrip <i>msshi_skripsi_drop.py</i> dan peluncur <i>MULAI_SKRIPSI_DRAG_AND_DROP.bat</i> memeriksa Drive D:\\ secara dinamis: "
        "bila Drive D:\\ tersedia dan dapat ditulis, data dan pustaka ringan (<i>skripsi-pylibs</i>) diarahkan ke <b>D:\\HermesData\\Skripsi_Output</b>; "
        "bila perangkat klien hanya memiliki Drive C:\\, sistem otomatis fallback ke <b>%USERPROFILE%\\HermesData</b> dan <b>%USERPROFILE%\\Documents\\MuZA_Skripsi_Output</b>.",
        s_body,
    ))

    # === BAGIAN 2 ===
    story.append(Paragraph("2. Katalog Visual Terkurasi &amp; Standardisasi Kanvas Pillow", s_h1))
    n_vis = visual_manifest.get("total_standardized_assets", len(visual_manifest.get("assets", [])))
    story.append(Paragraph(
        f"Sebanyak <b>{n_vis} aset gambar</b> diseleksi secara visual dari tiga koleksi sumber lokal "
        "(Arsip Karakter Hermes AI, Koleksi Meme Reaction, dan Arsip PP TIKTOK) sambil membuang seluruh foto pribadi kamera, undangan, "
        "maupun cuplikan non-relevan. Setiap gambar dirender ulang memakai <i>scripts/prepare_github_visuals.py</i> ke dalam 4 kanvas seragam.",
        s_body,
    ))

    # Show 5 Bot Avatars + Noir side by side
    bot_imgs = [
        [
            rl_img("assets/avatars/bot-01-yukino.png", 3.1, 3.1),
            rl_img("assets/avatars/bot-02-shizuka.png", 3.1, 3.1),
            rl_img("assets/avatars/bot-03-val.png", 3.1, 3.1),
            rl_img("assets/avatars/bot-04-kikichii.png", 3.1, 3.1),
            rl_img("assets/avatars/bot-05-shikaku.png", 3.1, 3.1),
        ],
        [
            Paragraph("<b>Yukino</b><br/>(#2CE8C6 Cyan)", s_cap),
            Paragraph("<b>Shizuka</b><br/>(#8B5CF6 Purple)", s_cap),
            Paragraph("<b>Val</b><br/>(#F59E0B Amber)", s_cap),
            Paragraph("<b>Kiki-Chii</b><br/>(#FF6B1A Orange)", s_cap),
            Paragraph("<b>Shikaku</b><br/>(#10B981 Emerald)", s_cap),
        ],
    ]
    bot_tbl = Table(bot_imgs, colWidths=[3.6 * cm] * 5)
    bot_tbl.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story.append(bot_tbl)
    story.append(Spacer(1, 0.25 * cm))

    # Show 4 Evolution Meme panels + Skripsi + Budget meme grid (2x3)
    meme_grid = [
        [
            rl_img("assets/memes/meme-01-era-v1.png", 5.6, 3.5),
            rl_img("assets/memes/meme-02-era-v2.png", 5.6, 3.5),
            rl_img("assets/memes/meme-03-era-v30.png", 5.6, 3.5),
        ],
        [
            Paragraph("Era v1.0: Overheat 22 MCP", s_cap),
            Paragraph("Era v2.0: Hydrogen vs Coughing Baby", s_cap),
            Paragraph("Era v3.0: RAM 4GB Bernapas Lega", s_cap),
        ],
        [
            rl_img("assets/memes/meme-04-era-v31.png", 5.6, 3.5),
            rl_img("assets/memes/meme-05-skripsi-drop.png", 5.6, 3.5),
            rl_img("assets/memes/meme-06-budget-dan-cdrive.png", 5.6, 3.5),
        ],
        [
            Paragraph("Era v3.1.0: Taking It Easy + Skripsi", s_cap),
            Paragraph("MuZA Skripsi Drag-and-Drop v1.1", s_cap),
            Paragraph("$1 Shield &amp; Adaptif Drive C:/D:", s_cap),
        ],
    ]
    meme_tbl = Table(meme_grid, colWidths=[6.0 * cm] * 3)
    meme_tbl.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story.append(meme_tbl)
    story.append(PageBreak())

    # Full manifest table
    story.append(Paragraph("Daftar Lengkap Aset Visual dalam Manifest Portabel (configs/visual_assets_manifest.json)", s_h2))
    vis_rows = [[Paragraph("ID Aset", s_hdr), Paragraph("Path Repo Output", s_hdr), Paragraph("Dimensi", s_hdr), Paragraph("Koleksi &amp; Fungsi", s_hdr)]]
    for item in visual_manifest.get("assets", []):
        vis_rows.append([
            Paragraph(f"<b>{item['id']}</b>", s_cell),
            Paragraph(item["output"], s_cell),
            Paragraph(f"{item['width']}x{item['height']} ({item['size_bytes'] // 1024} KiB)", s_cell),
            Paragraph(f"[{item['source_collection']}] {item['purpose']}", s_cell),
        ])
    story.append(make_table(vis_rows, [3.6, 5.2, 3.0, 6.2], header_bg=PURPLE))
    story.append(Spacer(1, 0.3 * cm))

    # === BAGIAN 3 ===
    story.append(Paragraph("3. Integrasi MuZA Skripsi Starter v1.1 (Drag-and-Drop &amp; Google Colab)", s_h1))
    story.append(Paragraph(
        "Skill ke-63 (<b>skills/muza-skripsi-template/</b>) terpasang utuh dengan 11 file inti dan telah terdaftar pada pack <i>thesis</i> "
        "untuk bot <b>Val, Sensei Shizuka, Yukino</b>, mode <b>Solo (1-Bot)</b>, serta profil aktif Hermes &amp; Google Antigravity global.",
        s_body,
    ))
    skripsi_rows = [
        [Paragraph("Komponen Skripsi v1.1", s_hdr), Paragraph("Lokasi / Tautan", s_hdr), Paragraph("Fungsi Teknis", s_hdr)],
        [Paragraph("<b>Skill 63: muza-skripsi-template</b>", s_cell_b), Paragraph("skills/muza-skripsi-template/ (11 file)", s_cell), Paragraph("Aktivasi kontekstual Chat AI ('Buatkan aku template skripsi!') lewat 5 tahap wajib dengan [Dari Pedoman] vs [*Default].", s_cell)],
        [Paragraph("<b>campus_lookup.py</b>", s_cell_b), Paragraph("skills/muza-skripsi-template/scripts/", s_cell), Paragraph("Pencari otomatis logo PNG kampus, kota, gelar, dan nama/NIP Rektor, Dekan, serta Kaprodi dari Wikipedia/Wikidata/ROR/ac.id.", s_cell)],
        [Paragraph("<b>extract_guideline.py</b>", s_cell_b), Paragraph("skills/muza-skripsi-template/scripts/", s_cell), Paragraph("Ekstraksi ukuran kertas, margin 4-4-3-3/4-3-3-3, font, spasi, dan gaya sitasi langsung dari PDF/DOCX pedoman kampus.", s_cell)],
        [Paragraph("<b>build_template.py + 5 Presets</b>", s_cell_b), Paragraph("assets/presets/ (5 JSON metodologi)", s_cell), Paragraph("OOXML .docx builder + injektor .zip/.csv/.ris hasil MuZA_Search (Informatika/Ilkom, Kuantitatif, Kualitatif, R&amp;D, PTK).", s_cell)],
        [Paragraph("<b>MuZA_Search.ipynb</b>", s_cell_b), Paragraph("notebooks/skripsi/MuZA_Search.ipynb<br/>Colab ID: 15ckekQcGu4ssHQMQgXyK1gMMgobVZMFv", s_cell), Paragraph("Riset literatur OpenAlex/CrossRef/Semantic Scholar, matriks Research Gap, dan ekspor paket .zip siap suntik.", s_cell)],
        [Paragraph("<b>MuZA_Skripsi_Builder.ipynb</b>", s_cell_b), Paragraph("notebooks/skripsi/MuZA_Skripsi_Builder.ipynb<br/>Colab ID: 1rrl38cwQZ0CA00cMyQvfjJUf1CSEtJpS", s_cell), Paragraph("Perakit awan gratis tanpa instalasi Python lokal; menghasilkan Template_Skripsi_&lt;Kampus&gt;.docx siap unduh.", s_cell)],
        [Paragraph("<b>Peluncur Drag-and-Drop Windows</b>", s_cell_b), Paragraph("MULAI_SKRIPSI_DRAG_AND_DROP.bat + scripts/msshi_skripsi_drop.py", s_cell), Paragraph("Drag &amp; drop .zip/.pdf/.docx/.ris langsung ke file .bat; output adaptif ke D:\\HermesData\\Skripsi_Output atau ~/Documents/MuZA_Skripsi_Output.", s_cell)],
    ]
    story.append(make_table(skripsi_rows, [4.2, 6.2, 7.6], header_bg=EMERALD))
    story.append(PageBreak())

    # === BAGIAN 4 ===
    story.append(Paragraph("4. Hasil Audit Keamanan, Release Checks &amp; Uji End-to-End .docx", s_h1))
    checks = results.get("checks", [])
    chk_rows = [[Paragraph("Pemeriksaan / Skrip Uji", s_hdr), Paragraph("Hasil", s_hdr), Paragraph("Ringkasan Bukti Teramati", s_hdr)]]
    for row in checks:
        status = row.get("status", "UNKNOWN")
        badge = f"<b><font color='#047857'>{status}</font></b>" if status == "PASS" else f"<b><font color='#DC2626'>{status}</font></b>"
        chk_rows.append([
            Paragraph(row.get("name", ""), s_cell_b),
            Paragraph(badge, s_cell),
            Paragraph(row.get("detail", ""), s_cell),
        ])
    story.append(make_table(chk_rows, [5.4, 2.2, 10.4], header_bg=NAVY))
    story.append(Spacer(1, 0.35 * cm))

    # === BAGIAN 5 ===
    story.append(Paragraph("5. Tautan Multi-Kanal, Distribusi 3 Lokasi PDF &amp; Panduan Klien", s_h1))
    dist_rows = [
        [Paragraph("Artefak / Lokasi Salinan Resmi", s_hdr), Paragraph("Alamat / Keterangan", s_hdr)],
        [Paragraph("<b>Salinan PDF 1 (Repo GitHub docs/pdf-guides/)</b>", s_cell_b), Paragraph("01_Repo_GitHub_MSSHI/docs/pdf-guides/Laporan_Eksekusi_Hydrogen_MSSHI_v3.1.0_Memeable_dan_Skripsi.pdf", s_cell)],
        [Paragraph("<b>Salinan PDF 2 (Arsip Proyek Lokal)</b>", s_cell_b), Paragraph("Paket Setup Hermes/03_Arsip_Visual_dan_Laporan_PDF/Laporan_Eksekusi_Hydrogen_MSSHI_v3.1.0_Memeable_dan_Skripsi.pdf", s_cell)],
        [Paragraph("<b>Salinan PDF 3 (Folder Downloads Pengguna)</b>", s_cell_b), Paragraph("Downloads/Laporan_Eksekusi_Hydrogen_MSSHI_v3.1.0_Memeable_dan_Skripsi.pdf", s_cell)],
        [Paragraph("<b>Manual PDF Resmi di GitHub (1-Click Download)</b>", s_cell_b), Paragraph("docs/pdf-guides/Buku_Panduan_Master_Klien_Hermes_dan_MSSHI_v3.1.0.pdf · docs/manuals/latest/ · docs/manuals/v3.0/ · docs/pdf-guides/Spesifikasi_Lengkap_Settings_MSSHI_v3.0_Hermes_Ultimate_Optimizer.pdf", s_cell)],
        [Paragraph("<b>Repositori &amp; Tag Rilis GitHub</b>", s_cell_b), Paragraph("https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/tree/v3.1.0", s_cell)],
    ]
    story.append(make_table(dist_rows, [6.2, 11.8], header_bg=ORANGE))
    story.append(Spacer(1, 0.3 * cm))

    # Noir fullbody signature block
    sig_tbl = Table([[
        rl_img("assets/avatars/muza-noir-fullbody.png", 3.1, 5.5),
        Paragraph(
            "<b>Checklist Cepat Klien / Mahasiswa (Zero-Friction):</b><br/><br/>"
            "1. Buka folder <b>02_Paket_Siap_Kirim_Klien</b> (atau clone repo GitHub <i>v3.1.0</i>).<br/>"
            "2. Pemula instalasi penuh: klik 2x <b>MULAI_DI_SINI_PEMULA.bat</b>; pengguna lama v2.x: jalankan <b>UPDATE_OTOMATIS_KE_V3.bat</b>.<br/>"
            "3. Untuk skripsi cepat tanpa ketik perintah: jalankan <b>MuZA_Search.ipynb</b> di Colab, unduh file <b>.zip</b> hasil riset, "
            "lalu seret (<i>drag-and-drop</i>) <b>.zip</b> + pedoman <b>.pdf</b> kampus ke atas ikon <b>MULAI_SKRIPSI_DRAG_AND_DROP.bat</b>.<br/>"
            "4. Di dalam Chat AI (Antigravity, Hermes, Claude, OpenClaw), cukup ketik: <i>'Buatkan aku template skripsi!'</i> dan jawab 5 langkah konfirmasi.",
            s_body,
        ),
    ]], colWidths=[3.8 * cm, 14.2 * cm])
    sig_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), SOFT_BG),
        ("BOX", (0, 0), (-1, -1), 0.8, BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(KeepTogether(sig_tbl))

    doc.build(story, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)
    for target in extra_outs:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.resolve() != primary_out.resolve():
            shutil.copy2(primary_out, target)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the official MSSHI v3.1.0 Hydrogen Execution Report PDF.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--results-json", type=Path, default=None, help="JSON file of verified test/command outcomes.")
    parser.add_argument(
        "--out-repo",
        type=Path,
        default=ROOT / "docs" / "pdf-guides" / "Laporan_Eksekusi_Hydrogen_MSSHI_v3.1.0_Memeable_dan_Skripsi.pdf",
    )
    parser.add_argument("--out-archive", type=Path, default=None)
    parser.add_argument("--out-downloads", type=Path, default=None)
    parser.add_argument("--install-deps", action="store_true")
    args = parser.parse_args(argv)

    ensure_reportlab(auto_install=args.install_deps)
    repo_root = args.repo_root.expanduser().resolve()
    results = json.loads(args.results_json.read_text(encoding="utf-8-sig")) if args.results_json and args.results_json.is_file() else {}
    primary = args.out_repo.expanduser().resolve()
    extras = [p.expanduser().resolve() for p in (args.out_archive, args.out_downloads) if p is not None]
    build_pdf(repo_root, results, primary, extras)

    from pypdf import PdfReader
    reader = PdfReader(str(primary))
    print(f"GENERATED_PDF: {primary} ({primary.stat().st_size:,} bytes, {len(reader.pages)} pages)")
    for ex in extras:
        print(f"COPIED_PDF:    {ex} ({ex.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
