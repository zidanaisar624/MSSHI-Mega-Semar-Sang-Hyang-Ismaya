#!/usr/bin/env python3
"""
MuZA_Skripsi_Template v1.0 — Thesis & Skripsi Word (.docx) Builder (MuZA Project).

Turns a JSON spec (extracted from a campus thesis guideline, optionally merged
with a methodology preset and MuZA_Search v1.0 research outputs) into a
finished-looking .docx template with:
  - Redesigned tutorial & cheat-sheet guide page
  - Indonesian academic Three-Line (booktabs) tables with repeat headers
  - Automatic hanging indent & optional tiered sub-heading indentation
  - Blockquote ('Kutipan Langsung') & centered Equation ('Rumus') styles/blocks
  - Live Word SEQ captions + auto-filled Daftar Isi/Tabel/Gambar/Lampiran
    (via LibreOffice render OR Analytical Fallback Page Estimator)
  - Direct injection of MuZA_Search v1.0 Bab 2 synthesis tables & APA/IEEE references

Usage:
    python build_template.py spec.json Output.docx [--muza-zip file.zip] [--preset informatika_ilkom] [--logo logo.png]
"""
import argparse
import copy
import csv
import datetime
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

for _pylibs_cand in (
    os.path.join(os.path.expanduser("~"), "HermesData", "skripsi-pylibs"),
    r"D:\HermesData\skripsi-pylibs",
):
    if os.path.isdir(_pylibs_cand) and _pylibs_cand not in sys.path:
        sys.path.insert(0, _pylibs_cand)

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ALIGN = {
    "left": WD_ALIGN_PARAGRAPH.LEFT,
    "center": WD_ALIGN_PARAGRAPH.CENTER,
    "right": WD_ALIGN_PARAGRAPH.RIGHT,
    "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
}
PAPER = {
    "A4": (21.0, 29.7),
    "LETTER": (21.59, 27.94),
    "KUARTO": (21.5, 28.0),
    "F4": (21.5, 33.0),
    "FOLIO": (21.5, 33.0),
}
GREY = RGBColor(0x80, 0x80, 0x80)
BLACK = RGBColor(0, 0, 0)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRESETS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "assets", "presets")

DEFAULT_PLACEHOLDERS = [
    {"key": "title", "sample": "JUDUL SKRIPSI DITULIS DI SINI MENGGUNAKAN HURUF KAPITAL", "label": "Judul skripsi"},
    {"key": "name", "sample": "NAMA LENGKAP MAHASISWA", "label": "Nama lengkap mahasiswa (isi sendiri setelah unduh template)"},
    {"key": "nim", "sample": "0000000000", "label": "NIM mahasiswa (isi sendiri setelah unduh template)"},
    {"key": "supervisor1", "sample": "Nama Pembimbing I, Gelar", "label": "Nama pembimbing I"},
    {"key": "id1", "sample": "0000000001", "label": "NIDN/NIP pembimbing I"},
    {"key": "supervisor2", "sample": "Nama Pembimbing II, Gelar", "label": "Nama pembimbing II"},
    {"key": "id2", "sample": "0000000002", "label": "NIDN/NIP pembimbing II"},
    {"key": "dean", "sample": "Nama Dekan Fakultas, Gelar", "label": "Nama Dekan fakultas"},
    {"key": "id_dean", "sample": "0000000000", "label": "NIP / NIDN Dekan"},
    {"key": "head_program", "sample": "Nama Ketua Program Studi, Gelar", "label": "Nama Ketua Program Studi / Kaprodi"},
    {"key": "id_head", "sample": "0000000004", "label": "NIP / NIDN Ketua Program Studi"},
    {"key": "rector", "sample": "Nama Rektor Perguruan Tinggi, Gelar", "label": "Nama Rektor / Pimpinan Perguruan Tinggi"},
    {"key": "id_rector", "sample": "0000000003", "label": "NIP / NIDN Rektor"},
    {"key": "degree", "sample": "Sarjana (S1)", "label": "Gelar lulusan sesuai SK Prodi"},
    {"key": "ministry", "sample": "KEMENTERIAN PENDIDIKAN TINGGI, SAINS, DAN TEKNOLOGI", "label": "Kementerian / Yayasan menaungi"},
    {"key": "city", "sample": "Kota", "label": "Kota kampus"},
    {"key": "date", "sample": "Tanggal Bulan Tahun", "label": "Tanggal penandatanganan"},
    {"key": "year", "sample": str(datetime.date.today().year), "label": "Tahun lulus/pengajuan"},
]

SAMPLE_SENTENCES = (
    "Paragraf ini adalah contoh isi bagian {topic}. Formatnya sudah mengikuti pedoman kampus, mulai dari "
    "jenis dan ukuran huruf, spasi antarbaris, rata kanan-kiri, hingga menjorok pada baris pertama. Hapus "
    "paragraf contoh ini, lalu ketik tulisanmu sendiri di tempat yang sama agar tata letak tetap rapi."
)


def warn(msg):
    print("WARNING:", msg, file=sys.stderr)


def find_soffice():
    """Find LibreOffice binary across Windows, macOS, and Linux."""
    found = shutil.which("soffice") or shutil.which("libreoffice")
    if found:
        return found
    for candidate in (
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\LibreOffice\program\soffice.exe"),
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/usr/bin/soffice",
        "/usr/local/bin/soffice",
    ):
        if candidate and os.path.exists(candidate):
            return candidate
    return None


def _pick_system_font(bold=True):
    """Find a readable TTF font across Windows, macOS, and Linux."""
    candidates = (
        [
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\segoeuib.ttf",
            r"C:\Windows\Fonts\calibrib.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
        if bold else [
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\calibri.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]
    )
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


# --------------------------------------------------------------------------- low-level OOXML helpers

def set_rfonts(rpr, name):
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if rfonts.get(qn(attr)) is not None:
            del rfonts.attrib[qn(attr)]
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), name)


def set_lang(rpr, lang):
    el = rpr.find(qn("w:lang"))
    if el is None:
        el = OxmlElement("w:lang")
        rpr.append(el)
    el.set(qn("w:val"), lang)


def set_outline(style, level):
    ppr = style.element.get_or_add_pPr()
    for el in ppr.findall(qn("w:outlineLvl")):
        ppr.remove(el)
    if level is not None:
        el = OxmlElement("w:outlineLvl")
        el.set(qn("w:val"), str(level))
        ppr.append(el)


def fld_run(p, kind, dirty=False):
    r = p.add_run()
    e = OxmlElement("w:fldChar")
    e.set(qn("w:fldCharType"), kind)
    if dirty and kind == "begin":
        e.set(qn("w:dirty"), "true")
    r._r.append(e)
    return r


def instr_run(p, instr):
    r = p.add_run()
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = " %s " % instr
    r._r.append(it)
    return r


def add_field(p, instr, placeholder="", dirty=False):
    fld_run(p, "begin", dirty)
    instr_run(p, instr)
    fld_run(p, "separate")
    p.add_run(placeholder)
    fld_run(p, "end")


def _insert_before(parent, el, successor_tags):
    for child in parent:
        if child.tag in successor_tags:
            child.addprevious(el)
            return
    parent.append(el)


def _set_cell_margins(table, top=60, bottom=60, left=100, right=100):
    tbl_pr = table._tbl.tblPr
    for old in tbl_pr.findall(qn("w:tblCellMar")):
        tbl_pr.remove(old)
    cmar = OxmlElement("w:tblCellMar")
    for side, val in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        node = OxmlElement("w:" + side)
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        cmar.append(node)
    succ = {qn(t) for t in ("w:tblLook", "w:tblCaption", "w:tblDescription")}
    _insert_before(tbl_pr, cmar, succ)


def _set_cell_borders(cell, top=None, bottom=None, left=None, right=None):
    tcpr = cell._tc.get_or_add_tcPr()
    for old in tcpr.findall(qn("w:tcBorders")):
        tcpr.remove(old)
    borders = OxmlElement("w:tcBorders")
    for side, cfg in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        if cfg is None:
            continue
        e = OxmlElement("w:" + side)
        e.set(qn("w:val"), cfg.get("val", "nil"))
        if cfg.get("val", "nil") != "nil":
            e.set(qn("w:sz"), str(cfg.get("sz", 4)))
            e.set(qn("w:space"), "0")
            e.set(qn("w:color"), cfg.get("color", "000000"))
        borders.append(e)
    succ = {qn(t) for t in ("w:shd", "w:noWrap", "w:tcMar", "w:textDirection", "w:tcFitText", "w:vAlign")}
    _insert_before(tcpr, borders, succ)


def table_borders(table, mode="three_line", header=True):
    """Apply 'three_line' (booktabs), 'grid', or 'none' borders + OOXML repeat header."""
    if mode is True:
        mode = "grid"
    elif mode is False or mode is None:
        mode = "none"
    mode = str(mode).lower()

    tbl_pr = table._tbl.tblPr
    for old in tbl_pr.findall(qn("w:tblBorders")):
        tbl_pr.remove(old)

    borders = OxmlElement("w:tblBorders")
    if mode == "grid":
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            e = OxmlElement("w:" + edge)
            e.set(qn("w:val"), "single")
            e.set(qn("w:sz"), "4")
            e.set(qn("w:space"), "0")
            e.set(qn("w:color"), "000000")
            borders.append(e)
    elif mode == "three_line":
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            e = OxmlElement("w:" + edge)
            if edge in ("top", "bottom"):
                e.set(qn("w:val"), "single")
                e.set(qn("w:sz"), "8")
                e.set(qn("w:space"), "0")
                e.set(qn("w:color"), "000000")
            else:
                e.set(qn("w:val"), "nil")
            borders.append(e)
    else:
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            e = OxmlElement("w:" + edge)
            e.set(qn("w:val"), "nil")
            borders.append(e)

    succ = {qn(t) for t in ("w:shd", "w:tblLayout", "w:tblCellMar", "w:tblLook", "w:tblCaption", "w:tblDescription")}
    _insert_before(tbl_pr, borders, succ)
    if mode in ("three_line", "grid"):
        _set_cell_margins(table, top=60, bottom=60, left=100, right=100)

    for idx, row in enumerate(table.rows):
        trpr = row._tr.get_or_add_trPr()
        if not trpr.findall(qn("w:cantSplit")):
            trpr.append(OxmlElement("w:cantSplit"))
        if header and idx == 0:
            if not trpr.findall(qn("w:tblHeader")):
                trpr.append(OxmlElement("w:tblHeader"))
            if mode == "three_line":
                for cell in row.cells:
                    _set_cell_borders(
                        cell,
                        top={"val": "single", "sz": 8},
                        bottom={"val": "single", "sz": 6},
                        left={"val": "nil"},
                        right={"val": "nil"},
                    )


def set_widths(table, widths_cm):
    table.autofit = False
    grid = table._tbl.tblGrid
    for i, gc in enumerate(grid.findall(qn("w:gridCol"))):
        if i < len(widths_cm):
            gc.set(qn("w:w"), str(int(widths_cm[i] * 567)))
    for row in table.rows:
        for i, cell in enumerate(row.cells):
            if i < len(widths_cm):
                cell.width = Cm(widths_cm[i])


def shade_cell(cell, hex_fill):
    tcpr = cell._tc.get_or_add_tcPr()
    for old in tcpr.findall(qn("w:shd")):
        tcpr.remove(old)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    succ = {qn(t) for t in ("w:noWrap", "w:tcMar", "w:textDirection", "w:tcFitText", "w:vAlign")}
    _insert_before(tcpr, shd, succ)


