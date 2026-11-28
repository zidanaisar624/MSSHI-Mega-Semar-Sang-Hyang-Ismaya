#!/usr/bin/env python3
"""
doi_engine.py — Engine Riset Akademik 2-Lapis untuk Bot Val (MSSHI / MuZA Project).

Cukup tempel DOI, URL DOI, ID arXiv, PMID, daftar DOI, atau judul/kata kunci di chat/CLI/Web.
Engine mengembalikan metadata lengkap, abstrak, metrik & sampel sitasi, ekstraksi sintesis Bab 2,
format daftar pustaka (APA 7th, IEEE, Harvard, Vancouver) bebas placeholder, serta tautan PDF
Open Access yang 100% LEGAL.

Arsitektur 2-Lapis:
1. Lapisan 1 — Jalur Open Access Gratis (Aktif Otomatis Tanpa API Key):
   - OpenAlex API (singleton DOI $0 gratis, pencarian karya, & graf sitasi)
   - Unpaywall REST API v2 (status OA berbasis DOI & best_oa_location PDF)
   - Crossref REST API (metadata resmi penerbit, volume/issue/halaman/ISSN/referensi)
   - Semantic Scholar Graph API (abstrak, TLDR, citationCount, openAccessPdf)
   - arXiv Atom API (metadata & PDF pra-cetak fisika/komputasi/matematika)
   - NCBI PubMed E-utilities + Europe PMC REST API (abstrak biomedis, PMID/PMCID & PDF OA)
   - Internet Archive Scholar / Fatcat API (salinan arsip OA legal di web.archive.org)
   - Green-OA / Preprint Resolver (mencari versi preprint/repositori legal berjudul & penulis sama
     ketika DOI jurnal utama terkunci paywall)
2. Lapisan 2 — Jalur API Resmi Penerbit (BYOK Opsional):
   - Elsevier Developer API (Scopus Search, Scopus Abstract Retrieval, ScienceDirect Entitlement
     & Full-Text XML/PDF via X-ELS-APIKey dan X-ELS-Insttoken kampus, lengkap pelacak kuota 7 hari).

Prinsip Keamanan & Kepatuhan:
- Hanya menggunakan sumber legal. Situs bayangan/pembajakan (termasuk sci-hub.box, LibGen, Z-Lib)
  diblokir untuk koneksi keluar maupun tautan unduhan. Bila pengguna menempel URL sci-hub yang
  mengandung DOI, engine otomatis mengekstrak DOI-nya saja (tanpa menghubungi sci-hub) dan mencari
  salinan legal + daftar jalur alternatif resmi.
- Ramah Windows 10/11 RAM 4 GB: murni Python stdlib (0 dependensi berat), unduhan PDF di-stream
  per 64 KB ke disk, ukuran respons JSON dibatasi, cache disk dipangkas otomatis (LRU <= 300 file),
  dan memakai threading.Lock (aman lintas thread/loop).
"""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import dataclasses
import difflib
import getpass
import hashlib
import html
import ipaddress
import json
import os
import re
import socket
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional

__version__ = "1.2.0"

# Domain pembajakan / shadow library yang mendistribusikan karya berhak cipta tanpa izin.
# Tidak pernah dihubungi ataupun direkomendasikan oleh engine.
PIRACY_HOST_MARKERS = (
    "sci-hub", "scihub", "sci-hub.box", "sci-hub.se", "sci-hub.st", "sci-hub.ru",
    "libgen", "library.lol", "z-lib", "zlibrary", "singlelogin", "annas-archive",
    "dokumen.pub", "pdfcoffee", "epdf.pub", "vdoc.pub", "ebin.pub", "doku.pub",
    "idoc.pub", "kupdf", "documents.pub", "dokumen.tips", "fdocuments", "pdfdrive",
    "123dok", "pdfroom", "pdfslide", "vdocuments", "pdfcookie", "dokumen.site",
    "booksc", "bookfi", "b-ok",
)

DOI_RE = re.compile(r"\b(10\.\d{4,9}/[^\s\"'<>{}|\\^`\[\]]+)", re.I)
ARXIV_RE = re.compile(
    r"(?:arxiv[:\s/]*|arxiv\.org/(?:abs|pdf)/|10\.48550/arxiv\.)"
    r"(\d{4}\.\d{4,5}(?:v\d+)?|[a-z\-]+(?:\.[A-Z]{2})?/\d{7})",
    re.I,
)
PMID_RE = re.compile(r"(?:pmid[:\s]*|pubmed\.ncbi\.nlm\.nih\.gov/)(\d{5,9})", re.I)

MAX_JSON_BYTES = 6 * 1024 * 1024
MAX_PDF_BYTES = 60 * 1024 * 1024
CACHE_TTL_SECONDS = 7 * 24 * 3600
MAX_CACHE_FILES = 300
DEFAULT_TIMEOUT = 18

_CACHE_LOCK = threading.Lock()

ENV_KEYS: Dict[str, tuple[str, ...]] = {
    "email": ("MSSHI_RESEARCH_EMAIL", "UNPAYWALL_EMAIL"),
    "openalex_api_key": ("OPENALEX_API_KEY",),
    "s2_api_key": ("S2_API_KEY", "SEMANTIC_SCHOLAR_API_KEY"),
    "elsevier_api_key": ("ELSEVIER_API_KEY", "ELS_API_KEY"),
    "elsevier_insttoken": ("ELSEVIER_INSTTOKEN", "ELS_INSTTOKEN"),
    "ncbi_api_key": ("NCBI_API_KEY",),
}


# ----------------------------------------------------------------------------- path adaptif

def data_home() -> str:
    """Folder data adaptif ramah C:-only maupun D:: $HERMES_HOME > D:\\HermesData > ~/HermesData."""
    env = os.environ.get("HERMES_HOME", "").strip()
    if env:
        return env
    if os.name == "nt" and os.path.isdir("D:\\"):
        d_home = "D:\\HermesData"
        if os.path.isdir(d_home) or os.access("D:\\", os.W_OK):
            return d_home
    return os.path.join(os.path.expanduser("~"), "HermesData")


def default_state_dir() -> str:
    return os.path.join(data_home(), "val-research")


def default_output_dir() -> str:
    if os.path.isdir("/content"):
        return "/content/Val_Research_hasil"
    return os.path.join(data_home(), "Val_Research_Output")


# ----------------------------------------------------------------------------- model data terstruktur

@dataclass
class Author:
    given: str = ""
    family: str = ""
    full: str = ""
    orcid: str = ""
    affiliation: str = ""

    def display(self) -> str:
        if self.full:
            return self.full
        return " ".join(x for x in (self.given, self.family) if x).strip()


@dataclass
class OALink:
    url: str
    kind: str            # "pdf" | "landing"
    source: str          # "Unpaywall" | "OpenAlex" | "Semantic Scholar" | "Europe PMC" | "PubMed" | "arXiv" | "Internet Archive" | "Green-OA Preprint"
    version: str = ""    # "publishedVersion" | "acceptedVersion" | "submittedVersion"
    license: str = ""
    host_type: str = ""  # "publisher" | "repository"
    note: str = ""


@dataclass
class RelatedWork:
    title: str
    doi: str = ""
    year: Optional[int] = None
    cited_by_count: int = 0
    openalex_id: str = ""
    is_oa: bool = False
    pdf_url: str = ""


@dataclass
class LegalAlternative:
    label: str
    url: str
    note: str = ""


@dataclass
class Bab2SynthesisRow:
    penulis_tahun: str
    judul_jurnal: str
    metode: str
    dataset_sampel: str
    hasil_metrik: str
    sitasi_intext: str
    doi: str = ""


@dataclass
class Citation:
    style: str
    text: str
    intext: str
    segments: List[Dict[str, Any]]  # [{"text": str, "italic": bool}]


@dataclass
class PaperRecord:
    query: str
    doi: str = ""
    title: str = ""
    authors: List[Author] = field(default_factory=list)
    year: Optional[int] = None
    published_date: str = ""
    venue: str = ""
    publisher: str = ""
    volume: str = ""
    issue: str = ""
    first_page: str = ""
    last_page: str = ""
    article_number: str = ""
    issn: str = ""
    work_type: str = ""
    language: str = ""
    abstract: str = ""
    abstract_source: str = ""
    tldr: str = ""
    keywords: List[str] = field(default_factory=list)
    cited_by_count: int = 0
    reference_count: int = 0
    openalex_id: str = ""
    arxiv_id: str = ""
    pmid: str = ""
    pmcid: str = ""
    is_oa: bool = False
    oa_status: str = ""
    best_pdf_url: str = ""
    best_pdf_source: str = ""
    landing_url: str = ""
    oa_links: List[OALink] = field(default_factory=list)
    references: List[RelatedWork] = field(default_factory=list)
    citing_sample: List[RelatedWork] = field(default_factory=list)
    publisher_access: Dict[str, Any] = field(default_factory=dict)
    legal_alternatives: List[LegalAlternative] = field(default_factory=list)
    field_sources: Dict[str, str] = field(default_factory=dict)
    sources_used: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    found: bool = False

    @property
    def doi_url(self) -> str:
        return f"https://doi.org/{self.doi}" if self.doi else ""

    @property
    def pages(self) -> str:
        if self.first_page and self.last_page and self.first_page != self.last_page:
            return f"{self.first_page}–{self.last_page}"
        return self.first_page or self.article_number or ""

    def to_dict(self) -> Dict[str, Any]:
        d = dataclasses.asdict(self)
        d["doi_url"] = self.doi_url
        d["pages"] = self.pages
        d["citations_formatted"] = {
            "apa": format_citation(self, "APA 7th").text,
            "ieee": format_citation(self, "IEEE", 1).text,
            "harvard": format_citation(self, "Harvard").text,
            "vancouver": format_citation(self, "Vancouver", 1).text,
        }
        d["bab2_synthesis"] = dataclasses.asdict(extract_bab2_row(self))
        return d

    def to_ris_record(self) -> Dict[str, Any]:
        """Kompatibel langsung dengan parse_ris_text() di build_template.py (Auto-Template)."""
        authors = []
        for a in self.authors:
            if a.family and a.given:
                authors.append(f"{a.family}, {a.given}".strip())
            elif a.display():
                authors.append(a.display())
        return {
            "type": _ris_type(self.work_type),
            "authors": authors,
            "keywords": list(self.keywords),
            "title": self.title,
            "year": str(self.year) if self.year else "",
            "journal": self.venue,
            "publisher": self.publisher,
            "volume": self.volume,
            "issue": self.issue,
            "sp": self.first_page or self.article_number,
            "ep": self.last_page,
            "issn": self.issn,
            "doi": self.doi,
            "url": self.doi_url or self.best_pdf_url or self.landing_url,
            "abstract": self.abstract,
        }


@dataclass
class EngineConfig:
    email: str = ""
    openalex_api_key: str = ""
    s2_api_key: str = ""
    elsevier_api_key: str = ""
    elsevier_insttoken: str = ""
    ncbi_api_key: str = ""
    timeout: int = DEFAULT_TIMEOUT
    use_cache: bool = True
    discover_preprints: bool = True
    state_dir: str = field(default_factory=default_state_dir)
    max_related: int = 10

    @property
    def keys_path(self) -> str:
        return os.path.join(self.state_dir, "keys.json")

    @property
    def onboarding_flag_path(self) -> str:
        return os.path.join(self.state_dir, "onboarding_state.json")

    @property
    def cache_dir(self) -> str:
        return os.path.join(self.state_dir, "cache")

    @property
    def layer2_enabled(self) -> bool:
        return bool(self.elsevier_api_key)

    def masked_status(self) -> Dict[str, str]:
        return {
            "email (Unpaywall)": _mask(self.email, keep=3) if self.email else "— (opsional; isi email agar Unpaywall v2 ikut aktif)",
            "OpenAlex API key": _mask(self.openalex_api_key) if self.openalex_api_key else "— (opsional; singleton DOI tetap $0 gratis)",
            "Semantic Scholar key": _mask(self.s2_api_key) if self.s2_api_key else "— (opsional)",
            "Elsevier API key": _mask(self.elsevier_api_key) if self.elsevier_api_key else "— (Lapisan 2 BYOK nonaktif)",
            "Elsevier InstToken": _mask(self.elsevier_insttoken) if self.elsevier_insttoken else "— (opsional, dari perpustakaan kampus)",
            "NCBI PubMed API key": _mask(self.ncbi_api_key) if self.ncbi_api_key else "— (opsional; menaikkan batas 3→10 req/dtk)",
        }


@dataclass
class HttpResult:
    status: int
    data: Any = None
    headers: Dict[str, str] = field(default_factory=dict)
    error: str = ""

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300 and self.data is not None


