# CLI MSSHI

Gunakan Python 3.10 atau lebih baru. Python 3.12 disarankan. Jika nama perintah berbeda, ganti `python` dengan `python3` di macOS/Linux atau `py -3` di Windows, sesuai instalasi Anda. Jalankan contoh dari root paket.

```sh
python --version
python scripts/check_release.py
```

Pemeriksaan standar memvalidasi struktur paket. Gunakan `python scripts/check_release.py --smoke` untuk ikut menguji alur CLI dengan data contoh lokal.

## Perintah global untuk akun pengguna

Pasang lewat [Quick Start](../README.md#-quick-start-30-detik-pilih-agen-anda) atau jalankan dari salinan kandidat v3 yang sudah diperiksa. Perintah berbasis URL GitHub mengambil versi yang sudah dipublikasikan, sedangkan `-SourcePath .` memakai paket lokal.

```powershell
.\install.ps1 -SourcePath .
```

```sh
bash install.sh --source-dir .
```

Installer menyiapkan perintah `msshi` di PATH akun. Buka terminal baru jika perubahan belum terbaca. Opsi instalasi `-NoSetup` (PowerShell) atau `--no-setup` (Bash) melewati wizard interaktif. Bootstrap tetap dapat memigrasikan profil Hermes yang terdeteksi; opsi ini bukan mode read-only. Opsi `-NoPath` atau `--no-path` menyediakan launcher tanpa memperbarui PATH. Sebagai alternatif, jalankan `npm install --global .` dari root repo, lalu `msshi setup`. Pembungkus npm tetap membutuhkan Python 3.10+.

| Perintah | Cara kerja |
| --- | --- |
| `msshi setup` | Pilih mode Solo, Custom Multi-Bot, Selective Packs, atau Preset MuZA. Tinjau target dan file sebelum menerapkan. |
| `msshi check` / `msshi status` | Bandingkan versi paket aktif dengan `VERSION.json` dari GitHub `main`, tampilkan changelog, dan ringkas rute aplikasi. |
| `msshi update` | Ambil `main` dari GitHub, lalu segarkan skill terkelola yang masih cocok dengan versi pemasangan. Gunakan setup atau select untuk menambah skill baru. Simpan cadangan SOUL dan Creative DNA yang ditemukan. Jalankan migrasi profil v3 yang tersedia, lalu segarkan cache 49 sumber dan integrasi terpilih. Provider/model utama serta skill yang dikustomisasi dijaga oleh pemeriksaan dan cadangan. |
| `msshi update --skip-upstreams` | Perbarui rilis, skill terkelola, dan migrasi profil tanpa mengambil sumber eksternal. |
| `msshi connect` | Baca menu dan status rute aplikasi. Pada profil v3, eksekusi memakai `msshi runtime ticket` dan `msshi runtime run`. |
| `msshi select` | Pilih paket atau slug dengan angka/nama dan tinjau rencana. Gunakan `msshi select --local` untuk memakai versi yang sudah ada di perangkat. |

Status versi paket dapat berbeda dari versi skill tertentu setelah pembaruan selektif atau ketika file hasil kustomisasi dipertahankan. Pemasangan melalui marketplace atau Skills CLI dikelola melalui host tersebut. Dalam CLI MSSHI, `msshi select` juga dapat menambahkan skill atau paket baru ke target yang dipilih. Satu target dapat dipilih secara eksplisit dengan `--platform` dan `--target-dir`.

Cache dan metadata biasanya berada di `%LOCALAPPDATA%\MSSHI` di Windows atau `$XDG_DATA_HOME/msshi` di macOS/Linux (default `~/.local/share/msshi`). `MSSHI_HOME` memilih lokasi lain. Cadangan file profil dicatat di `backups/` dengan petunjuk lokasi asli. Cadangan skill berada di luar direktori yang dipindai host, dan CLI mencetak lokasi tersebut saat update. Simpan cadangan secara privat.

### Pengambilan upstream

`msshi update` mencoba 46 repositori Git, dua kartu model, dan satu situs katalog sesuai manifest 49 sumber. Git menyimpan snapshot ringan tanpa checkout dan mencatat SHA. Baca file pilihan dengan `git -C <lokasi-snapshot> show HEAD:<path>`; Git akan mengambil isi yang belum tersedia di cache bila diperlukan. Lihat `upstreams/last-fetch.json` untuk sumber yang berhasil dan yang perlu dicoba ulang. Jika ada sumber gagal, perintah mengembalikan status 1 dan mempertahankan pembaruan yang sudah berhasil. Tahap fetch cache sendiri tidak memasang runtime, menyalin skill ke profil, menjalankan skrip upstream, atau mengunduh bobot OCR. Jalur global `msshi update` v3 juga memanggil installer integrasi terpilih setelah fetch; pemasangan tersebut memiliki receipt terpisah dan dapat menyalin skill terpilih ke profil. Model, akun, dan layanan tetap memerlukan prasyaratnya.

Skrip langsung berikut juga mendukung fetch. Berikan folder cache yang terpisah dan gunakan `--apply` setelah meninjau rencana.

```sh
python scripts/install_msshi.py --platform hermes --mode solo --pull-upstreams --apply
python scripts/msshi_update.py --mode auto --source ./rilis-baru --baseline ./rilis-lama --skills-dir ./msshi-skills --pull-upstreams --apply
```

### Windows untuk Hermes dan Antigravity

Untuk migrasi v3, baca [panduan migrasi](V3_MIGRATION.md), lalu gunakan `msshi runtime migrate --home PATH_HERMES` pada home yang telah diperiksa. Rute aplikasi desktop dan utilitas Hersona/Llmtrim menggunakan CLI; eksekusi aplikasi memerlukan tiket. GDrive pada setup MuZA tetap dinonaktifkan. `scripts/installers/Install_Overhaul_Hermes_dan_Antigravity.ps1` merupakan jalur installer lama; tinjau scope dan opsinya sebelum dipakai pada pemasangan yang belum dimigrasikan.

Pengguna CLI v2.1 atau kandidat lama menjalankan installer/BAT dari paket v3 yang telah diperiksa sekali agar jalur migrasi baru tersedia. Setelah itu gunakan `msshi update`. Validasi menolak sumber dengan versi lebih rendah daripada versi lokal.

## Hubungkan aplikasi

Jalankan `msshi connect` untuk membuka menu Auto-Reconnect atau memilih target. Untuk audit ringan, gunakan `msshi connect --status`. [Pilihan lengkap, profil, dan cara membuka aplikasi](CLI_ANYTHING_BRIDGE.md).

## Memperbarui skill dari folder rilis lokal

`msshi-update` bekerja dengan folder rilis lokal. Siapkan folder **rilis baru** yang telah Anda tinjau, folder **rilis lama** yang dahulu dipasang sebagai baseline, serta **folder skill tujuan** dari installer atau host. Folder tujuan harus sudah ada dan terpisah dari folder `skills/` dalam kedua rilis.

```sh
python scripts/msshi_update.py --mode check --source ./rilis-baru --baseline ./rilis-lama --skills-dir ./msshi-skills
python scripts/msshi_update.py --mode auto --source ./rilis-baru --baseline ./rilis-lama --skills-dir ./msshi-skills
python scripts/msshi_update.py --mode select --source ./rilis-baru --baseline ./rilis-lama --skills-dir ./msshi-skills --skills literature-review
```

| Mode | Perilaku |
| --- | --- |
| `check` | Baca versi dan bandingkan hash file skill terpasang dengan rilis sumber. |
| `auto` | Pilih skill yang sudah terpasang dan cocok dengan baseline. |
| `select` | Pilih satu atau beberapa slug setelah `--skills`, dipisah spasi. Skill yang belum ada dapat ditambahkan dengan `--apply`. |

Setelah memeriksa hasil pratinjau, ulangi `auto` atau `select` dengan `--apply`. Perintah menyimpan cadangan di folder tersembunyi `.msshi-backup-*` yang sejajar dengan folder skill tujuan. Folder ini berada di luar folder yang dipindai host. Misalnya, jika tujuan `./msshi-skills`, cadangan berada di `./.msshi-backup-*/`. Jika skill berbeda dari baseline, gabungkan perubahan Anda secara manual, atau tinjau isi lalu gunakan `--replace-custom` untuk menggantinya dengan versi rilis. Tanpa baseline, skill yang berbeda menunggu tinjauan atau pilihan penggantian tersebut. Untuk pemulihan, hentikan agen yang memakai skill. Gunakan path cadangan yang dicetak updater. Pindahkan folder skill versi baru ke lokasi terpisah, lalu salin `<folder-cadangan>/<slug-skill>` kembali ke `<folder-skill-tujuan>/<slug-skill>`. Untuk tim, jalankan per workspace dengan `--skills-dir ./my-msshi-team/ID-BOT/skills`.

Jika sudah menerapkan contoh instalasi lokal dari panduan publik, periksa hasilnya menggunakan rilis yang sama. Perintah berikut seharusnya melaporkan `current` untuk skill yang sama dengan salinan di paket.

```sh
python scripts/msshi_update.py --mode check --source . --skills-dir ./msshi-demo-skills
```

Di Windows, `.\scripts\msshi-update.cmd` memakai `python` dari PATH. Di macOS/Linux, `sh scripts/msshi-update` memakai `python3`. Gunakan perintah Python langsung jika launcher berbeda.

## Cek biaya dan pratinjau bridge

```sh
python skills/persona-shizuka-yukino-shikaku/scripts/cli_anything_sovereign_hub.py --json token-audit --balance-usd 1.25 --estimated-cost-usd 0.15
python skills/persona-shizuka-yukino-shikaku/scripts/cli_anything_sovereign_hub.py --json bridge --target youtube-chrome --query "audio editing"
```

Gunakan saldo dan estimasi biaya yang sudah diperiksa. Contoh TokenShield di atas memproyeksikan saldo USD 1,10 dan mengembalikan exit 0. Cadangan minimal USD 1,00. Jika masukan belum lengkap atau proyeksi di bawah cadangan, perintah mengembalikan exit 2. Cek ulang sebelum menjalankan operasi berbayar karena status tagihan tetap berasal dari provider.

Contoh bridge lama di atas hanya untuk pratinjau. Pada profil v3, gunakan dispatcher `msshi runtime ticket` dan `msshi runtime run` untuk eksekusi. Jangan memakai helper lama sebagai jalan pintas melewati tiket. Untuk browsing, ikuti [kebijakan Steel dan persetujuan akun](STEEL_BROWSER_POLICY.md); penilai rute tidak mengaktifkan Steel atau memindahkan login secara otomatis.

## Utilitas lokal dan penghematan otomatis v3

Hersona memakai CLI untuk katalog dan draf persona saat tugas memerlukannya. Persona native Hermes dan `SOUL.md` tetap aktif tanpa pemanggilan katalog pada setiap balasan. Lihat [Hersona CLI](HERSONA_CLI.md).

Plugin native [msshi-auto-trim](../hermes_plugins/msshi-auto-trim/README.md) memanggil Llmtrim otomatis pada hook `transform_tool_result` untuk hasil alat JSON valid yang cukup besar. Hasil diterima hanya bila data JSON tetap sama; bila kompresi gagal, hasil asli dipertahankan. Percakapan, kode, file, konfigurasi, persona, dan error dilewati. Ini tidak membuat proxy seluruh chat atau menjamin penghematan setiap giliran.

```powershell
msshi trim --status --profile default
```

Ganti `default` dengan ID profil bot yang diperiksa. Status membaca penghitung agregat tanpa chat atau panggilan model. Pemrosesan file khusus tersedia sebagai opsi terpisah, `msshi trim --input request.json --output request-ringkas.json`.

## Tambahan v3.1

`msshi brag doctor` memeriksa alur video; `msshi scrapling status` memeriksa parser; `msshi harness2 status` memeriksa demo harness. Subperintah setup/pemakaian ada pada [panduan v3.1](V3_1_UPDATE.md). Unslop adalah skill instruksi UI sesuai konteks dan tidak membutuhkan server/CLI baru.

## Penjelasan langsung saat memilih

`msshi setup` dan `msshi select` menampilkan fungsi setiap mode, paket, dan skill di samping ID-nya. Nama alternatif ditandai sebagai alias; instruksi bawaan dibedakan dari referensi eksternal. Skill fondasi wajib tetap disertakan. `--lang en` mengganti bahasa penjelasan, bukan ID/format jawaban. Daftar seluruh fungsi: [Panduan pilihan](OPTION_GUIDE.md) / [English](OPTION_GUIDE_EN.md).

```sh
msshi choices rea
msshi choices kat
msshi choices --kind skills
msshi choices --kind apps --lang en
msshi setup --lang en
msshi select --local --lang en
msshi optional list
```

`msshi choices` dan `msshi optional list` hanya membaca bantuan, tanpa login, unduhan, aplikasi atau kredit LLM. Menu KAT menjelaskan bahwa pilihannya baru menyimpan preferensi; ia belum memasang/mengaktifkan model. REA hanya ditambahkan bila dipilih secara eksplisit, dengan runtime terpisah. Menu `msshi connect` menjelaskan fungsi aplikasi dan bahwa registrasi tidak sama dengan koneksi/autentikasi yang sudah teruji. Opsi yang dilewati dapat ditambahkan nanti.
