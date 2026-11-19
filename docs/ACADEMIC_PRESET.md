# Academic Preset — Mahasiswa & Dosen (v3.1.2)

Academic adalah pilihan tambahan pada versi yang sama, berdampingan dengan MuZA. Instalasi baru memakai **Academic Mahasiswa** sebagai pilihan awal; pengguna dapat memilih Academic Dosen/Pimpinan Kampus, MuZA, Solo, atau mode lain. Pembaruan pengguna lama tidak boleh mengubah preset, persona, model, akun, atau susunan bot tanpa pilihan eksplisit dan cadangan.

| Pilihan | ID | Fokus |
| --- | --- | --- |
| Academic Mahasiswa (pilihan awal instalasi baru) | `academic-mahasiswa` | Mahasiswa Indonesia S1–S3: tugas, kerkom, bimbingan, skripsi/tesis/disertasi, revisi, dan sidang. |
| Academic Dosen & Pimpinan Kampus | `academic-dosen` | Mengajar, RPS/modul, pembimbingan, penelitian, rapat, dan tindak lanjut kampus. |
| MuZA | `muza-preset` | Susunan lintas akademik, kreatif/film, bisnis, dan pengembangan perangkat lunak yang sudah ada. |

Keduanya termasuk keluarga **ACADEMIC PRESET (Mahasiswa & Dosen)** (`academic-mahasiswa-dosen`). Untuk perintah tanpa pertanyaan gunakan ID subpreset yang spesifik di atas. Nama preset tidak menetapkan nama pengguna: bot menanyakan sapaan pilihan dan mempertahankan ejaannya.

## Lima peran dan kerja sama

| Bot | Mahasiswa | Dosen/Pimpinan kampus |
| --- | --- | --- |
| Yukino | Ide, target kecil, jadwal, kesiapan kerkom/bimbingan | Agenda, ideasi, kesiapan rapat, notulensi dan tindak lanjut |
| Sensei Shizuka | Penjelasan materi, prioritas revisi, latihan ujian/sidang | RPS, modul, kasus, rubrik, koordinasi pembimbingan dan strategi riset |
| Val | Literatur, metode, analisis, bukti, dokumen dan sitasi | Sintesis riset S1–S3, publikasi, evaluasi argumen, respons reviewer |
| Kiki-Chii | Slide sidang, poster, diagram, konten edukasi | Slide mengajar/konferensi, infografis, visual komunikasi penelitian |
| Sir. Robot (`shikaku`) | Kode tugas akhir, data, Colab/web dan debugging | Kode riset, praktikum, reproduksi, data dan automasi teknis |

Yukino merapikan kebutuhan; Shizuka mengoordinasikan bila perlu; spesialis mengembalikan hasil, sumber, batas, dan pertanyaan keputusan. Tugas kecil tidak memerlukan semua bot. Host tanpa delegasi menggunakan brief atau peran bergantian dengan batas yang dijelaskan. Hasil perlu dipahami dan ditinjau pengguna; kelulusan tetap mengikuti proses kampus serta pembimbing.

## Isi paket dan batasnya

- SOUL publik memberi gambaran besar, tidak memuat identitas pribadi, pengaturan model/provider, API key, atau akses akun pembuat.
- `configs/academic_presets.json` memetakan instruksi dari 67 skill bundel yang sudah ada ke kedua subpreset; tidak menambah salinan runtime berat.
- `configs/academic_app_policy.json` memprioritaskan dokumen, tabel, slide, Python, dan browser yang dipilih pengguna. Route adalah izin sesuai tugas, bukan bukti aplikasi terpasang atau jaminan layanan gratis.
- Aplikasi tidak dibuka saat boot. CAD/3D/OBS/alat keamanan tidak menjadi route default; jika diperlukan, periksa instalasi, kebutuhan, izin, dan kemampuan perangkat terlebih dahulu. RAM rendah tetap memerlukan batas ukuran data/aplikasi yang realistis; preset tidak menjamin semua pekerjaan muat di RAM 4 GB.
- MuZA_Search v1.1, Skripsi Builder, `muza-skripsi-template`, ekspor DOCX, dan RIS digunakan bila alat/bahan tersedia. Pedoman kampus serta sumber/metadata sitasi harus diperiksa; jangan menjanjikan dokumen siap diterima tanpa review.
- NotebookLM, Zotero, layanan jurnal, kalender, WhatsApp/LMS dan sumber lain memerlukan koneksi atau berkas dari pengguna. Tidak ada OAuth atau akun pribadi yang ikut dibagikan.
- OmniVoice, generator gambar/suara, render berat, dan plugin meeting tetap pilihan terpisah; tidak otomatis memanggil layanan berbayar.

## Template biasa, tanpa Obsidian otomatis

Installer menyalin template kosong ke `workspace/academic` di dalam lokasi data Hermes yang terdeteksi (misalnya `%LOCALAPPDATA%\HermesData\workspace\academic` atau `D:\HermesData\workspace\academic`). Memori dan hasil tetap memakai ruang kerja native Hermes; folder proyek/vault eksternal tidak dibuat. Subfolder di dalam workspace dapat dipilih lewat `--academic-project`. **Preset publik tidak membuat atau menghubungkan vault Obsidian, tidak memindai folder pribadi, dan tidak memasang penguncian PowerShell.** Akses folder pribadi tetap tidak diberikan otomatis kepada bot mana pun, termasuk Yukino. Kebijakan atau koneksi Obsidian milik pembuat tidak ikut dalam preset publik.

Isi [`templates/academic/`](../templates/academic/):