@dataclass
class DownloadResult:
    ok: bool
    path: str = ""
    url: str = ""
    size: int = 0
    message: str = ""


# ----------------------------------------------------------------------------- utilitas dasar

def _mask(value: str, keep: int = 4) -> str:
    # Redaksi sebelum pemotongan agar prefix token pendek tidak pernah bocor (aturan cindy-code-review).
    value = str(value or "").strip()
    if not value:
        return ""
    if "@" in value:
        user, _, dom = value.partition("@")
        u_mask = (user[:2] + "***") if len(user) > 2 else "***"
        return f"{u_mask}@{dom}"
    if len(value) <= keep * 2 + 2:
        return "*" * min(len(value), 8)
    return f"{value[:keep]}…{value[-keep:]}"


def _clean(text: Any) -> str:
    if text is None:
        return ""
    if isinstance(text, list):
        text = " ".join(str(x) for x in text if x) if len(text) <= 2 else str(text[0])
    text = html.unescape(str(text))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _year(value: Any) -> Optional[int]:
    m = re.search(r"(1[5-9]\d{2}|20\d{2})", str(value or ""))
    return int(m.group(1)) if m else None


def _ris_type(work_type: str) -> str:
    t = (work_type or "").lower()
    if "book-chapter" in t or t == "chapter":
        return "CHAP"
    if "book" in t:
        return "BOOK"
    if "proceedings" in t or "conference" in t:
        return "CPAPER"
    if "dissertation" in t or "thesis" in t:
        return "THES"
    if "preprint" in t or "posted-content" in t:
        return "UNPB"
    return "JOUR"


def normalize_doi(raw: str) -> str:
    """Ekstrak & normalisasi DOI dari string, URL penerbit, ataupun URL pembungkus."""
    if not raw:
        return ""
    text = urllib.parse.unquote(str(raw).strip())
    m = DOI_RE.search(text)
    if not m:
        return ""
    doi = m.group(1).rstrip(".,;:)]}>\"'")
    doi = re.sub(r"(/(full|pdf|abstract|epdf|fulltext|html|meta| citation))+$", "", doi, flags=re.I)
    return doi.lower()


def extract_identifiers(text: str) -> List[str]:
    """Pecah teks hasil copy-paste percakapan menjadi daftar DOI, arXiv, PMID, atau kueri judul."""
    if not text:
        return []
    found: List[str] = []
    for m in DOI_RE.finditer(text):
        d = normalize_doi(m.group(1))
        if d and d not in found:
            found.append(d)
    for m in ARXIV_RE.finditer(text):
        aid = m.group(1)
        tag = f"arxiv:{aid}"
        if tag not in found and not any(aid.lower() in f.lower() for f in found):
            found.append(tag)
    for m in PMID_RE.finditer(text):
        pid = f"pmid:{m.group(1)}"
        if pid not in found:
            found.append(pid)
    if found:
        return found
    parts = [p.strip() for p in re.split(r"[\n;]+", text) if p.strip() and not is_piracy_url(p.strip())]
    return parts


def is_piracy_url(url: str) -> bool:
    raw = str(url or "").strip().lower()
    if not raw:
        return False
    try:
        host = urllib.parse.urlparse(raw if "://" in raw else f"http://{raw}").netloc.lower()
    except ValueError:
        host = raw
    return any(marker in host for marker in PIRACY_HOST_MARKERS)


def _is_public_http_url(url: str) -> bool:
    """Validasi anti-SSRF & blokir domain pembajakan sebelum melakukan koneksi keluar."""
    if is_piracy_url(url):
        return False
    try:
        parts = urllib.parse.urlparse(url)
    except ValueError:
        return False
    if parts.scheme not in ("http", "https") or not parts.hostname:
        return False
    host = parts.hostname.lower()
    if host in ("localhost",) or host.endswith((".local", ".internal")):
        return False
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False
    for info in infos:
        try:
            ip = ipaddress.ip_address(info[4][0])
        except ValueError:
            return False
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            return False
    return True


