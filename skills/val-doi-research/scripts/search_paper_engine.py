#!/usr/bin/env python3
"""
search_paper_engine.py — Modul Searching Paper Ringan (Win10/11 RAM 4 GB) Terhubung ke Engine DOI 2-Lapis.

Menyediakan pencarian literatur akademik Nasional (Indonesia) & Internasional yang terhubung
langsung ke `doi_engine.py` (Lapisan 1 Gratis + Lapisan 2 Elsevier BYOK), tanpa membutuhkan
dependensi berat seperti scikit-learn/matplotlib saat dijalankan lokal di laptop RAM 4 GB.

Fitur:
- Input fleksibel: topik penelitian, daftar DOI langsung (copy-paste), atau gabungan keduanya.
- Morfologi Bahasa Indonesia (peluluhan KPTS) + skor relevansi BM25 ringan murni Python stdlib.
- Klasifikasi Nasional vs Internasional + anti-kebocoran aksara non-Latin.
- Pengayaan otomatis tiap kandidat terpilih lewat `ResearchEngine.resolve()` (Unpaywall, Crossref,
  Semantic Scholar, PubMed/Europe PMC, arXiv, Green-OA Preprint, dan Elsevier BYOK bila aktif).
- Ekspor langsung bundel `.zip` (`01_IMPOR_KE_ZOTERO.ris`, `02_TABEL_PENELITIAN_TERDAHULU_BAB2.csv`,
  `03_METADATA_MUZA_SKRIPSI.json`, `metadata_doi.json`, `referensi.bib`) siap masuk `build_template.py`.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import urllib.parse
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import doi_engine as de  # noqa: E402

STOPWORDS = {
    "dan", "yang", "di", "ke", "dari", "pada", "untuk", "dengan", "dalam", "atau", "adalah",
    "sebagai", "oleh", "terhadap", "menggunakan", "berbasis", "studi", "analisis", "penelitian",
    "the", "and", "of", "in", "to", "for", "with", "on", "using", "based", "study", "analysis",
    "a", "an", "by", "from", "at", "as", "is", "are", "this", "that",
}

NON_LATIN_RE = re.compile(r"[\u0400-\u04FF\u0600-\u06FF\u0E00-\u0E7F\u3040-\u30FF\u4E00-\u9FFF\uAC00-\uD7AF]")
INDO_MARKERS = (
    "universitas", "institut", "politeknik", "sekolah tinggi", "indonesia", "jurnal",
    "sinta", "garuda", "semarang", "jakarta", "bandung", "yogyakarta", "surabaya", "malang",
)
INDO_INTL_PREFIXES = ("10.11591/", "10.14716/", "10.12928/", "10.22266/", "10.26555/", "10.30596/")


@dataclass
class SearchCandidate:
    record: de.PaperRecord
    category: str = "Internasional"   # "Nasional" | "Internasional"
    relevance_score: float = 0.0
    country_code: str = ""


@dataclass
class PaperSearchResult:
    topic: str
    national: List[SearchCandidate] = field(default_factory=list)
    international: List[SearchCandidate] = field(default_factory=list)
    direct_doi_records: List[de.PaperRecord] = field(default_factory=list)
    bundle_info: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)


def stem_id_light(word: str) -> str:
    """Stemmer ringan morfologi KPTS Bahasa Indonesia tanpa library eksternal (hemat RAM)."""
    w = word.lower().strip()
    if len(w) <= 4:
        return w
    for suf in ("kannya", "annya", "nya", "kan", "an"):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            w = w[: -len(suf)]
            break
    if w.startswith(("meng", "peng")) and len(w) > 6:
        rest = w[4:]
        return ("k" + rest) if rest[:1] in "aiueo" else rest
    if w.startswith(("meny", "peny")) and len(w) > 6:
        return "s" + w[4:]
    if w.startswith(("mem", "pem")) and len(w) > 5:
        rest = w[3:]
        return ("p" + rest) if rest[:1] in "aiueo" else rest
    if w.startswith(("men", "pen")) and len(w) > 5:
        rest = w[3:]
        return ("t" + rest) if rest[:1] in "aiueo" else rest
    for pre in ("ber", "ter", "per", "di", "ke", "se"):
        if w.startswith(pre) and len(w) - len(pre) >= 4:
            return w[len(pre):]
    return w


def tokenize_stemmed(text: str) -> List[str]:
    words = re.findall(r"[A-Za-z0-9]{2,}", (text or "").lower())
    return [stem_id_light(w) for w in words if w not in STOPWORDS]


def score_bm25_lite(query: str, docs: List[str]) -> List[float]:
    q_tokens = tokenize_stemmed(query)
    if not q_tokens or not docs:
        return [0.0 for _ in docs]
    doc_tokens = [tokenize_stemmed(d) for d in docs]
    avgdl = max(1.0, sum(len(t) for t in doc_tokens) / len(doc_tokens))
    n_docs = len(docs)
    df: Dict[str, int] = {}
    for q in set(q_tokens):
        df[q] = sum(1 for dt in doc_tokens if q in dt)
    scores: List[float] = []
    k1, b = 1.5, 0.75
    for dt in doc_tokens:
        dl = len(dt) or 1
        tf_map: Dict[str, int] = {}
        for tok in dt:
            tf_map[tok] = tf_map.get(tok, 0) + 1
        sc = 0.0
        for q in q_tokens:
            f = tf_map.get(q, 0)
            if not f:
                continue
            idf = math.log(1.0 + (n_docs - df.get(q, 0) + 0.5) / (df.get(q, 0) + 0.5))
            sc += idf * (f * (k1 + 1.0)) / (f + k1 * (1.0 - b + b * dl / avgdl))
        scores.append(sc)
    peak = max(scores) if scores else 0.0
    if peak <= 0:
        return [25.0 for _ in docs]
    return [round(min(100.0, 35.0 + 65.0 * (s / peak)), 1) for s in scores]


def classify_paper(rec: de.PaperRecord, country_code: str = "", intl_indo_as: str = "Internasional") -> Optional[str]:
    blob = f"{rec.title} {rec.venue} {rec.publisher}".strip()
    if NON_LATIN_RE.search(blob):
        return None
    doi = (rec.doi or "").lower()
    if any(doi.startswith(p) for p in INDO_INTL_PREFIXES) and (rec.language or "en").lower() == "en":
        return intl_indo_as
    aff_blob = " ".join(a.affiliation.lower() for a in rec.authors)
    is_id = (
        country_code.upper() == "ID"
        or (rec.language or "").lower() in ("id", "ind", "ms")
        or doi.startswith("10.2") and any(m in (rec.venue + " " + rec.publisher + " " + aff_blob).lower() for m in INDO_MARKERS)
        or any(m in (rec.venue + " " + rec.publisher).lower() for m in INDO_MARKERS)
    )
    return "Nasional" if is_id else "Internasional"


def search_papers(
    topic: str = "",
    dois: Optional[List[str]] = None,
    n_national: int = 5,
    n_international: int = 5,
    year_from: int = 0,
    year_to: int = 0,
    oa_only: bool = False,
    citation_style: str = "APA 7th",
    out_dir: str = "",
    download_pdf: bool = False,
    engine: Optional[de.ResearchEngine] = None,
) -> PaperSearchResult:
    """Cari paper berdasarkan topik + daftar DOI opsional memakai Engine DOI 2-Lapis."""
    engine = engine or de.ResearchEngine()
    result = PaperSearchResult(topic=topic or "Riset DOI & Literatur")

    # 1) Ekstrak DOI langsung bila ditempel di `topic` maupun parameter `dois`
    inline_dois = de.extract_identifiers(topic) if topic and de.DOI_RE.search(topic) else []
    explicit_dois: List[str] = []
    for item in (dois or []) + inline_dois:
        for ext in de.extract_identifiers(item):
            if ext not in explicit_dois:
                explicit_dois.append(ext)
    if inline_dois and len(inline_dois) == 1 and topic.strip() == inline_dois[0]:
        topic = ""  # murni lookup DOI

    if explicit_dois:
        result.direct_doi_records = de.resolve_many(explicit_dois, engine=engine)

    # 2) Pencarian kandidat topik di OpenAlex (+ DOAJ + Scopus BYOK bila aktif)
    raw_candidates: List[SearchCandidate] = []
    seen_dois: set[str] = {r.doi for r in result.direct_doi_records if r.doi}

    def _pull_openalex(extra_filter: str, query_text: str, per_page: int = 35) -> None:
        filters = ["has_doi:true"]
        if oa_only:
            filters.append("is_oa:true")
        if year_from and year_to:
            filters.append(f"publication_year:{year_from}-{year_to}")
        elif year_from:
            filters.append(f"from_publication_date:{year_from}-01-01")
        if extra_filter:
            filters.append(extra_filter)
        params = engine._openalex_params({
            "search": query_text,
            "filter": ",".join(filters),
            "per_page": per_page,
            "select": engine.OPENALEX_SELECT,
        })
        r = engine.get("https://api.openalex.org/works", params)
        if not (r.ok and isinstance(r.data, dict)):
            return
        for w in r.data.get("results") or []:
            rec = de.PaperRecord(query=query_text)
            rec.doi = de.normalize_doi(w.get("doi") or "")
            if rec.doi and rec.doi in seen_dois:
                continue
            engine._merge_openalex(rec, w)
            engine._finalize_oa(rec)
            cc = ""
            insts = [i.get("country_code", "") for a in (w.get("authorships") or []) for i in (a.get("institutions") or []) if isinstance(i, dict)]
            if "ID" in insts:
                cc = "ID"
            cat = classify_paper(rec, country_code=cc)
            if not cat:
                continue
            if rec.doi:
                seen_dois.add(rec.doi)
            raw_candidates.append(SearchCandidate(record=rec, category=cat, country_code=cc))

    if topic.strip():
        if n_national > 0:
            _pull_openalex("institutions.country_code:ID", topic, per_page=max(20, n_national * 4))
            # Tambahan DOAJ khusus jurnal Indonesia
            r_doaj = engine.get(
                f"https://doaj.org/api/search/articles/{urllib.parse.quote(topic)}",
                {"pageSize": max(15, n_national * 3)},
                retries=0,
            )
            if r_doaj.ok and isinstance(r_doaj.data, dict):
                for it in r_doaj.data.get("results") or []:
                    bib = it.get("bibjson") or {}
                    doi_v = next((de.normalize_doi(x.get("id", "")) for x in (bib.get("identifier") or []) if x.get("type") == "doi"), "")
                    if not doi_v or doi_v in seen_dois:
                        continue
                    yr = de._year(bib.get("year"))
                    if (year_from and yr and yr < year_from) or (year_to and yr and yr > year_to):
                        continue
                    country = ((bib.get("journal") or {}).get("country") or "").upper()
                    rec = de.PaperRecord(
                        query=topic, doi=doi_v, title=de._clean(bib.get("title")),
                        authors=[de._split_name(a.get("name", "")) for a in (bib.get("author") or []) if a.get("name")],
                        year=yr, venue=de._clean((bib.get("journal") or {}).get("title")),
                        publisher=de._clean((bib.get("journal") or {}).get("publisher")),
                        abstract=de._clean(bib.get("abstract")), abstract_source="DOAJ",
                        is_oa=True, oa_status="gold", sources_used=["DOAJ"], found=True,
                    )
                    for lk in bib.get("link") or []:
                        if lk.get("type") == "fulltext" and lk.get("url"):
                            rec.oa_links.append(de.OALink(lk["url"], "pdf" if ".pdf" in lk["url"].lower() else "landing", "DOAJ", "publishedVersion"))
                    engine._finalize_oa(rec)
                    cat = classify_paper(rec, country_code=country)
                    if cat:
                        seen_dois.add(doi_v)
                        raw_candidates.append(SearchCandidate(record=rec, category=cat, country_code=country))

        if n_international > 0:
            _pull_openalex("language:en", topic, per_page=max(25, n_international * 4))
            if engine.cfg.layer2_enabled:
                sc = engine.elsevier_search_scopus(f"TITLE-ABS-KEY({topic})", count=min(15, n_international * 2))
                for rw in sc.get("results") or []:
                    if rw.doi and rw.doi not in seen_dois:
                        seen_dois.add(rw.doi)
                        rec = engine.resolve(rw.doi)
                        cat = classify_paper(rec)
                        if cat:
                            raw_candidates.append(SearchCandidate(record=rec, category=cat))

        # Skor relevansi BM25 ringan
        scores = score_bm25_lite(topic, [f"{c.record.title} {c.record.abstract}" for c in raw_candidates])
        for cand, sc in zip(raw_candidates, scores):
            oa_bonus = 6.0 if cand.record.best_pdf_url else (3.0 if cand.record.is_oa else 0.0)
            cand.relevance_score = round(min(100.0, sc + oa_bonus), 1)

        nat_pool = sorted([c for c in raw_candidates if c.category == "Nasional"], key=lambda x: (-x.relevance_score, -(x.record.cited_by_count or 0)))
        intl_pool = sorted([c for c in raw_candidates if c.category == "Internasional"], key=lambda x: (-x.relevance_score, -(x.record.cited_by_count or 0)))

        # Perkaya kandidat terpilih melalui Engine DOI 2-Lapis penuh (Unpaywall + Crossref + S2 + EPMC + Preprint)
        for cand in nat_pool[:n_national]:
            if cand.record.doi:
                cand.record = engine.resolve(cand.record.doi)
            result.national.append(cand)
        for cand in intl_pool[:n_international]:
            if cand.record.doi:
                cand.record = engine.resolve(cand.record.doi)
            result.international.append(cand)

    all_records: List[de.PaperRecord] = list(result.direct_doi_records) + [
        c.record for c in (result.national + result.international)
    ]
    if out_dir and all_records:
        result.bundle_info = de.export_bundle(
            all_records,
            out_dir=out_dir,
            style=citation_style,
            download_pdf=download_pdf,
            make_zip=True,
            topic_label=topic or "Koleksi Riset DOI",
            engine=engine,
        )
    return result


def main(argv: Optional[List[str]] = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(description="MuZA Searching Paper v2.0 (Terhubung ke Engine DOI 2-Lapis)")
    parser.add_argument("--topik", default="", help="Topik / kata kunci riset")
    parser.add_argument("--doi", action="append", default=[], help="DOI atau daftar DOI (dapat diulang)")
    parser.add_argument("--nasional", type=int, default=5, help="Target kuota paper Nasional")
    parser.add_argument("--internasional", type=int, default=5, help="Target kuota paper Internasional")
    parser.add_argument("--tahun-dari", type=int, default=0)
    parser.add_argument("--tahun-sampai", type=int, default=0)
    parser.add_argument("--oa-only", action="store_true", help="Hanya ambil paper Open Access")
    parser.add_argument("--style", default="APA 7th", help="APA 7th | IEEE | Harvard | Vancouver")
    parser.add_argument("--download-pdf", action="store_true", help="Unduh PDF Open Access legal")
    parser.add_argument("--out", default="", help="Folder output bundel .zip siap Auto-Template")
    args = parser.parse_args(argv)

    if not args.topik.strip() and not args.doi:
        parser.print_help()
        return 2
    out_dir = args.out or de.default_output_dir()
    res = search_papers(
        topic=args.topik,
        dois=args.doi,
        n_national=args.nasional,
        n_international=args.internasional,
        year_from=args.tahun_dari,
        year_to=args.tahun_sampai,
        oa_only=args.oa_only,
        citation_style=args.style,
        out_dir=out_dir,
        download_pdf=args.download_pdf,
    )
    print(f"✅ Selesai: {len(res.direct_doi_records)} DOI langsung · "
          f"{len(res.national)} Nasional · {len(res.international)} Internasional")
    if res.bundle_info.get("zip_path"):
        print(f"🗜️ Paket siap Auto-Template: {res.bundle_info['zip_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
