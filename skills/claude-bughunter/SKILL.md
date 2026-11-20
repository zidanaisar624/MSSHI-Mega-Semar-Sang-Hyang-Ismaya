---
name: claude-bughunter
description: Kerangka kerja audit kerentanan, triage, validasi bukti, dan pelaporan keamanan terotorisasi (83 skill, 15 command, 681 pola laporan terungkap) untuk Coder (Shikaku / Sir. Robot) khusus pada aset milik sendiri, program bug bounty in-scope, atau lab/CTF berizin.
license: MIT
metadata:
  upstream: https://github.com/elementalsouls/Claude-BugHunter
  upstream_commit: 0e70a021e59d6875004e7a563f8511aca2ba3bc1
  upstream_license: MIT (code); CC-BY-4.0 (documentation and skill content)
  activation: contextual-authorized-security
---

# Audit Kerentanan & Triage Terotorisasi (Claude-BugHunter)

Gunakan skill ini pada peran Coder (`shikaku` / `Sir. Robot` / Antigravity) saat pengguna meminta
peninjauan kerentanan, *code review* keamanan, validasi *triage*, redaksi bukti (*evidence hygiene*),
atau penyusunan laporan keamanan untuk aset yang **dimiliki pengguna atau memiliki izin tertulis /
ruang lingkup (*Rules of Engagement* / program *bug bounty* in-scope / CTF / lab uji) yang jelas**.

Meskipun repositori upstream bernama `Claude-BugHunter`, wrapper MSSHI sepenuhnya **model-agnostic**:
gunakan provider dan model yang telah dipilih pengguna di Hermes tanpa mengubah konfigurasi model,
provider, endpoint, API key, atau SOUL.

## 1. Lokasi Pustaka & Cache Lokal Terpin

Seluruh 83 skill, 15 panduan command, indeks `cbh/data/skill_index.json`, dan 681 pola laporan
keamanan disimpan di cache sumber terpin di luar pemindai `skills/` agar pemindaian skill tetap
cepat dan paket inti tetap ringan:

```text
msshi integrations source --home HERMES_ROOT --name claude-bughunter
msshi integrations source --home HERMES_ROOT --name claude-bughunter --fetch
msshi integrations source --home HERMES_ROOT --name claude-bughunter --list
msshi integrations source --home HERMES_ROOT --name claude-bughunter --skill triage-validation
```

- Tanpa `--fetch`, perintah hanya menampilkan status lokal (`0` panggilan model, `0` koneksi jaringan).
- `--fetch` mengunduh dan memverifikasi hash Git blob serta SHA-256 pada commit terpin
  `0e70a021e59d6875004e7a563f8511aca2ba3bc1` ke
  `msshi-private/context-sources/claude-bughunter/0e70a021e59d6875004e7a563f8511aca2ba3bc1`.
- Baca hanya 1–2 file skill/referensi relevan dari `source_path` (atau lewat `--skill <nama>`);
  **jangan** memuat seluruh 83 skill atau seluruh arsip laporan ke konteks sekaligus.

## 2. Gerbang Otorisasi Wajib (Before Any Security Work)

1. **Verifikasi Ruang Lingkup & Izin**: Sebelum melakukan pengujian atau analisis target eksternal,
   konfirmasi bahwa target adalah:
   - Repositori/aplikasi/infrastruktur milik pengguna sendiri, atau
   - Aset yang tercantum eksplisit *in-scope* pada program *bug bounty* / *Rules of Engagement* tertulis, atau
   - Lingkungan lab/pelatihan terotorisasi (seperti DVWA, OWASP Juice Shop, atau CTF).
2. **Tolak Penggunaan Tanpa Izin**: Jangan menjalankan pemindaian massal, eksploitasi target tanpa
   otorisasi, *credential stuffing*, pembuatan malware, *persistence*, atau *post-exploitation* di luar
   mandat resmi (selaras dengan `SECURITY.md` upstream).
3. **Tanpa Auto-Scan & Tanpa MCP Otomatis**: Wrapper ini **tidak** memasang Burp MCP, HackerOne MCP,
   scanner eksternal, ataupun *hook/daemon* otomatis. Eksekusi alat uji apa pun tetap memerlukan
   persetujuan eksplisit pengguna.

## 3. Lapisan Metodologi yang Dapat Dimuat Sesuai Konteks

- **Metodologi & Scope**: `bb-methodology`, `recon-scope-triage`, `redteam-mindset`, `ENGAGEMENTS.md`,
  dan panduan command (`commands/scope.md`, `commands/surface.md`, `commands/triage.md`).
- **Kelas Kerentanan Aplikasi & API (`hunt-*`)**: Pilih hanya kelas relevan dengan arsitektur target
  (misalnya `hunt-idor`, `hunt-auth-bypass`, `hunt-oauth`, `hunt-graphql`, `hunt-ssrf`, `hunt-xss`,
  `hunt-sqli`, `hunt-csrf`, `hunt-race-condition`, `hunt-business-logic`, `hunt-llm-ai`, `hunt-rag-vector`,
  `hunt-nextjs`, `hunt-laravel`, `hunt-nodejs`, `hunt-k8s`, `hunt-cloud-misconfig`).
- **Validasi, Kebersihan Bukti, & Pelaporan**: `triage-validation` (*7-Question Gate*), `evidence-hygiene`
  (redaksi rahasia/PII sebelum berbagi bukti), `report-writing`, dan `redteam-report-template`.
- **Sinergi dengan `grim-prompter`**: Gunakan `grim-prompter` terlebih dahulu untuk *threat model*
  arsitektur secara *read-only*, lalu pakai kelas `hunt-*` atau `triage-validation` dari `claude-bughunter`
  untuk memverifikasi kontrol keamanan dan menyusun rekomendasi mitigasi konkret.

Lisensi upstream bersifat ganda: kode berlisensi **MIT** (Copyright (c) 2026 Sachin Sharma,
`LICENSE.upstream`), sedangkan dokumentasi dan konten skill berlisensi **CC BY 4.0**
(`LICENSE-CONTENT.upstream`, beserta `NOTICE.upstream`). Wrapper MSSHI asli berlisensi MIT.
