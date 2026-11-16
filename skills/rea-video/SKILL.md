---
name: rea-video
description: Kiki-Chii membedah video referensi per shot menjadi VIDEO.md, bukti dan rencana pembuatan ulang ketika diminta. Awali dengan analisis lokal ringan; VLM, OCR/ASR, pemisahan audio, unduhan model dan generasi ulang merupakan langkah terpisah yang dipilih pengguna.
license: MIT
metadata:
  upstream: https://github.com/JuneYaooo/rea-video
  upstream_commit: 820d661e807034e0f0284262b4e93085cfd3da49
  upstream_license: Apache-2.0
  activation: contextual-filmmaking
---

# Bedah video untuk Kiki-Chii

Gunakan bersama filmmaking-videography-photography-s2 dan
auto-curiousity-for-film-making saat pengguna memberikan video referensi atau meminta
analisis cara pembuatan, shot, editing, suara dan rencana remake. Tetap mulai dari
tujuan kreatif dan review manusia; analisis referensi tidak mengizinkan menyalin aset,
identitas, merek atau suara yang tidak disediakan/diizinkan.

```text
msshi integrations source --home HERMES_ROOT --name rea-video
msshi integrations source --home HERMES_ROOT --name rea-video --fetch
msshi integrations source --home HERMES_ROOT --name rea-video --install-runtime
```

Source dan runtime Python dipasang terpisah di luar `skills/`; Python 3.10+ dan
FFmpeg/ffprobe diperlukan. Instalasi ini tidak memasang extras OCR/ASR, mengunduh bobot,
menjalankan video, membuka aplikasi, atau memanggil model. Baca source SKILL dan
referensi setup di path cache yang dilaporkan; jalankan CLI dari runtime yang dilaporkan.

Upstream mempunyai default yang dapat mengunduh model pemisahan suara pada operasi
pertama. Untuk tahap lokal ringan gunakan flag yang benar-benar ada pada pin ini:

```text
rea-video decompose INPUT.mp4 -o OUTPUT_BARU --no-vlm --no-whole --no-ocr --no-packaging --no-asr --no-speakers --no-stems --workers 1 --lang en
rea-video summary OUTPUT_BARU/breakdown.json
```

Jangan menambahkan `--vlm` ke tahap ringan itu; ia akan mengaktifkan panggilan model.
Periksa durasi/input, disk/RAM, FFmpeg, hak bahan dan output baru terlebih dahulu.
Analisis deterministik tetap menggunakan CPU/disk dan belum membuktikan klasifikasi
asal video. Tandai ketidakpastian, cek gambar kontak shot, dan minta review bila perlu.

Mulai membaca dari VIDEO.md lalu timeline/shot yang relevan. Hindari memuat seluruh
breakdown.json besar ke konteks model. Bahasa CLI pin ini hanya zh/en; penjelasan
agen dapat diterjemahkan ke Indonesia tanpa mengarang flag `--lang id`.

OCR/ASR, stem audio, VLM eksternal, remake-run atau video generasi bukan kelanjutan
otomatis: jelaskan kebutuhan unduhan/model/akun/biaya dan pakai hanya ketika dipilih.
Simpan source/editable storyboard serta rencana, lalu serahkan ke pipeline Kiki yang
tersedia (Remotion/ArtCraft/Blender) sesuai format yang benar-benar didukung.

Source Apache-2.0; wrapper MSSHI asli MIT. Tidak ada model, media contoh, dependency
atau implementasi upstream yang dibundel di dalam pemindai skill ini.