def _title_key(title: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", (title or "").lower()).strip()


def title_similarity(a: str, b: str) -> float:
    ka, kb = re.sub(r"\s+", " ", _title_key(a)), re.sub(r"\s+", " ", _title_key(b))
    if not ka or not kb:
        return 0.0
    return difflib.SequenceMatcher(None, ka, kb).ratio()


def _split_name(full: str) -> Author:
    full = _clean(full)
    if not full:
        return Author()
    if "," in full:
        family, given = [x.strip() for x in full.split(",", 1)]
        return Author(given=given, family=family, full=f"{given} {family}".strip())
    parts = full.split()
    if len(parts) == 1:
        return Author(family=parts[0], full=full)
    return Author(given=" ".join(parts[:-1]), family=parts[-1], full=full)


def abstract_from_inverted_index(inv: Optional[Dict[str, List[int]]]) -> str:
    if not inv or not isinstance(inv, dict):
        return ""
    slots: Dict[int, str] = {}
    for word, positions in inv.items():
        if isinstance(positions, list):
            for pos in positions:
                if isinstance(pos, int) and 0 <= pos < 20000:
                    slots[pos] = str(word)
    return " ".join(slots[i] for i in sorted(slots))


# ----------------------------------------------------------------------------- konfigurasi & onboarding Val

def load_config(**overrides: Any) -> EngineConfig:
    """Urutan prioritas: argumen eksplisit > environment variable > keys.json lokal (di luar repo)."""
    cfg = EngineConfig()
    state_dir = overrides.get("state_dir") or cfg.state_dir
    cfg.state_dir = str(state_dir)
    stored: Dict[str, str] = {}
    try:
        with open(cfg.keys_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        if isinstance(raw, dict):
            stored = {k: str(v) for k, v in raw.items() if isinstance(v, (str, int))}
    except (OSError, ValueError):
        stored = {}
    for attr, env_names in ENV_KEYS.items():
        val = stored.get(attr, "")
        for env in env_names:
            if os.environ.get(env, "").strip():
                val = os.environ[env].strip()
                break
        if overrides.get(attr):
            val = str(overrides[attr]).strip()
        setattr(cfg, attr, val)
    for attr in ("timeout", "use_cache", "max_related", "discover_preprints"):
        if attr in overrides and overrides[attr] is not None:
            setattr(cfg, attr, overrides[attr])
    if cfg.email and not re.match(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$", cfg.email, re.I):
        cfg.email = ""
    return cfg


def save_keys(cfg: EngineConfig, values: Dict[str, str], skipped: bool = False) -> str:
    """Simpan key riset ke HermesData/val-research/keys.json (100% di luar repo Git)."""
    os.makedirs(cfg.state_dir, exist_ok=True)
    current: Dict[str, str] = {}
    try:
        with open(cfg.keys_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            if isinstance(raw, dict):
                current = {str(k): str(v) for k, v in raw.items()}
    except (OSError, ValueError):
        current = {}
    for k, v in values.items():
        if k not in ENV_KEYS:
            continue
        if v and str(v).strip():
            current[k] = str(v).strip()
        elif v == "":
            current.pop(k, None)
    tmp = cfg.keys_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2)
    os.replace(tmp, cfg.keys_path)
    try:
        os.chmod(cfg.keys_path, 0o600)
    except OSError:
        pass
    mark_onboarding_done(cfg, mode="skipped_layer1" if skipped else "configured")
    return cfg.keys_path


def is_onboarding_done(cfg: Optional[EngineConfig] = None) -> bool:
    cfg = cfg or load_config()
    return os.path.isfile(cfg.onboarding_flag_path) or os.path.isfile(cfg.keys_path)


def mark_onboarding_done(cfg: Optional[EngineConfig] = None, mode: str = "skipped_layer1") -> str:
    cfg = cfg or load_config()
    os.makedirs(cfg.state_dir, exist_ok=True)
    payload = {"completed": True, "mode": mode, "updated_epoch": int(time.time())}
    tmp = cfg.onboarding_flag_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, cfg.onboarding_flag_path)
    return cfg.onboarding_flag_path


ONBOARDING_TEXT = """\
Halo! Aku Val, pemimpin riset akademik MSSHI 🔬
Pertanyaan singkat sebelum mulai (OPSIONAL — cukup 1x):
Apakah kamu memiliki API key riset akademik yang ingin dihubungkan?

  • Ketik "Lewati" (Rekomendasi Cepat) → langsung jalan memakai LAPISAN 1 GRATIS:
    OpenAlex · Unpaywall · Crossref · Semantic Scholar · arXiv · PubMed/Europe PMC · IA Scholar.

  • Atau isi salah satu yang kamu punya untuk kuota/akses ekstra:
    [1] Email Aktif untuk Unpaywall (gratis, tanpa daftar akun)
        → mengaktifkan Unpaywall REST API v2 (100.000 cek OA/hari).
    [2] OpenAlex API Key (gratis, daftar 30 detik di https://openalex.org/settings/api)
        → menaikkan kuota harian 10x ($1/hari kredit gratis; singleton lookup DOI tetap $0).
    [3] Elsevier Developer API Key — LAPISAN 2 BYOK (https://dev.elsevier.com → My API Key)
        → menghubungkan Scopus Search (kuota 20.000/minggu) & Abstract Retrieval (10.000/minggu).
        Catatan: abstrak penuh Scopus & full-text XML ScienceDirect memerlukan jaringan IP kampus
        yang berlangganan atau InstToken resmi dari perpustakaan kampusmu.
    [4] Elsevier InstToken (opsional, minta ke perpustakaan kampus bila bekerja dari luar kampus).
    [5] Semantic Scholar / NCBI PubMed API Key (opsional, menaikkan rate limit).

Lokasi simpan aman (lokal, tidak pernah masuk GitHub): {keys_path}
"""


def onboarding_text(cfg: Optional[EngineConfig] = None) -> str:
    cfg = cfg or load_config()
    return ONBOARDING_TEXT.format(keys_path=cfg.keys_path)


# ----------------------------------------------------------------------------- HTTP + cache hemat RAM

Fetcher = Callable[[str, Dict[str, str], int], HttpResult]


def _cache_path(cfg: EngineConfig, url: str) -> str:
    safe = re.sub(r"(api_key|email|mailto|apiKey|insttoken)=[^&]*", r"\1=*", url, flags=re.I)
    return os.path.join(cfg.cache_dir, hashlib.sha1(safe.encode("utf-8")).hexdigest() + ".json")


def _prune_cache_if_needed(cache_dir: str) -> None:
    with _CACHE_LOCK:
        try:
            entries = [os.path.join(cache_dir, fn) for fn in os.listdir(cache_dir) if fn.endswith(".json")]
            if len(entries) <= MAX_CACHE_FILES:
                return
            entries.sort(key=lambda p: os.path.getmtime(p))
            for old in entries[: len(entries) - MAX_CACHE_FILES]:
                try:
                    os.remove(old)
                except OSError:
                    pass
        except OSError:
            pass


def default_fetcher(url: str, headers: Dict[str, str], timeout: int) -> HttpResult:
    if is_piracy_url(url):
        return HttpResult(status=451, error="Diblokir oleh kebijakan legal MSSHI (situs pembajakan).")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(MAX_JSON_BYTES + 1)
            hdrs = {k.lower(): v for k, v in resp.headers.items()}
            if len(body) > MAX_JSON_BYTES:
                return HttpResult(status=413, headers=hdrs, error="respons melebihi batas aman RAM (6 MB)")
            ctype = hdrs.get("content-type", "")
            text = body.decode("utf-8", errors="replace")
            if "json" in ctype or text.lstrip().startswith(("{", "[")):
                return HttpResult(status=resp.status, data=json.loads(text), headers=hdrs)
            return HttpResult(status=resp.status, data=text, headers=hdrs)
    except urllib.error.HTTPError as e:
        hdrs = {k.lower(): v for k, v in (e.headers or {}).items()}
        return HttpResult(status=e.code, headers=hdrs, error=f"HTTP {e.code}")
    except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError, ValueError) as e:
        return HttpResult(status=0, error=str(getattr(e, "reason", e))[:160])


class ResearchEngine:
    """Orkestrator riset DOI & literatur 2-lapis. `fetcher` dapat di-stub untuk tes offline deterministik."""

    def __init__(self, config: Optional[EngineConfig] = None, fetcher: Optional[Fetcher] = None):
        self.cfg = config or load_config()
        self._fetch = fetcher or default_fetcher
        ua = f"MSSHI-Val-DOI-Engine/{__version__} (+https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya"
        self.user_agent = ua + (f"; mailto:{self.cfg.email})" if self.cfg.email else ")")

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cache: bool = True,
        retries: int = 1,
    ) -> HttpResult:
        if params:
            clean_p = {k: v for k, v in params.items() if v not in (None, "")}
            if clean_p:
                url = f"{url}{'&' if '?' in url else '?'}{urllib.parse.urlencode(clean_p)}"
        hdrs = {"User-Agent": self.user_agent, "Accept": "application/json"}
        hdrs.update(headers or {})
        cpath = _cache_path(self.cfg, url)
        if cache and self.cfg.use_cache:
            try:
                if time.time() - os.path.getmtime(cpath) < CACHE_TTL_SECONDS:
                    with open(cpath, "r", encoding="utf-8") as f:
                        return HttpResult(status=200, data=json.load(f), headers={"x-cache": "hit"})
            except (OSError, ValueError):
                pass
        res = HttpResult(status=0, error="belum dicoba")
        for attempt in range(retries + 1):
            res = self._fetch(url, hdrs, self.cfg.timeout)
            if res.status in (429, 500, 502, 503, 504) and attempt < retries:
                wait = min(5.0, float(res.headers.get("retry-after", 0) or 0) or (1.2 * (attempt + 1)))
                time.sleep(wait)
                continue
            break
        if res.ok and cache and self.cfg.use_cache and isinstance(res.data, (dict, list)):
            try:
                os.makedirs(self.cfg.cache_dir, exist_ok=True)
                tmp = f"{cpath}.{threading.get_ident()}.tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(res.data, f)
                os.replace(tmp, cpath)
                _prune_cache_if_needed(self.cfg.cache_dir)
            except OSError:
                pass
        return res

    # ------------------------------------------------------------------ Lapisan 1 — Konektor OA Legal
    def _openalex_params(self, extra: Dict[str, Any]) -> Dict[str, Any]:
        # OpenAlex mendeprekasi parameter mailto; kirim api_key bila tersedia.
        p = dict(extra)
        if self.cfg.openalex_api_key:
            p["api_key"] = self.cfg.openalex_api_key
        return p

    OPENALEX_SELECT = (
        "id,doi,display_name,publication_year,publication_date,type,language,authorships,"
        "primary_location,best_oa_location,locations,open_access,biblio,cited_by_count,"
        "referenced_works,abstract_inverted_index,ids,keywords"
    )

    def openalex_work(self, doi: str) -> Optional[Dict[str, Any]]:
        r = self.get(
            f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi, safe='/')}",
            self._openalex_params({"select": self.OPENALEX_SELECT}),
        )
        return r.data if r.ok and isinstance(r.data, dict) else None

    def unpaywall(self, doi: str) -> Optional[Dict[str, Any]]:
        if not self.cfg.email:
            return None
        r = self.get(f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi, safe='/')}", {"email": self.cfg.email})
        return r.data if r.ok and isinstance(r.data, dict) else None

    def crossref_work(self, doi: str) -> Optional[Dict[str, Any]]:
        r = self.get(
            f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='/')}",
            {"mailto": self.cfg.email} if self.cfg.email else None,
        )
        if r.ok and isinstance(r.data, dict):
            return r.data.get("message")
        return None

    S2_FIELDS = (
        "title,abstract,year,venue,authors,citationCount,referenceCount,openAccessPdf,"
        "externalIds,publicationTypes,journal,publicationDate,tldr"
    )

    def semantic_scholar(self, ident: str) -> Optional[Dict[str, Any]]:
        headers = {"x-api-key": self.cfg.s2_api_key} if self.cfg.s2_api_key else None
        r = self.get(
            f"https://api.semanticscholar.org/graph/v1/paper/{urllib.parse.quote(ident, safe=':/')}",
            {"fields": self.S2_FIELDS},
            headers=headers,
            retries=0,
        )
        return r.data if r.ok and isinstance(r.data, dict) else None

    def europepmc(self, query: str) -> Optional[Dict[str, Any]]:
        r = self.get(
            "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
            {"query": query, "resultType": "core", "format": "json", "pageSize": 1},
        )
        if r.ok and isinstance(r.data, dict):
            results = (r.data.get("resultList") or {}).get("result") or []
            return results[0] if results else None
        return None

    def pubmed_by_pmid_or_doi(self, pmid: str = "", doi: str = "") -> Optional[Dict[str, Any]]:
        """Konektor resmi NCBI PubMed E-utilities (esearch + efetch XML + PMC OA link)."""
        base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        common: Dict[str, Any] = {"tool": "msshi_val_doi", "email": self.cfg.email or None,
                                  "api_key": self.cfg.ncbi_api_key or None}
        if not pmid and doi:
            sr = self.get(f"{base}/esearch.fcgi", {**common, "db": "pubmed", "term": f"{doi}[AID]", "retmode": "json"})
            if sr.ok and isinstance(sr.data, dict):
                idlist = ((sr.data.get("esearchresult") or {}).get("idlist") or [])
                pmid = idlist[0] if idlist else ""
        if not pmid:
            return None
        fr = self.get(f"{base}/efetch.fcgi", {**common, "db": "pubmed", "id": pmid, "retmode": "xml"},
                      headers={"Accept": "application/xml,text/xml"})
        if not (fr.status == 200 and isinstance(fr.data, str)):
            return None
        return parse_pubmed_xml(fr.data, fallback_pmid=pmid)

    def fatcat_ia_scholar(self, doi: str) -> Optional[Dict[str, Any]]:
        """Internet Archive Scholar (Fatcat) — salinan arsip jurnal OA legal yang dilestarikan."""
        r = self.get(
            "https://api.fatcat.wiki/v0/release/lookup",
            {"doi": doi, "expand": "files,container"},
            retries=0,
        )
        return r.data if r.ok and isinstance(r.data, dict) else None

    def arxiv(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        r = self.get(
            "https://export.arxiv.org/api/query",
            {"id_list": arxiv_id, "max_results": 1},
            headers={"Accept": "application/atom+xml"},
        )
        if not (r.status == 200 and isinstance(r.data, str)):
            return None
        return parse_arxiv_atom(r.data)

    def _discover_green_oa_version(self, rec: PaperRecord) -> None:
        """Cari versi preprint / accepted manuscript legal untuk karya yang DOI penerbitnya terkunci."""
        if rec.best_pdf_url or not rec.title or len(rec.title) < 12:
            return
        first_family = (rec.authors[0].family or rec.authors[0].display().split()[-1]).lower() if rec.authors else ""
        # 1) Cari versi OA lain di OpenAlex dengan judul sama
        r = self.get(
            "https://api.openalex.org/works",
            self._openalex_params({
                "search": rec.title[:160],
                "filter": "is_oa:true",
                "per_page": 5,
                "select": "id,doi,display_name,authorships,best_oa_location,open_access",
            }),
        )
        if r.ok and isinstance(r.data, dict):
            for cand in r.data.get("results") or []:
                sim = title_similarity(rec.title, cand.get("display_name", ""))
                if sim < 0.88:
                    continue
                cand_authors = " ".join(
                    ((a.get("author") or {}).get("display_name") or "").lower()
                    for a in (cand.get("authorships") or [])
                )
                if first_family and first_family not in cand_authors:
                    continue
                loc = cand.get("best_oa_location") or {}
                pdf_u = loc.get("pdf_url") or (cand.get("open_access") or {}).get("oa_url") or ""
                if pdf_u and not is_piracy_url(pdf_u):
                    rec.oa_links.append(OALink(
                        url=pdf_u,
                        kind="pdf",
                        source="Green-OA Preprint (OpenAlex)",
                        version=loc.get("version") or "submittedVersion",
                        license=loc.get("license") or "",
                        host_type="repository",
                        note="Versi repositori/preprint legal dari penulis yang sama",
                    ))
                    return
        # 2) Cari preprint di arXiv berdasarkan judul & penulis pertama
        q_parts = [f'ti:"{re.sub(r"[^A-Za-z0-9 ]+", " ", rec.title)[:90].strip()}"']
        if first_family:
            q_parts.append(f"au:{first_family}")
        ar = self.get(
            "https://export.arxiv.org/api/query",
            {"search_query": " AND ".join(q_parts), "max_results": 3},
            headers={"Accept": "application/atom+xml"},
            retries=0,
        )
        if ar.status == 200 and isinstance(ar.data, str):
            parsed = parse_arxiv_atom(ar.data)
            if parsed and parsed.get("pdf") and title_similarity(rec.title, parsed.get("title", "")) >= 0.88:
                rec.oa_links.append(OALink(
                    url=parsed["pdf"],
                    kind="pdf",
                    source="Green-OA Preprint (arXiv)",
                    version="submittedVersion",
                    host_type="repository",
                    note=f"arXiv:{parsed.get('id', '')}",
                ))
                if not rec.arxiv_id and parsed.get("id"):
                    rec.arxiv_id = parsed["id"]

    # ------------------------------------------------------------------ Lapisan 2 — Elsevier BYOK
    def _elsevier_headers(self) -> Dict[str, str]:
        h = {"X-ELS-APIKey": self.cfg.elsevier_api_key, "Accept": "application/json"}
        if self.cfg.elsevier_insttoken:
            h["X-ELS-Insttoken"] = self.cfg.elsevier_insttoken
        return h

    def elsevier_search_scopus(self, query: str, count: int = 10) -> Dict[str, Any]:
        """Pencarian resmi Scopus Search API (kuota default: 20.000 request / 7 hari)."""
        if not self.cfg.elsevier_api_key:
            return {"ok": False, "results": [], "message": "Elsevier API key belum dikonfigurasi."}
        r = self.get(
            "https://api.elsevier.com/content/search/scopus",
            {"query": query, "count": max(1, min(count, 25))},
            headers=self._elsevier_headers(),
            cache=False,
            retries=0,
        )
        quota = {
            "limit": r.headers.get("x-ratelimit-limit", ""),
            "remaining": r.headers.get("x-ratelimit-remaining", ""),
            "reset_epoch": r.headers.get("x-ratelimit-reset", ""),
        }
        if not r.ok or not isinstance(r.data, dict):
            return {"ok": False, "status": r.status, "results": [], "quota": quota, "message": r.error or f"HTTP {r.status}"}
        entries = ((r.data.get("search-results") or {}).get("entry") or [])
        items: List[RelatedWork] = []
        for ent in entries:
            if not isinstance(ent, dict) or ent.get("error"):
                continue
            items.append(RelatedWork(
                title=_clean(ent.get("dc:title")),
                doi=normalize_doi(ent.get("prism:doi", "")),
                year=_year(ent.get("prism:coverDate")),
                cited_by_count=_int(ent.get("citedby-count")),
                is_oa=str(ent.get("openaccess", "0")) == "1",
            ))
        return {"ok": True, "status": r.status, "results": items, "quota": quota}

    def elsevier_abstract(self, doi: str) -> Dict[str, Any]:
        r = self.get(
            f"https://api.elsevier.com/content/abstract/doi/{urllib.parse.quote(doi, safe='/')}",
            headers=self._elsevier_headers(),
            cache=False,
            retries=0,
        )
        info: Dict[str, Any] = {
            "status": r.status,
            "quota_limit": r.headers.get("x-ratelimit-limit", ""),
            "quota_remaining": r.headers.get("x-ratelimit-remaining", ""),
            "quota_reset": r.headers.get("x-ratelimit-reset", ""),
        }
        if r.ok and isinstance(r.data, dict):
            core = (r.data.get("abstracts-retrieval-response") or {}).get("coredata") or {}
            info.update({
                "title": _clean(core.get("dc:title")),
                "abstract": _clean(core.get("dc:description")),
                "venue": _clean(core.get("prism:publicationName")),
                "cover_date": core.get("prism:coverDate", ""),
                "volume": core.get("prism:volume", ""),
                "issue": core.get("prism:issueIdentifier", ""),
                "page_range": core.get("prism:pageRange", ""),
                "cited_by_count": _int(core.get("citedby-count")),
                "scopus_id": str(core.get("dc:identifier", "")).replace("SCOPUS_ID:", ""),
                "openaccess": str(core.get("openaccess", "")) == "1",
            })
        elif r.status in (401, 403):
            info["message"] = (
                "API key dikenali tetapi langganan kampus/InstToken dibutuhkan untuk view FULL Scopus "
                "(gunakan jaringan IP kampus atau tambahkan X-ELS-Insttoken)."
            )
        elif r.status == 429:
            info["message"] = "Kuota mingguan Elsevier habis (otomatis reset tiap 7 hari / 168 jam)."
        elif r.status == 404:
            info["message"] = "DOI tidak terdaftar di indeks Scopus."
        else:
            info["message"] = r.error or f"HTTP {r.status}"
        return info

    def elsevier_entitlement(self, doi: str) -> Dict[str, Any]:
        r = self.get(
            f"https://api.elsevier.com/content/article/entitlement/doi/{urllib.parse.quote(doi, safe='/')}",
            headers=self._elsevier_headers(),
            cache=False,
            retries=0,
        )
        info: Dict[str, Any] = {"status": r.status, "entitled": False}
        if r.ok and isinstance(r.data, dict):
            ent = (r.data.get("entitlement-response") or {}).get("document-entitlement") or {}
            info["entitled"] = str(ent.get("entitled", "")).lower() == "true" or ent.get("entitled") is True
            info["link"] = ent.get("link", {}).get("@href", "") if isinstance(ent.get("link"), dict) else ""
        return info

    def elsevier_fulltext(self, doi: str, out_dir: str) -> DownloadResult:
        """Unduh full-text XML ScienceDirect resmi hanya bila entitlement bernilai true."""
        if not self.cfg.elsevier_api_key:
            return DownloadResult(ok=False, message="Elsevier API key belum diisi.")
        ent = self.elsevier_entitlement(doi)
        if not ent.get("entitled"):
            return DownloadResult(ok=False, message="Akun/IP belum ter-entitle untuk full-text ScienceDirect.")
        headers = self._elsevier_headers()
        headers["Accept"] = "text/xml"
        url = f"https://api.elsevier.com/content/article/doi/{urllib.parse.quote(doi, safe='/')}"
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, _safe_filename(doi) + "_sciencedirect.xml")
        return _stream_to_file(url, headers, path, self.cfg.timeout, magic=None)

    # ------------------------------------------------------------------ graf sitasi & pencarian judul
    def citing_works(self, openalex_id: str, limit: int) -> List[RelatedWork]:
        wid = openalex_id.rsplit("/", 1)[-1]
        r = self.get("https://api.openalex.org/works", self._openalex_params({
            "filter": f"cites:{wid}", "per_page": max(1, min(limit, 50)), "sort": "cited_by_count:desc",
            "select": "id,doi,display_name,publication_year,cited_by_count,open_access",
        }))
        return [_related_from_openalex(w) for w in ((r.data or {}).get("results") or [])] if r.ok else []

    def referenced_works(self, work_ids: Iterable[str], limit: int) -> List[RelatedWork]:
        ids = [w.rsplit("/", 1)[-1] for w in work_ids if w][: max(1, min(limit, 50))]
        if not ids:
            return []
        r = self.get("https://api.openalex.org/works", self._openalex_params({
            "filter": "openalex:" + "|".join(ids), "per_page": len(ids),
            "select": "id,doi,display_name,publication_year,cited_by_count,open_access",
        }))
        return [_related_from_openalex(w) for w in ((r.data or {}).get("results") or [])] if r.ok else []

    def search(self, query: str, limit: int = 8) -> List[RelatedWork]:
        out: List[RelatedWork] = []
        seen: set[str] = set()
        r = self.get("https://api.openalex.org/works", self._openalex_params({
            "search": query, "per_page": max(1, min(limit, 25)),
            "select": "id,doi,display_name,publication_year,cited_by_count,open_access",
        }))
        if r.ok and isinstance(r.data, dict):
            for w in r.data.get("results") or []:
                rw = _related_from_openalex(w)
                key = rw.doi or _title_key(rw.title)
                if key and key not in seen:
                    seen.add(key)
                    out.append(rw)
        if self.cfg.layer2_enabled and len(out) < limit:
            sc = self.elsevier_search_scopus(f"TITLE-ABS-KEY({query})", count=min(10, limit))
            for rw in sc.get("results") or []:
                key = rw.doi or _title_key(rw.title)
                if key and key not in seen:
                    seen.add(key)
                    out.append(rw)
        if not out:
            r2 = self.get("https://api.crossref.org/works", {
                "query.bibliographic": query, "rows": max(1, min(limit, 20)),
                "select": "DOI,title,issued,is-referenced-by-count", "mailto": self.cfg.email or None,
            })
            items = ((r2.data or {}).get("message") or {}).get("items") or [] if r2.ok else []
            for it in items:
                out.append(RelatedWork(
                    title=_clean(it.get("title")),
                    doi=normalize_doi(it.get("DOI", "")),
                    year=_year(((it.get("issued") or {}).get("date-parts") or [[None]])[0][0]),
                    cited_by_count=_int(it.get("is-referenced-by-count")),
                ))
        return out[:limit]

    # ------------------------------------------------------------------ resolve utama
    def resolve(self, query: str, with_citations: bool = False, use_layer2: bool = True) -> PaperRecord:
        query = (query or "").strip()
        rec = PaperRecord(query=query)
        if not query:
            rec.warnings.append("Input kosong.")
            return rec
        if is_piracy_url(query):
            extracted_doi = normalize_doi(query)
            rec.warnings.append(
                "Domain pembajakan (mis. sci-hub.box) tidak dihubungi demi kepatuhan hak cipta & keamanan; "
                + (f"DOI '{extracted_doi}' diekstrak otomatis dan dicari lewat jalur Open Access legal."
                   if extracted_doi else "tempelkan kode DOI (10.xxxx/...) atau judul paper secara langsung.")
            )
            if not extracted_doi:
                return rec
            query = extracted_doi

        doi = normalize_doi(query)
        arxiv_id = ""
        m_arx = ARXIV_RE.search(query)
        if m_arx:
            arxiv_id = m_arx.group(1)
        if doi.startswith("10.48550/arxiv."):
            arxiv_id = doi.split("arxiv.", 1)[1]
        pmid = ""
        m_pmid = PMID_RE.search(query)
        if m_pmid and not doi:
            pmid = m_pmid.group(1)

        if not doi and not arxiv_id and not pmid:
            hits = self.search(query, limit=6)
            best = max(hits, key=lambda h: title_similarity(query, h.title), default=None)
            if best and best.doi and title_similarity(query, best.title) >= 0.52:
                doi = best.doi
                rec.warnings.append(
                    f"Dicocokkan dari judul/kata kunci → DOI {doi} (kemiripan judul {title_similarity(query, best.title):.0%})."
                )
            elif hits and hits[0].openalex_id and title_similarity(query, hits[0].title) >= 0.72:
                # Karya ber-OpenAlex tanpa DOI (mis. prosiding/jurnal lokal)
                w_res = self.get(
                    f"https://api.openalex.org/works/{hits[0].openalex_id.rsplit('/', 1)[-1]}",
                    self._openalex_params({"select": self.OPENALEX_SELECT}),
                )
                if w_res.ok and isinstance(w_res.data, dict):
                    self._merge_openalex(rec, w_res.data)
                    self._finalize_oa(rec)
                    return rec
            else:
                rec.citing_sample = hits
                rec.warnings.append("Belum ada satu judul yang cocok kuat; pilih dari kandidat yang ditemukan atau tempel DOI langsung.")
                return rec

        if pmid and not doi:
            pm = self.pubmed_by_pmid_or_doi(pmid=pmid)
            if pm:
                self._merge_pubmed(rec, pm)
                if pm.get("doi"):
                    doi = normalize_doi(pm["doi"])
            if not doi:
                epmc = self.europepmc(f"EXT_ID:{pmid} AND SRC:MED")
                if epmc:
                    self._merge_europepmc(rec, epmc)
                    doi = normalize_doi(epmc.get("doi", ""))

        rec.doi = doi
        rec.arxiv_id = arxiv_id
        if not doi and arxiv_id:
            ax = self.arxiv(arxiv_id)
            if ax:
                self._merge_arxiv(rec, ax)
                if ax.get("doi"):
                    rec.doi = doi = normalize_doi(ax["doi"])

        if not doi and not rec.found:
            rec.warnings.append("Identifier tidak dikenali atau belum terindeks.")
            return rec

        jobs: Dict[str, Callable[[], Any]] = {}
        if doi:
            jobs = {
                "OpenAlex": lambda: self.openalex_work(doi),
                "Crossref": lambda: self.crossref_work(doi),
                "Unpaywall": lambda: self.unpaywall(doi),
                "Semantic Scholar": lambda: self.semantic_scholar(f"DOI:{doi}"),
                "Europe PMC": lambda: self.europepmc(f'DOI:"{doi}"'),
                "Internet Archive": lambda: self.fatcat_ia_scholar(doi),
            }
            if arxiv_id:
                jobs["arXiv"] = lambda: self.arxiv(arxiv_id)

        results: Dict[str, Any] = {}
        if jobs:
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
                futs = {pool.submit(fn): name for name, fn in jobs.items()}
                for fut in concurrent.futures.as_completed(futs):
                    name = futs[fut]
                    try:
                        results[name] = fut.result()
                    except Exception as e:
                        results[name] = None
                        rec.warnings.append(f"{name}: {e.__class__.__name__}")

        if results.get("Crossref"):
            self._merge_crossref(rec, results["Crossref"])
        if results.get("OpenAlex"):
            self._merge_openalex(rec, results["OpenAlex"])
        if results.get("Unpaywall"):
            self._merge_unpaywall(rec, results["Unpaywall"])
        if results.get("Semantic Scholar"):
            self._merge_s2(rec, results["Semantic Scholar"])
        if results.get("Europe PMC"):
            self._merge_europepmc(rec, results["Europe PMC"])
        if results.get("Internet Archive"):
            self._merge_fatcat(rec, results["Internet Archive"])
        if results.get("arXiv"):
            self._merge_arxiv(rec, results["arXiv"])

        # Bila PMID ditemukan (mis. dari OpenAlex/S2) tetapi abstrak masih kosong, tarik langsung dari NCBI PubMed
        if (rec.pmid or (doi and not rec.abstract)) and not results.get("Europe PMC"):
            pm = self.pubmed_by_pmid_or_doi(pmid=rec.pmid, doi=doi)
            if pm:
                self._merge_pubmed(rec, pm)

        if use_layer2 and self.cfg.layer2_enabled and doi:
            self._layer2_elsevier(rec)

        self._finalize_oa(rec)

        # Bila masih belum ada PDF OA pada DOI utama, cari versi Green-OA / preprint legal berjudul & penulis sama
        if self.cfg.discover_preprints and rec.found and not rec.best_pdf_url:
            self._discover_green_oa_version(rec)
            self._finalize_oa(rec)

        if with_citations and rec.openalex_id:
            rec.citing_sample = self.citing_works(rec.openalex_id, self.cfg.max_related)
            if results.get("OpenAlex"):
                rec.references = self.referenced_works(
                    results["OpenAlex"].get("referenced_works") or [],
                    self.cfg.max_related,
                )
        return rec

    # ------------------------------------------------------------------ merge helpers
    def _set(self, rec: PaperRecord, attr: str, value: Any, source: str) -> None:
        if value in (None, "", [], 0) or getattr(rec, attr) not in (None, "", [], 0):
            return
        setattr(rec, attr, value)
        rec.field_sources[attr] = source

    def _used(self, rec: PaperRecord, source: str) -> None:
        rec.found = True
        if source not in rec.sources_used:
            rec.sources_used.append(source)

    def _merge_crossref(self, rec: PaperRecord, m: Dict[str, Any]) -> None:
        self._used(rec, "Crossref")
        self._set(rec, "title", _clean(m.get("title")), "Crossref")
        authors = []
        for a in m.get("author") or []:
            affs = a.get("affiliation") or []
            aff_name = _clean(affs[0].get("name")) if affs and isinstance(affs[0], dict) else ""
            if a.get("family") or a.get("name"):
                authors.append(Author(
                    given=_clean(a.get("given")),
                    family=_clean(a.get("family")) or _clean(a.get("name")),
                    orcid=str(a.get("ORCID", "")).rsplit("/", 1)[-1],
                    affiliation=aff_name,
                ))
        self._set(rec, "authors", authors, "Crossref")
        parts = ((m.get("published") or m.get("issued") or {}).get("date-parts") or [[None]])[0]
        self._set(rec, "year", _year(parts[0] if parts else None), "Crossref")
        if parts and parts[0]:
            self._set(rec, "published_date", "-".join(f"{int(p):02d}" if i else str(p) for i, p in enumerate(parts) if p), "Crossref")
        self._set(rec, "venue", _clean(m.get("container-title")), "Crossref")
        self._set(rec, "publisher", _clean(m.get("publisher")), "Crossref")
        self._set(rec, "volume", _clean(m.get("volume")), "Crossref")
        self._set(rec, "issue", _clean(m.get("issue")), "Crossref")
        self._set(rec, "article_number", _clean(m.get("article-number")), "Crossref")
        page = _clean(m.get("page"))
        if page:
            fp, _, lp = page.replace("–", "-").partition("-")
            self._set(rec, "first_page", fp.strip(), "Crossref")
            self._set(rec, "last_page", lp.strip(), "Crossref")
        self._set(rec, "issn", _clean((m.get("ISSN") or [""])[0]), "Crossref")
        self._set(rec, "work_type", _clean(m.get("type")), "Crossref")
        self._set(rec, "language", _clean(m.get("language")), "Crossref")
        self._set(rec, "reference_count", _int(m.get("reference-count") or m.get("references-count")), "Crossref")
        rec.cited_by_count = max(rec.cited_by_count, _int(m.get("is-referenced-by-count")))
        self._set(rec, "landing_url", _clean((m.get("resource") or {}).get("primary", {}).get("URL")), "Crossref")
        abstract = _clean(m.get("abstract"))
        if abstract and not rec.abstract:
            rec.abstract = re.sub(r"^(abstract|abstrak|summary)\s*[:.\-]?\s*", "", abstract, flags=re.I)
            rec.abstract_source = "Crossref"

    def _merge_openalex(self, rec: PaperRecord, w: Dict[str, Any]) -> None:
        self._used(rec, "OpenAlex")
        rec.openalex_id = rec.openalex_id or str(w.get("id", ""))
        if not rec.doi and w.get("doi"):
            rec.doi = normalize_doi(w["doi"])
        self._set(rec, "title", _clean(w.get("display_name")), "OpenAlex")
        authors = []
        for a in w.get("authorships") or []:
            au = _split_name((a.get("author") or {}).get("display_name", ""))
            au.orcid = str((a.get("author") or {}).get("orcid") or "").rsplit("/", 1)[-1]
            insts = a.get("institutions") or []
            if insts and isinstance(insts[0], dict):
                au.affiliation = _clean(insts[0].get("display_name"))
            if au.display():
                authors.append(au)
        self._set(rec, "authors", authors, "OpenAlex")
        self._set(rec, "year", _int(w.get("publication_year")) or None, "OpenAlex")
        self._set(rec, "published_date", w.get("publication_date") or "", "OpenAlex")
        src = ((w.get("primary_location") or {}).get("source") or {})
        self._set(rec, "venue", _clean(src.get("display_name")), "OpenAlex")
        self._set(rec, "publisher", _clean(src.get("host_organization_name")), "OpenAlex")
        self._set(rec, "issn", _clean(src.get("issn_l")), "OpenAlex")
        b = w.get("biblio") or {}
        self._set(rec, "volume", _clean(b.get("volume")), "OpenAlex")
        self._set(rec, "issue", _clean(b.get("issue")), "OpenAlex")
        self._set(rec, "first_page", _clean(b.get("first_page")), "OpenAlex")
        self._set(rec, "last_page", _clean(b.get("last_page")), "OpenAlex")
        self._set(rec, "work_type", _clean(w.get("type")), "OpenAlex")
        self._set(rec, "language", _clean(w.get("language")), "OpenAlex")
        self._set(rec, "reference_count", len(w.get("referenced_works") or []), "OpenAlex")
        rec.cited_by_count = max(rec.cited_by_count, _int(w.get("cited_by_count")))
        ids = w.get("ids") or {}
        self._set(rec, "pmid", str(ids.get("pmid", "")).rsplit("/", 1)[-1], "OpenAlex")
        self._set(rec, "pmcid", str(ids.get("pmcid", "")).rsplit("/", 1)[-1], "OpenAlex")
        kws = [_clean(k.get("display_name")) for k in (w.get("keywords") or []) if isinstance(k, dict) and k.get("display_name")]
        if kws and not rec.keywords:
            rec.keywords = kws[:10]
        if not rec.abstract:
            ab = abstract_from_inverted_index(w.get("abstract_inverted_index"))
            if ab:
                rec.abstract, rec.abstract_source = ab, "OpenAlex"
        oa = w.get("open_access") or {}
        rec.is_oa = rec.is_oa or bool(oa.get("is_oa"))
        self._set(rec, "oa_status", _clean(oa.get("oa_status")), "OpenAlex")
        self._set(rec, "landing_url", _clean((w.get("primary_location") or {}).get("landing_page_url")), "OpenAlex")
        locs = [w.get("best_oa_location")] + list(w.get("locations") or [])
        for loc in locs:
            if not loc or not loc.get("is_oa", True):
                continue
            host = ((loc.get("source") or {}).get("type") or "")
            if loc.get("pdf_url"):
                rec.oa_links.append(OALink(loc["pdf_url"], "pdf", "OpenAlex", loc.get("version") or "",
                                           loc.get("license") or "", host))
            if loc.get("landing_page_url") and loc.get("is_oa"):
                rec.oa_links.append(OALink(loc["landing_page_url"], "landing", "OpenAlex", loc.get("version") or "",
                                           loc.get("license") or "", host))

    def _merge_unpaywall(self, rec: PaperRecord, u: Dict[str, Any]) -> None:
        self._used(rec, "Unpaywall")
        rec.is_oa = rec.is_oa or bool(u.get("is_oa"))
        if u.get("oa_status"):
            rec.oa_status = str(u["oa_status"])
            rec.field_sources["oa_status"] = "Unpaywall"
        self._set(rec, "title", _clean(u.get("title")), "Unpaywall")
        self._set(rec, "year", _int(u.get("year")) or None, "Unpaywall")
        self._set(rec, "venue", _clean(u.get("journal_name")), "Unpaywall")
        self._set(rec, "publisher", _clean(u.get("publisher")), "Unpaywall")
        best = u.get("best_oa_location") or {}
        ordered = ([best] if best else []) + [x for x in (u.get("oa_locations") or []) if x is not best]
        for loc in ordered:
            if loc.get("url_for_pdf"):
                rec.oa_links.insert(
                    0 if loc is best else len(rec.oa_links),
                    OALink(loc["url_for_pdf"], "pdf", "Unpaywall", loc.get("version") or "",
                           loc.get("license") or "", loc.get("host_type") or ""),
                )
            if loc.get("url_for_landing_page"):
                rec.oa_links.append(OALink(
                    loc["url_for_landing_page"], "landing", "Unpaywall",
                    loc.get("version") or "", loc.get("license") or "", loc.get("host_type") or "",
                ))

    def _merge_s2(self, rec: PaperRecord, s: Dict[str, Any]) -> None:
        self._used(rec, "Semantic Scholar")
        self._set(rec, "title", _clean(s.get("title")), "Semantic Scholar")
        self._set(
            rec, "authors",
            [_split_name(a.get("name", "")) for a in (s.get("authors") or []) if a.get("name")],
            "Semantic Scholar",
        )
        self._set(rec, "year", _int(s.get("year")) or None, "Semantic Scholar")
        self._set(rec, "venue", _clean(s.get("venue") or (s.get("journal") or {}).get("name")), "Semantic Scholar")
        rec.cited_by_count = max(rec.cited_by_count, _int(s.get("citationCount")))
        self._set(rec, "reference_count", _int(s.get("referenceCount")), "Semantic Scholar")
        if not rec.abstract and s.get("abstract"):
            rec.abstract, rec.abstract_source = _clean(s["abstract"]), "Semantic Scholar"
        tldr = _clean((s.get("tldr") or {}).get("text")) if isinstance(s.get("tldr"), dict) else ""
        if tldr and not rec.tldr:
            rec.tldr = tldr
        ext = s.get("externalIds") or {}
        self._set(rec, "arxiv_id", _clean(ext.get("ArXiv")), "Semantic Scholar")
        self._set(rec, "pmid", _clean(ext.get("PubMed")), "Semantic Scholar")
        pdf = (s.get("openAccessPdf") or {}).get("url")
        if pdf:
            rec.is_oa = True
            rec.oa_links.append(OALink(pdf, "pdf", "Semantic Scholar"))

    def _merge_europepmc(self, rec: PaperRecord, e: Dict[str, Any]) -> None:
        self._used(rec, "Europe PMC")
        self._set(rec, "title", _clean(e.get("title")), "Europe PMC")
        authors = [
            Author(given=_clean(a.get("firstName")), family=_clean(a.get("lastName")), full=_clean(a.get("fullName")))
            for a in ((e.get("authorList") or {}).get("author") or []) if a.get("lastName") or a.get("fullName")
        ]
        self._set(rec, "authors", authors, "Europe PMC")
        ji = e.get("journalInfo") or {}
        self._set(rec, "venue", _clean((ji.get("journal") or {}).get("title")), "Europe PMC")
        self._set(rec, "volume", _clean(ji.get("volume")), "Europe PMC")
        self._set(rec, "issue", _clean(ji.get("issue")), "Europe PMC")
        self._set(rec, "year", _int(ji.get("yearOfPublication") or e.get("pubYear")) or None, "Europe PMC")
        self._set(rec, "pmid", _clean(e.get("pmid")), "Europe PMC")
        self._set(rec, "pmcid", _clean(e.get("pmcid")), "Europe PMC")
        if not rec.abstract and e.get("abstractText"):
            rec.abstract, rec.abstract_source = _clean(e["abstractText"]), "Europe PMC"
        if str(e.get("isOpenAccess", "")).upper() == "Y":
            rec.is_oa = True
        for ft in ((e.get("fullTextUrlList") or {}).get("fullTextUrl") or []):
            avail = str(ft.get("availabilityCode", "")).upper()
            if avail not in ("OA", "F"):
                continue
            kind = "pdf" if str(ft.get("documentStyle", "")).lower() == "pdf" else "landing"
            if ft.get("url"):
                rec.oa_links.append(OALink(ft["url"], kind, "Europe PMC", host_type=_clean(ft.get("site"))))

    def _merge_pubmed(self, rec: PaperRecord, pm: Dict[str, Any]) -> None:
        self._used(rec, "PubMed")
        self._set(rec, "title", pm.get("title", ""), "PubMed")
        self._set(rec, "authors", pm.get("authors", []), "PubMed")
        self._set(rec, "venue", pm.get("venue", ""), "PubMed")
        self._set(rec, "year", pm.get("year"), "PubMed")
        self._set(rec, "volume", pm.get("volume", ""), "PubMed")
        self._set(rec, "issue", pm.get("issue", ""), "PubMed")
        self._set(rec, "pmid", pm.get("pmid", ""), "PubMed")
        self._set(rec, "pmcid", pm.get("pmcid", ""), "PubMed")
        if not rec.abstract and pm.get("abstract"):
            rec.abstract, rec.abstract_source = pm["abstract"], "PubMed"
        if pm.get("pmcid"):
            rec.is_oa = True
            rec.oa_links.append(OALink(
                f"https://pmc.ncbi.nlm.nih.gov/articles/{pm['pmcid']}/pdf/",
                "pdf", "PubMed Central", "publishedVersion", "", "repository",
            ))

    def _merge_fatcat(self, rec: PaperRecord, fc: Dict[str, Any]) -> None:
        files = fc.get("files") or []
        added = False
        for fobj in files:
            for u in fobj.get("urls") or []:
                url = u.get("url", "")
                if url and ("web.archive.org" in url or url.lower().endswith(".pdf")) and not is_piracy_url(url):
                    rec.oa_links.append(OALink(url, "pdf", "Internet Archive Scholar", "", "", "repository"))
                    added = True
                    break
        if added:
            self._used(rec, "Internet Archive Scholar")
            rec.is_oa = True

    def _merge_arxiv(self, rec: PaperRecord, a: Dict[str, Any]) -> None:
        self._used(rec, "arXiv")
        self._set(rec, "title", a.get("title", ""), "arXiv")
        self._set(rec, "authors", [_split_name(n) for n in a.get("authors", [])], "arXiv")
        self._set(rec, "year", _year(a.get("published")), "arXiv")
        self._set(rec, "venue", "arXiv", "arXiv")
        self._set(rec, "work_type", "preprint", "arXiv")
        self._set(rec, "arxiv_id", a.get("id", ""), "arXiv")
        if not rec.abstract and a.get("summary"):
            rec.abstract, rec.abstract_source = a["summary"], "arXiv"
        if a.get("pdf"):
            rec.is_oa = True
            rec.oa_links.append(OALink(a["pdf"], "pdf", "arXiv", "submittedVersion", "", "repository"))

    def _layer2_elsevier(self, rec: PaperRecord) -> None:
        abs_info = self.elsevier_abstract(rec.doi)
        ent_info = self.elsevier_entitlement(rec.doi)
        rec.publisher_access["elsevier"] = {
            "abstract_status": abs_info.get("status"),
            "fulltext_entitled": ent_info.get("entitled", False),
            "quota_limit": abs_info.get("quota_limit", ""),
            "quota_remaining": abs_info.get("quota_remaining", ""),
            "quota_reset": abs_info.get("quota_reset", ""),
            "message": abs_info.get("message", ""),
            "scopus_id": abs_info.get("scopus_id", ""),
            "insttoken_used": bool(self.cfg.elsevier_insttoken),
        }
        if abs_info.get("title"):
            self._used(rec, "Elsevier Scopus (BYOK)")
            if not rec.abstract and abs_info.get("abstract"):
                rec.abstract, rec.abstract_source = abs_info["abstract"], "Elsevier Scopus"
            self._set(rec, "venue", abs_info.get("venue", ""), "Elsevier Scopus")
            self._set(rec, "volume", abs_info.get("volume", ""), "Elsevier Scopus")
            self._set(rec, "issue", abs_info.get("issue", ""), "Elsevier Scopus")
            rec.cited_by_count = max(rec.cited_by_count, _int(abs_info.get("cited_by_count")))

    def _finalize_oa(self, rec: PaperRecord) -> None:
        seen: set[str] = set()
        clean_links: List[OALink] = []
        for link in rec.oa_links:
            if not link.url or link.url in seen or is_piracy_url(link.url):
                continue
            seen.add(link.url)
            clean_links.append(link)
        rec.oa_links = clean_links
        pdfs = [x for x in clean_links if x.kind == "pdf"]
        rank = {"publishedVersion": 0, "acceptedVersion": 1, "submittedVersion": 2, "": 3}
        src_rank = {"Unpaywall": 0, "OpenAlex": 1, "PubMed Central": 1, "Europe PMC": 1, "arXiv": 2, "Semantic Scholar": 2}
        pdfs.sort(key=lambda x: (rank.get(x.version, 3), src_rank.get(x.source, 4)))
        if pdfs:
            rec.best_pdf_url = pdfs[0].url
            rec.best_pdf_source = pdfs[0].source
            rec.is_oa = True
            if not rec.oa_status or rec.oa_status == "closed":
                rec.oa_status = "green" if "Preprint" in pdfs[0].source else "open"
        if not rec.landing_url:
            rec.landing_url = rec.doi_url
        if not rec.oa_status:
            rec.oa_status = "open" if rec.is_oa else "closed"
        rec.legal_alternatives = build_legal_alternatives(rec)


