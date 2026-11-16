---
name: remote-jobs
description: Cari perusahaan ramah kerja remote dari direktori remoteintech ketika topik karier muncul; tersedia pada kelima bot. Cocokkan lokasi, zona waktu dan peran lalu verifikasi lowongan aktif secara terpisah, tanpa job scan atau layanan latar belakang.
license: MIT
metadata:
  upstream: https://github.com/remoteintech/remote-jobs
  upstream_commit: 155939ad935d22afa8edbaaf0770b99f9d0dbf0d
  upstream_license: ISC
  activation: context-or-explicit
---

# Direktori perusahaan remote

Yukino, Shizuka, Val, Kiki-Chii dan Shikaku dapat memakai direktori yang sama ketika
pengguna membahas pekerjaan/karier. Tidak ada proses atau panggilan model saat boot.
Indeks instruksi host tetap dapat mempunyai biaya konteks kecil; jangan menjanjikan
semua token percakapan gratis.

```text
msshi integrations source --home HERMES_ROOT --name remote-jobs
msshi integrations source --home HERMES_ROOT --name remote-jobs --fetch
msshi integrations source --home HERMES_ROOT --name remote-jobs --query python --limit 10
```

`--fetch` eksplisit mengambil sumber terpin. Query sesudahnya hanya membaca Markdown
lokal di cache privat, tidak menjalankan build website, Node, crawling, browser atau LLM.
Hasil adalah kecocokan direktori perusahaan, bukan bukti posisi masih terbuka.

Periksa batas negara, zona waktu, status kontrak dan halaman karier resmi untuk posisi
yang dipilih. Berikan sumber dan ketidakpastian; padukan dengan CareerOps serta CV
pengguna bila diminta. Jangan mengirim aplikasi, outreach atau pesan tanpa instruksi.

Kode/direktori proyek ISC; boilerplate MIT dan font SIL OFL tetap mempunyai notices
masing-masing. [Sumber terpin](https://github.com/remoteintech/remote-jobs/tree/155939ad935d22afa8edbaaf0770b99f9d0dbf0d).
