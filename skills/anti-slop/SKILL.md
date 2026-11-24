---
name: anti-slop
description: Filter kualitas lintas 5 bot untuk mencegah klise AI, basa-basi generik, struktur antarmuka template seragam, dan boilerplate kode berulang sebelum hasil dikirim ke pengguna.
license: MIT
metadata:
  upstream: https://github.com/miqdadbadjuber/anti-slop
  upstream_commit: 7f6a03df2931c12cb244dc4ab14ee4866b0ac2ba
  upstream_license: MIT
  activation: core-quality-gate-all-bots
---

# Gerbang Kualitas Anti-Slop (`anti-slop` — Semua 5 Bot)

Gunakan skill ini sebagai penyaring mutu sebelum menyerahkan draf tulisan, analisis, kode, atau rancangan visual pada kelima peran (**Yukino**, **Shizuka**, **Val**, **Kiki-Chii**, dan **Shikaku / Sir. Robot**).

## Pembagian Peran Tanpa Tumpang Tindih

- **`anti-slop` (gerbang pencegahan lintas 5 bot)**: Mencegah pola generik AI sejak penyusunan awal — baik pada teks, struktur argumen, komponen UI, maupun *boilerplate* kode.
- **`humanizer-indonesia` & `humanizer-en`**: Penyuntingan akhir keluwesan bahasa alami setelah substansi selesai.
- **`unslop`**: Audit mendalam tata letak dan hierarki antarmuka khusus tugas desain UI (`kiki-chii`, `val`, `shikaku`).

## Aturan Inti Anti-Slop per Domain

1. **Teks, Riset & Penjelasan Akademik (`yukino`, `shizuka`, `val`)**:
   - Pangkas kalimat pembuka basa-basi (*"Tentu, ini pertanyaan menarik!"*, *"Di era modern yang berkembang pesat..."*, *"Penting untuk diingat bahwa..."*). Masuk langsung ke inti jawaban atau bukti.
   - Hindari kontras mekanis berulang (*"Bukan sekadar X, melainkan Y"*), daftar tiga kata sifat kosong, dan klaim bombastis tanpa rujukan (`doc#halaman`, DOI, atau data terukur).
   - **Jaga 100% utuh**: kutipan langsung, sitasi akademik, angka, rumus, kode, nama pilihan pengguna, dan *Voice Card* pada `match-my-writing-style`.
2. **Desain Antarmuka & Konten Visual (`kiki-chii`, `shikaku`)**:
   - Hindari *template AI UI slop*: gradien ungu-biru generik tanpa alasan merek, kartu 3-kolom identik dengan ikon emoji acak, *copywriting* klise (*"Supercharge your workflow"*), dan dekorasi berlebihan yang mengorbankan keterbacaan.
   - Pilih tipografi berkarakter, hierarki kontras jelas, ruang kosong terukur, dan warna yang sesuai identitas proyek.
3. **Kode & Rekayasa Perangkat Lunak (`shikaku`)**:
   - Hindari abstraksi berlapis yang hanya dipakai sekali, komentar yang sekadar mengulang nama fungsi, `try/except: pass` yang menyembunyikan akar masalah, serta dependensi berat untuk hal yang sudah tersedia di *standard library*.

Wrapper MSSHI ini 100% **model-agnostic** (`0` perubahan pada `config.yaml`, provider, model, atau `SOUL.md`). Lisensi upstream: **MIT License** (Copyright (c) 2026 Miqdad Badjuber, disimpan pada `LICENSE.upstream`).
