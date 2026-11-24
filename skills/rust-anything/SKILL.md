---
name: rust-anything
description: Migrasi dan port bertahap kode TypeScript/JS, Python, C, Go, Ruby, atau Java ke Rust yang terverifikasi perilaku aslinya (profile, plan, bridge, record, port, diff, bench, shadow, gate) untuk Coder (Shikaku / Sir. Robot) melalui CLI/MCP rust-anything terpisah.
license: MIT
metadata:
  upstream: https://github.com/erkamyaman/rust-anything
  upstream_commit: 584e63888495a5568b8400a6a4194e43885ae609
  upstream_license: MIT
  activation: contextual-coding-rust-migration
---

# Migrasi & Porting Terverifikasi ke Rust (`rust-anything`)

Gunakan skill ini pada peran Coder (`shikaku` / `Sir. Robot`) ketika pengguna meminta:
- memindahkan (*port*) satu fungsi panas (*hot path*) atau seluruh aplikasi dari TypeScript/JavaScript, Python, C, Go, Ruby, atau Java ke Rust,
- membuktikan kesetaraan perilaku hasil tulis ulang Rust terhadap aplikasi asli (*differential verification*), atau
- merencanakan tahapan migrasi Rust secara bertahap dengan metrik performa dan *gate* kelulusan yang jelas.

Wrapper MSSHI ini sepenuhnya **model-agnostic**: tetap memakai provider dan model pilihan pengguna di Hermes tanpa mengubah `config.yaml`, endpoint, API key, atau `SOUL.md`.

## 0. Aturan Wajib Penggunaan Rust Anti-Bug (*Hot-Path Only*)

Agar basis kode tetap bersih, cepat diuji, dan bebas bug kompilasi/*borrow-checker* yang tidak perlu:

1. **Gunakan Python / TypeScript / JavaScript / Go Secara Default** untuk orkestrasi agen, CLI *wrapper*, skrip automasi, antarmuka web, *glue code*, dan fitur umum yang tidak terikat *bottleneck* CPU/memori.
2. **Gunakan Rust HANYA untuk *Hot-Path* Terbukti atau Binary Portabel Kecil**: seperti pemrosesan piksel/audio/teks masif, *parser*/kompresi berkecepatan tinggi, atau *launcher* native ringan tanpa *runtime* berat — selalu didahului bukti profil (`profile`) dan diakhiri verifikasi perilaku (`record -> port -> diff -> bench -> gate`).
3. **Dilarang Menulis Ulang ke Rust Tanpa Alasan Terukur**: Jika pengguna belum meminta Rust secara eksplisit dan masalah performa dapat diselesaikan dengan algoritma/indeks/cache yang tepat di bahasa asli, utamakan perbaikan di bahasa asli terlebih dahulu.

## 1. Cache Panduan Terpin di Luar `skills/` (Hemat Token)

Panduan resmi `rust-anything` (`SKILL.md` dan `whole-app.md`) disimpan di cache sumber terpin di luar pemindai `skills/` agar startup Hermes tetap cepat:

```text
msshi integrations source --home HERMES_ROOT --name rust-anything
msshi integrations source --home HERMES_ROOT --name rust-anything --fetch
msshi integrations source --home HERMES_ROOT --name rust-anything --list
msshi integrations source --home HERMES_ROOT --name rust-anything --skill rust-anything
```

- Tanpa `--fetch`, perintah hanya memeriksa status lokal (`0` panggilan model, `0` koneksi jaringan).
- `--fetch` memverifikasi hash Git blob & SHA-256 pada commit terpin `584e63888495a5568b8400a6a4194e43885ae609` ke `msshi-private/context-sources/rust-anything/584e63888495a5568b8400a6a4194e43885ae609`.
- Untuk migrasi seluruh aplikasi (*whole app rewrite*), baca `whole-app.md` dari folder `source_path` tersebut sesuai kebutuhan.

## 2. Alur Kerja Bertahap (Unit per Unit)

1. **Profile & Plan**: Petakan jalur kritis, batas modul, dan dependensi sebelum menulis satu baris kode Rust pun.
2. **Bridge & Record Ground Truth**: Rekam perilaku nyata aplikasi asli sebagai acuan kebenaran (*ground truth*).
3. **Port Satu Unit**: Tulis implementasi Rust terisolasi (batch loop panas agar dapat memanfaatkan banyak core bila relevan).
4. **Diff, Bench, Shadow & Gate**: Bandingkan keluaran terhadap rekaman asli, ukur peningkatan performa, dan nyatakan unit selesai **hanya jika `gate` lulus**.

## 3. Prasyarat & Batas Keamanan

- Binary CLI / MCP `rust-anything` (`cargo install rust-anything` atau `npx rust-anything`) dan toolchain Rust (`rustc`/`cargo`) merupakan prasyarat terpisah yang dipasang eksplisit oleh pengguna; wrapper ini tidak memasang paket, daemon, atau MCP secara otomatis.
- Seluruh penulisan ulang kode dan pengujian tetap dibatasi pada repositori/workspace yang disetujui pengguna.

Lisensi upstream: **MIT License** (Copyright (c) 2026 Erkam Yaman / `erkamyaman`, teks asli disimpan di `LICENSE.upstream`). Wrapper MSSHI asli berlisensi MIT.