def roman(n, upper=False):
    vals = [
        (1000, "m"), (900, "cm"), (500, "d"), (400, "cd"),
        (100, "c"), (90, "xc"), (50, "l"), (40, "xl"),
        (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i"),
    ]
    out = ""
    for v, s in vals:
        while n >= v:
            out += s
            n -= v
    return out.upper() if upper else out


def make_logo_placeholder(path, label="LOGO\nKAMPUS"):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return False
    size = 800
    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([24, 24, size - 24, size - 24], fill=(244, 244, 248, 255), outline=(140, 140, 160, 255), width=14)
    font_path = _pick_system_font(bold=True)
    if font_path:
        font = ImageFont.truetype(font_path, 96)
        small = ImageFont.truetype(_pick_system_font(bold=False) or font_path, 40)
    else:
        font = small = ImageFont.load_default()
    bbox = d.multiline_textbbox((0, 0), label, font=font, align="center", spacing=18)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.multiline_text(((size - w) / 2, (size - h) / 2 - 42), label, font=font, fill=(95, 95, 115, 255), align="center", spacing=18)
    hint = "klik kanan > Ubah Gambar"
    bb = d.textbbox((0, 0), hint, font=small)
    d.text(((size - (bb[2] - bb[0])) / 2, size / 2 + h / 2 + 8), hint, font=small, fill=(135, 135, 150, 255))
    img.save(path)
    return True


def make_figure_placeholder(path):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return False
    if os.path.exists(path):
        return True
    img = Image.new("RGB", (1200, 700), (245, 246, 250))
    d = ImageDraw.Draw(img)
    d.rectangle([8, 8, 1191, 691], outline=(165, 170, 185), width=8)
    font_path = _pick_system_font(bold=False)
    font = ImageFont.truetype(font_path, 52) if font_path else ImageFont.load_default()
    text = "Contoh Gambar Penelitian\nklik kanan > Ubah Gambar / Change Picture"
    bb = d.multiline_textbbox((0, 0), text, font=font, align="center", spacing=20)
    d.multiline_text(((1200 - (bb[2] - bb[0])) / 2, (700 - (bb[3] - bb[1])) / 2), text, font=font, fill=(115, 120, 135), align="center", spacing=20)
    img.save(path)
    return True


# --------------------------------------------------------------------------- MuZA_Search v1.0 integration helpers

def _strip_tags_clean(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()


def parse_ris_text(ris_text):
    """Parse RIS bibliographic text into structured dicts."""
    records = []
    cur = {"authors": [], "keywords": []}
    last_tag = None
    for raw_line in str(ris_text or "").splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        m = re.match(r"^([A-Z0-9]{2})\s{1,2}-\s?(.*)$", line)
        if m:
            tag, val = m.group(1), m.group(2).strip()
            last_tag = tag
            if tag == "TY":
                if cur.get("title") or cur.get("authors"):
                    records.append(cur)
                cur = {"type": val, "authors": [], "keywords": []}
            elif tag == "ER":
                if cur.get("title") or cur.get("authors"):
                    records.append(cur)
                cur = {"authors": [], "keywords": []}
                last_tag = None
            elif tag in ("AU", "A1"):
                cur["authors"].append(val)
            elif tag in ("TI", "T1"):
                cur["title"] = val
            elif tag in ("PY", "Y1"):
                ym = re.search(r"\d{4}", val)
                if ym:
                    cur["year"] = ym.group(0)
            elif tag in ("T2", "JO", "JF", "BT"):
                cur.setdefault("journal", val)
            elif tag == "PB":
                cur["publisher"] = val
            elif tag == "VL":
                cur["volume"] = val
            elif tag in ("IS", "M1"):
                cur.setdefault("issue", val)
            elif tag == "SP":
                cur["sp"] = val
            elif tag == "EP":
                cur["ep"] = val
            elif tag == "DO":
                cur["doi"] = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", val, flags=re.I)
            elif tag == "UR":
                cur["url"] = val
            elif tag == "KW":
                cur["keywords"].append(val)
        elif last_tag and last_tag in ("TI", "T1", "T2"):
            key = "title" if last_tag in ("TI", "T1") else "journal"
            cur[key] = (cur.get(key, "") + " " + line.strip()).strip()
    if cur.get("title") or cur.get("authors"):
        records.append(cur)
    return records


def _fmt_author_apa(raw_name):
    raw_name = _strip_tags_clean(raw_name)
    if not raw_name:
        return "Anonim"
    if "," in raw_name:
        last, rest = [x.strip() for x in raw_name.split(",", 1)]
        initials = " ".join(f"{w[0].upper()}." for w in rest.split() if w)
        return f"{last}, {initials}".strip() if initials else last
    parts = raw_name.split()
    if len(parts) == 1:
        return parts[0]
    initials = " ".join(f"{w[0].upper()}." for w in parts[:-1] if w)
    return f"{parts[-1]}, {initials}"


def _fmt_author_ieee(raw_name):
    raw_name = _strip_tags_clean(raw_name)
    if not raw_name:
        return "Anonim"
    if "," in raw_name:
        last, rest = [x.strip() for x in raw_name.split(",", 1)]
        initials = " ".join(f"{w[0].upper()}." for w in rest.split() if w)
        return f"{initials} {last}".strip()
    parts = raw_name.split()
    if len(parts) == 1:
        return parts[0]
    initials = " ".join(f"{w[0].upper()}." for w in parts[:-1] if w)
    return f"{initials} {parts[-1]}"


def _citation_sort_key(rec):
    first = rec["authors"][0] if rec.get("authors") else rec.get("title", "zzz")
    return (_strip_tags_clean(first).lower(), str(rec.get("year") or "9999"), str(rec.get("title") or "").lower())


def format_reference_segments(rec, style_name="APA 7th", index=1):
    """Return list of (text, italic_bool) segments for a bibliographic entry."""
    style_low = (style_name or "APA").lower()
    authors = rec.get("authors") or []
    year = rec.get("year") or "n.d."
    title = _strip_tags_clean(rec.get("title") or "Untitled")
    if title and not title.endswith((".", "?", "!")):
        title_dot = title + "."
    else:
        title_dot = title
    journal = _strip_tags_clean(rec.get("journal") or rec.get("publisher") or "")
    vol = _strip_tags_clean(rec.get("volume"))
    issue = _strip_tags_clean(rec.get("issue"))
    sp, ep = _strip_tags_clean(rec.get("sp")), _strip_tags_clean(rec.get("ep"))
    pages = f"{sp}–{ep}" if (sp and ep and sp != ep) else (sp or ep)
    doi = _strip_tags_clean(rec.get("doi"))
    link = f"https://doi.org/{doi}" if doi else _strip_tags_clean(rec.get("url"))

    if "ieee" in style_low:
        if not authors:
            au_str = "Anonim"
        elif len(authors) == 1:
            au_str = _fmt_author_ieee(authors[0])
        elif len(authors) <= 6:
            f_a = [_fmt_author_ieee(a) for a in authors]
            au_str = ", ".join(f_a[:-1]) + ", and " + f_a[-1]
        else:
            au_str = f"{_fmt_author_ieee(authors[0])} et al."
        segs = [(f"[{index}] {au_str}, \"{title},\" ", False)]
        if journal:
            segs.append((journal, True))
        tail = []
        if vol:
            tail.append(f"vol. {vol}")
        if issue:
            tail.append(f"no. {issue}")
        if pages:
            tail.append(f"pp. {pages}")
        tail.append(year)
        if tail:
            segs.append((", " + ", ".join(tail) + ".", False))
        else:
            segs.append((".", False))
        if doi:
            segs.append((f" doi: {doi}.", False))
        elif link:
            segs.append((f" [Online]. Available: {link}", False))
        return segs

    if "harvard" in style_low:
        if not authors:
            au_str = "Anonim"
        elif len(authors) == 1:
            au_str = _fmt_author_apa(authors[0])
        elif len(authors) == 2:
            au_str = f"{_fmt_author_apa(authors[0])} and {_fmt_author_apa(authors[1])}"
        else:
            au_str = f"{_fmt_author_apa(authors[0])} et al."
        segs = [(f"{au_str} ({year}) '{title}', ", False)]
        if journal:
            segs.append((journal, True))
        extra = ""
        if vol and issue:
            extra = f", {vol}({issue})"
        elif vol:
            extra = f", {vol}"
        if pages:
            extra += f", pp. {pages}"
        segs.append((extra + ".", False))
        if link:
            segs.append((f" Available at: {link}.", False))
        return segs

    # Default: APA 7th Edition
    apa_authors = [_fmt_author_apa(a) for a in authors[:20]]
    if not apa_authors:
        au_str = "Anonim"
    elif len(apa_authors) == 1:
        au_str = apa_authors[0]
    elif len(apa_authors) <= 20:
        au_str = ", ".join(apa_authors[:-1]) + ", & " + apa_authors[-1]
    else:
        au_str = ", ".join(apa_authors[:19]) + ", … " + _fmt_author_apa(authors[-1])
    if not au_str.endswith("."):
        au_str += "."
    segs = [(f"{au_str} ({year}). {title_dot} ", False)]
    if journal:
        segs.append((journal, True))
        if vol:
            segs.append((", ", False))
            segs.append((vol, True))
            if issue:
                segs.append((f"({issue})", False))
        if pages:
            segs.append((f", {pages}", False))
        segs.append((".", False))
    elif rec.get("publisher"):
        segs.append((f"{_strip_tags_clean(rec['publisher'])}.", False))
    if link:
        segs.append((f" {link}", False))
    return segs


def _read_bab2_csv_bytes(raw_bytes):
    text = raw_bytes.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for row in reader:
        if any(str(v or "").strip() for v in row.values()):
            rows.append(row)
    return rows


def _read_bab2_xlsx_bytes(raw_bytes):
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(raw_bytes), data_only=True)
    ws = wb.active
    all_rows = list(ws.iter_rows(values_only=True))
    header_idx = None
    for idx, r in enumerate(all_rows):
        joined = " ".join(str(c or "") for c in r).lower()
        if "penulis" in joined and ("judul" in joined or "metode" in joined):
            header_idx = idx
            break
    if header_idx is None:
        return []
    headers = [str(c or "").strip() for c in all_rows[header_idx]]
    out = []
    for r in all_rows[header_idx + 1:]:
        if not any(c is not None and str(c).strip() for c in r):
            continue
        item = {headers[i]: (str(r[i]).strip() if i < len(r) and r[i] is not None else "") for i in range(len(headers)) if headers[i]}
        out.append(item)
    return out


def _normalize_bab2_table_rows(raw_rows):
    """Turn parsed CSV/XLSX dicts from MuZA_Search v1.1 into a clean 6-column table."""
    if not raw_rows:
        return None
    header = ["No", "Penulis & Tahun", "Judul & Jurnal", "Metode / Algoritma", "Dataset / Sampel", "Hasil Utama & Metrik"]
    out = [header]
    for idx, r in enumerate(raw_rows, 1):
        penulis = r.get("Penulis & Tahun") or r.get("Penulis") or "-"
        judul = r.get("Judul & Jurnal") or r.get("Judul") or "-"
        metode = (
            r.get("Metode / Algoritma / Pendekatan")
            or r.get("Metode / Algoritma")
            or r.get("Metode (Sintesis Bab 2)")
            or r.get("Metode / Variabel")
            or r.get("Metode")
            or "-"
        )
        dataset = (
            r.get("Dataset / Objek / Sampel")
            or r.get("Dataset/Sampel (Bab 2)")
            or r.get("Gap Penelitian")
            or r.get("Objek / Sampel")
            or "-"
        )
        hasil = (
            r.get("Hasil Utama & Metrik Evaluasi")
            or r.get("Hasil Utama (Bab 2)")
            or r.get("Hasil Utama")
            or "-"
        )
        if len(hasil) > 220:
            hasil = hasil[:217].rstrip() + "…"
        if len(judul) > 140:
            judul = judul[:137].rstrip() + "…"
        out.append([str(idx), str(penulis), str(judul), str(metode), str(dataset), str(hasil)])
    return out


def load_muza_search_data(zip_path=None, bab2_path=None, ris_path=None):
    """Load Bab 2 synthesis rows and RIS bibliographic entries from MuZA_Search v1.1 outputs."""
    bab2_raw = []
    ris_records = []

    if zip_path and os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = [n for n in zf.namelist() if not n.endswith("/")]
            csv_name = (
                next((n for n in names if n.endswith("02_TABEL_PENELITIAN_TERDAHULU_BAB2.csv")), None)
                or next((n for n in names if n.lower().endswith(".csv") and any(k in os.path.basename(n).lower() for k in ("bab2", "penelitian", "sintesis"))), None)
                or next((n for n in names if n.lower().endswith(".csv")), None)
            )
            xlsx_name = (
                next((n for n in names if n.endswith(("02_TABEL_PENELITIAN_TERDAHULU_BAB2.xlsx", "Tabel_Sintesis_Bab2.xlsx"))), None)
                or next((n for n in names if n.lower().endswith(".xlsx") and any(k in os.path.basename(n).lower() for k in ("bab2", "penelitian", "sintesis"))), None)
            )
            ris_name = (
                next((n for n in names if n.endswith("01_IMPOR_KE_ZOTERO.ris")), None)
                or next((n for n in names if n.lower().endswith(".ris")), None)
            )
            if csv_name:
                bab2_raw = _read_bab2_csv_bytes(zf.read(csv_name))
            elif xlsx_name:
                try:
                    bab2_raw = _read_bab2_xlsx_bytes(zf.read(xlsx_name))
                except Exception as e:
                    warn("Could not read Bab 2 xlsx from ZIP: %s" % e)
            if ris_name:
                ris_records = parse_ris_text(zf.read(ris_name).decode("utf-8-sig", errors="replace"))

    if bab2_path and os.path.exists(bab2_path):
        with open(bab2_path, "rb") as f:
            raw = f.read()
        if bab2_path.lower().endswith(".xlsx"):
            bab2_raw = _read_bab2_xlsx_bytes(raw)
        else:
            bab2_raw = _read_bab2_csv_bytes(raw)

    if ris_path and os.path.exists(ris_path):
        with open(ris_path, "r", encoding="utf-8-sig", errors="replace") as f:
            ris_records = parse_ris_text(f.read())

    return {
        "bab2_table": _normalize_bab2_table_rows(bab2_raw),
        "ris_records": ris_records,
    }


def _resolve_preset_path(name_or_path):
    if not name_or_path:
        return None
    if os.path.exists(name_or_path):
        return name_or_path
    clean = re.sub(r"\.json$", "", str(name_or_path).strip().lower())
    aliases = {
        "kuantitatif": "preset_kuantitatif.json",
        "kualitatif": "preset_kualitatif.json",
        "rnd": "preset_rnd.json",
        "r&d": "preset_rnd.json",
        "informatika": "preset_informatika_ilkom.json",
        "informatika_ilkom": "preset_informatika_ilkom.json",
        "ilkom": "preset_informatika_ilkom.json",
        "ptk": "preset_ptk.json",
    }
    fname = aliases.get(clean, f"preset_{clean}.json")
    candidate = os.path.join(PRESETS_DIR, fname)
    return candidate if os.path.exists(candidate) else None


def apply_preset_to_spec(spec, preset_name):
    ppath = _resolve_preset_path(preset_name)
    if not ppath:
        warn("Preset not found: %s" % preset_name)
        return spec
    with open(ppath, "r", encoding="utf-8") as f:
        pdata = json.load(f)
    spec = json.loads(json.dumps(spec))
    if pdata.get("chapters"):
        spec.setdefault("body", {})["chapters"] = pdata["chapters"]
    if pdata.get("citation_style") and not spec.get("citation_style"):
        spec["citation_style"] = pdata["citation_style"]
    return spec


# --------------------------------------------------------------------------- layout & typography helpers

def _infer_heading_spacing(chapters, tiered=False):
    """Infer sensible default (left_indent_cm, hanging_indent_cm) per heading level 2..4."""
    result = {}
    has_prefix = {2: False, 3: False, 4: False}
    alpha_prefix = {2: False, 3: False, 4: False}
    max_depth = {2: 0, 3: 0, 4: 0}
    for ch in chapters or []:
        for sub in ch.get("sections", []):
            lvl = min(max(int(sub.get("level", 2)), 2), 4)
            title = str(sub.get("title", "")).strip()
            m_num = re.match(r"^(\d+(?:\.\d+)*)\.?\s+", title)
            m_alpha = re.match(r"^([A-Za-z]|[IVXLCDM]+|\d+)[\.\)]\s+", title)
            if m_num:
                has_prefix[lvl] = True
                max_depth[lvl] = max(max_depth[lvl], len(m_num.group(1)))
            elif m_alpha:
                has_prefix[lvl] = True
                alpha_prefix[lvl] = True
                max_depth[lvl] = max(max_depth[lvl], len(m_alpha.group(1)) + 1)

    cum_left = 0.0
    for lvl in (2, 3, 4):
        if not has_prefix[lvl]:
            result[lvl] = (0.0, 0.0)
            continue
        if alpha_prefix[lvl]:
            hang = 0.65
        else:
            hang = max(0.75, min(1.55, 0.30 + max_depth[lvl] * 0.22))
            hang = round(hang, 2)
        left = round(cum_left, 2) if tiered else 0.0
        result[lvl] = (left, hang)
        cum_left += hang
    return result


def _format_inverted_pyramid(text, max_first=46):
    """Break a long title into lines shaped like an inverted pyramid (longest -> shortest)."""
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    if "\n" in text or len(text) <= max_first:
        return text
    words = text.split(" ")
    if len(words) < 3:
        return text
    # Target 2..4 balanced decreasing lines
    n_lines = min(4, max(2, math.ceil(len(text) / max_first)))
    lines = []
    idx = 0
    total_chars = len(text)
    rem_lines = n_lines
    prev_len = max_first + 8
    while idx < len(words):
        if rem_lines <= 1:
            lines.append(" ".join(words[idx:]))
            break
        # Aim for slightly more than average remaining so each line narrows cleanly
        rem_text_len = sum(len(w) + 1 for w in words[idx:]) - 1
        target = min(prev_len - 2, max(16, int((rem_text_len / rem_lines) * 1.18)))
        cur = []
        cur_len = 0
        while idx < len(words):
            w = words[idx]
            add_len = len(w) + (1 if cur else 0)
            if cur and cur_len + add_len > target:
                break
            cur.append(w)
            cur_len += add_len
            idx += 1
        line_str = " ".join(cur)
        lines.append(line_str)
        prev_len = max(20, len(line_str))
        rem_lines -= 1
    return "\n".join(lines)


class Layout:
    def __init__(self, spec):
        page = spec.get("page", {})
        w, h = PAPER.get(str(page.get("paper", "A4")).upper(), PAPER["A4"])
        self.w = page.get("width_cm", w)
        self.h = page.get("height_cm", h)
        m = page.get("margins_cm", {})
        self.top, self.bottom = m.get("top", 4), m.get("bottom", 3)
        self.left, self.right = m.get("left", 4), m.get("right", 3)
        self.gutter = page.get("gutter_cm", 0)
        self.header_dist = page.get("header_distance_cm", 1.25)
        self.footer_dist = page.get("footer_distance_cm", 1.25)
        self.text_width = self.w - self.left - self.right - self.gutter
        self.text_height = self.h - self.top - self.bottom


# --------------------------------------------------------------------------- builder

class Builder:
    def __init__(self, spec, cache=None, workdir=None, muza_data=None, logo_override=None, table_style_override=None):
        self.spec = spec
        self.cache = cache
        self.lay = Layout(spec)
        self.doc = Document()
        self.items = []
        self.item_sections = {}  # id(p._element) -> item metadata
        self.workdir = workdir or tempfile.mkdtemp()
        self.muza_data = muza_data or {}
        self.logo_override = logo_override
        self.table_style = table_style_override or spec.get("table_style", "three_line")
        self.tiered_heading_indent = bool(spec.get("tiered_heading_indent") or spec.get("body", {}).get("tiered_heading_indent"))
        self.heading_spacing = _infer_heading_spacing(spec.get("body", {}).get("chapters", []), tiered=self.tiered_heading_indent)
        self.heading_has_hang = {}
        self._seq_reset_done = set()

        ph = {p["key"]: dict(p) for p in DEFAULT_PLACEHOLDERS}
        for p in spec.get("placeholders", []):
            ph[p["key"]] = {**ph.get(p["key"], {}), **p}
        campus = spec.get("campus", {})
        for ck, clabel in (
            ("university", "Nama perguruan tinggi"),
            ("short", "Singkatan kampus"),
            ("faculty", "Nama fakultas"),
            ("program", "Nama program studi"),
            ("degree", "Gelar lulusan"),
            ("ministry", "Kementerian / Yayasan"),
        ):
            if campus.get(ck):
                ph[ck] = {**ph.get(ck, {}), "key": ck, "sample": campus[ck], "label": clabel}
        self.placeholders = ph
        self._logo_comment_done = False
        self.can_comment = hasattr(self.doc, "add_comment")
        self.end_marker = "MUZASKRIPSI-END-OF-TUTORIAL"

    # ---- text helpers
    def sub(self, text):
        def rep(m):
            k = m.group(1)
            return self.placeholders[k]["sample"] if k in self.placeholders else m.group(0)
        return re.sub(r"\{(\w+)\}", rep, str(text))

    def add_text(self, p, text, bold=None, italic=None, size=None, hint=False, caps=None, color=None):
        lines = self.sub(text).split("\n")
        runs = []
        for i, line in enumerate(lines):
            r = p.add_run(line, style="Petunjuk" if hint else None)
            if bold is not None:
                r.bold = bold
            if italic is not None:
                r.italic = italic
            if size:
                r.font.size = Pt(size)
            if caps is False:
                r.font.all_caps = False
            if color is not None:
                r.font.color.rgb = color
            if i < len(lines) - 1:
                r.add_break(WD_BREAK.LINE)
            runs.append(r)
        return runs

    def para(self, text="", style=None, align=None, **kw):
        p = self.doc.add_paragraph(style=style)
        runs = self.add_text(p, text, **kw) if text else []
        if align:
            p.alignment = ALIGN[align]
        return p, runs

    def comment(self, runs, text, fallback_style="Isi Paragraf"):
        if not text:
            return
        text = "Petunjuk pedoman: " + self.sub(text)
        if self.can_comment and runs:
            try:
                self.doc.add_comment(runs, text=text, author="MuZA Agent", initials="MZ")
                return
            except Exception as e:
                warn("comment failed (%s), using grey hint" % e)
                self.can_comment = False
        self.para("[%s]" % text, style=fallback_style, hint=True)

    def record(self, kind, style, text, level=1, toc=True, region="front", para_obj=None, page_prefix=""):
        clean = re.sub(r"\s+", " ", self.sub(text)).strip()
        item = {
            "kind": kind,
            "style": style,
            "text": clean,
            "level": level,
            "toc": toc,
            "region": region,
            "page_prefix": page_prefix,
            "elem": para_obj._element if para_obj is not None else None,
        }
        self.items.append(item)

    def add_caption_with_seq(self, full_text, style="Judul Tabel", chapter_num=None):
        """Write a caption using Word SEQ fields (while preserving full text for Pass 1 & TOC)."""
        resolved = self.sub(full_text)
        live_seq = self.spec.get("captions", {}).get("live_seq_fields", True)
        p = self.doc.add_paragraph(style=style)
        m = re.match(r"^(Tabel|Gambar|Lampiran)\s+(?:(\d+)\.)?(\d+)(.*)$", resolved.strip(), re.I)
        if m and live_seq:
            label_word = m.group(1)
            ch_str = m.group(2)
            seq_num = m.group(3)
            rest = m.group(4)
            reset_key = (label_word.lower(), ch_str or str(chapter_num or ""))
            should_reset = (seq_num == "1" and reset_key not in self._seq_reset_done)
            self._seq_reset_done.add(reset_key)
            r_pre = p.add_run(f"{label_word} " + (f"{ch_str}." if ch_str else ""))
            instr = f"SEQ {label_word} \\* ARABIC" + (" \\r 1" if should_reset else "")
            add_field(p, instr, seq_num)
            r_post = p.add_run(rest)
            runs = [r_pre, r_post]
        else:
            runs = self.add_text(p, resolved)
        return p, runs, resolved

    # ---- sections & page numbering
    def setup_section(self, section, numbering, v_align=None):
        lay = self.lay
        section.page_width, section.page_height = Cm(lay.w), Cm(lay.h)
        section.top_margin, section.bottom_margin = Cm(lay.top), Cm(lay.bottom)
        section.left_margin, section.right_margin = Cm(lay.left), Cm(lay.right)
        section.gutter = Cm(lay.gutter)
        section.header_distance, section.footer_distance = Cm(lay.header_dist), Cm(lay.footer_dist)
        sect = section._sectPr
        for tag in ("w:pgNumType", "w:vAlign"):
            for el in sect.findall(qn(tag)):
                sect.remove(el)
        numbering = numbering or {}
        pg = OxmlElement("w:pgNumType")
        pg.set(qn("w:fmt"), numbering.get("fmt", "decimal"))
        if numbering.get("restart_at") is not None:
            pg.set(qn("w:start"), str(numbering["restart_at"]))
        cols = sect.find(qn("w:cols"))
        cols.addprevious(pg) if cols is not None else sect.append(pg)
        if v_align:
            va = OxmlElement("w:vAlign")
            va.set(qn("w:val"), v_align)
            succ = [qn(t) for t in ("w:noEndnote", "w:titlePg", "w:textDirection", "w:bidi", "w:rtlGutter", "w:docGrid", "w:printerSettings")]
            target = next((c for c in sect if c.tag in succ), None)
            target.addprevious(va) if target is not None else sect.append(va)

        diff_first = bool(numbering.get("different_first"))
        section.different_first_page_header_footer = diff_first
        page_prefix = numbering.get("prefix", "")
        pairs = [(section.header, section.footer, numbering.get("others"))]
        if diff_first:
            pairs.append((section.first_page_header, section.first_page_footer, numbering.get("first")))
        for header, footer, pos in pairs:
            for hf in (header, footer):
                hf.is_linked_to_previous = False
                for p in hf.paragraphs:
                    for r in list(p.runs):
                        r._r.getparent().remove(r._r)
                    p.style = "Nomor Halaman"
            if not pos or pos == "none":
                continue
            where, side = pos.split("_")
            p = (header if where == "top" else footer).paragraphs[0]
            p.alignment = ALIGN[side]
            if page_prefix:
                p.add_run(page_prefix)
            add_field(p, "PAGE", "1")

    def new_section(self, numbering, v_align=None):
        sec = self.doc.add_section(WD_SECTION.NEW_PAGE)
        self.setup_section(sec, numbering, v_align)
        return sec

    # ---- styles
    def build_styles(self):
        doc, spec, lay = self.doc, self.spec, self.lay
        font = spec.get("font", {}).get("name", "Times New Roman")
        size = spec.get("font", {}).get("size", 12)
        lang = spec.get("language_code", "id-ID")
        body = spec.get("body_text", {})
        st = spec.get("styles", {})
        ls = body.get("line_spacing", 1.5)

        def apply(style, f, tab_at=None):
            style.font.name = f.get("font", font)
            set_rfonts(style.element.get_or_add_rPr(), f.get("font", font))
            set_lang(style.element.get_or_add_rPr(), lang)
            style.font.color.rgb = BLACK
            style.font.size = Pt(f.get("size", size))
            style.font.bold = bool(f.get("bold", False))
            style.font.italic = bool(f.get("italic", False))
            style.font.all_caps = bool(f.get("caps", False))
            style.font.underline = bool(f.get("underline", False))
            pf = style.paragraph_format
            pf.alignment = ALIGN[f.get("align", "left")]
            pf.line_spacing = float(f.get("line_spacing", ls))
            pf.space_before = Pt(f.get("space_before", 0))
            pf.space_after = Pt(f.get("space_after", 0))
            pf.first_line_indent = Cm(f.get("first_indent", 0))
            pf.left_indent = Cm(f.get("left_indent", 0))
            pf.right_indent = Cm(f.get("right_indent", 0))
            hang = f.get("hanging_indent")
            if isinstance(hang, (int, float)) and hang > 0:
                total_left = f.get("left_indent", 0) + hang
                pf.left_indent = Cm(total_left)
                pf.first_line_indent = Cm(-hang)
                if tab_at is True:
                    pf.tab_stops.add_tab_stop(Cm(total_left), WD_TAB_ALIGNMENT.LEFT)
            pf.keep_with_next = bool(f.get("keep_with_next", False))
            pf.widow_control = True

        def get(name, kind=WD_STYLE_TYPE.PARAGRAPH, base="Normal"):
            try:
                return doc.styles[name]
            except KeyError:
                s = doc.styles.add_style(name, kind)
                if base:
                    s.base_style = doc.styles[base]
                s.quick_style = True
                return s

        h2_def_left, h2_def_hang = self.heading_spacing[2]
        h3_def_left, h3_def_hang = self.heading_spacing[3]
        h4_def_left, h4_def_hang = self.heading_spacing[4]

        defaults = {
            "chapter": {"bold": True, "caps": True, "align": "center", "space_after": 24, "keep_with_next": True},
            "h2": {"bold": True, "keep_with_next": True, "space_before": 10, "space_after": 4, "left_indent": h2_def_left, "hanging_indent": h2_def_hang},
            "h3": {"bold": True, "keep_with_next": True, "space_before": 6, "space_after": 4, "left_indent": h3_def_left, "hanging_indent": h3_def_hang},
            "h4": {"bold": True, "keep_with_next": True, "space_before": 4, "space_after": 4, "left_indent": h4_def_left, "hanging_indent": h4_def_hang},
            "front_title": {"bold": True, "caps": True, "align": "center", "line_spacing": 1.0, "space_after": 24, "keep_with_next": True},
            "table_caption": {"align": "center", "line_spacing": 1.0, "space_before": 8, "space_after": 6, "keep_with_next": True},
            "figure_caption": {"align": "center", "line_spacing": 1.0, "space_before": 6, "space_after": 4},
            "appendix_caption": {"bold": True, "line_spacing": 1.0, "space_after": 12},
            "caption_source": {"size": max(size - 2, 10), "italic": True, "line_spacing": 1.0, "space_before": 3, "space_after": 12},
            "blockquote": {"align": "justify", "line_spacing": 1.0, "left_indent": 1.25, "right_indent": 0, "space_before": 6, "space_after": 6},
            "equation": {"align": "left", "line_spacing": 1.0, "space_before": 6, "space_after": 6},
            "bibliography": {"align": "justify", "line_spacing": 1.0, "hanging_indent": 1.25, "space_after": 10},
            "table_text": {"size": max(size - 1, 10), "line_spacing": 1.0},
            "toc": {"line_spacing": 1.0, "space_after": 4},
            "abstract": {"align": "justify", "line_spacing": 1.0, "first_indent": body.get("first_indent_cm", 1.25)},
            "cover": {"bold": True, "caps": True, "align": "center", "line_spacing": 1.0},
            "page_number": {"line_spacing": 1.0},
        }

        def fmt(key):
            d = dict(defaults[key])
            user = dict(st.get(key, {}))
            if user.get("hanging_indent") == "auto":
                user.pop("hanging_indent")
            d.update(user)
            return d

        apply(doc.styles["Normal"], {"line_spacing": ls})
        rpr_default = doc.styles.element.find(qn("w:docDefaults"))
        if rpr_default is not None:
            rpr = rpr_default.find(qn("w:rPrDefault") + "/" + qn("w:rPr"))
            if rpr is not None:
                set_rfonts(rpr, font)

        isi = get("Isi Paragraf")
        apply(isi, {
            "align": body.get("align", "justify"),
            "line_spacing": ls,
            "first_indent": body.get("first_indent_cm", 1.25),
            "space_before": body.get("space_before", 0),
            "space_after": body.get("space_after", 0),
        })
        isi.next_paragraph_style = isi

        for i, key in enumerate(("chapter", "h2", "h3", "h4"), 1):
            s = doc.styles["Heading %d" % i]
            cfg = fmt(key)
            has_hang = isinstance(cfg.get("hanging_indent"), (int, float)) and cfg.get("hanging_indent", 0) > 0
            self.heading_has_hang[i] = has_hang
            apply(s, cfg, tab_at=has_hang)
            set_outline(s, i - 1)
            s.next_paragraph_style = isi

        jb = get("Judul Bagian")
        apply(jb, fmt("front_title"))
        set_outline(jb, 0)
        jb.next_paragraph_style = isi
        jbn = get("Judul Bagian Tanpa Daftar Isi")
        apply(jbn, fmt("front_title"))
        set_outline(jbn, None)
        jbn.next_paragraph_style = isi

        for name, key in [
            ("Judul Tabel", "table_caption"),
            ("Judul Gambar", "figure_caption"),
            ("Judul Lampiran", "appendix_caption"),
            ("Keterangan Sumber", "caption_source"),
            ("Kutipan Langsung", "blockquote"),
            ("Rumus", "equation"),
            ("Daftar Pustaka", "bibliography"),
            ("Teks Tabel", "table_text"),
            ("Abstrak", "abstract"),
            ("Sampul", "cover"),
            ("Nomor Halaman", "page_number"),
        ]:
            s = get(name)
            apply(s, fmt(key))
            set_outline(s, None)

        rumus_s = doc.styles["Rumus"]
        rumus_s.paragraph_format.tab_stops.add_tab_stop(Cm(lay.text_width / 2.0), WD_TAB_ALIGNMENT.CENTER)
        rumus_s.paragraph_format.tab_stops.add_tab_stop(Cm(lay.text_width), WD_TAB_ALIGNMENT.RIGHT)

        doc.styles["Kutipan Langsung"].next_paragraph_style = doc.styles["Kutipan Langsung"]
        doc.styles["Daftar Pustaka"].next_paragraph_style = doc.styles["Daftar Pustaka"]
        doc.styles["Abstrak"].next_paragraph_style = doc.styles["Abstrak"]
        for name in ("Header", "Footer"):
            try:
                apply(doc.styles[name], fmt("page_number"))
            except KeyError:
                pass

        hint = get("Petunjuk", WD_STYLE_TYPE.CHARACTER, base=None)
        hint.font.italic = True
        hint.font.color.rgb = GREY

        toc_f = fmt("toc")
        step = toc_f.pop("indent_step_cm", 0.75)
        l1bold = toc_f.pop("level1_bold", False)
        for i in range(1, 5):
            s = get("toc %d" % i)
            f = dict(toc_f, left_indent=step * (i - 1), bold=(l1bold if i == 1 else False))
            apply(s, f)
            s.paragraph_format.right_indent = Cm(0.8)
            s.paragraph_format.tab_stops.add_tab_stop(Cm(lay.text_width), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        tof = get("table of figures")
        apply(tof, toc_f)
        tof.paragraph_format.right_indent = Cm(0.8)
        tof.paragraph_format.tab_stops.add_tab_stop(Cm(lay.text_width), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)

    # ---- blocks
    def blocks(self, blocks, region, chapter_num=None):
        for b in blocks or []:
            t = b.get("type", "text")
            style = b.get("style", "Isi Paragraf")
            if t in ("text", "placeholder"):
                p, runs = self.para(b.get("text", ""), style=style, align=b.get("align"),
                                    bold=b.get("bold"), italic=b.get("italic"), size=b.get("size"))
                if b.get("no_indent"):
                    p.paragraph_format.first_line_indent = Cm(0)
                if b.get("hint"):
                    self.comment(runs, b["hint"], style)
            elif t == "blockquote":
                p, runs = self.para(
                    b.get("text", ""),
                    style=b.get("style", "Kutipan Langsung"),
                    italic=b.get("italic"),
                    size=b.get("size"),
                )
                if b.get("hint"):
                    self.comment(runs, b["hint"], "Kutipan Langsung")
            elif t == "equation":
                p = self.doc.add_paragraph(style=b.get("style", "Rumus"))
                p.add_run("\t")
                r_formula = p.add_run(self.sub(b.get("formula", "y = a + bx")))
                r_formula.italic = bool(b.get("italic", True))
                runs = [r_formula]
                num = b.get("number", "")
                if num:
                    p.add_run("\t")
                    runs.append(p.add_run(self.sub(num)))
                if b.get("hint"):
                    self.comment(runs, b["hint"], "Rumus")
            elif t == "sample_paragraph":
                for _ in range(int(b.get("count", 1))):
                    self.para(SAMPLE_SENTENCES.format(topic=b.get("topic", "ini")), style=style)
            elif t == "hint":
                runs = self.doc.paragraphs[-1].runs if self.doc.paragraphs else []
                self.comment(runs, b.get("text"), style)
            elif t == "blank":
                for _ in range(int(b.get("lines", 1))):
                    self.doc.add_paragraph(style=style)
            elif t == "signature":
                self.signature(b)
            elif t == "fields":
                self.fields_table(b.get("rows", []), b.get("label_width_cm", 3.5))
            elif t == "table":
                self.data_table(
                    b.get("rows", [["", ""]]),
                    header=b.get("header", True),
                    table_style=b.get("table_style", self.table_style),
                    widths_cm=b.get("widths_cm"),
                )
            elif t == "keywords":
                p = self.doc.add_paragraph(style=b.get("style", "Abstrak"))
                p.paragraph_format.first_line_indent = Cm(0)
                p.paragraph_format.space_before = Pt(12)
                r = p.add_run(b.get("label", "Kata kunci: "))
                r.bold = True
                r2 = p.add_run(self.sub(b.get("text", "kata kunci satu, kata kunci dua, kata kunci tiga")))
                if b.get("italic"):
                    r2.italic = True
            elif t == "caption":
                st = b.get("style", "Judul Tabel")
                p, runs, resolved = self.add_caption_with_seq(b.get("text", ""), style=st, chapter_num=chapter_num)
                self.record("caption", st, resolved, region=region, para_obj=p)
                if b.get("hint"):
                    self.comment(runs, b["hint"], st)
            elif t == "page_break":
                self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
            else:
                warn("unknown block type %s" % t)

    def signature(self, b):
        cols = [list(c) for c in b.get("columns", [])]
        if not cols:
            return
        if b.get("position") == "right" and len(cols) == 1:
            cols = [[]] + cols
        doc = self.doc
        table = doc.add_table(rows=1, cols=len(cols))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table_borders(table, mode="none", header=False)
        set_widths(table, [self.lay.text_width / len(cols)] * len(cols))
        for i, lines in enumerate(cols):
            cell = table.rows[0].cells[i]
            first = True
            for line in lines:
                p = cell.paragraphs[0] if first else cell.add_paragraph()
                first = False
                p.style = "Teks Tabel"
                p.paragraph_format.line_spacing = 1.0
                p.alignment = ALIGN[b.get("align", "center")]
                if line == "{materai}":
                    self.add_text(p, "Materai 10.000", hint=True)
                    continue
                runs = self.add_text(p, line)
                is_name = any(line.startswith("{" + k) for k in ("name", "supervisor", "dean", "head", "rector")) or b.get("bold_line") == line
                for r in runs:
                    r.font.size = Pt(self.spec.get("font", {}).get("size", 12))
                    if is_name:
                        r.bold = True
                        r.underline = bool(b.get("underline_names", True))
        doc.add_paragraph(style="Teks Tabel")

    def fields_table(self, rows, label_w):
        table = self.doc.add_table(rows=len(rows), cols=3)
        table_borders(table, mode="none", header=False)
        set_widths(table, [label_w, 0.5, self.lay.text_width - label_w - 0.5])
        for i, (label, value) in enumerate(rows):
            cells = table.rows[i].cells
            for c, txt in zip(cells, (label, ":", value)):
                c.paragraphs[0].style = "Teks Tabel"
                c.paragraphs[0].paragraph_format.space_after = Pt(6)
                for r in self.add_text(c.paragraphs[0], txt):
                    r.font.size = Pt(self.spec.get("font", {}).get("size", 12))
        self.doc.add_paragraph(style="Teks Tabel")

    def data_table(self, rows, header=True, table_style=None, widths_cm=None, font_size=None):
        if not rows:
            return None
        mode = table_style if table_style is not None else self.table_style
        ncols = max(len(r) for r in rows)
        table = self.doc.add_table(rows=len(rows), cols=ncols)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table_borders(table, mode=mode, header=header)
        w_list = widths_cm if (widths_cm and len(widths_cm) == ncols) else [self.lay.text_width / ncols] * ncols
        set_widths(table, w_list)
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                p = table.rows[i].cells[j].paragraphs[0]
                p.style = "Teks Tabel"
                if header and i == 0:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for r in self.add_text(p, val, size=font_size):
                    if header and i == 0:
                        r.bold = True
        return table

    # ---- page-level
    def auto_space(self, lines, title_pt=0):
        cover_size = self.spec.get("styles", {}).get("cover", {}).get("size", self.spec.get("font", {}).get("size", 12))
        width_pt = self.lay.text_width * 28.35
        avail = (self.lay.h - self.lay.top - self.lay.bottom) * 28.35 * 0.95 - title_pt
        used = 0
        for it in lines:
            if it.get("type") == "logo":
                used += (it.get("height_cm") or it.get("width_cm", 4)) * 28.35
                continue
            if it.get("type") == "fields":
                used += len(it.get("rows", [])) * 20
                continue
            size = it.get("size", cover_size)
            txt = self.sub(it.get("text", ""))
            if it.get("inverted_pyramid"):
                txt = _format_inverted_pyramid(txt)
            k = 0.62 if it.get("caps", True) and it.get("bold", True) else 0.5
            n = sum(max(1, math.ceil(len(t) * size * k / width_pt)) for t in txt.split("\n"))
            used += n * size * 1.2
        gap = max((avail - used) / max(len(lines) - 1, 1), 4)
        out = []
        for i, it in enumerate(lines):
            it = dict(it)
            if i < len(lines) - 1 and "space_after" not in it:
                it["space_after"] = round(gap)
            out.append(it)
        return out

    def cover_lines(self, lines, auto=False, title_pt=0):
        if auto:
            lines = self.auto_space(lines, title_pt)
        for item in lines:
            if item.get("type") == "fields":
                self.fields_table(item.get("rows", []), item.get("label_width_cm", 3.5))
                continue
            if item.get("type") == "logo":
                p = self.doc.add_paragraph(style="Sampul")
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(item.get("space_before", 0))
                p.paragraph_format.space_after = Pt(item.get("space_after", 0))
                path = self.logo_override or item.get("path")
                if not (path and os.path.exists(path)):
                    path = os.path.join(self.workdir, "logo_placeholder.png")
                    if not os.path.exists(path) and not make_logo_placeholder(path):
                        self.add_text(p, "[ LOGO KAMPUS ]", hint=True)
                        continue
                w = item.get("width_cm", 4)
                h = item.get("height_cm")
                logo_run = p.add_run()
                logo_run.add_picture(path, width=Cm(w), height=Cm(h) if h else None)
                ov_logo = (self.spec.get("online_verification") or {}).get("logo") or {}
                if ov_logo.get("ok") and not self._logo_comment_done:
                    self._logo_comment_done = True
                    self.comment(
                        [logo_run],
                        f"Logo kampus dipasang otomatis dari sumber resmi ({ov_logo.get('method', 'Online')}: "
                        f"{ov_logo.get('source_url', '-')}). Klik kanan -> Change Picture jika perlu variasi logo fakultas.",
                    )
                continue
            p = self.doc.add_paragraph(style="Sampul")
            p.alignment = ALIGN[item.get("align", "center")]
            p.paragraph_format.space_before = Pt(item.get("space_before", 0))
            p.paragraph_format.space_after = Pt(item.get("space_after", 0))
            if "line_spacing" in item:
                p.paragraph_format.line_spacing = float(item["line_spacing"])
            raw_text = self.sub(item.get("text", ""))
            if item.get("inverted_pyramid"):
                raw_text = _format_inverted_pyramid(raw_text)
            self.add_text(p, raw_text, bold=item.get("bold", True), italic=item.get("italic"),
                          size=item.get("size"), caps=item.get("caps"))

    def tutorial_page(self):
        doc, spec = self.doc, self.spec
        self.setup_section(doc.sections[0], None)
        campus = spec.get("campus", {})
        ov = spec.get("online_verification") or {}
        ov_logo = ov.get("logo") or {}
        ov_fields = ov.get("fields") or {}
        has_real_logo = bool(self.logo_override and os.path.exists(self.logo_override))

        self.para("PANDUAN PENGGUNAAN TEMPLATE SKRIPSI (MuZA_Skripsi_Template v1.1)", style="Judul Bagian Tanpa Daftar Isi")
        p, _ = self.para(
            " — ".join(x for x in (campus.get("faculty"), campus.get("program"), campus.get("university")) if x),
            style="Sampul", bold=False, caps=False
        )
        p.paragraph_format.space_after = Pt(12)

        box = doc.add_table(rows=1, cols=1)
        table_borders(box, mode="grid", header=False)
        set_widths(box, [self.lay.text_width])
        cell = box.rows[0].cells[0]
        shade_cell(cell, "FFF2CC")
        cp = cell.paragraphs[0]
        cp.style = "Teks Tabel"
        r = cp.add_run("Silahkan Hapus halaman ini jika skripsi kamu sudah jadi atau sudah tidak diperlukan.")
        r.bold = True
        r.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
        cp2 = cell.add_paragraph(style="Teks Tabel")
        cp2.add_run("Catatan MuZA Project: ").bold = True
        cp2.add_run(
            "Halaman panduan ini berada pada section terpisah tanpa nomor halaman dan tidak masuk ke Daftar Isi, "
            "sehingga tidak mengganggu penomoran skripsimu. Untuk menghapusnya sebelum cetak: blok seluruh isi panduan "
            "ini sampai tepat sebelum Halaman Sampul, lalu tekan Delete."
        )

        step2_title = (
            "2. Logo resmi kampus sudah terpasang otomatis (bisa diganti jika perlu)"
            if has_real_logo
            else "2. Ganti logo kampus secara presisi"
        )
        step2_body = (
            f"Logo {campus.get('university', 'kampus')} sudah diunduh dan dipasang otomatis di Sampul & Halaman Judul "
            f"(sumber: {ov_logo.get('source_url') or 'file lokal'}). Jika prodi/fakultas memakai variasi logo khusus, "
            "klik kanan gambar logo -> Change Picture."
            if has_real_logo
            else "Klik kanan gambar lingkaran LOGO KAMPUS -> pilih Change Picture / Ubah Gambar -> pilih logo resmimu. "
                 "Dimensi cm logo sudah disesuaikan dengan pedoman."
        )
        steps = [
            ("1. Semua halaman wajib sudah jadi — isi Nama & NIM kamu sendiri via Ctrl+H",
             "Sampul, halaman judul, pengesahan, pernyataan keaslian, abstrak, kata pengantar, BAB I-V, daftar pustaka, "
             "dan lampiran sudah terisi rapi. Nama Mahasiswa dan NIM sengaja dipertahankan sebagai contoh agar kamu "
             "isi sendiri menggunakan Find & Replace (Ctrl+H) sesuai tabel di bawah."),
            (step2_title, step2_body),
            ("3. Petunjuk isi tiap sub-bab & sumber data pejabat ada di Komentar (Margin Review)",
             "Arahan pedoman kampus ditempatkan sebagai Word Comments dari MuZA Agent (tab Review). Komentar tidak ikut "
             "tercetak jika dimatikan, atau hapus semua sekaligus via Review -> Delete -> Delete All Comments."),
            ("4. Gunakan Style Word bawaan template, jangan format manual",
             "Tabel, Kutipan Langsung (spasi 1), Rumus (nomor rata kanan), serta Sub-Bab (Hanging Indent rapi) sudah "
             "tersedia sebagai Style resmi agar tata letak tidak rusak."),
            ("5. Daftar Isi, Tabel, Gambar, dan Lampiran sudah terisi & tetap Live Field",
             "Setelah selesai menulis skripsi, klik kanan daftar lalu pilih Update Field -> Update entire table."),
        ]
        for title, body in steps + [tuple(x) for x in spec.get("tutorial", {}).get("extra_steps", [])]:
            p = doc.add_paragraph(style="Teks Tabel")
            p.paragraph_format.space_before = Pt(7)
            p.paragraph_format.keep_with_next = True
            p.add_run(title).bold = True
            doc.add_paragraph(body, style="Teks Tabel")

        def heading(text):
            p = doc.add_paragraph(style="Teks Tabel")
            p.paragraph_format.space_before = Pt(11)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            p.add_run(text).bold = True

        heading("Cheat-Sheet Shortcut & Style Word (MuZA Project Quick Guide)")
        cheat_rows = [
            ["Kebutuhan", "Style / Shortcut", "Keterangan Cepat"],
            ["Isi Nama, NIM & Judul", "Ctrl + H (Mac: Cmd+Shift+H)", "Buka Find & Replace untuk mengubah NAMA LENGKAP MAHASISWA, NIM, Judul, & Pembimbing serentak"],
            ["Update Daftar Isi", "Klik Kanan -> Update Field (F9)", "Windows: Ctrl+A lalu F9 · Word Web: References -> Update Table · WPS: Update Index"],
            ["Judul BAB & Sub-Bab", "Heading 1 s/d Heading 4", "Heading 1 = BAB · Heading 2-4 otomatis Hanging Indent rapi untuk Daftar Isi"],
            ["Paragraf & Kutipan", "Isi Paragraf / Kutipan Langsung", "Gunakan Kutipan Langsung (spasi 1, menjorok) untuk kutipan >= 40 kata"],
            ["Rumus & Caption", "Rumus / Judul Tabel / Judul Gambar", "Rumus memusatkan formula & meratakan nomor (2.1) di kanan otomatis"],
        ]
        self.data_table(cheat_rows, header=True, table_style="grid", widths_cm=[
            round(self.lay.text_width * 0.25, 2),
            round(self.lay.text_width * 0.30, 2),
            round(self.lay.text_width * 0.45, 2),
        ], font_size=9.5)

        if ov_fields or ov_logo.get("ok"):
            heading("Identitas, Logo & Pejabat Kampus Hasil Pencarian Daring (Verifikasi Sebelum Cetak)")
            ov_rows = [["Komponen", "Nilai Diterapkan", "Status & Sumber Internet"]]
            label_map = {
                "university": "Perguruan Tinggi",
                "short": "Singkatan",
                "city": "Kota Kampus",
                "ministry": "Kementerian/Naungan",
                "degree": "Gelar Lulusan",
                "rector": "Rektor / Pimpinan PT",
                "id_rector": "NIP/NIDN Rektor",
                "dean": "Dekan Fakultas",
                "id_dean": "NIP/NIDN Dekan",
                "head_program": "Ketua Program Studi",
                "id_head": "NIP/NIDN Kaprodi",
            }
            for k, lbl in label_map.items():
                info = ov_fields.get(k)
                if info and info.get("value"):
                    st_txt = "✓ Terverifikasi" if info.get("verified") else "ℹ Periksa ulang"
                    src_u = info.get("source_url") or info.get("source_label") or "-"
                    ov_rows.append([lbl, info["value"], f"{st_txt} ({src_u})"])
                elif k in ("dean", "head_program", "rector"):
                    ov_rows.append([lbl, self.placeholders.get(k, {}).get("sample", "-"), "⚠ Isi/periksa manual (tidak dipublikasikan terbuka)"])
            if ov_logo.get("ok"):
                ov_rows.append([
                    "Logo Resmi Kampus",
                    f"Terpasang ({ov_logo.get('width', '?')}x{ov_logo.get('height', '?')} px PNG)",
                    f"✓ {ov_logo.get('method', 'Online')} ({ov_logo.get('source_url', '-')})",
                ])
            self.data_table(ov_rows, header=True, table_style="grid", widths_cm=[
                round(self.lay.text_width * 0.24, 2),
                round(self.lay.text_width * 0.36, 2),
                round(self.lay.text_width * 0.40, 2),
            ], font_size=9.0)

        used = set()
        blob = json.dumps(spec, ensure_ascii=False)
        for k in self.placeholders:
            if "{" + k + "}" in blob:
                used.add(k)
        # Keep student & unresolved/editable placeholders in Find & Replace table
        verified_static = {k for k, v in ov_fields.items() if v.get("verified") and k in ("city", "university", "short", "ministry")}
        skip_replace = {"university", "short", "faculty", "program", "ministry"} | verified_static
        rows = [["Teks contoh di template", "Ganti dengan (via Find & Replace Ctrl+H)"]]
        rows += [
            [self.placeholders[k]["sample"], self.placeholders[k].get("label", k)]
            for k in self.placeholders
            if k in used and k not in skip_replace
        ]
        if len(rows) > 1:
            heading("Teks contoh yang perlu diisi sendiri (Find & Replace Ctrl+H)")
            self.data_table(rows, header=True, table_style="grid", font_size=9.5)

        summary = spec.get("format_summary", [])
        if summary:
            heading("Ringkasan Ketentuan Pedoman Kampus (* = standar default MuZA)")
            srows = [["Aspek Format", "Ketentuan Diterapkan", "Sumber & Status"]]
            for s in summary:
                from_g = s.get("from_guideline", True)
                val = s.get("value", "") + ("" if from_g else " *")
                src_txt = s.get("source", "Tidak diatur")
                status = f"✓ Sesuai Pedoman ({src_txt})" if from_g else f"* Default Akademik ({src_txt})"
                srows.append([s.get("item", ""), val, status])
            self.data_table(srows, header=True, table_style="grid", font_size=9.5)

        src = spec.get("source_document", {})
        p = doc.add_paragraph(style="Teks Tabel")
        p.paragraph_format.space_before = Pt(10)
        self.add_text(p, "Sumber pedoman: %s%s" % (src.get("title", "-"), (" — " + src["url"]) if src.get("url") else ""), hint=True)
        p = doc.add_paragraph(style="Teks Tabel")
        self.add_text(p, spec.get("credit", "Template dibuat otomatis dengan MuZA_Skripsi_Template v1.1 (MuZA Project)."), hint=True)
        p = doc.add_paragraph(style="Teks Tabel")
        r = p.add_run(self.end_marker)
        r.font.size = Pt(1)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    def cover_page(self):
        cover = self.spec.get("cover", {})
        va = cover.get("vertical_align", "auto")
        self.new_section(None, None if va == "auto" else va)
        self.cover_lines(cover.get("lines", []), auto=(va == "auto"))

    def listing(self, instr, key, empty_msg):
        entries = (self.cache or {}).get(key)
        if not entries:
            p = self.doc.add_paragraph(style="Isi Paragraf")
            p.paragraph_format.first_line_indent = Cm(0)
            add_field(p, instr, empty_msg, dirty=True)
            return
        last = len(entries) - 1
        for i, (style, text, page) in enumerate(entries):
            p = self.doc.add_paragraph(style=style)
            if i == 0:
                fld_run(p, "begin")
                instr_run(p, instr)
                fld_run(p, "separate")
            p.add_run(text)
            p.add_run("\t" + page)
            if i == last:
                fld_run(p, "end")

    def front_matter(self):
        fm = self.spec.get("front_matter", {})
        fmt = fm.get("number_format", "lowerRoman")
        pos = fm.get("number_position", "bottom_center")
        levels = self.spec.get("toc", {}).get("levels", 3)
        for n, pg in enumerate(fm.get("pages", [])):
            show = pg.get("show_number", True)
            numbering = {"fmt": fmt, "restart_at": fm.get("start_at", 1) if n == 0 else None,
                         "others": pos if show else None}
            va = pg.get("vertical_align", "auto" if pg.get("lines") else None)
            self.new_section(numbering, None if va == "auto" else va)
            self.record("anchor", "", "#SECTION#", toc=False, region="front")
            in_toc = pg.get("in_toc", True)
            if pg.get("title"):
                tp, runs = self.para(pg["title"], style="Judul Bagian" if in_toc else "Judul Bagian Tanpa Daftar Isi")
                self.record("heading", "toc 1", pg["title"], toc=in_toc, region="front", para_obj=tp)
                self.comment(runs, pg.get("hint"))
            if pg.get("lines"):
                self.cover_lines(pg["lines"], auto=(va == "auto"), title_pt=60 if pg.get("title") else 0)
            kind = pg.get("kind", "page")
            if kind == "toc":
                self.listing('TOC \\o "1-%d" \\h \\z \\u' % levels, "toc",
                             "Klik kanan di sini lalu pilih Update Field untuk menampilkan Daftar Isi.")
            elif kind in ("list_of_tables", "list_of_figures", "list_of_appendices"):
                sty = {"list_of_tables": "Judul Tabel", "list_of_figures": "Judul Gambar",
                       "list_of_appendices": "Judul Lampiran"}[kind]
                self.listing('TOC \\h \\z \\t "%s,1"' % sty, sty,
                             "Klik kanan di sini lalu pilih Update Field untuk menampilkan daftar.")
            self.blocks(pg.get("blocks"), "front")

    def _inject_muza_bab2(self, p_section, ch_num):
        """Inject MuZA_Search v1.1 Bab 2 synthesis table right into Bab 2 Penelitian Terdahulu."""
        rows = self.muza_data.get("bab2_table")
        if not rows or len(rows) < 2:
            return
        self.para(
            f"Tabel {ch_num}.1 merangkum matriks penelitian terdahulu yang relevan hasil pencarian dan ekstraksi "
            "otomatis menggunakan mesin MuZA_Search v1.1 untuk memetakan metode, dataset/sampel, dan capaian metrik evaluasi.",
            style="Isi Paragraf",
        )
        tcap_str = f"Tabel {ch_num}.1 Ringkasan Penelitian Terdahulu (Sintesis MuZA_Search v1.1)"
        cp, runs, resolved = self.add_caption_with_seq(tcap_str, style="Judul Tabel", chapter_num=ch_num)
        self.record("caption", "Judul Tabel", resolved, region="body", para_obj=cp)
        self.comment(runs, "Tabel ini diimpor otomatis dari file hasil MuZA_Search v1.1 (02_TABEL_PENELITIAN_TERDAHULU_BAB2.csv).", "Judul Tabel")

        w = self.lay.text_width
        widths = [round(w * r, 2) for r in (0.06, 0.16, 0.23, 0.18, 0.16, 0.21)]
        self.data_table(rows, header=True, table_style=self.table_style, widths_cm=widths, font_size=9.5)
        yr = self.placeholders.get("year", {}).get("sample", "2026")
        self.para(f"Sumber: Sintesis literatur otomatis MuZA_Search v1.1 ({yr}).", style="Keterangan Sumber")

    def chapters(self):
        bd = self.spec.get("body", {})
        fmt = bd.get("number_format", "decimal")
        first_pos = bd.get("chapter_first_page_position", "bottom_center")
        other_pos = bd.get("other_pages_position", "top_right")
        levels = self.spec.get("toc", {}).get("levels", 3)
        has_bab2_table = bool(self.muza_data.get("bab2_table"))
        bab2_injected = False

        for n, ch in enumerate(bd.get("chapters", [])):
            ch_num = ch.get("number", n + 1)
            numbering = {"fmt": fmt, "restart_at": bd.get("start_at", 1) if n == 0 else None,
                         "first": first_pos, "others": other_pos, "different_first": first_pos != other_pos}
            self.new_section(numbering)
            self.record("anchor", "", "#SECTION#", toc=False, region="body")
            p = self.doc.add_paragraph(style="Heading 1")
            sep = "\n" if bd.get("chapter_heading_two_lines", True) else " "
            runs = self.add_text(p, ("%s%s%s" % (ch.get("label", ""), sep, ch.get("title", ""))).strip())
            self.record("heading", "toc 1", "%s %s" % (ch.get("label", ""), ch.get("title", "")), region="body", para_obj=p)
            self.comment(runs, ch.get("hint"))

            sections = list(ch.get("sections", []))
            if ch_num == 2 and has_bab2_table:
                idx_prev = next(
                    (idx for idx, s in enumerate(sections)
                     if re.search(r"penelitian\s+terdahulu|penelitian\s+relevan|kajian\s+empiris|tinjauan\s+studi", s.get("title", ""), re.I)),
                    None,
                )
                if idx_prev is None:
                    sections.append({"level": 2, "title": f"2.{len(sections) + 1} Penelitian Terdahulu", "_inject_muza_bab2": True})
                else:
                    sections[idx_prev] = dict(sections[idx_prev], _inject_muza_bab2=True)

            for sub in sections:
                lvl = min(max(int(sub.get("level", 2)), 2), 4)
                raw_title = str(sub.get("title", ""))
                disp_title = raw_title
                if self.heading_has_hang.get(lvl):
                    m_pre = re.match(r"^((?:\d+(?:\.\d+)*\.?|[A-Za-z]{1,2}[\.\)]))\s+(.+)$", raw_title.strip())
                    if m_pre:
                        disp_title = f"{m_pre.group(1)}\t{m_pre.group(2)}"
                sp, runs = self.para(disp_title, style="Heading %d" % lvl)
                self.record("heading", "toc %d" % lvl, raw_title, level=lvl, toc=lvl <= levels, region="body", para_obj=sp)
                self.comment(runs, sub.get("hint"))
                if sub.get("_inject_muza_bab2") and not bab2_injected:
                    self._inject_muza_bab2(sp, ch_num)
                    bab2_injected = True
                elif sub.get("blocks"):
                    self.blocks(sub["blocks"], "body", chapter_num=ch_num)
                elif sub.get("placeholder", True):
                    topic = re.sub(r"^\s*([A-Za-z]|\d+(\.\d+)*)[\.\)]?\s+", "", raw_title)
                    self.para(SAMPLE_SENTENCES.format(topic=topic), style="Isi Paragraf")

            if ch.get("sample_captions"):
                self.sample_captions(ch)

    def sample_captions(self, ch):
        cap = self.spec.get("captions", {})
        n = ch.get("number", 1)
        tcap = cap.get("table_example", "Tabel %s.1 Contoh Judul Tabel" % n)
        tp, runs, resolved_t = self.add_caption_with_seq(tcap, style="Judul Tabel", chapter_num=n)
        self.record("caption", "Judul Tabel", resolved_t, region="body", para_obj=tp)
        self.comment(runs, cap.get("table_hint", "Contoh penulisan tabel akademik (3-garis horizontal tanpa garis vertikal + repeat header)."))
        self.data_table(
            [["No", "Aspek Pengamatan", "Indikator / Hasil"],
             ["1", "Contoh aspek pertama", "Contoh data terukur (98,4%)"],
             ["2", "Contoh aspek kedua", "Contoh perbandingan baseline"]],
            header=True,
            table_style=self.table_style,
            widths_cm=[round(self.lay.text_width * r, 2) for r in (0.10, 0.45, 0.45)],
        )
        if cap.get("table_source"):
            self.para(cap["table_source"], style="Keterangan Sumber")
        else:
            self.doc.add_paragraph(style="Isi Paragraf")

        p = self.doc.add_paragraph(style="Judul Gambar")
        p.paragraph_format.keep_with_next = True
        path = os.path.join(self.workdir, "figure_placeholder.png")
        if make_figure_placeholder(path):
            p.add_run().add_picture(path, width=Cm(min(10, self.lay.text_width)))
        fcap = cap.get("figure_example", "Gambar %s.1 Contoh Judul Gambar" % n)
        fp, _, resolved_f = self.add_caption_with_seq(fcap, style="Judul Gambar", chapter_num=n)
        self.record("caption", "Judul Gambar", resolved_f, region="body", para_obj=fp)
        if cap.get("figure_source"):
            self.para(cap["figure_source"], style="Keterangan Sumber", align="center")

    def back_matter(self):
        bm = self.spec.get("back_matter", {})
        bd = self.spec.get("body", {})
        fmt = bd.get("number_format", "decimal")
        first_pos = bm.get("first_page_position", bd.get("chapter_first_page_position", "bottom_center"))
        other_pos = bm.get("other_pages_position", bd.get("other_pages_position", "top_right"))
        ris_records = list(self.muza_data.get("ris_records") or [])
        cite_style = self.spec.get("citation_style", "APA 7th")

        for pg in bm.get("pages", []):
            mode = str(pg.get("numbering_mode", "continue" if pg.get("show_number", True) else "none")).lower()
            prefix = ""
            restart = None
            if mode == "none" or not pg.get("show_number", True):
                numbering = {"fmt": fmt, "first": None, "others": None, "different_first": False}
            elif mode == "prefix":
                prefix = pg.get("page_prefix", "L-")
                restart = 1
                numbering = {"fmt": fmt, "restart_at": restart, "first": first_pos, "others": other_pos,
                             "different_first": first_pos != other_pos, "prefix": prefix}
            else:
                numbering = {"fmt": fmt, "first": first_pos, "others": other_pos,
                             "different_first": first_pos != other_pos}

            self.new_section(numbering)
            self.record("anchor", "", "#SECTION#", toc=False, region="body", page_prefix=prefix)
            in_toc = pg.get("in_toc", True)
            if pg.get("title"):
                bp, runs = self.para(pg["title"], style="Judul Bagian" if in_toc else "Judul Bagian Tanpa Daftar Isi")
                self.record("heading", "toc 1", pg["title"], toc=in_toc, region="body", para_obj=bp, page_prefix=prefix)
                self.comment(runs, pg.get("hint"))

            kind = pg.get("kind", "page")
            if kind == "references":
                if ris_records:
                    ordered = ris_records if "ieee" in cite_style.lower() else sorted(ris_records, key=_citation_sort_key)
                    for idx, rec in enumerate(ordered, 1):
                        p = self.doc.add_paragraph(style="Daftar Pustaka")
                        for seg_text, is_it in format_reference_segments(rec, cite_style, index=idx):
                            r = p.add_run(seg_text)
                            if is_it:
                                r.italic = True
                else:
                    for ex in pg.get("examples", []):
                        self.para(ex, style="Daftar Pustaka")
            elif kind == "appendices":
                for i, ap in enumerate(pg.get("items", ["Lampiran 1 Judul Lampiran"])):
                    if i:
                        self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
                    ap_p, _, resolved_ap = self.add_caption_with_seq(ap, style="Judul Lampiran")
                    self.record("caption", "Judul Lampiran", resolved_ap, region="body", para_obj=ap_p, page_prefix=prefix)
                    self.para("Letakkan isi lampiran di sini.", style="Isi Paragraf")
            self.blocks(pg.get("blocks"), "body")

    def build(self, update_fields):
        self.build_styles()
        self.tutorial_page()
        self.cover_page()
        self.front_matter()
        self.chapters()
        self.back_matter()

        settings = self.doc.settings.element
        zoom = settings.find(qn("w:zoom"))
        if zoom is not None and zoom.get(qn("w:percent")) is None:
            zoom.set(qn("w:percent"), "100")
        if update_fields:
            uf = OxmlElement("w:updateFields")
            uf.set(qn("w:val"), "true")
            after = {qn(t) for t in (
                "w:hdrShapeDefaults", "w:footnotePr", "w:endnotePr", "w:compat", "w:docVars",
                "w:rsids", "m:mathPr", "w:attachedSchema", "w:themeFontLang",
                "w:clrSchemeMapping", "w:decimalSymbol", "w:listSeparator",
            )}
            _insert_before(settings, uf, after)

        cp = self.doc.core_properties
        cp.title = "Template Skripsi %s (MuZA_Skripsi_Template v1.0)" % self.spec.get("campus", {}).get("university", "")
        cp.author = "MuZA Agent — MuZA Project"
        return self.doc


# --------------------------------------------------------------------------- page detection & analytical fallback

def norm(s):
    return re.sub(r"\s+", " ", s).upper().strip()


PAGE_TOKEN = re.compile(r"^((?:[A-Z]-)?\d+|[ivxlcdm]+|[IVXLCDM]+)$")


def page_label(raw):
    lines = [l.strip() for l in raw.split("\n") if l.strip()]
    for l in (lines[-1:] + lines[:1]) if lines else []:
        if PAGE_TOKEN.match(l):
            return l
    return None


def _extract_pdf_pages_text(pdf_path):
    pdftotext = shutil.which("pdftotext")
    if pdftotext:
        try:
            out = subprocess.run(
                [pdftotext, "-layout", pdf_path, "-"],
                capture_output=True, text=True, encoding="utf-8", errors="ignore"
            ).stdout
            if out:
                return out.split("\f")
        except Exception:
            pass
    try:
        from pypdf import PdfReader
        return [(pg.extract_text() or "") for pg in PdfReader(pdf_path).pages]
    except Exception:
        return []


def estimate_cache(builder):
    """Analytical fallback page estimator when LibreOffice is absent."""
    fm = builder.spec.get("front_matter", {})
    fm_start = fm.get("start_at", 1)
    body_start = builder.spec.get("body", {}).get("start_at", 1)
    upper = fm.get("number_format", "lowerRoman") == "upperRoman"
    base_size = float(builder.spec.get("font", {}).get("size", 12))
    base_ls = float(builder.spec.get("body_text", {}).get("line_spacing", 1.5))
    chars_per_line = max(45, int(builder.lay.text_width * 28.35 / (base_size * 0.48)))
    avail_pt = builder.lay.text_height * 28.35

    by_elem = {it["elem"]: it for it in builder.items if it.get("elem") is not None}
    cache = {"toc": [], "Judul Tabel": [], "Judul Gambar": [], "Judul Lampiran": []}

    body_el = builder.doc.element.body
    # Group children into sections by trailing w:sectPr in pPr, skipping section 0 (tutorial) & 1 (cover)
    sections = []
    cur_sec = []
    for child in body_el:
        if child.tag == qn("w:sectPr"):
            sections.append(cur_sec)
            cur_sec = []
            continue
        cur_sec.append(child)
        ppr = child.find(qn("w:pPr")) if child.tag == qn("w:p") else None
        if ppr is not None and ppr.find(qn("w:sectPr")) is not None:
            sections.append(cur_sec)
            cur_sec = []

    front_page = fm_start - 1
    body_page = body_start - 1
    local_pref_page = 0
    region_anchors = [it for it in builder.items if it["kind"] == "anchor"]

    for sec_idx, elems in enumerate(sections):
        if sec_idx < 2:
            continue
        anc_idx = sec_idx - 2
        anchor = region_anchors[anc_idx] if anc_idx < len(region_anchors) else {"region": "body", "page_prefix": ""}
        reg = anchor["region"]
        prefix = anchor.get("page_prefix", "")
        if reg == "front":
            front_page += 1
        elif prefix:
            local_pref_page = 1
        else:
            body_page += 1
        used_pt = 0.0

        def advance_page():
            nonlocal front_page, body_page, local_pref_page, used_pt
            used_pt = 0.0
            if reg == "front":
                front_page += 1
            elif prefix:
                local_pref_page += 1
            else:
                body_page += 1

        for el in elems:
            tag = el.tag
            if tag == qn("w:p"):
                # Explicit page break
                has_pb = any(br.get(qn("w:type")) == "page" for br in el.findall(".//" + qn("w:br")))
                if has_pb:
                    advance_page()
                txt = "".join(t.text or "" for t in el.findall(".//" + qn("w:t")))
                n_lines = max(1, math.ceil(max(1, len(txt)) / chars_per_line))
                h_pt = n_lines * base_size * base_ls + 6.0
                if el.findall(".//" + qn("w:drawing")):
                    h_pt += 220.0
                if used_pt > 0 and used_pt + h_pt > avail_pt:
                    advance_page()

                it = by_elem.get(el)
                if it:
                    if reg == "front":
                        lab = roman(front_page, upper)
                    elif prefix:
                        lab = f"{prefix}{local_pref_page}"
                    else:
                        lab = str(body_page)
                    if it["kind"] == "heading" and it["toc"]:
                        cache["toc"].append((it["style"], it["text"], lab))
                    elif it["kind"] == "caption":
                        cache[it["style"]].append(("table of figures", it["text"], lab))
                used_pt += h_pt
            elif tag == qn("w:tbl"):
                rows = el.findall(qn("w:tr"))
                tbl_h = 0.0
                for tr in rows:
                    txt = "".join(t.text or "" for t in tr.findall(".//" + qn("w:t")))
                    r_lines = max(1, math.ceil(max(1, len(txt)) / max(30, chars_per_line * 0.85)))
                    r_h = r_lines * max(10.0, base_size - 1) * 1.15 + 8.0
                    if used_pt > 0 and used_pt + r_h > avail_pt:
                        advance_page()
                    used_pt += r_h
                    tbl_h += r_h

    return cache, "estimated"


def compute_cache(docx_path, builder):
    soffice = find_soffice()
    if not soffice:
        return estimate_cache(builder)
    out = tempfile.mkdtemp()
    try:
        subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", out, docx_path],
                       capture_output=True, timeout=240)
        pdf = os.path.join(out, os.path.splitext(os.path.basename(docx_path))[0] + ".pdf")
        if not os.path.exists(pdf):
            warn("PDF render failed: using analytical page estimator")
            return estimate_cache(builder)
        raw = _extract_pdf_pages_text(pdf)
        if not raw:
            warn("PDF text extraction empty: using analytical page estimator")
            return estimate_cache(builder)
    except Exception as e:
        warn("LibreOffice render failed (%s): using analytical page estimator" % e)
        return estimate_cache(builder)

    pages = [norm(p) for p in raw]
    labels = [page_label(p) for p in raw]
    cur = next((i for i, p in enumerate(raw) if builder.end_marker in p), 0) + 1
    fm = builder.spec.get("front_matter", {})
    fm_start = fm.get("start_at", 1)
    body_start = builder.spec.get("body", {}).get("start_at", 1)
    upper = fm.get("number_format", "lowerRoman") == "upperRoman"
    region_first = {}
    cache = {"toc": [], "Judul Tabel": [], "Judul Gambar": [], "Judul Lampiran": []}
    new_page = False
    for it in builder.items:
        if it["kind"] == "anchor":
            new_page = True
            continue
        target = norm(it["text"])
        if not target:
            continue
        start = cur + 1 if new_page else cur
        found = next((i for i in range(start, len(pages)) if target in pages[i]), None)
        if found is None:
            warn("not found in render: %s" % it["text"])
            continue
        cur, new_page = found, False
        region_first.setdefault(it["region"], found)
        lab = labels[found]
        if lab is None:
            first_idx = region_first[it["region"]]
            raw_lab = roman(fm_start + found - first_idx, upper) if it["region"] == "front" else str(body_start + found - first_idx)
            lab = f"{it.get('page_prefix', '')}{raw_lab}"
        if it["kind"] == "heading" and it["toc"]:
            cache["toc"].append((it["style"], it["text"], lab))
        elif it["kind"] == "caption":
            cache[it["style"]].append(("table of figures", it["text"], lab))
    return cache, "libreoffice"


# --------------------------------------------------------------------------- validation & build entrypoint

def validate(spec):
    for key in ("campus", "page", "font", "body_text", "front_matter", "body", "cover"):
        if key not in spec:
            warn("missing top-level key: %s" % key)
    if not spec.get("body", {}).get("chapters"):
        warn("body.chapters is empty")
    if not spec.get("format_summary"):
        warn("format_summary is empty: list every format rule with its source page")


def apply_campus_lookup_to_spec(spec, lookup_result=None, overrides=None):
    """Merge verified online campus lookup + optional official overrides into spec (never overwrites student name/nim)."""
    if not lookup_result and not overrides:
        return spec, None
    out = copy.deepcopy(spec)
    ov_fields = (lookup_result or {}).get("fields") or {}
    campus = dict(out.get("campus") or {})

    # Map lookup fields -> campus metadata & spec placeholders (expand short aliases like "UNDIP"/"UNNES" -> official full name)
    cur_u = (campus.get("university") or "").strip()
    found_u = ov_fields.get("university", {}).get("value")
    found_short = ov_fields.get("short", {}).get("value") or ""
    if found_u and (
        not cur_u
        or "contoh" in cur_u.lower()
        or (found_short and cur_u.lower() == found_short.lower())
        or (len(cur_u.split()) == 1 and len(found_u.split()) >= 2)
        or (cur_u.upper() in {"UNNES", "UNDIP", "UNWAHAS", "POLINES", "UDINUS", "UNISSULA", "USM", "UNIMUS", "UNISBANK"} and len(found_u.split()) >= 2)
    ):
        campus["university"] = found_u
    for ck in ("short", "website", "ministry", "degree"):
        val = (overrides or {}).get(ck) or ov_fields.get(ck, {}).get("value")
        if val:
            campus[ck] = val
    out["campus"] = campus

    phs = list(out.get("placeholders") or [])
    by_key = {p["key"]: dict(p) for p in phs}
    ph_keys = ("city", "dean", "id_dean", "head_program", "id_head", "rector", "id_rector", "degree", "ministry")
    for k in ph_keys:
        if k in by_key:
            cur_val = by_key[k].get("sample", "")
        else:
            cur_val = next((d["sample"] for d in DEFAULT_PLACEHOLDERS if d["key"] == k), "")
        manual_val = (overrides or {}).get(k)
        found_val = ov_fields.get(k, {}).get("value")
        chosen = manual_val or (found_val if (not cur_val or "contoh" in cur_val.lower() or "nama " in cur_val.lower() or cur_val in ("Kota", "0000000000", "Sarjana (S1)")) else cur_val)
        if chosen and chosen != cur_val:
            by_key[k] = {**by_key.get(k, {"key": k, "label": k}), "sample": str(chosen)}
            if manual_val:
                ov_fields[k] = {
                    "value": str(manual_val),
                    "verified": True,
                    "source_label": "Input / Override Pengguna",
                    "source_url": "Manual Form",
                }
        elif chosen and k not in by_key:
            by_key[k] = {"key": k, "sample": str(chosen), "label": k}
    out["placeholders"] = list(by_key.values())

    if lookup_result or overrides:
        out["online_verification"] = {
            "fields": ov_fields,
            "logo": (lookup_result or {}).get("logo") or {"ok": False},
            "sources": (lookup_result or {}).get("sources") or [],
            "pedoman_candidates": (lookup_result or {}).get("pedoman_candidates") or [],
        }

    # Update Pengesahan/cover/Kata Pengantar text automatically when university / faculty / program / officials exist
    _refresh_campus_labels_in_spec(out)
    logo_downloaded = ((lookup_result or {}).get("logo") or {}).get("path")
    return out, logo_downloaded


def _refresh_campus_labels_in_spec(spec):
    """Sync campus.university/faculty/program/city/degree strings into cover, front_matter, and example placeholder sentences."""
    campus = spec.get("campus") or {}
    uni = campus.get("university") or "Universitas Contoh"
    fac = campus.get("faculty") or "Fakultas Ilmu Komputer dan Sains"
    prog = campus.get("program") or "Teknik Informatika"
    deg = campus.get("degree") or "Sarjana (S1)"
    prog_full = f"Program Studi {prog}" if not prog.lower().startswith("program studi") else prog

    def _swap_campus_text(txt):
        if not txt:
            return txt
        txt = txt.replace("UNIVERSITAS CONTOH", uni.upper()).replace("Universitas Contoh", uni)
        if fac:
            txt = txt.replace("FAKULTAS ILMU KOMPUTER DAN SAINS", fac.upper()).replace("Fakultas Ilmu Komputer dan Sains", fac)
        if prog:
            txt = txt.replace("PROGRAM STUDI TEKNIK INFORMATIKA", prog_full.upper())
            txt = txt.replace("Program Studi Teknik Informatika", prog_full)
            txt = txt.replace("Program Studi Informatika", prog_full)
            txt = txt.replace("PROGRAM STUDI INFORMATIKA", prog_full.upper())
        if deg and "gelar Sarjana Komputer" in txt:
            txt = txt.replace("gelar Sarjana Komputer", f"gelar {deg}")
        return txt

    src_doc = spec.get("source_document")
    if isinstance(src_doc, dict) and "Universitas Contoh" in (src_doc.get("title") or ""):
        src_doc["title"] = _swap_campus_text(src_doc["title"])

    # Refresh cover lines if still referencing example university strings
    for item in spec.get("cover", {}).get("lines", []) or []:
        if "text" in item:
            item["text"] = _swap_campus_text(item["text"])

    for pg in spec.get("front_matter", {}).get("pages", []):
        for item in pg.get("lines", []) or []:
            if "text" in item:
                item["text"] = _swap_campus_text(item["text"])
        for blk in pg.get("blocks", []) or []:
            if blk.get("type") == "signature":
                for col in blk.get("columns", []):
                    for idx, line in enumerate(col):
                        if "Dekan Fakultas" in line and fac:
                            col[idx] = f"Dekan {fac}" if not fac.lower().startswith("dekan") else fac
                        elif "Ketua Program Studi" in line and prog:
                            col[idx] = f"Ketua Program Studi {prog}"
            elif blk.get("type") == "fields" and isinstance(blk.get("rows"), list):
                for row in blk["rows"]:
                    if isinstance(row, list) and len(row) >= 2 and isinstance(row[1], str):
                        row[1] = _swap_campus_text(row[1])
            elif isinstance(blk.get("text"), str):
                blk["text"] = _swap_campus_text(blk["text"])
            elif isinstance(blk.get("items"), list):
                new_items = []
                for it in blk["items"]:
                    if isinstance(it, str) and "Rektor Universitas" in it:
                        it = re.sub(r"Rektor Universitas [^,;]+", f"Rektor {uni} ({'{rector}'})", it)
                    elif isinstance(it, str) and "Dekan Fakultas" in it:
                        it = re.sub(r"Dekan Fakultas [^,;]+", f"Dekan {fac} ({'{dean}'})", it)
                    elif isinstance(it, str) and "Ketua Program Studi" in it:
                        it = re.sub(r"Ketua Program Studi [^,;]+", f"Ketua Program Studi {prog} ({'{head_program}'})", it)
                    new_items.append(_swap_campus_text(it) if isinstance(it, str) else it)
                blk["items"] = new_items


def build_from_spec(spec, out_path, muza_zip=None, muza_bab2=None, muza_ris=None,
                    preset=None, logo_path=None, table_style=None,
                    auto_online=False, find_pedoman=False, campus_overrides=None):
    """Build .docx file from a spec dict (with optional online campus/logo lookup) and return summary dict."""
    if preset or spec.get("preset"):
        spec = apply_preset_to_spec(spec, preset or spec.get("preset"))

    out = os.path.abspath(out_path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    work = tempfile.mkdtemp()

    lookup_res = None
    if auto_online or (spec.get("auto_lookup") is True):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            if script_dir not in sys.path:
                sys.path.insert(0, script_dir)
            from campus_lookup import cari_identitas_dan_pejabat_kampus, cari_pedoman_kampus_online
            c = spec.get("campus") or {}
            uni_q = c.get("university", "")
            fac_q = c.get("faculty", "")
            prog_q = c.get("program", "")
            if uni_q and "contoh" not in uni_q.lower():
                auto_logo_dest = None if (logo_path and os.path.exists(logo_path)) else os.path.join(work, "logo_kampus_resmi.png")
                lookup_res = cari_identitas_dan_pejabat_kampus(
                    uni_q, fakultas=fac_q, program_studi=prog_q, download_logo_to=auto_logo_dest
                )
                if find_pedoman:
                    ddg_p = cari_pedoman_kampus_online(uni_q, fakultas=fac_q, program_studi=prog_q, domain=lookup_res.get("domain", ""))
                    seen_u = {x["url"] for x in lookup_res.get("site_pedoman_pdfs", [])}
                    lookup_res["pedoman_candidates"] = list(lookup_res.get("site_pedoman_pdfs", [])) + [x for x in ddg_p if x["url"] not in seen_u]
        except Exception as e:
            warn(f"Online campus lookup skipped: {e}")

    spec, auto_logo = apply_campus_lookup_to_spec(spec, lookup_result=lookup_res, overrides=campus_overrides)
    effective_logo = logo_path if (logo_path and os.path.exists(logo_path)) else auto_logo
    validate(spec)

    integ = spec.get("muza_search_integration") or {}
    muza_data = load_muza_search_data(
        zip_path=muza_zip or integ.get("zip_path"),
        bab2_path=muza_bab2 or integ.get("bab2_path"),
        ris_path=muza_ris or integ.get("ris_path"),
    )

    cache = None
    source_mode = "estimated"
    for i in range(3):
        b = Builder(spec, cache, work, muza_data=muza_data, logo_override=effective_logo, table_style_override=table_style)
        b.build(update_fields=False)
        tmp = os.path.join(work, "pass%d.docx" % i)
        b.doc.save(tmp)
        new_cache, source_mode = compute_cache(tmp, b)
        if new_cache is None or new_cache == cache:
            cache = new_cache
            break
        cache = new_cache

    b2 = Builder(spec, cache, work, muza_data=muza_data, logo_override=effective_logo, table_style_override=table_style)
    b2.build(update_fields=(source_mode != "libreoffice"))
    b2.doc.save(out)
    n_toc = len(cache["toc"]) if cache else 0
    return {
        "output": out,
        "sections": len(b2.doc.sections),
        "chapters": len(spec.get("body", {}).get("chapters", [])),
        "toc_entries": n_toc,
        "page_source": source_mode,
        "bab2_injected": len(muza_data.get("bab2_table") or []) - 1 if muza_data.get("bab2_table") else 0,
        "refs_injected": len(muza_data.get("ris_records") or []),
        "online_lookup": lookup_res,
        "logo_placed": bool(effective_logo and os.path.exists(effective_logo)),
        "logo_path": effective_logo,
    }


def main():
    parser = argparse.ArgumentParser(description="MuZA_Skripsi_Template v1.1 (.docx Builder)")
    parser.add_argument("spec_json", help="Path to spec.json")
    parser.add_argument("out_docx", help="Output .docx path")
    parser.add_argument("--muza-zip", default=None, help="MuZA_Search v1.0 output .zip for auto Bab 2 & References")
    parser.add_argument("--muza-bab2", default=None, help="MuZA_Search 02_TABEL_PENELITIAN_TERDAHULU_BAB2 (.csv/.xlsx)")
    parser.add_argument("--muza-ris", default=None, help="MuZA_Search 01_IMPOR_KE_ZOTERO.ris")
    parser.add_argument("--preset", default=None, help="Methodology preset: kuantitatif|kualitatif|rnd|informatika_ilkom|ptk")
    parser.add_argument("--logo", default=None, help="Path to campus logo PNG/JPG")
    parser.add_argument("--table-style", default=None, choices=["three_line", "grid", "none"], help="Data table border mode")
    parser.add_argument("--auto-online", action="store_true", help="Cari & pasang logo serta identitas resmi kampus via internet")
    parser.add_argument("--find-pedoman", action="store_true", help="Cari juga tautan PDF pedoman skripsi kampus")
    parser.add_argument("--universitas", default=None, help="Override nama universitas")
    parser.add_argument("--fakultas", default=None, help="Override nama fakultas")
    parser.add_argument("--prodi", default=None, help="Override nama program studi")
    args = parser.parse_args()

    with open(args.spec_json, encoding="utf-8") as f:
        spec = json.load(f)
    if args.universitas:
        spec.setdefault("campus", {})["university"] = args.universitas
    if args.fakultas:
        spec.setdefault("campus", {})["faculty"] = args.fakultas
    if args.prodi:
        spec.setdefault("campus", {})["program"] = args.prodi

    res = build_from_spec(
        spec,
        args.out_docx,
        muza_zip=args.muza_zip,
        muza_bab2=args.muza_bab2,
        muza_ris=args.muza_ris,
        preset=args.preset,
        logo_path=args.logo,
        table_style=args.table_style,
        auto_online=args.auto_online,
        find_pedoman=args.find_pedoman,
    )
    print("OK: saved", res["output"])
    print(
        f"Sections: {res['sections']} | Chapters: {res['chapters']} | "
        f"TOC entries: {res['toc_entries']} ({res['page_source']}) | "
        f"Bab 2 injected: {res['bab2_injected']} | Refs injected: {res['refs_injected']} | "
        f"Logo placed: {res['logo_placed']}"
    )


if __name__ == "__main__":
    main()