# ----------------------------------------------------------------------------- jalur alternatif legal

def build_legal_alternatives(rec: PaperRecord) -> List[LegalAlternative]:
    """Rute alternatif 100% legal ketika PDF langsung tidak tersedia di DOI penerbit."""
    q_title = urllib.parse.quote_plus(rec.title or rec.query)
    alts: List[LegalAlternative] = []
    for link in [x for x in rec.oa_links if x.kind == "landing"][:2]:
        alts.append(LegalAlternative(f"Halaman OA ({link.source})", link.url, "Landing page repositori/penerbit terbuka."))
    if rec.doi:
        d_enc = urllib.parse.quote(rec.doi)
        alts.append(LegalAlternative(
            "Internet Archive Scholar",
            f"https://scholar.archive.org/search?q=doi%3A{d_enc}",
            "Arsip preservasi jurnal Open Access legal (Wayback / Fatcat).",
        ))
        alts.append(LegalAlternative(
            "CORE (Repositori Kampus Global)",
            f"https://core.ac.uk/search?q=doi%3A%22{d_enc}%22",
            "Mencari accepted manuscript / repositori universitas dunia.",
        ))
        alts.append(LegalAlternative(
            "OpenAIRE Explore",
            f"https://explore.openaire.eu/search/advanced/research-outcomes?f0=pid&fv0={d_enc}",
            "Indeks Open Science Eropa untuk salinan repositori institusi.",
        ))
    alts.append(LegalAlternative(
        "Google Scholar — Klik 'Semua Versi'",
        f"https://scholar.google.com/scholar?q={q_title}",
        "Sering menautkan draf PDF resmi di halaman dosen/universitas.",
    ))
    if rec.pmcid:
        alts.append(LegalAlternative(
            "PubMed Central (Full Text)",
            f"https://pmc.ncbi.nlm.nih.gov/articles/{rec.pmcid}/",
            "Arsip full-text biomedis terbuka.",
        ))
    if rec.title:
        alts.append(LegalAlternative(
            "Garuda Kemdiktisaintek",
            f"https://garuda.kemdiktisaintek.go.id/documents?select=title&q={q_title}",
            "Portal resmi jurnal nasional Indonesia (SINTA / OJS).",
        ))
    orcids = [a.orcid for a in rec.authors if a.orcid]
    if orcids:
        alts.append(LegalAlternative(
            "Profil ORCID Penulis",
            f"https://orcid.org/{orcids[0]}",
            "Cek tautan repositori pribadi atau kontak korespondensi penulis.",
        ))
    alts.append(LegalAlternative(
        "Akses Perpustakaan Kampus / Elsevier BYOK InstToken",
        rec.doi_url or rec.landing_url,
        "Gunakan SSO/VPN perpustakaan kampus atau aktifkan Lapisan 2 Elsevier.",
    ))
    return alts


