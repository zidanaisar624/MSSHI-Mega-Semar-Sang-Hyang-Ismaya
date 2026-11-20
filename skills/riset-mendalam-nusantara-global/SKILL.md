---
name: riset-mendalam-nusantara-global
description: Khusus Val (Riset Mendalam & Metodologi Akademik Indonesia + Global). Menggabungkan pipeline riset adaptif 10 tahap (Quick/Standard/Deep, adequacy gate, devil's advocate, audit klaim & sitasi, quality gate) dengan standar akademik Indonesia (Bab I-V, SINTA 1-6, Garuda, RAMA, EYD V) dan global (Scopus/WoS, PRISMA 2020, CONSORT/STROBE/COREQ, DOI). Baca 1 file references/ sesuai kebutuhan agar hemat token.
---

# Riset Mendalam Nusantara & Global (Khusus Val)

Skill ini **hanya terpasang pada Val** sebagai mesin riset mendalam & metodologi akademik standar **Indonesia dan Global**. Bot lain (Yukino, Shizuka, Kiki-Chii, Shikaku) tidak memasang skill ini; mereka cukup mendeteksi kapan sebuah pertanyaan memerlukan riset mendalam berbukti lalu mendelegasikan bagian riset tersebut kepada **Val** (dan Val mengembalikan dossier terverifikasi ringkas ke **Shizuka** / peminta).

> **Prinsip Hemat Token (Lazy References + MSSHITrim):** Jangan membaca seluruh folder `references/` sekaligus. Pilih **1–2 file** yang paling relevan dengan tahap kerja saat ini. Seluruh keluaran tool JSON ≥ 2048 karakter otomatis dipadatkan lokal oleh **MSSHITrim (`msshi-auto-trim`)** tanpa kehilangan nilai.

## 1. Pilih Mode Sesuai Kebutuhan (Jangan Over-Pipeline)
- **Quick (1 putaran, obrolan cepat):** verifikasi 1 konsep, definisi metodologi, atau pengecekan cepat 1–3 sumber. Tidak perlu memanggil seluruh 10 tahap.
- **Standard (Plan → Riset Terarah → Draf + Jejak Bukti):** tugas kuliah mendalam, tinjauan pustaka ringkas, desain bab metodologi, atau perbandingan 5–15 jurnal.
- **Deep (Pipeline 10 Tahap Penuh):** proposal/naskah **Skripsi, Tesis, Disertasi**, tinjauan sistematis (PRISMA), artikel **SINTA 1–6 / Scopus / WoS**, atau laporan riset strategis berisiko tinggi.

## 2. Peta Referensi Lazy (`references/` — Baca Hanya Yang Diperlukan)
1. [references/pipeline.md](references/pipeline.md) — Alur adaptif **10 tahap** (Rencana → Tesis & Perspektif → Riset Terarah + *Adequacy Gate* → Kerangka → Draf → Kritik Mandiri → *Devil's Advocate* → Audit Klaim → Audit Sitasi/DOI → Revisi & Skor Mutu 1–10 maks. 2 putaran) dengan *token-efficient chaining*.
2. [references/metodologi.md](references/metodologi.md) — Paradigma riset, desain kuantitatif, kualitatif, metode campuran (*mixed methods*), R&D & PTK, strategi sampling, validitas/reliabilitas, dan *trustworthiness*.
3. [references/indonesia.md](references/indonesia.md) — Standar akademik Indonesia: arsitektur Bab I–V (Skripsi/Tesis/Disertasi), SINTA 1–6 (ARJUNA), portal Garuda/RAMA/Neliti/Perpusnas, EYD V, etika riset & cek similaritas sesuai pedoman kampus.
4. [references/global.md](references/global.md) — Standar publikasi internasional: Scopus Q1–Q4 & Web of Science, PRISMA 2020, CONSORT, STROBE, COREQ, CRediT, preregistrasi OSF/PROSPERO, verifikasi DOI/Crossref/OpenAlex, dan korespondensi *rebuttal*.
5. [references/glosarium-id-en.md](references/glosarium-id-en.md) — Glosarium dwibahasa Indonesia ↔ Inggris untuk istilah metodologi, statistik, dan publikasi ilmiah.
6. [references/checklist.md](references/checklist.md) — Daftar periksa siap pakai untuk Proposal, Sidang Skripsi/Tesis/Disertasi, Submit Jurnal SINTA/Scopus, dan Audit Anti-Halusinasi.

## 3. Integrasi dengan Ekosistem Riset Val yang Sudah Ada
Skill ini **melengkapi, bukan menghapus** skill riset yang sudah aktif pada Val:
- **Pencarian & Katalog Sumber:** kombinasikan dengan `deep-research`, `literature-review`, `MuZA_Search.ipynb`, dan `paper-context-resolver`.
- **Peta Dokumen & Sitasi Akurat:** terapkan **Lima Lapis Konteks** (baca daftar isi/abstrak dulu, ekstrak hanya halaman relevan via `unlimited-ocr-2`) dan kunci setiap klaim dengan `backward-traceability` (`doc#halaman` atau `DOI`).
- **Kebaruan & Prediksi Kuantitatif:** gunakan `novelty-assessment` untuk menguji *research gap*, `data-analysis` + `math-reasoning` untuk statistik, serta `timesfm-forecasting` (dengan *chronological holdout* + *naive baseline*) bila riset melibatkan peramalan deret waktu.
- **Penulisan & Format Akhir:** kirim dossier terverifikasi (padatkan handoff internal dengan `caveman`, jaga kutipan/angka/DOI 100% utuh) agar dirakit ke naskah final lewat `research-paper-writing`, `muza-skripsi-template` (`.docx` kampus), `humanizer-indonesia`, atau `humanizer-en`.

## 4. Batasan Wajib (Zero-Hallucination & Privasi)
- **Dilarang keras mengarang DOI, judul jurnal, penulis, angka statistik, atau halaman kutipan.** Jika sumber belum terverifikasi, tandai eksplisit `[PERLU VERIFIKASI SUMBER]`.
- Tidak menjalankan server web, bot Discord, cron latar belakang, atau pemanggilan LLM otomatis tanpa izin pengguna.
- Jangan menyalin atau merujuk dokumen dari folder privat terlarang pengguna; patuhi batas akses folder kerja aktif.
