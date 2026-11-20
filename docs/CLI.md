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

`msshi choices` dan `msshi optional list` hanya membaca bantuan, tanpa login, unduhan, aplikasi atau kredit LLM. Menu KAT membuka wizard endpoint/key khusus Coder; aktivasi memerlukan key, ID model terverifikasi dan native routing. Dev dan StreamLake Pro berbeda; bobot tidak diunduh. REA hanya ditambahkan bila dipilih secara eksplisit, dengan runtime terpisah. Menu `msshi connect` menjelaskan fungsi aplikasi dan bahwa registrasi tidak sama dengan koneksi/autentikasi yang sudah teruji. Opsi yang dilewati dapat ditambahkan nanti.

## Alur Wizard 4 Tahap di `msshi setup`

Setelah memilih mode dan menyalin skill target, preset Hermes membuat lima profil native bernama `yukino`, `shizuka`, `val`, `kiki-chii`, `shikaku`; Hermes default tetap netral. `--default-bot keep-hermes` juga memperbaiki label default lama yang duplikat, tanpa menimpa SOUL/model. Plugin lokal memakai native named-profile delegation dan prompt koordinasi; mulai chat baru setelah gateway di-restart. Setup kemudian memandu 4 langkah lanjutan (flag tersedia dari `install.ps1` / `install.sh`):

1. **`[1/4] Skills`**: Menambah paket (`--extra-packs`) atau skill individu (`--extra-skills`) ke target/bot tertentu, serta opt-in REA (`--with-rea`, default OFF).
2. **`[2/4] Plugin`**: Memeriksa dan men-stage plugin fail-open `msshi-auto-trim` (`--stage-auto-trim`), wizard endpoint/key `KAT-Coder` opsional khusus Shikaku (`--kat-mode`; tidak mengubah model utama), konsolidasi memori offline `Hermes-Dreaming`, status `OmniVoice`, dan opt-in `Steel Browser Policy` (`--install-steel`).
3. **`[3/4] Koneksi`**: Memasang konektor MCP `GitLab` / `Tinyfish` (`--connect-services skip|per-profile|share-oauth`, tetap menjaga `BrightData` OFF dan aman bila `config.yaml` Hermes belum dibuat).
4. **`[4/4] Bot ke CLI-Anything ke Apps`**: Memetakan bot Hermes ke aplikasi lokal/web terdeteksi (`--connect-apps skip|auto-reconnect|select`, `--connect-bots`, `--connect-targets`) dengan mode semua bot, bot pilihan, atau mapping manual per bot (`auto_open_on_boot: false`).

Ringkasan setiap setup disimpan ke `<MSSHI_HOME>/reports/last-setup-report.json` tanpa mengubah `provider` atau `model` pengguna.


## v3.1.1: profil native, KAT, sumber kontekstual, dan PDF

Lihat [catatan perbaikan](V3_1_1_REPAIR.md), [KAT Coder](CODER_KAT.md), dan [integrasi kontekstual](CONTEXTUAL_INTEGRATIONS.md). Perintah `msshi coder --home ROOT wizard` mengatur endpoint/key privat; `status` membaca kesiapan lokal. `msshi integrations source --home ROOT --name NAME` membaca status; `--fetch` mengambil source terpin di luar scanner; runtime tetap eksplisit.

PDF terbaru otomatis disalin saat bootstrap/setup/update/direct apply ke Downloads/MSSHI_Manuals. `--pdf-dest` atau `MSSHI_PDF_DIR` memilih tujuan lain; `--no-pdf` / `MSSHI_NO_PDF=1` melewati penyalinan. Windows memakai `-PdfDest` / `-NoPdf`. Berkas yang berbeda dicadangkan sebelum penggantian.

`msshi runtime rebaseline --home ROOT` hanya preview; penerapan memerlukan `--apply --expected-snapshot SHA` dan, bila bukti historis tidak cocok, `--accept-current-llm-settings --reason "alasan"`. Ini menerima baseline sekarang dengan catatan, bukan mengklaim riwayat yang tidak terbukti.

## Light Build & Mode Low-RAM (Windows 10 RAM 4 GB)

Untuk perangkat Windows 10 spesifikasi rendah (RAM 4 GB, single-drive `C:`-only, Windows PowerShell 5.1), MSSHI menyediakan mode **Light Build** (`<= 50 MB`) dan profil **Low-RAM** tanpa menyentuh pilihan model, API key, atau `SOUL.md` pengguna. Lihat panduan lengkapnya di [WIN10_4GB_LIGHT_BUILD.md](WIN10_4GB_LIGHT_BUILD.md).

```powershell
# Instalasi interaktif (tanyakan Mode Standar vs Mode Hemat Win10 RAM 4 GB + lokasi drive/folder bebas C:/D:/E:/...)
.\install.ps1

# Instalasi ringan + Low-RAM ke drive/folder pilihan (PowerShell 5.1)
.\install.ps1 -Light -LowRam -InstallDir "E:\MSSHI" -HermesHome "E:\HermesData" -Mode academic-mahasiswa -Platform hermes -Yes

# Subperintah msshi light & fallback CLI
msshi light status --json
msshi light mode --set auto --apply --json
msshi light index --json
msshi light build --output .\dist\msshi-light.zip --json
msshi light benchmark --iterations 25 --json
msshi desktop --prefer-cli
```

- `install.ps1` (`-InstallDir`, `-HermesHome`, `-TargetDir`) dan `install.sh` (`--install-dir`, `--hermes-home`, `--target-dir`) mendukung direktori tujuan di drive atau folder mana saja (`C:\`, `D:\`, `E:\`, SSD eksternal, maupun folder kustom).
- `msshi setup` interaktif kini menampilkan tahap `[5/5] Mode Resource Perangkat` sehingga pengguna dapat langsung memilih Mode Standar atau Mode Hemat Windows 10 RAM 4 GB saat instalasi.
- `msshi setup --low-ram` atau `--resource-profile auto|light|normal` menyimpan profil resource secara atomik dengan rollback receipt ke `<HERMES_HOME>/msshi-runtime/resource-profile.json`.
- `msshi update --light` men-stage rilis ringan tanpa menyalin aset berat, PDF panduan otomatis, atau cache upstream.
- `msshi doctor --json` menampilkan blok `low_ram_diagnostics` (RAM fisik, ruang kosong drive target, memori proses, ukuran cache, dan uji cepat skill scan `p95`).

## Sistem Interaksi Cerdas 4 Pilar (`msshi system`)

Untuk menyatukan seluruh repositori, skill, plugin (`MSSHITrim`, `msshi-interaction`, `msshi-team-routing`), `Hermes-Dreaming`, **Google Research Harness²**, dan **TimesFM 2.5** menjadi sistem tertutup yang hemat token, makin pintar, serta kuat untuk riset dan prediksi (0 panggilan LLM, 0 request jaringan), gunakan `msshi system`. Lihat arsitektur lengkapnya di [SISTEM_INTERAKSI_CERDAS_MSSHI.md](SISTEM_INTERAKSI_CERDAS_MSSHI.md).

```powershell
msshi system status --json
msshi system route --task "Prediksi tren 12 bulan dengan backtesting"
msshi system cycle --domain prediction --goal "Bandingkan TimesFM 2.5 vs seasonal-naive"
```
