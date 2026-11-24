---
name: open-code-review
description: Pipeline review kode hibrida deterministik + agen baris-per-baris (Alibaba OpenCodeReview / CLI ocr) khusus Coder (Shikaku / Sir. Robot) untuk mengaudit git diff, commit, branch, atau PR dengan verifikasi anti-false-positive sebelum pelaporan.
license: MIT
metadata:
  upstream: https://github.com/alibaba/open-code-review
  upstream_commit: f6379f71edba1e59dbc056e8f455df1f84396498
  upstream_license: Apache-2.0
  activation: contextual-coding-diff-review
---

# OpenCodeReview (`alibaba/open-code-review` — Khusus Coder)

Gunakan skill ini pada peran **Coder (`shikaku` / `Sir. Robot`)** saat meninjau perubahan kode (*staged changes*, *commit*, *branch diff*, atau *Pull Request*) sebelum *commit*, *merge*, atau serah terima rilis.

OpenCodeReview (`ocr`) menggabungkan **pra-pemrosesan deterministik** (konteks Git, batas fungsi/simbol, cakupan bahasa) dengan **verifikasi berlapis (*verify-before-report*)** agar temuan *code review* akurat pada baris kode nyata dan bebas kebisingan (*false positive*).

## 1. Alur Kerja Triad Kualitas Kode Coder (Hemat Token & Presisi Tinggi)

Untuk perubahan kode menengah hingga besar, jalankan urutan tiga serangkai ini pada `shikaku`:

1. **Pra-Cek & Refaktor AST Deterministik (`ast-grep` / `sg`)**: Cari pola kode rentan atau terapkan refaktor struktural lintas berkas dengan `0` token LLM.
2. **Bersihkan Kode Mati & Ekspor Yatim (`knip`)**: Pada proyek JS/TS, hapus berkas, ekspor, tipe, dan dependensi tak terpakai sebelum review.
3. **Audit Diff Baris-per-Baris (`open-code-review` / `ocr`)**: Tinjau `git diff` secara tajam — baik melalui metode disiplin `open-code-review` langsung oleh Coder maupun melalui CLI lokal `ocr` bila terpasang.

## 2. Disiplin Review Wajib (Baik Tanpa maupun Dengan CLI `ocr`)

1. **Kumpulkan Konteks Diff Nyata Dulu**: Periksa `git status --short`, `git diff` / `git diff --staged`, serta fungsi pemanggil (*callers*) dan tes terkait sebelum memberi penilaian.
2. ** Empat Fokus Temuan Berbukti**:
   - **Bug Logika & Edge Case**: *null/undefined/None*, *race condition*, *off-by-one*, kebocoran *resource*/file handle, path Windows berspasi/apostrof, dan kegagalan *rollback*.
   - **Keamanan & Batas Kepercayaan**: injeksi perintah/path traversal/symlink, eksposur kredensial/token, SSRF, atau melewati *allowlist* (padukan dengan `grim-prompter` & `claude-bughunter` bila menyentuh permukaan keamanan).
   - **Kontrak API & Kompatibilitas Mundur**: perubahan skema JSON/CLI/tipe balik yang memutus pemanggil lama tanpa migrasi.
   - **Cakupan Tes**: pastikan setiap perbaikan bug disertai uji regresi yang benar-benar dijalankan.
3. **Verifikasi Sebelum Lapor (*Verify-Before-Report*)**: Buang komentar spekulatif atau sekadar selera gaya yang sudah ditangani formatter; laporkan hanya temuan yang dapat ditunjukkan `file:baris`, skenario pemicunya, dan saran perbaikan konkretnya.

## 3. Penggunaan CLI `ocr` Opsional (Jika Dipasang Pengguna)

Jika pengguna memasang CLI resmi secara terpisah (`npm install -g @alibaba-group/open-code-review`), jalankan sesuai target review yang disetujui:

```text
ocr --version
ocr review --staged
ocr review --commit HEAD
ocr review --base main
```

- **Prasyarat & Batas Keamanan**: CLI `ocr` tidak dipasang otomatis oleh MSSHI dan memakai konfigurasi BYO LLM milik pengguna sendiri bila dijalankan. Jangan pernah mengubah `config.yaml`, provider, model utama, API key, atau `SOUL.md` Hermes. Aturan spesifik proyek dapat disimpan di `.ocr/skills/` pada repositori kerja jika diminta pengguna.

Lisensi upstream: **Apache License 2.0** (`alibaba/open-code-review`, disimpan di `LICENSE.upstream`). Wrapper MSSHI berlisensi MIT.
