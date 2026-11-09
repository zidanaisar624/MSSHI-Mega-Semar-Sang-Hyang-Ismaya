#!/usr/bin/env python3
"""Generate the per-bot skill audit from the canonical MSSHI matrix."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "configs" / "bot_role_and_skill_matrix.json"
AUDIT = ROOT / "docs" / "AUDIT_SKILLS_PER_BOT.md"


def markdown_text(value):
    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def skill_ref(skill):
    slug = skill["slug"]
    if skill["status"] == "bundled":
        return f"[`{slug}`](../{skill['path']})"
    if source := skill.get("source"):
        return f"[`{slug}`]({source})"
    return f"`{slug}`"


def assignments(bots, catalog):
    owners = {slug: [] for slug in catalog}
    for bot in bots:
        for kind, status in (("required_skills", "bundled"), ("optional_skills", "external")):
            slugs = bot[kind]
            if len(slugs) != len(set(slugs)):
                raise ValueError(f"{bot['id']}: duplicate skill in {kind}")
            for slug in slugs:
                if slug not in catalog or catalog[slug]["status"] != status:
                    raise ValueError(f"{bot['id']}: wrong status or unknown skill: {slug}")
                owners[slug].append(bot["id"])
    return owners


def render(matrix):
    catalog = {item["slug"]: item for item in matrix["skills"]}
    bots = matrix["bots"]
    if len(catalog) != len(matrix["skills"]) or len({b["id"] for b in bots}) != len(bots):
        raise ValueError("Duplicate skill or bot ID")
    if any(s["status"] not in {"bundled", "external"} for s in catalog.values()):
        raise ValueError("Expected bundled or external status")
    disk_skills = {p.parent.name: p.relative_to(ROOT).as_posix() for p in (ROOT / "skills").glob("*/SKILL.md")}
    bundle = {s["slug"]: s["path"] for s in catalog.values() if s["status"] == "bundled"}
    if disk_skills != bundle:
        raise ValueError("Bundled catalog differs from skills/*/SKILL.md")
    if any(s["path"] is not None for s in catalog.values() if s["status"] == "external"):
        raise ValueError("External reference cannot declare a bundled path")
    if any(not (ROOT / b["persona_file"]).is_file() for b in bots):
        raise ValueError("Missing persona")
    for name in ("academic_engines", "context_layers"):
        allowed = {item["id"] for item in matrix[name]}
        if any(not set(b[name]) <= allowed for b in bots):
            raise ValueError(f"Invalid {name}")
    for name, slugs in matrix["packs"].items():
        if not set(slugs) <= bundle.keys():
            raise ValueError(f"Pack {name} can only list bundled skills")
    owners = assignments(bots, catalog)
    unassigned = sorted(slug for slug, assigned in owners.items() if not assigned)
    if unassigned:
        raise ValueError(f"Unassigned skills: {', '.join(unassigned)}")
    lines = [
        "# Audit skill per bot MuZA",
        "",
        "Sumber: [matriks bot](../configs/bot_role_and_skill_matrix.json). "
        "Jalankan `python scripts/render_bot_audit.py` setelah mengubah matriks.",
        "",
        f"Katalog berisi **{len(bundle)} skill bundel** dan **{len(catalog) - len(bundle)} rujukan eksternal**. "
        "Skill bundel disertakan sebagai file instruksi. Rujukan eksternal menunjukkan kemampuan yang dituju "
        "dan perlu disiapkan terpisah sesuai host, izin, dan dependensi.",
        "",
        "| Bot | Mandat | Bundel | Rujukan eksternal |",
        "| --- | --- | ---: | ---: |",
    ]
    for bot in bots:
        lines.append(f"| {markdown_text(bot['label'])} | {markdown_text(bot['role'])} | "
                     f"{len(bot['required_skills'])} | {len(bot['optional_skills'])} |")
    for bot in bots:
        lines += [
            "", f"## {bot['label']}", "",
            f"{bot['output']} [Baca persona](../{bot['persona_file']}).",
            "", "| Skill atau rujukan | Status | Fungsi |", "| --- | --- | --- |",
        ]
        for slug in bot["required_skills"] + bot["optional_skills"]:
            skill = catalog[slug]
            status = "Bundel" if skill["status"] == "bundled" else "Eksternal"
            lines.append(f"| {skill_ref(skill)} | {status} | {markdown_text(skill['purpose'])} |")
    lines += ["", "## Kelompok distribusi", ""]
    labels = {b["id"]: b["label"] for b in bots}
    grouped = {
        "Semua bot": {slug: group for slug, group in owners.items() if len(group) == len(bots)},
        "Beberapa bot": {slug: group for slug, group in owners.items() if 1 < len(group) < len(bots)},
        "Khusus satu bot": {slug: group for slug, group in owners.items() if len(group) == 1},
    }
    for category, entries in grouped.items():
        lines += [f"### {category}", ""]
        by_owners = {}
        for slug, group in sorted(entries.items()):
            by_owners.setdefault(tuple(group), []).append(skill_ref(catalog[slug]))
        for group, slugs in by_owners.items():
            lines.append("- **" + ", ".join(labels[bot] for bot in group) + "** — " + ", ".join(slugs))
        lines.append("")
    antigravity = matrix.get("antigravity", {})
    if antigravity:
        lines += ["## Pemetaan untuk Antigravity", "", antigravity["role"] + ".", ""]
        lines += ["- **Bundel** — " + ", ".join(skill_ref(catalog[s]) for s in antigravity["bundled_skills"]),
                  "- **Rujukan eksternal** — " + ", ".join(skill_ref(catalog[s]) for s in antigravity["external_skills"]),
                  "", "Pemetaan ini menjelaskan ruang kerja yang dituju. Ikuti panduan host untuk lokasi pemasangan "
                  "dan gunakan skill yang diaktifkan untuk proyek.", ""]
    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the audit matches the current matrix")
    args = parser.parse_args()
    generated = render(json.loads(MATRIX.read_text(encoding="utf-8-sig")))
    if args.check:
        if not AUDIT.is_file() or AUDIT.read_text(encoding="utf-8") != generated:
            parser.exit(1, "Audit stale; run python scripts/render_bot_audit.py\n")
        print("Matrix and generated audit match.")
    else:
        AUDIT.write_text(generated, encoding="utf-8")
        print("Updated docs/AUDIT_SKILLS_PER_BOT.md")


if __name__ == "__main__":
    main()
