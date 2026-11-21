#!/usr/bin/env python3
"""Cross-bot lazy skill discovery across active profiles, teammates, context sources, and archived skill vaults (`msshi find`).

Lets ANY Hermes bot automatically answer "Saya mau mengerjakan X, apakah ada skill yang bisa membantu?"
with 0 LLM calls, <50 ms warm archive lookup, strict role boundaries, and on-demand 1-file reading.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
from typing import Any

sys.dont_write_bytecode = True

_SCRIPTS_DIR = str(Path(__file__).resolve().parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import msshi_context_sources as cs
import msshi_hermes_profiles as hp
import msshi_skill_index as skill_idx

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_REL = Path("msshi-private") / "archived-skill-imports"
ARCHIVE_INDEX_REL = Path("msshi-runtime") / "skill-index" / "archive-catalog.json"

_WORD_RE = re.compile(r"[a-z0-9][a-z0-9_-]{1,}", re.I)
_STOPWORDS = frozenset({
    "saya", "aku", "mau", "ingin", "bisa", "ada", "yang", "untuk", "dengan", "dari", "ini", "itu",
    "mengerjakan", "kerjakan", "bikin", "buat", "membantu", "bantu", "tolong", "apakah", "skill",
    "skills", "pakai", "gunakan", "tentang", "cara", "dan", "atau", "the", "for", "with", "can",
    "help", "want", "need", "how", "make", "build", "any", "there", "that", "this",
})
_SYNONYMS: dict[str, tuple[str, ...]] = {
    "skripsi": ("thesis", "skripsi", "academic", "research", "paper", "docx", "muza"),
    "tesis": ("thesis", "academic", "research", "paper", "literature"),
    "disertasi": ("dissertation", "thesis", "research", "academic"),
    "riset": ("research", "literature", "paper", "evidence", "citation", "sinta", "scopus"),
    "jurnal": ("journal", "paper", "literature", "citation", "arxiv", "scopus", "sinta"),
    "prediksi": ("forecast", "timesfm", "timeseries", "predict", "statistics"),
    "ramal": ("forecast", "timesfm", "predict"),
    "belajar": ("learn", "tutor", "study", "pemula", "ossu", "chalk", "learnloop"),
    "kuliah": ("study", "learn", "ossu", "academic", "course"),
    "pemula": ("beginner", "pemula", "learn", "tutor"),
    "video": ("video", "film", "ffmpeg", "motion", "remotion", "hyperframes"),
    "film": ("film", "filmmaking", "video", "cinematography", "storyboard"),
    "foto": ("photo", "photography", "image", "sharewise", "privacy"),
    "desain": ("design", "ui", "ux", "figma", "poster", "canvas", "infographic"),
    "poster": ("poster", "canvas", "design", "infographic", "visual"),
    "slide": ("slide", "pptx", "presentation", "deck"),
    "presentasi": ("presentation", "slide", "pptx", "deck"),
    "coding": ("code", "programming", "software", "debug", "tdd", "developer"),
    "ngoding": ("code", "programming", "software", "debug", "tdd"),
    "web": ("web", "frontend", "react", "nextjs", "html", "css", "playwright"),
    "keamanan": ("security", "threat", "vulnerability", "cybersec", "bughunter", "grim"),
    "audit": ("audit", "review", "security", "check"),
    "dokumen": ("docx", "pdf", "document", "ocr", "word"),
    "excel": ("xlsx", "spreadsheet", "csv", "data", "table"),
    "tabel": ("table", "xlsx", "data", "csv"),
    "grafik": ("plot", "chart", "graph", "plotting", "visual"),
    "bersih": ("clean", "cleanup", "storage", "spacewise", "disk"),
    "privasi": ("privacy", "redact", "metadata", "sharewise"),
    "jadwal": ("schedule", "calendar", "meeting", "planning", "energy"),
    "curhat": ("empathy", "energy", "parenting", "support", "focus"),
    "karier": ("career", "job", "cv", "resume", "remote"),
    "lowongan": ("job", "remote", "career", "company"),
    "bahasa": ("humanizer", "writing", "indonesia", "english", "prose"),
}

_CONNECTED_SOURCES_META: tuple[dict[str, Any], ...] = (
    {
        "slug": "ossu-computer-science",
        "kind": "connected_university",
        "lead_bot": "shizuka",
        "command": "msshi ossu roadmap | msshi ossu open pemula | msshi ossu open start",
        "description": "Open Source Society University (OSSU) Computer Science — kurikulum S1 Ilmu Komputer gratis (15 jalur, 63 mata kuliah: Python, Math, Systems, OS/OSTEP, Algorithms, Security, ML).",
    },
    {
        "slug": "grim-prompter",
        "kind": "context_source",
        "lead_bot": "shikaku",
        "command": "msshi integrations source --name grim-prompter",
        "description": "Pemodelan ancaman berbasis bukti (STRIDE, PASTA, LINDDUN, attack trees, GDPR/CCPA privacy analysis) khusus Shikaku.",
    },
    {
        "slug": "claude-bughunter",
        "kind": "context_source",
        "lead_bot": "shikaku",
        "command": "msshi integrations source --name claude-bughunter --list",
        "description": "Audit kerentanan & bug bounty terotorisasi (83 skill keamanan, triage, validasi bukti) khusus Shikaku.",
    },
    {
        "slug": "mattpocock-skills",
        "kind": "context_source",
        "lead_bot": "shikaku",
        "command": "msshi integrations source --name mattpocock-skills --list",
        "description": "Disiplin rekayasa perangkat lunak praktis (TDD, arsitektur, PRD, refactoring, TypeScript).",
    },
    {
        "slug": "career-ops",
        "kind": "context_source",
        "lead_bot": "shizuka",
        "command": "msshi integrations source --name career-ops",
        "description": "Evaluasi lowongan kerja, CV/resume tailoring, dan persiapan wawancara karier.",
    },
    {
        "slug": "remote-jobs",
        "kind": "context_source",
        "lead_bot": "shizuka",
        "command": "msshi integrations source --name remote-jobs --query <kata>",
        "description": "Direktori perusahaan kerja remote global terverifikasi untuk pencarian karier.",
    },
    {
        "slug": "rea-video",
        "kind": "context_source",
        "lead_bot": "kiki-chii",
        "command": "msshi integrations source --name rea-video",
        "description": "Analisis struktur video, shot/scene breakdown, dan remake lokal khusus Kiki-Chii.",
    },
)

# Strict specialist ownership so non-owner bots delegate rather than copy restricted skills
_SPECIALIST_ONLY: dict[str, tuple[str, ...]] = {
    "riset-mendalam-nusantara-global": ("val",),
    "timesfm-forecasting": ("val",),
    "paper-context-resolver": ("val",),
    "firecrawl-research-papers": ("val",),
    "firecrawl-deep-research": ("val",),
    "github-research": ("val",),
    "muza-skripsi-template": ("val", "shizuka"),
    "deep-research": ("val", "shizuka"),
    "literature-review": ("val", "shizuka"),
    "novelty-assessment": ("val", "shizuka"),
    "research-paper-writing": ("val", "shizuka"),
    "paper-writing-section": ("val", "shizuka"),
    "paper-revision": ("val", "shizuka"),
    "rebuttal-writing": ("val", "shizuka"),
    "grim-prompter": ("shikaku",),
    "claude-bughunter": ("shikaku",),
    "ponytail": ("shikaku",),
}


def _extract_tokens(query: str) -> list[str]:
    base = [w.casefold() for w in _WORD_RE.findall(query) if w.casefold() not in _STOPWORDS]
    expanded: list[str] = []
    seen: set[str] = set()
    for tok in base:
        if tok not in seen:
            expanded.append(tok)
            seen.add(tok)
        for syn in _SYNONYMS.get(tok, ()):
            if syn not in seen:
                expanded.append(syn)
                seen.add(syn)
    return expanded


def _score_entry(tokens: list[str], raw_tokens: set[str], slug: str, name: str, description: str, extra: str = "") -> float:
    slug_l = slug.casefold()
    name_l = name.casefold()
    desc_l = description.casefold()
    extra_l = extra.casefold()
    slug_parts = set(_WORD_RE.findall(slug_l)) | set(_WORD_RE.findall(name_l))
    score = 0.0
    for tok in tokens:
        weight = 1.0 if tok in raw_tokens else 0.65
        if tok == slug_l or tok == name_l:
            score += 8.0 * weight
        elif tok in slug_parts:
            score += 4.5 * weight
        elif tok in slug_l or tok in name_l:
            score += 3.0 * weight
        if tok in desc_l:
            score += 2.0 * weight
        elif extra_l and tok in extra_l:
            score += 1.0 * weight
    return round(score, 2)


def _scan_skills_tree(root: Path, bucket_label: str) -> list[dict[str, Any]]:
    """Safely scan SKILL.md frontmatter inside `root` (skipping symlinks & excluded dirs)."""
    if not root.is_dir() or skill_idx.is_link(root):
        return []
    excluded = skill_idx.excluded_scan_dirs()
    entries: list[dict[str, Any]] = []
    for current, dirs, files in os.walk(root, followlinks=False):
        cur = Path(current)
        dirs[:] = sorted(
            d for d in dirs
            if d.lower() not in excluded
            and not d.startswith(".")
            and ".bak-" not in d.lower()
            and not d.lower().endswith(".bak")
            and not skill_idx.is_link(cur / d)
        )
        if "SKILL.md" in files:
            skill_md = cur / "SKILL.md"
            if skill_idx.is_link(skill_md):
                continue
            meta = skill_idx._read_frontmatter_metadata(skill_md)
            rel_dir = cur.relative_to(root).as_posix()
            slug = cur.name
            entries.append({
                "slug": slug,
                "name": meta.get("name") or slug,
                "description": (meta.get("description") or "")[:360],
                "bucket": bucket_label,
                "rel_path": f"{rel_dir}/SKILL.md" if rel_dir != "." else "SKILL.md",
                "path": str(skill_md),
            })
    return entries


_ARCHIVE_MEM_CACHE: dict[str, tuple[str, dict[str, Any]]] = {}
_PROFILE_SKILLS_MEM_CACHE: dict[str, tuple[str, list[dict[str, Any]]]] = {}


def _dir_sig(root: Path) -> str:
    if not root.is_dir() or skill_idx.is_link(root):
        return ""
    try:
        st = root.stat()
        children = [p.name for p in root.iterdir()]
        return f"{int(st.st_mtime_ns)}:{len(children)}"
    except OSError:
        return ""


def _scan_skills_tree_cached(root: Path, bucket_label: str, *, refresh: bool = False) -> list[dict[str, Any]]:
    key = f"{root.resolve() if root.exists() else root}|{bucket_label}"
    sig = _dir_sig(root)
    if not sig:
        _PROFILE_SKILLS_MEM_CACHE.pop(key, None)
        return []
    if not refresh:
        cached = _PROFILE_SKILLS_MEM_CACHE.get(key)
        if cached and cached[0] == sig:
            return cached[1]
    rows = _scan_skills_tree(root, bucket_label)
    _PROFILE_SKILLS_MEM_CACHE[key] = (sig, rows)
    return rows


def build_or_load_archive_index(home: Path, *, refresh: bool = False) -> dict[str, Any]:
    """Load cached archive skill catalog or rebuild it when archive directories change."""
    home = cs.checked(home)
    archive_root = home / ARCHIVE_REL
    cache_path = home / ARCHIVE_INDEX_REL

    if not archive_root.is_dir():
        return {"schema_version": 1, "archive_root": str(archive_root), "count": 0, "fingerprint": "", "entries": []}

    # Fast top-level + 1-level fingerprint (sub-millisecond) to avoid rescanning 1,600+ files every call
    sig_parts: list[str] = []
    for p in sorted(archive_root.iterdir()):
        if p.is_dir() and not skill_idx.is_link(p):
            st = p.stat()
            child_count = sum(1 for _ in p.iterdir())
            sig_parts.append(f"{p.name}:{child_count}:{int(st.st_mtime)}")
    fp = "|".join(sig_parts)

    mem_key = str(archive_root)
    if not refresh:
        mem = _ARCHIVE_MEM_CACHE.get(mem_key)
        if mem and mem[0] == fp:
            return mem[1]

    if not refresh and cache_path.is_file() and not skill_idx.is_link(cache_path):
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8-sig"))
            if isinstance(cached, dict) and cached.get("fingerprint") == fp and cached.get("archive_root") == str(archive_root):
                _ARCHIVE_MEM_CACHE[mem_key] = (fp, cached)
                return cached
        except (OSError, ValueError):
            pass

    entries: list[dict[str, Any]] = []
    for bucket in sorted(archive_root.iterdir()):
        if bucket.is_dir() and not skill_idx.is_link(bucket):
            entries.extend(_scan_skills_tree(bucket, bucket.name))

    payload = {
        "schema_version": 1,
        "archive_root": str(archive_root),
        "fingerprint": fp,
        "count": len(entries),
        "entries": entries,
    }
    try:
        skill_idx._atomic_write_json(cache_path, payload)
    except OSError:
        pass
    _ARCHIVE_MEM_CACHE[mem_key] = (fp, payload)
    return payload


def _logical_role(home: Path, active_profile: str) -> str:
    try:
        roles = hp.team_role_profiles(home)
        for role, actual in roles.items():
            if actual == active_profile:
                return role
    except (OSError, ValueError):
        pass
    return active_profile


def _live_profile_dirs(home: Path) -> dict[str, Path]:
    live = hp.live_named_profiles(home)
    return {"default": home, **live}


def _detect_profile(explicit: str | None = None, env: dict[str, str] | None = None) -> str:
    """Detect active Hermes bot profile from CLI flag, HERMES_PROFILE, or HERMES_HOME/profiles/<name>."""
    if explicit and explicit.strip():
        return explicit.strip().lower()
    environ = env if env is not None else os.environ
    if prof := (environ.get("HERMES_PROFILE") or "").strip():
        return prof.lower()
    if raw_home := (environ.get("HERMES_HOME") or "").strip():
        p = Path(raw_home).expanduser().absolute()
        if p.parent.name.lower() == "profiles" and p.name:
            return p.name.lower()
    return "default"


def find_skills(
    query: str,
    home: Path,
    *,
    profile: str = "default",
    top: int = 5,
    refresh_index: bool = False,
) -> dict[str, Any]:
    """Search active bot skills, teammate specialist skills, connected sources, and archived vault (0 LLM calls)."""
    query = query.strip()
    if not query:
        raise ValueError("Masukkan deskripsi tugas atau kata kunci pencarian skill.")
    home = cs.checked(home)
    raw_tokens = {w.casefold() for w in _WORD_RE.findall(query) if w.casefold() not in _STOPWORDS}
    tokens = _extract_tokens(query)
    if not tokens:
        tokens = [w.casefold() for w in _WORD_RE.findall(query)]
        raw_tokens = set(tokens)

    profiles = _live_profile_dirs(home)
    active_profile = profile.strip().lower() if profile else "default"
    if active_profile not in profiles:
        active_profile = "default"
    active_role = _logical_role(home, active_profile)

    # Layer 1 & 2: Active skills on current bot vs specialist teammates
    active_matches: list[dict[str, Any]] = []
    teammate_best: dict[str, dict[str, Any]] = {}
    own_slugs: set[str] = set()

    for pname, pdir in sorted(profiles.items()):
        rows = _scan_skills_tree_cached(pdir / "skills", pname, refresh=refresh_index)
        for row in rows:
            sc = _score_entry(tokens, raw_tokens, row["slug"], row["name"], row["description"])
            if sc <= 0:
                continue
            if pname == active_profile:
                own_slugs.add(row["slug"])
                active_matches.append({
                    "slug": row["slug"],
                    "name": row["name"],
                    "score": sc,
                    "description": row["description"],
                    "path": row["path"],
                    "action": "use_directly",
                })
            else:
                slug = row["slug"]
                if slug not in teammate_best or sc > teammate_best[slug]["score"]:
                    teammate_best[slug] = {
                        "slug": slug,
                        "name": row["name"],
                        "score": sc,
                        "owners": [pname],
                        "description": row["description"],
                        "restricted_to": list(_SPECIALIST_ONLY.get(slug, ())),
                    }
                elif pname not in teammate_best[slug]["owners"]:
                    teammate_best[slug]["owners"].append(pname)

    # Filter out skills already active on the current bot from teammate delegation suggestions
    teammate_matches = [
        {
            **row,
            "action": f"delegate_to:{'/'.join(row['restricted_to'] or row['owners'])}",
        }
        for slug, row in teammate_best.items()
        if slug not in own_slugs
    ]
    active_matches.sort(key=lambda r: (-r["score"], r["slug"]))
    teammate_matches.sort(key=lambda r: (-r["score"], r["slug"]))

    # Layer 3: Connected sources & open curricula (OSSU, grim-prompter, etc.)
    connected_matches: list[dict[str, Any]] = []
    for src in _CONNECTED_SOURCES_META:
        sc = _score_entry(tokens, raw_tokens, src["slug"], src["slug"], src["description"])
        if sc > 0:
            connected_matches.append({**src, "score": sc})
    connected_matches.sort(key=lambda r: (-r["score"], r["slug"]))

    # Layer 4: Archived skill vault (1,600+ skills indexed in <40ms, read 1 SKILL.md on demand!)
    archive = build_or_load_archive_index(home, refresh=refresh_index)
    archive_matches: list[dict[str, Any]] = []
    for row in archive.get("entries", []):
        slug = row["slug"]
        # Respect strict specialist-only rules & avoid duplicating live active/teammate skills
        if slug in _SPECIALIST_ONLY and active_role not in _SPECIALIST_ONLY[slug]:
            continue
        if slug in own_slugs or slug in teammate_best:
            continue
        sc = _score_entry(tokens, raw_tokens, slug, row["name"], row["description"], row.get("bucket", ""))
        if sc > 0:
            archive_matches.append({
                "slug": slug,
                "name": row["name"],
                "bucket": row["bucket"],
                "score": sc,
                "description": row["description"],
                "path": row["path"],
                "read_command": f'msshi find --open "{slug}" --home "{home}"',
            })
    archive_matches.sort(key=lambda r: (-r["score"], r["slug"]))

    # Pick single clearest recommendation
    if active_matches and active_matches[0]["score"] >= (teammate_matches[0]["score"] if teammate_matches else 0):
        recommendation = f"Pakai skill aktif `{active_matches[0]['slug']}` langsung pada profil `{active_profile}`."
    elif teammate_matches and (not archive_matches or teammate_matches[0]["score"] >= archive_matches[0]["score"]):
        owners = "/".join(teammate_matches[0]["restricted_to"] or teammate_matches[0]["owners"])
        recommendation = f"Delegasikan ke spesialis `{owners}` yang sudah memiliki skill `{teammate_matches[0]['slug']}`."
    elif connected_matches and (not archive_matches or connected_matches[0]["score"] >= archive_matches[0]["score"]):
        recommendation = f"Gunakan sumber terhubung `{connected_matches[0]['slug']}` (`{connected_matches[0]['command']}`)."
    elif archive_matches:
        recommendation = f"Baca 1 panduan arsip on-demand: `{archive_matches[0]['slug']}` ({archive_matches[0]['path']}) — tidak perlu memindahkan folder arsip."
    else:
        recommendation = "Belum ada skill khusus yang cocok; kerjakan langsung dengan kemampuan inti bot secara bertahap."

    return {
        "query": query,
        "profile": active_profile,
        "llm_calls": 0,
        "archive_indexed_count": archive.get("count", 0),
        "recommendation": recommendation,
        "active_on_bot": active_matches[:top],
        "delegate_to_teammate": teammate_matches[:top],
        "connected_sources": connected_matches[:top],
        "archived_vault": archive_matches[:top],
    }


def open_archived_skill(slug: str, home: Path, *, profile: str | None = None, max_chars: int = 16000) -> dict[str, Any]:
    """Read ONE archived SKILL.md safely on demand (strictly confined inside msshi-private/archived-skill-imports/)."""
    home = cs.checked(home)
    archive_root = cs.checked(home / ARCHIVE_REL)
    archive = build_or_load_archive_index(home)
    wanted = slug.strip().casefold()
    match = next((r for r in archive.get("entries", []) if r["slug"].casefold() == wanted or r["name"].casefold() == wanted), None)
    if match is None:
        match = next((r for r in archive.get("entries", []) if wanted in r["slug"].casefold() or wanted in r["name"].casefold()), None)
    if match is None:
        raise ValueError(f"Skill arsip '{slug}' tidak ditemukan di {archive_root}.")
    active_profile = _detect_profile(profile)
    active_role = _logical_role(home, active_profile)
    if match["slug"] in _SPECIALIST_ONLY and active_role not in _SPECIALIST_ONLY[match["slug"]]:
        owners = "/".join(_SPECIALIST_ONLY[match["slug"]])
        raise ValueError(f"Skill '{match['slug']}' adalah spesialis {owners}; delegasikan ke {owners} daripada membuka arsip.")
    target = cs.checked(Path(match["path"]))
    if not target.is_relative_to(archive_root) or target.name != "SKILL.md":
        raise ValueError("Refusing to read path outside archived skill vault.")
    content = target.read_text(encoding="utf-8-sig", errors="replace")
    truncated = len(content) > max_chars
    return {
        "slug": match["slug"],
        "name": match["name"],
        "bucket": match["bucket"],
        "path": str(target),
        "truncated": truncated,
        "content": content[:max_chars],
    }


def handle_tool_call(args: dict[str, Any], home: Path, *, profile: str | None = None) -> dict[str, Any]:
    """In-process dispatcher for native Hermes tool `msshi_find_skill` (0 LLM calls)."""
    if not isinstance(args, dict):
        raise ValueError("Arguments must be a JSON object.")
    action = str(args.get("action") or "").strip().lower()
    active_profile = _detect_profile(profile)
    if action == "search":
        query = str(args.get("query") or "").strip()
        if not query:
            raise ValueError("Parameter 'query' wajib diisi untuk action='search'.")
        if len(query) > 500:
            raise ValueError("Parameter 'query' terlalu panjang (maksimal 500 karakter).")
        raw_top = args.get("top", 5)
        if isinstance(raw_top, bool) or not isinstance(raw_top, int):
            raise ValueError("Parameter 'top' harus bilangan bulat 1-10.")
        top = max(1, min(10, raw_top))
        reindex = bool(args.get("reindex", False))
        res = find_skills(query, home, profile=active_profile, top=top, refresh_index=reindex)
        return {"ok": True, "action": "search", **res}
    if action == "open":
        slug = str(args.get("slug") or "").strip()
        if not slug:
            raise ValueError("Parameter 'slug' wajib diisi untuk action='open'.")
        if len(slug) > 160 or "/" in slug or "\\" in slug or ".." in slug:
            raise ValueError("Parameter 'slug' tidak valid; gunakan nama slug skill arsip saja.")
        data = open_archived_skill(slug, home, profile=active_profile)
        return {"ok": True, "action": "open", "llm_calls": 0, **data}
    raise ValueError("Parameter 'action' harus 'search' atau 'open'.")


def _print_human(res: dict[str, Any]) -> None:
    print(f"=== MSSHI Pencari Skill Otomatis (profil: {res['profile']} | arsip terindeks: {res['archive_indexed_count']}) ===")
    print(f"Tugas       : {res['query']}")
    print(f"Rekomendasi : {res['recommendation']}")
    if res["active_on_bot"]:
        print("\n[1] Sudah Aktif di Bot Ini (langsung pakai):")
        for r in res["active_on_bot"]:
            print(f"  - {r['slug']} (skor {r['score']}): {r['description'][:120]}")
    if res["delegate_to_teammate"]:
        print("\n[2] Ada di Bot Spesialis Lain (delegasikan, jangan duplikasi):")
        for r in res["delegate_to_teammate"]:
            owners = ", ".join(r["restricted_to"] or r["owners"])
            print(f"  - {r['slug']} [{owners}] (skor {r['score']}): {r['description'][:120]}")
    if res["connected_sources"]:
        print("\n[3] Sumber / Kurikulum Terhubung:")
        for r in res["connected_sources"]:
            print(f"  - {r['slug']} [{r['lead_bot']}] -> {r['command']}")
    if res["archived_vault"]:
        print("\n[4] Tersedia di Brankas Arsip (baca 1 file on-demand, 0 beban startup):")
        for r in res["archived_vault"]:
            print(f"  - {r['slug']} ({r['bucket']}, skor {r['score']}): {r['description'][:110]}")
            print(f"    Buka: msshi find --open \"{r['slug']}\"")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="msshi find", description=__doc__)
    parser.add_argument("query", nargs="*", help="Deskripsi tugas atau kata kunci (mis. 'bikin presentasi statistik').")
    parser.add_argument("--profile", default=None, help="Profil bot yang sedang bertanya (otomatis terdeteksi dari sesi Hermes jika dikosongkan).")
    parser.add_argument("--home", type=Path, help="Folder Hermes home.")
    parser.add_argument("--top", type=int, default=5, help="Jumlah maksimal hasil per kategori (default: 5).")
    parser.add_argument("--open", dest="open_slug", help="Baca langsung 1 SKILL.md dari brankas arsip berdasarkan slug.")
    parser.add_argument("--reindex", action="store_true", help="Bangun ulang indeks arsip skill lokal.")
    parser.add_argument("--json", action="store_true", help="Keluaran JSON.")
    args = parser.parse_args(argv)
    try:
        home = cs.checked(hp.resolve_hermes_home(args.home))
        active_profile = _detect_profile(args.profile)
        if args.open_slug:
            data = open_archived_skill(args.open_slug, home, profile=active_profile)
            if args.json:
                print(json.dumps(data, ensure_ascii=False, indent=2))
            else:
                print(f"=== Arsip Skill: {data['name']} ({data['bucket']}) ===")
                print(f"Path: {data['path']}\n")
                print(data["content"])
            return 0
        if args.reindex and not args.query:
            idx = build_or_load_archive_index(home, refresh=True)
            print(json.dumps({"indexed": idx["count"], "archive_root": idx["archive_root"]}, indent=2))
            return 0
        q = " ".join(args.query).strip()
        if not q:
            parser.print_help()
            return 0
        res = find_skills(q, home, profile=active_profile, top=max(1, min(20, args.top)), refresh_index=bool(args.reindex))
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            _print_human(res)
        return 0
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"msshi find: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
