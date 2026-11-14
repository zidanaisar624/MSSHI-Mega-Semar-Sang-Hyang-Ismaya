#!/usr/bin/env python3
"""
campus_lookup.py — Pencarian identitas kampus, logo resmi, pejabat (Rektor, Dekan,
Ketua Prodi + NIP), dan pedoman skripsi resmi secara daring untuk MuZA Skripsi.

Prinsip integritas data:
- Tidak pernah mengarang/menghalusinasikan nama pejabat atau NIP/NIDN.
- Setiap data yang terisi menyimpan metadata sumber (`source_url`, `source_label`,
  `raw_snippet`, `verified`) agar pengguna dapat memverifikasi dengan satu klik.
- Bergantung hanya pada library standar Python + `requests` + `Pillow` (fallback ke
  `urllib.request` bila `requests` tidak tersedia).
"""

from __future__ import annotations

import concurrent.futures
import hashlib
import html
from html.parser import HTMLParser
import io
import json
import os
import re
import ssl
import urllib.parse
import urllib.request
import warnings
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
    HAS_REQUESTS = True
except ImportError:  # pragma: no cover
    requests = None
    HAS_REQUESTS = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:  # pragma: no cover
    Image = None
    HAS_PIL = False

try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except Exception:
    pass


USER_AGENT = (
    "MuZASkripsiBuilder/1.1 "
    "(https://colab.research.google.com/drive/1rrl38cwQZ0CA00cMyQvfjJUf1CSEtJpS; "
    "academic-thesis-template-helper)"
)
BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

COMMON_ACRONYMS: Dict[str, str] = {
    "universitas indonesia": "UI",
    "institut teknologi bandung": "ITB",
    "universitas gadjah mada": "UGM",
    "institut pertanian bogor": "IPB",
    "ipb university": "IPB",
    "institut teknologi sepuluh nopember": "ITS",
    "universitas airlangga": "UNAIR",
    "universitas padjadjaran": "UNPAD",
    "universitas diponegoro": "UNDIP",
    "universitas brawijaya": "UB",
    "universitas hasanuddin": "UNHAS",
    "universitas sebelas maret": "UNS",
    "universitas pendidikan indonesia": "UPI",
    "universitas negeri yogyakarta": "UNY",
    "universitas negeri malang": "UM",
    "universitas negeri semarang": "UNNES",
    "universitas wahid hasyim": "UNWAHAS",
    "universitas wahid hasyim semarang": "UNWAHAS",
    "uin walisongo": "UIN Walisongo",
    "uin walisongo semarang": "UIN Walisongo",
    "universitas islam negeri walisongo": "UIN Walisongo",
    "universitas islam negeri walisongo semarang": "UIN Walisongo",
    "politeknik negeri semarang": "POLINES",
    "universitas dian nuswantoro": "UDINUS",
    "universitas katolik soegijapranata": "UNIKA Soegijapranata",
    "unika soegijapranata": "UNIKA Soegijapranata",
    "soegijapranata catholic university": "UNIKA Soegijapranata",
    "universitas islam sultan agung": "UNISSULA",
    "universitas semarang": "USM",
    "universitas muhammadiyah semarang": "UNIMUS",
    "universitas stikubank": "UNISBANK",
    "universitas stikubank semarang": "UNISBANK",
    "universitas negeri jakarta": "UNJ",
    "universitas negeri surabaya": "UNESA",
    "universitas sumatera utara": "USU",
    "universitas andalas": "UNAND",
    "universitas sriwijaya": "UNSRI",
    "universitas lampung": "UNILA",
    "universitas riau": "UNRI",
    "universitas syiah kuala": "USK",
    "universitas jenderal soedirman": "UNSOED",
    "universitas jember": "UNEJ",
    "universitas udayana": "UNUD",
    "universitas mataram": "UNRAM",
    "universitas mulawarman": "UNMUL",
    "universitas lambung mangkurat": "ULM",
    "universitas tanjungpura": "UNTAN",
    "universitas sam ratulangi": "UNSRAT",
    "universitas bina nusantara": "BINUS",
    "binus university": "BINUS",
    "universitas telkom": "Tel-U",
    "telkom university": "Tel-U",
    "universitas muhammadiyah yogyakarta": "UMY",
    "universitas muhammadiyah surakarta": "UMS",
    "universitas muhammadiyah malang": "UMM",
    "universitas islam indonesia": "UII",
    "universitas ahmad dahlan": "UAD",
    "universitas katolik parahyangan": "UNPAR",
    "universitas atma jaya yogyakarta": "UAJY",
    "universitas gunadarma": "UG",
    "universitas mercu buana": "UMB",
    "universitasesa unggul": "UEU",
    "universitas esa unggul": "UEU",
    "uin syarif hidayatullah jakarta": "UIN Jakarta",
    "uin sunan kalijaga yogyakarta": "UIN Suka",
    "uin maulana malik ibrahim malang": "UIN Malang",
    "universitas terbuk": "UT",
    "universitas terbuka": "UT",
    "politeknik elektronika negeri surabaya": "PENS",
    "politeknik negeri bandung": "POLBAN",
    "politeknik negeri jakarta": "PNJ",
    "politeknik negeri malang": "POLINEMA",
}

ALIAS_TO_UNIVERSITY: Dict[str, str] = {
    "undip": "Universitas Diponegoro",
    "unnes": "Universitas Negeri Semarang",
    "unwahas": "Universitas Wahid Hasyim",
    "uin walisongo": "Universitas Islam Negeri Walisongo Semarang",
    "walisongo": "Universitas Islam Negeri Walisongo Semarang",
    "polines": "Politeknik Negeri Semarang",
    "udinus": "Universitas Dian Nuswantoro",
    "unika": "Universitas Katolik Soegijapranata",
    "unika soegijapranata": "Universitas Katolik Soegijapranata",
    "scu": "Universitas Katolik Soegijapranata",
    "unissula": "Universitas Islam Sultan Agung",
    "usm": "Universitas Semarang",
    "unimus": "Universitas Muhammadiyah Semarang",
    "unisbank": "Universitas Stikubank Semarang",
    "ui": "Universitas Indonesia",
    "itb": "Institut Teknologi Bandung",
    "ugm": "Universitas Gadjah Mada",
    "ipb": "IPB University",
    "its": "Institut Teknologi Sepuluh Nopember",
    "ub": "Universitas Brawijaya",
    "unair": "Universitas Airlangga",
    "unpad": "Universitas Padjadjaran",
    "uns": "Universitas Sebelas Maret",
    "upi": "Universitas Pendidikan Indonesia",
    "uny": "Universitas Negeri Yogyakarta",
    "unhas": "Universitas Hasanuddin",
    "unsoed": "Universitas Jenderal Soedirman",
}

ACADEMIC_DEGREE_RULES: List[Tuple[Tuple[str, ...], str]] = [
    (("informatika", "ilmu komputer", "sistem informasi", "teknologi informasi", "rekayasa perangkat lunak", "sains data", "data science", "kecerdasan buatan", "sistem komputer", "komputer"), "Sarjana Komputer (S.Kom.)"),
    (("teknik elektro", "teknik mesin", "teknik sipil", "teknik kimia", "teknik industri", "arsitektur", "teknik lingkungan", "teknik geologi", "teknik pertambangan", "teknik geofisika", "teknik material", "teknik metalurgi", "perencanaan wilayah"), "Sarjana Teknik (S.T.)"),
    (("kedokteran gigi", "pendidikan dokter gigi"), "Sarjana Kedokteran Gigi (S.KG.)"),
    (("kedokteran", "pendidikan dokter"), "Sarjana Kedokteran (S.Ked.)"),
    (("keperawatan", "ilmu keperawatan"), "Sarjana Keperawatan (S.Kep.)"),
    (("kesehatan masyarakat",), "Sarjana Kesehatan Masyarakat (S.K.M.)"),
    (("farmasi",), "Sarjana Farmasi (S.Farm.)"),
    (("gizi", "ilmu gizi"), "Sarjana Gizi (S.Gz.)"),
    (("kebidanan",), "Sarjana Kebidanan (S.Keb.)"),
    (("hukum", "ilmu hukum"), "Sarjana Hukum (S.H.)"),
    (("psikologi",), "Sarjana Psikologi (S.Psi.)"),
    (("akuntansi",), "Sarjana Akuntansi (S.Ak.)"),
    (("manajemen",), "Sarjana Manajemen (S.M.)"),
    (("ekonomi", "pembangunan"), "Sarjana Ekonomi (S.E.)"),
    (("pendidikan", "pgsd", "pgpaud", "bimbingan dan konseling"), "Sarjana Pendidikan (S.Pd.)"),
    (("ilmu komunikasi", "komunikasi", "jurnalistik", "hubungan masyarakat"), "Sarjana Ilmu Komunikasi (S.I.Kom.)"),
    (("hubungan internasional", "ilmu politik", "administrasi publik", "administrasi negara", "sosiologi", "antropologi", "ilmu pemerintahan", "kesejahteraan sosial"), "Sarjana Ilmu Sosial (S.Sos.)"),
    (("administrasi bisnis", "administrasi niaga"), "Sarjana Administrasi Bisnis (S.A.B.)"),
    (("sastra", "bahasa", "sejarah", "filsafat", "ilmu perpustakaan"), "Sarjana Humaniora (S.Hum.)"),
    (("agroteknologi", "agribisnis", "peternakan", "kehutanan", "ilmu tanah", "proteksi tanaman", "pertanian", "perikanan", "kelautan"), "Sarjana Pertanian (S.P.)"),
    (("matematika", "fisika", "kimia", "biologi", "statistika", "aktuaria", "geofisika", "bioteknologi"), "Sarjana Sains (S.Si.)"),
    (("desain komunikasi visual", "desain produk", "seni rupa", "desain interior"), "Sarjana Desain (S.Ds.)"),
]


