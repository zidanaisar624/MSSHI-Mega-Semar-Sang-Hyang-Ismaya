---
name: cli-anything-universal-bridge
description: Detect and register Hermes application routes, browse the CLI-Anything catalog, and open or run a registered target on demand. Use when the user asks to connect, reconnect, inspect, or use an app.
---

# CLI-Anything Universal Bridge

Gunakan terminal di perangkat atau profil Hermes yang benar. Bridge menyimpan pilihan rute per profil dan membaca nama konektor dari konfigurasi Hermes. Periksa akses ke terminal, aplikasi, akun, dan file yang dibutuhkan.

## Pilih cara koneksi

Tanyakan mode saat pengguna meminta menghubungkan aplikasi tanpa pilihan spesifik.

1. **Auto-Reconnect Semua.** Pratinjau aplikasi yang terdeteksi dan konektor yang tercantum pada profil dengan `msshi connect --mode auto-reconnect --dry-run`. Tampilkan daftar dan statusnya. Jika pengguna memilih rencana ini, jalankan perintah yang sama tanpa `--dry-run`.
2. **Pilih Connect Satu-Satu.** Jalankan `msshi connect --catalog` dan tawarkan rute yang relevan. Setelah pengguna memilih, jalankan `msshi connect --mode select --targets TARGET1,TARGET2`. Pilih profil yang sama pada setiap langkah.
3. **Kelola satu target.** Gunakan `msshi connect --add TARGET`, `msshi connect --remove TARGET`, atau `msshi connect --status` sesuai permintaan.

Jika perintah global belum tersedia, panggil `python scripts/setup_cli_anything_hermes.py` dari direktori skill ini dengan argumen koneksi yang sama. Gunakan `--hermes-home PATH` bila profil aktif ambigu. Periksa `--help` untuk pilihan lain. Jangan mengambil token, URL privat, atau isi konfigurasi mentah ke chat.

## Jalankan saat dibutuhkan

- **Browser atau aplikasi desktop.** Pakai `msshi connect --open TARGET` hanya ketika pengguna meminta alat dibuka. Google Drive memakai versi web. Perplexity memilih rute sesuai RAM dan ketersediaan aplikasi saat dibuka. YouTube membutuhkan Chrome untuk rute Chrome.
- **Harness CLI.** Pakai `msshi connect --run TARGET -- ARGUMEN` dengan argumen yang telah ditinjau. Gunakan harness yang terpasang dan cocok dengan aplikasi. Untuk menemukan harness, lihat [CLI-Hub](https://clianything.cc/) atau [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything).
- **MCP Hermes.** Untuk rute ArtCraft atau Blender, periksa daftar tool profil dan gunakan tool MCP Hermes yang sesuai. Status terdaftar menunjukkan konfigurasi ditemukan. Cek kesehatan atau kesiapan melalui Hermes sebelum mengklaim operasi berhasil.

Pertahankan `auto_open_on_boot: false`. Koneksi hanya mendaftarkan rute. Buka atau jalankan alat sesuai tugas dan izin pengguna. Periksa biaya serta izin pengiriman sebelum operasi berbayar atau mengirim data ke layanan luar. Pertahankan pilihan provider dan model.
