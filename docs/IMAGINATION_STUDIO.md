# Imagination Studio — Addon Opsional untuk Kiki-Chii (Filmmaker & Content Creator)

Integrasi opsional ini menghubungkan **Kiki-Chii** (`filmmaking-videography-photography-s2`) dengan **Imagination Studio by keys+Wasserman** (powered by TensorFold) dan plugin resmi Hermes-nya:
- Repositori upstream: `https://github.com/Keys-Wasserman/Imagination-Studio-by-keys-Wasserman` (pin `16f00b462a5a389e2c5e19c2cbf7d9527ad526ea`, **Apache-2.0**, atribusi: **Keys (`github.com/drowzeys`)** & **Sam Wasserman / Wasserman Productions (`wassermanproductions.com`)**).
- Daftar Plugin Hermes: `https://hermeswatcher.com/plugins/imagination-studio` (Hermes `>= 0.22.7`, HTTP lokal `http://127.0.0.1:7870`, tanpa telemetri eksternal).

## Sifat Opsional (`public_default: false`)
- Pada instalasi publik standar (maupun Light Build Windows 10 RAM 4 GB), `imagination-studio` **tidak terpasang otomatis** (`public_default: false`).
- Cara memilih saat instalasi atau kapan saja nanti:
  ```powershell
  # 1. Saat instalasi preset yang memiliki Kiki-Chii (MuZA, Academic Mahasiswa/Dosen, Solo, Custom)
  msshi setup --mode muza-preset --with-imagination-studio

  # 2. Atau aktifkan kapan saja pada profil Kiki-Chii / bot Content Creator pilihan
  msshi optional list
  msshi optional enable imagination-studio --target-dir "D:\HermesData\profiles\kiki-chii\skills"
  ```

## Cara Kerja Sama dengan `filmmaking-videography-photography-s2`
Ketika `imagination-studio` terpasang atau dipilih, **Kiki-Chii** otomatis memadukan kurikulum MFA 5 Fase dengan alur **Slate & Studio Queue**:
1. **Fase 1 (Concepting First)**: Kunci Emosi (51%), Cerita (23%), naskah Fountain/AV, dan review manusia terlebih dahulu.
2. **Fase 2 (Slate Pre-Production)**: Ubah *Master Shot List* menjadi *Slate setups*, *coverage plan*, kontinuitas karakter/lokasi, dan *seed*. *(Tahap Slate planning ringan dan tidak butuh unduhan bobot GPU besar.)*
3. **Fase 3 (Cek Memori + Render via Antrean Studio)**: Cek headroom memori dulu (`msshi studio status --probe` / `studio_status` / `memory_status`), lalu kirim render **hanya** lewat antrean Imagination Studio (`studio_picture`, `studio_clip`, `studio_voice`, `studio_song`, `studio_sound`, `studio_job`) — **dilarang** memintas antrean dengan skrip Python terpisah.
4. **Fase 4–5 (Post-Production & Review)**: Tarik hasil dari `HERMES_HOME/plugin-data/imagination-studio/outputs` atau `$STUDIO_URL/files/<path>` kembali ke `filmcraft`, `effectcraft`, `lightcraft` (ACES/Rec.709), `soundcraft` (`-14 LUFS` / `-24 LKFS`), atau `blender`, lalu tunggu review manusia sebelum ekspor final.

## Penghubung Runtime & Catatan Perangkat Keras
- **Plugin resmi Hermes** *(opsional, dijalankan terpisah oleh pengguna)*:
  ```powershell
  hermes plugins install imagination-studio
  hermes plugins enable imagination-studio
  ```
- **Alternatif stdio MCP**: `mcp/studio-mcp.py` dengan `STUDIO_URL=http://127.0.0.1:7870`.
- **Perintah cek & rencana lokal (`0` panggilan LLM)**:
  ```powershell
  msshi studio status
  msshi studio status --probe
  msshi studio plan --concept "Video pendek sinematik 60 detik" --format short
  ```
- **Kejujuran Hardware & Lisensi**: Aplikasi Imagination Studio dan bobot model di dalamnya diunduh terpisah oleh pengguna. Render GPU lokal penuh ditujukan untuk Apple Silicon Mac / NVIDIA DGX Spark / RTX Spark ber-RAM besar (hingga 128 GiB). Pada laptop 4–16 GB RAM, gunakan untuk **Slate planning**, atau sambungkan ke **ComfyUI PC / Comfy Cloud**, atau tetap memakai jalur bawaan `ArtCraft` / `Motion-as-Code` / `Higgsfield`.
