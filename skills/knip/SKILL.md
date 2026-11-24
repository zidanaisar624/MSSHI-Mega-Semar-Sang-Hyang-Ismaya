---
name: knip
description: Pendeteksi deterministik berkas mati, ekspor/tipe tak terpakai, dan dependensi yatim pada proyek JavaScript/TypeScript & monorepo (webpro-nl/knip) khusus Coder (Shikaku / Sir. Robot) sebagai pendamping open-code-review.
license: MIT
metadata:
  upstream: https://github.com/webpro-nl/knip
  upstream_commit: 74c07a6361e720ee31ac2e428c6b6648f5598210
  upstream_license: ISC
  activation: contextual-coding-deadcode-hygiene
---

# Audit Dead Code, Ekspor & Dependensi (`knip` — Pendamping Coder)

Gunakan skill ini pada peran **Coder (`shikaku` / `Sir. Robot`)** setelah menambah fitur, menghapus komponen lama, atau melakukan refaktor pada proyek **JavaScript, TypeScript, Node.js, React/Next/Vite, dan monorepo** agar tidak ada kode mati (*dead code*) atau dependensi membengkak yang lolos ke repositori.

## 1. Mengapa `knip` Mendampingi `open-code-review` & `ast-grep`

 agen AI sering meninggalkan fungsi *helper* lama, tipe TypeScript yatim, berkas komponen yang sudah digantikan, atau paket di `package.json` yang tidak lagi diimpor. `open-code-review` fokus pada `git diff` baris yang berubah, sedangkan **`knip`** memeriksa **graf impor seluruh proyek** secara deterministik (`0` token LLM) untuk menemukan apa yang seharusnya ikut dibersihkan.

## 2. Alur Pemeriksaan Aman (Read-Only Dulu!)

Jika proyek memiliki `package.json` dan pengguna telah memasang Node/npm atau `knip`, jalankan mode pemeriksaan *read-only* terlebih dahulu:

```text
# Audit seluruh berkas, ekspor, tipe, dan dependensi tak terpakai (read-only)
npx --no-install knip --no-progress

# Fokus hanya pada berkas & ekspor tak terpakai (cepat saat refaktor)
npx --no-install knip --files --exports --no-progress

# Fokus hanya pada dependensi package.json
npx --no-install knip --dependencies --no-progress
```

- **Jangan jalankan `--fix` buta tanpa meninjau hasil**: Pastikan simbol yang ditandai bukan *public entrypoint* library, *dynamic import*, atau *plugin hook* eksternal. Jika memang *entrypoint* sah, daftarkan pada `knip.json` ketimbang menghapusnya.
- Jangan mengunduh paket dari internet tanpa izin (`npx --no-install` memakai instalasi lokal proyek/global yang sudah ada).

## 3. Batas Keamanan & Kompatibilitas

- Sepenuhnya **model-agnostic**: tidak pernah mengubah `config.yaml`, provider, model, atau `SOUL.md` Hermes.
- Lisensi upstream: **ISC License** (Copyright 2022–2026 Lars Kappert / `webpro-nl/knip`, disimpan di `LICENSE.upstream`). Wrapper MSSHI berlisensi MIT.
