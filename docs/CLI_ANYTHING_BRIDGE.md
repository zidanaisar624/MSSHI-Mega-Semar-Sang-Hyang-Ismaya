# CLI-Anything Universal Bridge

MSSHI v2.1 menyimpan rute aplikasi per profil Hermes. Bridge mendeteksi konektor yang dideklarasikan dan aplikasi atau harness yang tersedia. Hermes tetap menangani koneksi serta tool MCP. Harness CLI-Anything dijalankan sebagai proses lokal setelah dipilih untuk tugas.

## Pilih cara koneksi

```powershell
msshi connect
msshi connect --mode auto-reconnect --dry-run
msshi connect --mode auto-reconnect
msshi connect --catalog
msshi connect --mode select --targets gdrive-web,youtube-chrome
msshi connect --mode select --targets artcraft,blender,ffmpeg
msshi connect --add perplexity
msshi connect --remove perplexity
msshi connect --status
msshi connect --status --json
```

- **Auto-Reconnect** mendaftarkan rute dari konektor terdeteksi dan aplikasi yang tersedia untuk profil tersebut. Pakai `--dry-run` untuk melihat rencana terlebih dahulu.
- **Pilih satu-satu** menampilkan daftar interaktif. Berikan ID dengan `--targets` bila pilihannya sudah diketahui.
- **Tambah, lepas, dan cek status** mengelola rute MSSHI secara individual. Melepas rute MSSHI mempertahankan konfigurasi konektor asli di Hermes.

Gunakan kelompok `existing` untuk memilih konektor yang sudah dideklarasikan. Konektor lain yang ditemukan muncul sebagai `mcp:<slug>`.

Jika ada beberapa profil, tambahkan `--hermes-home` dan `--profile` secara eksplisit. Contoh berikut membaca profil Kiki-Chii tanpa menjalankan aplikasi.

```powershell
msshi connect --status --hermes-home 'D:\HermesData' --profile kiki-chii
```

Dari salinan repo yang sudah diekstrak, ganti `msshi connect` dengan `python scripts/setup_cli_anything_hermes.py`. Dari chat Hermes, minta agen menggunakan skill `cli-anything-universal-bridge` dan sebutkan profil atau aplikasi yang diinginkan. Skill juga membawa skrip mandiri saat CLI global belum tersedia.

## Rute dan kebutuhan

| Target | Jalur |
| --- | --- |
| `gdrive-web` | Google Drive di browser dengan akun Google pengguna. |
| `perplexity` | Desktop bila terdeteksi, RAM tersedia minimal 2,2 GiB, dan penggunaan RAM maksimal 80%. Jika syarat gagal atau RAM tidak terbaca, pakai web. Kueri yang disertakan lewat `--query` dibuka di web. |
| `youtube-chrome` | YouTube di Chrome. |
| `tiktok` | Aplikasi TikTok yang terdeteksi atau web. |
| `antigravity` | Antigravity IDE jika terdeteksi di perangkat. |
| `artcraft` | Kelompok 15 rute FilmCraft, EffectCraft, PhotoCraft, LightCraft, SoundCraft, DesignCraft, VectorCraft, FigCraft, WordCraft, GridCraft, DeckCraft, PDFCraft, CADCraft, SolidCraft, dan CraftAnything. Pilih satu atau satu kelompok melalui menu. |
| `blender`, `blender-cli`, `ffmpeg` | Gunakan Blender MCP yang dideklarasikan oleh Hermes, harness Blender yang sudah terpasang, atau FFmpeg lokal sesuai jenis tugas. |
| `cli-hub`, `libreoffice`, `gimp`, `audacity`, `obs` | Pilih harness yang sudah dipasang, misalnya GIMP, LibreOffice, Audacity, atau OBS. Cari yang sesuai di katalog upstream. |

Status `configured` berarti deklarasi MCP ditemukan pada profil. Jalankan tool native Hermes pada tugas yang sesuai untuk memeriksa koneksi sesungguhnya. Buka target web atau desktop dengan `msshi connect --open TARGET`. Jalankan harness CLI yang terpasang dengan `msshi connect --run TARGET -- ARGUMEN`. Tinjau argumen dan biaya sebelum menerapkannya.

`auto_open_on_boot: false` berlaku tetap pada bridge. Pemasangan, pemindaian, pratinjau, dan daftar status mencatat rute atau memeriksa status tanpa membuka aplikasi. Daftar rute disimpan di `msshi-bridge/connections.json` pada profil yang dipilih. Bridge mempertahankan konfigurasi provider, model, dan kredensial. Akun, sesi browser, runtime, serta otorisasi MCP mengikuti aplikasi masing-masing.

Untuk harness tambahan yang sudah ada di PATH, tambahkan `msshi connect --add cli:SLUG` dan panggil `msshi connect --run cli:SLUG -- --help`. ID `cli:SLUG` mencari executable `cli-anything-SLUG`. Tinjau paket dan petunjuk upstream sebelum memasangnya. CLI-Hub menyediakan `cli-hub search`, `cli-hub info`, dan `cli-hub install` untuk penelusuran dan instalasi pilihan. [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) · [CLI-Hub](https://clianything.cc/).