def author_request_template(
    rec: PaperRecord,
    requester_name: str = "Mahasiswa Peneliti",
    institution: str = "Universitas",
) -> str:
    first = rec.authors[0] if rec.authors else Author(family="Author")
    return (
        f"Subject: Academic Request for Article Copy — \"{rec.title}\"\n\n"
        f"Dear Dr. {first.family or first.display()},\n\n"
        f"I am {requester_name} from {institution}. I am citing and studying your work "
        f"\"{rec.title}\" ({rec.venue or 'Journal'}, {rec.year or 'n.d.'}; {rec.doi_url}) "
        f"for my academic research. Would you kindly share an author's accepted manuscript "
        f"or reprint for personal scholarly reading?\n\nThank you very much for your time.\n\n"
        f"Sincerely,\n{requester_name}\n"
    )


# ----------------------------------------------------------------------------- parser XML arXiv & PubMed

def parse_arxiv_atom(xml_text: str) -> Optional[Dict[str, Any]]:
    ns = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return None
    entry = root.find("a:entry", ns)
    if entry is None or entry.find("a:title", ns) is None:
        return None
    pdf = ""
    for link in entry.findall("a:link", ns):
        if link.get("title") == "pdf" or link.get("type") == "application/pdf":
            pdf = link.get("href", "")
    ident = (entry.findtext("a:id", default="", namespaces=ns) or "").rsplit("/abs/", 1)[-1]
    title = _clean(entry.findtext("a:title", default="", namespaces=ns))
    if not title or title.lower() == "error":
        return None
    return {
        "id": ident,
        "title": title,
        "summary": _clean(entry.findtext("a:summary", default="", namespaces=ns)),
        "authors": [_clean(a.findtext("a:name", default="", namespaces=ns)) for a in entry.findall("a:author", ns)],
        "published": entry.findtext("a:published", default="", namespaces=ns),
        "doi": entry.findtext("arxiv:doi", default="", namespaces=ns),
        "pdf": pdf.replace("http://", "https://"),
    }


