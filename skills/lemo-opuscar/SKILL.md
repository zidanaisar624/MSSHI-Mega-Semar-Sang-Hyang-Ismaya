---
name: lemo-opuscar
description: Katalog 15 kategori dan 99 gaya film pendek berbasis kode (Lemo-Opuscar by Lemomo / LemoLab) untuk Kiki-Chii (Content Creator / Filmmaker): pilih gaya, baca 1 panduan STYLE.md on-demand dari cache terpin, lalu bangun konsep & film berbasis kode dengan review manusia.
license: MIT
metadata:
  upstream: https://github.com/lemomo-ai/lemo-opuscar
  upstream_commit: f9e204293930952b61ba921cd8944d05f121beee
  upstream_license: MIT (code); CC-BY-NC-4.0 with film-making permission (docs); CC-BY-4.0 (demo films/pictures)
  activation: contextual-creative-code-film
---

# Gaya Film Pendek Berbasis Kode (`Lemo-Opuscar` — 15 Kategori, 99 Gaya)

Gunakan skill ini pada peran Content Creator / Filmmaker (**`kiki-chii`**) saat pengguna ingin membuat film pendek, video explainer, trailer produk, dokumenter data, animasi tipografi, atau visualisasi cerita berbasis kode dengan gaya sinematik yang terkurasi.

Wrapper MSSHI ini sepenuhnya **model-agnostic**: tetap menggunakan provider dan model pilihan pengguna di Hermes (tidak mengubah `config.yaml`, model, API key, atau `SOUL.md`) dan bekerja selaras dengan `filmmaking-videography-photography-s2` (*Concepting First*), `motion-graphics-suite`, dan `brag`.

## 1. Cache Ringan Terpin di Luar `skills/` (0 Aset Berat, Baca 1 Gaya On-Demand)

Repositori upstream berukuran ~133 MB karena poster & media demo, sehingga **tidak** dibundel ke folder `skills/`. Cache terpin hanya menyimpan metadata teks/JSON (`style.json`, `STYLE.md`, `DEMO.md`, `TECHNIQUE.md`, `LICENSE`) di luar pemindai `skills/`:

```text
msshi integrations source --home HERMES_ROOT --name lemo-opuscar
msshi integrations source --home HERMES_ROOT --name lemo-opuscar --fetch
msshi integrations source --home HERMES_ROOT --name lemo-opuscar --list
msshi integrations source --home HERMES_ROOT --name lemo-opuscar --query "isometric"
msshi integrations source --home HERMES_ROOT --name lemo-opuscar --skill blueprint
```

- Tanpa `--fetch`, perintah hanya membaca status/katalog lokal (`0` panggilan model, `0` jaringan).
- Baca hanya **1 gaya terpilih** (`--skill <slug>`) per sesi agar hemat token; jangan memuat 99 `STYLE.md` sekaligus.

## 2. Peta 15 Kategori Gaya (Total 99 Gaya)

1. **Edit & Documentary (8)**: `caption-news`, `newsreel`, `countdown`, `city-symphony`, `visual-investigation`, `kino-montage`, `telestrator`, `news-package`.
2. **Painting & Illustration (5)**: `crayon-book`, `watercolor`, `impasto`, `urban-sketch`, `colored-pencil`.
3. **Sketch & Board (7)**: `one-line`, `whiteboard`, `chalkboard`, `sketchnote`, `stick-explainer`, `ipad-sketch`, `marker-paper`.
4. **Traditional Crafts (7)**: `ink-wash`, `shadow-puppet`, `ukiyoe`, `papercut-red`, `paper-lantern`, `stained-glass`, `gilded-illumination`.
5. **Print & Printmaking (8)**: `risograph`, `halftone-dossier`, `woodcut`, `engraving`, `silkscreen-poster`, `printed-long-take`, `pop-art`, `vintage-collage`.
6. **Graphic & Type (8)**: `swiss-motion`, `spy-titles`, `art-deco`, `pictogram-motion`, `bauhaus-shapes`, `flat-space-explainer`, `text-flash-cuts`, `silhouette-rhythm`.
7. **Line Diagrams (8)**: `blueprint`, `iso-infographic`, `teardown`, `hardcore-info`, `precise-mechanism`, `instruction-manual`, `pen-plotter`, `assembly-line-diagram`.
8. **Cartoons (6)**: `rubber-hose`, `cel-anime-80s`, `scifi-toon`, `midcentury-toon`, `comic-history`, `manga-panels`.
9. **Games (4)**: `pixel-rpg`, `hd-2d`, `microgame`, `game-show`.
10. **Film & Tape (5)**: `ascii-crt`, `silent-film`, `backrooms`, `scratch-film`, `double-exposure`.
11. **Screens & Interfaces (6)**: `dark-keynote`, `living-screencast`, `hologram-hud`, `desktop-flythrough`, `spreadsheet`, `one-bit-dither`.
12. **Light & Lines (5)**: `circuit-board`, `firefly-pointillism`, `flow-field`, `oscilloscope-math`, `neon-tubes`.
13. **3D & Miniature (8)**: `brick-toy`, `paper-popup`, `tilt-shift`, `lowpoly-island`, `glass-product`, `memphis-diorama`, `isometric-picture-book`, `crayon-world`.
14. **Instruments & Evidence (8)**: `satellite-briefing`, `briefing-board`, `lidar-survey`, `microscope`, `archive-lighttable`, `security-xray`, `dark-documentary`, `thermal-camera`.
15. **Data & Maps (6)**: `dataviz`, `white-model`, `data-physical`, `transit-map`, `map-explainer`, `pip-simulation`.

## 3. Alur Produksi Kiki-Chii (*Concepting First*)

1. **Pilih Gaya & Kunci Cerita**: Bantu pengguna memilih 1 gaya dari 15 kategori sesuai tujuan (edukasi, peluncuran produk, dokumenter data, cerita visual).
2. **Muat 1 Panduan Saja**: Baca `STYLE.md` dan `style.json` gaya tersebut dari cache terpin (`--skill <slug>`).
3. **Review Manusia Antar-Tahap**: Kunci *storyboard*/struktur adegan dan estimasi render sebelum menjalankan render video/audio lokal (FFmpeg/Chromium/Node dipasang terpisah oleh pengguna).

## 4. Atribusi & Batas Lisensi Wajib

- Kredit upstream: **Lemo-Opuscar by Lemomo (LemoLab)** (`https://github.com/lemomo-ai/lemo-opuscar`), termasuk kontributor gaya eksternal **Memphis Diorama by EianLu** dan **Crayon World 3D by 2nd1st**.
- Lisensi upstream multi-lapis (`LICENSE.upstream`): **MIT** untuk kode; **CC BY-NC 4.0** (dengan izin tambahan untuk membaca, mengikuti, dan mengadaptasi panduan guna membuat film pribadi maupun komersial/klien) untuk dokumentasi Markdown & prompt; **CC BY 4.0** untuk film/gambar demo.
- **Film yang Anda buat sepenuhnya milik Anda** (termasuk penggunaan komersial), tetapi **jangan** mendistribusikan ulang/menjual berkas dokumentasi upstream secara komersial tanpa lisensi komersial Lemomo, dan **jangan** menyalin karakter/merek pihak ketiga (mis. Clawd, logo/UI pihak ketiga, atau 6 trek narasi TTS demo yang dikecualikan di `LICENSE.upstream`). Wrapper MSSHI ini 100% ditulis orisinal (0 byte dokumen upstream disalin ke repo publik MSSHI).
