# Alur preset lima bot MuZA

Preset ini menyediakan persona dan rute kerja. Pada host yang mendukung beberapa agen, Shizuka dapat menyerahkan tugas sesuai izin yang berlaku. Pada mode solo, satu agen berganti peran secara berurutan dengan kontrak serah terima yang sama. Di mode tim khusus, nama dan pembagian peran dapat diubah di [matriks bot](../configs/bot_role_and_skill_matrix.json).

| Kebutuhan | Pemilik langkah | Hasil yang diteruskan |
| --- | --- | --- |
| Ide masih mentah | Yukino | Tujuan, alternatif, pertanyaan, langkah pertama → Shizuka |
| Riset, data, dan literatur | Val | Dossier bukti, batas kepastian, serta sumber → Shizuka |
| Produksi kreatif | Kiki-Chii | Brief, rencana produksi, dan aset → Shizuka |
| Kode dan keamanan | Shikaku | Rencana, perubahan, hasil verifikasi, dan risiko → Shizuka |
| Strategi dan penjelasan akhir | Shizuka | Sintesis, keputusan, dan pekerjaan tersisa → pengguna |

## Langkah pelaksanaan

1. Yukino merangkum ide awal dan menanyakan hasil yang ingin dicapai. Permintaan matang dapat langsung masuk ke Shizuka.
2. Shizuka menetapkan batas tugas, hasil yang diharapkan, dan siapa yang mengerjakan. Untuk permintaan campuran, pecah menurut keluaran dan gunakan rujukan bukti yang sama.
3. Bot spesialis memuat skill bundel yang relevan, lalu memeriksa apakah integrasi eksternal yang diperlukan tersedia dan diizinkan.
4. Spesialis menyerahkan tujuan, sumber berizin, temuan, ketidakpastian, hasil kerja, dan langkah berikut. Shizuka membawa bukti Val ke penjelasan yang mudah dipahami pengguna.
5. Jika ada tugas yang belum bisa dikerjakan, sebutkan dependensi atau izin yang kurang, lalu tawarkan jalur manual yang sesuai.

Contoh serah terima:

```json
{
  "from": "val",
  "to": "shizuka",
  "task": "Bandingkan dua metode pengukuran pada data latihan",
  "status": "partial",
  "claims": [
    {"text": "Hasil belum dapat dibandingkan langsung", "evidence": ["metode.md#batas-pengukuran"], "confidence": "provisional"}
  ],
  "artifacts": ["hasil/metode.md"],
  "open_questions": ["Apakah variabel kontrol pada data latihan tersedia?"],
  "approval_scope": "Baca sumber contoh dan tulis ringkasan lokal"
}
```

Gunakan penunjuk file relatif atau kutipan sumber yang diizinkan. Nama file contoh bersifat ilustratif. Pastikan penerima memiliki akses sebelum membagikan materi. Untuk penggunaan berbayar, jalankan preflight TokenShield dengan saldo dan estimasi biaya aktual. Pengaturan model dan provider tetap berada pada host.

## Concepting First dan Creative DNA

Sebelum membuka alat produksi, Kiki-Chii merangkum audiens, pesan, rasa visual, shot, suara, tenggat, anggaran, dan keluaran. Setelah brief disepakati, ia memilih kombinasi kamera nyata, penyuntingan lokal, modul Higgsfield, empat rujukan motion graphics, adapter ArtCraft yang tersedia, dan Blender sesuai kebutuhan. Untuk proyek web kreatif, Kiki-Chii memegang arah visual dan Shikaku memegang implementasi serta verifikasi.

Salin [templat Creative DNA](../configs/user_creative_dna.json) ke lokasi privat proyek, misalnya `curiosity_ledger/user_creative_dna.json`. Isi hanya preferensi yang ingin digunakan, ubah `example` menjadi `false`, dan aktifkan pembelajaran hanya jika dikehendaki. Setelah proyek, catat revisi yang disetujui beserta tanggal, preferensi, dan alasan. Gunakan rujukan lokal yang sah. Simpan contoh pelanggan, kredensial, dan proyek nyata di penyimpanan terpisah.

## Video berdurasi 10–40 menit

1. Susun outline bab dan anggaran durasi untuk pembuka, isi, transisi, serta penutup. Sepakati tujuan tiap bab sebelum produksi.
2. Siapkan naskah, shot list, aset, dan draf yang dapat diedit untuk setiap segmen. Gunakan penamaan konsisten agar segmen mudah digabungkan ke timeline master.
3. Bagikan preview per bab dan catat masukan dengan timecode. Setelah revisi, satukan rough cut dan periksa durasi total, kontinuitas visual, audio, serta subtitle.
4. Minta persetujuan pengguna sebelum ekspor final. Simpan timeline master yang bisa diedit, versi final, dan keputusan yang sudah disetujui.

## Keamanan dan integrasi

Aplikasi dipanggil sesuai tugas aktif. Rujukan eksternal dalam matriks memerlukan adapter, izin, serta pengaturan yang berlaku pada host. Untuk forensik darurat, persetujuan sebelumnya harus menyebut target lokal, jangka waktu, dan jenis pemeriksaan baca-saja. Alurnya peringatan → pemeriksaan dalam ruang lingkup → laporan. Perubahan, target eksternal, dan langkah di luar mandat memerlukan persetujuan tersendiri.

Lihat [audit skill per bot](AUDIT_SKILLS_PER_BOT.md), [tujuh mesin akademik](TUJUH_MESIN_AKADEMIK.md), dan [lima lapis konteks](LIMA_LAPIS_KONTEKS.md).

