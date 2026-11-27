---
name: cindy-grand-plan
description: Tampilkan Peta Perencanaan Besar interaktif (tujuan, tahapan, pembagian lintas-bot Yukino/Shizuka/Val/Kiki-Chii/Shikaku, skill & alat aktif, serta titik cek) khusus saat pengguna meminta perencanaan besar atau proyek multi-tahap agar pengguna dapat mengoreksi rencana sendiri sebelum eksekusi berat dijalankan.
license: MIT
metadata:
  upstream: https://github.com/makecindy/cindy
  upstream_license: Apache-2.0
  activation: contextual-grand-plan-preview
---

# Gerbang Perencanaan Besar Interaktif (`cindy-grand-plan`)

Diadaptasi secara orisinal dari pola *Decision Gate*, *Interactive Plan Review*, dan *Orca Multi-Agent Orchestration* pada [`makecindy/cindy`](https://github.com/makecindy/cindy) (Apache-2.0) untuk seluruh bot pada seluruh preset **MSSHI (`muza-preset`, `academic-mahasiswa`, `academic-dosen`, `solo`, `light`, `custom-bots`, dan `antigravity`)**.

## 1. Pemicu Kontekstual Ketat (Hanya untuk Perencanaan Besar)

- **JANGAN AKTIFKAN** pada sapaan harian, tanya-jawab singkat, penjelasan satu konsep, perbaikan bug kecil satu berkas, atau perintah mikro yang sudah jelas (*Tier 0 Fast Chat* tetap dijawab langsung tanpa hambatan).
- **AKTIFKAN OTOMATIS** ketika konteks menunjukkan pengguna meminta atau membutuhkan **Perencanaan Besar (*Grand Plan*)**, antara lain:
  1. Pengguna secara eksplisit meminta rencana besar, *roadmap*, arsitektur menyeluruh, strategi multi-bab/skripsi penuh, kampanye konten multi-tahap, atau *master plan*.
  2. Permintaan membutuhkan koordinasi **lintas beberapa bot** (`Yukino` -> `Shizuka` -> `Val` / `Kiki-Chii` / `Shikaku`), beberapatahap berurutan, atau kombinasi riset + produksi kreatif + rekayasa kode.
  3. Pekerjaan melibatkan langkah berbiaya/eksternal (generasi gambar/video `Higgsfield`, model 3D `Meshy`, render film panjang, atau perubahan besar lintas modul) yang wajib disepakati arahnya lebih dulu.

## 2. Format Kartu Peta Perencanaan Besar (Untuk Dikoreksi Pengguna)

Sebelum menjalankan eksekusi berat, panggilan Dewan/Advisor berbiaya, atau delegasi lintas-bot, tampilkan **Peta Perencanaan Besar** yang ringkas, jernih, dan mudah dikoreksi pengguna sendiri:

1. **Tujuan Akhir & Kriteria Selesai**
   - Rumusan hasil konkret yang akan diterima pengguna beserta ukuran selesainya.
2. **Alur Eksekusi Tahap demi Tahap & Pembagian Antar-Bot**
   - Jabarkan urutan tahap secara eksplisit beserta peran yang menangani setiap tahap (sesuai preset aktif):
     - **Yukino (`Tipe 1`)**: penjernihan ide mentah, prioritas waktu/energi, dan brief awal.
     - **Shizuka (`Tipe 1`)**: orkestrasi strategi lintas-bot, sintesis temuan, dan pendampingan belajar/sidang.
     - **Val (`Tipe 2`)**: riset mendalam, verifikasi literatur/DOI, statistik, dan dossier bukti S1–S3.
     - **Kiki-Chii (`Tipe 2`)**: *Concepting First*, desain visual, slide, video/motion, `Higgsfield`, atau aset 3D (`Blender MCP` / `Meshy` / `RAEA`).
     - **Shikaku / Sir. Robot (`Tipe 2`)**: arsitektur sistem, implementasi kode, akselerasi *hot-path* Rust bila relevan, audit keamanan berizin, dan verifikasi tes (`ast-grep`, `knip`, `open-code-review`).
   - Pada mode **Solo / Satu Asisten**, tampilkan tahapan yang sama sebagai perspektif kerja berurutan dalam satu asisten.
   - Pada mode **Light (RAM rendah)**, nyatakan bahwa tahapan dijalankan berurutan satu per satu tanpa proses paralel.
3. **Pemetaan Skill, Alat & Prasyarat Koneksi per Tahap**
   - Sebutkan skill MSSHI yang akan dipakai di tiap tahap, rute `CLI-Anything` / aplikasi lokal, serta **gerbang koneksi akun** bila diperlukan (misalnya wajib login `higgsfield auth login` untuk kreasi visual Higgsfield, atau `meshy auth login --device` untuk aset 3D Meshy).
4. **Asumsi, Batas Sumber Daya & Titik Cek (*Checkpoints*)**
   - Pisahkan fakta yang sudah diketahui dari asumsi sementara, perkiraan beban/biaya, dan di tahap mana pengguna akan meninjau hasil antara.
5. **Pertanyaan Koreksi Mandiri kepada Pengguna**
   - Akhiri kartu rencana dengan ajakan koreksi langsung yang ringkas:
     > *"Berikut rencana besar bagaimana tugasmu akan dijalankan lintas tahap/bot. Bagian mana yang ingin kamu ubah, tambah, atau kurangi lebih dulu? Jika sudah pas, balas **Lanjut** (atau pilih **Tahap 1 dulu**) untuk mulai mengeksekusi."*

## 3. Penyatuan dengan Sistem Interaksi Native MSSHI (`msshi-interaction`)

- Saat pengguna mengoreksi rencana, perbarui **hanya** bagian rencana yang diubah tanpa mengulang interogasi dari awal, lalu catat ruang lingkup dan *Initial Plan* yang telah dikoreksi pengguna ke `msshi_interaction_begin` (jika plugin native `msshi-interaction` tersedia di host).
- Untuk tugas **Tipe 1 (`Yukino`, `Shizuka`)**, lanjutkan ke telaah *Advisor* bila diperlukan lalu eksekusi/delegasi.
- Untuk tugas **Tipe 2 (`Val`, `Kiki-Chii`, `Shikaku`)**, gunakan rencana besar yang telah dikoreksi pengguna sebagai dasar *Initial Plan* sebelum memasuki Putaran 1 Dewan -> Audit Main -> Putaran 2 Dewan -> *Final Centralized Blueprint*.
- Persetujuan pengguna atas Peta Perencanaan Besar mengesahkan urutan kerja proyek, namun tindakan eksternal berisiko (pembayaran baru di luar batas, publikasi publik, pengiriman pesan keluar, atau penghapusan permanen) tetap mematuhi gerbang izin spesifiknya.

Inspirasi arsitektur upstream: `makecindy/cindy` berlisensi **Apache-2.0** (`LICENSE.upstream`). Teks skill dan penyatuan lintas-bot MSSHI ini merupakan karya orisinal berlisensi **MIT**.
