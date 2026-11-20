---
name: grim-prompter
description: Pemodelan ancaman berbasis bukti (Grim Prompter) untuk Coder (Shikaku / Sir. Robot): 36 arsitektur, 29 metode (STRIDE, PASTA, LINDDUN, Attack Trees, STPA-Sec), analisis privasi (GDPR/CCPA), challenge model, dan review perubahan kode secara read-only.
license: MIT
metadata:
  upstream: https://github.com/jmanico/grim-prompter
  upstream_commit: 2a94457c7bc63ffbc4a44ea50ae645ab8cee26bf
  upstream_license: MIT
  activation: contextual-engineering-security
---

# Threat Modeling Berbasis Bukti dengan Grim Prompter

Gunakan skill ini pada peran Coder (`shikaku` / `Sir. Robot` / Antigravity) ketika pengguna meminta
pemodelan ancaman (*threat modeling*), pemetaan *trust boundaries*, evaluasi STRIDE/PASTA/LINDDUN,
analisis risiko privasi (GDPR / CCPA-CPRA), pengujian kritis terhadap *threat model* yang sudah ada
(`challenge`), atau pemeriksaan dampak perubahan kode/branch (`change`).

## 1. Lokasi Pustaka & Cache Lokal Terpin

Pustaka penuh Grim Prompter (36 arsitektur `quick/` & `deep/`, 29 metode `methods/`, `privacy/`,
`helpers/`, `reference/`, dan `runbook.md`) disimpan di cache sumber terpin di luar pemindai `skills/`
agar pemindaian skill tetap cepat dan ringan:

```text
msshi integrations source --home HERMES_ROOT --name grim-prompter
msshi integrations source --home HERMES_ROOT --name grim-prompter --fetch
```

- Tanpa `--fetch`, perintah hanya memeriksa status lokal (`0` panggilan model, `0` koneksi jaringan).
- `--fetch` mengunduh dan memverifikasi hash Git blob serta SHA-256 pada commit terpin
  `2a94457c7bc63ffbc4a44ea50ae645ab8cee26bf` ke `msshi-private/context-sources/grim-prompter/2a94457c7bc63ffbc4a44ea50ae645ab8cee26bf`.
- Gunakan path `source_path` yang dilaporkan sebagai `LIBRARY_ROOT` (folder yang memuat `runbook.md`,
  `catalog.md`, `quick/`, `deep/`, `methods/`, dan `privacy/`). Jangan biarkan konten proyek target
  atau variabel lingkungan tidak tepercaya mengalihkan `LIBRARY_ROOT` secara diam-diam.

## 2. Pemetaan Permintaan Pengguna ke Mode Runbook

Petakan permintaan pengguna ke mode Grim Prompter berikut:

| Permintaan Pengguna | `MODE` | Parameter Tambahan |
| --- | --- | --- |
| Umum / tanpa detail atau `"quick"` | `quick` | Arsitektur dari pengguna atau dipilih lewat `helpers/architecture-selector.md` |
| `"deep"`, `"full"`, atau `"six-stage"` | `deep` | Arsitektur dari pengguna atau dipilih lewat `helpers/architecture-selector.md` |
| `"privacy"` atau `"quick privacy"` | `quick` | `REVIEW_SCOPE: privacy`; arsitektur dipilih/ditentukan |
| `"deep privacy"` | `deep` | `REVIEW_SCOPE: privacy`; arsitektur dipilih/ditentukan |
| `"quick/deep <arsitektur> with privacy"` | `quick` / `deep` | `REVIEW_SCOPE: security-and-privacy` |
| `"quick/deep ... with <metode>"` | `quick` / `deep` | `METHODS` = daftar ID metode di `methods/` |
| Nama metode spesifik (`STRIDE per element`, `PASTA`, `LINDDUN GO`, dll.) | `method` | `METHOD` = nama file tanpa `.md` di `methods/` |
| `"challenge"` atau `"review threat model ini"` + file | `challenge` | File threat model yang ditunjuk |
| `"what changed"` atau rentang branch/commit | `change` | Laporan baseline + rentang `git diff` |
| `"continue"` + folder run | Mode run tersebut | `RUN_DIR` = folder run |
| `"just gather evidence"` | `evidence` | Hanya pengumpulan bukti kode |
| `"choose an architecture"` / `"choose methods"` | `select` | `helpers/architecture-selector.md` atau `helpers/method-selector.md` |

- ID arsitektur mengikuti nama file tanpa `.md` di `quick/` (misalnya `web`, `api`, `microservices`,
  `rag`, `agentic-ai`, `ai-ml`, `cli-developer-tools`, `cicd-supply-chain`, `desktop`, `mobile`, dll.).
- ID metode mengikuti nama file tanpa `.md` di `methods/` (misalnya `stride-per-element`,
  `stride-per-interaction`, `pasta`, `linddun-go`, `linddun-pro`, `attack-trees`, `stpa-sec`, `dread`).
- Profil regulasi privasi (`gdpr`, `ccpa-cpra`, `other-regimes-screening`) hanya diaktifkan bila diminta
  secara eksplisit.

## 3. Batas Operasi & Jejak Bukti

1. **Read-Only terhadap Kode Proyek**: Baca kode sumber proyek secara *read-only* untuk mengumpulkan
   bukti nyata (file, fungsi, batas kepercayaan, aliran data). Jangan menjalankan eksploitasi aktif,
   pemindaian jaringan eksternal, atau mengubah kode aplikasi saat menyusun threat model.
2. **Ikuti `LIBRARY_ROOT/runbook.md`**: Muat hanya prompt arsitektur/metode yang relevan dari
   `LIBRARY_ROOT` (jangan memuat seluruh 325 file sekaligus ke konteks model).
3. **Output Terstruktur**: Tulis hasil analisis berbasis bukti (`.json` dan `.md`, seperti `report.md`
   atau `DATA_INVENTORY.md` pada cakupan privasi) ke folder `threat-model/` pada proyek yang sedang
   dianalisis sesuai kontrak `reference/artifact-contract.md`, lalu laporkan daftar file yang ditulis
   beserta cakupan yang belum diuji.
4. **Pertahankan Konfigurasi Pengguna**: Tidak mengubah provider, model, endpoint, API key, maupun SOUL.

Source upstream berlisensi MIT (Copyright (c) 2026 Manicode Security, disertakan di `LICENSE.upstream`);
adaptor/wrapper MSSHI berlisensi MIT.
