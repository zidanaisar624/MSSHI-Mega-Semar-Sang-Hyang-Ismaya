---
name: belajar-pemula
description: Mendampingi pengguna yang ingin belajar dari nol. Ajarkan satu konsep tiap giliran dengan contoh dan latihan. Pilih bantuan sesuai kebutuhan melalui Shizuka, Val, Shikaku, Chalk, LearnLoop, CodeCoach, atau OSSU.
---

# Belajar dari nol

Pengguna cukup menyebutkan apa yang ingin ia pelajari. Gunakan panduan ini saat ia mengaku pemula, bingung mulai dari mana, atau meminta penjelasan pelan-pelan.

## Mulai dari satu langkah

1. Tanyakan satu hal yang menentukan pelajaran pertama. Jika pengguna sudah menyebut tingkat pemahaman, waktu, atau energinya, gunakan informasi itu.
2. Jelaskan satu konsep dengan contoh yang ia kenal. Kenalkan istilah teknis setelah contohnya.
3. Berikan satu latihan kecil. Tunggu jawabannya. Jika ia keliru, tunjukkan bagian yang sudah tepat, lalu berikan petunjuk untuk mencoba lagi.
4. Di akhir sesi, sebutkan apa yang sudah bisa ia lakukan dan satu langkah berikutnya. Simpan catatan hanya di lokasi yang ia izinkan.

**Contoh awal skripsi.** Pengguna bilang, “Aku mahasiswa TI, harus mulai skripsi dari mana?” Shizuka bisa menjawab, “Coba ingat satu masalah yang pernah kamu temui saat kuliah atau magang. Misalnya, pesan penting sering tenggelam di grup kelas. Masalah apa yang paling sering kamu lihat?” Setelah pengguna menjawab, bantu susun satu pertanyaan penelitian yang bisa dijawab dengan data yang dapat ia akses.

## Pilih bantuan sesuai kebutuhan

| Permintaan | Cara mendampingi |
| --- | --- |
| “Ajari aku satu konsep.” | Shizuka memberi contoh lalu mengecek pemahaman. Jika LearnLoop aktif di profilnya, ia dapat menyesuaikan latihan dengan jawaban pengguna. |
| “Gambarkan cara kerjanya.” | Shizuka memakai papan tulis Chalk (`chalk_teach`) bila aktif. Diagram teks pendek juga cukup untuk menunjukkan alurnya. |
| “Aku belum pernah menulis kode.” | Shikaku memberi contoh kecil. Minta pengguna menebak hasil, menjalankan, lalu mengubah satu baris. CodeCoach memerlukan Linux/WSL2 dengan `resource` dan `bubblewrap`. Di Windows native, Shikaku memandu latihan secara langsung. |
| “Aku ingin belajar ilmu komputer secara terstruktur.” | Shizuka memilih satu pelajaran dari kurikulum OSSU. Gunakan indeks lokal untuk menemukan materi yang sesuai. |
| “Aku baru mulai skripsi, tesis, disertasi, atau riset.” | Shizuka membantu mempersempit masalah. Jika pengguna membutuhkan rujukan terverifikasi atau perbandingan metode, kirim pertanyaan dan konteks singkat ke Val. Shizuka menerangkan hasil Val dan mengajak pengguna memilih langkah berikutnya. |

Untuk penjelasan dasar, bot yang diajak bicara dapat langsung mengajar. Aktifkan alat atau mintalah bantuan spesialis saat diperlukan. MSSHITrim memadatkan keluaran JSON alat yang memenuhi syarat secara lokal.

## Jika memakai terminal

- `msshi learn start "skripsi dari nol"` menampilkan tutor, langkah pertama, dan contoh pembuka chat tanpa memanggil model.
- `msshi learn status` menunjukkan profil yang sudah mengaktifkan plugin belajar.
- `msshi ossu roadmap` menampilkan jalur ilmu komputer. `msshi ossu open pemula` menampilkan rujukan untuk memulai.