def parse_pubmed_xml(xml_text: str, fallback_pmid: str = "") -> Optional[Dict[str, Any]]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return None
    art = root.find(".//PubmedArticle")
    if art is None:
        return None
    title = _clean("".join(art.find(".//ArticleTitle").itertext())) if art.find(".//ArticleTitle") is not None else ""
    abs_parts = []
    for ab_el in art.findall(".//Abstract/AbstractText"):
        lbl = ab_el.get("Label", "")
        txt = _clean("".join(ab_el.itertext()))
        if txt:
            abs_parts.append(f"{lbl}: {txt}" if lbl else txt)
    authors: List[Author] = []
    for au in art.findall(".//AuthorList/Author"):
        last = _clean(au.findtext("LastName", default=""))
        fore = _clean(au.findtext("ForeName", default=""))
        coll = _clean(au.findtext("CollectiveName", default=""))
        if last or coll:
            authors.append(Author(given=fore, family=last or coll))
    pmid = _clean(art.findtext(".//MedlineCitation/PMID", default=fallback_pmid))
    doi = ""
    pmcid = ""
    for aid in art.findall(".//PubmedData/ArticleIdList/ArticleId"):
        id_type = aid.get("IdType", "")
        if id_type == "doi":
            doi = normalize_doi(aid.text or "")
        elif id_type == "pmc":
            pmcid = _clean(aid.text)
    return {
        "pmid": pmid,
        "pmcid": pmcid,
        "doi": doi,
        "title": title,
        "abstract": " ".join(abs_parts),
        "authors": authors,
        "venue": _clean(art.findtext(".//Journal/Title", default="")),
        "volume": _clean(art.findtext(".//JournalIssue/Volume", default="")),
        "issue": _clean(art.findtext(".//JournalIssue/Issue", default="")),
        "year": _year(art.findtext(".//JournalIssue/PubDate/Year", default="")
                      or art.findtext(".//JournalIssue/PubDate/MedlineDate", default="")),
    }


def _related_from_openalex(w: Dict[str, Any]) -> RelatedWork:
    oa = w.get("open_access") or {}
    return RelatedWork(
        title=_clean(w.get("display_name")),
        doi=normalize_doi(w.get("doi") or ""),
        year=_int(w.get("publication_year")) or None,
        cited_by_count=_int(w.get("cited_by_count")),
        openalex_id=str(w.get("id", "")),
        is_oa=bool(oa.get("is_oa")),
        pdf_url=_clean(oa.get("oa_url")),
    )


# ----------------------------------------------------------------------------- unduhan PDF OA legal

def _safe_filename(text: str, max_len: int = 90) -> str:
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", text or "paper").strip("_")
    return s[:max_len] or "paper"


def _stream_to_file(
    url: str,
    headers: Dict[str, str],
    path: str,
    timeout: int,
    magic: Optional[bytes] = b"%PDF",
) -> DownloadResult:
    if is_piracy_url(url):
        return DownloadResult(ok=False, url=url, message="Diblokir: domain pembajakan.")
    if not _is_public_http_url(url):
        return DownloadResult(ok=False, url=url, message="URL tidak aman / bukan http(s) publik.")
    req = urllib.request.Request(url, headers=headers)
    tmp = path + ".part"
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            final_url = resp.geturl()
            if is_piracy_url(final_url) or not _is_public_http_url(final_url):
                return DownloadResult(ok=False, url=final_url, message="Redirect tidak aman/diblokir.")
            total = 0
            first = b""
            with open(tmp, "wb") as f:
                while True:
                    chunk = resp.read(64 * 1024)
                    if not chunk:
                        break
                    if not first:
                        first = chunk[:1024]
                        if magic and magic not in first:
                            raise ValueError("respons bukan PDF valid (halaman landing/paywall)")
                    total += len(chunk)
                    if total > MAX_PDF_BYTES:
                        raise ValueError("ukuran PDF melebihi batas aman 60 MB")
                    f.write(chunk)
        os.replace(tmp, path)
        return DownloadResult(ok=True, path=path, url=final_url, size=total, message="OK")
    except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError, ValueError, OSError) as e:
        try:
            os.remove(tmp)
        except OSError:
            pass
        return DownloadResult(ok=False, url=url, message=str(getattr(e, "reason", e))[:160])


def download_oa_pdf(rec: PaperRecord, out_dir: str, timeout: int = 35) -> DownloadResult:
    candidates = [x.url for x in rec.oa_links if x.kind == "pdf"]
    if rec.best_pdf_url and rec.best_pdf_url not in candidates:
        candidates.insert(0, rec.best_pdf_url)
    if not candidates:
        return DownloadResult(ok=False, message="Tidak ada PDF Open Access legal. Gunakan daftar legal_alternatives.")
    os.makedirs(out_dir, exist_ok=True)
    lead = (rec.authors[0].family if rec.authors else "") or "Paper"
    name = _safe_filename(f"{lead}_{rec.year or 'nd'}_{rec.doi or rec.title}")
    path = os.path.join(out_dir, name + ".pdf")
    headers = {"User-Agent": f"MSSHI-Val-DOI-Engine/{__version__}", "Accept": "application/pdf,*/*;q=0.8"}
    last = DownloadResult(ok=False, message="belum dicoba")
    for url in candidates[:4]:
        last = _stream_to_file(url, headers, path, timeout)
        if last.ok:
            return last
    return last


# ----------------------------------------------------------------------------- format sitasi bebas placeholder (4 gaya)

def _initials(given: str, sep: str = " ", dot: bool = True) -> str:
    parts = [p for p in re.split(r"[\s.\-]+", given or "") if p]
    suf = "." if dot else ""
    return sep.join(f"{p[0].upper()}{suf}" for p in parts)


def _apa_author(a: Author) -> str:
    if a.family and a.given:
        return f"{a.family}, {_initials(a.given, sep=' ', dot=True)}"
    return a.family or a.display()