def _http_get(
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 12,
    headers: Optional[Dict[str, str]] = None,
    binary: bool = False,
) -> Tuple[int, Any, str]:
    """Perform HTTP GET with graceful SSL fallback and return (status, body, final_url)."""
    hdrs = {"User-Agent": USER_AGENT}
    if headers:
        hdrs.update(headers)
    if params:
        qs = urllib.parse.urlencode(params)
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}{qs}"

    if HAS_REQUESTS:
        req_timeout = (min(4, timeout), timeout)
        for verify in (True, False):
            try:
                resp = requests.get(url, headers=hdrs, timeout=req_timeout, allow_redirects=True, verify=verify)
                data = resp.content if binary else resp.text
                return resp.status_code, data, resp.url
            except requests.exceptions.SSLError:
                if verify:
                    continue
                return 0, b"" if binary else "", url
            except Exception:
                return 0, b"" if binary else "", url
        return 0, b"" if binary else "", url

    # Fallback urllib.request
    for use_unverified in (False, True):
        try:
            req = urllib.request.Request(url, headers=hdrs)
            ctx = ssl._create_unverified_context() if use_unverified else None
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                raw = resp.read()
                final_url = resp.geturl()
                if binary:
                    return resp.status, raw, final_url
                return resp.status, raw.decode("utf-8", errors="replace"), final_url
        except ssl.SSLError:
            if not use_unverified:
                continue
            return 0, b"" if binary else "", url
        except Exception:
            return 0, b"" if binary else "", url
    return 0, b"" if binary else "", url


def _http_get_json(url: str, *, params: Optional[Dict[str, Any]] = None, timeout: int = 12) -> Optional[Dict[str, Any]]:
    status, text, _ = _http_get(
        url,
        params=params,
        timeout=timeout,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
        binary=False,
    )
    if status != 200 or not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        return None


def _clean_text(s: str) -> str:
    s = html.unescape(s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _strip_wikitext(raw: str) -> str:
    if not raw:
        return ""
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", raw, flags=re.I | re.S)
    s = re.sub(r"<ref[^/]*/>", "", s, flags=re.I)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<br\s*/?>", ", ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    # [[Target|Display]] -> Display, [[Target]] -> Target
    s = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r"\2", s)
    s = re.sub(r"\[\[([^\]]+)\]\]", r"\1", s)
    # {{nowrap|...}}, {{small|...}}
    for _ in range(3):
        s = re.sub(r"\{\{[^{}|]*\|([^{}]+)\}\}", r"\1", s)
    s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    s = s.replace("'''", "").replace("''", "")
    s = html.unescape(s)
    s = re.sub(r"\[\d+\]", "", s)
    s = re.sub(r"\s+", " ", s).strip(" ,;|•")
    return s


def _extract_infobox_fields(wikitext: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not wikitext:
        return out
    for line in wikitext.splitlines():
        m = re.match(r"^\s*\|\s*([A-Za-z0-9_ ]+?)\s*=\s*(.+)$", line)
        if not m:
            continue
        k = m.group(1).strip().lower().replace(" ", "_")
        v = m.group(2).strip()
        if v and k not in out:
            out[k] = v
    return out


def _infer_short_name(univ_name: str) -> str:
    low = re.sub(r"\s+", " ", (univ_name or "").strip().lower())
    if low in COMMON_ACRONYMS:
        return COMMON_ACRONYMS[low]
    stop = {"dan", "of", "the", "and", "di", "ke", "negeri", "swasta"}
    words = [w for w in re.split(r"[\s\-]+", univ_name.strip()) if w and w.lower() not in stop]
    if len(words) >= 2:
        acr = "".join(w[0].upper() for w in words if w[0].isalnum())
        if 2 <= len(acr) <= 8:
            return acr
    return re.sub(r"[^A-Za-z0-9]", "", univ_name)[:10] or "Kampus"


def _infer_ministry(univ_name: str, inst_type: str = "") -> str:
    low = f"{univ_name} {inst_type}".lower()
    if any(k in low for k in ("uin ", "universitas islam negeri", "iain ", "institut agama islam negeri", "stain ", "iahn", "iakn", "kementerian agama")):
        return "KEMENTERIAN AGAMA REPUBLIK INDONESIA"
    if any(k in low for k in ("negeri", "ptn-bh", "ptn ", "institut teknologi", "institut pertanian", "politeknik negeri", "universitas terbuka", "stan", "ipdn", "stis")):
        if "keuangan" in low or "stan" in low:
            return "KEMENTERIAN KEUANGAN REPUBLIK INDONESIA"
        if "statistika" in low or "stis" in low:
            return "BADAN PUSAT STATISTIK"
        return "KEMENTERIAN PENDIDIKAN TINGGI, SAINS, DAN TEKNOLOGI"
    return ""


def _infer_degree(program_studi: str) -> str:
    low = (program_studi or "").lower()
    if not low.strip():
        return ""
    for keywords, deg in ACADEMIC_DEGREE_RULES:
        if any(kw in low for kw in keywords):
            return deg
    return ""


def _clean_city_name(city: str) -> str:
    if not city:
        return ""
    c = _clean_text(city)
    c = re.sub(r"^(?:Kota\s+Administrasi|Kota|Kabupaten|Kab\.)\s+", "", c, flags=re.I)
    c = c.split(",")[0].strip()
    return c


def _extract_domain(url: str) -> str:
    if not url:
        return ""
    try:
        parsed = urllib.parse.urlparse(url if "://" in url else f"https://{url}")
        host = parsed.netloc.lower()
        host = re.sub(r"^www\.", "", host)
        return host
    except Exception:
        return ""


def _is_plausible_person_name(name: str) -> bool:
    if not name:
        return False
    low = name.lower()
    bad_words = (
        "universitas", "institut", "politeknik", "fakultas", "program studi",
        "jurusan", "beranda", "profil", "selengkapnya", "lihat semua", "baca",
        "struktur organisasi", "pimpinan", "dekanat", "menu", "login", "search",
        "copyright", "all rights", "email", "http", "www.", "jalan ", "jl.",
        "telepon", "telp", "fax", "halaman", "skripsi", "tugas akhir", "pedoman",
        "kalender", "akademik", "visiting", "download", "berita", "pengumuman",
        "mahasiswa", "alumni", "kurikulum", "visi misi", "akreditasi",
    )
    if any(bw in low for bw in bad_words):
        return False
    if "@" in name or re.search(r"https?://", low):
        return False
    # Buang angka panjang di nama
    if re.search(r"\d{4,}", name):
        return False
    tokens = [t for t in re.split(r"[\s,]+", name) if re.search(r"[A-Za-z]", t)]
    if len(tokens) < 2 or len(tokens) > 14:
        return False
    return True


def _clean_person_name(raw: str) -> str:
    s = _clean_text(raw)
    s = re.sub(r"^(?:Prof\.?|Dr\.?|Ir\.?|H\.?|Hj\.?|Drs\.?|Dra\.?)\s+", lambda m: m.group(0), s)
    # Strip trailing role words or periods/years
    s = re.split(r"\s+(?:menjabat|sebagai|periode|NIP\.?|NIDN\.?|NIK\.?)\b", s, maxsplit=1, flags=re.I)[0]
    s = re.sub(r"\(\d{4}\s*[–\-−]\s*(?:\d{4}|sekarang|present)?\)", "", s, flags=re.I)
    s = re.sub(r"\s*[|•/–—-]\s*$", "", s)
    s = re.sub(r"\s+", " ", s).strip(" ,;:-")
    # Preserve trailing dot after degree like M.T. or S.Kom.
    return s


def _wikipedia_lookup(universitas: str) -> Dict[str, Any]:
    """Query id.wikipedia.org and en.wikipedia.org for structured info + Wikimedia QID."""
    result: Dict[str, Any] = {}
    queries = [universitas.strip()]
    for lang in ("id", "en"):
        api = f"https://{lang}.wikipedia.org/w/api.php"
        for q in queries:
            sdata = _http_get_json(api, params={
                "action": "query",
                "list": "search",
                "srsearch": q,
                "srlimit": 5,
                "format": "json",
            })
            hits = ((sdata or {}).get("query") or {}).get("search") or []
            if not hits:
                continue
            chosen = None
            q_low = universitas.lower()
            for h in hits:
                title = h.get("title", "")
                snip = re.sub(r"<[^>]+>", "", h.get("snippet", "")).lower()
                t_low = title.lower()
                if any(k in t_low or k in snip for k in ("universitas", "institut", "politeknik", "sekolah tinggi", "university", "institute", "akademi")):
                    if q_low in t_low or any(w in t_low for w in q_low.split() if len(w) > 3):
                        chosen = title
                        break
            if not chosen:
                chosen = hits[0].get("title")
            if not chosen:
                continue

            pdata = _http_get_json(api, params={
                "action": "query",
                "prop": "pageprops|pageimages|extracts|extlinks|info",
                "inprop": "url",
                "piprop": "original|thumbnail|name",
                "pithumbsize": 600,
                "exintro": 1,
                "explaintext": 1,
                "ellimit": 30,
                "redirects": 1,
                "titles": chosen,
                "format": "json",
            })
            pages = ((pdata or {}).get("query") or {}).get("pages") or {}
            page = next(iter(pages.values()), None)
            if not page or page.get("missing") is not None:
                continue

            page_url = page.get("fullurl") or f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(page.get('title', chosen).replace(' ', '_'))}"
            qid = (page.get("pageprops") or {}).get("wikibase_item")
            title_canon = page.get("title", chosen)

            # Parse section 0 wikitext for infobox
            wdata = _http_get_json(api, params={
                "action": "parse",
                "page": title_canon,
                "prop": "wikitext",
                "section": 0,
                "redirects": 1,
                "format": "json",
            })
            wikitext = (((wdata or {}).get("parse") or {}).get("wikitext") or {}).get("*") or ""
            infobox = _extract_infobox_fields(wikitext)

            if not result.get("title"):
                result["title"] = title_canon
                result["wikipedia_url"] = page_url
                result["extract"] = (page.get("extract") or "")[:600]
            if qid and not result.get("qid"):
                result["qid"] = qid

            # Extract rector from infobox
            for rk in ("rektor", "rector", "president", "chancellor", "direktur", "director", "ketua"):
                if rk in infobox and not result.get("rector"):
                    cand = _clean_person_name(_strip_wikitext(infobox[rk]))
                    if _is_plausible_person_name(cand):
                        result["rector"] = cand
                        result["rector_source"] = page_url

            # Extract acronym / short name
            for ak in ("singkatan", "akronim", "acronym", "nickname", "nama_lain"):
                if ak in infobox and not result.get("short"):
                    val = _strip_wikitext(infobox[ak])
                    if 2 <= len(val) <= 15:
                        result["short"] = val

            # Extract city / location
            for lk in ("kota", "lokasi", "city", "location", "tempat"):
                if lk in infobox and not result.get("city"):
                    val = _clean_city_name(_strip_wikitext(infobox[lk]))
                    if val and len(val) >= 3:
                        result["city"] = val
                        result["city_source"] = page_url

            # Extract type
            for tk in ("jenis", "type"):
                if tk in infobox and not result.get("type"):
                    result["type"] = _strip_wikitext(infobox[tk])

            # Extract website
            for wk in ("situs_web", "situs", "website", "url", "homepage"):
                if wk in infobox and not result.get("website"):
                    m_url = re.search(r"https?://[^\s\|\}\]]+", infobox[wk])
                    if m_url:
                        result["website"] = m_url.group(0).rstrip("/")
                        result["website_source"] = page_url
            if not result.get("website"):
                for el in page.get("extlinks") or []:
                    u = el.get("*", "")
                    if ".ac.id" in u.lower() or ".edu" in u.lower():
                        parsed = urllib.parse.urlparse(u)
                        result["website"] = f"{parsed.scheme}://{parsed.netloc}"
                        result["website_source"] = page_url
                        break

            # Extract logo filename from infobox
            for ik in ("gambar", "logo", "lambang", "image_name", "image", "coat_of_arms"):
                if ik in infobox and not result.get("commons_logo_file"):
                    raw_fn = _strip_wikitext(infobox[ik]).split("|")[0]
                    raw_fn = re.sub(r"^(?:Berkas|File|Image):", "", raw_fn, flags=re.I).strip()
                    m_img = re.search(r"([A-Za-z0-9_.,'\-\(\)\s]+?\.(?:png|svg|jpe?g|webp))", raw_fn, flags=re.I)
                    fn = (m_img.group(1) if m_img else raw_fn).strip(" }]|'\"")
                    fn_low = fn.lower()
                    if any(fn_low.endswith(ext) for ext in (".png", ".svg", ".jpg", ".jpeg", ".webp")):
                        if not any(bad in fn_low for bad in ("gedung", "campus", "building", "rektorat", "aerial", "view")):
                            result["commons_logo_file"] = fn
                            result["logo_info_source"] = page_url

            # Pageimage fallback
            pi_name = page.get("pageimage") or ""
            pi_thumb = (page.get("thumbnail") or {}).get("source") or (page.get("original") or {}).get("source")
            if pi_thumb and not result.get("pageimage_url"):
                if any(good in pi_name.lower() for good in ("logo", "lambang", "seal", "crest", "emblem")):
                    result["commons_logo_file"] = result.get("commons_logo_file") or pi_name
                    result["pageimage_url"] = pi_thumb
                    result["logo_info_source"] = result.get("logo_info_source") or page_url

            if result.get("qid") and result.get("website") and result.get("commons_logo_file"):
                break
        if result.get("qid") and result.get("website"):
            break
    return result


