#!/usr/bin/env python3
"""Zero-friction MuZA Skripsi Starter v1.1 (Drag-and-Drop & CLI runner)."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "muza-skripsi-template"
SKILL_SCRIPTS = SKILL_DIR / "scripts"
for p in (Path(__file__).resolve().parent, SKILL_SCRIPTS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def adaptive_data_home() -> Path:
    env = os.environ.get("HERMES_HOME", "").strip()
    if env:
        return Path(env)
    if os.name == "nt" and Path("D:/").exists():
        d_home = Path("D:/HermesData")
        if d_home.exists() or os.access("D:/", os.W_OK):
            return d_home
    return Path.home() / "HermesData"


def adaptive_output_dir(explicit: Path | None = None) -> Path:
    if explicit:
        out = explicit.expanduser().resolve()
        out.mkdir(parents=True, exist_ok=True)
        return out
    if os.name == "nt" and Path("D:/").exists():
        d_out = Path("D:/HermesData/Skripsi_Output")
        try:
            d_out.mkdir(parents=True, exist_ok=True)
            return d_out
        except OSError:
            pass
    c_out = Path.home() / "Documents" / "MuZA_Skripsi_Output"
    c_out.mkdir(parents=True, exist_ok=True)
    return c_out


def ensure_pylibs(auto_install: bool = False) -> Path | None:
    home = adaptive_data_home()
    candidates = [
        home / "skripsi-pylibs",
        Path.home() / "HermesData" / "skripsi-pylibs",
        Path("D:/HermesData/skripsi-pylibs"),
    ]
    for cand in candidates:
        if cand.is_dir() and str(cand) not in sys.path:
            sys.path.insert(0, str(cand))

    missing = [m for m in ("docx", "lxml", "pypdf", "PIL") if importlib.util.find_spec(m) is None]
    if not missing:
        return None

    target = home / "skripsi-pylibs"
    if not auto_install:
        raise RuntimeError(
            f"Dependensi Python belum lengkap ({', '.join(missing)}). "
            f"Jalankan dengan --install-deps atau pasang ke {target}."
        )
    target.mkdir(parents=True, exist_ok=True)
    cache_dir = home / "pip-cache"
    tmp_dir = home / "temp"
    cache_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["PIP_CACHE_DIR"] = str(cache_dir)
    env["TEMP"] = str(tmp_dir)
    env["TMP"] = str(tmp_dir)
    pkg_map = {"docx": "python-docx", "lxml": "lxml", "pypdf": "pypdf", "PIL": "pillow"}
    pkgs = [pkg_map[m] for m in missing]
    print(f"[MuZA Skripsi] Memasang {', '.join(pkgs)} secara hemat ke {target} ...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--no-user", "--target", str(target), *pkgs],
                   check=True, env=env)
    if str(target) not in sys.path:
        sys.path.insert(0, str(target))
    return target


def read_muza_search_meta(zip_path: Path) -> dict:
    meta = {}
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if name.endswith("03_METADATA_MUZA_SKRIPSI.json"):
                try:
                    meta = json.loads(zf.read(name).decode("utf-8-sig"))
                except Exception:
                    meta = {}
                break
    return meta


def classify_inputs(paths: list[str]) -> dict:
    classified = {
        "muza_zip": None,
        "guideline": None,
        "spec_json": None,
        "muza_bab2": None,
        "muza_ris": None,
        "logo": None,
        "unknown": [],
    }
    for raw in paths:
        p = Path(raw.strip().strip('"')).expanduser()
        if not p.exists():
            classified["unknown"].append(str(p))
            continue
        suf = p.suffix.lower()
        if suf == ".zip":
            classified["muza_zip"] = p
        elif suf in {".pdf", ".docx", ".doc", ".txt"}:
            classified["guideline"] = p
        elif suf == ".json":
            classified["spec_json"] = p
        elif suf in {".csv", ".xlsx"}:
            classified["muza_bab2"] = p
        elif suf == ".ris":
            classified["muza_ris"] = p
        elif suf in {".png", ".jpg", ".jpeg", ".webp"}:
            classified["logo"] = p
        else:
            classified["unknown"].append(str(p))
    return classified


def merge_guideline_rules(spec: dict, rules: dict, guideline_name: str) -> dict:
    fmt = spec.setdefault("format", {})
    detected = rules.get("detected", {})

    def first_val(key):
        items = detected.get(key) or []
        return items[0]["value"] if items else None

    if paper := first_val("paper"):
        if paper.upper() in {"A4", "LETTER", "FOLIO", "F4", "B5"}:
            fmt["paper"] = "F4" if paper.upper() == "FOLIO" else paper.upper()
    if font := first_val("font"):
        fmt["font"] = font
    if spacing := first_val("spacing"):
        try:
            sp = float(str(spacing).replace(",", "."))
            if 1.0 <= sp <= 3.0:
                fmt["line_spacing"] = sp
        except ValueError:
            pass
    if margin := first_val("margin"):
        nums = [float(x.replace(",", ".")) for x in re.findall(r"\d+(?:[.,]\d+)?", str(margin))]
        if len(nums) == 4:
            # Indonesian standard order when 4 numbers follow margin notation (atas-kiri-bawah-kanan vs kiri-atas-kanan-bawah)
            fmt["margin_top_cm"], fmt["margin_left_cm"], fmt["margin_bottom_cm"], fmt["margin_right_cm"] = nums
    if cite := first_val("citation_style"):
        spec["citation_style"] = cite
    fmt.setdefault("guideline_source", guideline_name)
    return spec


def short_campus_slug(campus_name: str) -> str:
    tokens = re.findall(r"[A-Za-z0-9]+", campus_name or "Kampus")
    if len(tokens) == 1:
        return tokens[0][:16]
    skip = {"universitas", "institut", "sekolah", "tinggi", "politeknik", "negeri", "islam", "dan", "di"}
    acro = "".join(t[0].upper() for t in tokens if t.lower() not in skip)
    return (acro or tokens[0])[:16]


def run_pipeline(
    paths: list[str],
    *,
    universitas: str = "",
    fakultas: str = "",
    prodi: str = "",
    preset: str = "informatika_ilkom",
    out_dir: Path | None = None,
    out_file: Path | None = None,
    auto_online: bool = True,
    find_pedoman: bool = False,
    install_deps: bool = False,
    no_open: bool = False,
    interactive: bool = True,
) -> Path:
    ensure_pylibs(auto_install=install_deps)
    inputs = classify_inputs(paths)

    if interactive and not any(inputs[k] for k in ("muza_zip", "guideline", "spec_json")) and not universitas:
        print("\n========================================================")
        print("  MuZA Agent — MuZA Skripsi Starter v1.1 (Drag & Drop)")
        print("========================================================")
        print("Proses 5 Tahap: Kampus/Pedoman -> Lookup/Ekstrak -> Preset -> Build .docx -> Hasil\n")
        universitas = input("1. Nama Universitas (contoh: UNNES / UNDIP / UGM) : ").strip() or "Universitas Indonesia"
        fakultas = input("2. Fakultas (opsional)                           : ").strip()
        prodi = input("3. Program Studi (opsional)                      : ").strip()
        p_choice = input("4. Metodologi [1=Informatika/Ilkom, 2=Kuantitatif, 3=Kualitatif, 4=R&D, 5=PTK] (default 1): ").strip()
        preset_map = {"1": "informatika_ilkom", "2": "kuantitatif", "3": "kualitatif", "4": "rnd", "5": "ptk"}
        preset = preset_map.get(p_choice, preset)
        g_in = input("5. Path Pedoman PDF/DOCX (Enter jika lewat online): ").strip().strip('"')
        if g_in:
            inputs = classify_inputs([g_in])
        z_in = input("6. Path .zip hasil MuZA_Search (Enter jika belum ada): ").strip().strip('"')
        if z_in:
            z_cls = classify_inputs([z_in])
            if z_cls["muza_zip"]:
                inputs["muza_zip"] = z_cls["muza_zip"]

    meta = {}
    if inputs["muza_zip"]:
        meta = read_muza_search_meta(inputs["muza_zip"])
        universitas = universitas or meta.get("universitas", "")
        fakultas = fakultas or meta.get("fakultas", "")
        prodi = prodi or meta.get("prodi", "")
        if meta.get("preset") in {"kuantitatif", "kualitatif", "rnd", "informatika_ilkom", "ptk"}:
            preset = meta["preset"]

    if inputs["spec_json"]:
        spec = json.loads(inputs["spec_json"].read_text(encoding="utf-8-sig"))
    else:
        spec = json.loads((SKILL_DIR / "assets" / "example_spec.json").read_text(encoding="utf-8-sig"))

    campus = spec.setdefault("campus", {})
    if universitas:
        campus["university"] = universitas
        campus["name"] = universitas
        campus["short"] = short_campus_slug(universitas)
    if fakultas:
        campus["faculty"] = fakultas
    if prodi:
        campus["program"] = prodi
    if meta.get("topik"):
        spec.setdefault("cover", {})["title_placeholder"] = meta["topik"]

    with tempfile.TemporaryDirectory(prefix="muza-skripsi-", dir=str(adaptive_data_home() if adaptive_data_home().exists() else tempfile.gettempdir())) as tmp:
        tmpdir = Path(tmp)
        if inputs["guideline"]:
            print(f"[Tahap 2/5] Mengekstrak aturan pedoman: {inputs['guideline'].name}")
            rules_json = tmpdir / "rules.json"
            txt_out = tmpdir / "guideline.txt"
            subprocess.run([
                sys.executable, "-B", "-X", "utf8",
                str(SKILL_SCRIPTS / "extract_guideline.py"),
                str(inputs["guideline"]), str(txt_out), "--json", str(rules_json),
            ], check=True)
            if rules_json.is_file():
                rules = json.loads(rules_json.read_text(encoding="utf-8-sig"))
                spec = merge_guideline_rules(spec, rules, inputs["guideline"].name)

        spec_path = tmpdir / "working_spec.json"
        spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")

        target_dir = adaptive_output_dir(out_dir)
        campus_tag = re.sub(r"[^A-Za-z0-9_-]+", "_", campus.get("short") or "Kampus")
        dest_docx = out_file.expanduser().resolve() if out_file else target_dir / f"Template_Skripsi_{campus_tag}.docx"
        dest_docx.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            sys.executable, "-B", "-X", "utf8",
            str(SKILL_SCRIPTS / "build_template.py"),
            str(spec_path),
            str(dest_docx),
            "--preset", preset,
        ]
        if inputs["muza_zip"]:
            cmd += ["--muza-zip", str(inputs["muza_zip"])]
        if inputs["muza_bab2"]:
            cmd += ["--muza-bab2", str(inputs["muza_bab2"])]
        if inputs["muza_ris"]:
            cmd += ["--muza-ris", str(inputs["muza_ris"])]
        if inputs["logo"]:
            cmd += ["--logo", str(inputs["logo"])]
        if universitas:
            cmd += ["--universitas", universitas]
        if fakultas:
            cmd += ["--fakultas", fakultas]
        if prodi:
            cmd += ["--prodi", prodi]
        if auto_online:
            cmd.append("--auto-online")
        if find_pedoman:
            cmd.append("--find-pedoman")

        print(f"[Tahap 4/5] Merakit Template Word (.docx) preset '{preset}' ...")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0 and auto_online:
            print("[Info] Mode online gagal/offline; mencoba ulang dalam mode offline bersih ...")
            cmd_off = [c for c in cmd if c not in {"--auto-online", "--find-pedoman"}]
            res = subprocess.run(cmd_off, capture_output=True, text=True)
        if res.stdout.strip():
            print(res.stdout.strip())
        if res.returncode != 0:
            raise RuntimeError(f"build_template.py gagal ({res.returncode}): {res.stderr.strip()}")

        print(f"\n[Tahap 5/5] SELESAI! Template tersimpan di:\n  {dest_docx}")
        print(f"Ukuran file: {dest_docx.stat().st_size:,} bytes")
        print("Tips Cepat: Buka di Microsoft Word -> tekan Ctrl+H -> ganti {name}, {nim}, Pembimbing I/II, dan {title}!")
        if not no_open and os.name == "nt" and sys.stdin.isatty():
            try:
                os.startfile(str(dest_docx))
            except OSError:
                pass
        return dest_docx


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="File yang di-drag-and-drop: .zip (MuZA_Search), .pdf/.docx (Pedoman), .ris, .csv/.xlsx, .json, atau .png logo.")
    parser.add_argument("--universitas", default="", help="Nama universitas (mis. Universitas Negeri Semarang).")
    parser.add_argument("--fakultas", default="", help="Nama fakultas.")
    parser.add_argument("--prodi", default="", help="Nama program studi.")
    parser.add_argument("--preset", default="informatika_ilkom", choices=("informatika_ilkom", "kuantitatif", "kualitatif", "rnd", "ptk"))
    parser.add_argument("--out-dir", type=Path, help="Folder output kustom (default: D:\\HermesData\\Skripsi_Output atau ~/Documents/MuZA_Skripsi_Output).")
    parser.add_argument("--out", type=Path, help="Path file .docx output lengkap.")
    parser.add_argument("--no-online", action="store_true", help="Nonaktifkan pencarian logo/pejabat online.")
    parser.add_argument("--find-pedoman", action="store_true", help="Cari juga tautan PDF pedoman kampus saat lookup online.")
    parser.add_argument("--install-deps", action="store_true", help="Otomatis pasang python-docx/lxml ke folder adaptif HermesData/skripsi-pylibs bila belum ada.")
    parser.add_argument("--no-open", action="store_true", help="Jangan otomatis membuka hasil .docx di Word.")
    parser.add_argument("--non-interactive", action="store_true", help="Jalankan tanpa prompt interaktif.")
    args = parser.parse_args(argv)
    try:
        run_pipeline(
            args.paths,
            universitas=args.universitas,
            fakultas=args.fakultas,
            prodi=args.prodi,
            preset=args.preset,
            out_dir=args.out_dir,
            out_file=args.out,
            auto_online=not args.no_online,
            find_pedoman=args.find_pedoman,
            install_deps=args.install_deps,
            no_open=args.no_open,
            interactive=(not args.non_interactive) and sys.stdin.isatty(),
        )
        return 0
    except Exception as exc:
        print(f"ERROR MuZA Skripsi: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
