# Panduan Praktis Instalasi MSSHI v3.1.2

Edisi 19 November 2026. Untuk mahasiswa S1/S2/S3, dosen dan pengguna Windows.
Panduan ini tidak berisi model, provider, base URL/endpoint pribadi, API key,
akun atau data pemilik proyek.

## Halaman 1 - Mulai dari tujuan yang kecil

MSSHI menambahkan susunan bot, instruksi skill dan alat bantu ke agen seperti
Hermes. Hermes adalah aplikasi/host yang menjalankan model. MSSHI tidak
membagikan akses model gratis dan tidak menggantikan pemasangan Hermes.

Urutannya: siapkan Hermes dan alat dasar; pasang MSSHI; pilih preset; atur mesin
sendiri secara privat; periksa kesiapan; kerjakan satu tugas kecil.

| Yang diperlukan | Pemeriksaan awal |
| --- | --- |
| Hermes yang didukung | Aplikasi/CLI terpasang melalui jalur resmi |
| Python 3.10 atau lebih baru | `python --version` atau `py -3 --version` |
| Git | `git --version` |
| Internet dan ruang penyimpanan | Untuk mengambil source dan pilihan runtime |
| Akses model milik pengguna | Disiapkan sendiri; tidak disalin dari pembuat MSSHI |

Untuk RAM 4 GB, mulai dari Academic dan aplikasi dokumen ringan. Kebutuhan
Hermes, browser, OS dan aplikasi lain tetap diperhitungkan. Angka RAM ini bukan
jaminan semua fitur, model lokal atau render video akan muat.

Repositori resmi: [MSSHI di GitHub](https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya).

Jika Hermes belum terpasang, ikuti petunjuk resmi host dan dukungan Windows
yang tersedia. Jangan membuat dua home Hermes hanya untuk menyamai contoh.

## Halaman 2 - Pasang dari PowerShell

Buka PowerShell biasa pada akun yang akan memakai Hermes. Periksa Python dan
Git terlebih dahulu. Bila salah satunya belum tersedia, selesaikan pemasangan
program itu sebelum menjalankan MSSHI.

```powershell
python --version
git --version
```

Ambil pemasang dari repo resmi. URL dipisah agar mudah disalin dari PDF:

```powershell
$MsshiRaw = "https://raw.githubusercontent.com/"
$MsshiRepo = "zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya"
irm ($MsshiRaw + $MsshiRepo + "/main/install.ps1") | iex
```

Perintah ini mengunduh dan menjalankan pemasang dari `main`. Tinjau source jika
ingin memeriksanya lebih dahulu. Installer menyiapkan perintah `msshi` dan
menawarkan wizard; catat lokasi data serta receipt yang dicetak.

| Pilihan utama | Pilih bila |
| --- | --- |
| Academic Mahasiswa | Fokus tugas akhir S1/S2/S3; pilihan awal instalasi baru |
| Academic Dosen | Mengajar, membimbing, riset dan rapat kampus |
| MuZA | Memerlukan susunan lintas bidang kreatif, riset dan coding |
| Solo / Custom / Selective | Memerlukan satu agen, tim sendiri atau paket tertentu |

Instalasi yang sudah ada dipertahankan bila tidak memilih pergantian secara
eksplisit. Academic memakai workspace native Hermes; tidak memasang Obsidian
atau mengambil akun browser. Pilihan Chrome/Edge/Firefox hanya label untuk
login manual. Jika belum membutuhkan browser, pilih tidak memilih.

PDF lengkap disalin otomatis ke `Downloads/MSSHI_Manuals`, kecuali dilewati.
Jika `msshi` belum dikenali setelah selesai, buka terminal baru dan baca pesan
lokasi launcher; jangan langsung mengulang seluruh pemasangan.

## Halaman 3 - Atur akses sendiri, lalu buka bot