def _wikidata_entity_lookup(qid: str) -> Dict[str, Any]:
    """Query Wikidata entity JSON for structured logo (P154/P94), website (P856), rector (P1075), city (P131)."""
    out: Dict[str, Any] = {}
    if not qid:
        return out
    data = _http_get_json(f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json", timeout=12)
    ent = ((data or {}).get("entities") or {}).get(qid)
    if not ent:
        return out
    wd_url = f"https://www.wikidata.org/wiki/{qid}"
    out["wikidata_url"] = wd_url

    labels = ent.get("labels") or {}
    if "id" in labels:
        out["official_name"] = labels["id"].get("value")
    elif "en" in labels:
        out["official_name"] = labels["en"].get("value")

    claims = ent.get("claims") or {}

    def _all_claim_vals(prop: str) -> List[Any]:
        arr = claims.get(prop) or []
        arr_sorted = sorted(arr, key=lambda c: 0 if c.get("rank") == "preferred" else (2 if c.get("rank") == "deprecated" else 1))
        vals = []
        for item in arr_sorted:
            if item.get("rank") == "deprecated":
                continue
            dv = ((item.get("mainsnak") or {}).get("datavalue") or {})
            if "value" in dv:
                vals.append(dv["value"])
        return vals

    def _first_claim_val(prop: str) -> Any:
        vals = _all_claim_vals(prop)
        return vals[0] if vals else None

    logo_cands: List[str] = []
    for prop in ("P154", "P94", "P41", "P18"):
        for val in _all_claim_vals(prop):
            if isinstance(val, str) and val:
                if prop == "P18" and any(b in val.lower() for b in ("gedung", "campus", "building", "rektorat", "aerial")):
                    continue
                logo_cands.append(val)
    if logo_cands:
        out["commons_logo_files"] = logo_cands
        out["commons_logo_file"] = logo_cands[0]
        out["logo_source_wikidata"] = wd_url

    wval = _first_claim_val("P856")
    if isinstance(wval, str) and wval.startswith("http"):
        out["website"] = wval.rstrip("/")

    sval = _first_claim_val("P1813")
    if isinstance(sval, dict) and sval.get("text"):
        txt_s = sval["text"].strip()
        if len(txt_s) >= 2 and txt_s.upper() != "ID":
            out["short"] = txt_s
    elif isinstance(claims.get("P1813"), list):
        for item in claims["P1813"]:
            dv = ((item.get("mainsnak") or {}).get("datavalue") or {}).get("value")
            if isinstance(dv, dict) and dv.get("language") == "id" and dv.get("text"):
                out["short"] = dv["text"].strip()
                break

    # Resolve QID entities for rector (P1075) and city (P131)
    qids_to_resolve: Dict[str, str] = {}
    rval = _first_claim_val("P1075")
    if isinstance(rval, dict) and rval.get("id"):
        qids_to_resolve["rector"] = rval["id"]
    cval = _first_claim_val("P131")
    if isinstance(cval, dict) and cval.get("id"):
        qids_to_resolve["city"] = cval["id"]

    if qids_to_resolve:
        wb = _http_get_json("https://www.wikidata.org/w/api.php", params={
            "action": "wbgetentities",
            "ids": "|".join(qids_to_resolve.values()),
            "props": "labels",
            "languages": "id|en",
            "format": "json",
        })
        ents = (wb or {}).get("entities") or {}
        for role, rq in qids_to_resolve.items():
            rl = (ents.get(rq) or {}).get("labels") or {}
            lbl = (rl.get("id") or rl.get("en") or {}).get("value")
            if lbl:
                if role == "city":
                    out["city"] = _clean_city_name(lbl)
                else:
                    out[role] = lbl
    return out


def _ror_openalex_lookup(universitas: str) -> Dict[str, Any]:
    """Query ROR v2 and OpenAlex Institutions for official website, city, acronym."""
    out: Dict[str, Any] = {}
    q = universitas.strip()
    if not q:
        return out

    ror = _http_get_json("https://api.ror.org/v2/organizations", params={"query": q}, timeout=12)
    items = (ror or {}).get("items") or []
    best = None
    for it in items[:8]:
        locs = it.get("locations") or []
        cc = ((locs[0].get("geonames_details") or {}).get("country_code") if locs else "") or ""
        if cc == "ID":
            best = it
            break
    if not best and items:
        best = items[0]
    if best:
        for lnk in best.get("links") or []:
            if lnk.get("type") == "website" and lnk.get("value"):
                out["website"] = lnk["value"].rstrip("/")
                out["ror_url"] = best.get("id")
                break
        locs = best.get("locations") or []
        if locs:
            cname = (locs[0].get("geonames_details") or {}).get("name")
            if cname:
                out["city"] = _clean_city_name(cname)
        for nm in best.get("names") or []:
            types = nm.get("types") or []
            if "ror_display" in types and nm.get("value"):
                out["display_name"] = nm["value"]
            if "acronym" in types and nm.get("value") and not out.get("short"):
                out["short"] = nm["value"]

    if not out.get("website") or not out.get("city"):
        oa = _http_get_json("https://api.openalex.org/institutions", params={"search": q, "per-page": 5}, timeout=12)
        res = (oa or {}).get("results") or []
        chosen = None
        for r in res:
            if r.get("country_code") == "ID":
                chosen = r
                break
        if not chosen and res:
            chosen = res[0]
        if chosen:
            if not out.get("website") and chosen.get("homepage_url"):
                out["website"] = chosen["homepage_url"].rstrip("/")
                out["openalex_url"] = chosen.get("id")
            if not out.get("city"):
                geo = chosen.get("geo") or {}
                if geo.get("city"):
                    out["city"] = _clean_city_name(geo["city"])
            if not out.get("short"):
                acrs = chosen.get("display_name_acronyms") or []
                if acrs:
                    out["short"] = acrs[0]
    return out


def _commons_file_to_png_url(filename: str, width: int = 600) -> Tuple[Optional[str], Optional[str]]:
    """Resolve Wikimedia Commons `File:...` to a crisp PNG/JPG render URL + Commons description URL."""
    if not filename:
        return None, None
    clean_name = re.sub(r"^(?:File|Berkas|Image):", "", filename.strip(), flags=re.I).replace(" ", "_")
    for api in ("https://commons.wikimedia.org/w/api.php", "https://id.wikipedia.org/w/api.php", "https://en.wikipedia.org/w/api.php"):
        data = _http_get_json(api, params={
            "action": "query",
            "titles": f"File:{clean_name}",
            "prop": "imageinfo",
            "iiprop": "url|mime|size",
            "iiurlwidth": width,
            "format": "json",
        }, timeout=12)
        pages = ((data or {}).get("query") or {}).get("pages") or {}
        page = next(iter(pages.values()), None)
        if not page or page.get("missing") is not None:
            continue
        infos = page.get("imageinfo") or []
        if not infos:
            continue
        ii = infos[0]
        mime = (ii.get("mime") or "").lower()
        thumb = ii.get("thumburl")
        orig = ii.get("url")
        desc = ii.get("descriptionurl")
        if "svg" in mime or (ii.get("width", 0) > width):
            if thumb:
                return thumb, desc or orig
        if orig and any(x in mime for x in ("png", "jpeg", "jpg", "webp", "gif")):
            return orig, desc or orig
        if thumb:
            return thumb, desc or orig
    return None, None


def _commons_search_logo(universitas: str) -> List[str]:
    """Search Wikimedia Commons directly for university logo/emblem files."""
    files: List[str] = []
    for query in (f'"{universitas}" logo', f'lambang {universitas}', f'seal {universitas}'):
        data = _http_get_json("https://commons.wikimedia.org/w/api.php", params={
            "action": "query",
            "list": "search",
            "srnamespace": 6,
            "srsearch": query,
            "srlimit": 6,
            "format": "json",
        }, timeout=12)
        hits = ((data or {}).get("query") or {}).get("search") or []
        for h in hits:
            t = h.get("title", "")
            tl = t.lower()
            if any(k in tl for k in ("logo", "lambang", "emblem", "seal", "crest", "coat")) and not any(
                b in tl for b in ("bem ", "hima", "ukm", "lkm", "event", "seminar", "wisuda")
            ):
                files.append(re.sub(r"^File:", "", t))
        if files:
            break
    return files


class _SimpleHTMLCollector(HTMLParser):
    """O(N) HTML parser extracting anchors, images, icons, and meta tags safely without regex backtracking."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: List[Tuple[str, str]] = []
        self.imgs: List[Dict[str, str]] = []
        self.links: List[Dict[str, str]] = []
        self.metas: List[Dict[str, str]] = []
        self._in_a = False
        self._a_href = ""
        self._a_buf: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        t = tag.lower()
        d = {k.lower(): (v or "") for k, v in attrs if k}
        if t == "a":
            self._in_a = True
            self._a_href = d.get("href", "")
            self._a_buf = []
        elif t == "img":
            self.imgs.append(d)
        elif t == "link":
            self.links.append(d)
        elif t == "meta":
            self.metas.append(d)

    def handle_data(self, data: str) -> None:
        if self._in_a:
            self._a_buf.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._in_a:
            self.anchors.append((self._a_href, _clean_text("".join(self._a_buf))))
            self._in_a = False
            self._a_href = ""
            self._a_buf = []


def _parse_html_elements(html_text: str) -> _SimpleHTMLCollector:
    parser = _SimpleHTMLCollector()
    try:
        parser.feed(html_text or "")
        parser.close()
    except Exception:
        pass
    return parser


def _scrape_site_logo_candidates(website: str) -> List[str]:
    """Inspect official university website HTML for high-res logo / apple-touch-icon / og:image URLs."""
    urls: List[str] = []
    if not website:
        return urls
    status, html_text, final_url = _http_get(website, headers={"User-Agent": BROWSER_UA}, timeout=8)
    if status != 200 or not html_text:
        return urls
    base = final_url or website
    parsed = _parse_html_elements(html_text)

    def _abs(u: str) -> str:
        return urllib.parse.urljoin(base, u.strip())

    for d in parsed.imgs:
        src = d.get("data-src") or d.get("src") or ""
        blob = " ".join(str(v) for v in d.values()).lower()
        if src and any(k in blob for k in ("logo", "lambang", "crest", "brand", "navbar-brand")):
            if not src.lower().endswith(".svg") and not src.lower().startswith("data:"):
                urls.append(_abs(src))

    for d in parsed.links:
        rel = (d.get("rel") or "").lower()
        href = d.get("href") or ""
        if href and any(r in rel for r in ("apple-touch-icon", "icon", "shortcut")) and not href.lower().endswith(".svg"):
            urls.append(_abs(href))

    for d in parsed.metas:
        if (d.get("property") or "").lower() == "og:image":
            c = d.get("content") or ""
            if c and any(k in c.lower() for k in ("logo", "lambang", "icon")):
                urls.append(_abs(c))

    seen = set()
    uniq = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq[:10]


def _save_valid_logo_png(raw: bytes, out_path: str) -> Tuple[bool, int, int]:
    """Validate raw image bytes via Pillow and write crisp PNG (max 600px side)."""
    if not raw or len(raw) < 400:
        return False, 0, 0
    low_head = raw[:200].lstrip().lower()
    if low_head.startswith(b"<svg") or b"<!doctype html" in low_head or b"<html" in low_head:
        return False, 0, 0
    if not HAS_PIL:
        # Basic PNG/JPG magic check
        if raw.startswith(b"\x89PNG\r\n\x1a\n") or raw.startswith(b"\xff\xd8"):
            os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
            with open(out_path, "wb") as f:
                f.write(raw)
            return True, 0, 0
        return False, 0, 0
    try:
        im = Image.open(io.BytesIO(raw))
        im.load()
        w, h = im.size
        if min(w, h) < 48:
            return False, 0, 0
        ratio = w / max(1, h)
        if ratio < 0.25 or ratio > 4.0:
            return False, 0, 0
        if im.mode not in ("RGBA", "RGB"):
            im = im.convert("RGBA")
        if max(w, h) > 640:
            im.thumbnail((640, 640), Image.Resampling.LANCZOS)
            w, h = im.size
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        im.save(out_path, format="PNG")
        return True, w, h
    except Exception:
        return False, 0, 0


def _score_logo_filename(fn: str, universitas: str, from_curated_infobox: bool = False) -> int:
    """Rank Wikimedia/Wikipedia logo filenames so main university crest beats faculty sub-logos or event graphics."""
    low = fn.lower()
    score = 0
    if any(k in low for k in ("lambang", "seal", "crest", "emblem", "coat_of_arms", "makara", "logo", "official")):
        score += 20
    if low.endswith(".svg"):
        score += 12
    faculty_or_weak_tags = (
        "feb", "filkom", "fmipa", "ft_", "fk_", "fh_", "fisip", "fia", "fib", "fapet", "faperta",
        "fkg", "fkm", "vokasi", "pascasarjana", "wordmark", "banner", "hanya_teks", "text_only",
        "teks_saja", "monochrome", "white", "putih",
    )
    if any(t in low for t in faculty_or_weak_tags):
        score -= 55
    noise_tags = ("pimnas", "baku", "dies", "wisuda", "seminar", "conference", "bem", "hima", "ukm", "kkn", "ospek", "pkkmb")
    if any(t in low for t in noise_tags):
        score -= 120

    generic_words = {
        "universitas", "institut", "politeknik", "sekolah", "tinggi", "negeri", "swasta",
        "islam", "katolik", "kristen", "muhammadiyah", "indonesia", "nasional",
        "sains", "teknologi", "semarang", "jakarta", "bandung", "surabaya", "yogyakarta", "malang",
    }
    acr = _infer_short_name(universitas).lower()
    acr_tokens = [t for t in re.split(r"[\s\-]+", acr) if len(t) >= 2]
    distinct_words = [w for w in re.split(r"\s+", (universitas or "").lower()) if len(w) > 3 and w not in generic_words]

    matched_identity = False
    for tok in acr_tokens:
        if re.search(rf"(?<![a-z0-9]){re.escape(tok)}(?![a-z0-9])", low):
            score += 32
            matched_identity = True
            break
    for w in distinct_words:
        if w in low:
            score += 16
            matched_identity = True
    if not from_curated_infobox and not matched_identity and (distinct_words or acr_tokens):
        score -= 50
    return score


def cari_dan_unduh_logo_kampus(
    universitas: str,
    website: str = "",
    out_path: Optional[str] = None,
    wiki_info: Optional[Dict[str, Any]] = None,
    wd_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Cari logo resmi kampus lewat Wikimedia Commons, Wikipedia, ROR, dan situs .ac.id lalu simpan sebagai PNG."""
    out_path = out_path or os.path.abspath("logo_kampus.png")
    wiki_info = wiki_info if wiki_info is not None else (_wikipedia_lookup(universitas) if universitas else {})
    if wd_info is None and wiki_info.get("qid"):
        wd_info = _wikidata_entity_lookup(wiki_info["qid"])
    wd_info = wd_info or {}

    target_site = website or wd_info.get("website") or wiki_info.get("website") or ""
    attempts: List[Tuple[str, str, str]] = []  # (method, url, source_page)

    # Collect & score Wikimedia Commons files: Wikipedia infobox usually holds main seal, plus all Wikidata logo claims
    raw_commons: List[Tuple[str, str]] = []
    if wiki_info.get("commons_logo_file"):
        raw_commons.append((wiki_info["commons_logo_file"], "Wikipedia"))
    for cf_wd in wd_info.get("commons_logo_files") or ([wd_info["commons_logo_file"]] if wd_info.get("commons_logo_file") else []):
        raw_commons.append((cf_wd, "Wikidata"))
    for cf in _commons_search_logo(universitas):
        raw_commons.append((cf, "Wikimedia Commons Search"))

    # Deduplicate then sort by score descending (ties keep original priority: Wikipedia -> Wikidata -> Commons Search)
    seen_files = set()
    uniq_commons: List[Tuple[int, int, str, str]] = []
    for idx_ord, (cf, label) in enumerate(raw_commons):
        norm = cf.lower().replace(" ", "_")
        if norm in seen_files:
            continue
        seen_files.add(norm)
        bonus = 35 if label == "Wikipedia" else (15 if label == "Wikidata" else 0)
        uniq_commons.append((-(_score_logo_filename(cf, universitas, from_curated_infobox=(label in ("Wikipedia", "Wikidata"))) + bonus), idx_ord, cf, label))
    uniq_commons.sort()

    for _, _, cf, label in uniq_commons:
        dl_url, desc_url = _commons_file_to_png_url(cf, width=600)
        if dl_url:
            attempts.append((label, dl_url, desc_url or dl_url))

    if wiki_info.get("pageimage_url"):
        attempts.append(("Wikipedia PageImage", wiki_info["pageimage_url"], wiki_info.get("wikipedia_url") or wiki_info["pageimage_url"]))

    # Official campus site HTML logo/icon
    if target_site:
        for img_url in _scrape_site_logo_candidates(target_site):
            attempts.append(("Situs Resmi Kampus", img_url, target_site))

    for method, dl_url, src_url in attempts:
        status, raw, final_url = _http_get(
            dl_url,
            headers={"User-Agent": USER_AGENT if "wikimedia" in dl_url or "wikipedia" in dl_url else BROWSER_UA},
            timeout=14,
            binary=True,
        )
        if status == 200 and isinstance(raw, (bytes, bytearray)):
            ok, w, h = _save_valid_logo_png(bytes(raw), out_path)
            if ok:
                sha = hashlib.sha256(bytes(raw)).hexdigest()[:16]
                return {
                    "ok": True,
                    "path": out_path,
                    "width": w,
                    "height": h,
                    "method": method,
                    "download_url": final_url or dl_url,
                    "source_url": src_url,
                    "sha256": sha,
                }

    return {
        "ok": False,
        "path": None,
        "width": 0,
        "height": 0,
        "method": "none",
        "download_url": None,
        "source_url": None,
        "error": f"Logo resmi untuk '{universitas}' tidak berhasil diunduh otomatis.",
    }


def _duckduckgo_search(query: str, max_results: int = 8) -> List[Dict[str, str]]:
    """Query DuckDuckGo HTML search endpoint without requiring API key (O(N) HTML parsing)."""
    results: List[Dict[str, str]] = []
    status, text, _ = _http_get(
        "https://html.duckduckgo.com/html/",
        params={"q": query, "kl": "id-id"},
        headers={
            "User-Agent": BROWSER_UA,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
        },
        timeout=8,
    )
    if status != 200 or not text:
        return results

    parsed = _parse_html_elements(text)
    for href_raw, title in parsed.anchors:
        if "duckduckgo.com" in href_raw and "uddg=" not in href_raw:
            continue
        href = href_raw
        if "uddg=" in href:
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
            if "uddg" in qs:
                href = qs["uddg"][0]
        if href.startswith("http") and "duckduckgo.com" not in href and len(title) >= 4:
            results.append({"title": title, "url": href, "snippet": ""})
            if len(results) >= max_results:
                break
    return results


def _html_to_lines(html_text: str) -> List[str]:
    txt = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", html_text or "", flags=re.I | re.S)
    txt = re.sub(r"</?(?:p|div|li|tr|td|th|h[1-6]|br|section|article|span)[^>]*>", "\n", txt, flags=re.I)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html.unescape(txt)
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in txt.splitlines()]
    return [ln for ln in lines if ln]