def _ieee_author(a: Author) -> str:
    if a.family and a.given:
        return f"{_initials(a.given, sep=' ', dot=True)} {a.family}"
    return a.display()


def _vancouver_author(a: Author) -> str:
    if a.family and a.given:
        return f"{a.family} {_initials(a.given, sep='', dot=False)}"
    return a.family or a.display()


def _intext_author_year(rec: PaperRecord) -> str:
    yr = str(rec.year) if rec.year else "n.d."
    if not rec.authors:
        short_t = " ".join((rec.title or rec.venue or "Studi").split()[:3])
        return f"({short_t}, {yr})"
    f0 = rec.authors[0].family or rec.authors[0].display()
    if len(rec.authors) == 1:
        return f"({f0}, {yr})"
    if len(rec.authors) == 2:
        f1 = rec.authors[1].family or rec.authors[1].display()
        return f"({f0} & {f1}, {yr})"
    return f"({f0} et al., {yr})"


def format_citation(rec: PaperRecord, style: str = "APA 7th", index: int = 1) -> Citation:
    """Format sitasi bibliografi bersih tanpa placeholder 'Anonim' / 'Untitled'."""
    s = (style or "APA 7th").lower()
    title = (rec.title or rec.venue or rec.doi or "Dokumen Ilmiah").rstrip(".")
    year = str(rec.year) if rec.year else "n.d."
    seg: List[Dict[str, Any]] = []

    def add(text: str, italic: bool = False) -> None:
        if text:
            seg.append({"text": text, "italic": italic})

    if "ieee" in s:
        names = [x for x in (_ieee_author(a) for a in rec.authors) if x]
        if len(names) > 6:
            auth = names[0] + " et al."
        elif len(names) > 1:
            auth = ", ".join(names[:-1]) + ", and " + names[-1]
        else:
            auth = names[0] if names else (rec.publisher or "")
        add(f"[{index}] " + (f"{auth}, " if auth else ""))
        add(f"\"{title},\" ")
        if rec.venue:
            add(rec.venue, italic=True)
        tail = []
        if rec.volume:
            tail.append(f"vol. {rec.volume}")
        if rec.issue:
            tail.append(f"no. {rec.issue}")
        if rec.pages:
            tail.append(("pp. " if "–" in rec.pages else "p. ") + rec.pages)
        if rec.year:
            tail.append(year)
        if tail:
            add((", " if rec.venue else "") + ", ".join(tail))
        add(f", doi: {rec.doi}." if rec.doi else ".")
        return Citation(style=style, text="".join(x["text"] for x in seg).strip(), intext=f"[{index}]", segments=seg)

    if "vancouver" in s:
        names = [x for x in (_vancouver_author(a) for a in rec.authors) if x]
        if len(names) > 6:
            auth = ", ".join(names[:6]) + ", et al."
        else:
            auth = ", ".join(names)
        if auth:
            add(f"{index}. {auth.rstrip('.')}. {title}. ")
        else:
            add(f"{index}. {title}. ")
        if rec.venue:
            add(f"{rec.venue}. ")
        loc = year
        if rec.volume:
            loc += f";{rec.volume}"
            if rec.issue:
                loc += f"({rec.issue})"
        if rec.pages:
            loc += f":{rec.pages}"
        add(f"{loc}.")
        if rec.doi:
            add(f" doi:{rec.doi}.")
        return Citation(style=style, text="".join(x["text"] for x in seg).strip(), intext=f"({index})", segments=seg)

    if "harvard" in s:
        names = [x for x in (_apa_author(a) for a in rec.authors) if x]
        if len(names) > 3:
            auth = f"{names[0]} et al."
        elif len(names) > 1:
            auth = ", ".join(names[:-1]) + " and " + names[-1]
        else:
            auth = names[0] if names else ""
        if auth:
            add(f"{auth} ({year}) '{title}', ")
        else:
            add(f"'{title}' ({year}), ")
        if rec.venue:
            add(rec.venue, italic=True)
        vol = rec.volume + (f"({rec.issue})" if rec.issue else "") if rec.volume else ""
        tail = ", ".join(x for x in (vol, f"pp. {rec.pages}" if rec.pages else "") if x)
        add((", " + tail if tail else "") + ".")
        if rec.doi_url:
            add(f" doi:{rec.doi}.")
        elif rec.landing_url:
            add(f" Available at: {rec.landing_url}.")
        return Citation(style=style, text="".join(x["text"] for x in seg).strip(),
                        intext=_intext_author_year(rec), segments=seg)

    # Default: APA 7th Edition (termasuk aturan 21+ penulis: 19 pertama + ... + penulis terakhir)
    all_apa = [x for x in (_apa_author(a) for a in rec.authors) if x]
    if not all_apa:
        # Aturan resmi APA 7th bila tanpa penulis individu: judul maju ke posisi penulis
        add(f"{title}. ({year}). ")
    else:
        if len(all_apa) == 1:
            auth = all_apa[0]
        elif len(all_apa) <= 20:
            auth = ", ".join(all_apa[:-1]) + ", & " + all_apa[-1]
        else:
            auth = ", ".join(all_apa[:19]) + ", . . . " + all_apa[-1]
        if not auth.endswith("."):
            auth += "."
        add(f"{auth} ({year}). {title}. ")
    if rec.venue:
        add(rec.venue, italic=True)
        if rec.volume:
            add(", ")
            add(rec.volume, italic=True)
            if rec.issue:
                add(f"({rec.issue})")
        if rec.pages:
            add(f", {rec.pages}")
        add(".")
    elif rec.publisher:
        add(f"{rec.publisher}.")
    link = rec.doi_url or rec.landing_url
    if link:
        add(f" {link}")
    return Citation(style=style, text="".join(x["text"] for x in seg).strip(),
                    intext=_intext_author_year(rec), segments=seg)


# ----------------------------------------------------------------------------- ekstraksi Tabel Sintesis Bab 2

_METHOD_PATTERNS = [
    r"\b(transformer|bert|IndoBERT|gpt|llm|rag|cnn|rnn|lstm|bi-lstm|gru|yolo\w*|resnet\w*|random forest|"
    r"xgboost|lightgbm|catboost|svm|support vector|naive bayes|k-means|knn|decision tree|deep learning|"
    r"machine learning|reinforcement learning|transfer learning|federated learning|autoencoder|gan)\b",
    r"\b(regresi\s+\w+|structural equation modeling|pls-sem|anova|uji-t|chi-square|korelasional|"
    r"kuantitatif|kualitatif|studi kasus|fenomenologi|systematic literature review|slr|prisma|"
    r"research and development|r&d|addie|borg\s*(?:&|and)\s*gall|scrum|agile|waterfall|prototype)\b",
]
_METRIC_RE = re.compile(
    r"([^.;]{0,70}\b(?:accuracy|akurasi|precision|presisi|recall|f1(?:-score)?|auc|roc|rmse|mae|mape|"
    r"bleu|rouge|mAP|p\s*[<=>]\s*0[.,]\d+|r2|r-square|\d{2,3}(?:[.,]\d+)?\s*%)[^.;]{0,70})",
    re.I,
)
_DATASET_RE = re.compile(
    r"([^.;]{0,60}\b(?:dataset|corpus|korpus|responden|sampel|sample|participants|patients|mahasiswa|"
    r"siswa|citra|images|dokumen|tweet|ulasan|reviews|benchmark|n\s*=\s*\d+)[^.;]{0,60})",
    re.I,
)


def extract_bab2_row(rec: PaperRecord) -> Bab2SynthesisRow:
    """Ekstrak baris Tabel Penelitian Terdahulu Bab 2 secara deterministik dari metadata + abstrak."""
    intext = _intext_author_year(rec)
    lead = (rec.authors[0].family or rec.authors[0].display()) if rec.authors else (rec.venue or "Studi")
    if len(rec.authors) > 2:
        penulis_th = f"{lead} et al. ({rec.year or 'n.d.'})"
    elif len(rec.authors) == 2:
        f2 = rec.authors[1].family or rec.authors[1].display()
        penulis_th = f"{lead} & {f2} ({rec.year or 'n.d.'})"
    else:
        penulis_th = f"{lead} ({rec.year or 'n.d.'})"

    judul_jurnal = rec.title or rec.doi
    if rec.venue:
        judul_jurnal += f" — {rec.venue}"
    if len(judul_jurnal) > 155:
        judul_jurnal = judul_jurnal[:152].rstrip() + "…"

    corpus = f"{rec.title}. {rec.abstract} {rec.tldr}".strip()
    found_methods: List[str] = []
    for pat in _METHOD_PATTERNS:
        for m in re.finditer(pat, corpus, re.I):
            tok = m.group(0).strip()
            if tok.lower() not in {x.lower() for x in found_methods}:
                found_methods.append(tok)
    metode = ", ".join(found_methods[:4]) if found_methods else (
        "Studi empiris / analisis literatur pada domain terkait" if corpus else "Analisis ilmiah terpublikasi"
    )

    m_ds = _DATASET_RE.search(rec.abstract or "")
    dataset = _clean(m_ds.group(1))[:120] if m_ds else (
        f" Publikasi pada {rec.venue}" if rec.venue else "Data primer/sekunder studi terkait"
    ).strip()

    m_met = _METRIC_RE.search(rec.abstract or "")
    if m_met:
        hasil = _clean(m_met.group(1))[:180]
    elif rec.tldr:
        hasil = rec.tldr[:180]
    elif rec.abstract:
        sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", rec.abstract) if len(s.strip()) > 35]
        hasil = (sents[-1] if sents else rec.abstract)[:180]
    else:
        hasil = f"Tersitasi {rec.cited_by_count} kali; terverifikasi via {', '.join(rec.sources_used[:2]) or 'DOI'}."

    return Bab2SynthesisRow(
        penulis_tahun=penulis_th,
        judul_jurnal=judul_jurnal,
        metode=metode,
        dataset_sampel=dataset,
        hasil_metrik=hasil,
        sitasi_intext=intext,
        doi=rec.doi,
    )


# ----------------------------------------------------------------------------- ekspor RIS / BibTeX / CSV / ZIP

def to_ris(records: List[PaperRecord]) -> str:
    lines: List[str] = []
    for r in records:
        if not r.found:
            continue
        lines.append(f"TY  - {_ris_type(r.work_type)}")
        lines.append(f"TI  - {r.title}")
        for a in r.authors:
            lines.append(f"AU  - {a.family + ', ' + a.given if a.family and a.given else a.display()}")
        if r.year:
            lines.append(f"PY  - {r.year}")
        for tag, val in (
            ("T2", r.venue), ("JO", r.venue), ("PB", r.publisher), ("VL", r.volume),
            ("IS", r.issue), ("SP", r.first_page or r.article_number), ("EP", r.last_page),
            ("SN", r.issn), ("DO", r.doi), ("UR", r.doi_url or r.best_pdf_url or r.landing_url),
            ("AB", r.abstract[:4000] if r.abstract else ""),
        ):
            if val:
                lines.append(f"{tag}  - {val}")
        for kw in r.keywords[:8]:
            lines.append(f"KW  - {kw}")
        lines.append("ER  - ")
        lines.append("")
    return "\n".join(lines)


def to_bibtex(records: List[PaperRecord]) -> str:
    out: List[str] = []
    used: set[str] = set()
    for r in records:
        if not r.found:
            continue
        base = re.sub(r"[^A-Za-z]", "", (r.authors[0].family if r.authors else "ref")) or "ref"
        key = f"{base.lower()}{r.year or ''}"
        k, i = key, 2
        while k in used:
            k = f"{key}{chr(96 + i)}" if i <= 26 else f"{key}_{i}"
            i += 1
        used.add(k)
        rt = _ris_type(r.work_type)
        kind = "book" if rt == "BOOK" else ("inproceedings" if rt == "CPAPER" else "article")
        fields = {
            "title": r.title,
            "author": " and ".join(f"{a.family}, {a.given}" if a.family and a.given else a.display() for a in r.authors),
            "journal" if kind == "article" else "booktitle": r.venue,
            "year": str(r.year or ""),
            "volume": r.volume,
            "number": r.issue,
            "pages": r.pages.replace("–", "--"),
            "issn": r.issn,
            "publisher": r.publisher,
            "doi": r.doi,
            "url": r.doi_url or r.best_pdf_url or "",
        }
        body = ",\n".join(f"  {fk} = {{{fv.replace('{', '').replace('}', '')}}}" for fk, fv in fields.items() if fv)
        out.append(f"@{kind}{{{k},\n{body}\n}}")
    return "\n\n".join(out) + ("\n" if out else "")