1. `00_PROFIL_AKADEMIK_PENGGUNA.md` — sapaan, jenjang/peran, pedoman, target dan batas akses; kosong untuk diisi pengguna.
2. `01_STATUS_RISET_DAN_AKTIVITAS.md` — sedang fokus apa, yang sudah selesai, dan target berikutnya.
3. `01_Template_Kerkom_Bimbingan_dan_Rapat_Kampus.md` — kesiapan 30 detik, rundown, keputusan, dan pembagian tugas/disposisi.
4. `02_Template_Zoom_Kelas_dan_Perkuliahan.md` — tujuan belajar, rundown, latihan, catatan, dan draf rangkuman.
5. `03_Template_Target_Harian_Skripsi_Tesis_Disertasi.md` — target kecil harian, brain dump yang dibagikan pengguna, bukti, dan langkah berikutnya.

Penyalinan ulang tidak boleh menimpa isi profil/status yang telah diisi. Template bisa digunakan sebagai Markdown biasa tanpa aplikasi catatan tambahan.

## Persiapan dan evaluasi pertemuan

`prep-for-meetings` membantu menyiapkan kartu kesiapan 30 detik, rundown, serta notulensi/tindak lanjut berdasarkan catatan atau rekaman yang diberikan dan diizinkan. Bot menjelaskan dokumen/aplikasi yang akan dipakai; perekaman, transkripsi, pengiriman pesan dan pembagian materi memerlukan otorisasi yang sesuai.

Nama plugin berikut adalah **opsi terpisah; status pemasangan/kompatibilitas harus diperiksa pada host**: `meeting-copilot-live` (pendamping sesi langsung), `transcribo` (transkripsi), dan `solverforge-planner` (perencanaan tugas). Keberadaan nama dalam manifest bukan pemasangan. Periksa sumber resmi, kompatibilitas versi host, izin audio/rekaman, akun dan biaya sebelum pemasangan. Alur manual tetap dapat dipakai dari catatan yang diberikan pengguna.

## Contoh permintaan

> Aku mahasiswa S1, baru punya ide, dan bimbingan minggu depan. Bantu pilih masalah yang cukup kecil, buat target hari ini, dan siapkan brief untuk dosen. Jangan jalankan layanan berbayar.

> Aku dosen yang akan mengajar 90 menit. Bantu buat tujuan belajar, rundown, slide yang dapat diedit, dan latihan dari materi yang kuberikan.

> Tolong rapikan revisi tesis sesuai komentar pembimbing. Val periksa sumber, Sir. Robot bantu analisis yang diperlukan, lalu Shizuka jelaskan perubahan yang harus kutinjau.

## Jumlah instruksi awal

| Subpreset | Yukino | Shizuka | Val | Kiki-Chii | Sir. Robot |
| --- | ---: | ---: | ---: | ---: | ---: |
| Mahasiswa | 13 | 13 | 19 | 12 | 13 |
| Dosen | 13 | 14 | 21 | 12 | 13 |

Ini jumlah slug yang dipilih manifest sebelum tambahan fondasi yang diberlakukan host/installer, bukan jumlah tool aktif, proses, atau panggilan model. Audit hasil pemasangan melaporkan jumlah akhir yang benar-benar tersedia.

## Perintah pemasangan dan pemeriksaan

```powershell
msshi setup --mode academic-mahasiswa --platform hermes
msshi setup --mode academic-dosen --platform hermes
msshi setup --mode muza-preset --platform hermes
msshi connect --status
```

Menu tanpa mode menawarkan Mahasiswa sebagai pilihan awal hanya untuk pemasangan baru. Instalasi yang sudah mempunyai penanda preset dipertahankan; memilih Academic tidak dijalankan pada laptop pembuat secara otomatis. `--yes` melewati pertanyaan tanpa membuka browser atau memasang layanan akun.

Untuk satu aplikasi berat yang memang diperlukan dan sudah terpasang, pilih ID-nya secara eksplisit, contohnya `msshi connect --profile kiki-chii --mode select --targets blender`. Deteksi executable wajib berhasil; pilihan grup/auto-reconnect tidak mengaktifkan aplikasi berat. Rute tetap membutuhkan tiket tugas sekali pakai untuk menjalankan aplikasi, tidak membuka aplikasi ketika didaftarkan. Pemisahan peran ini bukan isolasi keamanan sistem operasi.

## Batas plugin meeting yang diperiksa

- **SolverForge Planner**: mesin jadwal lokal untuk Windows x64 telah diperiksa. Ia membuat usulan penempatan tugas; pengguna meninjau sebelum menerapkan. Plugin tidak dipasang otomatis dan tidak menghubungkan kalender cloud. [Sumber terpin](https://github.com/blackopsrepl/hermes-solverforge-planner/tree/c2ae4f2ad893501aa644c5f70b8fb6df65d0495d).
- **Meeting Copilot Live**: capture native Windows masih diblokir pada revisi yang diperiksa; jangan menganggapnya siap merekam Zoom. Jalur Meetily memerlukan perangkat lunak/sesi tersendiri. [Batas Windows](https://github.com/adam4788/meeting-copilot/blob/175f23d8a79d2423ed4493f068676442a2631929/docs/windows-setup.md).
- **Transcribo**: layanan transkripsi hosted dengan OAuth; unggahan audio dan transkripsi dapat memakai saldo layanan. Pemasangan, login, rekaman dan unggahan bukan bagian setup default. [Sumber](https://github.com/santigamo/transcribo-skill/tree/15328a4).

Kartu kesiapan dan rundown dapat dibuat sebelum rapat. Notulensi akhir hanya disusun dari catatan/transkrip yang benar-benar diberikan; bagian yang belum terjadi tetap berupa template kosong. Tidak ada janji kelulusan, data penelitian, kuota API, atau hasil demo yang dikarang. Materi WhatsApp/LMS disiapkan sebagai draf untuk ditinjau, bukan dikirim otomatis.
