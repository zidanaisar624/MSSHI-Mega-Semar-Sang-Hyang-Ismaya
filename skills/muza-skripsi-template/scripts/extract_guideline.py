#!/usr/bin/env python3
"""
MuZA_Skripsi_Template v1.0 — Smart Guideline Extractor & Rule Detector.
Extracts all text from a campus thesis guideline (PDF / DOCX / DOC / TXT) with
`=== PAGE n ===` markers, ranks pages by format keyword density, detects sample
layout pages (cover, approval, abstract, TOC), and auto-detects candidate rules
(paper, margins, font, spacing, indent, numbering, citation style, chapters).

Cross-OS compatible: Windows, Linux, macOS, and Google Colab.

Usage:
    python extract_guideline.py <guideline_file> [out.txt] [--json rules.json]
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

for _pylibs_cand in (
    os.path.join(os.path.expanduser("~"), "HermesData", "skripsi-pylibs"),
    r"D:\HermesData\skripsi-pylibs",
):
    if os.path.isdir(_pylibs_cand) and _pylibs_cand not in sys.path:
        sys.path.insert(0, _pylibs_cand)

KEYWORDS = [
    # paper / margins
    "kertas", "a4", "kuarto", "folio", "f4", "hvs", "gram", "margin", "batas", "tepi", "kiri", "kanan", "atas", "bawah",
    # font / spacing
    "huruf", "font", "times new roman", "arial", "calibri", "cambria", "garamond", "ukuran", "spasi", "spacing",
    "paragraf", "alinea", "menjorok", "ketukan",
    # numbering
    "nomor halaman", "penomoran", "romawi", "angka arab", "pojok", "tengah bawah", "bawah tengah", "kanan atas", "kanan bawah",
    # structure
    "sistematika", "bab i", "bab ii", "bab iii", "bab iv", "bab v", "sampul", "cover", "halaman judul", "pengesahan",
    "persetujuan", "pernyataan", "keaslian", "abstrak", "abstract", "kata pengantar", "daftar isi", "daftar tabel",
    "daftar gambar", "daftar lampiran", "daftar pustaka", "lampiran", "logo", "tabel", "gambar", "kutipan", "rumus",
    "apa", "harvard", "vancouver", "ieee", "chicago", "turabian", "catatan kaki", "bodynote",
]

SAMPLE_PAGE_PATTERNS = {
    "contoh_sampul": r"\b(?:contoh\s+(?:halaman\s+)?sampul|contoh\s+cover|format\s+sampul)\b",
    "contoh_halaman_judul": r"\bcontoh\s+halaman\s+judul\b",
    "contoh_persetujuan": r"\bcontoh\s+(?:lembar|halaman)\s+persetujuan\b",
    "contoh_pengesahan": r"\bcontoh\s+(?:lembar|halaman)\s+pengesahan\b",
    "contoh_pernyataan": r"\bcontoh\s+(?:surat\s+)?pernyataan\s+keaslian\b",
    "contoh_abstrak": r"\bcontoh\s+abstrak\b",
    "contoh_daftar_isi": r"\bcontoh\s+daftar\s+isi\b",
    "contoh_daftar_pustaka": r"\bcontoh\s+(?:penulisan\s+)?daftar\s+pustaka\b",
}


def find_soffice():
    """Find LibreOffice soffice binary across Windows, macOS, and Linux."""
    found = shutil.which("soffice") or shutil.which("libreoffice")
    if found:
        return found
    candidates = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\LibreOffice\program\soffice.exe"),
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/usr/bin/soffice",
        "/usr/local/bin/soffice",
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def pdf_text(path):
    """Extract text page-by-page using pdftotext, pypdf, or pdfplumber."""
    pages = []
    pdftotext = shutil.which("pdftotext")
    if pdftotext:
        try:
            out = subprocess.run(
                [pdftotext, "-layout", path, "-"],
                capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=180
            ).stdout
            if out:
                pages = out.split("\f")
                if len(pages) > 1 and not pages[-1].strip():
                    pages = pages[:-1]
        except Exception:
            pages = []

    if sum(len(p.strip()) for p in pages) < 200:
        try:
            from pypdf import PdfReader
            reader = PdfReader(path)
            pages = [(pg.extract_text() or "") for pg in reader.pages]
        except Exception:
            pages = []

    if sum(len(p.strip()) for p in pages) < 200:
        try:
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                pages = [(pg.extract_text() or "") for pg in pdf.pages]
        except Exception as e:
            if not pages:
                print("Could not read PDF:", e, file=sys.stderr)
    return pages


def docx_text(path):
    """Extract text from a DOCX file into ~60-line virtual blocks."""
    from docx import Document
    d = Document(path)
    chunks = [p.text for p in d.paragraphs if p.text.strip()]
    for t in d.tables:
        for row in t.rows:
            chunks.append(" | ".join(c.text.strip() for c in row.cells))
    lines = "\n".join(chunks).split("\n")
    return ["\n".join(lines[i:i + 60]) for i in range(0, len(lines), 60)] or [""]


def _add_candidate(store, key, value, page_num, snippet=""):
    entry = {"value": value, "page": page_num}
    if snippet:
        entry["evidence"] = re.sub(r"\s+", " ", snippet).strip()[:140]
    bucket = store.setdefault(key, [])
    if not any(x["value"] == value and x["page"] == page_num for x in bucket):
        bucket.append(entry)


def auto_detect_rules(pages):
    """Scan extracted guideline pages to produce structured candidate rules with page citations."""
    rules = {
        "paper": [],
        "paper_weight": [],
        "margins": [],
        "font": [],
        "font_sizes": [],
        "line_spacing": [],
        "indent": [],
        "page_numbering": [],
        "citation_style": [],
        "abstract_words": [],
        "chapters": [],
        "sample_pages": {},
    }

    margin_side_re = re.compile(
        r"(?:batas|margin|pias)\s*(?:atas|top|kiri|left|bawah|bottom|kanan|right)?[^\n.]{0,40}"
        r"(\d+(?:[.,]\d+)?)\s*(cm|inci|inch|mm)",
        re.I,
    )
    margin_explicit_re = re.compile(
        r"(?:margin\s+(?:atas|kiri|bawah|kanan)[^0-9]{1,25}\d|atas\s*[:=]?\s*\d+(?:[.,]\d+)?\s*cm|"
        r"(?:4|3|2\.5|2,5)\s*[-–/]\s*(?:4|3|2\.5|2,5)\s*[-–/]\s*(?:3|2\.5|2,5)\s*[-–/]\s*(?:3|2\.5|2,5))",
        re.I,
    )
    font_re = re.compile(r"\b(Times New Roman|Arial|Calibri|Cambria|Garamond|Book Antiqua|Tahoma|Verdana)\b", re.I)
    font_size_re = re.compile(r"(?:ukuran|size|huruf|font)[^\n.]{0,35}\b(10|11|12|14|16)\s*(?:pt|point)?\b", re.I)
    spasi_re = re.compile(r"\b(1[.,]5|2[.,]0|1[.,]0|1|2|satu|dua|ganda|double|single)\s*spasi\b|\bspasi\s*(1[.,]5|2[.,]0|1[.,]0|1|2|ganda|double|single)\b", re.I)
    indent_re = re.compile(r"(?:menjorok|alinea|paragraf|tab)[^\n.]{0,35}(\d+(?:[.,]\d+)?\s*(?:cm|ketukan|karakter|huruf|tab|mm))", re.I)
    cite_re = re.compile(r"\b(APA(?:\s*(?:edisi|ed\.?)?\s*[67])?|IEEE|Vancouver|Harvard|Chicago|Turabian|Body\s*note|Footnote|Catatan\s*kaki)\b", re.I)
    abs_re = re.compile(r"abstrak[^\n.]{0,60}(\d{2,3}\s*(?:-|s/?d|sampai|hingga)?\s*\d{2,3}|\bmaksimal\s*\d{2,3}|\bpaling\s*banyak\s*\d{2,3})\s*kata", re.I)
    bab_re = re.compile(r"\b(BAB\s+(?:I|II|III|IV|V|VI)\s+[A-Z][A-Z\s]{3,45})\b")

    for i, raw in enumerate(pages, 1):
        txt = raw or ""
        low = txt.lower()

        if re.search(r"\bA4\b|21\s*[x×]\s*29[.,]7", txt, re.I):
            _add_candidate(rules, "paper", "A4 (21 x 29.7 cm)", i)
        if re.search(r"\b(?:Kuarto|Quarto|Letter)\b|21[.,]5\s*[x×]\s*28", txt, re.I):
            _add_candidate(rules, "paper", "Kuarto / Letter", i)
        if re.search(r"\b(?:F4|Folio)\b|21[.,]5\s*[x×]\s*33", txt, re.I):
            _add_candidate(rules, "paper", "F4 / Folio (21.5 x 33 cm)", i)

        for m in re.finditer(r"\b(70|80)\s*(?:gram|gr|gsm)\b", low):
            _add_candidate(rules, "paper_weight", f"HVS {m.group(1)} gram", i, m.group(0))

        for m in margin_explicit_re.finditer(txt):
            start = max(0, m.start() - 20)
            end = min(len(txt), m.end() + 70)
            _add_candidate(rules, "margins", re.sub(r"\s+", " ", txt[start:end]).strip(), i)
        if not rules["margins"]:
            for m in margin_side_re.finditer(txt):
                _add_candidate(rules, "margins", m.group(0), i)

        for m in font_re.finditer(txt):
            _add_candidate(rules, "font", m.group(1), i)

        for m in font_size_re.finditer(txt):
            _add_candidate(rules, "font_sizes", f"{m.group(1)} pt", i, m.group(0))

        for m in spasi_re.finditer(txt):
            val = (m.group(1) or m.group(2) or "").replace(",", ".")
            _add_candidate(rules, "line_spacing", f"{val} spasi", i, m.group(0))

        for m in indent_re.finditer(txt):
            _add_candidate(rules, "indent", m.group(1), i, m.group(0))

        for pat, desc in [
            (r"romawi\s+kecil", "Romawi kecil (i, ii, iii)"),
            (r"angka\s+arab", "Angka Arab (1, 2, 3)"),
            (r"kanan\s+atas|atas\s+(?:sebelah\s+)?kanan", "Pojok kanan atas"),
            (r"tengah\s+bawah|bawah\s+tengah", "Tengah bawah"),
            (r"kanan\s+bawah|bawah\s+(?:sebelah\s+)?kanan", "Pojok kanan bawah"),
        ]:
            m = re.search(pat, low)
            if m:
                _add_candidate(rules, "page_numbering", desc, i)

        for m in cite_re.finditer(txt):
            _add_candidate(rules, "citation_style", m.group(1), i)

        for m in abs_re.finditer(txt):
            _add_candidate(rules, "abstract_words", m.group(0), i)

        for m in bab_re.finditer(txt):
            title_clean = re.sub(r"\s+", " ", m.group(1)).strip()
            if 7 <= len(title_clean) <= 55:
                _add_candidate(rules, "chapters", title_clean, i)

        for sp_key, sp_pat in SAMPLE_PAGE_PATTERNS.items():
            if re.search(sp_pat, low):
                rules["sample_pages"].setdefault(sp_key, []).append(i)

    return rules


def print_rule_summary(rules):
    print("\n=== AUTO-DETECTED GUIDELINE CANDIDATES (Verify against full text) ===")
    labels = [
        ("paper", "Paper size"),
        ("paper_weight", "Paper weight"),
        ("margins", "Margins"),
        ("font", "Font family"),
        ("font_sizes", "Font sizes"),
        ("line_spacing", "Line spacing"),
        ("indent", "Paragraph indent"),
        ("page_numbering", "Page numbering"),
        ("citation_style", "Citation style"),
        ("abstract_words", "Abstract word limit"),
        ("chapters", "Detected chapters"),
    ]
    for key, label in labels:
        items = rules.get(key) or []
        if not items:
            continue
        shown = "; ".join(f"{x['value']} (hlm. {x['page']})" for x in items[:5])
        print(f"  - {label:20s}: {shown}")
    if rules.get("sample_pages"):
        print("  - Sample/Appendix pages:")
        for k, pgs in rules["sample_pages"].items():
            print(f"      * {k:24s}: hlm. {', '.join(str(p) for p in pgs[:8])}")


def extract_file(src, out_txt=None):
    """Extract text pages from src PDF/DOCX/DOC/TXT and return (pages, out_txt_path)."""
    if out_txt is None:
        out_txt = os.path.join(tempfile.gettempdir(), "guideline.txt")
    ext = os.path.splitext(src)[1].lower()
    if ext == ".doc":
        soffice = find_soffice()
        if not soffice:
            raise RuntimeError("LibreOffice not found to convert legacy .doc file. Convert to .pdf or .docx first.")
        tmpdir = tempfile.mkdtemp()
        subprocess.run([soffice, "--headless", "--convert-to", "docx", "--outdir", tmpdir, src],
                       capture_output=True, timeout=180)
        src = os.path.join(tmpdir, os.path.splitext(os.path.basename(src))[0] + ".docx")
        ext = ".docx"
    if ext == ".pdf":
        pages = pdf_text(src)
    elif ext == ".docx":
        pages = docx_text(src)
    else:
        with open(src, encoding="utf-8", errors="ignore") as f:
            pages = [f.read()]

    os.makedirs(os.path.dirname(os.path.abspath(out_txt)), exist_ok=True)
    with open(out_txt, "w", encoding="utf-8") as f:
        for i, p in enumerate(pages, 1):
            f.write("\n=== PAGE %d ===\n%s\n" % (i, p))
    return pages, out_txt


def main():
    args = sys.argv[1:]
    if not args or "-h" in args or "--help" in args:
        print(__doc__)
        sys.exit(1 if not args else 0)

    json_out = None
    pos = []
    i = 0
    while i < len(args):
        if args[i] == "--json" and i + 1 < len(args):
            json_out = args[i + 1]
            i += 2
        else:
            pos.append(args[i])
            i += 1

    src = pos[0]
    out = pos[1] if len(pos) > 1 else os.path.join(tempfile.gettempdir(), "guideline.txt")
    pages, out = extract_file(src, out)

    total = sum(len(p) for p in pages)
    print("Pages/blocks: %d | characters: %d | saved to %s" % (len(pages), total, out))
    ext = os.path.splitext(src)[1].lower()
    if ext == ".pdf" and total < 200 * max(1, len(pages)) / 4:
        print("LOW TEXT: this PDF is probably scanned. Render pages to images and view them.")

    hits = {}
    for idx, p in enumerate(pages, 1):
        low = p.lower()
        for k in KEYWORDS:
            if re.search(r"\b" + re.escape(k) + r"\b", low):
                hits.setdefault(idx, []).append(k)
    ranked = sorted(hits.items(), key=lambda kv: -len(kv[1]))
    print("\nPages with the most format keywords (read these first, then read the rest):")
    for page, ks in ranked[:25]:
        print("  page %d: %s" % (page, ", ".join(ks[:12])))

    rules = auto_detect_rules(pages)
    print_rule_summary(rules)
    if json_out:
        with open(json_out, "w", encoding="utf-8") as jf:
            json.dump(rules, jf, ensure_ascii=False, indent=2)
        print("\nSaved detected rule candidates to:", json_out)


if __name__ == "__main__":
    main()