# Pattern nama akademisi bergelar Indonesia (termasuk nama tunggal bergelar seperti "Prof. Dr. Suharnomo, S.E., M.Si.")
_ACADEMIC_NAME_RE = re.compile(
    r"(?:"
    r"(?:(?:Prof\.|Dr\.|Dr\.\s*rer\.?\s*nat\.?|Ir\.|H\.|Hj\.|Drs\.|Dra\.|Ns\.|Apt\.|drg?\.|K\.?H\.?)\s+){1,4}"
    r"[A-Z][a-zA-Z'`\-]+(?:\s+[A-Z][a-zA-Z'`\-\.]+){0,5}"
    r"|"
    r"[A-Z][a-zA-Z'`\-]+(?:\s+[A-Z][a-zA-Z'`\-\.]+){1,5}"
    r")"
    r"(?:,\s*(?:S\.\s*[A-Za-z\.]+|M\.\s*[A-Za-z\.]+|B\.\s*[A-Za-z\.]+|Ph\.?\s*D\.?|D\.?\s*Sc\.?|Ed\.?\s*D\.?|Dr\.|Sp\.\s*[A-Za-z\.]+|IPM|ASEAN\s*Eng\.?|CPMA|Ak\.?|CA|MM|MT|MH|MSc|MA))+",
)
_PREFIXED_NAME_RE = re.compile(
    r"(?:Prof\.|Dr\.|Ir\.)\s+(?:(?:Dr\.|Dr\.\s*rer\.?\s*nat\.?|Ir\.|H\.|Hj\.)\s+)?[A-Z][a-zA-Z'`\-]+(?:\s+[A-Z][a-zA-Z'`\-\.]+){1,4}"
    r"(?:,\s*[A-Za-z\.\s]{2,14})*"
)
_NIP_RE = re.compile(r"\b(?:NIP|NIP\.|NIDN|NIDN\.|NIK|NIK\.|NUPTK)\s*[:.]?\s*([0-9][0-9\s\-]{7,23}[0-9])\b", re.I)