def write_bab2_csv(records: List[PaperRecord], csv_path: str) -> int:
    found = [r for r in records if r.found]
    headers = [
        "No", "Penulis & Tahun", "Judul & Jurnal", "Metode / Algoritma / Pendekatan",
        "Dataset / Objek / Sampel", "Hasil Utama & Metrik Evaluasi", "Sitasi In-Text", "DOI",
    ]
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for idx, rec in enumerate(found, 1):
            row = extract_bab2_row(rec)
            writer.writerow([
                idx, row.penulis_tahun, row.judul_jurnal, row.metode,
                row.dataset_sampel, row.hasil_metrik, row.sitasi_intext, row.doi,
            ])
    return len(found)


def resolve_many(
    queries: Iterable[str],
    engine: Optional[ResearchEngine] = None,
    with_citations: bool = False,
    use_layer2: bool = True,
) -> List[PaperRecord]:
    engine = engine or ResearchEngine()
    out: List[PaperRecord] = []
    seen_q: set[str] = set()
    for raw in queries:
        for q in extract_identifiers(raw) or ([raw.strip()] if raw and raw.strip() else []):
            norm = normalize_doi(q) or q.lower()
            if norm in seen_q:
                continue
            seen_q.add(norm)
            out.append(engine.resolve(q, with_citations=with_citations, use_layer2=use_layer2))
    return out


def export_bundle(
    records: List[PaperRecord],
    out_dir: str,
    style: str = "APA 7th",
    download_pdf: bool = False,
    make_zip: bool = True,
    topic_label: str = "Riset Literatur via DOI",
    engine: Optional[ResearchEngine] = None,
) -> Dict[str, Any]:
    """Ekspor paket lengkap yang 100% kompatibel dengan Auto-Template (build_template.py --muza-zip) & Zotero."""
    os.makedirs(out_dir, exist_ok=True)
    found = [r for r in records if r.found]
    ordered = found if any(x in style.lower() for x in ("ieee", "vancouver")) else sorted(
        found,
        key=lambda r: ((r.authors[0].family if r.authors else r.title).lower(), r.year or 9999, r.title.lower()),
    )

    ris_path = os.path.join(out_dir, "01_IMPOR_KE_ZOTERO.ris")
    csv_path = os.path.join(out_dir, "02_TABEL_PENELITIAN_TERDAHULU_BAB2.csv")
    meta_path = os.path.join(out_dir, "03_METADATA_MUZA_SKRIPSI.json")
    bib_path = os.path.join(out_dir, "referensi.bib")
    json_path = os.path.join(out_dir, "metadata_doi.json")
    txt_path = os.path.join(out_dir, f"Daftar_Pustaka_{_safe_filename(style)}.txt")

    with open(ris_path, "w", encoding="utf-8") as f:
        f.write(to_ris(ordered))
    write_bab2_csv(ordered, csv_path)
    with open(bib_path, "w", encoding="utf-8") as f:
        f.write(to_bibtex(ordered))
    with open(txt_path, "w", encoding="utf-8") as f:
        for i, r in enumerate(ordered, 1):
            f.write(format_citation(r, style, i).text + "\n\n")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump([r.to_dict() for r in ordered], f, ensure_ascii=False, indent=2)

    meta = {
        "generator": f"Val DOI Engine v{__version__}",
        "topik": topic_label,
        "topik_id": topic_label,
        "topik_en": topic_label,
        "total_referensi": len(ordered),
        "jumlah_nasional": sum(1 for r in ordered if (r.language or "").lower() == "id"),
        "jumlah_internasional": sum(1 for r in ordered if (r.language or "").lower() != "id"),
        "citation_style": style,
        "dois": [r.doi for r in ordered if r.doi],
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    downloads: List[Dict[str, Any]] = []
    if download_pdf:
        pdf_dir = os.path.join(out_dir, "PDF")
        for r in ordered:
            res = download_oa_pdf(r, pdf_dir, timeout=(engine.cfg.timeout * 2 if engine else 35))
            downloads.append({"doi": r.doi, "ok": res.ok, "path": res.path, "message": res.message})

    zip_path = ""
    if make_zip:
        zip_path = os.path.join(out_dir, "Val_DOI_Bundle_Skripsi.zip")
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for fp in (ris_path, csv_path, meta_path, bib_path, json_path, txt_path):
                zf.write(fp, os.path.basename(fp))
            for d in downloads:
                if d.get("ok") and d.get("path") and os.path.isfile(d["path"]):
                    zf.write(d["path"], f"PDF/{os.path.basename(d['path'])}")

    return {
        "out_dir": out_dir,
        "zip_path": zip_path,
        "found": len(ordered),
        "total": len(records),
        "downloads": downloads,
    }


# ----------------------------------------------------------------------------- CLI

def _print_record(rec: PaperRecord, style: str) -> None:
    print("=" * 78)
    print(f"🔎 Input   : {rec.query}")
    if not rec.found:
        print("❌ Tidak ditemukan.")
        for w in rec.warnings:
            print(f"   ⚠ {w}")
        for h in rec.citing_sample[:5]:
            print(f"   • {h.title} ({h.year or 'n.d.'}) — {h.doi or h.openalex_id}")
        return
    print(f"📄 Judul   : {rec.title}")
    print(f"👥 Penulis : {', '.join(a.display() for a in rec.authors[:8])}{' et al.' if len(rec.authors) > 8 else ''}")
    print(f"📚 Terbit  : {rec.venue or '-'} · {rec.year or 'n.d.'} · vol {rec.volume or '-'} no {rec.issue or '-'} hlm {rec.pages or '-'}")
    print(f"🔗 DOI     : {rec.doi_url or '-'}")
    print(f"📈 Sitasi  : dikutip {rec.cited_by_count}× · {rec.reference_count} referensi")
    oa_line = f"{rec.oa_status.upper()}"
    if rec.best_pdf_url:
        oa_line += f" · PDF Legal ({rec.best_pdf_source}): {rec.best_pdf_url}"
    else:
        oa_line += " · PDF langsung belum terbuka (lihat jalur alternatif legal di bawah)"
    print(f"🔓 Akses   : {oa_line}")
    if rec.publisher_access.get("elsevier"):
        el = rec.publisher_access["elsevier"]
        print(f"🏛️ Elsevier: HTTP {el['abstract_status']} · full-text entitled={el['fulltext_entitled']} "
              f"· sisa kuota {el.get('quota_remaining') or '?'}")
        if el.get("message"):
            print(f"             {el['message']}")
    if rec.abstract:
        print(f"📝 Abstrak ({rec.abstract_source}): {rec.abstract[:650]}{'…' if len(rec.abstract) > 650 else ''}")
    cit = format_citation(rec, style, 1)
    print(f"🧾 {style} : {cit.text}")
    print(f"🔖 In-Text : {cit.intext}")
    if not rec.best_pdf_url:
        print("🧭 Jalur Alternatif Legal:")
        for alt in rec.legal_alternatives[:6]:
            print(f"   • {alt.label}: {alt.url}")
    if rec.citing_sample:
        print("⬆️ Paper pengutip tertinggi (OpenAlex):")
        for c in rec.citing_sample[:5]:
            print(f"   • {c.title} ({c.year or 'n.d.'}) · {c.cited_by_count}× · {c.doi}")
    if rec.references:
        print("⬇️ Sampel referensi yang dirujuk:")
        for c in rec.references[:5]:
            print(f"   • {c.title} ({c.year or 'n.d.'}) · {c.doi}")
    print(f"🧩 Sumber  : {', '.join(rec.sources_used)}")
    for w in rec.warnings:
        print(f"   ⚠ {w}")


def _cmd_setup(cfg: EngineConfig) -> int:
    print(onboarding_text(cfg))
    ans = input("Ingin mengisi API key opsional sekarang? [y/N/Lewati]: ").strip().lower()
    if ans in ("", "n", "no", "tidak", "lewati", "skip"):
        save_keys(cfg, {}, skipped=True)
        print("✅ Dilewati — Lapisan 1 gratis langsung aktif tanpa API key.")
        return 0
    values = {
        "email": input("[1] Email Unpaywall (Enter = lewati): ").strip(),
        "openalex_api_key": getpass.getpass("[2] OpenAlex API key (tersembunyi, Enter = lewati): ").strip(),
        "elsevier_api_key": getpass.getpass("[3] Elsevier API key (tersembunyi, Enter = lewati): ").strip(),
        "elsevier_insttoken": getpass.getpass("[4] Elsevier InstToken kampus (Enter = lewati): ").strip(),
        "s2_api_key": getpass.getpass("[5] Semantic Scholar key (Enter = lewati): ").strip(),
        "ncbi_api_key": getpass.getpass("[6] NCBI PubMed key (Enter = lewati): ").strip(),
    }
    path = save_keys(cfg, {k: v for k, v in values.items() if v}, skipped=False)
    print(f"✅ Tersimpan aman di {path} (di luar repo Git).")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(description="Val DOI Engine v1.2 — Riset Akademik 2-Lapis Legal (MSSHI)")
    parser.add_argument("query", nargs="*", help="DOI / URL DOI / arXiv / PMID / judul, atau: setup | status | onboarding")
    parser.add_argument("--file", help="File teks berisi daftar DOI/judul (satu per baris)")
    parser.add_argument("--format", default="apa", choices=["apa", "ieee", "harvard", "vancouver"], help="Gaya sitasi")
    parser.add_argument("--citations", action="store_true", help="Ambil graf sitasi & referensi (OpenAlex)")
    parser.add_argument("--download-oa", action="store_true", help="Unduh PDF Open Access legal")
    parser.add_argument("--out", default="", help="Folder output paket (RIS, CSV Bab 2, BibTeX, JSON, ZIP)")
    parser.add_argument("--json", action="store_true", help="Cetak hasil sebagai JSON terstruktur")
    parser.add_argument("--no-layer2", action="store_true", help="Nonaktifkan Lapisan 2 meski key tersedia")
    parser.add_argument("--no-cache", action="store_true", help="Abaikan cache disk")
    parser.add_argument("--email", default="", help="Email Unpaywall sekali pakai")
    args = parser.parse_args(argv)

    cfg = load_config(email=args.email or None, use_cache=not args.no_cache)
    style_map = {"apa": "APA 7th", "ieee": "IEEE", "harvard": "Harvard", "vancouver": "Vancouver"}
    style = style_map[args.format]
    words = args.query
    if words and len(words) == 1 and words[0].lower() in ("setup", "status", "onboarding", "skip-onboarding"):
        cmd = words[0].lower()
        if cmd == "setup":
            return _cmd_setup(cfg)
        if cmd == "onboarding":
            print(onboarding_text(cfg))
            return 0
        if cmd == "skip-onboarding":
            mark_onboarding_done(cfg, mode="skipped_layer1")
            print("OK: Onboarding dilewati — Lapisan 1 gratis aktif.")
            return 0
        print(f"Val DOI Engine v{__version__}")
        print("Lapisan 1 (Gratis): AKTIF — OpenAlex, Crossref, Semantic Scholar, arXiv, PubMed, Europe PMC, IA Scholar"
              + (", Unpaywall" if cfg.email else " (Unpaywall aktif otomatis setelah email diisi)"))
        print(f"Lapisan 2 (Elsevier BYOK): {'AKTIF' if cfg.layer2_enabled else 'nonaktif (opsional)'}")
        print(f"Onboarding Selesai: {'Ya' if is_onboarding_done(cfg) else 'Belum'}")
        for k, v in cfg.masked_status().items():
            print(f"  • {k}: {v}")
        return 0

    raw = " ".join(words)
    if args.file:
        with open(args.file, "r", encoding="utf-8-sig") as f:
            raw += "\n" + f.read()
    queries = extract_identifiers(raw)
    if not queries:
        parser.print_help()
        return 2
    engine = ResearchEngine(cfg)
    records = resolve_many(queries, engine=engine, with_citations=args.citations, use_layer2=not args.no_layer2)
    if args.json:
        print(json.dumps([r.to_dict() for r in records], ensure_ascii=False, indent=2))
    else:
        for rec in records:
            _print_record(rec, style)
    if args.out or args.download_oa:
        summary = export_bundle(records, args.out or default_output_dir(), style=style,
                                download_pdf=args.download_oa, engine=engine)
        if not args.json:
            print(f"\n📦 Bundel skripsi & Zotero tersimpan di: {summary['out_dir']} ({summary['found']}/{summary['total']} karya)")
            if summary.get("zip_path"):
                print(f"   🗜️ Siap diumpankan ke Auto-Template (--muza-zip): {summary['zip_path']}")
            for d in summary["downloads"]:
                print(f"   {'✅' if d['ok'] else '⚠'} {d['doi']}: {d['path'] or d['message']}")
    return 0 if any(r.found for r in records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
