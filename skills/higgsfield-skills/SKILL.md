---
name: higgsfield-skills
description: Rutekan dan jalankan kebutuhan produksi kreatif gambar, video, brand kit, photoshoot produk, maupun Soul ID ke Higgsfield CLI & companion skills dengan gerbang wajib koneksi akun pengguna saat kreasi konten diperlukan.
license: MIT
metadata:
  upstream: https://github.com/higgsfield-ai/skills
  cli_package: "@higgsfield/cli"
  upstream_license: MIT
  activation: contextual-creative-higgsfield
---

# Produksi Kreatif Higgsfield (`@higgsfield/cli` + `higgsfield-ai/skills`)

Gunakan skill ini (terutama pada peran **Kiki-Chii** maupun mode **Solo / Antigravity**) saat pengguna meminta pembuatan gambar AI, video AI, *faceless explainer*, *product photoshoot*, *marketplace cards*, *YouTube thumbnail*, *Soul ID*, *Brand Kit*, atau halaman visual melalui ekosistem **Higgsfield**.

## 0. Gerbang Wajib Koneksi Akun Saat Kreasi Konten Diperlukan (*Mandatory Auth Gate*)

- **Jika tugas TIDAK membutuhkan generasi aset kreatif Higgsfield** (misalnya hanya diskusi konsep, naskah teks, atau pengeditan lokal): **jangan** memaksa pengguna login ke Higgsfield.
- **Jika tugas MEMBUTUHKAN kreasi konten visual/video melalui Higgsfield**:
  1. Periksa ketersediaan CLI dan status autentikasi lokal terlebih dahulu tanpa membocorkan token ke output chat:
     - Pastikan `higgsfield --version` tersedia (jika belum terpasang dan pengguna mengizinkan setup CLI: `npm i -g @higgsfield/cli` serta companion skills `npx skills add higgsfield-ai/skills`).
     - Periksa apakah sesi login lokal sudah aktif (misalnya memeriksa status akun/kredit `higgsfield account status` tanpa mencetak isi `higgsfield auth token`).
  2. **WAJIB Sambungkan Akun Bila Belum Login**: Apabila CLI melaporkan belum terautentikasi / token belum ada, **hentikan sementara langkah generasi** dan minta pengguna menyambungkan akunnya terlebih dahulu dengan menjalankan:
     ```bash
     higgsfield auth login
     ```
     Tunggu hingga pengguna menyelesaikan proses *sign-in* OAuth 2.0 PKCE di browser yang terbuka sebelum menjalankan perintah `higgsfield generate create ...` atau workflow berbayar.
  3. Periksa sisa kredit (`higgsfield account status`) dan konfirmasi estimasi pemakaian kredit kepada pengguna sebelum mengeksekusi generasi berbayar.

## 1. Alur Produksi Kreatif (*Concepting First*)

1. **Sepakati Konsep & Brief**: Kunci pesan utama, audiens, rasio aspek, durasi/jumlah variasi, gaya visual, referensi berizin, dan batas kredit/anggaran. Untuk proyek multi-aset besar, tampilkan terlebih dahulu peta rencana melalui `cindy-grand-plan`.
2. **Pilih Modul Companion Skill yang Tepat**:
   - `higgsfield-generate` — generasi gambar & klip video sinematik dari prompt/gambar referensi (`higgsfield model list`, `higgsfield generate create`).
   - `higgsfield-soul-id` — konsistensi karakter/identitas visual lintas adegan.
   - `higgsfield-brandkit` — palet, tipografi, dan pedoman identitas brand.
   - `higgsfield-product-photoshoot` & `higgsfield-marketplace-cards` — foto produk studio & kartu e-commerce siap tayang.
   - `higgsfield-faceless-video` & `higgsfield-video-explainer` — video narasi/explainer terstruktur dari naskah ke adegan.
   - `higgsfield-youtube-thumbnail` & `higgsfield-websites` — sampul klik-tinggi & tata letak halaman web visual.
3. **Pratinjau, Evaluasi & Serah Terima**: Tampilkan hasil pratinjau untuk dinilai pengguna sebelum render lanjutan atau ekspor akhir, lalu serahkan file aset, parameter prompt/model yang dipakai, dan berkas proyek yang dapat diedit.

Rujukan hulu: [`higgsfield-ai/skills`](https://github.com/higgsfield-ai/skills) (MIT License) dan paket resmi `@higgsfield/cli`. Wrapper MSSHI ini menjaga model/provider utama pilihan pengguna di Hermes tetap utuh.