def _extract_official_from_text_window(
    lines: List[str],
    role_patterns: List[str],
    context_keywords: List[str],
    exclude_patterns: Optional[List[str]] = None,
    faculty_kws: Optional[List[str]] = None,
    program_kws: Optional[List[str]] = None,
) -> Optional[Dict[str, str]]:
    """Find best verified Indonesian academic name + optional NIP/NIDN near a leadership title line."""
    excl = exclude_patterns or []
    is_dean_search = any("dekan" in rp.lower() or "dean" in rp.lower() for rp in role_patterns)
    is_rector_search = any("rektor" in rp.lower() or "rector" in rp.lower() for rp in role_patterns)
    is_head_search = any(k in rp.lower() for rp in role_patterns for k in ("kaprodi", "program", "departemen", "chair"))
    for idx, ln in enumerate(lines):
        if excl and any(re.search(ep, ln, flags=re.I) for ep in excl):
            continue
        if not any(re.search(rp, ln, flags=re.I) for rp in role_patterns):
            continue
        win_start = max(0, idx - 3)
        win_end = min(len(lines), idx + 6)
        window_text = "\n".join(lines[win_start:win_end])
        if context_keywords:
            tight_ctx = "\n".join(lines[max(0, idx - 1):min(len(lines), idx + 2)]).lower()
            w_low = tight_ctx if is_head_search else window_text.lower()
            if not any(kw in w_low for kw in context_keywords):
                continue

        # Reject explicit different-faculty mention (e.g. "Dekan Fakultas Kedokteran" when looking for Ilmu Komputer)
        if is_dean_search and faculty_kws:
            fac_mentions = re.findall(r"\b(?:Dekan|Dean\s+of)\s+(?:Fakultas|Faculty\s+of)\s+([A-Za-z\s,&\-]{3,45})", ln, flags=re.I)
            if fac_mentions and not any(any(fk in fm.lower() for fk in faculty_kws) for fm in fac_mentions):
                continue
        # Reject explicit different-prodi mention (e.g. "Ketua Program Studi Pendidikan Matematika" when looking for Teknologi Informasi)
        if is_head_search and program_kws:
            prodi_mentions = re.findall(
                r"\b(?:Ketua\s+Program\s+Studi|Kaprodi|Koordinator\s+Program\s+Studi|Ketua\s+Jurusan|Ketua\s+Departemen)\s+([A-Za-z0-9\s,&\-\(\)]{3,55})",
                ln,
                flags=re.I,
            )
            if prodi_mentions and not any(any(pk in pm.lower() for pk in program_kws) for pm in prodi_mentions):
                continue

        # Search current line, previous 2 lines, and next 3 lines (skipping lines mentioning Wakil/Vice/Secretary)
        search_order = [ln]
        for off in (-1, 1, -2, 2, 3):
            pos = idx + off
            if 0 <= pos < len(lines):
                cand = lines[pos]
                if excl and any(re.search(ep, cand, flags=re.I) for ep in excl):
                    continue
                search_order.append(cand)

        for cand_line in search_order:
            role_spans = [(mr.start(), mr.end()) for rp in role_patterns for mr in re.finditer(rp, cand_line, flags=re.I)]
            for pat in (_ACADEMIC_NAME_RE, _PREFIXED_NAME_RE):
                for m in pat.finditer(cand_line):
                    name = _clean_person_name(m.group(0))
                    # On multi-person paragraphs, only accept name close to the matching role token
                    if role_spans and len(cand_line) > 100:
                        dist = min(min(abs(m.start() - rs), abs(m.end() - re_)) for rs, re_ in role_spans)
                        if dist > 95:
                            continue
                    # Avoid grabbing someone whose adjacent parenthetical explicitly assigns a different role
                    after_ctx = cand_line[m.end():m.end() + 55].lower()
                    paren_m = re.match(r"^\s*\(([^)]{2,60})\)", after_ctx)
                    if paren_m:
                        ptxt = paren_m.group(1)
                        if is_dean_search and "dekan" not in ptxt and "dean" not in ptxt:
                            if re.search(r"rektor|wakil|ketua|sekretaris|direktur|kepala|mwa|senat", ptxt):
                                continue
                        elif is_rector_search and "rektor" not in ptxt and "rector" not in ptxt:
                            if re.search(r"dekan|wakil|ketua|sekretaris|direktur|kepala|mwa|senat", ptxt):
                                continue
                    if _is_plausible_person_name(name):
                        nip_m = _NIP_RE.search(window_text)
                        nip_val = re.sub(r"\s+", "", nip_m.group(1)) if nip_m else ""
                        return {
                            "name": name,
                            "nip": nip_val,
                            "snippet": _clean_text(f"{ln} | {cand_line}")[:220],
                        }
    return None


