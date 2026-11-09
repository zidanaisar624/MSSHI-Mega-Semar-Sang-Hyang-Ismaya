# CLI MSSHI

Gunakan Python 3.10 atau lebih baru. Python 3.12 disarankan. Jika nama perintah berbeda, ganti `python` dengan `python3` di macOS/Linux atau `py -3` di Windows, sesuai instalasi Anda. Jalankan contoh dari root paket.

```sh
python --version
python scripts/check_release.py
```

Pemeriksaan standar memvalidasi struktur paket. Gunakan `python scripts/check_release.py --smoke` untuk ikut menguji alur CLI dengan data contoh lokal.

## Memperbarui skill yang sudah dipasang

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
| `select` | Pilih satu atau beberapa slug skill terpasang setelah `--skills`, dipisah spasi. |

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

Contoh bridge mencetak rute tanpa membuka aplikasi. Tambahkan `--open` saat memang akan membuka target. Halaman web memakai browser sistem dan sesi akun pengguna. Target desktop memerlukan aplikasi terpasang dan terdeteksi.
