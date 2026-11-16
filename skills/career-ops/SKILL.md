---
name: career-ops
description: Bantu pencarian kerja, kecocokan CV-lowongan skor 1-5, CV/cover letter, tracker dan latihan wawancara ketika topik karier dibahas atau diminta. Gunakan source CareerOps lengkap dan data pengguna privat; tidak melakukan scan, kirim aplikasi atau panggilan model di latar belakang.
license: MIT
metadata:
  upstream: https://github.com/career-ops-hq/career-ops
  upstream_commit: c687a6f89aa766de468d41402df1ce24bdd86315
  activation: context-or-explicit
---

# CareerOps untuk kelima bot

Tersedia bagi Yukino, Shizuka, Val, Kiki-Chii dan Shikaku. Yukino membantu ide/tujuan,
Shizuka merangkum strategi, Val memeriksa bukti lowongan, Kiki memperjelas portofolio,
dan Shikaku menilai bukti engineering. Peran ini dapat berkonsultasi melalui mekanisme
delegasi profil yang benar-benar tersedia; memasang skill tidak otomatis memulai diskusi.

Muat hanya saat ada konteks pekerjaan, CV, lowongan atau wawancara. Jangan menjalankan
job scan, model atau layanan otomatis pada boot maupun percakapan lain. Metadata skill
dapat masuk indeks host; ini bukan jaminan tagihan/token selalu nol.

## Source, runtime dan data

```text
msshi integrations source --home HERMES_ROOT --name career-ops
msshi integrations source --home HERMES_ROOT --name career-ops --fetch
msshi integrations source --home HERMES_ROOT --name career-ops --install-runtime
```

Status hanya membaca. `--fetch` mengambil source yang dipin di luar `skills/`.
`--install-runtime` adalah setup dependency Node/npm eksplisit dengan lifecycle scripts
dinonaktifkan; tidak mengunduh browser atau menjalankan scan/model. Kebutuhan browser
untuk PDF atau interaksi portal ditinjau terpisah, bukan dipasang saat boot.

Gunakan `source_path` sebagai PROJECT_ROOT, baca AGENTS.md dan mode yang diperlukan.
Source harus memiliki AGENTS.md dan `modes/`; menyalin SKILL.md saja belum cukup.
User Layer berada pada `data_root` privat yang dilaporkan status. Set
`CAREER_OPS_DATA_DIR` ke sana hanya untuk proses CareerOps. CV/profil, tracker dan
output milik pengguna tidak ditulis ke cache source, repo publik, atau profil bot lain.
Jika `cv_present` masih false, minta bahan yang diperlukan ketika tugas karier dimulai;
jangan mengarang evaluasi personal atau menggunakan CV contoh milik upstream.

## Kerja dan review

Gunakan mode asli upstream yang relevan: skor 1-5 adalah rekomendasi berdasarkan
CV dan bukti JD, bukan kepastian diterima. Tandai syarat lokasi, zona waktu, senioritas,
hak kerja dan tanggal bukti. Direktori remote-jobs merupakan bahan pencarian awal;
verifikasi lowongan aktif pada laman karier perusahaan saat diminta.

Pertahankan fakta pengalaman pengguna saat menyunting CV. Buat draf outreach/aplikasi
untuk ditinjau; izin memasang skill bukan izin mengirim pesan atau menekan Submit.
Provider/model/SOUL/MoA pengguna tetap utuh. Operasi model, portal dan browser dapat
memakai kredit/kuota; jelaskan scope yang belum tersedia sebelum menyebutnya siap.

Kode upstream MIT; data `employers/` memakai CC BY 4.0 dan ketentuan merek terpisah.
Paket MSSHI ini berisi wrapper asli, bukan CV, dependency atau seluruh source upstream.