Tentukan sendiri model, provider dan alamat layanan pada pengaturan Hermes.
Masukkan API key melalui kolom rahasia/autentikasi yang sesuai. Jangan menaruh
key dalam chat grup, screenshot, PDF, SOUL, repo Git atau contoh perintah.
Membeli paket akses dari penjual tidak berarti akun pembuat ikut dipasang.

Periksa pilihan untuk setiap bot yang dipakai. Jangan menyalin `config.yaml`,
`.env`, riwayat atau koneksi orang lain menjadi pengaturan Anda. Model/provider
untuk penasihat dan Dewan juga dipilih sendiri; tidak ada paket mesin bawaan
yang diam-diam diterapkan oleh persona.

| Bot | Mulai dari |
| --- | --- |
| Yukino | Ide, jadwal, prioritas dan kesiapan pertemuan |
| Sensei Shizuka | Belajar, strategi, latihan sidang dan koordinasi |
| Val | Literatur, metode, data dan draf penelitian |
| Kiki-Chii | Slide, poster, konten dan video |
| Sir. Robot / Shikaku | Kode, debugging dan pengolahan data |

Buka Hermes Desktop seperti aplikasi biasa. Gunakan profil yang benar dan
sesi baru setelah reload yang diperlukan. Pada instalasi baru, default dapat
menjadi Yukino sesuai layout; pada tim lama, nama/pemetaan yang ada dijaga.

Yukino/Shizuka memakai Main dan Advisor untuk pekerjaan yang perlu telaah.
Val/Kiki/Coder memakai Main dan Dewan dua putaran dengan audit Main di tengah.
Pertanyaan singkat tetap dijawab Main. Bila Dewan belum dikonfigurasi, tampilkan
prasyarat, bukan mengarang hasil atau mengaktifkan model baru.

## Halaman 4 - Periksa dan perbaiki sesuai kebutuhan

Pemeriksaan lokal dilakukan sebelum mengirim pekerjaan model. Gunakan bantuan
versi yang benar; nama folder/profil dan lokasi pada setiap laptop bisa berbeda.

```powershell
msshi --help
msshi doctor --help
msshi doctor --json
msshi connect --status
msshi trim --status --profile default
```

Perintah bantuan/status tersebut tidak mengirim chat model. `msshi status` atau
`msshi check` berbeda: ia dapat memeriksa GitHub dan membutuhkan internet.
`default` adalah ID profil, bukan selalu nama tampilan; gunakan ID bot yang
benar ketika memeriksa profil bernama.

Setelah membaca diagnosis dan memilih pemulihan yang sesuai:

```powershell
msshi doctor --fix
```

`--fix` menulis hanya file hilang yang fingerprint kepemilikannya terbukti
milik MSSHI, lalu membuat receipt. Edit kustom, SOUL, konfigurasi, model,
provider, base URL/endpoint, key dan akun dipertahankan. Tidak mengunduh
dependency, menjalankan aplikasi atau memperbaiki semua masalah. Exit code
0 berarti sehat, 1 berarti error inti, 2 berarti peringatan yang perlu dibaca.

Baca masalah yang dilaporkan. Dependency yang belum ada dapat hanya diperlukan
oleh fitur tertentu. Status pending, login belum diuji dan model belum diatur
tidak diselesaikan dengan mengubah pilihan provider secara otomatis.

Simpan pesan error, waktu, versi dan path receipt. Jangan mengirim config mentah
atau key ketika meminta bantuan. Jika perubahan terjadi setelah cadangan,
pulihkan hanya transaksi yang cocok; jangan menghapus seluruh home atau chat.

## Halaman 5 - Minta bot yang sesuai melalui Bot Forge

Mulai dari rancangan bot pada percakapan dengan bot mana pun yang tersedia.
Jelaskan tugas, bahan, hasil, batas alat/biaya dan cara menilai keberhasilan.