def _extract_links(html_text: str, base_url: str, root_domain: str) -> List[Tuple[str, str]]:
    """Extract same-institution <a href> links as (abs_url, link_text) in O(N) using HTMLParser."""
    out: List[Tuple[str, str]] = []
    if not html_text or not base_url:
        return out
    parsed = _parse_html_elements(html_text)
    seen = set()
    for href_raw, txt in parsed.anchors:
        h_s = (href_raw or "").strip()
        if not h_s or h_s.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        abs_u = urllib.parse.urljoin(base_url, h_s).split("#")[0]
        dom = _extract_domain(abs_u)
        if root_domain and root_domain not in dom:
            continue
        if abs_u in seen:
            continue
        seen.add(abs_u)
        out.append((abs_u, txt))
    return out


_COMMON_FACULTY_SUBDOMAINS: List[Tuple[Tuple[str, ...], List[str]]] = [
    (("ilmu komputer", "informatika", "teknologi informasi", "fakultas ilmu komputer"), ["filkom", "cs", "fasilkom", "ilkom", "fti"]),
    (("teknik", "engineering", "sekolah teknik elektro"), ["ft", "stei", "teknik"]),
    (("matematika", "ilmu pengetahuan alam", "sains", "mipa"), ["fmipa", "mipa", "fsains", "fst"]),
    (("ekonomi", "bisnis"), ["feb", "fe"]),
    (("hukum",), ["fh", "hukum"]),
    (("kedokteran",), ["fk", "kedokteran"]),
    (("ilmu sosial", "ilmu politik", "fisip"), ["fisip"]),
    (("ilmu budaya", "sastra", "humaniora"), ["fib", "fs"]),
    (("ilmu pendidikan", "keguruan"), ["fkip", "fip"]),
    (("pertanian",), ["fp", "faperta"]),
    (("ilmu administrasi",), ["fia"]),
    (("psikologi",), ["fpsi", "psikologi"]),
]


def _guess_faculty_urls(root_domain: str, fakultas: str) -> List[str]:
    if not root_domain or not fakultas.strip():
        return []
    low = fakultas.lower()
    urls: List[str] = []
    for kws, subs in _COMMON_FACULTY_SUBDOMAINS:
        if any(k in low for k in kws):
            for s in subs:
                urls.append(f"https://{s}.{root_domain}")
    return urls[:4]


def _follow_meta_refresh(html_text: str, base_url: str) -> Optional[str]:
    if not html_text or len(html_text) > 4096:
        return None
    m = re.search(r'<meta[^>]+http-equiv\s*=\s*["\']?refresh["\']?[^>]+content\s*=\s*["\'][^"\']*url\s*=\s*([^"\'\s;>]+)', html_text, flags=re.I)
    if m:
        return urllib.parse.urljoin(base_url, html.unescape(m.group(1).strip()))
    return None


