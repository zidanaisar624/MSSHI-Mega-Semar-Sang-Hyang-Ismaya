# Lima lapis konteks untuk proyek panjang

Alur ini menyimpan dokumen di proyek dan mengambil bagian yang dibutuhkan untuk pertanyaan saat ini. Lima lapis dapat dijalankan dengan alat lokal yang tersedia. Rujukan Graphify, Unlimited-OCR-2, Jev, dan pemantau penggunaan memerlukan setup terpisah sesuai host.

| Lapis | Kerja utama | Keluaran dan jalur pengganti |
| --- | --- | --- |
| 1. Peta lokal | Daftarkan dokumen, modul kode, versi, serta relasi antarbagian. Gunakan Graphify bila tersedia. | Indeks path atau peta struktur. Gunakan pencarian teks lokal dan metadata file bila graph tidak tersedia. |
| 2. Ekstraksi berhalaman | Ambil teks langsung dari PDF. OCR hanya bagian yang perlu, dalam batch sesuai perangkat. Catat bahasa, nomor halaman, dan mutu hasil. | Potongan yang memuat ID dokumen, versi, halaman, serta teks yang diperiksa. Jika hasil lemah, tandai dan baca halaman sumber. |
| 3. Pilih dan padatkan | Cari dengan istilah, sumber, dan fokus pertanyaan. Pilih bagian yang beragam, lalu ringkas dengan penunjuk sumber. Jev hanya membantu seleksi bila dipasang; `jev_model_routing` tetap `false`. | Paket konteks dengan batas ukuran, petikan bukti, dan daftar potongan yang tersisih. Gunakan pencarian manual jika adapter tidak ada. |
| 4. Memori proyek | Simpan fakta yang disepakati, keputusan, dan pertanyaan yang masih terbuka. Tautkan setiap catatan ke sumber dan versi. | `MEMORY.md`, `USER.md`, atau `session_graph.json` privat atas persetujuan pengguna. Tandai keputusan usang dan hapus ketika pengguna memintanya. |
| 5. Prefix dan anggaran | Letakkan instruksi stabil di awal dan bukti berubah di bagian tugas. Ukur token aktual dan status cache bila host menampilkan keduanya. | Catatan konteks yang dipakai dan biaya aktual. Jika data saldo tidak tersedia, tunda otomatisasi berbayar dan minta nilai yang telah diperiksa. |

Format penunjuk yang disarankan: `dokumen-v2#p12:par3`. Untuk kode, gunakan path, versi, serta baris atau simbol. Setiap ringkasan sebaiknya bisa dikembalikan ke sumber asli. Jika panjang konteks masih melebihi kapasitas, pecah pertanyaan, simpan bukti tiap subhasil, dan gabungkan sintesis setelahnya. Biaya, mutu OCR, dan keuntungan cache bergantung pada perangkat, provider, serta penggunaan aktual.

**Contoh.** Untuk membandingkan dua definisi dari sepuluh PDF, daftarkan berkas, ambil teks dari halaman yang relevan, ambil dua petikan yang dapat dibandingkan, catat keputusan istilah di memori proyek, lalu kirim dua petikan dan pertanyaan perbandingan. Cek kedua nomor halaman pada berkas asli sebelum mengutip.

Lihat [alur akademik](TUJUH_MESIN_AKADEMIK.md) dan [matriks rujukan](../configs/bot_role_and_skill_matrix.json).