> Rancang bot untuk membantu kegiatan saya. Tentukan mandat, skill minimum,
> tipe interaksi, input-output, izin, batas biaya dan cara mengujinya. Jangan
> membuat profil atau menyalin model, provider, endpoint, API key dan akun dulu.
> Tampilkan rancangan untuk saya pilih sebelum diterapkan.

Jika rancangan sudah disepakati, simpan JSON dengan bidang `id`, `name`,
`purpose`, `skills`, `gap` dan `reviews`. Catat hanya penilaian peran yang
benar-benar diterima. Gunakan ID baru yang belum ada atau pernah dihapus.

```powershell
msshi forge --roster
msshi forge --blueprint rancangan.json
msshi forge --blueprint rancangan.json --apply
```

Roster dan preview tidak membuat bot. `--apply` meminta konfirmasi sebelum
pembuatan profil native, SOUL, metadata dan skill yang dipilih. Pengguna
menyiapkan model/provider sendiri sesudahnya. Konsultasi model melalui chat
memiliki biaya tersendiri; perintah roster/preview tidak memanggil model.

Menyiapkan rancangan bukan bukti profil sudah dibuat. Jika memilih provisioning
native opsional, periksa dukungan host/OS, nama profil dan preview terlebih
dahulu. Jalur upstream yang belum diuji pada Windows harus diberi label tersebut
dan boleh diganti dengan handoff manual; jangan mengklaim sudah berhasil.

Pembuatan bot tidak memberikan izin menyalin `.env`, konfigurasi model/provider,
akun, riwayat atau data pribadi. Pengguna mengatur mesin sendiri untuk profil
baru. Tidak ada gateway, notifikasi, browser atau aplikasi kreatif yang boleh
dinyalakan hanya karena rancangan bot telah dibuat.

## Halaman 6 - Ritme ringan dan serah terima

Untuk RAM 4 GB, gunakan satu tugas kecil dahulu. Tutup aplikasi yang tidak
diperlukan. Jangan mengunduh bobot besar, menyalakan CAD/3D/OBS atau merender
video panjang untuk sekadar memeriksa instalasi. Rute aplikasi bekerja sesuai
tugas dan tiket, bukan saat boot.

MSSHITrim bekerja otomatis pada JSON tool yang memenuhi syarat bila plugin dan
binary siap. Ia tidak memadatkan seluruh chat, memasang proxy/sertifikat atau
menjamin persentase penghematan tagihan. Suara dan generasi media merupakan
pilihan terpisah. Pertemuan dimulai dari tujuan, rentang waktu, kartu kesiapan
dan rundown; notulensi hanya dari catatan/transkrip nyata.

| Sebelum serah terima | Bukti yang perlu dipahami |
| --- | --- |
| Versi dan lokasi diketahui | Perintah bantuan/status dapat dibuka pada home yang benar |
| Preset sesuai kebutuhan | Nama, peran dan sapaan bukan identitas pembuat |
| Pengaturan rahasia milik sendiri | Model/provider/endpoint/key diatur pengguna secara privat |
| Pemeriksaan dibaca | Bagian siap, pending dan belum diuji dibedakan |
| Batas penggunaan jelas | Runtime, akun, kuota dan biaya fitur tambahan diketahui |
| Panduan tersimpan | PDF lengkap dan lokasi receipt dapat ditemukan |

Ketika akses model sudah disiapkan dan Anda memilih memakai kredit, mulai
dengan satu pertanyaan kecil pada bot yang sesuai. Instalasi dan status lokal
tidak membuktikan chat berbayar atau Dewan telah teruji. Pertahankan proyek,
log dan keputusan yang berguna untuk bantuan berikutnya.

Jika pekerjaan akan diteruskan ke Antigravity, minta handoff berisi tujuan,
keputusan, struktur berkas, input-output, tes, kendala dan rollback. Kirim hanya
bahan yang Anda izinkan; kredensial dan pengaturan pribadi tetap terpisah.

Baseline source: `42cb1dd782e19d697fdf08a3207ba9fa619e0383`. Panduan publik tanpa pengaturan pribadi.