def _crawl_campus_official_pages(
    website: str,
    domain: str,
    fakultas: str = "",
    program_studi: str = "",
) -> Tuple[Dict[str, Dict[str, str]], List[Dict[str, str]]]:
    """
    Crawl official .ac.id homepage + faculty portal (1-2 hops, bounded concurrency)
    to extract verified officials (Rektor, Dekan, Kaprodi + NIP) and official Pedoman PDFs.
    """
    found: Dict[str, Dict[str, str]] = {}
    pdfs: List[Dict[str, str]] = []
    if not website:
        return found, pdfs

    base_site = website if website.startswith("https://") else website.replace("http://", "https://", 1)
    st, home_html, final_home = _http_get(base_site, headers={"User-Agent": BROWSER_UA}, timeout=5)
    if st != 200 or not home_html:
        st, home_html, final_home = _http_get(website, headers={"User-Agent": BROWSER_UA}, timeout=5)
    if st != 200 or not home_html:
        return found, pdfs

    home_url = final_home or base_site
    root_dom = _extract_domain(home_url) or domain
    home_links = _extract_links(home_html, home_url, root_dom)

    fk_short = re.sub(r"^fakultas\s+", "", fakultas.strip(), flags=re.I)
    fk_kws = [w.lower() for w in fk_short.split() if len(w) > 3]
    ps_short = re.sub(r"^(?:program\s+studi|prodi|s1|d3|d4)\s+", "", program_studi.strip(), flags=re.I)
    ps_kws = [w.lower() for w in ps_short.split() if len(w) > 3]

    faculty_subdomains: List[str] = []
    faculty_root_links: List[str] = []
    uni_leader_pages: List[str] = [home_url]
    for suffix in ("/pimpinan", "/id/pimpinan", "/profil/pimpinan", "/en/leadership"):
        u_root_p = home_url.rstrip("/") + suffix
        if u_root_p not in uni_leader_pages:
            uni_leader_pages.append(u_root_p)
    seen_pdf = set()
    _NEWS_RE = re.compile(r"/20\d{2}/|/berita/|/news/|/artikel/|/siaran-pers|/berkunjung|/kunjungan|/event/", re.I)

    for u, txt in home_links:
        ul = u.lower()
        tl = txt.lower()
        if ul.endswith(".pdf") and any(k in f"{ul} {tl}" for k in ("pedoman", "panduan", "skripsi", "tugas-akhir", "tugas akhir")):
            if u not in seen_pdf:
                seen_pdf.add(u)
                pdfs.append({"title": txt or os.path.basename(u), "url": u, "snippet": f"Tautan langsung di {home_url}"})
            continue
        if _NEWS_RE.search(ul):
            continue
        if fk_kws and (all(k in f"{ul} {tl}" for k in fk_kws[:2]) or any(k in tl and ("fakultas" in tl or "faculty" in tl) for k in fk_kws)):
            if _extract_domain(u) != root_dom:
                if u not in faculty_subdomains:
                    faculty_subdomains.append(u)
            elif u not in faculty_root_links:
                faculty_root_links.append(u)
        if any(k in f"{ul} {tl}" for k in ("pimpinan", "leadership", "rektor", "rector", "profil", "profile", "struktur", "manajemen")):
            if len(uni_leader_pages) < 7 and u not in uni_leader_pages:
                uni_leader_pages.append(u)

    faculty_portals: List[str] = list(faculty_subdomains)
    for gu in _guess_faculty_urls(root_dom, fakultas):
        if gu not in faculty_portals:
            faculty_portals.append(gu)
    for fu_l in faculty_root_links:
        if fu_l not in faculty_portals:
            faculty_portals.append(fu_l)

    faculty_portal_roots: List[str] = []
    faculty_pages: List[str] = []
    prodi_pages: List[str] = []

    def _fetch_one(target_u: str) -> Tuple[str, int, str, str]:
        s, body, fu = _http_get(target_u, headers={"User-Agent": BROWSER_UA}, timeout=5)
        if s == 200 and body and len(body) < 4096:
            ref = _follow_meta_refresh(body, fu or target_u)
            if ref:
                s, body, fu = _http_get(ref, headers={"User-Agent": BROWSER_UA}, timeout=5)
        return target_u, s, body or "", fu or target_u

    if faculty_portals:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
            for _, s, body, fu in ex.map(_fetch_one, faculty_portals[:6]):
                if s != 200 or not body or len(body) < 2000:
                    continue
                if _extract_domain(fu) != root_dom or any(kw in fu.lower() for kw in fk_kws):
                    if fu not in faculty_portal_roots:
                        faculty_portal_roots.append(fu)
                if fu not in faculty_pages:
                    faculty_pages.append(fu)
                f_links = _extract_links(body, fu, root_dom)
                for u, txt in f_links:
                    ul = u.lower()
                    tl = txt.lower()
                    if ul.endswith(".pdf") and any(k in f"{ul} {tl}" for k in ("pedoman", "panduan", "skripsi", "tugas-akhir", "tugas akhir")):
                        if u not in seen_pdf:
                            seen_pdf.add(u)
                            pdfs.append({"title": txt or os.path.basename(u), "url": u, "snippet": f"Tautan langsung di {fu}"})
                        continue
                    if _NEWS_RE.search(ul):
                        continue
                    if any(k in f"{ul} {tl}" for k in ("pimpinan", "dekan", "dean", "leadership", "management", "struktur", "pengelola", "organisasi", "about", "tentang", "profil")):
                        if u not in faculty_pages:
                            faculty_pages.append(u)
                    if ps_kws and any(k in f"{ul} {tl}" for k in ps_kws) and any(k in f"{ul} {tl}" for k in ("prodi", "program-studi", "program studi", "departemen", "jurusan", "sarjana", "s1", "ilkom", "informatika", "komputer")):
                        if u not in prodi_pages:
                            prodi_pages.append(u)
                parsed_f = urllib.parse.urlparse(fu)
                f_root = f"{parsed_f.scheme}://{parsed_f.netloc}"
                for suffix in ("/pimpinan", "/id/pimpinan", "/id/profil/pimpinan", "/en/profile/leadership", "/profil/pimpinan", "/dekanat", "/struktur-organisasi"):
                    probe_u = f_root + suffix
                    if probe_u not in faculty_pages:
                        faculty_pages.append(probe_u)

    all_inspect: List[str] = []
    for u in (prodi_pages[:4] + faculty_pages[:8] + uni_leader_pages[:5]):
        if u not in all_inspect and not u.lower().endswith((".pdf", ".jpg", ".png", ".zip")):
            all_inspect.append(u)
    all_inspect = all_inspect[:12]

    role_specs = [
        ("rector", [r"^\s*Rektor(?:\s+[A-Z0-9\.\-]{2,20})?\s*$|\bRektor\s+Universitas\b|\bRektor\s+mengemban\b|\bRector\b"], [r"Wakil\s+Rektor|Vice\s+Rector|Sekretaris|Senat|Mantan|Sambutan|Ketua\s+MWA|membantu\s+Rektor|oleh\s+Rektor|bersama\s+Rektor|tugas\s+Rektor|kepada\s+Rektor"], []),
        ("dean", [r"\bDekan\b|\bDean\s+of\b"], [r"Wakil\s+Dekan|Vice\s+Dean|Pembantu\s+Dekan|Plt\.?\s*Wakil|Mantan"], []),
        ("head_program", [r"\b(?:Ketua\s+Program\s+Studi|Kaprodi|Koordinator\s+Program\s+Studi|Ketua\s+Departemen|Head\s+of\s+(?:Study\s+Program|Department)|Chair\s+of)\b"], [r"Sekretaris\s+(?:Program|Departemen)|Wakil"], ps_kws),
    ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for _, s, body, fu in ex.map(_fetch_one, all_inspect):
            if s != 200 or not body:
                continue
            for lu, ltxt in _extract_links(body, fu, root_dom):
                lul = lu.lower()
                ltl = ltxt.lower()
                if lul.endswith(".pdf") and any(k in f"{lul} {ltl}" for k in ("pedoman", "panduan", "skripsi", "tugas-akhir", "tugas akhir")):
                    if lu not in seen_pdf:
                        seen_pdf.add(lu)
                        pdfs.append({"title": ltxt or os.path.basename(lu), "url": lu, "snippet": f"Ditemukan di {fu}"})
            if _NEWS_RE.search(fu):
                continue
            lines = _html_to_lines(body)
            is_dedicated_faculty = (
                _extract_domain(fu) != root_dom
                or any(fu == fp or fu.startswith(fp.rstrip("/") + "/") for fp in faculty_portal_roots)
            )
            for role, rpats, epats, ckws in role_specs:
                if role in found:
                    continue
                if role == "dean":
                    use_ckws = [] if is_dedicated_faculty else fk_kws
                elif role == "head_program":
                    use_ckws = [] if fu in prodi_pages else ps_kws
                else:
                    use_ckws = ckws
                res = _extract_official_from_text_window(
                    lines, rpats, use_ckws, exclude_patterns=epats,
                    faculty_kws=fk_kws if role == "dean" else None,
                    program_kws=ps_kws if role == "head_program" else None,
                )
                if res:
                    res["source_url"] = fu
                    res["source_label"] = "Situs Resmi Kampus"
                    found[role] = res

    return found, pdfs


def _search_officials_on_web(
    domain: str,
    universitas: str,
    fakultas: str = "",
    program_studi: str = "",
) -> Dict[str, Dict[str, str]]:
    """Search official .ac.id pages via DuckDuckGo Lite/HTML fallback when direct site crawl didn't find them."""
    found: Dict[str, Dict[str, str]] = {}
    site_filter = f"site:{domain}" if domain else f'"{universitas}"'

    queries: List[Tuple[str, str, List[str], List[str], List[str]]] = []
    if fakultas.strip():
        fk_short = re.sub(r"^fakultas\s+", "", fakultas.strip(), flags=re.I)
        fk_kws = [w.lower() for w in fk_short.split() if len(w) > 3]
        queries.append((
            "dean",
            f'{site_filter} "Dekan" "{fakultas.strip()}"',
            [r"\bDekan\b"],
            [r"Wakil\s+Dekan|Pembantu\s+Dekan"],
            fk_kws,
        ))
    if program_studi.strip():
        ps_clean = re.sub(r"^(?:program\s+studi|prodi|s1|d3|d4)\s+", "", program_studi.strip(), flags=re.I)
        ps_kws = [w.lower() for w in ps_clean.split() if len(w) > 3]
        queries.append((
            "head_program",
            f'{site_filter} ("Ketua Program Studi" OR "Kaprodi" OR "Koordinator Program Studi") "{ps_clean}"',
            [r"\b(?:Ketua\s+Program\s+Studi|Kaprodi|Koordinator\s+Program\s+Studi|Ketua\s+Jurusan)\b"],
            [r"Sekretaris\s+Program"],
            ps_kws,
        ))

    visited_urls: Dict[str, List[str]] = {}
    for role, q, role_pats, excl_pats, ctx_kws in queries:
        hits = _duckduckgo_search(q, max_results=3)
        for h in hits[:2]:
            u = h["url"]
            if domain and domain not in _extract_domain(u):
                continue
            if u not in visited_urls:
                st, body, _ = _http_get(u, headers={"User-Agent": BROWSER_UA}, timeout=7)
                visited_urls[u] = _html_to_lines(body) if st == 200 and body else []
            lines = visited_urls[u]
            if lines:
                res = _extract_official_from_text_window(
                    lines, role_pats, ctx_kws, exclude_patterns=excl_pats,
                    faculty_kws=ctx_kws if role == "dean" else None,
                )
                if res:
                    res["source_url"] = u
                    res["source_label"] = "Situs Resmi Kampus"
                    found[role] = res
                    break
            snip_lines = [h.get("title", ""), h.get("snippet", "")]
            res_sn = _extract_official_from_text_window(
                snip_lines, role_pats, ctx_kws, exclude_patterns=excl_pats,
                faculty_kws=ctx_kws if role == "dean" else None,
            )
            if res_sn:
                res_sn["source_url"] = u
                res_sn["source_label"] = "Indeks Situs Resmi"
                found[role] = res_sn
                break
    return found


def cari_pedoman_kampus_online(
    universitas: str,
    fakultas: str = "",
    program_studi: str = "",
    domain: str = "",
    limit: int = 5,
) -> List[Dict[str, str]]:
    """Cari tautan PDF pedoman penulisan skripsi / tugas akhir resmi kampus di internet."""
    if not universitas.strip():
        return []
    parts = [f'"{universitas.strip()}"']
    if fakultas.strip():
        parts.append(f'"{fakultas.strip()}"')
    q_base = " ".join(parts)
    queries = [f'filetype:pdf ("pedoman penulisan skripsi" OR "panduan tugas akhir" OR "pedoman tugas akhir") {q_base}']
    if domain:
        queries.append(f'site:{domain} filetype:pdf ("pedoman" OR "panduan") ("skripsi" OR "tugas akhir")')

    seen = set()
    pdfs: List[Dict[str, str]] = []
    for q in queries:
        for h in _duckduckgo_search(q, max_results=limit + 3):
            u = h["url"]
            if u in seen:
                continue
            if ".pdf" in u.lower() or "pedoman" in h["title"].lower() or "panduan" in h["title"].lower():
                seen.add(u)
                pdfs.append({
                    "title": h["title"] or os.path.basename(urllib.parse.urlparse(u).path) or "Pedoman Kampus",
                    "url": u,
                    "snippet": h.get("snippet", ""),
                })
                if len(pdfs) >= limit:
                    return pdfs
    return pdfs


def unduh_pedoman_pdf(url: str, out_path: str) -> Dict[str, Any]:
    """Unduh PDF pedoman kampus dan pastikan header `%PDF-` valid."""
    status, raw, final_url = _http_get(url, headers={"User-Agent": BROWSER_UA}, timeout=15, binary=True)
    if status == 200 and isinstance(raw, (bytes, bytearray)) and bytes(raw).lstrip().startswith(b"%PDF-"):
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(bytes(raw))
        return {"ok": True, "path": out_path, "url": final_url or url, "size": len(raw)}
    return {"ok": False, "path": None, "url": url, "error": f"Bukan file PDF valid (HTTP {status})."}


def cari_identitas_dan_pejabat_kampus(
    universitas: str,
    fakultas: str = "",
    program_studi: str = "",
    city_hint: str = "",
    short_hint: str = "",
    deep_official_search: bool = True,
    download_logo_to: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Orkestrator pencarian identitas kampus, logo resmi, gelar lulusan,
    kota kampus, kementerian, dan pejabat (Rektor, Dekan, Kaprodi + NIP/NIDN).
    """
    univ_raw = (universitas or "").strip()
    if not univ_raw:
        return {"ok": False, "error": "Nama universitas kosong.", "fields": {}, "logo": {"ok": False}}
    univ_in = ALIAS_TO_UNIVERSITY.get(univ_raw.lower(), univ_raw)

    wiki = _wikipedia_lookup(univ_in)
    wd = _wikidata_entity_lookup(wiki["qid"]) if wiki.get("qid") else {}
    ror = _ror_openalex_lookup(univ_in)

    official_univ = wd.get("official_name") or ror.get("display_name") or wiki.get("title") or univ_in
    # Preserve Indonesian casing/preference if input was Indonesian and English Wikipedia returned English
    if "university of" in official_univ.lower() and "universitas" in univ_in.lower():
        official_univ = univ_in

    website = wd.get("website") or wiki.get("website") or ror.get("website") or ""
    domain = _extract_domain(website)

    known_short = COMMON_ACRONYMS.get(re.sub(r"\s+", " ", official_univ.lower()))
    known_short = known_short or COMMON_ACRONYMS.get(re.sub(r"\s+", " ", univ_in.lower()))
    short_name = short_hint.strip() or known_short or wd.get("short") or wiki.get("short") or ror.get("short") or _infer_short_name(official_univ)
    city = city_hint.strip() or ror.get("city") or wiki.get("city") or wd.get("city") or ""
    ministry = _infer_ministry(official_univ, wiki.get("type", ""))
    degree = _infer_degree(program_studi)

    fields: Dict[str, Dict[str, Any]] = {}

    def _set_field(key: str, value: str, verified: bool, source_label: str, source_url: str = "", snippet: str = "") -> None:
        if value:
            fields[key] = {
                "value": value,
                "verified": verified,
                "source_label": source_label,
                "source_url": source_url,
                "snippet": snippet,
            }

    _set_field(
        "university",
        official_univ,
        bool(wd.get("official_name") or wiki.get("title") or ror.get("display_name")),
        "Wikidata/Wikipedia/ROR" if (wd or wiki or ror) else "Input Pengguna",
        wd.get("wikidata_url") or wiki.get("wikipedia_url") or ror.get("ror_url") or "",
    )
    _set_field("short", short_name, bool(wd.get("short") or wiki.get("short") or ror.get("short") or short_name in COMMON_ACRONYMS.values()), "Singkatan Kampus", website)
    if website:
        _set_field("website", website, True, "Situs Resmi Kampus", website)
    if city:
        _set_field("city", city, bool(wd.get("city") or wiki.get("city") or ror.get("city")), "Wikidata/Wikipedia/ROR", wd.get("wikidata_url") or wiki.get("wikipedia_url") or "")
    if ministry:
        _set_field("ministry", ministry, True, "Klasifikasi PTN/PTKIN Indonesia", wiki.get("wikipedia_url") or "")
    if degree:
        _set_field("degree", degree, False, "Pemetaan Gelar SN-Dikti (periksa ulang sesuai SK Prodi)", "")
    if fakultas.strip():
        _set_field("faculty", fakultas.strip(), False, "Input Pengguna", "")
    if program_studi.strip():
        _set_field("program", program_studi.strip(), False, "Input Pengguna", "")

    # Rector from Wikidata / Wikipedia first
    if wd.get("rector"):
        _set_field("rector", wd["rector"], True, "Wikidata (P1075)", wd.get("wikidata_url", ""))
    elif wiki.get("rector"):
        _set_field("rector", wiki["rector"], True, "Wikipedia Infobox", wiki.get("rector_source") or wiki.get("wikipedia_url", ""))

    # Deep search on official campus domain for Dean, Head of Program, and Rector confirmation
    web_officials: Dict[str, Dict[str, str]] = {}
    site_pdfs: List[Dict[str, str]] = []
    if deep_official_search and (website or domain or univ_in):
        site_officials, site_pdfs = _crawl_campus_official_pages(website, domain, fakultas=fakultas, program_studi=program_studi)
        web_officials.update(site_officials)
        missing_roles = [r for r in ("dean", "head_program") if r not in web_officials]
        if missing_roles:
            ddg_off = _search_officials_on_web(domain, official_univ, fakultas=fakultas, program_studi=program_studi)
            for k, v in ddg_off.items():
                if k not in web_officials:
                    web_officials[k] = v
        if "rector" in web_officials:
            r_info = web_officials["rector"]
            _set_field("rector", r_info["name"], True, r_info["source_label"], r_info["source_url"], r_info.get("snippet", ""))
            if r_info.get("nip"):
                _set_field("id_rector", r_info["nip"], True, r_info["source_label"], r_info["source_url"])
        if "dean" in web_officials:
            d_info = web_officials["dean"]
            _set_field("dean", d_info["name"], True, d_info["source_label"], d_info["source_url"], d_info.get("snippet", ""))
            if d_info.get("nip"):
                _set_field("id_dean", d_info["nip"], True, d_info["source_label"], d_info["source_url"])
        if "head_program" in web_officials:
            h_info = web_officials["head_program"]
            _set_field("head_program", h_info["name"], True, h_info["source_label"], h_info["source_url"], h_info.get("snippet", ""))
            if h_info.get("nip"):
                _set_field("id_head", h_info["nip"], True, h_info["source_label"], h_info["source_url"])

    # Logo lookup + optional download
    logo_res: Dict[str, Any] = {"ok": False}
    if download_logo_to:
        logo_res = cari_dan_unduh_logo_kampus(
            official_univ,
            website=website,
            out_path=download_logo_to,
            wiki_info=wiki,
            wd_info=wd,
        )

    sources = []
    for k in ("wikipedia_url",):
        if wiki.get(k):
            sources.append({"label": "Wikipedia", "url": wiki[k]})
    if wd.get("wikidata_url"):
        sources.append({"label": "Wikidata", "url": wd["wikidata_url"]})
    if ror.get("ror_url"):
        sources.append({"label": "ROR Registry", "url": ror["ror_url"]})
    if website:
        sources.append({"label": "Website Resmi", "url": website})
    if logo_res.get("ok") and logo_res.get("source_url"):
        sources.append({"label": f"Logo ({logo_res.get('method')})", "url": logo_res["source_url"]})

    return {
        "ok": True,
        "query": {"university": univ_in, "faculty": fakultas, "program": program_studi},
        "fields": fields,
        "logo": logo_res,
        "website": website,
        "domain": domain,
        "sources": sources,
        "site_pedoman_pdfs": site_pdfs,
    }


def _cli() -> None:
    import argparse
    ap = argparse.ArgumentParser(description="MuZA Skripsi Online Campus Identity & Logo Lookup")
    ap.add_argument("--universitas", required=True, help="Nama universitas")
    ap.add_argument("--fakultas", default="", help="Nama fakultas")
    ap.add_argument("--prodi", default="", help="Nama program studi")
    ap.add_argument("--logo-out", default="", help="Path output PNG untuk logo kampus")
    ap.add_argument("--find-pedoman", action="store_true", help="Cari link PDF pedoman skripsi kampus")
    ap.add_argument("--no-deep", action="store_true", help="Skip pencarian situs resmi untuk Dekan/Kaprodi")
    args = ap.parse_args()

    res = cari_identitas_dan_pejabat_kampus(
        args.universitas,
        fakultas=args.fakultas,
        program_studi=args.prodi,
        deep_official_search=not args.no_deep,
        download_logo_to=args.logo_out or None,
    )
    if args.find_pedoman:
        ddg_pdfs = cari_pedoman_kampus_online(
            args.universitas,
            fakultas=args.fakultas,
            program_studi=args.prodi,
            domain=res.get("domain", ""),
        )
        seen_u = {p["url"] for p in res.get("site_pedoman_pdfs", [])}
        res["pedoman_candidates"] = list(res.get("site_pedoman_pdfs", [])) + [p for p in ddg_pdfs if p["url"] not in seen_u]
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    _cli()
