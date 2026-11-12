---
name: cli-anything-universal-bridge
description: Detect local application routes and run an application for an active user task through a one-use MSSHI ticket. Use when connecting, inspecting, or using apps for creative, research, or coding work.
---

# CLI-Anything Universal Bridge

Gunakan terminal pada profil Hermes yang sedang bekerja. Tentukan ID profil sebelum membuat tiket. ID bawaan MuZA adalah default, shizuka-hiratsuka, val, kiki-chii, dan nyenyenye-ya-gw-coder. Nama tampilan kustom tetap memakai ID profil yang sama.

## Periksa kesiapan

Jalankan msshi runtime status dan msshi connect --status untuk melihat rute yang sudah dimigrasikan. Pemeriksaan status membaca metadata dan tidak menyalakan aplikasi. Gunakan --home pada runtime atau --hermes-home pada connect bila folder aktif ambigu.

Jika perintah global belum tersedia, panggil Python pada scripts/msshi_runtime.py atau scripts/setup_cli_anything_hermes.py dari direktori skill ini. Kedua skrip disertakan bersama skill.

## Jalankan tugas melalui tiket v3

Buat tiket hanya untuk permintaan pengguna yang sedang dikerjakan. Pengguna dapat menyebut aplikasi langsung atau menyerahkan pekerjaan yang membutuhkan aplikasi tersebut. Pilih sumber direct untuk perintah eksplisit dan context untuk keputusan alat berdasarkan tugas aktif.

Contoh pemeriksaan versi FFmpeg untuk Kiki-Chii menggunakan dua perintah berikut. Simpan ID yang dicetak perintah pertama sebagai TICKET_ID.

1. msshi runtime ticket --profile kiki-chii --target ffmpeg --task "Periksa versi FFmpeg untuk proyek video aktif" --source context --ttl 120
2. msshi runtime run --profile kiki-chii --ticket TICKET_ID ffmpeg -- -version

Tiket terikat pada satu profil, satu aplikasi, satu kali eksekusi, dan batas waktu. Tiket kedaluwarsa atau yang sudah dipakai akan ditolak. Gunakan tiket baru untuk perintah berikutnya. Tinjau argumen sebelum menjalankannya.

Dispatcher menyalakan executable CLI lokal dalam proses yang dikelola. Proses turunannya ditutup saat tugas selesai atau mencapai batas waktu. Aplikasi yang dibuka pengguna sendiri tetap di luar kepemilikan dispatcher. Hormati batas biaya, hak file, dan izin pengiriman data sebelum tindakan berbayar atau pengiriman ke layanan luar.

ArtCraft, LightCraft, dan Blender memakai rute native CLI yang terdaftar. Jangan menyalakan server MCP Desktop atau flag koneksi permanen sebagai jalan alternatif. Jika rute belum tersedia, laporkan prasyaratnya dan pilih alat yang sudah siap sesuai tugas pengguna.

## Koneksi lain

GitLab dan Tinyfish tetap menjadi konektor MCP layanan web. Hersona dan llmtrim adalah utilitas lokal yang telah dialihkan dari MCP stdio ke CLI. Gunakan route hersona hanya untuk tugas persona yang relevan dan pratinjau katalog, blend, atau ekspor; persona native Hermes dan SOUL.md tidak diganti otomatis.

Contoh Hersona memerlukan tiket baru pada setiap eksekusi. Jalankan msshi runtime ticket --target hersona --task "Tinjau atribut persona yang diminta", lalu msshi runtime run --ticket TICKET_ID hersona -- show personality/kuudere. Tentukan --profile secara eksplisit bila profil aktif ambigu.

Llmtrim berjalan otomatis melalui plugin native msshi-auto-trim pada hook transform_tool_result untuk hasil tool JSON valid yang cukup besar. Hasil dipakai hanya jika data JSON tetap persis sama. Jika kompresi gagal, pertahankan hasil asli. Percakapan, kode, file, konfigurasi, persona, dan error dilewati. Periksa penghitung dengan msshi trim --status --profile default dengan ID profil yang sedang diperiksa. Perintah msshi trim --input request.json --output request-ringkas.json adalah opsi pemrosesan file, bukan langkah wajib setiap chat. Tidak ada proxy chat menyeluruh atau perubahan provider/model utama.

Google Drive dinonaktifkan untuk setup pribadi MuZA. Periksa kebijakan runtime sebelum menawarkan rute web atau aplikasi Drive.

## Instalasi lama

Jika folder msshi-runtime/policy.json belum ada, jalankan migrasi v3 melalui installer yang tersedia sebelum memakai tiket. Jalur lama connect --open dan connect --run hanya dipertahankan untuk instalasi v2 yang belum dimigrasikan. Pada v3, semua pemanggilan aplikasi melalui bridge memerlukan tiket.

Pertahankan auto_open_on_boot false dan jev_model_routing false. Daftar rute menunjukkan executable yang terdeteksi. Laporkan keberhasilan pekerjaan setelah memeriksa keluarannya.

## Browsing policy for v3

Prefer Hermes-Steel through native Hermes browser tools after verifying the plugin and endpoint are ready. Read the public browser policy and use msshi browser for route assessment. Ask for task-specific approval before using a personal Chrome/other-browser session and require that account-specific need for any local-browser fallback. Account migration needs separate approval naming source, destination, account, data, and duration. Automatic login-data transfer is not implemented. Do not open a cloud session during boot or status checks.
