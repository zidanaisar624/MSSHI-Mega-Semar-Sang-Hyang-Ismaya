"""Render release cards from public artwork, then build the looping GIF and MP4.

Developer dependencies: Python 3.10+, Pillow, FFmpeg, and Chrome/Chromium.
Run: python scripts/visuals/render_semar.py [--chrome PATH] [--ffmpeg PATH]
All paths are relative to the checkout. Original avatar files are read-only.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
from html import escape
import json
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"
STYLE = Path(__file__).with_name("semar.css").read_text(encoding="utf-8")
VERSION = json.loads((ROOT / "VERSION.json").read_text(encoding="utf-8"))
EDITION = escape(VERSION["version"])
BUNDLED = int(VERSION["bundled_skills"])
UPSTREAMS = int(VERSION["external_sources"])
OPTIONAL = sum(1 for directory in (ROOT / "optional").iterdir() if (directory / "SKILL.md").is_file())
BOTS = [("bot-01-yukino","Yukino"), ("bot-02-shizuka","Shizuka"), ("bot-03-val","Val"),
        ("bot-04-kikichii","Kiki-Chii"), ("bot-05-shikaku","Shikaku")]
VISUALS = {
    "hero": ("hero-muza-banner", "avatars/hero-muza-banner.png", 1600, 900),
    "meme": ("meme-ram4gb-mcp-panik", "memes/meme-ram4gb-mcp-panik.png", 640, 400),
    "missions": ("showcase-5-missions-overview", "showcases/showcase-5-missions-overview.png", 1280, 720),
    "studio": ("showcase-higgsfield-pipeline", "showcases/showcase-higgsfield-pipeline.png", 1280, 720),
}
STORIES = [
    ("Saat laptop sibuk", "Buka alat saat diperlukan", "CLI-Anything memanggil aplikasi ketika ada tugas. Paket memilih alat yang dibutuhkan setiap bot.",
     "$1 TokenShield  ·  MSSHITrim", "visuals/01_hero_sovereign_orchestrator.jpg"),
    ("Tim lima bot", "Satu ide, lima peran", "Yukino merapikan ide. Shizuka membagi tugas ke Val untuk riset, Kiki-Chii untuk kreatif, dan Shikaku untuk kode.",
     "Cindy Grand-Plan Gate  ·  Tinjau rencana proyek besar", "memes/let-mi-ting-cat.jpg"),
    ("Studio Kiki-Chii", "Dari meme ke video", "Rancang dua caption dan bandingkan meme lokal Rp0. Untuk produksi awan, pilih dari sembilan modul Higgsfield setelah login dan persetujuan biaya.",
     "Opsional di Hermes  ·  Blender MCP dan RAEA", "visuals/04_bot_kikichii_creative.jpg"),
    ("Misi 02", "Riset Untuk S1–S3", "Val membantu menyiapkan pencarian pustaka, membaca data, dan menyusun draf untuk ditinjau bersama pembimbing.",
     "Diutamakan S1 Skripsi", "visuals/03_bot_val_research_skripsi.jpg"),
    ("Tiga repositori", "Pasang, pakai, periksa", "Connect memasang paket. Core menyediakan skill dan peran. Doctor membandingkan file program dan menyiapkan pemulihan.",
     f"{BUNDLED} skill bundel  ·  {OPTIONAL} opt-in  ·  {UPSTREAMS} sumber upstream", "avatars/muza-noir-fullbody.png"),
]


def picture(rel: str, css: str = "") -> str:
    return f'<img class="{css}" src="{escape((ASSETS / rel).as_uri(), quote=True)}" alt="">'


def folio(topic: str) -> str:
    return f'<div class="folio"><span>MSSHI &nbsp;/&nbsp; v{EDITION}</span><span>{topic}</span></div>'


def layouts() -> dict[str, str]:
    portraits = "".join(f'<figure class="portrait">{picture("avatars/" + file + ".png")}<figcaption>{label}</figcaption></figure>' for file, label in BOTS)
    numbers = "".join(f'<div class="metric"><strong>{n}</strong><small>{t}</small></div>'
                      for n,t in [(BUNDLED,"Bundled Skills"),(OPTIONAL,"Opt-in Skills"),(UPSTREAMS,"Pinned Upstreams")])
    hero = f'''<section class="plate hero">{picture("visuals/semar-v2-stage.webp","hero-art")}<div class="hero-shade"></div>
      <div class="hero-copy"><div class="eyebrow">Hermes Agent &nbsp; / &nbsp; v{EDITION}</div><h1>MSSHI</h1>
      <div class="longname">Mega Semar Sang Hyang Ismaya</div>
      <p class="dek">Lima asisten untuk belajar, riset, karya kreatif, pemrograman, dan rencana harian.</p>
      <div class="numbers">{numbers}</div><div class="ribbon">{portraits}</div>
      <p class="summary">Cindy Grand-Plan Gate · $1 TokenShield · Rust Hot-Path Accel<br>Kiki-Chii Rp0 Meme Studio + Higgsfield 9 Modul</p></div>
      <div class="art-credit">Kyai Semar <i>·</i> Dalang lima bot</div></section>'''
    missions = [
        ("01","Belajar &amp; mentor","","Yukino menguji ide awal. Shizuka membantu menyusun langkah belajar."),
        ("02","Riset Untuk S1–S3","Diutamakan S1 Skripsi","Val mendampingi pencarian literatur, analisis data, dan draf."),
        ("03","Konten &amp; film","","Kiki-Chii merancang meme Rp0 dan produksi melalui 9 modul Higgsfield."),
        ("04","Kode &amp; web","","Shikaku membagi masalah, menulis kode, dan menguji perbaikan."),
        ("05","Strategi harian","","Yukino dan Shizuka menyesuaikan rencana dengan waktu yang tersedia."),
    ]
    cells = "".join(f'<section class="mission"><span class="role">Misi {n}</span><h3>{title}</h3><div class="priority">{badge}</div><p>{desc}</p></section>' for n,title,badge,desc in missions)
    board = f'''<section class="plate board">{folio("Peta peran")}
      <h2>Lima misi <em>tim Semar</em></h2><p class="intro">{BUNDLED} skill bundel · {OPTIONAL} opt-in · {UPSTREAMS} sumber upstream</p>
      <div class="missions">{cells}</div><p class="note"><b>Cindy Grand-Plan Interactive Gate</b> membantu kelima bot menyusun rencana yang bisa dikoreksi.<br>
      <b>Anti-slop</b> mendampingi penyuntingan. <b>Rust Hot-Path (&lt;40%)</b> dibatasi pada jalur kerja tertentu.</p></section>'''
    studio = f'''<section class="plate studio">{folio("Studio kreatif Kiki-Chii")}
      <h2>Mulai dari <em>konsep</em></h2><p class="intro">Sepakati audiens, pesan, hak penggunaan bahan, dan format hasil. Lalu pilih jalur produksi.</p>
      <div class="branched"><article class="lane"><h3>Meme Studio Rp0</h3>
      <p><b>Di laptop</b> · Tulis dua caption, render dari gambar sendiri, lalu nilai hasil A/B secara lokal.</p>
      <p><b>Di web</b> · Buat URL meme dengan caption yang boleh dibagikan.</p><p>Empat sumber berlisensi MIT.</p></article>
      <article class="lane remote"><h3>9 modul Higgsfield</h3><p><b>2 untuk sinema</b> · Generasi aset dan konsistensi karakter.</p>
      <p><b>3 untuk brand</b> · Foto produk, brand kit, dan kartu katalog.</p><p><b>4 untuk video &amp; web</b> · Video tanpa wajah, explainer, thumbnail, dan situs.</p></article></div>
      <p class="foot"><b>Gerbang wajib Higgsfield</b> · Masuk ke akun sendiri dan konfirmasi biaya sebelum generasi.<br><b>Modul opt-in</b> · MCP for Blender, RAEA, dan Lemo-Opuscar dapat dipilih sesuai kebutuhan.</p></section>'''
    meme = f'''<section class="plate meme">{folio("Kiki-Chii · Meme Studio Rp0")}
      <div class="twins"><article>{picture("memes/dev-cat-laptop.jpg")}<h3>Baru buka laptop.<br>Semua alat ikut bangun.</h3></article>
      <article>{picture("visuals/semar-v2-coffee.webp")}<h3>“Sek, kopinya dulu.”<br>Buka alat pas perlu.</h3></article></div><p class="caption">CLI-Anything · $1 TokenShield · {BUNDLED} skill bundel</p></section>'''
    pages = {"hero":hero,"missions":board,"studio":studio,"meme":meme}
    for index, (label,title,detail,key,image) in enumerate(STORIES, 1):
        pages[f"scene{index}"] = f'''<section class="plate scene"><div class="copy"><span class="eyebrow">MSSHI v{EDITION} &nbsp; / &nbsp; {index}/5 &nbsp; / &nbsp; {label}</span>
        <h2>{title}</h2><p>{detail}</p><div class="key">{key}</div></div>{picture(image,"art")}</section>'''
    return pages


def render(work: Path, chrome: str, name: str, content: str) -> None:
    width, height = VISUALS[name][2:] if name in VISUALS else (1280, 720)
    doc = work / f"{name}.html"
    doc.write_text(f'<!doctype html><meta charset="utf-8"><html lang="id"><style>{STYLE}</style><body>{content}</body></html>', encoding="utf-8")
    out = work / f"{name}.png"
    subprocess.run([chrome, "--headless", "--disable-gpu", "--disable-background-networking", "--no-first-run",
                    "--hide-scrollbars", "--allow-file-access-from-files", "--force-device-scale-factor=1",
                    f"--user-data-dir={work / ('profile-' + name)}", f"--window-size={width},{height}",
                    f"--screenshot={out}", doc.as_uri()], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with Image.open(out) as shot:
        if shot.size != (width,height):
            raise ValueError(f"Unexpected {name} dimensions: {shot.size}")
        if name in VISUALS:
            # Palette PNG reduces the README download size while preserving exact type placement.
            shot.convert("RGB").quantize(colors=256).save(ASSETS / VISUALS[name][1], optimize=True)


def movies(work: Path, ffmpeg: str) -> tuple[Path,Path]:
    output = ASSETS / "showcases"
    movie = output / "msshi-visual-explainer.mp4"
    gif = output / "msshi-visual-explainer.gif"
    # Each 3.6-second plate includes a short fade at its ends. Stream one plate at a time.
    clips = []
    for index in range(1, 6):
        clip = work / f"clip{index}.mp4"
        subprocess.run([ffmpeg,"-loglevel","error","-y","-loop","1","-framerate","12","-i",str(work / f"scene{index}.png"),
                        "-frames:v","44","-vf","fade=t=in:s=0:n=3,fade=t=out:s=41:n=3,format=yuv420p",
                        "-c:v","libx264","-threads","2","-crf","20",str(clip)],check=True)
        clips.append(f"file '{clip.name}'")
    listing = work / "concat.txt"
    listing.write_text("\n".join(clips) + "\n",encoding="utf-8")
    subprocess.run([ffmpeg,"-loglevel","error","-y","-f","concat","-safe","1","-i",str(listing),
                    "-c","copy","-movflags","+faststart",str(movie)],check=True)
    subprocess.run([ffmpeg,"-loglevel","error","-y","-i",str(movie),"-filter_complex_threads","1","-filter_complex",
                    "fps=4,scale=800:450:flags=lanczos,split[x][p];[p]palettegen=max_colors=128[p];[x][p]paletteuse=dither=bayer:bayer_scale=3",
                    "-loop","0",str(gif)],check=True)
    if gif.stat().st_size >= 3_800_000:
        raise ValueError("GIF exceeds the public 3.8 MB limit")
    return gif,movie


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chrome", default=os.environ.get("CHROME_EXECUTABLE") or shutil.which("chromium") or shutil.which("google-chrome"))
    parser.add_argument("--ffmpeg", default=shutil.which("ffmpeg"))
    args = parser.parse_args()
    if not args.chrome or not args.ffmpeg:
        parser.error("Pass --chrome PATH and --ffmpeg PATH, or add both to PATH.")
    with TemporaryDirectory(prefix="msshi-semar-") as tmp:
        work = Path(tmp)
        pages = layouts()
        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(lambda item: render(work,args.chrome,*item),pages.items()))
        gif,movie = movies(work,args.ffmpeg)
    generated = {v[0]:(ASSETS/v[1],v[2],v[3]) for v in VISUALS.values()}
    generated.update({"msshi-visual-explainer-gif":(gif,800,450),"msshi-visual-explainer-mp4":(movie,1280,720)})
    manifest = ROOT / "configs/visual_assets_manifest.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    purposes = {"hero-muza-banner":"Semar V2 · pengantar ekosistem","meme-ram4gb-mcp-panik":"Semar dan alat sesuai kebutuhan",
                "showcase-5-missions-overview":"Lima misi dan prioritas riset S1–S3","showcase-higgsfield-pipeline":"Meme Studio Rp0 dan sembilan modul Higgsfield",
                "msshi-visual-explainer-gif":"Lima babak MSSHI untuk README","msshi-visual-explainer-mp4":"Lima babak MSSHI dalam HD"}
    for asset in data["assets"]:
        if asset["id"] in generated:
            file,width,height = generated[asset["id"]]
            raw = file.read_bytes()
            asset.update(width=width,height=height,size_bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),
                         purpose=f"{purposes[asset['id']]} · v{EDITION}",source_collection="msshi_public_artwork_semar_v2",
                         source_filename="scripts/visuals/render_semar.py")
            print(f"{file.name}: {len(raw)} bytes")
    manifest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


if __name__ == "__main__":
    main()
