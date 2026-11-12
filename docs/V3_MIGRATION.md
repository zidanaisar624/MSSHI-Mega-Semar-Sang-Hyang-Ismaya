# Migrasi MSSHI v3.0

MSSHI menyediakan instruksi skill, migrasi profil, dan dispatcher aplikasi lokal. Agen memilih skill berdasarkan tugas. Dispatcher menjalankan aplikasi hanya dengan tiket tugas yang masih berlaku dan merekam hasilnya di folder runtime pengguna.

## Mulai

Pengguna yang sudah memakai CLI v3 dapat menjalankan `msshi update`. Perintah ini mengambil rilis baru, menyimpan cadangan, memperbarui skill terkelola, dan menjalankan migrasi profil Hermes yang terdeteksi.

Pengguna CLI v2.1 perlu menjalankan installer dari paket v3 sekali agar kode migrasi v3 terpasang. Updater v2.1 belum memiliki pemanggilan migrasi setelah pembaruan. Klik `UPDATE_OTOMATIS_KE_V3.bat` dari ZIP v3 untuk melakukannya dengan satu langkah. Setelah itu gunakan `msshi update`.

`MULAI_DI_SINI_PEMULA.bat` membuka pilihan setup, migrasi profil, Desktop, dan audit. Mode preset menawarkan nama tampilan kustom sambil mempertahankan ID peran dan pembagian skill.

## Perintah

| Tujuan | Perintah |
| --- | --- |
| Migrasi Hermes aktif | `msshi runtime migrate` |
| Status runtime | `msshi runtime status` |
| Pemulihan Desktop Windows | `msshi desktop` |
| Audit nyata | `msshi audit` |
| Instal sumber integrasi | `msshi integrations install` |
| Konsolidasi lokal | `msshi dream --run-now` |
| Status suara lokal | `msshi voice --status` |
| Pilihan subagen opsional | `msshi kat --help` |

Gunakan `--help` pada subperintah untuk memilih folder Hermes. Cadangan dan laporan migrasi disimpan di folder Hermes milik pengguna. Laporan audit menyebutkan kemampuan yang siap, yang perlu runtime, dan yang gagal.

## Aplikasi dan memori

Migrasi menghapus registrasi MCP aplikasi desktop dan memindahkan utilitas lokal Hersona/llmtrim dari MCP stdio ke CLI. GitLab dan Tinyfish dipertahankan sebagai MCP yang mengakses layanan web. [Hersona CLI](HERSONA_CLI.md) menyediakan pratinjau katalog, blend, dan ekspor melalui tiket tugas persona; hasilnya tidak otomatis mengganti persona native Hermes atau SOUL.md. [Plugin Llmtrim otomatis](../hermes_plugins/msshi-auto-trim/README.md) menjalankan compress pada hasil tool JSON valid yang cukup besar melalui hook transform_tool_result. Hasil diterima hanya jika data JSON persis sama, dan kegagalan memakai hasil asli. Percakapan, kode, file, konfigurasi, persona, dan error dilewati. Penghitung tersedia melalui msshi trim --status --profile default. Perintah file msshi trim --input request.json --output request-ringkas.json tetap opsional. Tidak ada proxy seluruh chat atau perubahan provider/model utama. Perintah status, pencarian skill, dan deteksi aplikasi membaca metadata. Pemanggilan aplikasi membutuhkan tiket tugas. Aplikasi yang belum memiliki CLI terverifikasi dilaporkan sebagai belum tersedia.

MSSHI memakai tier hardware sebagai batas awal. Pengukuran memori bebas saat menjalankan tugas tetap diperlukan. Jumlah skill aktif dan ukuran model tidak membuktikan bahwa suatu komputer mampu menjalankan seluruh runtime sekaligus.

Pengaman proses membatasi penghentian otomatis pada proses yang dapat dibuktikan dimulai oleh MSSHI. PID, waktu mulai, dan jalur executable diperiksa untuk melindungi pekerjaan pengguna yang sudah terbuka. Temuan anomali lain menghasilkan peringatan dan bahan pemeriksaan.

Pemeriksaan saldo US$1 bergantung pada saldo aktual serta estimasi yang diberikan. Batas biaya keras memerlukan dukungan provider. Deteksi pola secret lokal membantu menemukan kandidat kebocoran. Pemeriksaan ini perlu peninjauan manusia untuk memastikan konteks dan risiko.

## Voice, Dreaming, dan KAT

OmniVoice perlu plugin yang kompatibel, dependensi, bobot model, dan uji suara lokal. Pengaturan persona saja belum membuktikan suara dapat dihasilkan. Status suara mencatat prasyarat yang ditemukan dan hasil pemeriksaan runtime.

Dreaming tanpa panggilan model menghasilkan usulan lokal yang sudah disaring dari pola rahasia. Memori asli dipertahankan. Perubahan pengetahuan yang membutuhkan interpretasi harus ditinjau. Jadwal lokal Windows mengikuti zona waktu mesin, yang diperiksa ketika tugas didaftarkan.

KAT-Coder adalah pilihan subagen yang terpisah dari model utama. Mode lokal membutuhkan file model dan runtime yang sesuai. Angka ukuran kuantisasi pada panduan merupakan perkiraan, sehingga pemasangan memverifikasi ketersediaan serta ruang perangkat. Mode cloud membutuhkan endpoint dan izin biaya pengguna.

## Hak dan kredit

MuZA mengarahkan arsitektur dan kebutuhan proyek. Google Gemini, OpenAI ChatGPT, dan Google Antigravity tercatat sebagai alat kolaborasi dalam pengembangan. Lisensi setiap sumber mengikuti revisi yang digunakan. Lihat [pemberitahuan pihak ketiga](../THIRD_PARTY_NOTICES.md).
