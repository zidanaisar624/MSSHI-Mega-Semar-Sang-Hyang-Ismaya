# Modul Pelanggan MSSHI v3.1.1

Edisi distribusi Senin, 16 November 2026 | Dasar implementasi 84ecd134f01ec65c4848b4f50c597b811f6b3a80 | Disusun 16 November 2026

# 1. Mulai di sini: bentuk produk dan cara membaca modul

MSSHI (Mega Semar Sang Hyang Ismaya) adalah kumpulan instruksi skill, kerangka persona/peran, dan alat CLI untuk mengelola pemasangan, pembaruan, serta penggunaan alat sesuai tugas. Agen seperti Hermes membaca instruksi tersebut untuk menentukan alur kerja. Aplikasi kreatif, runtime Python/Node, bobot model, dan akun layanan disiapkan menurut fitur yang dipakai.

Modul pelanggan ini menjelaskan **MSSHI 3.1.1**, berdasarkan source implementasi commit `84ecd134f01ec65c4848b4f50c597b811f6b3a80`. Edisi: **Senin, 16 November 2026 (Asia/Jakarta)**. Pembaruan mencakup lima profil native Hermes, koordinasi peran, pembagian aplikasi, wizard endpoint KAT khusus Coder, integrasi kontekstual, dan penyalinan PDF otomatis. Contoh merupakan petunjuk pemakaian; laporan pengujian pada perangkat tertentu disimpan terpisah. Kode dan bantuan versi terpasang menjadi acuan perilaku command.

Jika Hermes sudah disiapkan untuk Anda, mulai dari Bab 3 dan Praktikum 1; gunakan bot/profil yang diberikan saat serah terima. Bab instalasi ditujukan untuk pemasangan baru atau penyesuaian host. Semua path konkret seperti `C:\HermesClient` adalah contoh: sesuaikan dengan folder instalasi pada perangkat Anda.

## Hasil belajar

Setelah menggunakan modul, Anda dapat memilih jalur instalasi, mengenali fungsi fitur, meminta pekerjaan kepada bot yang sesuai, membaca dan menjalankan perintah yang relevan, membedakan status kesiapan, serta mencari penyebab kegagalan tanpa langsung menghabiskan kredit chat. Bab referensi memuat sintaks dan opsi CLI; latihan menunjukkan pemakaiannya pada pekerjaan kecil.

| Jalur baca | Bagian yang dibaca | Hasil yang dituju |
| --- | --- | --- |
| Baru mengenal MSSHI | Bab 1-4, lalu satu latihan | Dapat mulai tanpa memasang semua integrasi |
| Hermes sudah disiapkan | Bab 3-4, alur lima bot, operasional | Memakai instalasi yang ada tanpa mengulang setup |
| Mencari sebuah command | Referensi CLI dan indeks opsi | Menemukan sintaks, efek, dan prasyarat |
| Menambah skill/aplikasi | Pilihan fitur, CLI-Anything, runtime terkait | Menambah komponen yang memang diperlukan |
| Mengatasi error | Bab operasional dan tabel troubleshooting | Memeriksa bukti serta memulihkan lingkup yang tepat |

## Isi versi ini

| Komponen | Jumlah / fungsi |
| --- | --- |
| Skill standar | 67 folder instruksi: 51 inti dan 16 wrapper integrasi |
| Opsi terpisah | REA berada di `optional/rea`, default publik OFF |
| Referensi upstream | 52 sumber; pengambilan source terpisah dari pemasangan runtime |
| Nama pada katalog skill | 128 nama kanonis: 67 bawaan dan 61 referensi eksternal; banyak nama dapat berkaitan dengan sumber yang sama |
| Paket kategori | `core`, `filmmaking`, `business`, `thesis`, `webdev`, `cybersec` |
| Mode setup | Solo, Custom Multi-Bot, Selective Packs, Preset 5-Bot MuZA |
| Peran preset | Yukino, Shizuka, Val, Kiki-Chii, Shikaku |

Jumlah skill yang sudah ada pada komputer pengguna dapat lebih besar karena mencakup koleksi lama, integrasi tambahan, dan kustomisasi. Angka katalog, jumlah folder terpasang, jumlah repositori, dan jumlah tool bukan satu ukuran yang sama.

## Lima status yang perlu dibedakan

<!-- FIGURE: readiness -->

1. **Instruksi ditemukan:** agen/CLI dapat membaca `SKILL.md`.
2. **Rute terdaftar:** registri mengetahui cara mengakses suatu tool.
3. **Runtime tersedia:** executable/dependency yang diperlukan ditemukan.
4. **Akun dan izin siap:** layanan memerlukan login/key serta lingkup akses yang sesuai.
5. **Tugas terbukti berhasil:** input nyata atau fixture menghasilkan keluaran yang diperiksa.

Kolom `registered: true`, `available`, atau `configured` menjawab bagian tertentu dari rangkaian tersebut. Gunakan bukti eksekusi dan pemeriksaan hasil untuk memastikan tujuan tugas benar-benar tercapai.

## Istilah yang dipakai

| Istilah | Arti praktis |
| --- | --- |
| Skill | Instruksi untuk mengenali tugas dan menjalankan alur tertentu |
| Wrapper | Instruksi/adaptor kecil yang menghubungkan kemampuan MSSHI dengan alat lain |
| Runtime | Program dan dependency yang benar-benar menjalankan pekerjaan |
| Native CLI | Akses aplikasi melalui perintah lokal atau adaptor yang didukung |
| CLI-Anything bridge | Registri dan jalur tugas untuk memakai CLI/adaptor yang tersedia |
| MCP web | Konektor layanan web; GitLab dan Tinyfish tetap memakai jalur ini |
| Profil | Home/config/persona/skill milik bot tertentu |
| Tiket tugas | Otorisasi satu tugas dengan lingkup dan anggaran yang diterima runner |
| Receipt | Catatan perubahan, hasil uji, hash, atau cadangan untuk lingkup tertentu |
| Upstream cache | Source referensi eksternal di luar folder yang dipindai sebagai skill |

## Biaya dan efek perintah

| Jenis tindakan | Apa yang perlu diperhatikan |
| --- | --- |
| Membaca bantuan/katalog lokal | `--help`, `msshi choices`, dan `msshi optional list` tidak memanggil model |
| Memeriksa versi | `msshi check/status` membaca GitHub; membutuhkan internet |
| Setup/update/install | Dapat menulis file, registri, source cache, atau dependency sesuai opsi |
| Chat dengan agen | Model yang telah Anda pilih dapat memakai kredit/token provider |
| Render/analisis lokal | Menggunakan CPU/GPU, RAM, disk, waktu, dan kemungkinan lisensi aplikasi |
| Operasi layanan web | Dapat memakai kuota/kredit layanan, terpisah dari kredit LLM |
| Mengunduh runtime/model | Membutuhkan jaringan dan disk; bobot atau aset memiliki ketentuan masing-masing |

Tidak memakai kredit LLM tidak selalu berarti read-only, offline, tanpa proses baru, atau tanpa biaya layanan lain. Contohnya pemeriksaan Desktop tertentu dapat menyiapkan gateway; command install jelas menulis dependency. Referensi CLI menandai efeknya.

Contoh-contoh dalam modul adalah petunjuk untuk dikerjakan ketika diperlukan. Penyusunan modul ini tidak menjalankan render, model, chat berbayar, login akun, atau pekerjaan layanan baru.

# 2. Instalasi menurut perangkat dan agen

## Langkah awal

Siapkan Python 3.10 atau lebih baru untuk CLI utama; Python 3.12 merupakan pilihan praktis bagi beberapa runtime yang diuji. Git diperlukan untuk mengambil source dari GitHub. Node/npm diperlukan oleh integrasi tertentu dan jalur `npx`, bukan oleh semua fungsi dasar MSSHI. Baca syarat runtime masing-masing fitur sebelum mengunduhnya.

Untuk pengguna yang sudah memiliki instalasi, mulai dari `msshi choices rea` dan `msshi connect --status`. Jalankan update bila perintah bantuan baru belum tersedia. Anda tidak perlu membuat ulang lima bot hanya untuk memakai penjelasan menu yang baru.

```powershell
python --version
git --version
Get-Command msshi -ErrorAction SilentlyContinue
```

Perintah di atas memeriksa program, bukan menjalankan model. Jika nama Python di perangkat Anda berbeda, gunakan `py -3` di Windows atau `python3` di macOS/Linux.

## Windows PowerShell

Installer dari `main` dapat dipanggil dengan susunan berikut. URL dibagi menjadi variabel agar mudah disalin dari halaman PDF:

```powershell
$MsshiRaw = "https://raw.githubusercontent.com/"
$MsshiRepoPath = "zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya"
irm ($MsshiRaw + $MsshiRepoPath + "/main/install.ps1") | iex
```

Perintah tersebut mengunduh dan menjalankan installer dari `main`. Untuk memeriksa source terlebih dahulu, gunakan checkout lokal:

```powershell
$MsshiRepoUrl = "https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya.git"
git clone $MsshiRepoUrl
Set-Location "MSSHI-Mega-Semar-Sang-Hyang-Ismaya"
python scripts/check_release.py
.\install.ps1 -SourcePath .
```

Installer global menyiapkan launcher pada PATH akun pengguna dan menawarkan wizard ketika terminal interaktif. Pada instalasi Hermes yang terdeteksi, bootstrap v3 juga dapat menjalankan migrasi profil. Opsi `-NoSetup` melewati wizard, sementara langkah bootstrap/migrasi yang berlaku tetap dapat berjalan. Periksa lingkup migrasi v3 ketika berpindah dari setup Hermes lama, termasuk perubahan jalur MCP desktop ke CLI.

```powershell
.\install.ps1 -SourcePath . -NoSetup
.\install.ps1 -SourcePath . -NoSetup -NoPath
```

`-NoPath` tidak menambahkan launcher ke PATH; gunakan path launcher yang dicetak installer. Jangan menganggap `-NoSetup` sebagai dry-run. Untuk pratinjau pemasangan skill tanpa menulis, gunakan installer langsung:

```powershell
python scripts/install_msshi.py --platform hermes --mode solo --target-dir "C:\MSSHI-Latihan\msshi-skills"
```

Tambahkan `--apply` hanya ketika ingin menerapkan rencana yang ditampilkan. Folder contoh `C:\MSSHI-Latihan\...` dapat diganti dengan lokasi pilihan Anda; folder contoh tidak diasumsikan sudah tersedia.

## Panduan PDF ikut terpasang otomatis

Installer resmi, bootstrap CLI, setup yang diterapkan, dan update menyalin panduan sesuai katalog. Default Windows mengikuti folder Downloads pengguna yang sebenarnya, termasuk jika dipindahkan, lalu subfolder `MSSHI_Manuals`. Pada sistem lain gunakan Downloads bila ada atau folder manual pada data MSSHI. Lokasi hasil dicetak installer.

```powershell
.\install.ps1 -SourcePath . -PdfDest "C:\MSSHI-Latihan\Panduan"
msshi setup --platform hermes --pdf-dest "C:\MSSHI-Latihan\Panduan"
msshi manual list
msshi manual download --version latest --dest "C:\MSSHI-Latihan\Panduan"
```

Perintah setup di atas tetap membuka wizard pemasangan; gunakan `manual download` bila hanya memerlukan PDF. Untuk melewati penyalinan otomatis, gunakan `-NoPdf` pada installer PowerShell atau `--no-pdf` pada CLI/Bash. Variabel `MSSHI_PDF_DIR` dapat menentukan folder; `MSSHI_NO_PDF=1` menonaktifkan pengiriman otomatis untuk proses tersebut. Flag `--yes` bukan pilihan menolak PDF.

Checksum SHA-256 PDF dicocokkan dengan katalog. File identik dibiarkan; file bernama sama yang berbeda disimpan sebagai salinan `.previous-<waktu>.pdf` sebelum penggantian. Kegagalan penyalinan otomatis dilaporkan dengan perintah mencoba ulang dan tidak membatalkan instalasi utama yang berhasil. Unduhan PDF eksplisit yang gagal tetap melaporkan error. Pemasangan melalui marketplace/Skills CLI pihak ketiga hanya menyalin skill yang dipilih dan belum tentu menjalankan installer PDF MSSHI; pengguna jalur itu dapat memakai perintah manual di atas setelah CLI tersedia.

## macOS dan Linux

```sh
MSSHI_RAW="https://raw.githubusercontent.com"
MSSHI_REPO="zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya"
curl -fsSL "$MSSHI_RAW/$MSSHI_REPO/main/install.sh" | bash
```

Dari checkout yang telah diperiksa:

```sh
bash install.sh --source-dir .
bash install.sh --source-dir . --no-setup
bash install.sh --source-dir . --no-setup --no-path
```

Perintah Bash memakai flag berbeda dari PowerShell. Ketentuan host/runtime tertentu tetap bergantung OS, versi Python, arsitektur CPU, dan tool yang tersedia. Uji Windows tidak otomatis membuktikan semua dependency opsional berjalan pada setiap sistem.

## Instalasi melalui chat agen

Untuk agen yang dapat membaca web, menjalankan terminal, dan menulis folder skill lokal, gunakan pesan dari repo:

> Tolong baca https://raw.githubusercontent.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/main/INSTALL_FOR_AGENTS.md lalu instal dan konfigurasikan MSSHI untukku!

Tambahkan tujuan bila sudah diketahui, misalnya profil Hermes tertentu atau mode Selective Packs. Agen harus menjelaskan fungsi pilihan, meninjau target, dan menghormati instruksi serta izin yang sudah Anda berikan. Koneksi akun dan dependency tetap dapat memerlukan langkah pengguna.

## Jalur setiap host

| Host | Jalur yang tersedia di repo | Catatan |
| --- | --- | --- |
| Hermes | CLI MSSHI, Skills CLI, atau Hermes tap | Tap mendaftarkan katalog; pemilihan/pemasangan skill tetap terpisah |
| OpenClaw | Root `SKILL.md`, pemasangan Git/Skills CLI, atau skill yang diekstrak | Fitur lampiran dan perintah instalasi mengikuti versi host |
| Claude Code | Marketplace plugin atau Skills CLI | Marketplace dan plugin install adalah dua tahap |
| Claude.ai Web/Desktop | Upload `portable/msshi.zip` melalui fitur skill yang tersedia | Tidak memberikan terminal/aplikasi lokal secara otomatis |
| ChatGPT Projects/Custom GPT | Knowledge Bundle dan Custom Instructions pada `portable/` | Pengetahuan/instruksi tidak menciptakan koneksi CLI lokal |
| Codex | Skills CLI atau folder skill host | Tindakan tetap mengikuti sandbox dan alat sesi |
| Antigravity | `msshi setup --platform antigravity` atau jalur skill IDE | Lokasi skill mengikuti host; model IDE dipertahankan |
| Agen lain | `--platform manual` dengan folder yang dipilih | Host harus mampu membaca format dan mendukung alat yang dibutuhkan |

Contoh jalur Skills CLI yang dicantumkan repo untuk Hermes:

```powershell
$MsshiSkillsUrl = "https://github.com/zidanaisar624/" +
    "MSSHI-Mega-Semar-Sang-Hyang-Ismaya/tree/main/skills"
npx skills add $MsshiSkillsUrl --global --agent hermes-agent
```

Untuk agen lain, ikuti nama agent yang dituliskan README/host terkait. Jalur `/skills` memilih koleksi standar; REA berada di direktori opsional terpisah. Pemasangan melalui host/marketplace dikelola oleh host itu, sedangkan CLI MSSHI mengelola target yang terdaftar padanya. Perintah host pihak ketiga ini diambil dari panduan repo; modul ini tidak menguji ulang pemasangan pada semua produk/akun.

## Pertahankan konfigurasi yang sudah ada

Pada Hermes yang didukung, mode `muza-preset` sekarang menyiapkan lima profil native bernama `yukino`, `shizuka`, `val`, `kiki-chii`, dan `shikaku`, termasuk marker identitas serta pengenalan oleh host. Default tetap Hermes netral. Profil yang sudah ada mempertahankan SOUL, rahasia dan pilihan modelnya; profil baru mendapatkan konfigurasi awal melalui mekanisme host. Pada host selain Hermes, hasil mode tim tetap berupa workspace portabel dan harus dihubungkan sesuai kemampuan host. Instalasi tidak membuat akun, grup Telegram atau Discord secara otomatis.

Jangan menempelkan API key ke Knowledge Bundle, README publik, screenshot laporan, atau GitHub. Gunakan mekanisme rahasia/akun dari host masing-masing.

# 3. Pilihan setup dan kebiasaan memakai terminal

## Empat mode

| Mode | Pilih ketika | Yang dihasilkan |
| --- | --- | --- |
| `solo` | Satu agen menangani beragam tugas | Semua instruksi standar pada satu target |
| `custom-bots` | Anda ingin jumlah/nama/peran sendiri | Workspace bot dan pilihan skill masing-masing |
| `selective` | Anda hanya membutuhkan bidang tertentu | Paket/skill pilihan beserta fondasi wajib |
| `muza-preset` | Anda ingin lima peran terstruktur | Lima profil native pada Hermes yang didukung; workspace portabel pada host lain |

```powershell
msshi setup
msshi setup --platform hermes
msshi setup --platform antigravity
msshi setup --lang en
```

Menu kini menampilkan fungsi tiap pilihan sebelum pengguna menjawab. Bahasa penjelasan dapat dipilih; ID, angka pilihan, pemisah koma, dan format jawaban tetap sama. `all` memilih semua item dalam daftar yang sedang ditampilkan. Tinjau daftar tersebut karena makna `all` mengikuti konteks menu.

KAT dan REA merupakan pilihan opsional. Memilih KAT membuka wizard endpoint untuk Shikaku: pilih deployment Dev yang memang tersedia atau preset resmi StreamLake Pro v2.5 yang berbeda varian, lalu siapkan key secara privat. Aktivasi memerlukan endpoint, model yang terverifikasi, key dan rute native yang sesuai. Pada terminal tanpa interaksi, helper hanya menyiapkan status pending, tanpa mengunduh model. Pilihan lama light/ideal/cloud tetap diterima sebagai alias menuju wizard; tidak menjanjikan model 35B muat di laptop. Memilih wrapper REA belum memasang runtime npm atau engine native.

## Paket kategori

Paket mempercepat pemilihan kelompok skill. Skill individual memberi kontrol lebih rinci. Fondasi wajib tetap disertakan oleh installer, dan source eksternal yang dicatat dalam rencana tetap membutuhkan langkah terpisah.

```powershell
msshi choices --kind packs
msshi choices --kind skills
msshi choices unslop
msshi choices rea
msshi choices kat
msshi optional list
```

Gunakan `msshi select --local` untuk memilih dari paket yang sudah ada di perangkat. `msshi select` mengambil kandidat dari GitHub. Keduanya menampilkan rencana sebelum menerapkan pilihan; perintah ini dapat memasang skill yang belum ada pada target yang dipilih.

## Format command

Dalam contoh `msshi scrapling --hermes-home "C:\HermesClient" parse --input ...`, urutannya penting: opsi global keluarga berada sebelum subcommand bila parser keluarga mendefinisikannya demikian. Selalu buka bantuan pada level yang dibutuhkan:

```powershell
msshi --help
msshi scrapling --help
msshi scrapling parse --help
msshi rea native --help
```

Teks `PATH_HERMES`, `PATH_SKILLS`, `INPUT`, atau `OUTPUT_BARU` pada referensi adalah penanda yang harus diganti. Tanda `[]` pada baris `usage:` berarti opsional; tanda `{a,b}` berarti pilih salah satu. Tanda itu bukan selalu bagian yang perlu diketik. Output baru sebaiknya berada di luar folder input jika adaptor menerapkan batas tersebut.

Dalam PowerShell, beri tanda kutip pada path yang mengandung spasi atau apostrof. Gunakan `&` untuk menjalankan path executable yang dikutip. Jangan memakai `$HOME`/`$home` sebagai variabel tugas; nama itu sudah digunakan PowerShell. Modul menggunakan nama seperti `$MsshiHermesRoot` dan `$MsshiReceipt`.

Contoh PowerShell panjang pada PDF memakai backtick di akhir baris untuk melanjutkan command; contoh Bash memakai backslash. Pertahankan tanda lanjutannya dan hindari spasi setelah tanda tersebut. Versi Markdown juga menyediakan command yang mudah disalin.

## Baca status dengan benar

```powershell
msshi connect --status --hermes-home "C:\HermesClient" --profile default
msshi connect --status --hermes-home "C:\HermesClient" --profile kiki-chii
msshi managed status
msshi check
```

Nama peran pada preset publik dapat berbeda dari ID folder instalasi lama. Gunakan ID profil yang diberikan untuk instalasi Anda; nama tampilan bot di Desktop tidak selalu menjadi nama folder. Preset publik memakai ID `yukino`, `shizuka`, `val`, `kiki-chii`, dan `shikaku`; home default dan pemetaan host dapat berbeda.

## Bantuan yang dapat dicari

```powershell
msshi choices --kind apps
msshi choices --kind features --lang en
msshi choices --kind skills --json
msshi optional list --lang en
```

Katalog koneksi juga menjelaskan fungsi aplikasi. Untuk penjelasan koneksi berbahasa Inggris pada proses PowerShell saat ini:

```powershell
$env:MSSHI_LANG = "en"
msshi connect --catalog
```

Untuk kembali ke penjelasan Indonesia, set `$env:MSSHI_LANG = "id"`. Ini memilih bahasa bantuan; tidak mengubah provider atau model.

# 4. Dari permintaan percakapan menjadi pekerjaan alat

<!-- FIGURE: execution -->

## Instruksi otomatis, konteks, dan tindakan eksplisit

Skill merupakan instruksi yang dikenali/dibaca agen berdasarkan tugas dan dukungan host. Keberadaan skill tidak menjamin semua isi dimuat pada setiap pesan. Buat permintaan yang menyebut tujuan, bahan, hasil, dan batas agar agen dapat memilih alur yang sesuai.

| Pola | Contoh pada setup ini | Kapan berjalan |
| --- | --- | --- |
| Hook otomatis yang memenuhi syarat | Llmtrim pada hasil tool JSON besar dan valid | Hanya ketika hook native terpasang dan syarat data terpenuhi |
| Pemilihan menurut konteks | Riset ke Val; video ke Kiki; coding ke Shikaku | Saat agen mengenali tugas dan skill tersedia pada sesi/profil |
| Opsi/aksi eksplisit | Install runtime, aktifkan REA, login layanan, ekspor final | Saat pengguna meminta/memilih langkah yang memiliki efek tersebut |
| Proses proposal lokal terjadwal | Dreaming bila pendaftarannya diaktifkan | Menghasilkan proposal yang masih perlu ditinjau |

Llmtrim tidak merangkum semua chat atau menjamin persentase penghematan tagihan. Hersona menyediakan referensi/draf persona melalui CLI; `SOUL.md` native tetap menentukan persona yang dipakai. Status KAT membedakan persiapan, prasyarat yang hilang, serta konfigurasi aktif yang belum diuji inferensi. Model utama Coder dan delegasi biasa tetap memakai pilihan pengguna.

## Contoh permintaan yang jelas

> Kiki, siapkan tiga konsep video penjelasan untuk mahasiswa baru. Target 90 detik, vertikal, bahasa Indonesia. Gunakan folder proyek yang saya tunjuk, simpan bahan yang bisa diedit, dan tunggu pilihan konsep sebelum membuat storyboard. Jangan render final atau menjalankan layanan berbayar dulu.

> Val, dari HTML yang sudah saya simpan, ekstrak judul dan URL referensi. Batasi 100 hasil, simpan JSON baru, dan jelaskan data yang tidak bisa dibaca. Gunakan parser lokal, bukan crawling situs.

> Shikaku, petakan struktur repo ini dan usulkan satu perbaikan kecil. Pertahankan konfigurasi model, tulis perubahan di source proyek, lalu jalankan pemeriksaan yang relevan. Tunjukkan diff dan hasilnya.

Percakapan ini dapat memakai model provider pengguna. Command lokal yang dijalankan agen memiliki efek tersendiri; periksa output/receipt dan status keberhasilan agar tidak menyamakan balasan agen dengan hasil tool yang sudah terbukti.

## CLI-Anything untuk aplikasi

Anda dapat meminta penghubung melalui percakapan, misalnya:

> Hubungkan Blender dan Lightcraft lewat CLI-Anything untuk proyek ini. Periksa rute yang tersedia, lalu gunakan aplikasi hanya saat pekerjaan memerlukannya.

Dari terminal, gunakan:

```powershell
msshi connect --catalog
msshi connect --mode select --targets blender,lightcraft --hermes-home "C:\HermesClient" --profile kiki-chii
msshi connect --status --hermes-home "C:\HermesClient" --profile kiki-chii
```

Registrasi tersebut menyiapkan rute. Eksekusi native pada arsitektur v3 memakai runner dan tiket tugas yang dijelaskan dalam referensi CLI. Aplikasi perlu memiliki CLI/adaptor yang tersedia; permintaan menyambungkan aplikasi baru tidak otomatis menciptakan adaptor lengkap atau memasang lisensi/akun.

Pada arsitektur v3, aplikasi desktop seperti Lightcraft/Blender diarahkan melalui native CLI. GitLab dan Tinyfish tetap merupakan MCP web. Jika sebuah dokumen lama menyebut ArtCraft MCP/Blender MCP, gunakan kebijakan v3 dan rute native saat ini; jangan mengaktifkan ulang server desktop lama hanya karena label historis tersebut.

## Lima bot sebagai pembagian kerja

<!-- FIGURE: roles -->

Yukino membantu menampung ide dan membuat pertanyaan awal. Shizuka menyusun strategi serta menyampaikan hasil riset dalam bahasa yang dapat dipakai. Val menyuplai riset dan bukti. Kiki-Chii mengerjakan ranah kreatif/film/foto/video. Shikaku mengerjakan coding dan evaluasi keamanan sesuai tugas yang diizinkan.

Pada Hermes yang didukung, preset memasang plugin lokal `msshi-team-routing` pada profil. Plugin menambahkan kebijakan koordinasi ke prompt sesi baru dan menawarkan profil hidup melalui backend delegasi native. Bot Chat memakai `message_agent` bila tool itu memang tersedia; fallback memakai `delegate_task` dengan parameter profil yang ditawarkan schema aktual. Backend kustom pengguna dipertahankan. Instalasi tidak mengirim tugas model; percakapan antarbots yang benar-benar dijalankan dapat memakai kredit. Mulai sesi baru setelah plugin dimuat ulang agar aturan baru masuk; riwayat lama tetap disimpan. Host tanpa fasilitas itu dapat memakai paket handoff pada bab praktik.

Setelah tugas, periksa output/receipt dan batas pengujiannya. Pakai bukti yang sudah ada sebelum mengulang render atau operasi web.

# 5. Versi, sumber, dan batas kepercayaan modul

`VERSION.json` memuat nomor versi paket. Commit Git menunjukkan isi source yang lebih spesifik. `main` dapat menerima perbaikan penjelasan tanpa menaikkan nomor versi; karena itu dua paket bertuliskan 3.1.1 dapat memiliki commit berbeda.

| Identitas | Nilai edisi ini |
| --- | --- |
| Versi paket | `3.1.1` |
| Commit implementasi yang dijelaskan | `84ecd134f01ec65c4848b4f50c597b811f6b3a80` |
| Edisi modul | 16 November 2026, Asia/Jakarta |
| Manifest | 67 skill fisik, 51 inti, 16 wrapper, 52 sumber |
| Cakupan bukti | Sintaks dan perilaku source; status perangkat/akun diuji tersendiri |

`msshi check/status` membandingkan versi dan menampilkan changelog. Identitas commit membantu membedakan isi source. Tag historis tidak perlu dipindahkan untuk memasang revisi baru. Pada versi ini manifest sumber berisi 49 Git, dua model-card, dan satu katalog; jumlah itu berbeda dari jumlah rute aplikasi atau tool.

## Urutan rujukan saat ada perbedaan

1. Parser `--help`, source implementasi, dan output command pada commit yang benar.
2. Manifest/version serta panduan fitur saat ini yang cocok dengan implementasi.
3. Receipt privat untuk fakta yang hanya berlaku pada laptop tersebut.
4. Dokumen historis dan roadmap sebagai konteks, bukan bukti runtime sudah siap.

API key, cookie, token, dan arsip pribadi tidak dicantumkan dalam modul. Katalog sumber dan instruksi skill tidak sama dengan telah mengunduh seluruh bahan sumber. Akses akun personal dan koneksi layanan tetap memerlukan mekanisme host yang sesuai.

## Sumber utama

- [Repositori MSSHI](https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya)
- [Commit yang menjadi dasar modul](https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/commit/84ecd134f01ec65c4848b4f50c597b811f6b3a80)
- [README pada commit ini](https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/blob/84ecd134f01ec65c4848b4f50c597b811f6b3a80/README.md)
- [CLI dan panduan pilihan](https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/blob/84ecd134f01ec65c4848b4f50c597b811f6b3a80/docs/CLI.md)
- [Penjelasan seluruh pilihan](https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/blob/84ecd134f01ec65c4848b4f50c597b811f6b3a80/docs/OPTION_GUIDE.md)
- [Lisensi/atribusi pihak ketiga](https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/blob/84ecd134f01ec65c4848b4f50c597b811f6b3a80/THIRD_PARTY_NOTICES.md)

Kode orisinal MSSHI: MIT. Lisensi pihak ketiga tetap berlaku: bobot OmniVoice CC-BY-NC dan instruksi Unslop CC BY 4.0. Periksa ketentuan aset/dependency sebelum penggunaan atau distribusi komersial.


# 6. Menjalankan proyek lewat percakapan dan terminal

Panduan ini ditujukan untuk pengguna yang menerima setup MSSHI atau memasangnya sendiri. Semua path Windows C:\HermesClient dan C:\MSSHI-Latihan di bawah adalah contoh, bukan lokasi yang pasti ada di komputer Anda. Ganti C:\HermesClient dengan root Hermes yang dicatat saat serah terima, dan gunakan folder latihan baru milik sendiri. Jangan membuat root Hermes kedua hanya untuk menyamakan contoh. Nama profil pada command juga harus cocok dengan profil yang benar-benar terpasang.

## Pahami lapisan yang sedang dipakai

MSSHI memberi petunjuk kerja, persona, pemilihan alat, dan helper terminal. Hermes adalah host yang membaca petunjuk itu dan menjalankan model serta tool yang tersedia. Karena itu, memasang MSSHI belum berarti setiap aplikasi, model lokal, atau akun layanan sudah siap. Gunakan enam lapisan berikut ketika membaca laporan atau mencari sumber masalah.

| Lapisan | Yang diperiksa | Bukti yang masuk akal |
| --- | --- | --- |
| Instruksi skill | Apakah folder dan SKILL.md tersedia pada profil yang benar? | Nama skill ditemukan oleh host atau ada pada katalog pemasangan. |
| Runtime | Apakah program/dependency/model yang diperlukan sudah dipasang? | Status helper, versi paket, executable, checksum atau metadata instalasi. |
| Registrasi rute | Apakah Hermes tahu alat mana yang akan dipanggil? | Rute tercatat, misalnya native-cli dan registered:true. |
| Autentikasi | Apakah akun layanan memberi akses saat ini? | Probe/login berhasil pada akun dan profil yang benar. |
| Operasi | Apakah tindakan tertentu benar-benar berhasil? | File keluaran, hasil parser, ekspor, atau respons operasi yang dapat diperiksa. |
| Mutu hasil | Apakah keluaran memenuhi brief? | Pemeriksaan isi, pengujian yang relevan, dan penilaian pengguna. |

Contohnya, Blender dengan readiness available berarti executable/adapter tersedia. Itu belum menjadi bukti sebuah adegan tertentu sudah dirender. Tinyfish yang registered belum tentu memiliki token login yang masih berlaku. Jika sebuah uji MP4 satu detik berhasil, itu membuktikan jalur ekspor kecil; ia belum membuktikan seluruh film 40 menit, kualitas suara, atau akun generator video.

### Otomatis, sesuai konteks, dan manual

Pada setup yang memasang plugin lossless Llmtrim, hook dapat memadatkan hasil tool JSON besar yang memenuhi syarat secara otomatis. JSON diperiksa kesetaraannya; percakapan biasa, kode, konfigurasi, persona, serta error dilewati. Penghematan tergantung jenis keluaran, bukan janji persentase pengurangan semua token atau tagihan.

Skill kontekstual dipilih ketika tugas memerlukannya: Unslop untuk layar UI, Scrapling untuk file HTML, TimesFM untuk deret waktu numerik, dan BRAG untuk film peluncuran. Percakapan dan penalaran agen dapat memakai token/kredit sesuai model serta provider yang dipilih. Menjalankan parser lokal tanpa LLM berbeda dari meminta agen menyusun penjelasan panjang tentang hasilnya.

Instalasi dependency, login, penerbitan, unggahan, dan penggunaan layanan berbayar adalah tindakan tersendiri. Sebutkan scope dengan jelas. Contoh: “Baca file HTML lokal ini dan simpan hasil baru” memberi ruang kerja yang lebih jelas daripada “urus semuanya”. Bridge MSSHI memakai auto_open_on_boot:false dan dispatcher mengeksekusi alat untuk tugas aktif melalui tiket dengan umur terbatas. Pengaturan startup mandiri aplikasi atau sistem operasi perlu diperiksa terpisah.

## Memakai satu bot atau lima peran

Preset MSSHI pada Hermes yang didukung membuat atau mengenali lima profil native dengan folder dan marker identitas yang benar. Default adalah Hermes netral; Yukino memiliki profil bernama sendiri. Periksa daftar profil di Desktop dan kecocokan folder ketika menerima instalasi. Plugin lokal koordinasi menyuplai aturan kerja ke sesi baru serta rute ke profil hidup. Pada host lain, workspace/persona tetap memerlukan fasilitas koordinasi host masing-masing.

Dalam mode Solo, satu agen mengerjakan langkah peran secara berurutan. Pada preset tim Hermes, Yukino menampung ide lalu menyerahkan rencana lintas bidang kepada Shizuka; Shizuka membagi tugas ke Val, Kiki atau Shikaku dan menyatukan jawabannya. Tidak perlu memalsukan nama model atau membuat lima jawaban dalam satu persona untuk menyebutnya kolaborasi. Tool yang ditawarkan sesi menentukan apakah penyerahan dapat benar-benar dijalankan.

| Peran | Kapan mulai dari sini | Yang sebaiknya diserahkan |
| --- | --- | --- |
| Yukino | Ide masih kabur, terlalu banyak pilihan, atau perlu menentukan langkah kecil. | Tujuan, beberapa alternatif, batas waktu, bahan awal, dan pertanyaan untuk Shizuka. |
| Sensei Shizuka | Perlu strategi, pembagian kerja, atau penjelasan terpadu. | Rencana yang menyebut pemilik langkah, keluaran, bukti, batas, dan keputusan pengguna. |
| Val | Perlu sumber, literatur, metode, data, atau evaluasi bukti. | Dossier sumber, klaim beserta bukti, ketidakpastian, dan hal yang belum dapat disimpulkan. |
| Kiki-Chii | Perlu konsep, naskah, foto, video, desain, editing, warna, atau suara. | Brief, proyek yang dapat diedit, preview, catatan review, dan aset final yang disetujui. |
| Shikaku / Coder | Perlu kode, debugging, toolchain, evaluasi harness, atau audit artefak yang diizinkan. | Rencana perubahan, diff, hasil verifikasi, batas pengujian, dan cara pemulihan. |

Preset lima peran MuZA adalah salah satu pilihan publik, bukan kewajiban. Nama peran manusia dan ID folder dapat berbeda pada setup kustom. Lihat catatan serah terima untuk mencocokkan nama bot dengan ID profilnya; jangan membuat folder baru hanya karena nama tampilan bot berubah. Pada contoh berikut, kiki-chii dipakai sebagai ID ilustratif untuk peran kreatif.

### Pola percakapan yang mengurangi salah paham

Gunakan brief dengan enam unsur: tujuan, bahan, lokasi kerja, hasil, batas, dan titik review. Contoh:

> Shizuka, aku ingin membuat tutorial 12 menit tentang proyek contoh di C:\MSSHI-Latihan\MyApp. Val memeriksa klaim dari bahan lokal. Kiki memegang konsep dan video; Shikaku membantu kode komposisi jika diperlukan. Hasilnya proyek yang dapat diedit, preview per bab, lalu MP4. Gunakan alat lokal yang tersedia, jangan ganti provider/model, dan tunggu pilihanku pada konsep, storyboard, rough cut, serta final.

Dalam Bot Chat, gunakan `message_agent` bila schema sesi menyediakannya. Di sesi lain, backend `msshi-team` dapat menawarkan `delegate_task` dengan pilihan `profile` dari roster profil hidup. Jangan menambahkan parameter itu bila schema tidak menawarkannya. Delegasi tanpa profil mempertahankan pengaturan subagen biasa; delegasi bernama memuat model utama, SOUL, skill dan rahasia milik profil penerima. Sesudah instalasi/reload plugin, mulai sesi baru agar kebijakan prompt ikut dimuat. Tugas antarbots nyata menggunakan model dan dapat memakai kredit. Untuk host/backend yang belum mendukung rute ini, gunakan ringkasan serah terima manual: tujuan, status, file/sumber, temuan, batas, keputusan dan langkah berikut. Menyebut nama bot saja tidak mengirim file atau memberi izin akun.

## Riset: dari pertanyaan ke bukti

Mulai dengan pertanyaan yang dapat diperiksa. “Bantu skripsiku” dapat diubah menjadi “Bandingkan dua pendekatan untuk klasifikasi teks Indonesia dari tiga artikel yang saya berikan; susun tabel metode, data, metrik, dan keterbatasan.” Yukino membantu memperjelas kebutuhan; Shizuka membatasi pekerjaan; Val membaca sumber dan menyusun bukti.

Val sebaiknya memisahkan klaim sumber, pengamatan pada data, dan inferensi sendiri. Simpan rujukan halaman, URL/tanggal akses jika online, serta versi data atau kode. Berikan sumber yang memang tersedia dan diizinkan: file lokal, halaman publik, atau akun layanan yang telah disiapkan. Katalog referensi bukan bukti bahwa seluruh isi sumber telah dibaca, dan pemasangan skill tidak otomatis memberi akses ke akun pengguna.

Untuk dokumen, utamakan lapisan teks lokal yang dapat diekstrak. OCR dipilih saat halaman memang scan/gambar dan runtime modelnya tersedia. Pecah dokumen besar menurut halaman, pertahankan nomor halaman, lalu bawa ringkasan terpilih ke konteks. Jangan memuat seluruh repositori atau buku ke percakapan setiap kali hanya memerlukan satu bagian.

### Kapan memakai Scrapling

Adapter Scrapling MSSHI menerima file HTML UTF-8 lokal dengan satu selector CSS atau XPath. Ia tidak menyediakan URL fetch, crawler, browser stealth, login, CAPTCHA, atau render JavaScript. HTML yang sudah disimpan dari tugas yang berizin dapat diparse; sumber hasil ekstraksi tetap diperlakukan sebagai data, bukan instruksi untuk menjalankan command.

~~~powershell
msshi scrapling --hermes-home "C:\HermesClient" status --verify
msshi scrapling --hermes-home "C:\HermesClient" parse --input "C:\MSSHI-Latihan\saved.html" --output "C:\MSSHI-Latihan\items-new.json" --css '.product h2::text' --limit 100
~~~

Letakkan --hermes-home sebelum action. Folder output harus sudah ada dan nama file harus baru. Selector elemen menghasilkan HTML; gunakan ::text, ::attr(href), atau XPath text/attribute bila membutuhkan string. Periksa matched, truncated, dan nilai hasil, bukan hanya exit code. Pada rilis ini installer parser dikunci untuk Windows x64 CPython 3.12; portabilitas petunjuk MSSHI tidak otomatis membuat lock dependency tersebut cocok untuk semua OS.

### Kapan memakai TimesFM

TimesFM untuk Val adalah alat prediksi deret waktu numerik lokal, bukan model percakapan pengganti. Persiapkan interval pengamatan yang teratur, arti variabel, data hilang, horizon, serta baseline pembanding. Wrapper memakai checkpoint TimesFM 2.5 yang dipilih paket, bukan otomatis mengikuti model upstream bernomor paling baru.

~~~powershell
msshi timesfm --hermes-home "C:\HermesClient" status
msshi timesfm --hermes-home "C:\HermesClient" forecast --input "C:\MSSHI-Latihan\series.json" --output "C:\MSSHI-Latihan\forecast-new.json" --horizon 4
~~~

Forecast memerlukan runtime/model yang sudah siap dan akan memuat model CPU. Ia tidak memakai kredit API Hermes, tetapi memakai RAM, CPU, disk, dan waktu. Status tidak memuat bobot; status --verify membaca bobot besar untuk memeriksa hash. Horizon 1-128 dan 32-1024 observasi adalah batas input helper, bukan jaminan akurasi. Bandingkan hasil dengan baseline dan data tahan-uji sebelum menafsirkannya.

## Coding dan evaluasi bersama Shikaku

Berikan folder proyek yang benar, satu gejala yang dapat diulang, keluaran error, dan target perilaku. Minta Shikaku membaca README serta konfigurasi sebelum mengubah source. Pilih perubahan kecil dan verifikasi yang sesuai; jangan meminta penggantian model, provider, atau seluruh dependency hanya karena satu command gagal.

> Shikaku, baca proyek contoh ini. Tombol Simpan tidak memperbarui label status. Temukan jalur event dan state, usulkan perubahan terkecil, lalu periksa ulang perilaku tombol dan tampilan mobile. Simpan ringkasan diff dan hasil pemeriksaan. Jangan ubah bagian lain tanpa kebutuhan yang terjelaskan.

Toolchain proyek tetap menentukan command nyata: npm scripts, pengujian Python, compiler, atau framework tertentu. MSSHI tidak menyediakan satu command “perbaiki semua aplikasi”. Alat seperti Goose, Graphify, atau playbook coding dipilih sesuai tugas dan kesiapan runtime; keberadaan referensi upstream tidak berarti semua telah dipasang.

### Unslop untuk UI, humanizer untuk tulisan

Unslop digunakan pada layar antarmuka: hierarki, ruang, warna, ikon, copy UI, tipografi, layout, detail, visual, dan gerak. Kiki menilai arah visual; Val meninjau grafik ilmiah, unit, label, legenda, sumber, dan ketidakpastian; Shikaku menerapkan perubahan komponen/CSS dan memeriksa hasil.

Humanizer Indonesia/Inggris serta match-my-writing-style menangani prosa dan suara penulis. Mereka harus mempertahankan fakta, kutipan, sitasi, serta maksud. Jangan meminta Unslop untuk menulis ulang semua percakapan atau menganggapnya filter penulisan global. Jika hanya mengaudit screenshot tanpa source/browser, hasilnya adalah diagnosis/brief; implementasi belum dapat diklaim selesai.

### Harness2: proposal dan demo, bukan pembaruan otomatis bot

Harness² tersedia sebagai instruksi bagi kelima bot. Yukino memperjelas hipotesis, Shizuka menyatukan rencana, Val merancang baseline/probe/holdout, Shikaku menguji kandidat di salinan eksperimen, dan Kiki dapat membandingkan alur kreatif. Setiap peran memakai disiplin yang relevan; kepemilikan skill tidak berarti benchmark model telah dijalankan atau perubahan otomatis dipromosikan.

~~~powershell
msshi harness2 --hermes-home "C:\HermesClient" status --verify
msshi harness2 --hermes-home "C:\HermesClient" plan --goal "Bandingkan instruksi tool singkat dengan baseline pada tugas contoh yang sama"
~~~

Plan mencetak proposal JSON. Demo terpasang dapat dijalankan dengan action demo, tetapi memerlukan runtime; ia menggunakan ledger deterministik, bukan panggilan model. Demo tersebut membuktikan jalur demonstrasi lokal, bukan kemenangan benchmark atau kualitas model. Wrapper tidak memasang benchmark model berbayar, Vertex/gcloud, executor Codex tanpa sandbox, atau promosi hasil ke memory/prompt/plugin bot aktif. Eksperimen nyata perlu data uji yang tidak bocor, diff, anggaran bila memakai API, dan rencana rollback.

### REA sebagai opsi terpisah

REA publik default OFF dan berada di optional/rea, di luar 67 skill standar. Pengguna memilihnya secara eksplisit bila perlu memeriksa artefak aplikasi yang dimiliki atau diizinkan. Pada preset lima peran, opsi ini ditujukan ke Coder; pada setup kustom, pilih profil penerima dengan jelas. Jika tugas tidak memerlukannya, biarkan tetap OFF.

~~~powershell
msshi optional list
msshi rea --hermes-home "C:\HermesClient" status
msshi rea --hermes-home "C:\HermesClient" javascript "C:\MSSHI-Latihan\owned-js" --output "C:\MSSHI-Latihan\js-analysis-new.json"
msshi rea --hermes-home "C:\HermesClient" inspect archive "C:\MSSHI-Latihan\owned.zip" --output "C:\MSSHI-Latihan\archive-analysis-new.json"
~~~

Instruksi REA, runtime npm, dan engine native adalah komponen berbeda. Analisis JavaScript/ZIP yang diuji tidak mengeksekusi target. Dukungan format lain bergantung engine dan input; jangan menganggap semua binary, ASAR, Android, debugger, atau Ghidra telah siap. Wrapper CLI ini tidak memasang MCP baru, tidak mengunduh engine native, dan mengecualikan jalur IDA yang bergantung pada bridge MCP upstream. Simpan laporan baru di luar input dan hormati ruang lingkup yang telah diizinkan.

## Produksi kreatif: konsep sampai proyek yang dapat diedit

Dalam preset lima peran, Kiki-Chii memegang rangkaian kreatif: ide, naskah, penyutradaraan, gambar, produksi visual, editing, warna, efek, suara, dan preview. Pada mode Solo atau tim kustom, tanggung jawab itu dapat diberikan kepada agen yang dipilih pengguna. Ini adalah tanggung jawab peran, bukan janji bahwa AI selalu dapat mengendalikan seluruh fitur setiap aplikasi. Adapter, akun, aset, dan toolchain yang tersedia menentukan tindakan yang dapat dieksekusi.

### Concepting First

Sebelum alat produksi dibuka, sepakati audiens, tujuan, satu pesan utama, durasi, rasio aspek, platform, rasa visual, sumber bukti, aset, suara, tenggat, dan batas biaya. Minta dua atau tiga konsep yang benar-benar berbeda, lalu pilih satu. Pengguna tetap dapat memberi komentar pada tiap tahap dan menyunting proyek melalui aplikasi yang sama.

Gerbang review yang praktis adalah konsep terpilih, naskah/storyboard, rough composition/cut, polished preview beserta audio/hak aset, lalu ekspor final. Persetujuan instalasi bukan persetujuan kreatif. Catat keputusan dengan nama versi, waktu, bagian yang disetujui, dan revisi yang masih diminta. Jangan menambahkan klaim produk atau aset pribadi yang tidak diberikan.

### Pilih alat berdasarkan hasil yang diperlukan

| Alat atau kelompok | Bentuk kerja | Batas yang perlu dipahami |
| --- | --- | --- |
| Bang Motion | Opener, explainer, teks bergerak, atau draf HTML yang dapat direvisi. | Memerlukan source/dependency proyek; bukan konverter universal ke semua editor. |
| BRAG + Hyperframes | Film peluncuran dari konsep, storyboard, komposisi HTML, preview, dan MP4 lokal. | init hanya membuat scaffold dokumen; komposisi/render memerlukan tahap kerja berikut dan runtime. |
| Remotion | Komposisi berbasis kode, timeline, timing, subtitle, dan render terprogram. | Menggunakan proyek/dependency Remotion yang benar; tidak ada perintah MSSHI remotion universal. |
| ArtCraft | Polishing foto, video, audio, desain, dan dokumen melalui adapter aplikasi yang tersedia. | Fungsi yang dapat dikendalikan bergantung CLI/adapter aplikasi, bukan semua tombol UI otomatis tersedia. |
| Blender | Adegan 3D, kamera, material, animasi, dan render sesuai project. | Dibutuhkan executable dan file project; status available belum membuktikan render proyek tertentu. |
| Higgsfield atau layanan hosted lain | Generasi gambar/video atau aset khusus bila alat, akun, dan izin tersedia. | Dapat memakai kredit layanan; jangan dipanggil sebagai tes gratis tanpa scope. |

Simpan source HTML/React, media asli, font, manifest aset, timeline, dan keputusan review. MP4 merupakan hasil gambar/audio yang sudah digabung; mengimpor MP4 ke Remotion atau ArtCraft menjadikannya klip footage, bukan mengembalikan lapisan teks, keyframe, atau objek 3D. Agar tetap mudah diedit, bawa sumber dan format pertukaran yang memang didukung kedua alat.

Contoh rantai yang masuk akal: Bang Motion membuat draf opener HTML; Kiki meninjau lalu mengekspor preview; Remotion memasukkan klip atau mengimplementasikan komposisi ulang dengan source yang tersedia; SoundCraft memoles audio; editor video yang mendukung format hasil menyelesaikan cut. Ini alur proyek yang dipilih, bukan pipeline otomatis terpasang untuk setiap tugas.

### BRAG dari terminal

~~~powershell
msshi brag doctor
msshi brag init --project "C:\MSSHI-Latihan\MyApp" --output "C:\MSSHI-Latihan\MyApp\brag-new" --title "Demo MyApp"
~~~

Init membuat CONCEPT.md, REVIEW.md, dan request.json baru. Ia tidak membaca seluruh source, memanggil LLM, membuat media, atau menganggap konsep sudah disetujui. Brief BRAG ini membatasi durasi 15-25 detik (default 20); ia bukan satu command untuk video 10-40 menit. Setelah komposisi benar-benar dibuat dan preview yang tepat disetujui, gunakan:

~~~powershell
msshi brag check --project "C:\MSSHI-Latihan\MyApp\brag-new\composition"
msshi brag render --project "C:\MSSHI-Latihan\MyApp\brag-new\composition" --output "C:\MSSHI-Latihan\MyApp\brag-new\final-new.mp4" --quality delivery --human-approved-preview
~~~

Flag --human-approved-preview menyatakan pengguna telah menyetujui preview itu; ia tidak menghasilkan persetujuan. Doctor membaca kesiapan lokal tanpa membuka browser. Check/render memakai browser render bersih dan dapat mengambil font publik bila belum dilokalkan. Rendering lokal tidak otomatis berarti offline. Minimum RAM/commit/disk helper hanya pagar awal; proyek produksi memerlukan kapasitas lebih besar.

### Video 10-40 menit

Gunakan pembagian bab, bukan satu prompt panjang yang langsung meminta hasil final. Buat outline dengan target durasi tiap bab, naskah AV atau shot list, daftar aset, dan kriteria selesai. Produksi satu segmen kecil dahulu untuk menguji gaya, keterbacaan, audio, serta beban render.

Misalnya video 12 menit dapat dibagi menjadi pembuka 30 detik, empat bab masing-masing sekitar dua setengah menit, lalu penutup. Angka tersebut adalah rancangan editorial yang boleh diubah, bukan aturan software. Setelah gaya disepakati, kerjakan per bab, simpan rough cut, dan mintalah komentar berbasis timecode: “02:14 teks terlalu cepat; 05:32 kecilkan musik saat narasi.”

Gabungkan bab di timeline master, lalu periksa kontinuitas gambar, level suara, subtitle, nama file, lisensi aset, klaim, dan durasi akhir. Finalisasi setelah pengguna menyetujui preview yang sesuai. Simpan master yang dapat diedit, ekspor distribusi, serta daftar keputusan. Jangan menyebut proses 40 menit telah terbukti hanya karena ekspor diagnostik satu detik berhasil.

### Narasi dan audio

OmniVoice lokal memerlukan bobot dan runtime yang sudah lolos sintesis. Mode voice chat dapat hanya melakukan STT; berbicara ke mikrofon tidak otomatis berarti semua jawaban dibacakan. Gunakan pilihan Read replies aloud/output audio pada host atau minta audio secara eksplisit. Pengaturan suara normal/calm/tired/incident menentukan preferensi gaya keluaran audio.

Bobot OmniVoice berlisensi CC-BY-NC; penggunaan komersial perlu hak yang sesuai. ElevenLabs, SoundCraft, musik, SFX, serta font memiliki akun/lisensi/dependency masing-masing. MSSHI tidak menganggap model ElevenLabs otomatis tersedia setelah kredit Hermes terisi. Sebutkan penyedia suara yang memang disiapkan, lalu tinjau naskah, bahasa, pengucapan, hak suara, dan biaya sebelum produksi.

Creative DNA menyimpan preferensi yang disetujui: misalnya tempo editing, kontras, ragam caption, atau jenis transisi. Templat publik adalah contoh. Simpan data preferensi dan proyek nyata secara privat; pembelajaran/penulisan perubahan perlu mengikuti pilihan pengguna. Kiki dapat mengusulkan pembaruan setelah proyek, bukan diam-diam menganggap semua koreksi sementara sebagai aturan permanen.

## CLI-Anything, browsing, dan akun layanan

Permintaan percakapan dapat memicu skill bridge bila profil telah memuatnya: “Kiki, gunakan Blender dan Lightcraft untuk proyek ini; periksa kesiapan dahulu.” Agen kemudian meninjau rute dan membuat tiket untuk alat yang diperlukan. Tidak perlu menulis command bila host dan skill mampu menanganinya, tetapi terminal tetap berguna untuk memeriksa apa yang sebenarnya terjadi.

~~~powershell
msshi choices --kind apps
msshi connect --status --hermes-home "C:\HermesClient" --profile kiki-chii
msshi connect --mode select --targets blender,lightcraft --hermes-home "C:\HermesClient" --profile kiki-chii
~~~

Pembagian ArtCraft pada preset MuZA bersifat khusus per peran:

| Profil | Aplikasi ArtCraft yang diizinkan |
| --- | --- |
| `default`, `yukino`, `shizuka` | Tidak diberi rute ArtCraft |
| `val` — 4 | pdfcraft, gridcraft, wordcraft, deckcraft |
| `shikaku` — 2 | craftanything, figcraft |
| `kiki-chii` — 13 | anicraft, filmcraft, effectcraft, soundcraft, photocraft, lightcraft, designcraft, figcraft, vectorcraft, cadcraft, solidcraft, materialcraft, texturecraft |

Figcraft adalah satu-satunya aplikasi bersama Shikaku/Kiki. Aplikasi pendamping seperti Python, FFmpeg, Blender atau browser memiliki aturan tersendiri. Tugas dokumen dari proyek film dapat didelegasikan ke Val. Memilih `all` pada koneksi tidak memberi hak ArtCraft di luar matriks preset.

Folder aplikasi Windows default preset adalah `D:\Program\ArtCraft Apps`; `MSSHI_ARTCRAFT_ROOT` dapat memberi lokasi yang berbeda. Binary dan lisensi tetap milik instalasi aplikasi. CraftAnything dipakai lewat CLI tugas yang didukung, bukan `setup --client hermes`, `mcp`, `serve`, atau `--connect`. GDrive/gdrive-web, GIMP, LibreOffice dan Solvecraft tetap nonaktif dalam rute preset ini; jangan menganggap koneksi Google Drive otomatis tersedia dari daftar lama.

Connect mendaftarkan rute; ia tidak membuka aplikasi, memasang dependency, atau membuktikan login. Setelah migrasi v3, aplikasi desktop dijalankan melalui dispatcher runtime dengan tiket satu kali. Contoh kecil berikut memeriksa versi FFmpeg untuk tugas aktif; ganti TICKET_ID dengan ID yang dicetak, bukan mengetiknya secara harfiah.

~~~powershell
msshi runtime ticket --home "C:\HermesClient" --profile kiki-chii --target ffmpeg --task "Periksa versi FFmpeg untuk proyek latihan aktif" --source context --ttl 120
msshi runtime run --home "C:\HermesClient" --profile kiki-chii --ticket TICKET_ID ffmpeg -- -version
~~~

Tiket terikat profil, target, satu eksekusi, dan waktu. Membuat tiket bukan izin untuk mengganti target atau menambah perintah lain. Perintah connect --open/--run yang muncul pada bagian dokumentasi v2.1 bukan jalur eksekusi profil v3. Istilah ArtCraft MCP/Blender MCP pada beberapa referensi film lama juga tidak menjadi instruksi mengaktifkan ulang MCP desktop; ikuti kebijakan CLI versi ini.

Steel adalah rute penjelajahan umum yang dikonfigurasi melalui guard. Tanpa key/endpoint, browsing umum berhenti dengan petunjuk setup dan tidak diam-diam berpindah ke Chrome personal. Jika tugas memerlukan akun yang sudah login pada browser pengguna, sebutkan situs, akun, tujuan, cakupan akses, dan masa akses. Persetujuan akses browser tidak sama dengan persetujuan menyalin cookie atau memindahkan login ke Steel; pemindahan sesi belum diimplementasikan otomatis.

GitLab dan Tinyfish tetap MCP layanan web, berbeda dari aplikasi desktop yang dipindahkan ke CLI. Login bersifat per akun/profil. Opsi berbagi cache OAuth pada Windows harus dipilih secara eksplisit untuk profil yang memakai identitas akun yang sama; jangan menggunakannya pada bot yang harus memakai akun berbeda. Registrasi status, discovery, autentikasi, dan operasi perlu dibedakan.

~~~powershell
msshi services status --hermes-home "C:\HermesClient"
msshi browser --status --hermes-home "C:\HermesClient"
~~~

Status di atas tidak membuka sesi Steel atau menjalankan Search/Fetch Tinyfish. Probe jaringan dan operasi layanan tetap tindakan terpisah. Jangan menempel token/key ke chat atau repo. Bila layanan meminta key, endpoint atau login ulang, siapkan melalui mekanisme rahasia/autentikasi yang didukung untuk akun Anda. BrightData memerlukan akun dan API key sendiri; jika belum disiapkan atau tidak diperlukan, biarkan nonaktif. Gunakan hasil pemeriksaan mesin Anda sendiri, bukan status instalasi orang lain.

## Business Sage sebagai alur kerja perangkat lunak

Gunakan Business Sage untuk menyusun pertanyaan, daftar asumsi, dan analisis yang dapat ditelusuri. Untuk usaha layanan API, contoh briefnya: “Susun lembar asumsi dengan jumlah pelanggan, pemakaian layanan, biaya dukungan, dan batas paket. Tandai angka yang belum diketahui; jangan mengarang saldo provider.” Simpan angka nyata di file privat dan minta Shizuka membawa hasil Val/Coder ke penjelasan yang mudah diperiksa.

Periksa katalog dahulu:

~~~powershell
msshi choices business-sage
msshi choices cli-anything-business-sage
~~~

Business Sage mempunyai harness terminal terpisah, cli-anything-business-sage/bsage, jika dipasang. Namanya bukan subcommand msshi. Gunakan --help dan status harness yang tersedia untuk menemukan sintaksnya, lalu bedakan kalkulasi deterministik dari penalaran agen. Modul penggunaan software ini tidak memverifikasi aturan pajak, menilai kelayakan investasi, atau memberi jaminan keuntungan. Untuk keluaran regulasi, angka pasar, atau kebijakan provider, gunakan sumber resmi yang masih berlaku pada saat keputusan dibuat.

## Lima praktikum bertahap

Semua contoh berikut adalah instruksi latihan, bukan laporan bahwa command sudah dijalankan saat modul ditulis. Ganti path dengan folder latihan milik sendiri. Jangan jalankan install, render, atau model berat hanya untuk membaca modul. Gunakan nama output baru; bila file sudah ada, pilih nama revisi baru atau periksa dahulu.

### Praktikum 1 - Membaca kesiapan sebelum meminta pekerjaan

**Tujuan:** memahami perbedaan katalog, skill terpasang, rute, dan operasi.

**Input:** instalasi MSSHI lokal dan nama profil yang akan dipakai.

**Prompt:** “Shizuka, jelaskan kesiapan Blender dan Lightcraft pada profil kiki-chii; cukup baca status profil tersebut. Baca status saja; jangan buka aplikasi atau menjalankan render. Pisahkan yang terdaftar, tersedia, dan belum diuji.”

~~~powershell
msshi choices rea
msshi choices --kind packs
msshi connect --status --hermes-home "C:\HermesClient" --profile kiki-chii
~~~

**Hasil yang diharapkan:** penjelasan fungsi REA dan paket; daftar rute profil beserta readiness/registered. Tidak ada proyek atau MP4 yang dibuat. Jika CLI tidak ditemukan, kembali ke bab instalasi; jangan memperbaiki model/provider untuk masalah PATH.

**Checkpoint:** dapatkah Anda menunjuk satu bukti bahwa rute tersedia dan satu hal yang masih belum dibuktikan? Tulis dua kalimat tersebut di catatan latihan.

### Praktikum 2 - Val mengekstrak data dari HTML lokal

**Tujuan:** mendapatkan JSON yang dapat diperiksa tanpa membuka situs.

**Input:** file C:\MSSHI-Latihan\saved.html dengan isi berikut; folder output sudah ada. Runtime Scrapling harus sudah siap.

~~~html
<html><body>
<article class="product"><h2>Buku Latihan</h2></article>
<article class="product"><h2>Kamera Contoh</h2></article>
</body></html>
~~~

**Prompt:** “Val, ekstrak hanya teks judul produk dari file ini dengan CSS. Simpan JSON baru, periksa apakah dua judul terbaca, dan laporkan batas ekstraksinya.”

~~~powershell
msshi scrapling --hermes-home "C:\HermesClient" status --verify
msshi scrapling --hermes-home "C:\HermesClient" parse --input "C:\MSSHI-Latihan\saved.html" --output "C:\MSSHI-Latihan\titles-new.json" --css '.product h2::text' --limit 10
~~~

**Hasil yang diharapkan:** JSON baru memuat Buku Latihan dan Kamera Contoh, dengan metadata jumlah/truncation yang dapat diperiksa. Jika dependency belum siap, berhenti pada status lalu gunakan prosedur instalasi eksplisit; parse tidak otomatis memasang runtime.

**Checkpoint:** bandingkan hasil dengan HTML asli. Ubah selector pada salinan latihan menjadi selector yang tidak cocok; apakah hasil kosong berarti command rusak, atau input/selector yang perlu diperiksa?

### Praktikum 3 - Kiki membuat dasar proyek video

**Tujuan:** memisahkan inisialisasi dokumen, keputusan kreatif, dan ekspor.

**Input:** folder proyek contoh yang benar-benar ada, misalnya C:\MSSHI-Latihan\MyApp, serta satu paragraf tentang fungsi aplikasinya. Jangan memakai proyek pelanggan atau rahasia untuk latihan.

**Prompt:** “Kiki, rancang video peluncuran 20 detik dari proyek contoh ini. Berikan tiga konsep dahulu. Setelah aku memilih, lanjutkan storyboard dan rough composition yang dapat diedit. Jangan membuat klaim fitur yang belum ada.”

~~~powershell
msshi brag doctor
msshi brag init --project "C:\MSSHI-Latihan\MyApp" --output "C:\MSSHI-Latihan\MyApp\brag-latihan-new" --title "MyApp Latihan"
~~~

**Hasil yang diharapkan:** CONCEPT.md, REVIEW.md, request.json. Tidak ada MP4 hanya dari init. Pengguna memilih konsep; Kiki kemudian menyiapkan source komposisi dengan alat yang tersedia. Tahap check/render baru layak setelah komposisi dan preview yang sesuai tersedia.

**Checkpoint:** dapatkah Anda menemukan sumber yang dapat diedit dan catatan persetujuan? Jika yang tersedia hanya MP4, proyek belum memenuhi tujuan “mudah diedit” secara penuh.

### Praktikum 4 - Shikaku memeriksa artefak sendiri secara statis

**Tujuan:** memahami REA opsional tanpa mengeksekusi target.

**Input:** direktori C:\MSSHI-Latihan\owned-js berisi file JavaScript latihan milik sendiri, misalnya export function add(a, b) { return a + b; }. REA wrapper dan runtime sudah dipasang secara eksplisit.

**Prompt:** “Shikaku, analisis statis direktori latihan ini. Jangan jalankan aplikasinya. Simpan laporan baru di luar input; jelaskan modul yang terlihat, bukti, dan apa yang belum dapat disimpulkan.”

~~~powershell
msshi optional list
msshi rea --hermes-home "C:\HermesClient" status
msshi rea --hermes-home "C:\HermesClient" javascript "C:\MSSHI-Latihan\owned-js" --output "C:\MSSHI-Latihan\owned-js-report-new.json"
~~~

**Hasil yang diharapkan:** laporan JSON dan diagnostik operasi. Pemeriksaan ini tidak membuat native engine menjadi tersedia, tidak menjalankan aplikasi, dan tidak mengubah kode. Pada mesin publik yang belum memilih REA, cukup baca list/status dan ikuti bab opsi bila kemampuan ini memang diperlukan.

**Checkpoint:** bedakan “fungsi add ditemukan” dari “seluruh perilaku aplikasi sudah dipahami”. Tuliskan keterbatasan input dan analisis, bukan hanya kata sukses.

### Praktikum 5 - Val dan Coder menyusun eksperimen yang dapat dinilai

**Tujuan:** membuat proposal perbaikan alur kerja tanpa mengubah bot aktif.

**Input:** satu hipotesis sempit, misalnya “format hasil tool yang lebih singkat membantu agen membaca hasil tanpa kehilangan field penting”. Siapkan baseline, tugas contoh, dan kriteria penilaian sebelum menguji model.

**Prompt:** “Val dan Shikaku, buat proposal baseline/probe/holdout untuk hipotesis ini. Pakai salinan eksperimen, pisahkan fakta dan dugaan, dan berikan rencana rollback. Jangan ganti prompt, memory, model atau plugin bot aktif.”

~~~powershell
msshi harness2 --hermes-home "C:\HermesClient" plan --goal "Uji hasil tool ringkas tanpa kehilangan field; gunakan baseline, probe, holdout, dan rollback"
~~~

**Hasil yang diharapkan:** proposal JSON, bukan hasil benchmark. Plan dapat dibaca tanpa menjalankan LLM atau mengaktifkan framework eksperimen. Bila runtime telah siap dan pengguna ingin mempelajari demo deterministik, baca action demo pada referensi command; hasil demo tetap tidak otomatis dipromosikan ke Hermes.

**Checkpoint:** apakah rencana memuat ukuran keberhasilan, contoh gagal, biaya bila ada, batas perubahan, dan cara kembali? Jika belum, proposal perlu diperjelas sebelum eksperimen.

## Serah terima dan kesiapan penggunaan klien

Sebelum mulai bekerja, pastikan catatan setup menyebut root Hermes, nama dan ID profil, versi MSSHI/commit, lokasi proyek, serta fitur yang dipilih. Catat juga siapa yang mengelola akun layanan, fitur mana yang masih memerlukan login/runtime, dan tempat menyimpan cadangan. Gunakan akun serta rahasia milik pengguna yang berhak; jangan menyalin config.yaml, token, persona pribadi, sampel suara, atau proyek pelanggan ke repo publik.

| Catatan serah terima | Yang perlu Anda ketahui |
| --- | --- |
| Agen dan profil | Bot mana untuk diskusi, riset, kreatif, atau coding; apakah memakai Solo atau tim. |
| Alat yang dipilih | Nama aplikasi/runtime yang sudah disiapkan dan fitur opsional yang sengaja dilewati. |
| Bukti operasi | Contoh tugas kecil yang benar-benar diperiksa pada mesin ini, tanggal, dan batas uji. |
| Akun dan biaya | Pemilik akun, kebutuhan login, serta batas pemakaian yang disepakati; rahasia disimpan terpisah. |
| Penyimpanan | Folder proyek, output, master yang dapat diedit, dan cadangan/receipt. |
| Bantuan berikutnya | Informasi error yang perlu disertakan dan jalur dukungan yang disepakati. |

Versi suite 3.1.1, commit source, versi aplikasi, versi runtime, dan versi model lokal adalah hal berbeda. Baca versi yang dilaporkan tiap komponen. Mengupdate petunjuk skill tidak selalu memperbarui bobot model atau package npm/pip; source cache juga tidak berarti runtime aktif. Pertahankan salinan yang dikustomisasi dan gunakan receipt yang sesuai lingkup ketika melakukan pemulihan. Daftar fitur publik merupakan pilihan kemampuan, bukan pernyataan semuanya sudah aktif pada setiap komputer klien.

Untuk tugas pertama, pilih satu keluaran kecil yang jelas: ringkasan satu sumber, ekstraksi dua judul HTML, audit satu layar, atau scaffold video pendek. Periksa hasil sebelum memperluas ke banyak sumber, model besar, atau film panjang. Setelah itu catat satu pola brief yang berhasil agar dapat digunakan kembali.

Jika tugas macet, simpan command, direktori kerja, profil, pesan error, waktu, dan lokasi output yang diharapkan. Lakukan status/help yang relevan dahulu. Jangan membayar chat berulang hanya untuk menemukan executable yang tidak ada, dan jangan menghapus library aplikasi yang sedang dipakai. Masalah Hermes Desktop, akun layanan, dependency parser, serta mutu video harus dipisahkan agar perbaikannya tepat. Sampaikan status yang benar-benar diperiksa, beserta hal yang masih perlu disiapkan.

## KAT opsional untuk Coder: dari pilihan ke konfigurasi nyata

KAT adalah helper delegasi khusus profil Shikaku. Model utama Coder, pengaturan delegasi biasa, dan MoA yang sudah dipilih pengguna tetap dipertahankan. Goose adalah agen CLI eksternal tersendiri; jangan menulis `goose` sebagai ID model MoA. Kehadiran binary Goose juga belum membuktikan provider, tool, workspace dan anggarannya sudah siap.

```powershell
msshi coder --home "C:\HermesClient" status
msshi coder --home "C:\HermesClient" presets
msshi coder --home "C:\HermesClient" wizard
```

`status` dan `presets` membaca keadaan/pilihan tanpa inferensi. Wizard meminta pilihan dan, bila diperlukan, key melalui input tersembunyi; jangan menaruh key pada argumen terminal atau chat. Pilihan terminal lama light/ideal/cloud menuju wizard yang sama, tanpa unduhan bobot. Bila memakai helper dalam terminal noninteraktif, status persiapan dapat tetap pending sampai kredensial dan endpoint disiapkan.

| Pilihan | Endpoint / model | Prasyarat dan batas |
| --- | --- | --- |
| Exact Dev | `Kwaipilot/KAT-Coder-V2.5-Dev`; URL dari deployment yang benar-benar melayaninya | Model terbuka 35B total/3B aktif. Halaman HF yang ditinjau belum menyediakan Inference Provider publik; URL localhost contoh adalah server milik pengguna |
| StreamLake PAYG resmi | Base `https://vanchin.streamlake.ai/api/gateway/v1/endpoints`, model `kat-coder-pro-v2.5` | Pro v2.5 adalah varian berbeda, membutuhkan akun/key dan penagihan StreamLake sendiri |
| Custom | Endpoint OpenAI-compatible yang dipilih pengguna, ID model sesuai katalog | HTTPS di luar localhost, tanpa key tertanam pada URL; verifikasi ID dan hak akun |

Jumlah parameter aktif tidak sama dengan ukuran bobot yang harus disimpan. Tidak ada janji model Dev muat pada RAM 16 GB/RTX 3050; unduhan model besar, penyewaan GPU dan deployment berbayar memerlukan keputusan tersendiri. Tidak ada endpoint atau saldo yang diciptakan oleh installer.

Untuk menyiapkan preset resmi tanpa mengaktifkannya:

```powershell
msshi coder --home "C:\HermesClient" configure --preset streamlake-payg
```

Untuk akun yang sudah memiliki key StreamLake, pengguna dapat menambahkan key lewat prompt rahasia dan mengaktifkan konfigurasi setelah menerima ID model resmi:

```powershell
msshi coder --home "C:\HermesClient" configure --preset streamlake-payg --read-key --probe --accept-documented-model --activate
```

`--probe` hanya melakukan GET katalog `/models`, bukan chat/completion. `--accept-documented-model` khusus menerima ID preset StreamLake yang didokumentasikan; opsi ini tidak menguji inferensi maupun membuktikan saldo akun. Pada endpoint Dev/custom, model harus ditemukan pada katalog yang benar. Konfigurasi disimpan di `msshi-private/coder/kat.json`, dengan referensi key `MSSHI_KAT_API_KEY`; bila pengguna memasukkan key melalui wizard, nilainya tersimpan pada `.env` privat Coder beserta cadangan perubahan sebelumnya.

| Status yang mungkin | Tindakan berikut |
| --- | --- |
| `needs_endpoint` | Pilih deployment nyata atau preset resmi yang sesuai varian |
| `needs_api_key` | Siapkan key akun yang benar melalui input rahasia |
| `needs_model_catalog` | Periksa ID pada katalog; jangan menebak nama model |
| `needs_native_team_routing` | Pastikan plugin dan backend native Coder telah dimuat |
| `prepared_not_enabled` | Konfigurasi disimpan tetapi belum diminta aktif |
| `configured_not_inference_tested` | Prasyarat rute terpenuhi; pemanggilan model nyata belum diuji |

Setelah konfigurasi siap, mulai sesi Shikaku baru. Hanya sesi Shikaku yang memenuhi syarat mendapat pilihan eksekusi KAT; named-profile delegation dari bot lain tetap memakai model utama Shikaku. Permintaan inferensi KAT kemudian dapat memakai biaya provider. Pengguna dapat menonaktifkan helper tanpa mengganti model utama:

```powershell
msshi coder --home "C:\HermesClient" disable
```

Rujukan endpoint/model: [model card resmi KAT Dev](https://huggingface.co/Kwaipilot/KAT-Coder-V2.5-Dev) dan [integrasi API resmi StreamLake](https://www.streamlake.ai/document/DOC/mg6k6nlp8j6qxicx4c9). Ketersediaan layanan dapat berubah; periksa katalog serta ketentuan akun saat benar-benar digunakan.

## Karier, engineering, dan bedah video sesuai konteks

Empat wrapper baru bekerja menurut topik. Mereka tidak menjalankan job scan, memasang model, membuka aplikasi atau mengirim lowongan saat Hermes boot. Indeks metadata skill tetap dapat memakai konteks host; istilah on-demand tidak menjamin seluruh tagihan menjadi nol.

| Skill | Penerima | Contoh permintaan |
| --- | --- | --- |
| career-ops | Kelima bot | Cocokkan CV milikku dengan JD ini, jelaskan skor dan kekurangan bukti |
| remote-jobs | Kelima bot | Saring perusahaan remote Python, lalu tandai posisi aktif yang belum diverifikasi |
| mattpocock-engineering | Kelima bot sesuai bidang | Susun diagnosis/TDD/spesifikasi sebelum implementasi |
| harness2 | Kelima bot | Buat proposal pembanding alur kerja dengan baseline dan holdout |
| rea-video | Kiki-Chii | Bedah referensi video ini per shot dan susun rencana remake yang dapat diedit |

Baca status tanpa jaringan:

```powershell
msshi integrations source --home "C:\HermesClient" --name career-ops
msshi integrations source --home "C:\HermesClient" --name remote-jobs
msshi integrations source --home "C:\HermesClient" --name mattpocock-skills
msshi integrations source --home "C:\HermesClient" --name rea-video
```

Source dipin dan disimpan di `msshi-private/context-sources`, di luar scanner. Ambil hanya yang diperlukan:

```powershell
msshi integrations source --home "C:\HermesClient" --name remote-jobs --fetch
msshi integrations source --home "C:\HermesClient" --name remote-jobs --query python --limit 5
msshi integrations source --home "C:\HermesClient" --name mattpocock-skills --fetch
msshi integrations source --home "C:\HermesClient" --name mattpocock-skills --list
msshi integrations source --home "C:\HermesClient" --name mattpocock-skills --skill tdd
```

Fetch memerlukan internet/disk, memeriksa hash blob Git serta SHA-256 cache, dan tidak memasang dependency. Query/list/read berikutnya memakai cache lokal. Hasil Remote In Tech merupakan direktori perusahaan, bukan bukti lowongan masih aktif, boleh remote dari negara pengguna, atau menerima tingkat pengalaman tertentu. Val dapat memeriksa laman karier resmi ketika tugas browsing diizinkan.

CareerOps perlu source workflow lengkap, AGENTS.md dan mode yang dipilih. Data CV, profil dan tracker ditempatkan privat di `msshi-private/career-ops-data`, bukan repo publik/cache source. Status menunjukkan `CAREER_OPS_DATA_DIR`; gunakan environment itu hanya untuk proses CareerOps. Jangan memakai CV/profil contoh sebagai fakta pengguna. Tugas outreach/aplikasi menghasilkan draf untuk ditinjau; instalasi tidak mengizinkan mengirim pesan atau menekan Submit.

```powershell
msshi integrations source --home "C:\HermesClient" --name career-ops --fetch
msshi integrations source --home "C:\HermesClient" --name career-ops --install-runtime
```

Pemasangan runtime CareerOps memerlukan Node sesuai upstream, memakai `npm ci --ignore-scripts`, serta melewati unduhan Chromium. Runtime siap bukan berarti CV/akun/browser sudah siap. Pisahkan tugas menilai CV, mencari lowongan dan mengirim aplikasi.

Matt Pocock memakai frontmatter upstream `disable-model-invocation`. TDD, diagnosis dan domain-modeling dapat dibaca sesuai konteks; orkestrator seperti grill-me/to-spec dan publikasi issue hanya dipakai bila pengguna meminta. Daftar menampilkan `explicit_only` dan `in_progress`; bahan in-progress perlu dipilih dengan sadar. Nama slash upstream belum tentu didaftarkan host, sehingga pada Hermes mintalah workflow melalui percakapan atau source reader.

rea-video berbeda dari REA milik morluto: rea-video membedah video, sedangkan REA opsional Coder menganalisis artefak aplikasi. Pemasangan rea-video merupakan runtime Python privat, bukan pemasangan engine REA Coder.

```powershell
msshi integrations source --home "C:\HermesClient" --name rea-video --fetch
msshi integrations source --home "C:\HermesClient" --name rea-video --install-runtime
```

Status menyebut interpreter dan flag lokal ringan yang benar. Jalankan binary `rea-video` dari venv yang dilaporkan, bukan nama executable yang kebetulan berada di PATH lain. Contoh tahap lokal tanpa fitur model:

```text
rea-video decompose INPUT.mp4 -o OUTPUT_BARU --no-vlm --no-whole --no-ocr --no-packaging --no-asr --no-speakers --no-stems --workers 1 --lang en
rea-video summary OUTPUT_BARU/breakdown.json
```

INPUT dan OUTPUT_BARU harus diganti; FFmpeg/ffprobe serta input yang sesuai tetap diperlukan. Tanpa flag penonaktifan, default upstream dapat mengunduh model pemisahan suara. OCR/ASR, stem, VLM dan generasi ulang adalah pilihan terpisah; mereka tidak otomatis dipanggil dari wrapper. Pin menyediakan bahasa laporan zh/en, bukan flag `--lang id`. Baca VIDEO.md kemudian shot relevan agar konteks tidak dipenuhi JSON besar. Kiki meninjau ketidakpastian analisis sebelum mengubahnya menjadi brief produksi.

## Praktikum tambahan untuk rilis 3.1.1

### Praktikum 6 — Cek KAT tanpa inferensi

**Tujuan:** memahami perbedaan pilihan model, endpoint dan aktivasi. **Input:** profil Shikaku yang sudah ada; key tidak diperlukan untuk membaca status/preset.

```powershell
msshi coder --home "C:\HermesClient" status
msshi coder --home "C:\HermesClient" presets
```

**Hasil yang diharapkan:** pilihan preset dan status prasyarat, tanpa POST inferensi atau unduhan bobot. Catat apakah model yang dituju Dev atau Pro. **Checkpoint:** dapatkah Anda menjelaskan mengapa adanya URL API tidak sama dengan akun bersaldo atau inference yang sudah berhasil? Jangan mengaktifkan akun berbayar hanya untuk menyelesaikan latihan.

### Praktikum 7 — Cari direktori remote dari cache

**Tujuan:** membaca sumber terpin tanpa mengklaim lowongan aktif. **Input:** cache remote-jobs yang sudah dipilih/diambil. Fetch awal memerlukan jaringan, query selanjutnya lokal.

```powershell
msshi integrations source --home "C:\HermesClient" --name remote-jobs --query python --limit 3
```

**Hasil yang diharapkan:** maksimal tiga direktori cocok beserta `active_job_verified: false`, atau hasil kosong yang sah. **Checkpoint:** tulis data tambahan yang diperlukan sebelum melamar: posisi aktif, lokasi, hak kerja, waktu, senioritas dan kecocokan CV. Tidak ada aplikasi yang dikirim.

### Praktikum 8 — Kerangka Word skripsi tanpa membuka aplikasi

**Tujuan:** merakit kerangka dokumen yang dapat diedit, terpisah dari penulisan/penilaian ilmiah. **Input:** folder output baru dan Python dengan `python-docx`/`lxml` yang sesuai. Gunakan bahan latihan sendiri; pedoman kampus sebenarnya diperiksa terpisah.

```powershell
msshi doctor --json
msshi skripsi --preset informatika_ilkom --out "C:\MSSHI-Latihan\Template-Latihan-Baru.docx" --no-online --no-open --non-interactive
```

`--no-online` melewati pencarian logo/pejabat/pedoman; `--no-open` menahan pembukaan Word. Default helper tanpa flag itu dapat memakai lookup online dan membuka hasil pada sesi Windows interaktif. `--install-deps` adalah pilihan unduhan terpisah bila dependency belum ada. Periksa nama file baru sebelum menjalankan; hasil Word perlu ditinjau identitas, pedoman, section, halaman dan placeholder. Dokumen kerangka belum membuktikan isi skripsi benar atau disetujui kampus.

## Sumber utama bab praktik

Bab ini membaca source publik MSSHI pada commit 84ecd134f01ec65c4848b4f50c597b811f6b3a80, bukan mengeksekusi operasi latihan. Referensi fungsi dan batasnya: docs/ALUR_PRESET_MUZA.md, docs/V3_1_UPDATE.md, docs/BRAG.md, docs/SCRAPLING.md, docs/HARNESS2.md, docs/TIMESFM.md, docs/REA.md, docs/UNSLOP.md, docs/CLI_ANYTHING_BRIDGE.md, docs/STEEL_BROWSER_POLICY.md, docs/SERVICE_CONNECTIONS.md, docs/CONTEXTUAL_INTEGRATIONS.md, hermes_plugins/msshi-team-routing/README.md, serta parser helper terkait.

Halaman sumber versi tetap: https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/tree/84ecd134f01ec65c4848b4f50c597b811f6b3a80 . Beberapa halaman integrasi/skill lama masih memakai hitungan v3.0 atau istilah MCP desktop. Untuk modul ini, jumlah 67 skill standar/52 sumber mengikuti VERSION.json terbaru; eksekusi aplikasi desktop mengikuti dispatcher CLI v3, bukan contoh legacy.


# 7. Operasional, pembaruan, dan pemecahan masalah

Bab ini merupakan panduan operasional untuk pelanggan MSSHI v3.1.1, berdasarkan source publik pada commit `84ecd134f01ec65c4848b4f50c597b811f6b3a80`. Semua path `C:\HermesClient` adalah contoh yang harus diganti dengan root instalasi pelanggan. Contoh tidak menyatakan bahwa aplikasi, model, atau akun pelanggan sudah terpasang maupun terhubung. Penyusunan modul tidak menjalankan perbaikan, model, render, atau operasi akun pelanggan.

## Kenali jenis pemeriksaan sebelum menekan Enter

**Tanpa kredit LLM** berarti tidak ada permintaan inferensi ke model berbayar. Istilah itu tidak selalu berarti tanpa jaringan, tanpa penulisan file, tanpa proses, atau tanpa biaya layanan lain. Contohnya, `msshi check` membaca GitHub, `msshi desktop --check-only` mempersiapkan gateway lokal, dan probe layanan menghubungi server MCP. Memasang runtime juga dapat mengunduh dependency, memakai disk, serta menjalankan proses instalasi walaupun tidak memanggil model.

Gunakan urutan diagnosis berikut:

1. Baca bantuan fungsi: `msshi choices <id>` atau `msshi <keluarga> --help`.
2. Periksa konfigurasi dan metadata melalui perintah status yang relevan.
3. Periksa log, receipt, hasil uji terdahulu, dan ruang perangkat.
4. Bila bukti tersebut belum cukup, rencanakan satu uji operasi kecil dengan input, keluaran, dan batas biaya yang jelas.
5. Ulangi uji hanya sesudah perubahan atau kegagalan yang memang perlu diverifikasi.

| Pemeriksaan | Yang dilakukan | Yang belum dibuktikan |
| --- | --- | --- |
| `msshi choices rea` | Membaca penjelasan fungsi/prasyarat | REA sudah aktif atau runtime terpasang |
| `msshi connect --status` | Membaca registrasi dan deteksi rute | Operasi aplikasi atau login layanan berhasil |
| `msshi runtime status --home "C:\HermesClient"` | Memeriksa kebijakan, rute, dan preservasi setting yang dilacak | Setiap proyek dapat dijalankan |
| `msshi audit --home "C:\HermesClient"` | Memeriksa paket/profil dan bukti operasi yang tersimpan | Menjalankan ulang semua operasi atau mengautentikasi akun saat ini |
| `msshi browser --status --hermes-home "C:\HermesClient"` | Membaca kesiapan konfigurasi dan keberadaan kredensial | Sesi Steel cloud nyata berhasil |
| `msshi services status --hermes-home "C:\HermesClient"` | Membaca konfigurasi layanan dan cache lokal | Token masih valid untuk operasi sekarang |
| `msshi desktop --check-only --hermes-home "C:\HermesClient"` | Menyiapkan gateway dan memeriksa kesiapan launcher Windows | Tes render UI atau percakapan model |

`PASS_SUCCESS` harus dibaca bersama scope dan bukti. Contoh hasil sintetis satu detik membuktikan jalur video dapat dieksekusi dalam kondisi uji itu; hasil tersebut belum mengukur kualitas film produksi atau keberhasilan render empat puluh menit.

## Rutinitas sesi pertama dan pemeriksaan berkala

Untuk sesi pertama pada instalasi yang sudah ada, buka PowerShell dan jalankan:

```powershell
Get-Command msshi
msshi choices --kind modes
msshi runtime status --home "C:\HermesClient"
msshi connect --status --hermes-home "C:\HermesClient" --profile default
msshi managed status
```

`Get-Command` menunjukkan launcher yang benar-benar ditemukan pada PATH. Perintah berikutnya menjelaskan pilihan dan membaca keadaan instalasi. Catat target yang `available`, yang baru `configured`, yang `disabled`, dan yang memerlukan setup. Bila tujuannya Kiki-Chii, ulangi status koneksi dengan `--profile kiki-chii`. Jangan menjalankan `setup` lagi hanya karena ingin memakai skill yang sudah terpasang.

Pada awal proyek, tulis folder input, folder keluaran baru, bot/peran yang dipakai, alat yang diperlukan, serta tahap yang harus ditinjau. Jalankan status/doctor milik alat itu saja. Untuk BRAG, misalnya, mulai dari `msshi brag doctor`; jangan memasang semua runtime penelitian ketika tugasnya hanya menyunting satu video.

Sekali dalam periode pemeliharaan yang Anda pilih, periksa `msshi check`, `msshi managed status`, kapasitas disk, serta log kegagalan terbaru. `msshi check` memakai jaringan untuk membandingkan versi/changelog GitHub. Lakukan update saat tidak ada render atau pekerjaan tulis aktif yang bergantung pada skill yang akan diganti. Setelah update, baca ringkasan cadangan dan ulangi status/tes kecil hanya pada bagian yang berubah. Tidak perlu mengirim chat model hanya untuk memastikan file instruksi masih ada.

## Bedakan paket, skill, runtime, model, dan cache

| Lapisan | Contoh | Cara memperbarui atau menambah |
| --- | --- | --- |
| Source MSSHI | Checkout Git, README, installer, kode CLI | `msshi update` mengambil GitHub `main` |
| Instruksi skill terkelola | Folder `SKILL.md` beserta referensi/helper ringan | Updater memperbarui target terdaftar jika fingerprint sesuai |
| Skill kustom/pihak ketiga | Hasil edit pengguna atau sumber yang belum terbukti | Dipertahankan; tinjau dan kelola sesuai asalnya |
| Cache upstream | Checkout referensi di luar scanner | Fetch sumber sesuai manifest; bukan aktivasi seluruh fiturnya |
| Runtime | venv Python, dependency npm, interpreter khusus | Ikuti installer/status integrasi terkait |
| Bobot model | TimesFM, OmniVoice | Unduhan dan setup khusus; tidak menjadi isi folder skill |
| Akun/kredensial | Steel, GitLab, Tinyfish | Login/secret lokal yang dikelola layanan/host |
| Proyek pengguna | HTML komposisi, data penelitian, source aplikasi | Simpan dalam workspace proyek, terpisah dari source paket |

`msshi update` bukan jaminan seluruh package npm/pip atau aplikasi desktop sudah paling baru. Tanpa `--skip-upstreams`, update juga mencoba cache sumber dan integrasi curated yang didukung. Fetch Git sendiri tidak menjalankan semua kode upstream, memasang semua dependency, mengunduh semua bobot, atau mengisi semua akun. Status setiap integrasi tetap diperiksa secara terpisah.

Pemasangan lama dapat didaftarkan dengan:

```powershell
msshi managed register --skills-dir "PATH_TO_SKILLS" --apply
msshi managed status
```

`PATH_TO_SKILLS` adalah placeholder folder skill yang benar-benar ingin dikelola. Opsi `--baseline PATH_RILIS_LAMA_YANG_DITINJAU` dapat membuktikan salinan rilis lama. Jangan memilih baseline agar memaksa menimpa edit yang masih diperlukan. Hasil `custom_or_unproven` berarti asal/isi belum cocok, bukan berarti file rusak. Hasil `custom_preserved` berarti edit lokal dipertahankan.

Junction yang didaftarkan secara eksplisit menyimpan tujuan fisiknya. Target bersama diperbarui sekali. Bila junction berubah arah, updater memblokir perubahan untuk ditinjau. Jangan membetulkannya dengan recursive delete atau membuat junction baru secara coba-coba.

## Pastikan versi dan source yang benar-benar dipakai

Versi paket edisi ini adalah 3.1.1, berdasarkan commit implementasi `84ecd134f01ec65c4848b4f50c597b811f6b3a80`. Nomor versi, commit checkout Git, snapshot CLI global, dependency aplikasi, dan bobot model merupakan identitas yang berbeda. Perubahan pada folder pengembangan belum tentu dipakai launcher global sampai instalasi/update menerapkannya.

```powershell
msshi status
Get-Command msshi
```

`msshi status` memakai jalur pemeriksaan versi yang sama dengan `check` dan membutuhkan GitHub. Untuk memeriksa source lokal tanpa jaringan, jika checkout Anda berada di contoh lokasi ini:

```powershell
Get-Content -LiteralPath "C:\HermesClient\msshi-upstream\VERSION.json"
git -C "C:\HermesClient\msshi-upstream" rev-parse HEAD
```

Jangan mengharapkan `git` bekerja pada folder snapshot CLI yang tidak memiliki history Git. Untuk snapshot CLI global Windows pada lokasi default:

```powershell
$MsshiStatePath = Join-Path $env:LOCALAPPDATA 'MSSHI\state.json'
(Get-Content -LiteralPath $MsshiStatePath -Raw | ConvertFrom-Json).git_commit
```

Jika memakai `MSSHI_HOME`, baca `state.json` pada lokasi tersebut. Bandingkan `git_commit` dengan source rilis yang dituju; jangan force-push, mengganti tag historis, atau menyalin file acak ke snapshot untuk memaksa versi terlihat sama. `msshi update` memperbarui dari source yang dikonfigurasi dan mempertahankan kustomisasi terkelola sesuai fingerprint.

## Memperbarui dengan menjaga provider, model, dan persona

Tentukan home yang benar sebelum update. Simpan cadangan privat konfigurasi, `SOUL.md`, Creative DNA, dan `state.json` updater sesuai kebutuhan. File konfigurasi dapat mengandung data pribadi; jangan memasukkannya ke repo publik atau melampirkannya mentah ke percakapan umum. Hash dapat dipakai untuk membandingkan file tanpa menampilkan isi rahasianya.

```powershell
msshi managed status
msshi update --hermes-home "C:\HermesClient" --skip-upstreams
msshi runtime status --home "C:\HermesClient"
msshi audit --home "C:\HermesClient"
```

Contoh tersebut melakukan update nyata, bukan dry-run. `--skip-upstreams` menghindari fetch sumber eksternal, tetapi tetap memperbarui paket/skill terkelola dan dapat menjalankan migrasi runtime profil. Bila memang membutuhkan pembaruan sumber tambahan, gunakan `msshi update --hermes-home "C:\HermesClient"` tanpa flag itu setelah meninjau internet, disk, serta integrasi yang terlibat.

Pemeriksaan preservasi MSSHI melindungi nilai LLM yang dilacak serta mempertahankan kustomisasi. Baca scope audit instalasi Anda: pemeriksaan tersebut tidak berarti seluruh isi disk telah diaudit. Bila diperlukan, simpan hash file konfigurasi sebelum update dan cocokkan sesudahnya. Bila Anda sengaja mengubah model sendiri, jangan “memperbaiki” mismatch baseline dengan mengembalikan model tanpa meninjau perubahan tersebut.

Hersona merupakan jalur katalog dan draf persona. Ia tidak mengganti `SOUL.md` secara otomatis setiap kali bot membalas. Llmtrim juga tidak memerlukan perubahan provider/proxy untuk bisa tersedia. Jangan menjalankan setup proxy atau memindahkan provider hanya untuk mengatasi persoalan help, PATH, ataupun discovery skill.

## Cadangan dan rollback: pilih receipt yang tepat

Tidak ada satu perintah yang mengembalikan seluruh laptop. Bedakan backup skill, metadata updater, receipt migrasi runtime, receipt browser Steel, cache OAuth, dan proyek pengguna. Selalu baca tujuan dan struktur receipt sebelum memulihkan.

| Yang ingin dipulihkan | Bahan yang digunakan | Batasnya |
| --- | --- | --- |
| Satu skill yang baru diperbarui | `.msshi-backup-*` dari update dan snapshot state terkait | Pulihkan ke target fisik yang sama; pertahankan junction |
| Pencatatan updater | Salinan `state.json` sebelum perubahan | Tidak otomatis mengembalikan isi skill/runtime |
| Perubahan migrasi runtime | Receipt dengan `home` dan daftar `changes` | Hanya perubahan yang dicatat receipt itu |
| Kebijakan Steel | Receipt ber-purpose `Strict Steel browser policy`, berisi `entries` | Gunakan rollback browser, bukan rollback runtime |
| OAuth layanan web | Receipt layanan dan cache asli privat | Pemulihan identitas/junction perlu peninjauan; jangan menghapus cache canonical |

Sintaks runtime yang benar:

```powershell
msshi runtime rollback "PATH_RECEIPT_RUNTIME\receipt.json" --home "C:\HermesClient"
```

Receipt harus berada di bawah `C:\HermesClient\msshi-runtime\backups` dan mencatat home yang sama. Implementasi memeriksa hash hasil pemasangan sebelum memulihkan tiap file. File yang berubah lagi dapat dilewati. Karena itu, baca jumlah `restored` dan cocokkan dengan daftar perubahan; exit code saja belum membuktikan seluruh isi dipulihkan.

Sintaks khusus Steel:

```powershell
msshi browser --rollback "PATH_RECEIPT_STEEL\receipt.json" --hermes-home "PATH_PROFIL"
```

Gunakan direktori profil yang menghasilkan receipt tersebut. Rollback Steel menolak file yang telah dikustomisasi setelah pemasangan. Reload/restart plugin melalui mekanisme Hermes sesudah pemulihan.

**Jangan langsung memakai `rollback_receipt` terbaru tanpa membaca jenisnya.** Direktori backup dapat berisi receipt beberapa keluarga. Receipt Steel dengan `entries` bukan receipt runtime dengan `changes`. Untuk skill, simpan versi kini dahulu, pulihkan backup ke folder fisik yang sama, lalu selaraskan fingerprint state terkait atau biarkan hasilnya dianggap kustom sampai ditinjau. Git checkout/tag lama juga tidak memulihkan database, kredensial, atau semua dependency runtime.

## Menjaga scanner skill tetap ringan

Scanner seharusnya menemukan instruksi, referensi terpilih, dan script inti. Simpan repo upstream penuh, `.git`, `node_modules`, venv, bobot model, footage, hasil render, eval dataset besar, serta cache di luar folder skill aktif. Folder `assets` kecil yang memang dibutuhkan skill tidak otomatis menjadi sampah; yang bermasalah adalah material besar atau tree dependency yang ikut dipindai berulang.

Dalam contoh struktur modul, checkout sistem ditempatkan di `C:\HermesClient\msshi-upstream`; runtime serta bukti lokal dapat berada di `C:\HermesClient\msshi-private`; hasil proyek ditempatkan di workspace tersendiri. Direktori lokal itu dibuat sesuai pemasangan dan tidak dibundel sebagai data pelanggan di repo publik. Anda boleh memilih lokasi lain dengan prinsip pemisahan yang sama. Jangan memindahkan helper yang masih dirujuk skill tanpa menyesuaikan path dan memverifikasi kembali.

Bila panel Skills timeout, baca log gateway/Desktop, cari folder berat pada profil yang tepat, lalu bandingkan dengan isi bundel. Catat path, ukuran, sumber, dan rencana tujuan sebelum memindahkan. Jangan menulis ulang `.hub/lock.json` dengan format tebakan atau menghapus semua cache tanpa mengetahui pemiliknya. Refresh/reload lewat mekanisme host setelah isi diperbaiki. Jumlah skill yang terlihat pada UI dapat berbeda dari jumlah `SKILL.md` di disk karena indeks, alias, koleksi lama, dan discovery host.

## Hermes Desktop abu-abu dan gateway belum siap

Launcher Windows MSSHI mempersiapkan gateway melalui launcher Hermes yang sudah terpasang sebelum membuka Desktop. Ia memakai mekanisme resmi pemulihan marker update dan menolak mengambil alih update yang masih aktif. Pengaturan software rendering berlaku untuk proses anak Desktop, bukan pengaturan model.

```powershell
msshi desktop --hermes-home "C:\HermesClient" --check-only
msshi desktop --hermes-home "C:\HermesClient" --software-rendering
```

Perintah pertama tidak membuka jendela Desktop, tetapi dapat menyalakan/mempersiapkan gateway. Perintah kedua membuka Desktop dengan switch resmi `HERMES_DESKTOP_DISABLE_GPU=1` pada proses anak. Launcher juga dapat membaca preferensi lokal `tools\msshi\desktop-preferences.json`. Untuk menghubungkan shortcut yang cocok dengan instalasi Windows ini, tersedia `--install-shortcut`; tindakan itu membuat cadangan shortcut dan kemudian menjalankan launcher. Jangan menambahkan flag GPU acak atau mematikan semua proses Electron/Chrome pada komputer.

Jika launcher melaporkan active/unresolved update, selesaikan update yang sah lebih dahulu. Jika gateway tidak ready, lihat `logs\gateway.log` dan `logs\desktop.log`; launcher pythonw juga mencatat `logs\msshi-desktop.log` bila dijalankan tanpa console. Nilai `--timeout` launcher dibatasi 30-600 detik, default 180 detik. Menaikkannya bukan pengganti perbaikan dependency, scanner, atau update yang gagal.

## Blender, Lightcraft, dan aplikasi yang terbuka sendiri

`registered: true` dan `readiness: available` berarti rute terdaftar dan CLI ditemukan. Aplikasi masih perlu proyek/input yang benar. Dispatcher v3 memerlukan tiket tugas sekali pakai sebelum menjalankan native CLI; memilih koneksi tidak semestinya membuka aplikasi saat Hermes boot.

```powershell
msshi connect --status --hermes-home "C:\HermesClient" --profile default
msshi connect --status --hermes-home "C:\HermesClient" --profile kiki-chii
msshi choices --kind apps
```

Blender memakai rute native dengan prefix background. Lightcraft mengelola/develop foto, crop, warna, dan ekspor; ia bukan nama alat pencahayaan generik. Setup ini tidak perlu memulihkan MCP desktop Blender/Lightcraft. Bila kartu MCP lama masih aktif atau log stdio terus memulai aplikasinya, periksa profil dan konfigurasi aktif yang sebenarnya, bukan mengaktifkan ulang konektor agar kartu berwarna hijau.

Lightcraft dapat menolak akses ketika library sedang dipakai pemilik lain. Simpan pekerjaan GUI, identifikasi sesi/library yang memakai path itu, lalu tutup pemiliknya secara normal sebelum uji CLI terarah. Jangan menghapus file lock saat proses pemilik masih hidup. Hindari mengoperasikan GUI dan CLI pada library sama secara bersamaan tanpa dukungan aplikasi. Periksa environment dan lokasi state yang dipakai adapter Anda; environment terpisah tetap tidak membuat satu library aman untuk penulisan serentak.

Pesan `stdio session recycled after idle_timeout_seconds; waiting for lazy reconnect` berasal dari lifecycle MCP dan tidak sendiri membuktikan aplikasi rusak. Pada rute native CLI, proses hanya dijalankan untuk tugas dan tidak memerlukan sesi MCP idle. Bila berpindah dari setup MCP lama, jangan menjalankan launcher engine otomatis yang sudah digantikan hanya untuk “menyambungkan kembali” Lightcraft.

## Remotion: bedakan timeout peluncuran Chrome dan timeout render

MSSHI v3.1.1 tidak menyediakan perintah global `msshi remotion`. Proyek Remotion memakai toolchain dan dependency proyeknya. Mulailah dengan komposisi satu detik, resolusi kecil, satu worker, dan file keluaran baru sebelum merender video panjang. Keberhasilan satu contoh kecil belum menjamin seluruh aset dan durasi proyek dapat diproses.

Tinjau bantuan dan script proyek untuk opsi executable browser yang didukung, misalnya `--browser-executable`, serta variabel yang benar-benar dibaca helper, misalnya `CHROME_PATH`. Timeout handshake DevTools saat Chrome diluncurkan berbeda dari timeout render sesudah browser siap. Jika proyek memerlukan perubahan batas 25 detik menjadi 90 detik, penyesuaian harus dilakukan pada launcher yang cocok dengan versi dependency dan ditinjau untuk proses proyek itu; angka tersebut bukan flag global MSSHI atau jaminan kompatibilitas lintas versi.

Jangan menganggap flag timeout render/delayRender otomatis memperpanjang handshake Chrome yang gagal sebelum browser siap. Jangan menganggap `REMOTION_CHROME_EXECUTABLE` atau `PUPPETEER_EXECUTABLE_PATH` sudah dibaca oleh setiap wrapper. Periksa script proyek dan bantuan versi terpasangnya. Setelah mengganti versi Remotion, tinjau kembali kompatibilitas penyesuaian launcher; jangan menyunting `node_modules` secara coba-coba sebagai perbaikan permanen.

Urutan diagnosis: verifikasi path Chrome, baca error peluncuran, cek ruang temp dan RAM/commit, uji komposisi sendiri yang kecil dengan satu worker, lalu periksa MP4 menggunakan metadata video. Baru setelah itu naikkan durasi atau resolusi bertahap. Jangan menyalin path helper dari komputer lain sebagai langkah instalasi; siapkan toolchain pada workspace proyek Anda sendiri.

## Sumber daya, kredit, dan lisensi

Tutup pekerjaan yang memang tidak diperlukan secara normal dan sisakan ruang disk untuk temp, browser, audio/video serta backup. Banyaknya skill berupa teks tidak sama dengan beban semua aplikasi/model sekaligus; beban terbesar muncul ketika runtime benar-benar dijalankan. Tier hardware dan pemeriksaan preflight hanya dasar penjadwalan, bukan kuota RAM sistem operasi yang keras.

BRAG, misalnya, menolak pekerjaan ketika preflight menemukan physical memory/commit/disk di bawah batas minimumnya. Lolos batas minimum tidak berarti film panjang dengan semua aset akan muat. Gunakan preview kecil, satu worker ketika sumber daya terbatas, dan simpan temp/media pada volume yang cukup. Folder runtime di drive D tidak menghilangkan seluruh kebutuhan cache sistem di C.

TokenShield/reserve US$1 bergantung pada data saldo dan estimasi yang tersedia. Batas tagihan keras harus didukung provider; jangan menganggap seluruh akun dijamin berhenti tepat pada satu dolar. Chat perencanaan tetap memakai model yang dipilih pengguna. Eksekusi CLI lokal dapat tanpa kredit LLM, tetapi layanan cloud, asset berbayar, TTS API, dan GPU eksternal mempunyai biaya masing-masing.

Llmtrim otomatis hanya menerima keluaran JSON besar yang memenuhi syarat dan lulus kesetaraan nilai. Ia tidak memadatkan seluruh percakapan/kode dan tidak menjamin persentase penghematan tagihan yang tetap. Angka 42,74% pada fixture terdahulu adalah pengurangan byte contoh JSON, bukan pengukuran seluruh token berbayar. OmniVoice lokal memerlukan bobot/runtime dan lisensi bobot yang membatasi penggunaan komersial; lisensi MIT MSSHI tidak menggantikan lisensi model, musik, font, atau aplikasi.

## Layanan eksternal: prasyarat dan pemeriksaan pelanggan

| Komponen | Prasyarat pada akun/perangkat pelanggan | Pemeriksaan sebelum tugas |
| --- | --- | --- |
| Steel | Key/endpoint kompatibel dan tugas/anggaran yang diizinkan | `msshi browser --status` membaca konfigurasi; sesi nyata diperiksa terpisah bila tugas memerlukannya |
| GitLab | OAuth/izin MCP pada akun yang tepat | `msshi services status`; login/probe sesuai profil, lalu operasi baca kecil yang diizinkan |
| Tinyfish | Login layanan, filter tool dan kuota/izin operasi | Bedakan registrasi, discovery, autentikasi dan hasil operasi; login ulang jika token kedaluwarsa |
| BrightData | Akun/key serta pemeriksaan biaya/kuota | Biarkan opsi nonaktif bila belum diperlukan atau kredensial belum tersedia |
| Google Drive | Rute GDrive/gdrive-web nonaktif dalam preset ini | Akses akun hanya melalui metode browser yang diizinkan untuk tugas; jangan mengaktifkan koneksi dari contoh lama |

GitLab dan Tinyfish tersedia menurut profil yang dipilih, termasuk default, Val dan Shizuka; registrasi dan autentikasi harus diperiksa di setiap cakupan itu. Panduan ini tidak menyatakan status akun pelanggan. Gunakan `msshi browser --status` dan `msshi services status` dengan root instalasi yang tepat untuk membaca konfigurasi sekarang. Login dilakukan sendiri pada profil yang dituju, misalnya `hermes mcp login tinyfish` setelah memastikan profil Hermes aktif benar. Identitas Google/GitLab/Tinyfish satu orang tidak boleh otomatis dipakai untuk pengguna lain. Opsi berbagi cache OAuth, bila dipilih, hanya cocok untuk profil yang sengaja memakai identitas akun sama; jangan membagikan cache pelanggan lain.

Steel merupakan jalur umum dengan guard tanpa fallback diam-diam ke Chrome ketika key belum ada. Akses akun personal pada browser pengguna memerlukan cakupan situs, akun, tujuan dan akses, lalu mekanisme persetujuan host. Pemindahan cookie/login ke Steel belum diimplementasikan; persetujuan mengakses browser personal bukan izin menyalin sesi. Jangan mengakali guard melalui terminal/Computer Use.

Periksa ketentuan dan kuota layanan sebelum operasi jaringan. Jangan menyamakan keberhasilan initialize/tools-list dengan keberhasilan Search, Fetch, atau otomasi browser. Jalur discovery, autentikasi dan operasi aktual merupakan pemeriksaan berbeda. Status lokal tanpa panggilan LLM bukan bukti bahwa seluruh penggunaan layanan akan gratis.

## Tabel pemecahan masalah

| Gejala | Pemeriksaan awal | Tindakan terarah | Tanda berhasil |
| --- | --- | --- | --- |
| `msshi` tidak dikenali | `Get-Command msshi`; periksa PATH/lokasi installer | Buka terminal baru setelah instalasi; jalankan launcher dari lokasi data user yang benar bila diperlukan | Help/choices tampil dari instalasi yang dimaksud |
| Nomor versi sama, bantuan baru belum ada | Baca commit snapshot CLI dan checkout | Jalankan update dari `main`; bedakan tag awal dengan revisi build | `msshi choices` tersedia dan commit sesuai sumber baru |
| `unrecognized arguments` | `msshi <keluarga> --help` | Gunakan flag keluarga yang benar: `--home`, `--hermes-home`, dan posisi option berbeda antar helper | Parser menerima command tanpa tindakan yang tidak dimaksud |
| Path berisi spasi/apostrof gagal | Periksa path literal dan quote PowerShell | Gunakan `"D:\Folder Saya\..."` serta call operator `&` untuk executable/script berpath | File/executable tujuan ditemukan |
| Opsi muncul tetapi tool belum jalan | Lihat status wrapper, runtime dan akun | Pasang hanya dependency yang benar-benar dibutuhkan; jangan mengulang seluruh setup | Status runtime siap, lalu satu tugas kecil menghasilkan artefak yang valid |
| `custom_preserved` atau `custom_or_unproven` | Baca diff/fingerprint dan asal salinan | Pertahankan edit; gunakan baseline yang ditinjau bila perlu | Kustomisasi tersimpan dan cakupan updater dipahami |
| Junction berubah / `blocked` | Cocokkan path logis dan fisik receipt | Hentikan update bagian itu dan tinjau target; jangan retarget sembarang | Tujuan fisik terbukti benar dan registrasi dapat diverifikasi |
| Lock update masih ada | Pastikan tidak ada operasi MSSHI yang sedang berjalan | Identifikasi pemilik/operasi dan log dahulu; jangan langsung menghapus lock | Operasi yang sah selesai atau lock stale ditangani dengan bukti |
| Panel Skills lama/timeout | Log gateway/Desktop dan tree skill | Pisahkan dependency/cache berat; refresh lewat host | Panel termuat dan skill yang diperlukan ditemukan |
| Desktop abu-abu | Gateway ready, log, dan mode rendering | Gunakan launcher MSSHI dan opsi software rendering yang didukung | Jendela menampilkan UI dan backend siap |
| Lightcraft library dipakai sesi lain | Library path serta GUI/proses pemilik | Simpan/tutup pemilik normal; coba satu tugas CLI | Library dapat dibuka dan artefak diekspor tanpa konflik |
| Aplikasi terbuka saat boot | Profil aktif, daftar MCP/plugin lama, startup aplikasi | Lepas jalur lama melalui migrasi yang ditinjau; pertahankan tiket tugas | Tidak ada aplikasi kreatif dibuka hanya karena Hermes startup |
| Tiket tidak berlaku | Target/profil/TTL/state tiket | Buat tiket baru untuk tugas nyata; satu tiket hanya satu run | Dispatcher menjalankan target yang sesuai dan mencatat hasil |
| Chrome gagal dalam 25 detik | Path browser, versi Remotion, log handshake | Tinjau launcher proyek/timeout handshake; satu worker dan uji kecil | Chrome tersambung lalu MP4/metadata valid |
| Cloud terdaftar tetapi gagal autentikasi | Status akun/cache dan response login | Login sendiri pada profil yang tepat, kemudian probe terbatas | Autentikasi aktual lulus, tidak hanya `configured` |
| Rollback tidak memulihkan semuanya | Jenis receipt dan hash file saat ini | Pakai keluarga rollback yang sesuai; tinjau file yang berubah sesudah install | Daftar file yang benar-benar dipulihkan cocok dengan rencana |

## Pindah komputer dan membagikan paket

Pasang source publik MSSHI pada komputer tujuan, pilih mode/peran, lalu pasang aplikasi/runtime yang diperlukan sesuai OS/Python/Node perangkat itu. Lakukan login layanan sendiri pada perangkat tujuan. Memindahkan ZIP paket tidak memindahkan model, akun, sesi browser, atau semua binary aplikasi.

Untuk memindahkan pekerjaan pribadi, salin proyek, preferensi yang ingin dibawa, dan bahan persona secara privat setelah meninjau isinya. Pisahkan `.env`, `mcp-tokens`, cookie/browser profile, API key, backup config, dan receipt yang mengandung data pribadi dari artefak publik. Jangan mengunggah `msshi-private` atau seluruh root Hermes Anda ke GitHub. Paket publik memakai contoh dan referensi umum; katalog akun dan bahan pribadi pelanggan disiapkan terpisah.

Sesudah migrasi perangkat, baca status, verifikasi path executable, periksa compatibility runtime, dan uji satu artefak kecil. Nama/path contoh pada modul bukan syarat universal. Anda boleh memilih nama dan folder sendiri. Preset Hermes memakai profil native bernama; host lain mengikuti pemasangan workspace dan kemampuan koordinasinya. Ulangi pengenalan profil dan reload plugin yang didukung host sesudah migrasi perangkat.

## Lima profil native dan perbaikan koordinasi

Pada Hermes yang didukung, `muza-preset` menggunakan lima direktori profil bernama. Default tetap Hermes netral. Nama tampilan tidak boleh menjadi satu-satunya bukti identitas: root default yang diberi judul Yukino dapat tampak seperti bot bernama meskipun home-nya berbeda.

| Profil | Tanggung jawab | Alat kreatif utama |
| --- | --- | --- |
| default | Asisten Hermes netral | Tanpa ArtCraft |
| yukino | Intake ide dan pertanyaan awal, lalu handoff ke Shizuka | Tanpa ArtCraft |
| shizuka | Koordinator, guru dan penyatu hasil spesialis | Tanpa ArtCraft |
| val | Riset, literatur, bukti, data | Empat ArtCraft dokumen/data |
| kiki-chii | Konsep, film/video/foto, suara dan hasil kreatif | Tiga belas ArtCraft kreatif, Blender/FFmpeg sesuai rute |
| shikaku | Coding, debugging, vibecoding, audit yang diminta | CraftAnything dan Figcraft |

Bila pemasangan baru diperlukan, gunakan wizard pada root yang benar:

```powershell
msshi setup --platform hermes --mode muza-preset --target-dir "C:\HermesClient\profiles" --default-bot keep-hermes
```

Perintah tersebut adalah setup nyata. Tinjau pilihan menu sebelum menerapkan. Dari checkout source yang benar, installer langsung menyediakan pratinjau dan flag apply:

```powershell
python scripts/install_msshi.py --platform hermes --mode muza-preset --target-dir "C:\HermesClient\profiles" --default-bot keep-hermes
```

Tambahkan `--apply` setelah meninjau pratinjau tersebut. Pemasangan menjaga SOUL, rahasia dan nilai konfigurasi LLM yang sudah ada. Konfigurasi dapat mendapat aktivasi plugin/backend yang dijelaskan di bawah, sementara kebijakan terkelola dan perubahan profil dicatat pada receipt. `keep-hermes` juga memperbaiki hanya label root yang terduplikasi sebagai Yukino; ia tidak mengganti persona atau model root. Alias lama `auto`/`yukino` tetap menempatkan Yukino pada profil bernama. Pembersihan marker deleted hanya berlaku pada profil yang sengaja dipilih dipasang, bukan semua profil yang pernah dihapus pengguna.

Plugin `msshi-team-routing` aktif sebagai backend `msshi-team` hanya ketika backend lama default/unset. Backend kustom dipertahankan, sehingga ia dapat memerlukan pengaturan tersendiri sebelum schema delegasi bernama tersedia. `--no-team-routing` pada installer langsung melewati pemasangan backend tersebut. Instalasi tidak mengirim pesan antarbots atau memanggil model.

Setelah pemasangan, restart/reload plugin melalui mekanisme Hermes yang didukung, lalu mulai chat baru. Prompt koordinasi dibangun saat sesi dimulai; chat lama belum tentu memuat tambahan baru walaupun file plugin telah ada. Riwayat percakapan tidak perlu dihapus. Pada Bot Chat gunakan `message_agent` jika tersedia; pada backend ini `delegate_task` dapat menawarkan enum profil hidup. Jangan menambahkan parameter profil yang tidak ditawarkan tool sesi.

Jika Yukino mengerjakan semua spesialisasi sendiri, periksa urutan berikut: apakah chat berada pada profil bernama Yukino, apakah plugin termuat, apakah sesi baru, apakah schema delegasi menawarkan target, dan apakah tugas memang perlu spesialis. Jangan menyimpulkan komunikasi rusak hanya dari satu tugas intake sederhana. Satu simulasi/fixture schema juga belum membuktikan pengiriman model antarbots nyata berhasil; pengiriman nyata dapat memakai kredit.

Untuk memulihkan receipt profil dari root checkout yang cocok:

```powershell
python scripts/install_msshi.py --rollback-receipt "PATH_RECEIPT_PROFIL" --apply
```

Gunakan receipt yang dihasilkan installer profil. Perubahan pengguna sesudah pemasangan dilaporkan sebagai konflik, bukan ditimpa. Receipt profil bukan receipt migrasi runtime, Steel atau backup proyek.

## Baseline preservasi: tinjau sebelum menerima keadaan baru

Audit membandingkan keadaan kini dengan bukti sebelumnya. Nilai model yang sengaja diubah pengguna dapat membuat baseline lama tidak cocok. Baseline hilang atau stale bukan bukti otomatis bahwa model rusak; mengubah label hasil audit menjadi true juga tidak membuktikan preservasi.

```powershell
msshi runtime rebaseline --home "C:\HermesClient"
```

Pratinjau ini membaca konfigurasi/SOUL yang dilacak, menghitung `snapshot`, dan melaporkan apakah penerimaan keadaan kini diperlukan. Ia tidak mengubah model atau menulis baseline. Cocokkan perubahan dengan cadangan/diff privat dan keputusan pengguna. Jangan menaruh key atau isi config mentah dalam laporan publik.

Setelah keadaan sekarang benar-benar ditinjau, gunakan SHA snapshot yang baru dicetak:

```powershell
msshi runtime rebaseline --home "C:\HermesClient" --apply --expected-snapshot SHA256_DARI_PRATINJAU
```

Placeholder SHA harus diganti 64 karakter hash sebenarnya. Bila pengaturan LLM historis telah berubah/hilang bukti dan pengguna memang menerima keadaan sekarang, diperlukan penerimaan eksplisit dan alasan:

```powershell
msshi runtime rebaseline --home "C:\HermesClient" --apply --expected-snapshot SHA256_DARI_PRATINJAU --accept-current-llm-settings --reason "Pengaturan saat ini sudah ditinjau dan dipilih pengguna"
```

Jangan memakai opsi penerimaan sebagai langkah rutin untuk menghilangkan error yang belum dipahami. Perintah menolak snapshot stale jika input berubah di antara preview dan apply. Receipt mencatat metode penerimaan, alasan dan baseline sebelumnya. Operasi ini mengubah baseline saja, tidak mengganti provider/model/SOUL atau membuktikan siapa yang membuat perubahan masa lalu. `historical_external_edits_verified: false` tetap jujur walaupun keadaan baru diterima untuk pemeriksaan berikutnya.

Sesudah apply, baca `msshi runtime status --home "C:\HermesClient"`. Bila auditor lain masih melaporkan perbedaan, baca baseline dan scope auditor itu; jangan menganggap satu baseline memutihkan semua riwayat/konfigurasi. Simpan path receipt privat sebagai jalan rollback baseline bila diperlukan.

## Troubleshooting tambahan 3.1.1

| Gejala | Penyebab yang perlu dibedakan | Tindakan |
| --- | --- | --- |
| Yukino hilang, tetapi folder ada | Marker deleted atau identitas profil tidak ditemukan | Pasang ulang hanya profil yang memang dipilih lewat installer native, lalu rescan host |
| Default juga berjudul Yukino | Metadata tampilan root lama duplikat | Pilih keep-hermes; jangan mengganti SOUL/model untuk masalah label |
| Skill ada, delegasi profil belum muncul | Plugin belum reload, chat lama, atau backend kustom dipertahankan | Periksa plugin/backend dan mulai sesi baru; gunakan schema tool aktual |
| `profile` ditolak oleh tool | Host/backend sesi tidak menawarkan parameter itu | Jangan menebak API; gunakan Bot Chat yang mendukung atau handoff manual |
| Pilihan KAT dahulu tidak melakukan setup | Installer lama hanya menulis preferensi | Pada 3.1.1 gunakan msshi coder wizard; lengkapi endpoint/key/catalog secara nyata |
| KAT pending setelah memilih cloud | Key, ID model, endpoint atau rute belum siap | Baca status reason; Pro v2.5 berbeda dengan Dev dan memerlukan akun sendiri |
| Katalog model berhasil tetapi chat gagal | Bukti metadata belum membuktikan saldo/izin inferensi | Periksa respons layanan saat penggunaan yang diotorisasi; jangan tes berulang otomatis |
| KAT tak muncul pada bot selain Coder | Pembatasan peran memang diterapkan | Delegasikan coding ke Shikaku; model utama bot lain tetap utuh |
| App dipilih tetapi tidak diberi rute | Matriks peran menolak target di luar 4/2/13 atau target dinonaktifkan | Jalankan lewat pemilik peran, bukan melonggarkan seluruh profil |
| Cache kontekstual berubah | File cache tidak lagi cocok SHA snapshot | Simpan perubahan yang ingin dipertahankan, tinjau asalnya; jangan memalsukan manifest |
| CareerOps ada tetapi skor personal belum siap | CV/profil belum dipersonalisasi | Siapkan User Layer privat; jangan memakai profil contoh upstream |
| rea-video mengunduh model | Default upstream fitur audio/model belum dinonaktifkan | Gunakan tahap ringan dengan flag no-ASR/no-stems/no-VLM sebelum tugas yang memerlukan model |
| Rebaseline ditolak | Snapshot stale atau penerimaan perubahan belum eksplisit | Ulang preview, tinjau perubahan, baru apply dengan SHA tepat |
| Panduan tidak masuk Downloads | NoPdf/env opt-out, tujuan tidak bisa ditulis atau katalog gagal | Baca pesan installer; coba msshi manual download --dest ke folder yang dapat ditulis |

Tidak semua status NEEDS_ATTENTION berarti reinstall seluruh Hermes diperlukan. Contohnya `msshi doctor` dapat melihat helper LibreOffice sebagai informasi lingkungan meskipun rute LibreOffice dilarang pada preset. Paritas skill, dependency skripsi, kesiapan akun, baseline preservasi dan hasil aplikasi merupakan pemeriksaan yang berbeda. Baca field spesifik sebelum mengambil tindakan.

## Rujukan bab operasional

Rujukan publik pada commit yang menjadi dasar modul: `scripts/msshi_cli.py`, `scripts/msshi_managed.py`, `scripts/msshi_runtime.py`, `scripts/msshi_desktop.py`, `scripts/msshi_browser_policy.py`, `docs/MANAGED_UPDATES.md`, `docs/V3_MIGRATION.md`, `docs/STEEL_BROWSER_POLICY.md`, `docs/SERVICE_CONNECTIONS.md`, serta `docs/OPTION_GUIDE.md`. Gunakan source dan panduan versi yang sama saat memeriksa perilaku. File akun, bukti lokal, konfigurasi pelanggan dan cadangan privat bukan bagian bahan publik yang harus dimiliki pembaca.


# 8. Referensi lengkap command MSSHI

Referensi ini cocok dengan source `84ecd134f01ec65c4848b4f50c597b811f6b3a80` pada 16 November 2026. Parser asli menjadi sumber sintaks; penjelasan operasional dibaca dari implementasi. Tidak ada command model, render, login, instalasi, atau layanan yang dijalankan untuk menyusun bagian ini. Tree parser ditangkap sebelum `parse_args` mengeksekusi aksi; `format_help` menghasilkan usage sebenarnya.

## Cara membaca dan menyalin

Contoh `C:\HermesClient` adalah contoh root Hermes yang harus diganti dengan lokasi instalasi Anda; jangan membuat root kedua hanya untuk menyamakan contoh. `C:\MSSHI-Latihan`, `C:\MSSHI-Hasil`, nama input, dan receipt adalah contoh yang harus disiapkan atau diganti. Jangan menyalin placeholder `PATH_*`, `ID_TIKET`, atau `RECEIPT` secara harfiah. Teks command dijalankan di terminal PowerShell, bukan dikirim sebagai slash command di kolom chat bot.

`-h`/`--help` tersedia pada setiap parser dan hanya menampilkan bantuan. Untuk keluarga yang memiliki shared flag, taruh flag sebelum subcommand: `msshi rea --hermes-home "C:\HermesClient" status`. BRAG berbeda: flag `--hermes-root` berada setelah `doctor`, `check`, `render`, atau `renderer`. Runtime menerima `--home` sebelum maupun pada subcommand. Perhatikan usage tiap node, jangan menyeragamkan flag antarfitur.

Status default pada tabel merepresentasikan nilai logis, bukan path fixture ekstraksi. Jika flag home kosong, resolusi mengikuti implementasi/env/host; lebih aman memilih home secara eksplisit pada tindakan yang menulis. `--help` sukses membuktikan sintaks, bukan membuktikan runtime, akun, lisensi, atau kualitas hasil tugas.

Pisahkan empat biaya: token LLM untuk memahami chat; layanan cloud/API; unduhan/storage; CPU/GPU/RAM lokal. Command tanpa LLM masih dapat memakai disk, CPU, jaringan atau kuota layanan. Tidak ada jaminan seluruh tagihan token menjadi nol.

## Peta keluarga command


Bantuan akar: `msshi --help`. Opsi `-h/--help` menampilkan petunjuk dan keluar sebelum aksi command.

```text
usage: msshi [-h]
             {check,status,connect,update,runtime,integrations,desktop,audit,doctor,skripsi,assets,compact,browser,trim,managed,services,timesfm,brag,scrapling,harness2,optional,rea,choices,manual,dream,voice,kat,coder,setup,select,bootstrap}
             ...
```

| Keluarga | Tujuan | Perintah awal |
| --- | --- | --- |
| `msshi check` | Membandingkan versi paket aktif dengan VERSION.json pada GitHub main, membaca changelog dan merangkum rute aplikasi serta cakupan updater.. | `msshi check --help` |
| `msshi status` | Alias tepat untuk check: ringkasan rute/updater lalu pemeriksaan versi dan changelog GitHub.. | `msshi status --help` |
| `msshi connect` | Mendaftarkan rute aplikasi/CLI/MCP web pada profil aktif. | `msshi connect --help` |
| `msshi update` | Mengambil source terbaru, membuat snapshot rilis aktif, memperbarui salinan skill terkelola yang masih cocok, menjaga kustomisasi, dan menjalankan migrasi Hermes yang tersedia. | `msshi update --help` |
| `msshi runtime` | Lapisan migrasi Hermes, pembacaan hardware/kebijakan, rebaseline yang ditinjau, tiket tugas sekali pakai, eksekusi proses milik dispatcher, guardian dan rollback transaksi migrasi.. | `msshi runtime --help` |
| `msshi integrations` | Pemasangan integrasi terpilih dari pin source, pembacaan/pengambilan source kontekstual, serta bentuk lengkap untuk dream/voice/kat. | `msshi integrations --help` |
| `msshi desktop` | Peluncur Windows untuk instalasi Hermes Desktop yang sudah ada. | `msshi desktop --help` |
| `msshi audit` | Memeriksa struktur paket/profil, hash preservasi, scope skill, konfigurasi guard, serta bukti operasi yang sudah direkam. | `msshi audit --help` |
| `msshi doctor` | Periksa paritas paket, dependensi skripsi, tool lokal dan lokasi data adaptif.. | `msshi doctor --help` |
| `msshi skripsi` | Merakit template skripsi Word dari pedoman, metadata kampus, bahan referensi dan preset metode.. | `msshi skripsi --help` |
| `msshi assets` | Mencari SOUL, sampel suara, nama file terkait katalog Notebook/knowledge base, dan arsip bahan personal pada root yang Anda tentukan.. | `msshi assets --help` |
| `msshi compact` | Meringkas representasi file konteks lokal: menghapus whitespace JSON atau merangkum pengulangan baris log. | `msshi compact --help` |
| `msshi browser` | Memasang atau memeriksa kebijakan Steel sebagai jalur browsing umum, menilai prasyarat akses akun personal/transfer, dan memulihkan transaksi Steel yang cocok.. | `msshi browser --help` |
| `msshi trim` | Membaca metrik hook Llmtrim otomatis atau memadatkan request JSON lokal melalui binary llmtrim. | `msshi trim --help` |
| `msshi managed` | Mendaftarkan dan memperbarui salinan MSSHI berdasarkan kecocokan isi/fingerprint, termasuk target fisik yang diakses melalui junction yang telah ditinjau.. | `msshi managed --help` |
| `msshi services` | Membaca registrasi GitLab/Tinyfish, memasang definisi konektor MCP web, atau melakukan discovery/autentikasi lewat transport native Hermes.. | `msshi services --help` |
| `msshi timesfm` | Menjalankan peramalan deret waktu numerik lokal untuk Val melalui runtime/bobot TimesFM terisolasi. | `msshi timesfm --help` |
| `msshi brag` | Membuat tiga berkas brief/konsep/review untuk video peluncuran, lalu memeriksa/merender komposisi HTML yang dibuat pada tahap berikut melalui Hyperframes pin lokal. | `msshi brag --help` |
| `msshi scrapling` | Parser HTML lokal dengan selector CSS/XPath untuk Val dan Coder. | `msshi scrapling --help` |
| `msshi harness2` | Menyusun proposal Propose-Probe-Compose dan menjalankan demo deterministik perbaikan harness dalam salinan terisolasi. | `msshi harness2 --help` |
| `msshi optional` | Melihat dan mengaktifkan wrapper tambahan di luar paket standar. | `msshi optional --help` |
| `msshi rea` | Analisis statis JavaScript/aplikasi yang diekstrak dan inventaris artefak lokal, dengan jalur native eksplisit bila engine tersedia. | `msshi rea --help` |
| `msshi choices` | Membaca fungsi, status instruksi, dan prasyarat mode, platform, paket, skill, fitur dan aplikasi. | `msshi choices --help` |
| `msshi manual` | Lihat katalog atau salin/unduh panduan PDF versi tertentu dengan SHA256.. | `msshi manual --help` |
| `msshi dream` | Membuat proposal rangkuman/pelajaran lokal dan deterministik dari bahan yang relevan, atau mendaftarkan jadwalnya. | `msshi dream --help` |
| `msshi voice` | Status, pemasangan dan aktivasi OmniVoice lokal sebagai TTS native Hermes, serta preferensi gaya suara per peran. | `msshi voice --help` |
| `msshi kat` | Alias kompatibilitas KAT: status membaca, pilihan light/ideal/cloud membuka wizard endpoint/key khusus Coder; skip menonaktifkan KAT saja.. | `msshi kat --help` |
| `msshi coder` | Atur model KAT opsional khusus subtask Coder melalui endpoint yang benar, input key privat, dan katalog model.. | `msshi coder --help` |
| `msshi setup` | Wizard awal empat mode: semua skill standar pada satu agen, tim kustom, paket kategori terpilih, atau preset lima peran. | `msshi setup --help` |
| `msshi select` | Memilih kategori atau skill satu per satu untuk ditambah/diperbarui. | `msshi select --help` |
| `msshi bootstrap` | Mendaftarkan snapshot rilis lokal, launcher global, PATH user dan panduan PDF otomatis. | `msshi bootstrap --help` |

## 1. `msshi check`

Membandingkan versi paket aktif dengan VERSION.json pada GitHub main, membaca changelog dan merangkum rute aplikasi serta cakupan updater.

**Prasyarat.** CLI telah terpasang. Bagian perbandingan versi memerlukan internet ke GitHub; tidak memanggil model LLM.

**Mulai dari.**

```powershell
msshi check --hermes-home "C:\HermesClient"
```

**Batas dan efek.** Ini pemeriksaan versi paket, bukan pembuktian seluruh runtime, login layanan, atau skill siap. Versi semantik yang sama dapat memiliki commit main baru; jalankan update bila ingin revisi main tersebut.

### `msshi check`

Efek: Baca lokal dan jaringan GitHub; tanpa perubahan profil.

```text
usage: msshi check [-h] [--hermes-home HERMES_HOME] [--profile PROFILE]
                   [--state-dir STATE_DIR]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--hermes-home` | opsional; default tidak diisi | Home/root Hermes yang dipilih; gunakan nilai eksplisit agar tidak mengarah ke profil lain. |
| `--profile` | opsional; default tidak diisi | ID folder profil Hermes, misalnya default atau kiki-chii; bukan selalu nama tampilan. |
| `--state-dir` | opsional; default tidak diisi | Lokasi alternatif registri koneksi per profil. |

## 2. `msshi status`

Alias tepat untuk check: ringkasan rute/updater lalu pemeriksaan versi dan changelog GitHub.

**Prasyarat.** Sama dengan check; status ini bukan perintah offline penuh.

**Mulai dari.**

```powershell
msshi status --hermes-home "C:\HermesClient"
```

**Batas dan efek.** Untuk status lokal aplikasi saja gunakan connect --status; untuk kebijakan/migrasi gunakan runtime status.

### `msshi status`

Efek: Baca lokal dan jaringan GitHub; tanpa perubahan profil.

```text
usage: msshi status [-h] [--hermes-home HERMES_HOME] [--profile PROFILE]
                    [--state-dir STATE_DIR]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--hermes-home` | opsional; default tidak diisi | Home/root Hermes yang dipilih; gunakan nilai eksplisit agar tidak mengarah ke profil lain. |
| `--profile` | opsional; default tidak diisi | ID folder profil Hermes, misalnya default atau kiki-chii; bukan selalu nama tampilan. |
| `--state-dir` | opsional; default tidak diisi | Lokasi alternatif registri koneksi per profil. |

## 3. `msshi connect`

Mendaftarkan rute aplikasi/CLI/MCP web pada profil aktif. Menu menjelaskan fungsi tiap aplikasi dan membedakan registrasi dari eksekusi. Auto-reconnect menyelaraskan yang terdeteksi/terkonfigurasi menurut peran dan penonaktifan tersimpan; select memilih ID tertentu.

**Prasyarat.** Aplikasi/CLI atau konektor yang relevan tersedia. Autentikasi, lisensi, runtime dan izin tugas merupakan tahap terpisah.

**Mulai dari.**

```powershell
msshi connect --catalog
msshi connect --status --hermes-home "C:\HermesClient"
```

**Batas dan efek.** --catalog/--status tidak membuka aplikasi. Pada profil v3, --open/--run memerlukan tiket tugas untuk rute yang dilindungi. Menghapus rute dari registri tidak menghapus aplikasi. GitLab/Tinyfish tetap MCP web; Blender/Lightcraft dan aplikasi desktop memakai native CLI. Preset ArtCraft dibatasi Val 4, Shikaku 2, Kiki 13; default/Yukino/Shizuka tidak mendapat ArtCraft, Figcraft saja yang dibagi Coder/Kiki.

| Pemilih tindakan | Fungsi | Efek |
| --- | --- | --- |
| --catalog | Daftar rute yang dikenal dan fungsinya; registrasi/readiness terpisah. | baca lokal |
| --status | Daftar rute yang telah terdaftar pada profil. | baca lokal |
| --mode auto-reconnect | Selaraskan yang terdeteksi/terkonfigurasi sesuai peran; pertahankan pilihan nonaktif, tanpa login/membuka aplikasi. | tulis registri |
| --mode select | Pilih angka/ID aplikasi, atau gunakan --targets. | tulis registri |
| --add TARGET | Daftarkan satu ID atau grup seperti artcraft. | tulis registri |
| --remove TARGET | Lepas rute dari registri; tidak uninstall aplikasi. | tulis registri |
| --open TARGET | Buka rute terdaftar, sesuai tiket dan kebijakan v3. | eksekusi proses/browser |
| --run TARGET -- ARGS | Jalankan CLI terdaftar, sesuai tiket dan argumen tugas. | eksekusi alat |

### `msshi connect`

Efek: Katalog/status membaca. Mode/add/remove menulis registri. Open/run dapat memulai proses, browser atau operasi sesuai rute.

```text
usage: msshi connect [-h] [--hermes-home HERMES_HOME] [--profile PROFILE]
                     [--state-dir STATE_DIR] [--json] [--dry-run]
                     [--targets TARGETS] [--query QUERY] [--ticket TICKET]
                     [--mode {auto-reconnect,select} | --catalog | --status | --add TARGET | --remove TARGET | --open TARGET | --run TARGET]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--hermes-home` | opsional; default tidak diisi | Home/root Hermes yang dipilih; gunakan nilai eksplisit agar tidak mengarah ke profil lain. |
| `--profile` | opsional; default tidak diisi | ID folder profil Hermes, misalnya default atau kiki-chii; bukan selalu nama tampilan. |
| `--state-dir` | opsional; default tidak diisi | Lokasi alternatif registri koneksi per profil. |
| `--json` | opsional; default Tidak/OFF | Tampilkan hasil dalam JSON. |
| `--dry-run` | opsional; default Tidak/OFF | Pratinjau perubahan tanpa menulis registri. |
| `--targets` | opsional; default tidak diisi | ID target dipisah koma untuk --mode select. |
| `--query` | opsional; default tidak diisi | Simbol/alamat/pola untuk operasi native, atau kueri/workspace untuk rute koneksi. |
| `--ticket` | opsional; default tidak diisi | ID tiket satu kali yang dibuat untuk target/profil/tugas ini. |
| `--mode` | opsional; default tidak diisi | Pilih mode operasi; daftar nilai sah dan artinya ada pada tabel tindakan. Nilai: auto-reconnect, select. |
| `--catalog` | opsional; default Tidak/OFF | Lihat pilihan target yang dikenal. |
| `--status` | opsional; default Tidak/OFF | Tampilkan status lokal; efek tepat mengikuti penjelasan keluarga. |
| `--add` | opsional; default tidak diisi | Daftarkan target atau grup. |
| `--remove` | opsional; default tidak diisi | Lepas target dari registri MSSHI. |
| `--open` | opsional; default tidak diisi | Buka rute web atau aplikasi yang terdaftar. |
| `--run` | opsional; default tidak diisi | Jalankan rute CLI terdaftar dengan argumen setelah --. |
| `command_args` | opsional; default tidak diisi | Sisa argumen yang diteruskan ke CLI saat --run; gunakan -- sebagai pemisah. |

Paling banyak satu dari: `--mode`, `--catalog`, `--status`, `--add`, `--remove`, `--open`, `--run`.

## 4. `msshi update`

Mengambil source terbaru, membuat snapshot rilis aktif, memperbarui salinan skill terkelola yang masih cocok, menjaga kustomisasi, dan menjalankan migrasi Hermes yang tersedia. Secara default juga menyegarkan cache upstream/integrasi terpilih dan menyalin PDF panduan dari katalog, kecuali --no-pdf.

**Prasyarat.** Python, Git, internet, disk cukup, dan target yang sudah terdaftar. Simpan receipt serta backup privat. Tutup tugas yang sedang memakai file skill sebelum pembaruan.

**Mulai dari.**

```powershell
msshi update --hermes-home "C:\HermesClient" --skip-upstreams
```

**Batas dan efek.** --skip-upstreams tidak membuat update menjadi read-only/offline: source MSSHI tetap diambil dan migrasi profil tetap dapat berjalan. Runtime pihak ketiga tidak semuanya diperbarui otomatis. --source memakai kandidat lokal yang sudah ditinjau; penanda git_commit menjadi local-candidate.

### `msshi update`

Efek: Unduhan, salinan skill, metadata updater, backup dan migrasi profil; bukan panggilan LLM.

```text
usage: msshi update [-h] [--skip-upstreams] [--hermes-home HERMES_HOME]
                    [--source SOURCE] [--download-pdf] [--no-pdf]
                    [--pdf-version PDF_VERSION] [--pdf-dest PDF_DEST]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--skip-upstreams` | opsional; default Tidak/OFF | Hanya perbarui MSSHI dan skill bundel. |
| `--hermes-home` | opsional; default tidak diisi | Home/root Hermes yang dipilih; gunakan nilai eksplisit agar tidak mengarah ke profil lain. |
| `--source` | opsional; default tidak diisi | Source yang dituju; artinya bergantung command, dijelaskan pada catatan keluarga. |
| `--download-pdf` | opsional; default Tidak/OFF | Minta pengiriman PDF secara eksplisit; rilis ini juga mengirim otomatis kecuali opt-out. |
| `--no-pdf` | opsional; default Tidak/OFF | Lewati salinan otomatis PDF sesudah instalasi/update; tidak membatalkan pemasangan skill. |
| `--pdf-version` | opsional; default tidak diisi | Versi panduan yang ada di katalog, default latest; PDF berbeda dari pemasangan runtime. |
| `--pdf-dest` | opsional; default tidak diisi | Folder tujuan PDF panduan; default Downloads/MSSHI_Manuals atau folder manual data MSSHI. |

## 5. `msshi runtime`

Lapisan migrasi Hermes, pembacaan hardware/kebijakan, rebaseline yang ditinjau, tiket tugas sekali pakai, eksekusi proses milik dispatcher, guardian dan rollback transaksi migrasi.

**Prasyarat.** Home Hermes dan profil tepat. Aplikasi sudah terdeteksi pada rute; tiket bukan batas keamanan OS.

**Mulai dari.**

```powershell
msshi runtime status --home "C:\HermesClient"
msshi runtime hardware --home "C:\HermesClient"
```

**Batas dan efek.** Migrate menulis konfigurasi/skill/kebijakan dengan backup; ia tidak sama dengan status. Guardian mengawasi tugas milik dispatcher, bukan antivirus/EDR dan bukan pembunuh proses pengguna. Rebaseline diawali preview read-only dan memerlukan snapshot segar saat apply; penerimaan keadaan LLM yang berubah harus eksplisit beserta alasan. Baseline baru tidak membuktikan riwayat perubahan masa lalu. Runtime rollback hanya menerima receipt migrasi yang cocok dengan home serta schema changes; receipt Steel memakai browser --rollback.

### `msshi runtime`

Efek: Status/hardware/scan dan preview rebaseline membaca; migrate/ticket/guardian-install/rollback serta rebaseline --apply menulis; run/guardian dapat menjalankan proses.

```text
usage: msshi runtime [-h] [--home HOME]
                     {migrate,status,hardware,guardian-install,rebaseline,ticket,run,guardian,scan,rollback}
                     ...
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--home` | opsional; default tidak diisi | Home data yang dituju; lihat catatan keluarga karena managed memakai state MSSHI, bukan home Hermes. |

#### `msshi runtime migrate`

Migrasikan home/profil: backup, rute native, guard, plugin dan konfigurasi yang ditangani MSSHI.

Efek: Status/hardware/scan dan preview rebaseline membaca; migrate/ticket/guardian-install/rollback serta rebaseline --apply menulis; run/guardian dapat menjalankan proses.

```text
usage: msshi runtime migrate [-h] [--home SUB_HOME] [--json]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--home` | opsional; default tidak diisi | Home data Hermes untuk operasi ini; dapat ditulis setelah subcommand runtime. |
| `--json` | opsional; default Tidak/OFF | Output is always JSON |

#### `msshi runtime status`

Baca kebijakan/rute dan bukti preservasi provider/model; baca hasil serta readiness dan alasan setup yang masih diperlukan.

Efek: Baca/cetak lokal; opsi verify melakukan hashing, bukan eksekusi model.

```text
usage: msshi runtime status [-h] [--home SUB_HOME] [--json]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--home` | opsional; default tidak diisi | Home data Hermes untuk operasi ini; dapat ditulis setelah subcommand runtime. |
| `--json` | opsional; default Tidak/OFF | Output is always JSON |

#### `msshi runtime hardware`

Baca hardware, RAM/commit yang tersedia dan tier/batas kerja yang disarankan.

Efek: Baca/cetak lokal; opsi verify melakukan hashing, bukan eksekusi model.

```text
usage: msshi runtime hardware [-h] [--home SUB_HOME] [--json]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--home` | opsional; default tidak diisi | Home data Hermes untuk operasi ini; dapat ditulis setelah subcommand runtime. |
| `--json` | opsional; default Tidak/OFF | Output is always JSON |

#### `msshi runtime guardian-install`

Pasang dan mulai watchdog lokal Windows; Task Scheduler atau fallback Startup yang dikelola.

Efek: Status/hardware/scan dan preview rebaseline membaca; migrate/ticket/guardian-install/rollback serta rebaseline --apply menulis; run/guardian dapat menjalankan proses.

```text
usage: msshi runtime guardian-install [-h] [--home SUB_HOME] [--json]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--home` | opsional; default tidak diisi | Home data Hermes untuk operasi ini; dapat ditulis setelah subcommand runtime. |
| `--json` | opsional; default Tidak/OFF | Output is always JSON |

#### `msshi runtime rebaseline`

Preview membaca snapshot konfigurasi/SOUL. Apply memerlukan SHA segar; penerimaan perubahan LLM perlu flag eksplisit dan alasan. Menulis baseline/receipt saja, tanpa mengganti nilai model atau membuktikan riwayat edit.

Efek: Preview read-only; --apply menulis baseline/receipt sesudah validasi snapshot, tanpa mengubah konfigurasi/SOUL.

```text
usage: msshi runtime rebaseline [-h] [--home SUB_HOME] [--apply]
                                [--expected-snapshot EXPECTED_SNAPSHOT]
                                [--accept-current-llm-settings]
                                [--reason REASON]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--home` | opsional; default tidak diisi | Home data Hermes untuk operasi ini; dapat ditulis setelah subcommand runtime. |
| `--apply` | opsional; default Tidak/OFF | Terapkan rencana yang didukung command ini; tanpa flag managed tetap merencanakan. |
| `--expected-snapshot` | opsional; default tidak diisi | SHA-256 snapshot dari preview rebaseline yang baru; apply ditolak bila input berubah sesudah preview. |
| `--accept-current-llm-settings` | opsional; default Tidak/OFF | Terima keadaan LLM sekarang hanya sesudah ditinjau pengguna; tidak membuktikan perubahan historis sah atau mengubah model. |
| `--reason` | opsional; default teks kosong | Alasan penerimaan keadaan kini; jangan memasukkan key atau rahasia. Diperlukan saat menerima perubahan LLM. |

#### `msshi runtime ticket`

Buat ID tiket satu kali untuk satu tugas/target/profil, TTL 1-3600 detik; uraian tugas minimal 8 karakter.

Efek: Status/hardware/scan dan preview rebaseline membaca; migrate/ticket/guardian-install/rollback serta rebaseline --apply menulis; run/guardian dapat menjalankan proses.

```text
usage: msshi runtime ticket [-h] [--home SUB_HOME] [--profile PROFILE]
                            --target TARGET --task TASK
                            [--source {direct,context}] [--ttl TTL]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--home` | opsional; default tidak diisi | Home data Hermes untuk operasi ini; dapat ditulis setelah subcommand runtime. |
| `--profile` | opsional; default tidak diisi | ID folder profil Hermes, misalnya default atau kiki-chii; bukan selalu nama tampilan. |
| `--target` | wajib; default tidak diisi | ID rute aplikasi native untuk satu tugas; harus tersedia pada profil yang dipilih. |
| `--task` | wajib; default tidak diisi | Uraian tugas aktif yang spesifik; minimal 8 karakter saat membuat tiket. |
| `--source` | opsional; default direct | Asal tugas direct atau context; tidak mengunduh repo atau memilih model. Nilai: direct, context. |
| `--ttl` | opsional; default 600 | Masa berlaku tiket dalam detik; rentang 1-3600, default 600, satu penggunaan. |

#### `msshi runtime run`

Gunakan tiket cocok untuk menjalankan satu rute CLI, dengan timeout dan kepemilikan proses dispatcher.

Efek: Status/hardware/scan dan preview rebaseline membaca; migrate/ticket/guardian-install/rollback serta rebaseline --apply menulis; run/guardian dapat menjalankan proses.

```text
usage: msshi runtime run [-h] [--home SUB_HOME] [--profile PROFILE] --ticket
                         TICKET [--timeout TIMEOUT]
                         target ...
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--home` | opsional; default tidak diisi | Home data Hermes untuk operasi ini; dapat ditulis setelah subcommand runtime. |
| `--profile` | opsional; default tidak diisi | ID folder profil Hermes, misalnya default atau kiki-chii; bukan selalu nama tampilan. |
| `--ticket` | wajib; default tidak diisi | ID tiket satu kali yang dibuat untuk target/profil/tugas ini. |
| `--timeout` | opsional; default 600 | Batas waktu dalam detik; bukan janji waktu selesai. Desktop menerima 30-600. |
| `target` | wajib; default tidak diisi | ID rute aplikasi native untuk satu tugas; harus tersedia pada profil yang dipilih. |
| `arguments` | opsional; default tidak diisi | Argumen yang diteruskan ke target setelah nama target, lazimnya dipisahkan --. |

#### `msshi runtime guardian`

Awasi tiket tugas milik dispatcher; --once satu putaran, tanpa itu loop lokal sampai dihentikan.

Efek: Status/hardware/scan dan preview rebaseline membaca; migrate/ticket/guardian-install/rollback serta rebaseline --apply menulis; run/guardian dapat menjalankan proses.

```text
usage: msshi runtime guardian [-h] [--home SUB_HOME] [--once]
                              [--interval INTERVAL] [--scan-root SCAN_ROOT]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--home` | opsional; default tidak diisi | Home data Hermes untuk operasi ini; dapat ditulis setelah subcommand runtime. |
| `--once` | opsional; default Tidak/OFF | Jalankan guardian satu putaran, lalu keluar; tanpa flag ia terus mengawasi secara lokal. |
| `--interval` | opsional; default 60 | Jeda guardian dalam detik; rentang 5-3600, default 60. |
| `--scan-root` | opsional; default tidak diisi | Folder opsional untuk pemindaian pola rahasia statis pada putaran guardian. |

#### `msshi runtime scan`

Pindai pola rahasia statis pada path terpilih; laporkan temuan tanpa otomatis memperbaiki semuanya.

Efek: Status/hardware/scan dan preview rebaseline membaca; migrate/ticket/guardian-install/rollback serta rebaseline --apply menulis; run/guardian dapat menjalankan proses.

```text
usage: msshi runtime scan [-h] [--home SUB_HOME] path
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `path` | wajib; default tidak diisi | File/folder input yang dipilih dan diizinkan; tidak sama dengan URL jaringan. |
| `--home` | opsional; default tidak diisi | Home data Hermes untuk operasi ini; dapat ditulis setelah subcommand runtime. |

#### `msshi runtime rollback`

Pulihkan hanya perubahan pada receipt migrasi dalam home ini, dengan pemeriksaan hash/target.

Efek: Status/hardware/scan dan preview rebaseline membaca; migrate/ticket/guardian-install/rollback serta rebaseline --apply menulis; run/guardian dapat menjalankan proses.

```text
usage: msshi runtime rollback [-h] [--home SUB_HOME] receipt
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `receipt` | wajib; default tidak diisi | Receipt migrasi runtime yang sesuai dengan home dan schema changes; bukan receipt Steel. |
| `--home` | opsional; default tidak diisi | Home data Hermes untuk operasi ini; dapat ditulis setelah subcommand runtime. |

## 6. `msshi integrations`

Pemasangan integrasi terpilih dari pin source, pembacaan/pengambilan source kontekstual, serta bentuk lengkap untuk dream/voice/kat. Tiga alias singkat msshi dream, voice, kat memiliki opsi yang sama dengan subcommand terkait di sini.

**Prasyarat.** Install memerlukan internet/Git, ruang disk dan home yang tepat. Dependency, aplikasi, bobot atau akun tidak semuanya otomatis siap setelah source skill disalin.

**Mulai dari.**

```powershell
msshi integrations --help
```

**Batas dan efek.** Install adalah tindakan nyata yang mengambil source curated dan memasang materi sesuai peran; dokumentasikan receipt. Subcommand source default hanya membaca cache; --fetch mengambil pin, --install-runtime memasang dependency secara eksplisit di luar scanner. CareerOps memerlukan User Layer privat; rea-video memisahkan fitur model dari tahap lokal. Gunakan status masing-masing runtime untuk membuktikan readiness. Jangan mengulang pemasangan hanya untuk memeriksa versi.

### `msshi integrations`

Efek: Install/--fetch mengambil source dan menulis cache; source query/list/read memakai cache lokal; --install-runtime menjalankan pemasangan dependency tanpa menjalankan tugas model/browser. Dream/voice/kat mengikuti efek alias masing-masing.

```text
usage: msshi integrations [-h] {install,dream,voice,kat,source} ...
```

Tidak ada flag khusus pada node ini selain `-h/--help`; opsi shared keluarga diletakkan sebelum subcommand.

#### `msshi integrations install`

Ambil dan pasang integrasi source terpilih sesuai peran, dengan tujuan Antigravity opsional.

Efek: Instalasi nyata: unduhan/build atau pemasangan berkas. Prasyarat/izin terpisah berlaku.

```text
usage: msshi integrations install [-h] [--home HOME]
                                  [--antigravity ANTIGRAVITY]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--home` | opsional; default HERMES_HOME / default host | Home data yang dituju; lihat catatan keluarga karena managed memakai state MSSHI, bukan home Hermes. |
| `--antigravity` | opsional; default tidak diisi | Folder skill Antigravity opsional yang dipilih untuk pemasangan integrasi. |

#### `msshi integrations dream`

Bentuk panjang msshi dream; opsi dan efek sama.

Efek: Install/--fetch mengambil source dan menulis cache; source query/list/read memakai cache lokal; --install-runtime menjalankan pemasangan dependency tanpa menjalankan tugas model/browser. Dream/voice/kat mengikuti efek alias masing-masing.

```text
usage: msshi integrations dream [-h] [--home HOME] (--run-now | --register)
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--home` | opsional; default HERMES_HOME / default host | Home data yang dituju; lihat catatan keluarga karena managed memakai state MSSHI, bukan home Hermes. |
| `--run-now` | opsional; default Tidak/OFF | Buat proposal dreaming lokal sekarang; dapat membaca bahan dan menulis proof/proposal. |
| `--register` | opsional; default Tidak/OFF | Daftarkan jadwal dreaming lokal, bukan status-only. |

Wajib satu dari: `--run-now`, `--register`.

#### `msshi integrations voice`

Bentuk panjang msshi voice; opsi dan efek sama.

Efek: Install/--fetch mengambil source dan menulis cache; source query/list/read memakai cache lokal; --install-runtime menjalankan pemasangan dependency tanpa menjalankan tugas model/browser. Dream/voice/kat mengikuti efek alias masing-masing.

```text
usage: msshi integrations voice [-h] [--home HOME] [--status] [--enable]
                                [--install-runtime]
                                [--role {yukino,shizuka,val,kiki-chii,shikaku}]
                                [--state {normal,calm,tired,incident}]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--home` | opsional; default HERMES_HOME / default host | Home data yang dituju; lihat catatan keluarga karena managed memakai state MSSHI, bukan home Hermes. |
| `--status` | opsional; default Tidak/OFF | Tampilkan status lokal; efek tepat mengikuti penjelasan keluarga. |
| `--enable` | opsional; default Tidak/OFF | Aktifkan TTS lokal yang telah lolos uji pada konfigurasi profil. |
| `--install-runtime` | opsional; default Tidak/OFF | Pasang runtime/dependency lokal secara eksplisit; dapat memakai internet/disk dan uji CPU. |
| `--role` | opsional; default tidak diisi | Peran suara: yukino, shizuka, val, kiki-chii atau shikaku. Nilai: yukino, shizuka, val, kiki-chii, shikaku. |
| `--state` | opsional; default tidak diisi | Preferensi suara normal/calm/tired/incident; berdasarkan pilihan pengguna, bukan diagnosis. Nilai: normal, calm, tired, incident. |

#### `msshi integrations kat`

Bentuk panjang msshi kat; opsi dan efek sama.

Efek: Install/--fetch mengambil source dan menulis cache; source query/list/read memakai cache lokal; --install-runtime menjalankan pemasangan dependency tanpa menjalankan tugas model/browser. Dream/voice/kat mengikuti efek alias masing-masing.

```text
usage: msshi integrations kat [-h] [--home HOME]
                              [--mode {skip,cloud,light,ideal,status}]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--home` | opsional; default HERMES_HOME / default host | Home data yang dituju; lihat catatan keluarga karena managed memakai state MSSHI, bukan home Hermes. |
| `--mode` | opsional; default status | Pilih mode operasi; daftar nilai sah dan artinya ada pada tabel tindakan. Nilai: skip, cloud, light, ideal, status. |

#### `msshi integrations source`

Status/cache reader untuk CareerOps, Remote In Tech, Matt Pocock dan rea-video. --fetch mengambil source pin; query/list/skill lokal; runtime dipasang hanya dengan --install-runtime. Tidak ada job scan/panggilan model pada boot.

Efek: Default/status/query/list/skill membaca cache; --fetch memakai jaringan/tulis cache; --install-runtime mengunduh dependency dan menjalankan installer, tanpa tugas/model.

```text
usage: msshi integrations source [-h] --home HOME --name
                            {career-ops,remote-jobs,mattpocock-skills,rea-video}
                            [--fetch | --install-runtime | --list | --skill SKILL | --query QUERY]
                            [--limit 1..50]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--home` | wajib; default tidak diisi | Home data yang dituju; lihat catatan keluarga karena managed memakai state MSSHI, bukan home Hermes. |
| `--name` | wajib; default tidak diisi | Source kontekstual: career-ops, remote-jobs, mattpocock-skills atau rea-video; bukan nama opsi REA Coder. Nilai: career-ops, remote-jobs, mattpocock-skills, rea-video. |
| `--fetch` | opsional; default Tidak/OFF | Ambil source GitHub pada pin yang ditinjau ke cache privat di luar scanner; tanpa runtime/model/eksekusi tugas. |
| `--install-runtime` | opsional; default Tidak/OFF | Pasang runtime/dependency lokal secara eksplisit; dapat memakai internet/disk dan uji CPU. |
| `--list` | opsional; default Tidak/OFF | Daftar path skill Matt Pocock pada cache, termasuk explicit_only dan in_progress. |
| `--skill` | opsional; default tidak diisi | Baca satu skill Matt Pocock yang sudah dicache berdasarkan nama folder yang tepat. |
| `--query` | opsional; default tidak diisi | Kueri teks pada cache direktori perusahaan remote; tanpa jaringan atau pengiriman aplikasi. |
| `--limit` | opsional; default 10 | Batas kecocokan direktori remote-company, 1-50; hasil bukan bukti lowongan masih aktif. Nilai: 1..50. |

Paling banyak satu dari: `--fetch`, `--install-runtime`, `--list`, `--skill`, `--query`.

## 7. `msshi desktop`

Peluncur Windows untuk instalasi Hermes Desktop yang sudah ada. Menangani marker update native, menyiapkan gateway, lalu membuka UI bila tidak memakai check-only.

**Prasyarat.** Instalasi Windows Hermes lengkap di home: hermes-agent, bin/hermes.exe, Desktop executable dan skrip update native.

**Mulai dari.**

```powershell
msshi desktop --help
```

**Batas dan efek.** --check-only tetap dapat mereklamasi marker update yang dinyatakan stale oleh Hermes dan memulai/prewarm gateway; ia bukan baca murni. Ia hanya melewati pembukaan UI Desktop. Software rendering berlaku pada child Desktop; tidak mengganti model/provider.

### `msshi desktop`

Efek: Dapat menyiapkan gateway dan membuka Desktop. --install-shortcut menulis shortcut beserta backup.

```text
usage: msshi desktop [-h] [--hermes-home HERMES_HOME] [--timeout TIMEOUT]
                     [--check-only] [--software-rendering]
                     [--install-shortcut]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--hermes-home` | opsional; default HERMES_HOME / default host | Home/root Hermes yang dipilih; gunakan nilai eksplisit agar tidak mengarah ke profil lain. |
| `--timeout` | opsional; default 180 | Batas waktu dalam detik; bukan janji waktu selesai. Desktop menerima 30-600. |
| `--check-only` | opsional; default Tidak/OFF | Reclaim marker yang aman dan prewarm gateway, lalu keluar tanpa membuka UI Desktop; bukan read-only murni. |
| `--software-rendering` | opsional; default Tidak/OFF | Use Hermes' supported GPU fallback for this Desktop launch only |
| `--install-shortcut` | opsional; default Tidak/OFF | Back up existing Hermes shortcuts and use gateway prewarming on future launches |

## 8. `msshi audit`

Memeriksa struktur paket/profil, hash preservasi, scope skill, konfigurasi guard, serta bukti operasi yang sudah direkam. Tidak mengulang model, render, browser atau probe layanan.

**Prasyarat.** Paket lokal; audit profil lengkap membutuhkan bukti/receipt yang relevan pada home yang diaudit.

**Mulai dari.**

```powershell
msshi audit --package-only
```

**Batas dan efek.** PASS berarti pemeriksaan dalam scope lulus, bukan seluruh layanan eksternal terautentikasi atau semua tugas produksi telah diuji. Instalasi publik baru dapat memiliki PENDING karena belum ada bukti operasi. --output menulis agregat; pilih nama baru, jangan menimpa proof/config JSON. Auditor menolak jenis overwrite yang tidak cocok.

### `msshi audit`

Efek: Baca saja, kecuali file agregat JSON yang dipilih lewat --output.

```text
usage: msshi audit [-h] [--home HOME] [--repo REPO] [--output OUTPUT]
                   [--package-only] [--baseline BASELINE]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--home` | opsional; default HERMES_HOME / default host | Home data yang dituju; lihat catatan keluarga karena managed memakai state MSSHI, bukan home Hermes. |
| `--repo` | opsional; default root paket aktif | Root paket/source yang diaudit; default adalah source aktif. |
| `--output` | opsional; default tidak diisi | Tujuan output baru. Jangan memakai file input/config/proof yang belum ditinjau sebagai target overwrite. |
| `--package-only` | opsional; default Tidak/OFF | Batasi audit ke paket, tanpa menganggap runtime/profil pribadi sudah terpasang. |
| `--baseline` | opsional; default tidak diisi | Rilis/baseline pembanding yang dipilih; bukan izin mengubah provider/model. |

## 9. `msshi doctor`

Periksa paritas paket, dependensi skripsi, tool lokal dan lokasi data adaptif.

**Prasyarat.** Paket lokal dan lokasi Hermes yang terdeteksi; tidak perlu model atau layanan berbayar.

**Mulai dari.**

```powershell
msshi doctor --json
```

**Batas dan efek.** Status HEALTHY mengikuti cek spesifik yang dilaporkan; tidak membuktikan semua koneksi aplikasi atau akun telah dipakai.

### `msshi doctor`

Efek: Diagnostik lokal; tidak memulai model/chat/render.

```text
usage: msshi doctor [-h] [--json]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--json` | opsional; default Tidak/OFF | Print JSON output. |

## 10. `msshi skripsi`

Merakit template skripsi Word dari pedoman, metadata kampus, bahan referensi dan preset metode.

**Prasyarat.** python-docx/lxml dan input milik pengguna. Temuan daring serta isi dokumen perlu diperiksa sendiri.

**Mulai dari.**

```powershell
msshi skripsi --help
```

**Batas dan efek.** Template adalah kerangka yang dapat diedit, bukan hasil riset, naskah skripsi selesai atau jaminan kesesuaian pedoman. Tanpa --no-online dapat mengakses web; tanpa --no-open dapat membuka Word.

### `msshi skripsi`

Efek: Membaca bahan dan menghasilkan DOCX; install-deps mengunduh dependensi, lookup daring dan membuka hasil bersifat opsional.

```text
usage: msshi skripsi [-h] [--universitas UNIVERSITAS] [--fakultas FAKULTAS]
                     [--prodi PRODI]
                     [--preset {informatika_ilkom,kuantitatif,kualitatif,rnd,ptk}]
                     [--out-dir OUT_DIR] [--out OUT] [--no-online]
                     [--find-pedoman] [--install-deps] [--no-open]
                     [--non-interactive]
                     [paths ...]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `paths` | opsional; default tidak diisi | File yang di-drag-and-drop: .zip (MuZA_Search), .pdf/.docx (Pedoman), .ris, .csv/.xlsx, .json, atau .png logo. |
| `--universitas` | opsional; default teks kosong | Nama universitas (mis. Universitas Negeri Semarang). |
| `--fakultas` | opsional; default teks kosong | Nama fakultas. |
| `--prodi` | opsional; default teks kosong | Nama program studi. |
| `--preset` | opsional; default informatika_ilkom | Kerangka metode skripsi yang dipilih; periksa isi/format terhadap pedoman kampus. Nilai: informatika_ilkom, kuantitatif, kualitatif, rnd, ptk. |
| `--out-dir` | opsional; default tidak diisi | Folder output kustom (default: D:\HermesData\Skripsi_Output atau ~/Documents/MuZA_Skripsi_Output). |
| `--out` | opsional; default tidak diisi | Path file .docx output lengkap. |
| `--no-online` | opsional; default Tidak/OFF | Nonaktifkan pencarian logo/pejabat online. |
| `--find-pedoman` | opsional; default Tidak/OFF | Cari juga tautan PDF pedoman kampus saat lookup online. |
| `--install-deps` | opsional; default Tidak/OFF | Otomatis pasang python-docx/lxml ke folder adaptif HermesData/skripsi-pylibs bila belum ada. |
| `--no-open` | opsional; default Tidak/OFF | Jangan otomatis membuka hasil .docx di Word. |
| `--non-interactive` | opsional; default Tidak/OFF | Jalankan tanpa prompt interaktif. |

## 11. `msshi assets`

Mencari SOUL, sampel suara, nama file terkait katalog Notebook/knowledge base, dan arsip bahan personal pada root yang Anda tentukan.

**Prasyarat.** Folder yang memang boleh diperiksa. Scan membaca metadata dan dapat membaca daftar isi ZIP yang cocok; tidak mengunggah berkas.

**Mulai dari.**

```powershell
msshi assets --root "C:\BahanPersona"
```

**Batas dan efek.** Hasil adalah inventaris lokal, bukan koneksi NotebookLM atau bukti ada 600 dokumen yang sudah diunduh. Path hasil dapat bersifat pribadi; simpan output secara privat.

### `msshi assets`

Efek: Membaca folder/arsip; menulis JSON hanya bila --output dipilih.

```text
usage: msshi assets [-h] --root ROOT [--output OUTPUT]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--root` | wajib; default tidak diisi; boleh diulang | Root bahan personal yang boleh dipindai; boleh diulang untuk beberapa lokasi. |
| `--output` | opsional; default tidak diisi | Tujuan output baru. Jangan memakai file input/config/proof yang belum ditinjau sebagai target overwrite. |

## 12. `msshi compact`

Meringkas representasi file konteks lokal: menghapus whitespace JSON atau merangkum pengulangan baris log. Hasil utama ke stdout, metadata perubahan ke stderr.

**Prasyarat.** File teks UTF-8 yang relevan, ukuran dalam anggaran baca.

**Mulai dari.**

```powershell
msshi compact "C:\MSSHI-Latihan\contoh.json" --format json
```

**Batas dan efek.** Mode log bertanda lossy:true dan menyandikan pengulangan baris; jangan mengganti bukti log asli. JSON menggunakan parser/dumper standar, bukan verifikasi typed-Decimal milik hook Llmtrim. Tidak mengubah file input; bukan jaminan persentase penghematan seluruh tagihan.

### `msshi compact`

Efek: Baca file dan cetak ringkasan; tidak memanggil LLM atau menulis input.

```text
usage: msshi compact [-h] [--format {json,log,auto}] [--max-bytes MAX_BYTES]
                     file
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `file` | wajib; default tidak diisi | File teks lokal yang akan diringkas; input asli tetap dipertahankan. |
| `--format` | opsional; default auto | auto memakai ekstensi .json sebagai JSON, selainnya log; mode log bersifat lossy. Nilai: json, log, auto. |
| `--max-bytes` | opsional; default 4194304 | Batas baca input compact: default 4 MiB, rentang 1 byte sampai 16 MiB. |

## 13. `msshi browser`

Memasang atau memeriksa kebijakan Steel sebagai jalur browsing umum, menilai prasyarat akses akun personal/transfer, dan memulihkan transaksi Steel yang cocok.

**Prasyarat.** Untuk status cukup konfigurasi lokal. Pemakaian Steel nyata memerlukan endpoint/API key dan izin tugas. Browser personal memerlukan persetujuan terikat situs, akun, tujuan dan cakupan.

**Mulai dari.**

```powershell
msshi browser --hermes-home "C:\HermesClient" --status
```

**Batas dan efek.** --approved/--approval-note merepresentasikan persetujuan nyata, bukan tombol untuk mengarang izin. --account-transfer adalah penilaian izin transfer, bukan penyalinan cookie otomatis. --install dapat mengambil source pin dan menulis plugin/guard, tanpa sesi API. --steel-ready usang dan diabaikan.

| Pemilih tindakan | Fungsi | Efek |
| --- | --- | --- |
| --status | Baca konfigurasi/readiness dan keputusan guard; tidak membuat sesi Steel. | baca lokal |
| --install | Pasang plugin official pin dan guard; tidak meminta key/sesi API. | unduhan/tulis |
| --rollback RECEIPT | Pulihkan transaksi Steel yang tepat, jangan receipt migrasi runtime. | tulis pemulihan |
| --personal-account ... | Nilai permintaan akses akun personal dengan persetujuan terikat tugas. | penilaian izin |
| --account-transfer ... | Nilai kebutuhan persetujuan transfer akun; bukan penyalinan cookie. | penilaian izin |

### `msshi browser`

Efek: Status/penilaian membaca. Install/rollback menulis plugin/kebijakan dan receipt; bukan sesi browsing otomatis.

```text
usage: msshi browser [-h] [--hermes-home HERMES_HOME] [--status] [--install]
                     [--rollback ROLLBACK] [--steel-source STEEL_SOURCE]
                     [--steel-ready] [--personal-account] [--account-transfer]
                     [--approved] [--approval-note APPROVAL_NOTE]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--hermes-home` | opsional; default HERMES_HOME / default host | Home/root Hermes yang dipilih; gunakan nilai eksplisit agar tidak mengarah ke profil lain. |
| `--status` | opsional; default Tidak/OFF | Tampilkan status lokal; efek tepat mengikuti penjelasan keluarga. |
| `--install` | opsional; default Tidak/OFF | Install native official plugin + strict routing; no API session/key prompt. |
| `--rollback` | opsional; default tidak diisi | Restore this profile's Steel receipt; refuse files customized after install. |
| `--steel-source` | opsional; default tidak diisi | Existing checkout at the reviewed pinned Steel commit |
| `--steel-ready` | opsional; default Tidak/OFF | Deprecated; ignored. Readiness is inspected locally. |
| `--personal-account` | opsional; default Tidak/OFF | Tandai kebutuhan akses akun personal agar guard menuntut persetujuan terikat tugas. |
| `--account-transfer` | opsional; default Tidak/OFF | Tandai kebutuhan transfer akun; persetujuan akses biasa tidak otomatis mencakup transfer. |
| `--approved` | opsional; default Tidak/OFF | Hanya gunakan bila persetujuan pengguna memang telah diberikan dalam scope tugas. |
| `--approval-note` | opsional; default teks kosong | Catat situs/akun/tujuan/cakupan persetujuan nyata; tidak boleh berisi rahasia akun. |

## 14. `msshi trim`

Membaca metrik hook Llmtrim otomatis atau memadatkan request JSON lokal melalui binary llmtrim. Hook otomatis hanya memproses hasil tool JSON besar yang memenuhi syarat dan menjaga nilai.

**Prasyarat.** Status memerlukan home/profil yang tepat; kompresi file memerlukan executable llmtrim dan format request yang didukung.

**Mulai dari.**

```powershell
msshi trim --home "C:\HermesClient" --status --profile default
```

**Batas dan efek.** --provider memilih bentuk JSON input, bukan mengganti provider Hermes. Penghematan hanya pada payload yang memenuhi syarat; chat biasa/kode/error/config tidak otomatis dipadatkan. Output baru harus berbeda dari input. Status tidak memanggil model.

| Pemilih tindakan | Fungsi | Efek |
| --- | --- | --- |
| --status | Baca agregat penghitung hook otomatis pada profil. | baca lokal |
| --input FILE | Kompresi request JSON lokal; stdout atau file baru via --output. | utilitas lokal/tulis opsional |

### `msshi trim`

Efek: Status membaca; input menjalankan utilitas lokal, menulis output baru bila diminta.

```text
usage: msshi trim [-h] [--home HOME] [--binary BINARY]
                  (--input INPUT | --status) [--profile PROFILE]
                  [--output OUTPUT]
                  [--provider {openai,anthropic,google,gemini}]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--home` | opsional; default HERMES_HOME / default host | Home data yang dituju; lihat catatan keluarga karena managed memakai state MSSHI, bukan home Hermes. |
| `--binary` | opsional; default tidak diisi | Path executable llmtrim yang telah dipasang; bukan model/provider LLM. |
| `--input` | opsional; default tidak diisi | Path input lokal sesuai format command; pilih file terkontrol yang telah disiapkan. |
| `--status` | opsional; default Tidak/OFF | Tampilkan status lokal; efek tepat mengikuti penjelasan keluarga. |
| `--profile` | opsional; default default | ID folder profil Hermes, misalnya default atau kiki-chii; bukan selalu nama tampilan. |
| `--output` | opsional; default tidak diisi | Tujuan output baru. Jangan memakai file input/config/proof yang belum ditinjau sebagai target overwrite. |
| `--provider` | opsional; default openai | Bentuk request JSON (openai/anthropic/google/gemini); tidak mengubah konfigurasi provider Hermes. Nilai: openai, anthropic, google, gemini. |

Wajib satu dari: `--input`, `--status`.

## 15. `msshi managed`

Mendaftarkan dan memperbarui salinan MSSHI berdasarkan kecocokan isi/fingerprint, termasuk target fisik yang diakses melalui junction yang telah ditinjau.

**Prasyarat.** Source rilis yang sah dan folder skill yang terpisah dari source/state. Backup baseline membantu membuktikan asal versi lama.

**Mulai dari.**

```powershell
msshi managed status
```

**Batas dan efek.** Register tanpa --apply hanya rencana. Salinan yang tidak terbukti atau diedit lokal dipertahankan. --include-optional rea harus eksplisit; tidak otomatis mengadopsi semua REA yang ditemukan. Retarget junction/alias source ambigu ditolak. State updater bukan snapshot seluruh laptop.

| Pemilih tindakan | Fungsi | Efek |
| --- | --- | --- |
| status | Baca apakah target exact/current/custom/blocked tanpa menulis skill. | baca lokal |
| register | Rencanakan enrollment salinan hash-proven; --apply untuk menyimpan. | rencana/tulis state |
| update | Rencanakan refresh source yang terdaftar; --apply untuk menerapkan. | rencana/tulis skill |

### `msshi managed`

Efek: Status membaca; register/update baru menulis bila --apply diberikan.

```text
usage: msshi managed [-h] [--source SOURCE] [--baseline BASELINE]
                     [--skills-dir SKILLS_DIR] [--home HOME] [--apply]
                     [--include-optional {rea}]
                     {register,status,update}
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `action` | wajib; default tidak diisi | Pilih tindakan yang tercantum; bukan nama file atau profil. Nilai: register, status, update. |
| `--source` | opsional; default root paket aktif | Root rilis MSSHI yang akan menjadi sumber salinan/fingerprint. |
| `--baseline` | opsional; default tidak diisi | Snapshot rilis lama untuk membuktikan kecocokan salinan terdahulu. |
| `--skills-dir` | opsional; default kosong; boleh diulang | Folder skill tujuan; flag dapat diulang untuk beberapa folder bila parser memakai append. |
| `--home` | opsional; default MSSHI_HOME / default OS | Folder state/updater MSSHI (MSSHI_HOME), bukan root data Hermes. |
| `--apply` | opsional; default Tidak/OFF | Terapkan rencana yang didukung command ini; tanpa flag managed tetap merencanakan. |
| `--include-optional` | opsional; default kosong; boleh diulang | Explicitly enroll exact copies of this optional wrapper; default is none. Nilai: rea. |

## 16. `msshi services`

Membaca registrasi GitLab/Tinyfish, memasang definisi konektor MCP web, atau melakukan discovery/autentikasi lewat transport native Hermes.

**Prasyarat.** Untuk probe: Hermes source/runtime native dengan dependency MCP, konfigurasi konektor dan akun/login layanan. Registrasi tidak sama dengan autentikasi.

**Mulai dari.**

```powershell
msshi services status --hermes-home "C:\HermesClient"
```

**Batas dan efek.** Probe memakai jaringan dan dapat memakai cache/refresh akun; bukan tes offline. --share-oauth adalah pilihan eksplisit berbagi identitas akun default antarprofil pada Windows, dengan pemeriksaan konflik dan backup. --read-test pada implementasi ini hanya menambah GET token-info GitLab; tidak menjalankan Search/Fetch Tinyfish. Login interaktif tetap melalui hermes mcp login NAMA_LAYANAN.

| Pemilih tindakan | Fungsi | Efek |
| --- | --- | --- |
| status | Baca registrasi/cakupan konektor pada profil. | baca lokal |
| install | Pasang definisi GitLab/Tinyfish; OAuth sharing hanya dengan flag eksplisit. | tulis konfigurasi |
| probe | Lakukan discovery/autentikasi jaringan; kegagalan tidak otomatis membuka login interaktif. | jaringan akun |

### `msshi services`

Efek: Status membaca lokal; install menulis config/cache-link; probe menghubungi layanan. Operasi layanan selanjutnya dapat berkuota/berbiaya.

```text
usage: msshi services [-h] [--hermes-home HERMES_HOME] [--share-oauth]
                      [--service {gitlab,tinyfish}]
                      [--hermes-source HERMES_SOURCE] [--read-test]
                      {status,install,probe}
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `action` | wajib; default tidak diisi | Pilih tindakan yang tercantum; bukan nama file atau profil. Nilai: status, install, probe. |
| `--hermes-home` | opsional; default HERMES_HOME / default host | Home/root Hermes yang dipilih; gunakan nilai eksplisit agar tidak mengarah ke profil lain. |
| `--share-oauth` | opsional; default Tidak/OFF | Explicitly share default workspace identity, after account-conflict checks and private backups |
| `--service` | opsional; default tinyfish | Layanan MCP web yang akan diprobe: gitlab atau tinyfish. Nilai: gitlab, tinyfish. |
| `--hermes-source` | opsional; default tidak diisi | Checkout source Hermes native untuk probe transport; default dicari dari home. |
| `--read-test` | opsional; default Tidak/OFF | Untuk probe GitLab: baca token-info guna memeriksa identitas; bukan uji Fetch Tinyfish. |

## 17. `msshi timesfm`

Menjalankan peramalan deret waktu numerik lokal untuk Val melalui runtime/bobot TimesFM terisolasi. Input/output file menggantikan panggilan API LLM.

**Prasyarat.** Runtime dan bobot yang cocok, RAM/commit/disk cukup, file input numerik valid serta horizon yang masuk batas.

**Mulai dari.**

```powershell
msshi timesfm --hermes-home "C:\HermesClient" status --verify
```

**Batas dan efek.** Install mengunduh dependency/bobot. Smoke dan forecast memuat model lokal, memakai RAM/CPU dan menulis hasil; tidak memakai kredit API LLM tetapi bukan tanpa biaya komputasi. Uji sintetis bukan bukti akurasi pada data pengguna. Subcommand berawalan underscore adalah worker internal.

### `msshi timesfm`

Efek: Status membaca/hash bila verify; install mengunduh; smoke/forecast mengeksekusi model lokal dan menulis proof/output.

```text
usage: msshi timesfm [-h] [--hermes-home HERMES_HOME]
                     {status,install,smoke,_download,forecast,_worker} ...
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--hermes-home` | opsional; default tidak diisi | Home/root Hermes yang dipilih; gunakan nilai eksplisit agar tidak mengarah ke profil lain. |

#### `msshi timesfm status`

Baca readiness lokal; --verify memeriksa hash berkas model/instalasi yang direkam.

Efek: Baca/cetak lokal; opsi verify melakukan hashing, bukan eksekusi model.

```text
usage: msshi timesfm status [-h] [--verify]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--verify` | opsional; default Tidak/OFF | Cocokkan hash runtime/file/proof yang direkam; tidak menjalankan ulang model/render/demo. |

#### `msshi timesfm install`

Unduh dependency dan bobot TimesFM ke runtime privat.

Efek: Instalasi nyata: unduhan/build atau pemasangan berkas. Prasyarat/izin terpisah berlaku.

```text
usage: msshi timesfm install [-h]
```

Tidak ada flag khusus pada node ini selain `-h/--help`; opsi shared keluarga diletakkan sebelum subcommand.

#### `msshi timesfm smoke`

Jalankan peramalan kecil sintetis lokal dan tulis bukti diagnostik.

Efek: Menjalankan fixture/proses lokal dan menulis proof; dapat memakai CPU/RAM/disk.

```text
usage: msshi timesfm smoke [-h]
```

Tidak ada flag khusus pada node ini selain `-h/--help`; opsi shared keluarga diletakkan sebelum subcommand.

#### `msshi timesfm _download`

Worker internal pemasangan bobot; jangan dipanggil sebagai alur penggunaan rutin.

Efek: Internal; dipanggil wrapper pengguna, jangan dijalankan manual.

```text
usage: msshi timesfm _download [-h]
```

Tidak ada flag khusus pada node ini selain `-h/--help`; opsi shared keluarga diletakkan sebelum subcommand.

#### `msshi timesfm forecast`

Jalankan model lokal atas file input numerik, simpan forecast baru.

Efek: Status membaca/hash bila verify; install mengunduh; smoke/forecast mengeksekusi model lokal dan menulis proof/output.

```text
usage: msshi timesfm forecast [-h] --input INPUT --output OUTPUT
                              [--horizon 1..128]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--input` | wajib; default tidak diisi | Path input lokal sesuai format command; pilih file terkontrol yang telah disiapkan. |
| `--output` | wajib; default tidak diisi | Tujuan output baru. Jangan memakai file input/config/proof yang belum ditinjau sebagai target overwrite. |
| `--horizon` | opsional; default 12 | Jumlah titik masa depan yang diprediksi; rentang 1-128, default 12. Nilai: 1..128. |

#### `msshi timesfm _worker`

Worker internal inferensi; gunakan forecast untuk guard dan format output pengguna.

Efek: Internal; dipanggil wrapper pengguna, jangan dijalankan manual.

```text
usage: msshi timesfm _worker [-h] --input INPUT --output OUTPUT
                             [--horizon 1..128]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--input` | wajib; default tidak diisi | Path input lokal sesuai format command; pilih file terkontrol yang telah disiapkan. |
| `--output` | wajib; default tidak diisi | Tujuan output baru. Jangan memakai file input/config/proof yang belum ditinjau sebagai target overwrite. |
| `--horizon` | opsional; default 12 | Jumlah titik masa depan yang diprediksi; rentang 1-128, default 12. Nilai: 1..128. |

## 18. `msshi brag`

Membuat tiga berkas brief/konsep/review untuk video peluncuran, lalu memeriksa/merender komposisi HTML yang dibuat pada tahap berikut melalui Hyperframes pin lokal. Kiki tetap Concepting First.

**Prasyarat.** Untuk init cukup source proyek dan folder output baru. Check/render perlu Node, runtime Hyperframes yang telah disiapkan, browser/FFmpeg, RAM/disk dan hak aset.

**Mulai dari.**

```powershell
msshi brag doctor --hermes-root "C:\HermesClient"
```

**Batas dan efek.** Tidak ada subcommand install di wrapper BRAG; ikuti petunjuk setup runtime pada docs/BRAG.md. Init hanya membuat request.json, CONCEPT.md, REVIEW.md; durasi awal wajib 15-25 detik dan belum ada index.html atau video. Check/render memerlukan komposisi index.html yang dibuat setelah tahapan review. Render membuat MP4; resource guard bisa menolak. Delivery memerlukan --human-approved-preview yang mencerminkan review nyata. Font publik dapat diunduh bila belum dilokalkan.

### `msshi brag`

Efek: Doctor membaca lokal; init menulis scaffold; check/render menjalankan browser/renderer lokal dan menghasilkan artefak.

```text
usage: msshi brag [-h] {doctor,init,renderer,check,render} ...
```

Tidak ada flag khusus pada node ini selain `-h/--help`; opsi shared keluarga diletakkan sebelum subcommand.

#### `msshi brag doctor`

Baca tool/version/receipt lokal tanpa unduhan atau membuka browser.

Efek: Baca/cetak lokal; opsi verify melakukan hashing, bukan eksekusi model.

```text
usage: msshi brag doctor [-h] [--hermes-root HERMES_ROOT] [--runtime RUNTIME]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--hermes-root` | opsional; default tidak diisi | Root Hermes untuk mencari runtime BRAG privat; nama flag ini berbeda dari --hermes-home. |
| `--runtime` | opsional; default tidak diisi | Lokasi runtime BRAG Hyperframes yang telah disiapkan; bukan instruksi mengunduh otomatis. |

#### `msshi brag init`

Buat request.json, CONCEPT.md dan REVIEW.md pada folder baru; belum membuat storyboard, index.html atau MP4.

Efek: Doctor membaca lokal; init menulis scaffold; check/render menjalankan browser/renderer lokal dan menghasilkan artefak.

```text
usage: msshi brag init [-h] --project PROJECT --output OUTPUT [--title TITLE]
                       [--duration DURATION]
                       [--format {landscape,vertical,square}] [--tone TONE]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--project` | wajib; default tidak diisi | Folder source proyek atau komposisi HTML yang dipilih; init membuat scaffold terpisah. |
| `--output` | wajib; default tidak diisi | Tujuan output baru. Jangan memakai file input/config/proof yang belum ditinjau sebagai target overwrite. |
| `--title` | opsional; default Project launch | Judul proyek/video pada scaffold baru. |
| `--duration` | opsional; default 20 | Durasi brief awal dalam detik, wajib 15-25, default 20; bukan jumlah menit. |
| `--format` | opsional; default landscape | Aspek komposisi landscape, vertical atau square pada scaffold. Nilai: landscape, vertical, square. |
| `--tone` | opsional; default polished | Arah rasa/gaya brief yang direkam pada scaffold, misalnya polished. |

#### `msshi brag renderer`

Bentuk umum doctor/check/render pada runtime pin; dapat membuat folder runtime dan menjalankan CLI lokal.

Efek: Doctor membaca lokal; init menulis scaffold; check/render menjalankan browser/renderer lokal dan menghasilkan artefak.

```text
usage: msshi brag renderer [-h] [--hermes-root HERMES_ROOT]
                           [--runtime RUNTIME] [--project PROJECT]
                           [--output OUTPUT] [--quality {draft,delivery}]
                           [--human-approved-preview]
                           {doctor,check,render}
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `action` | wajib; default tidak diisi | Pilih tindakan yang tercantum; bukan nama file atau profil. Nilai: doctor, check, render. |
| `--hermes-root` | opsional; default tidak diisi | Root Hermes untuk mencari runtime BRAG privat; nama flag ini berbeda dari --hermes-home. |
| `--runtime` | opsional; default tidak diisi | Lokasi runtime BRAG Hyperframes yang telah disiapkan; bukan instruksi mengunduh otomatis. |
| `--project` | opsional; default tidak diisi | Folder source proyek atau komposisi HTML yang dipilih; init membuat scaffold terpisah. |
| `--output` | opsional; default tidak diisi | Tujuan output baru. Jangan memakai file input/config/proof yang belum ditinjau sebagai target overwrite. |
| `--quality` | opsional; default draft | draft untuk preview; delivery untuk keluaran akhir setelah review yang nyata. Nilai: draft, delivery. |
| `--human-approved-preview` | opsional; default Tidak/OFF | Pernyataan bahwa preview memang sudah disetujui; wajib untuk delivery. |

#### `msshi brag check`

Validasi komposisi lokal melalui renderer; bisa membuka Chrome headless lokal.

Efek: Doctor membaca lokal; init menulis scaffold; check/render menjalankan browser/renderer lokal dan menghasilkan artefak.

```text
usage: msshi brag check [-h] [--hermes-root HERMES_ROOT] [--runtime RUNTIME]
                        --project PROJECT [--output OUTPUT]
                        [--quality {draft,delivery}]
                        [--human-approved-preview]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--hermes-root` | opsional; default tidak diisi | Root Hermes untuk mencari runtime BRAG privat; nama flag ini berbeda dari --hermes-home. |
| `--runtime` | opsional; default tidak diisi | Lokasi runtime BRAG Hyperframes yang telah disiapkan; bukan instruksi mengunduh otomatis. |
| `--project` | wajib; default tidak diisi | Folder source proyek atau komposisi HTML yang dipilih; init membuat scaffold terpisah. |
| `--output` | opsional; default tidak diisi | Tujuan output baru. Jangan memakai file input/config/proof yang belum ditinjau sebagai target overwrite. |
| `--quality` | opsional; default draft | draft untuk preview; delivery untuk keluaran akhir setelah review yang nyata. Nilai: draft, delivery. |
| `--human-approved-preview` | opsional; default Tidak/OFF | Pernyataan bahwa preview memang sudah disetujui; wajib untuk delivery. |

#### `msshi brag render`

Render komposisi menjadi video; kualitas delivery memerlukan preview yang benar-benar disetujui.

Efek: Doctor membaca lokal; init menulis scaffold; check/render menjalankan browser/renderer lokal dan menghasilkan artefak.

```text
usage: msshi brag render [-h] [--hermes-root HERMES_ROOT] [--runtime RUNTIME]
                         --project PROJECT [--output OUTPUT]
                         [--quality {draft,delivery}]
                         [--human-approved-preview]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--hermes-root` | opsional; default tidak diisi | Root Hermes untuk mencari runtime BRAG privat; nama flag ini berbeda dari --hermes-home. |
| `--runtime` | opsional; default tidak diisi | Lokasi runtime BRAG Hyperframes yang telah disiapkan; bukan instruksi mengunduh otomatis. |
| `--project` | wajib; default tidak diisi | Folder source proyek atau komposisi HTML yang dipilih; init membuat scaffold terpisah. |
| `--output` | opsional; default tidak diisi | Tujuan output baru. Jangan memakai file input/config/proof yang belum ditinjau sebagai target overwrite. |
| `--quality` | opsional; default draft | draft untuk preview; delivery untuk keluaran akhir setelah review yang nyata. Nilai: draft, delivery. |
| `--human-approved-preview` | opsional; default Tidak/OFF | Pernyataan bahwa preview memang sudah disetujui; wajib untuk delivery. |

## 19. `msshi scrapling`

Parser HTML lokal dengan selector CSS/XPath untuk Val dan Coder. Menghasilkan JSON terstruktur tanpa menyediakan crawler jaringan atau browser stealth.

**Prasyarat.** Runtime parser dan dependency Python yang kompatibel; file HTML UTF-8 lokal. Gunakan output baru.

**Mulai dari.**

```powershell
msshi scrapling --hermes-home "C:\HermesClient" status --verify
```

**Batas dan efek.** Adapter ini tidak menerima URL untuk HTTP fetch, sesi browser, CAPTCHA, atau JavaScript. Input dibatasi 4 MiB; hasil 2 MiB dan jumlah cocok sesuai limit. Install Windows x64/CPython 3.12 memakai wheel terkunci; platform lain perlu tinjauan tersendiri. Worker underscore bukan command pengguna.

### `msshi scrapling`

Efek: Status membaca; install mengunduh wheel; selftest/parse menjalankan parser lokal dan menulis proof/output yang baru.

```text
usage: msshi scrapling [-h] [--hermes-home HERMES_HOME]
                       {status,install,selftest,_inventory,parse,_parse} ...
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--hermes-home` | opsional; default tidak diisi | Home/root Hermes yang dipilih; gunakan nilai eksplisit agar tidak mengarah ke profil lain. |

#### `msshi scrapling status`

Baca readiness parser lokal; verify mencocokkan file dependency yang direkam.

Efek: Baca/cetak lokal; opsi verify melakukan hashing, bukan eksekusi model.

```text
usage: msshi scrapling status [-h] [--verify]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--verify` | opsional; default Tidak/OFF | Cocokkan hash runtime/file/proof yang direkam; tidak menjalankan ulang model/render/demo. |

#### `msshi scrapling install`

Unduh wheel parser hash-locked ke environment terisolasi.

Efek: Instalasi nyata: unduhan/build atau pemasangan berkas. Prasyarat/izin terpisah berlaku.

```text
usage: msshi scrapling install [-h]
```

Tidak ada flag khusus pada node ini selain `-h/--help`; opsi shared keluarga diletakkan sebelum subcommand.

#### `msshi scrapling selftest`

Uji HTML sintetis dan boundary input/output lokal, tulis audit diagnostik.

Efek: Menjalankan fixture/proses lokal dan menulis proof; dapat memakai CPU/RAM/disk.

```text
usage: msshi scrapling selftest [-h]
```

Tidak ada flag khusus pada node ini selain `-h/--help`; opsi shared keluarga diletakkan sebelum subcommand.

#### `msshi scrapling _inventory`

Worker internal inventaris package; gunakan status --verify untuk pemeriksaan pengguna.

Efek: Internal; dipanggil wrapper pengguna, jangan dijalankan manual.

```text
usage: msshi scrapling _inventory [-h]
```

Tidak ada flag khusus pada node ini selain `-h/--help`; opsi shared keluarga diletakkan sebelum subcommand.

#### `msshi scrapling parse`

Ekstrak HTML lokal dengan salah satu CSS atau XPath ke JSON baru.

Efek: Status membaca; install mengunduh wheel; selftest/parse menjalankan parser lokal dan menulis proof/output yang baru.

```text
usage: msshi scrapling parse [-h] --input INPUT --output OUTPUT
                             (--css CSS | --xpath XPATH) [--limit 1..1000]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--input` | wajib; default tidak diisi | Path input lokal sesuai format command; pilih file terkontrol yang telah disiapkan. |
| `--output` | wajib; default tidak diisi | Tujuan output baru. Jangan memakai file input/config/proof yang belum ditinjau sebagai target overwrite. |
| `--css` | opsional; default tidak diisi | Selector CSS untuk file HTML lokal; pilih salah satu CSS atau XPath. |
| `--xpath` | opsional; default tidak diisi | Selector XPath untuk file HTML lokal; pilih salah satu CSS atau XPath. |
| `--limit` | opsional; default 100 | Batas jumlah hasil cocok, 1-1000, default 100; metadata menjelaskan hasil terpotong. Nilai: 1..1000. |

Wajib satu dari: `--css`, `--xpath`.

#### `msshi scrapling _parse`

Worker internal parser; gunakan parse untuk validasi dan file output pengguna.

Efek: Internal; dipanggil wrapper pengguna, jangan dijalankan manual.

```text
usage: msshi scrapling _parse [-h] --input INPUT (--css CSS | --xpath XPATH)
                              [--limit 1..1000]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--input` | wajib; default tidak diisi | Path input lokal sesuai format command; pilih file terkontrol yang telah disiapkan. |
| `--css` | opsional; default tidak diisi | Selector CSS untuk file HTML lokal; pilih salah satu CSS atau XPath. |
| `--xpath` | opsional; default tidak diisi | Selector XPath untuk file HTML lokal; pilih salah satu CSS atau XPath. |
| `--limit` | opsional; default 100 | Batas jumlah hasil cocok, 1-1000, default 100; metadata menjelaskan hasil terpotong. Nilai: 1..1000. |

Wajib satu dari: `--css`, `--xpath`.

## 20. `msshi harness2`

Menyusun proposal Propose-Probe-Compose dan menjalankan demo deterministik perbaikan harness dalam salinan terisolasi. Instruksinya tersedia bagi kelima bot sesuai bidang, dengan hasil dibawa untuk review manusia.

**Prasyarat.** Plan tidak perlu model. Demo memerlukan runtime yang diverifikasi; instalasi membutuhkan Python/dependency dan checkout Harness2 pada commit pin yang tepat.

**Mulai dari.**

```powershell
msshi harness2 --hermes-home "C:\HermesClient" status --verify
msshi harness2 plan --goal "Uji hipotesis evaluasi yang sempit"
```

**Batas dan efek.** Tidak menjalankan benchmark LLM berbayar, tidak otomatis melatih/ganti model, dan tidak mempromosikan perubahan ke bot aktif. Adaptasi Windows hanya demo deterministik; upstream menargetkan Linux. --source adalah checkout pin, bukan URL bebas.

### `msshi harness2`

Efek: Status/plan membaca atau mencetak proposal. Install mengunduh build dependency; demo menjalankan worker lokal dan menulis proof.

```text
usage: msshi harness2 [-h] [--hermes-home HERMES_HOME]
                      {status,install,demo,plan} ...
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--hermes-home` | opsional; default tidak diisi | Home/root Hermes yang dipilih; gunakan nilai eksplisit agar tidak mengarah ke profil lain. |

#### `msshi harness2 status`

Baca readiness dan hash runtime/proof yang tersedia.

Efek: Baca/cetak lokal; opsi verify melakukan hashing, bukan eksekusi model.

```text
usage: msshi harness2 status [-h] [--verify]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--verify` | opsional; default Tidak/OFF | Cocokkan hash runtime/file/proof yang direkam; tidak menjalankan ulang model/render/demo. |

#### `msshi harness2 install`

Bangun runtime dari checkout source pada commit yang diverifikasi; install dependency build terkunci.

Efek: Instalasi nyata: unduhan/build atau pemasangan berkas. Prasyarat/izin terpisah berlaku.

```text
usage: msshi harness2 install [-h] [--source SOURCE]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--source` | opsional; default tidak diisi | Checkout Harness2 pada commit pin yang tepat; path lokal, bukan URL bebas. |

#### `msshi harness2 demo`

Jalankan demo deterministik dalam folder baru, lalu tulis proof/worker log.

Efek: Menjalankan fixture/proses lokal dan menulis proof; dapat memakai CPU/RAM/disk.

```text
usage: msshi harness2 demo [-h] [--output OUTPUT]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--output` | opsional; default tidak diisi | Tujuan output baru. Jangan memakai file input/config/proof yang belum ditinjau sebagai target overwrite. |

#### `msshi harness2 plan`

Cetak proposal eksperimen dan pembagian peran tanpa menjalankan benchmark/model.

Efek: Baca/cetak lokal; opsi verify melakukan hashing, bukan eksekusi model.

```text
usage: msshi harness2 plan [-h] [--goal GOAL]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--goal` | opsional; default Evaluate a narrow harness improvement without changing live Hermes | Hipotesis/tujuan eksperimen yang sempit untuk proposal Harness2, bukan perintah promosi otomatis. |

## 21. `msshi optional`

Melihat dan mengaktifkan wrapper tambahan di luar paket standar. Pada rilis ini opsi publik adalah REA, default OFF; preset merekomendasikannya hanya untuk Coder bila pengguna memilih.

**Prasyarat.** Untuk list hanya paket lokal. Enable memerlukan folder skill tujuan; runtime baru dipasang bila --install-runtime dipilih secara eksplisit.

**Mulai dari.**

```powershell
msshi optional list --lang id
```

**Batas dan efek.** Enable hanya wrapper ringan dan enrollment updater, bukan aktivasi semua kemampuan upstream. Runtime REA perlu Node/npm kompatibel; engine Ghidra/Hopper/Kuna tetap terpisah dan belum dibuktikan semua formatnya. Folder kustom yang bentrok dipertahankan.

### `msshi optional`

Efek: List membaca. Enable menyalin wrapper/state; --install-runtime menambah unduhan npm terisolasi.

```text
usage: msshi optional [-h] [--source SOURCE] {list,enable} ...
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--source` | opsional; default root paket aktif | Root paket MSSHI yang mendeklarasikan optional/manifest.json. |

#### `msshi optional list`

Baca fungsi opsi, prasyarat runtime, peran rekomendasi dan default publik OFF.

Efek: List membaca. Enable menyalin wrapper/state; --install-runtime menambah unduhan npm terisolasi.

```text
usage: msshi optional list [-h] [--lang {id,en}]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--lang` | opsional; default id | Bahasa penjelasan id/en; ID dan format input tetap sama. Nilai: id, en. |

#### `msshi optional enable`

Salin/enroll wrapper opsional yang dipilih; runtime hanya jika --install-runtime diminta.

Efek: List membaca. Enable menyalin wrapper/state; --install-runtime menambah unduhan npm terisolasi.

```text
usage: msshi optional enable [-h] --target-dir TARGET_DIR [--install-runtime]
                             [--hermes-home HERMES_HOME]
                             {rea}
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `name` | wajib; default tidak diisi | Nama opsi eksplisit yang tersedia; rilis ini rea. Nilai: rea. |
| `--target-dir` | wajib; default tidak diisi | Folder skill untuk solo/selective atau induk workspace untuk mode tim. |
| `--install-runtime` | opsional; default Tidak/OFF | Pasang runtime/dependency lokal secara eksplisit; dapat memakai internet/disk dan uji CPU. |
| `--hermes-home` | opsional; default tidak diisi | Home/root Hermes yang dipilih; gunakan nilai eksplisit agar tidak mengarah ke profil lain. |

## 22. `msshi rea`

Analisis statis JavaScript/aplikasi yang diekstrak dan inventaris artefak lokal, dengan jalur native eksplisit bila engine tersedia. Digunakan pada target milik pengguna atau yang diizinkan.

**Prasyarat.** Wrapper dan runtime rea-agents pin. Analisis native perlu engine yang dipilih, lisensi/platform/dependency yang cocok dan satu target biner terotorisasi.

**Mulai dari.**

```powershell
msshi rea --hermes-home "C:\HermesClient" status
```

**Batas dan efek.** Cakupan fixture integrasi adalah JavaScript dan ZIP, bukan pembuktian semua delapan format inspect atau engine native pada mesin pelanggan. JavaScript dianalisis statis; target tidak sengaja dijalankan. IDA tidak diekspos karena jalur upstream memerlukan MCP. Output harus baru dan di luar input; runtime tidak memasang engine native, model, atau server MCP baru.

### `msshi rea`

Efek: Status membaca; install mengunduh npm; selftest/analisis menjalankan utilitas lokal, native dapat memulai engine; hasil baru ditulis.

```text
usage: msshi rea [-h] [--hermes-home HERMES_HOME]
                 {status,install,selftest,javascript,inspect,native} ...
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--hermes-home` | opsional; default tidak diisi | Home/root Hermes yang dipilih; gunakan nilai eksplisit agar tidak mengarah ke profil lain. |

#### `msshi rea status`

Baca runtime, versi dan deteksi engine lokal; deteksi bukan uji analisis semua format.

Efek: Baca/cetak lokal; opsi verify melakukan hashing, bukan eksekusi model.

```text
usage: msshi rea status [-h]
```

Tidak ada flag khusus pada node ini selain `-h/--help`; opsi shared keluarga diletakkan sebelum subcommand.

#### `msshi rea install`

Pasang rea-agents pin lewat npm terisolasi dengan lifecycle/optional scripts dibatasi.

Efek: Instalasi nyata: unduhan/build atau pemasangan berkas. Prasyarat/izin terpisah berlaku.

```text
usage: msshi rea install [-h]
```

Tidak ada flag khusus pada node ini selain `-h/--help`; opsi shared keluarga diletakkan sebelum subcommand.

#### `msshi rea selftest`

Jalankan fixture JavaScript dan ZIP milik setup serta boundary refusal; simpan proof.

Efek: Menjalankan fixture/proses lokal dan menulis proof; dapat memakai CPU/RAM/disk.

```text
usage: msshi rea selftest [-h]
```

Tidak ada flag khusus pada node ini selain `-h/--help`; opsi shared keluarga diletakkan sebelum subcommand.

#### `msshi rea javascript`

Analisis statis direktori JavaScript/Electron yang diekstrak atau ASAR, tanpa menjalankan target.

Efek: Status membaca; install mengunduh npm; selftest/analisis menjalankan utilitas lokal, native dapat memulai engine; hasil baru ditulis.

```text
usage: msshi rea javascript [-h] --output OUTPUT
                            [--analysis-timeout-ms 1000..120000]
                            path
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `path` | wajib; default tidak diisi | File/folder input yang dipilih dan diizinkan; tidak sama dengan URL jaringan. |
| `--output` | wajib; default tidak diisi | Tujuan output baru. Jangan memakai file input/config/proof yang belum ditinjau sebagai target overwrite. |
| `--analysis-timeout-ms` | opsional; default 30000 | Batas analisis JavaScript dalam milidetik: 1000-120000, default 30000. Nilai: 1000..120000. |

#### `msshi rea inspect`

Inventaris artefak sesuai jenis; output read-only analysis, tanpa ekstraksi atau eksekusi target.

Efek: Status membaca; install mengunduh npm; selftest/analisis menjalankan utilitas lokal, native dapat memulai engine; hasil baru ditulis.

```text
usage: msshi rea inspect [-h] --output OUTPUT
                         {archive,managed,pe-imports,pe-certificates,go,rust,model,wasm}
                         path
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `kind` | wajib; default tidak diisi | Jenis artefak inspect atau kategori bantuan; daftar nilai sah ditampilkan di sini. Nilai: archive, managed, pe-imports, pe-certificates, go, rust, model, wasm. |
| `path` | wajib; default tidak diisi | File/folder input yang dipilih dan diizinkan; tidak sama dengan URL jaringan. |
| `--output` | wajib; default tidak diisi | Tujuan output baru. Jangan memakai file input/config/proof yang belum ditinjau sebagai target overwrite. |

#### `msshi rea native`

Jalankan operasi pada satu biner melalui engine native yang dipilih secara eksplisit.

Efek: Status membaca; install mengunduh npm; selftest/analisis menjalankan utilitas lokal, native dapat memulai engine; hasil baru ditulis.

```text
usage: msshi rea native [-h] --provider {ghidra,hopper,kuna} [--query QUERY]
                        --output OUTPUT
                        {analyze,search,function,decompile,xrefs,trace} path
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `operation` | wajib; default tidak diisi | Operasi engine native; selain analyze memerlukan --query yang bukan opsi. Nilai: analyze, search, function, decompile, xrefs, trace. |
| `path` | wajib; default tidak diisi | File/folder input yang dipilih dan diizinkan; tidak sama dengan URL jaringan. |
| `--provider` | wajib; default tidak diisi | Engine native eksplisit ghidra/hopper/kuna; perlu engine dan lisensi/dependency terpasang. Nilai: ghidra, hopper, kuna. |
| `--query` | opsional; default tidak diisi | Simbol/alamat/pola untuk operasi native, atau kueri/workspace untuk rute koneksi. |
| `--output` | wajib; default tidak diisi | Tujuan output baru. Jangan memakai file input/config/proof yang belum ditinjau sebagai target overwrite. |

## 23. `msshi choices`

Membaca fungsi, status instruksi, dan prasyarat mode, platform, paket, skill, fitur dan aplikasi. Cocok sebelum memilih opsi yang belum dikenal.

**Prasyarat.** Hanya paket lokal; tidak perlu akun, model, aplikasi kreatif, atau internet.

**Mulai dari.**

```powershell
msshi choices rea
msshi choices --kind apps --lang id
```

**Batas dan efek.** Katalog memiliki 128 nama kanonis: 67 instruksi bawaan dan 61 referensi eksternal; bukan 128 repo. Manifest berisi 52 sumber. Alias bukan skill tambahan; daftar kemampuan tidak membuktikan runtime sudah aktif.

### `msshi choices`

Efek: Baca bantuan lokal saja; tanpa instalasi, probe akun, atau eksekusi alat.

```text
usage: msshi choices [-h]
                     [--kind {all,modes,platforms,packs,skills,features,apps}]
                     [--lang {id,en}] [--json]
                     [item]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `item` | opsional; default tidak diisi | ID pilihan yang ingin dijelaskan, misalnya rea, kat atau unslop; kosong berarti daftar. |
| `--kind` | opsional; default all | Jenis artefak inspect atau kategori bantuan; daftar nilai sah ditampilkan di sini. Nilai: all, modes, platforms, packs, skills, features, apps. |
| `--lang` | opsional; default id | Bahasa penjelasan id/en; ID dan format input tetap sama. Nilai: id, en. |
| `--json` | opsional; default Tidak/OFF | Keluarkan katalog penjelasan sebagai JSON. |

## 24. `msshi manual`

Lihat katalog atau salin/unduh panduan PDF versi tertentu dengan SHA256.

**Prasyarat.** PDF lokal dibundel atau akses GitHub jika belum tersedia; direktori output yang dapat ditulis.

**Mulai dari.**

```powershell
msshi manual list
msshi manual download --version latest --dest "C:\PanduanMSSHI"
```

**Batas dan efek.** PDF adalah panduan; runtime dan akun tidak ikut dipasang dengan membuka PDF. Berkas tujuan berbeda dicadangkan sebelum diganti.

### `msshi manual`

Efek: List membaca; download menulis PDF/backup dan dapat mengambil file dari GitHub.

```text
usage: msshi manual [-h] {list,download} ...
```

Tidak ada flag khusus pada node ini selain `-h/--help`; opsi shared keluarga diletakkan sebelum subcommand.

#### `msshi manual list`

Baca katalog PDF versi yang tersedia; source lokal diutamakan, katalog dapat diambil dari GitHub jika tidak dibundel.

Efek: List membaca; download menulis PDF/backup dan dapat mengambil file dari GitHub.

```text
usage: msshi manual list [-h]
```

Tidak ada flag khusus pada node ini selain `-h/--help`; opsi shared keluarga diletakkan sebelum subcommand.

#### `msshi manual download`

Salin/unduh PDF sesuai versi dengan pemeriksaan SHA256. Identik dibiarkan; file berbeda pada nama tujuan dicadangkan sebelum diganti.

Efek: List membaca; download menulis PDF/backup dan dapat mengambil file dari GitHub.

```text
usage: msshi manual download [-h] [--version VERSION] [--dest DEST] [--json]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--version` | opsional; default latest | Versi PDF: latest atau versi yang tercantum di msshi manual list. |
| `--dest` | opsional; default tidak diisi | Folder tujuan salinan PDF panduan, bukan path file rahasia atau folder skill. |
| `--json` | opsional; default Tidak/OFF | Cetak output sebagai JSON. |

## 25. `msshi dream`

Membuat proposal rangkuman/pelajaran lokal dan deterministik dari bahan yang relevan, atau mendaftarkan jadwalnya. Proposal harus ditinjau sebelum menjadi memori aktif.

**Prasyarat.** Home Hermes dan bahan yang tersedia. Scheduler lokal diperlukan untuk registrasi jadwal.

**Mulai dari.**

```powershell
msshi dream --help
```

**Batas dan efek.** Tidak ada status-only flag di keluarga dream. --run-now menulis proposal; --register mengubah jadwal. Alur ini tidak memanggil LLM dan tidak otomatis mengubah SOUL/memori. Batas baca input bukan kuota RAM keras proses OS.

| Pemilih tindakan | Fungsi | Efek |
| --- | --- | --- |
| --run-now | Buat proposal pembelajaran lokal untuk ditinjau. | baca/tulis lokal |
| --register | Daftarkan jadwal proposal lokal; tidak mempromosikan memori otomatis. | tulis scheduler |

### `msshi dream`

Efek: Run-now membaca dan menulis proposal; register menulis jadwal/metadata, tidak memulai aplikasi kreatif.

```text
usage: msshi dream [-h] [--home HOME] (--run-now | --register)
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--home` | opsional; default HERMES_HOME / default host | Home data yang dituju; lihat catatan keluarga karena managed memakai state MSSHI, bukan home Hermes. |
| `--run-now` | opsional; default Tidak/OFF | Buat proposal dreaming lokal sekarang; dapat membaca bahan dan menulis proof/proposal. |
| `--register` | opsional; default Tidak/OFF | Daftarkan jadwal dreaming lokal, bukan status-only. |

Wajib satu dari: `--run-now`, `--register`.

## 26. `msshi voice`

Status, pemasangan dan aktivasi OmniVoice lokal sebagai TTS native Hermes, serta preferensi gaya suara per peran. Audio dipakai ketika diminta atau fitur read-aloud host aktif.

**Prasyarat.** Bobot/dependency lokal, RAM/disk, hak penggunaan lisensi model dan kemampuan audio/TTS host. Install-runtime melakukan uji sintesis lokal.

**Mulai dari.**

```powershell
msshi voice --home "C:\HermesClient" --status
```

**Batas dan efek.** Tidak ada --text untuk sintesis langsung pada wrapper ini. Setelah enable, minta audio melalui tool TTS Hermes. --enable mengubah bagian TTS lima profil setelah uji lokal terverifikasi; tidak mengganti provider/model LLM. Bobot memakai lisensi nonkomersial; jangan menganggap output komersial otomatis diizinkan.

| Pemilih tindakan | Fungsi | Efek |
| --- | --- | --- |
| --status | Baca runtime/model/proof sintesis lokal. | baca lokal |
| --install-runtime | Unduh dependency/bobot dan lakukan uji sintesis CPU. | unduhan/eksekusi lokal |
| --enable | Set TTS lima profil setelah sintesis terverifikasi, tanpa perubahan LLM. | tulis konfigurasi TTS |
| --role ROLE --state STATE | Simpan preferensi prosodi dari pilihan pengguna. | tulis preferensi |

### `msshi voice`

Efek: Status membaca. Install-runtime mengunduh/menguji model; enable menulis konfigurasi TTS; state menulis preferensi suara.

```text
usage: msshi voice [-h] [--home HOME] [--status] [--enable]
                                [--install-runtime]
                                [--role {yukino,shizuka,val,kiki-chii,shikaku}]
                                [--state {normal,calm,tired,incident}]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--home` | opsional; default HERMES_HOME / default host | Home data yang dituju; lihat catatan keluarga karena managed memakai state MSSHI, bukan home Hermes. |
| `--status` | opsional; default Tidak/OFF | Tampilkan status lokal; efek tepat mengikuti penjelasan keluarga. |
| `--enable` | opsional; default Tidak/OFF | Aktifkan TTS lokal yang telah lolos uji pada konfigurasi profil. |
| `--install-runtime` | opsional; default Tidak/OFF | Pasang runtime/dependency lokal secara eksplisit; dapat memakai internet/disk dan uji CPU. |
| `--role` | opsional; default tidak diisi | Peran suara: yukino, shizuka, val, kiki-chii atau shikaku. Nilai: yukino, shizuka, val, kiki-chii, shikaku. |
| `--state` | opsional; default tidak diisi | Preferensi suara normal/calm/tired/incident; berdasarkan pilihan pengguna, bukan diagnosis. Nilai: normal, calm, tired, incident. |

## 27. `msshi kat`

Alias kompatibilitas KAT: status membaca, pilihan light/ideal/cloud membuka wizard endpoint/key khusus Coder; skip menonaktifkan KAT saja.

**Prasyarat.** Status membaca konfigurasi lokal. Aktivasi membutuhkan profil Shikaku, backend native, endpoint nyata, key akun dan bukti ID model. Dev memerlukan deployment sendiri; preset resmi StreamLake Pro v2.5 adalah varian berbeda dengan penagihan akun sendiri.

**Mulai dari.**

```powershell
msshi kat --home "C:\HermesClient" --mode status
```

**Batas dan efek.** Pilihan light/ideal/cloud membuka wizard endpoint yang sama, tanpa unduhan bobot atau janji model 35B muat di RAM 16 GB. Key dapat dibaca secara tersembunyi; GET /models hanya memeriksa metadata. Helper dapat aktif bila seluruh prasyarat terpenuhi; configured_not_inference_tested tidak membuktikan chat atau saldo akun. Model utama/MoA/delegasi biasa tetap utuh.

| Pemilih tindakan | Fungsi | Efek |
| --- | --- | --- |
| --mode status | Baca endpoint, varian, key-present dan kesiapan native yang direkam, tanpa inferensi. | baca lokal |
| --mode skip | Nonaktifkan helper KAT saja; model utama/delegasi biasa tetap tersedia. | tulis state privat |
| --mode light | Alias menuju wizard endpoint/key; tidak mengunduh atau memuat model lokal. | tulis privat/metadata opsional |
| --mode ideal | Alias menuju wizard endpoint yang sama; tidak memasang Q4 atau menjanjikan kecukupan RAM. | tulis privat/metadata opsional |
| --mode cloud | Buka wizard Dev/custom deployment atau StreamLake Pro berbeda varian; key/billing akun diperlukan. | tulis privat/metadata opsional |

### `msshi kat`

Efek: Status membaca; skip menonaktifkan helper, pilihan lain dapat menulis konfigurasi endpoint/key privat dan mengambil metadata katalog; tidak menjalankan inferensi.

```text
usage: msshi kat [-h] [--home HOME]
                              [--mode {skip,cloud,light,ideal,status}]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--home` | opsional; default HERMES_HOME / default host | Home data yang dituju; lihat catatan keluarga karena managed memakai state MSSHI, bukan home Hermes. |
| `--mode` | opsional; default status | Pilih mode operasi; daftar nilai sah dan artinya ada pada tabel tindakan. Nilai: skip, cloud, light, ideal, status. |

## 28. `msshi coder`

Atur model KAT opsional khusus subtask Coder melalui endpoint yang benar, input key privat, dan katalog model.

**Prasyarat.** Profil shikaku dan backend native msshi-team. Dev memerlukan deployment sendiri; StreamLake Pro adalah varian berbeda dan memerlukan akun/keynya.

**Mulai dari.**

```powershell
msshi coder --home "C:\HermesClient" presets
msshi coder --home "C:\HermesClient" wizard
msshi coder --home "C:\HermesClient" status
```

**Batas dan efek.** Tidak mengubah model utama/MoA/delegasi biasa. GET /models tidak menghasilkan token inference. Tanpa key/endpoint/bukti model tetap nonaktif; status konfigurasi bukan uji inference.

### `msshi coder`

Efek: Status/presets membaca; wizard/configure/disable menulis state privat, read-key hanya ke .env Coder dengan backup; probe mengambil metadata.

```text
usage: msshi coder [-h] [--home HOME] [--mode {status,skip,cloud,light,ideal}]
                   {status,presets,wizard,disable,configure} ...
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--home/--hermes-home` | opsional; default HERMES_HOME / default host | Home data yang dituju; lihat catatan keluarga karena managed memakai state MSSHI, bukan home Hermes. |
| `--mode` | opsional; default tidak diisi | Pilih mode operasi; daftar nilai sah dan artinya ada pada tabel tindakan. Nilai: status, skip, cloud, light, ideal. |

#### `msshi coder status`

Baca kesiapan KAT serta deteksi binary Goose tanpa panggilan endpoint; Goose adalah agen eksternal, bukan model MoA.

Efek: Baca/cetak lokal; opsi verify melakukan hashing, bukan eksekusi model.

```text
usage: msshi coder status [-h]
```

Tidak ada flag khusus pada node ini selain `-h/--help`; opsi shared keluarga diletakkan sebelum subcommand.

#### `msshi coder presets`

Tampilkan pilihan model/endpoint terverifikasi: Exact Dev membutuhkan deployment nyata; StreamLake Pro v2.5 berbeda varian dan membutuhkan key akun.

Efek: Status/presets membaca; wizard/configure/disable menulis state privat, read-key hanya ke .env Coder dengan backup; probe mengambil metadata.

```text
usage: msshi coder presets [-h]
```

Tidak ada flag khusus pada node ini selain `-h/--help`; opsi shared keluarga diletakkan sebelum subcommand.

#### `msshi coder wizard`

Pilih endpoint/model dan input key tersembunyi secara interaktif; metadata diprobe, tanpa inferensi. Tanpa interaksi hanya menyiapkan state pending.

Efek: Dapat menulis endpoint/state/key privat dan GET metadata katalog; tidak melakukan inferensi.

```text
usage: msshi coder wizard [-h]
```

Tidak ada flag khusus pada node ini selain `-h/--help`; opsi shared keluarga diletakkan sebelum subcommand.

#### `msshi coder disable`

Nonaktifkan KAT saja, tetap simpan pilihan model utama/delegasi biasa dan konfigurasi lainnya.

Efek: Menulis state helper nonaktif, tanpa mengubah pilihan model utama atau MoA.

```text
usage: msshi coder disable [-h]
```

Tidak ada flag khusus pada node ini selain `-h/--help`; opsi shared keluarga diletakkan sebelum subcommand.

#### `msshi coder configure`

Simpan endpoint dan referensi key; --read-key membaca key privat. --probe hanya GET /models. --activate mengaktifkan rute jika key, bukti model dan backend native siap; --accept-documented-model khusus preset StreamLake resmi.

Efek: Dapat menulis endpoint/state/key privat dan GET metadata katalog; tidak melakukan inferensi.

```text
usage: msshi coder configure [-h]
                             [--preset {exact-dev,streamlake-payg,custom}]
                             [--base-url BASE_URL] [--model MODEL]
                             [--api-key-env API_KEY_ENV] [--read-key]
                             [--probe] [--activate]
                             [--accept-documented-model]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--preset` | opsional; default exact-dev | exact-dev/custom perlu endpoint nyata; streamlake-payg menggunakan Pro v2.5 berbeda varian dan key akun sendiri. Nilai: exact-dev, streamlake-payg, custom. |
| `--base-url` | opsional; default tidak diisi | Base URL endpoint OpenAI-compatible yang nyata; HTTPS di luar localhost, tanpa key/query tertanam. |
| `--model` | opsional; default tidak diisi | ID model KAT yang benar pada deployment; tidak mengganti model utama Coder atau MoA. |
| `--api-key-env` | opsional; default MSSHI_KAT_API_KEY | Nama variabel lingkungan tempat key privat disimpan, bukan nilai key. |
| `--read-key` | opsional; default Tidak/OFF | Baca key lewat prompt terminal tersembunyi dan simpan hanya pada .env privat Coder dengan backup. |
| `--probe` | opsional; default Tidak/OFF | Ambil metadata katalog model lewat GET /models; tanpa chat/completion atau inference. |
| `--activate` | opsional; default Tidak/OFF | Aktifkan helper hanya jika endpoint, key, ID model terverifikasi dan backend native tersedia. |
| `--accept-documented-model` | opsional; default Tidak/OFF | Terima ID resmi preset StreamLake Pro yang persis didokumentasikan; tidak membuktikan inferensi atau saldo. |

## 29. `msshi setup`

Wizard awal empat mode: semua skill standar pada satu agen, tim kustom, paket kategori terpilih, atau preset lima peran. Penjelasan muncul sebelum pilihan; rencana ditampilkan sebelum penerapan.

**Prasyarat.** Tentukan host dan folder tujuan. Pada Hermes yang didukung, preset menyiapkan lima profil native bernama; default tetap Hermes netral. Host lain memakai workspace yang dihubungkan sesuai kemampuan host.

**Mulai dari.**

```powershell
msshi setup --platform hermes --lang id
```

**Batas dan efek.** KAT opsional membuka wizard endpoint/key; aktif hanya saat prasyarat model dan native routing tersedia. Tidak mengunduh bobot. REA default Tidak/OFF; --with-rea opt-in wrapper, runtime tetap terpisah. Custom team memilih sendiri bot penerima REA. Setup tidak menjamin semua aplikasi/model/akun eksternal tersedia.

### `msshi setup`

Efek: Menulis skill, profil native/workspace, kebijakan koordinasi, receipt dan state sesudah rencana diterapkan. KAT membuka setup endpoint/key privat. PDF disalin otomatis kecuali --no-pdf; task model tidak dikirim saat instalasi.

```text
usage: msshi setup [-h]
                   [--platform {hermes,openclaw,claude,codex,antigravity,manual}]
                   [--target-dir TARGET_DIR] [--lang {id,en}]
                   [--mode {solo,custom-bots,selective,muza-preset}] [--yes]
                   [--default-bot {auto,yukino,keep-hermes}]
                   [--extra-packs EXTRA_PACKS [EXTRA_PACKS ...]]
                   [--extra-skills EXTRA_SKILLS [EXTRA_SKILLS ...]]
                   [--kat-mode {light,ideal,cloud,skip}] [--stage-auto-trim]
                   [--install-steel]
                   [--connect-services {skip,per-profile,share-oauth}]
                   [--connect-apps {skip,auto-reconnect,select}]
                   [--connect-bots CONNECT_BOTS]
                   [--connect-targets CONNECT_TARGETS] [--with-rea]
                   [--download-pdf] [--no-pdf] [--pdf-version PDF_VERSION]
                   [--pdf-dest PDF_DEST]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--platform` | opsional; default tidak diisi | Host tujuan: hermes/openclaw/claude/codex/antigravity/manual. Nilai: hermes, openclaw, claude, codex, antigravity, manual. |
| `--target-dir` | opsional; default tidak diisi | Folder skill untuk solo/selective atau induk workspace untuk mode tim. |
| `--lang` | opsional; default id | Bahasa penjelasan id/en; ID dan format input tetap sama. Nilai: id, en. |
| `--mode` | opsional; default tidak diisi | Pilih mode operasi; daftar nilai sah dan artinya ada pada tabel tindakan. Nilai: solo, custom-bots, selective, muza-preset. |
| `--yes/-y` | opsional; default Tidak/OFF | Konfirmasi otomatis tanpa prompt. |
| `--default-bot` | opsional; default auto | Pada Hermes preset, default tetap netral dan Yukino profil bernama. keep-hermes juga memperbaiki label root duplikat; auto/yukino adalah alias kompatibilitas. Nilai: auto, yukino, keep-hermes. |
| `--extra-packs` | opsional; default tidak diisi | Tambahkan extra packs di langkah [1/4] Skills. |
| `--extra-skills` | opsional; default tidak diisi | Tambahkan extra skill slugs di langkah [1/4] Skills. |
| `--kat-mode` | opsional; default tidak diisi | Pilihan kompatibilitas light/ideal/cloud membuka wizard endpoint; skip menonaktifkan KAT saja. Tidak ada unduhan model lokal. Nilai: light, ideal, cloud, skip. |
| `--stage-auto-trim` | opsional; default Tidak/OFF | Stage plugin fail-open msshi-auto-trim ke profil Hermes di langkah [2/4] Plugin. |
| `--install-steel` | opsional; default Tidak/OFF | Opt-in Steel Browser Policy di langkah [2/4] Plugin. |
| `--connect-services` | opsional; default tidak diisi | Atur koneksi MCP GitLab/Tinyfish di langkah [3/4] Koneksi. Nilai: skip, per-profile, share-oauth. |
| `--connect-apps` | opsional; default tidak diisi | Sambungkan Bot -> CLI-Anything -> Apps di langkah [4/4]. Nilai: skip, auto-reconnect, select. |
| `--connect-bots` | opsional; default tidak diisi | Daftar bot (dipisah koma atau 'all') untuk langkah [4/4]. |
| `--connect-targets` | opsional; default tidak diisi | Daftar app target (dipisah koma atau 'detected') untuk langkah [4/4]. |
| `--with-rea` | opsional; default Tidak/OFF | Opt-in analisis statis JavaScript/arsip: pasang instruksi REA; runtime Node/npm dan engine native terpisah. Default OFF. |
| `--download-pdf` | opsional; default Tidak/OFF | Minta pengiriman PDF secara eksplisit; rilis ini juga mengirim otomatis kecuali opt-out. |
| `--no-pdf` | opsional; default Tidak/OFF | Lewati salinan otomatis PDF sesudah instalasi/update; tidak membatalkan pemasangan skill. |
| `--pdf-version` | opsional; default tidak diisi | Versi panduan yang ada di katalog, default latest; PDF berbeda dari pemasangan runtime. |
| `--pdf-dest` | opsional; default tidak diisi | Folder tujuan PDF panduan; default Downloads/MSSHI_Manuals atau folder manual data MSSHI. |

## 30. `msshi select`

Memilih kategori atau skill satu per satu untuk ditambah/diperbarui. Angka, slug, alias, dan all didukung; fondasi wajib tetap disertakan.

**Prasyarat.** Folder target diketahui; source terbaru memerlukan internet kecuali --local.

**Mulai dari.**

```powershell
msshi select --local --platform hermes --lang id
```

**Batas dan efek.** --local memilih dari snapshot aktif di perangkat. Skill yang berubah secara lokal dipertahankan. Memilih wrapper tidak memasang seluruh dependency, akun atau bobot model upstream.

### `msshi select`

Efek: Rencana dulu; setelah diterapkan menulis skill terpilih, backup dan state updater.

```text
usage: msshi select [-h]
                    [--platform {hermes,openclaw,claude,codex,antigravity,manual}]
                    [--target-dir TARGET_DIR] [--lang {id,en}] [--local]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--platform` | opsional; default tidak diisi | Host tujuan: hermes/openclaw/claude/codex/antigravity/manual. Nilai: hermes, openclaw, claude, codex, antigravity, manual. |
| `--target-dir` | opsional; default tidak diisi | Folder skill untuk solo/selective atau induk workspace untuk mode tim. |
| `--lang` | opsional; default id | Bahasa penjelasan id/en; ID dan format input tetap sama. Nilai: id, en. |
| `--local` | opsional; default Tidak/OFF | Pilih dari rilis lokal tanpa mengakses GitHub. |

## 31. `msshi bootstrap`

Mendaftarkan snapshot rilis lokal, launcher global, PATH user dan panduan PDF otomatis. Biasanya dipanggil install.ps1/install.sh, bukan command pekerjaan harian.

**Prasyarat.** Jalankan dari source MSSHI valid dengan Python. Scope bootstrap memakai source yang sedang menjalankan command, bukan mengambil GitHub sendiri.

**Mulai dari.**

```powershell
msshi bootstrap --help
```

**Batas dan efek.** Bootstrap dapat memanggil migrasi Hermes yang terdeteksi sebelum memasang launcher. --no-path hanya menghindari perubahan PATH; bukan mode read-only dan bukan pencegah migrasi. Installer -NoSetup/--no-setup juga hanya melewati wizard, tidak menjamin bootstrap tidak bermigrasi. PDF masuk Downloads/MSSHI_Manuals atau tujuan yang dipilih; --no-pdf/MSSHI_NO_PDF=1 menolak salinan otomatis, --yes tidak menolaknya.

### `msshi bootstrap`

Efek: Menulis snapshot/launcher/state, dapat memperbarui PATH dan memigrasikan profil yang terdeteksi.

```text
usage: msshi bootstrap [-h] [--no-path] [--no-pdf] [--pdf-version PDF_VERSION]
                       [--pdf-dest PDF_DEST]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--no-path` | opsional; default Tidak/OFF | Jangan ubah PATH user. |
| `--no-pdf` | opsional; default Tidak/OFF | Lewati salinan otomatis PDF sesudah instalasi/update; tidak membatalkan pemasangan skill. |
| `--pdf-version` | opsional; default tidak diisi | Versi panduan yang ada di katalog, default latest; PDF berbeda dari pemasangan runtime. |
| `--pdf-dest` | opsional; default tidak diisi | Folder tujuan PDF panduan; default Downloads/MSSHI_Manuals atau folder manual data MSSHI. |

## Rangkaian contoh yang sintaksnya cocok

Contoh di bawah menggambarkan tindakan berbeda; jangan menjalankan seluruh blok sebagai satu checklist. Langkah install/enable/run hanya untuk kebutuhan yang sudah Anda pilih dan prasyarat yang telah diperiksa. Nama file output harus baru; beberapa wrapper sengaja menolak overwrite.

### Tiket dan CLI aplikasi sesuai tugas

```powershell
msshi runtime status --home "C:\HermesClient"
$ticket = msshi runtime ticket --home "C:\HermesClient" `
  --profile kiki-chii --target blender `
  --task "Periksa versi Blender untuk proyek pengguna" --source direct
msshi runtime run --home "C:\HermesClient" --profile kiki-chii `
  --ticket $ticket blender -- --version
```

Tiket satu kali dibuat untuk target dan profil tersebut. `--version` di contoh tetap mengeksekusi proses Blender CLI; bukan cara menguji render, file proyek, atau Lightcraft library. Untuk pekerjaan yang sesungguhnya, agen memilih argumen CLI sesuai dokumentasi aplikasi dan izin tugas. Native CLI yang terdaftar tidak otomatis menyediakan konektor MCP Desktop.

### Pilihan wrapper REA secara eksplisit

```powershell
msshi optional list
msshi optional enable rea `
  --target-dir "C:\HermesClient\profiles\shikaku\skills"
msshi rea --hermes-home "C:\HermesClient" status
```

Blok tersebut hanya memasang instruksi. Jika memang ingin runtime, tambahkan `--install-runtime --hermes-home "C:\HermesClient"` pada enable atau gunakan `msshi rea --hermes-home "C:\HermesClient" install`. Ini unduhan nyata; engine native tidak ikut dipasang. Contoh analisis setelah runtime siap:

```powershell
msshi rea --hermes-home "C:\HermesClient" javascript `
  "C:\MSSHI-Latihan\owned-app" --output "C:\MSSHI-Hasil\app-analysis-baru.json"
msshi rea --hermes-home "C:\HermesClient" inspect archive `
  "C:\MSSHI-Latihan\owned.zip" --output "C:\MSSHI-Hasil\archive-baru.json"
```

### HTML lokal dan forecast lokal

```powershell
msshi scrapling --hermes-home "C:\HermesClient" parse `
  --input "C:\MSSHI-Latihan\saved.html" --css "h1::text" `
  --output "C:\MSSHI-Hasil\judul-baru.json" --limit 100
msshi timesfm --hermes-home "C:\HermesClient" forecast `
  --input "C:\MSSHI-Latihan\series.json" --output "C:\MSSHI-Hasil\forecast-baru.json" `
  --horizon 12
```

Selector/HTML dan struktur series adalah input yang berbeda. Parser tidak mengambil URL. Forecast memerlukan file angka sesuai schema TimesFM yang dijelaskan pada bab data; ia memuat model dan perlu anggaran RAM.

### Konsep, validasi, lalu delivery video

```powershell
msshi brag doctor --hermes-root "C:\HermesClient"
msshi brag init --project "C:\MSSHI-Latihan\Produk" `
  --output "C:\MSSHI-Latihan\VideoDraftBaru" --title "Peluncuran produk" `
  --duration 20 --format vertical
```

Hasil init hanya tiga berkas brief/konsep/review. Setelah pengguna memilih konsep, Kiki/agen menyiapkan skrip, storyboard dan komposisi yang dapat diedit pada folder terpisah, misalnya `C:\MSSHI-Latihan\KomposisiVideo`, berisi `index.html` serta aset yang sah. Tahap pembuatan kreatif itu tidak dilakukan otomatis oleh command init. Setelah komposisi tersebut tersedia:

```powershell
msshi brag check --hermes-root "C:\HermesClient" `
  --project "C:\MSSHI-Latihan\KomposisiVideo"
```

Setelah preview dan hak aset benar-benar ditinjau, barulah render delivery:

```powershell
msshi brag render --hermes-root "C:\HermesClient" `
  --project "C:\MSSHI-Latihan\KomposisiVideo" `
  --output "C:\MSSHI-Hasil\video-final-baru.mp4" `
  --quality delivery --human-approved-preview
```

Durasi 20 di sini detik, bukan 20 menit. Film 10-40 menit memerlukan rencana per adegan, aset, staging, disk/RAM dan review; hasil uji MP4 kecil tidak menjamin proyek panjang akan lolos tanpa penyesuaian. Tidak ada command `msshi remotion`; Remotion/Bang Motion/ArtCraft dipakai melalui alur dan CLI proyek masing-masing bila tersedia.

## Batas cakupan command

Bagian ini mencakup seluruh keluarga CLI global MSSHI pada commit tersebut, termasuk alias, action selector, seluruh flag parser, serta empat worker internal agar inventaris tidak menyembunyikannya. `integrations dream/voice/kat` memiliki bentuk singkat yang sama; duplikasi itu tetap dicatat. Helper source langsung seperti `python scripts/install_msshi.py` dan perintah Hermes native, Git, npm/Skills CLI, FFmpeg atau aplikasi lain bukan subcommand global MSSHI. Gunakan bab instalasi/host dan dokumentasi tool tersebut untuk sintaksnya, bukan mengarang awalan `msshi`.

Periksa `--help` dari versi yang benar setelah update. Versi semantik sama tidak berarti hash commit sama. Jangan menyalin receipt rollback terakhir secara buta: cocokkan `home`, jenis/schema transaksi, daftar perubahan, hash dan backup sebelum memilih `msshi runtime rollback` atau `msshi browser --rollback`. Tidak ada satu command yang memulihkan seluruh laptop.



# 9. Katalog fungsi skill, pilihan fitur, dan aplikasi

Katalog ini membantu memilih instruksi dan fitur. Status dibundel menunjukkan instruksi tersedia dalam paket; runtime/aplikasi/model/akun diperiksa terpisah. Nama referensi eksternal tidak berarti source atau fiturnya sudah aktif.

## Paket kategori

| Paket | Fungsi |
| --- | --- |
| core | Fondasi ideasi, gaya tulisan, persona, OCR, koordinasi, dan akses alat sesuai tugas. |
| filmmaking | Perencanaan film/foto, visual, motion graphics, dan video; produksi memakai alat yang disiapkan terpisah. |
| business | Analisis usaha, skenario keuangan, dan perhitungan bisnis lewat harness lokal. |
| thesis | Ide penelitian, literatur, metode, analisis data, penulisan, revisi, dan presentasi skripsi. |
| webdev | Pemetaan proyek, pengembangan web/UI, eksperimen kode, dan pengujian. |
| cybersec | Pemetaan kode dan panduan audit keamanan pada target yang izinnya jelas; engine dipasang terpisah. |

## Seluruh 67 skill standar

| Skill | Fungsi singkat |
| --- | --- |
| academic-plotting | Menghasilkan figur publikasi dari data dan spesifikasi yang disepakati. |
| ai-research-explore | Merancang eksperimen kandidat yang terpisah dari baseline. |
| ai-research-reproduction | Menetapkan target reproduksi penelitian yang dapat dibuktikan. |
| analyze-project | Memetakan struktur proyek, konfigurasi, titik masuk, dan risiko perubahan. |
| antigravity-webdev-cybersec | Hubungkan pengerjaan web dan evaluasi keamanan terotorisasi dengan Antigravity, Goose, dan alat lokal. |
| auto-curiousity-for-film-making | Menguji kemampuan alat kreatif dan teknik produksi dalam eksperimen terpisah. |
| autoresearch | Mengoordinasikan siklus eksperimen dan sintesis dengan batas berhenti. |
| backward-traceability | Menautkan angka dan hasil laporan kembali ke data, skrip, atau perhitungan. |
| brag | Rancang video peluncuran produk yang dapat diedit dengan Hyperframes, dimulai dari konsep dan review manusia. |
| brainstorming-research-ideas | Memakai kerangka ideasi terstruktur untuk menemukan pertanyaan layak. |
| business-sage | Menyusun analisis usaha, skenario finansial, dan pertanyaan verifikasi aturan yang relevan. |
| career-ops | Bantu CV-lowongan, strategi karier, tracker dan wawancara; source, runtime dan CV pengguna terpisah. |
| chatgpt-hermes-portability-kit | Memandu adaptasi metode dan profil ke platform lain menggunakan sumber yang sah. |
| cli-anything-business-sage | Menjalankan perhitungan bisnis terstruktur melalui harness lokal yang tersedia. |
| cli-anything-universal-bridge | Daftarkan, periksa, dan jalankan rute aplikasi, browser, serta alat agen yang tersedia saat dibutuhkan. |
| creative-thinking-for-research | Mencoba reframing, analogi, dan kombinasi konsep untuk membuka pilihan. |
| data-analysis | Memeriksa kualitas data, asumsi, uji statistik, dan ketidakpastian. |
| deep-research | Menyusun pertanyaan, menelusuri literatur, dan mensintesis bukti yang dapat diperiksa. |
| evaluating-code-models | Menguji keluaran model kode dengan tugas dan tolok ukur yang relevan. |
| evaluating-llms-harness | Rencanakan evaluasi LLM memakai harness yang kompatibel dan anggaran yang disepakati. |
| explore-code | Mengembangkan perubahan eksperimen dalam ruang kerja terisolasi. |
| explore-run | Menjalankan uji terbatas dengan anggaran dan catatan hasil yang jelas. |
| filmmaking-videography-photography-s2 | Menyatukan konsep, pengarahan, kamera, foto, penyuntingan, warna, dan suara. |
| firecrawl-competitive-intel | Membandingkan perubahan produk, harga, dan fitur dengan bukti bertanggal. |
| firecrawl-dashboard-reporting | Mengambil dan memeriksa indikator dasbor untuk pelaporan. |
| firecrawl-deep-research | Mengumpulkan bukti web untuk sintesis dengan atribusi. |
| firecrawl-knowledge-base | Menyiapkan koleksi dokumen, potongan, serta metadata asalnya. |
| firecrawl-research-papers | Menemukan dan memeriksa makalah pada sumber akademik yang relevan. |
| focus-my-energy | Menyesuaikan beban tugas dan langkah awal dengan energi yang dilaporkan pengguna. |
| generate-fresh-ideas | Menghasilkan alternatif dari beberapa lensa kreatif untuk disaring pengguna. |
| get-more-perspectives | Menguji keputusan dari beberapa sudut pandang sebelum memilih. |
| github-research | Menelaah lisensi, rancangan, pemeliharaan, dan kesiapan repositori. |
| harness2 | Kelima bot dapat menyusun proposal dan demo evaluasi harness; tidak mempromosikan perubahan otomatis. |
| higgsfield-skills | Rutekan kebutuhan produksi kreatif ke modul Higgsfield yang sesuai setelah konsep disetujui. |
| humanizer-en | Sunting prosa bahasa Inggris agar terasa alami sambil menjaga makna, suara penulis, dan sitasi. |
| humanizer-indonesia | Sunting prosa bahasa Indonesia sesuai ragam pembaca sambil menjaga makna, istilah, dan sitasi. |
| idea-generation | Mengembangkan dan menyaring gagasan penelitian dalam beberapa putaran. |
| langsmith-observability | Memandu observabilitas dan evaluasi LangSmith pada lingkungan yang disetujui. |
| literature-review | Membangun tinjauan pustaka dengan beberapa perspektif dan jejak sumber. |
| match-my-writing-style | Menerapkan Voice Card yang disediakan pengguna sesuai audiens dan jenis tulisan. |
| math-reasoning | Memeriksa langkah penalaran matematika dan syarat berlakunya. |
| mattpocock-engineering | Pilih disiplin TDD, debugging dan domain model; orkestrator/spec publish hanya saat diminta. |
| motion-graphics-suite | Pilih dan hubungkan empat rujukan motion graphics untuk komposisi yang tetap dapat diedit. |
| muza-skripsi-template | Menyusun template Word (.docx) skripsi/tugas akhir sesuai aturan pedoman kampus, mencari logo & pejabat resmi otomatis, dan menyuntikkan hasil MuZA_Search. |
| nemo-evaluator-sdk | Memandu evaluasi dengan NeMo Evaluator SDK jika dependensinya tersedia. |
| notebooklm-thinking-datascience | Terapkan metode berpikir sistem dan data science dari indeks sumber milik pengguna. |
| novelty-assessment | Menguji klaim kebaruan terhadap studi terdekat dan batas pencarian. |
| paper-context-resolver | Mengikat klaim reproduksi pada bagian, gambar, tabel, atau lampiran makalah. |
| paper-revision | Memetakan catatan revisi ke perubahan konkret dan bukti perbaikan. |
| paper-writing-section | Menyusun dan menyunting bagian naskah akademik dengan dua tahap pemeriksaan. |
| parenting-6d-gad-mdd | Dukung percakapan dengan empati, struktur, dan otonomi; panduan ini tidak menggantikan perawatan klinis. |
| persona-shizuka-yukino-shikaku | Menjaga karakter, kontrak serah terima, dan batas kepemilikan tugas lima bot. |
| phoenix-observability | Memandu tracing dan evaluasi Phoenix tanpa memindahkan data di luar lingkup. |
| prep-for-meetings | Menyusun ringkasan pertemuan dari catatan dan tujuan yang tersedia. |
| prep-for-meetings-2 | Memadatkan bahan pertemuan menjadi pokok bahasan dan kartu pengingat. |
| rea-video | Kiki membedah referensi video ke VIDEO.md; VLM, audio-model dan remake adalah pilihan terpisah. |
| rebuttal-writing | Menyusun jawaban poin demi poin untuk masukan pembimbing atau reviewer. |
| remote-jobs | Cari perusahaan remote dari direktori lokal terpin; lowongan aktif tetap diverifikasi terpisah. |
| research-paper-writing | Memeriksa struktur argumen dan hubungan antara klaim, bukti, serta pembahasan. |
| scrapling | Ekstraksi CSS/XPath dari HTML lokal dalam runtime parser terisolasi. |
| slide-generation | Menyusun presentasi dari argumen, hasil, dan visual yang dapat diverifikasi. |
| symbolic-equation | Mencari kandidat persamaan yang dapat ditafsirkan dan diuji. |
| table-generation | Membangun tabel akademik dari hasil terverifikasi beserta satuan dan catatan. |
| timesfm-forecasting | Prediksi deret waktu numerik secara lokal memakai TimesFM 2.5 setelah setup runtime dan bobot terpisah. |
| unlimited-ocr-2 | Rutekan ekstraksi dokumen dan gambar berhalaman ke OCR yang tersedia dengan penunjuk bukti. |
| unslop | Tinjau dan perbaiki desain antarmuka; skill ini mengubah UI, bukan gaya prosa bot. |
| wise-judgment-and-sovereign-orchestrator | Mengatur pilihan alur, anggaran, persetujuan, delegasi, dan sintesis hasil Val. |

## Fitur opsional dan prasyarat

| Fitur | Fungsi dan syarat |
| --- | --- |
| rea | Analisis statis JavaScript/arsip milik pengguna melalui CLI; berguna untuk memahami aplikasi dan artefak. Default Tidak; pilihan ini hanya memasang wrapper, bukan runtime atau engine native. |
| rea-runtime | Pasang dependency npm REA ke runtime terisolasi; memerlukan Node/npm yang kompatibel dan unduhan internet. Engine seperti Ghidra dipasang terpisah; tidak menambahkan server MCP. |
| pull-upstreams | Unduh repositori referensi eksternal ke cache untuk modul tambahan. Memakai internet dan ruang disk; tidak otomatis menjalankan kode atau menjamin dependency/akun siap. |
| custom-display-names | Ubah nama tampilan bot pada preset; pembagian peran dan ID folder tetap sama. |
| artcraft | Aplikasi kreatif opsional untuk foto, video, audio, desain, dan dokumen melalui adapter yang tersedia. Boleh dilewati; aplikasi, lisensi, atau akun layanan disiapkan terpisah dan tidak dibuka saat boot. |
| kat | Helper KAT opsional khusus Shikaku. Wizard menyiapkan endpoint, ID model dan referensi key; model utama/MoA tetap utuh. Dev perlu deployment nyata; preset resmi StreamLake menggunakan Pro v2.5 yang berbeda dan membutuhkan key serta saldo akun sendiri. |
| kat-light | Alias kompatibilitas pilihan lama: membuka wizard KAT, tanpa mengunduh model lokal. RAM 16 GB tidak membuktikan model muat; pilihan harus memiliki endpoint/key yang valid. |
| kat-ideal | Alias pilihan lama yang membuka wizard endpoint; tidak memasang Q4 atau menjanjikan model 35B muat di laptop. Model utama Coder tidak diganti. |
| kat-cloud | Konfigurasikan endpoint KAT jarak jauh lewat wizard dan input key rahasia. KAT-Coder-V2.5-Dev tidak mendapat URL hosted otomatis; preset StreamLake adalah Pro v2.5, berbayar dan berbeda varian. |
| kat-skip | Nonaktifkan helper KAT khusus Coder; semua model utama, delegasi biasa dan skill coding tetap tersedia. |
| skill-vs-pack | Paket memilih kelompok skill sesuai bidang; skill individual memberi kontrol satu per satu. Skill fondasi wajib tetap disertakan, dan referensi eksternal belum tentu siap dijalankan. |
| voice | Suara lokal OmniVoice untuk audio atau baca-nyaring yang diminta; tidak otomatis menyuarakan setiap chat. Perlu bobot, RAM, dan setup audio; lisensi bobot membatasi penggunaan komersial. |
| dream | Buat proposal rangkuman/pelajaran secara lokal dan deterministik dari bahan terpilih. Tidak memanggil LLM atau otomatis memasukkan proposal ke memori aktif. |
| steel | Browser utama untuk penjelajahan umum jika key/endpoint sudah disiapkan; layanan dapat berbiaya. Akses akun personal perlu persetujuan sesuai tugas, dan login browser lain tidak disalin otomatis. |
| gitlab | Akses proyek GitLab melalui MCP web dengan autentikasi dan izin akun yang sesuai. Baca hanya data dalam lingkup tugas; perubahan proyek memerlukan instruksi yang jelas. |
| tinyfish | Cari atau ambil informasi web melalui MCP web setelah login layanan. Operasi dapat memakai kuota/kredit; registrasi koneksi saja tidak membuktikan autentikasi atau tugas berhasil. |
| brightdata | Layanan pengambilan data web opsional; tetap nonaktif tanpa akun dan API key. Pemakaian perlu setup layanan dan pemeriksaan biaya/kuota sebelum dijalankan. |
| llmtrim | Padatkan keluaran JSON besar yang memenuhi syarat tanpa kehilangan nilai, dengan pemeriksaan kesetaraan. Tidak memadatkan semua chat atau menjamin persentase penghematan tagihan tertentu. |
| hersona | Cari referensi persona dan siapkan draf penyesuaian karakter melalui CLI. Persona aktif tetap mengikuti SOUL native; draf tidak otomatis menimpa pengaturan pengguna. |
| timesfm-runtime | Siapkan dependency dan bobot TimesFM untuk prediksi deret waktu lokal. Memerlukan unduhan, ruang disk, dan RAM cukup; uji kecil bukan jaminan akurasi pada data pengguna. |
| brag-runtime | Siapkan Hyperframes untuk memvalidasi dan merender video lokal dari komposisi HTML yang dapat diedit. Perlu Node, browser/FFmpeg yang sesuai, RAM/disk, dan hak aset; font dapat memerlukan unduhan. |
| scrapling-runtime | Siapkan parser terisolasi untuk ekstraksi CSS/XPath dari file HTML lokal. Memerlukan dependency Python yang kompatibel; opsi ini tidak menyediakan browser stealth atau crawler jaringan. |
| harness2-runtime | Siapkan framework untuk demo perbaikan harness yang deterministik dan proposal eksperimen. Perlu Python/dependency yang kompatibel; benchmark berbasis model dan promosi perubahan ke bot tidak otomatis aktif. |
| managed-update | Perbarui salinan skill yang terdaftar dan fingerprint-nya cocok; pertahankan edit lokal yang berbeda. Pendaftaran ini bukan izin mengganti SOUL, provider/model, atau semua dependency runtime. |
| upstream-cache | Simpan checkout referensi eksternal di luar folder skill agar dapat diperiksa atau diintegrasikan terpisah. Cache memakai internet/disk dan tidak sama dengan fitur yang sudah terpasang atau aktif. |
| setup-skills | Tambahkan paket atau skill individual ekstra dan kelola skill opsional REA per bot saat setup tanpa mengubah skill kustom yang sudah ada. |
| setup-plugins | Kelola plugin Hermes dan integrasi runtime seperti msshi-auto-trim, KAT-Coder, Hermes-Dreaming, OmniVoice, dan Steel Browser Policy secara opsional dan non-destruktif. |
| setup-services | Periksa atau daftarkan koneksi MCP layanan eksternal GitLab dan Tinyfish secara aman per profil atau berbagi OAuth opt-in, sementara BrightData tetap nonaktif. |
| setup-bot-apps | Hubungkan tiap profil bot ke jembatan CLI-Anything dan aplikasi lokal atau web secara on-demand memakai tiket tugas, dengan auto_open_on_boot tetap nonaktif. |
| context-sources | Cache source terpin CareerOps, direktori remote, Matt Pocock dan rea-video di luar skills; default status tidak mengunduh atau menjalankan model. |
| career-ops-runtime | Pasang dependency Node secara eksplisit tanpa lifecycle scripts atau unduhan Chromium; CV/data pengguna tetap privat, tugas dan akun terpisah. |
| rea-video-runtime | Pasang runtime Python terisolasi; analisis lokal dapat melewati OCR/ASR/stems/VLM. Fitur model, unduhan bobot dan generasi tidak otomatis aktif. |

## Pilihan aplikasi pada CLI-Anything

Pilihan ini hanya mengatur registri rute. Aplikasi, runtime, login, izin akun, dan biaya layanan merupakan prasyarat terpisah; tidak ada aplikasi yang dibuka saat boot.

| ID rute | Fungsi dan prasyarat |
| --- | --- |
| existing | Daftarkan ulang konektor Hermes yang sudah aktif pada profil ini; login dan keberhasilan operasi tetap perlu diperiksa terpisah. |
| artcraft | Daftarkan kelompok 15 aplikasi kreatif ArtCraft untuk video, gambar, audio, desain, dokumen, dan 3D; aplikasi/runtime dipasang terpisah. |
| gdrive-web | Akses file Google Drive melalui web ketika tugas memerlukannya; perlu login dan izin akun, mengikuti kebijakan browser aktif. |
| perplexity | Riset dan pencarian melalui Perplexity; akses web/aplikasi serta batas akun diperiksa saat dipakai, tanpa membuka aplikasi sekarang. |
| youtube-chrome | Akses YouTube untuk riset video melalui rute yang tersedia; browser personal memerlukan izin sesuai tugas dan kebijakan aktif. |
| tiktok | Riset konten TikTok melalui web/aplikasi; login, izin akun, dan kebijakan browser tetap berlaku. |
| antigravity | Gunakan IDE Antigravity untuk workspace coding yang dipilih; IDE harus terpasang dan baru dibuka saat ada tugas. |
| blender | Pengerjaan scene, model, animasi, dan render 3D di Blender melalui rute yang terdaftar; perlu Blender dan adapter yang sesuai. |
| blender-cli | Kendalikan Blender lewat harness CLI-Anything untuk tugas 3D/render; perlu Blender dan executable cli-anything-blender. |
| ffmpeg | Konversi, potong, gabungkan, atau periksa media audio/video lewat CLI lokal; perlu executable FFmpeg. |
| cli-hub | Cari dan kelola harness CLI-Anything; menampilkan katalog tidak memasang atau menjalankan harness/aplikasi lain. |
| libreoffice | Tidak diaktifkan pada kebijakan preset MuZA; gunakan aplikasi ArtCraft yang sesuai peran. |
| gimp | Tidak diaktifkan pada kebijakan preset MuZA; gunakan aplikasi ArtCraft yang sesuai peran. |
| obs | Atur scene dan rekaman/streaming OBS melalui harness; mulai merekam atau siaran tetap merupakan tindakan tugas terpisah. |
| audacity | Edit dan olah audio lewat harness Audacity; perlu Audacity dan harness CLI-Anything. |
| inkscape | Buat dan edit grafis vektor/SVG melalui harness Inkscape; perlu Inkscape dan harness CLI-Anything. |
| krita | Ilustrasi dan lukisan digital melalui harness Krita; perlu Krita dan harness CLI-Anything. |
| kdenlive | Susun dan edit timeline video melalui harness Kdenlive; perlu Kdenlive dan harness CLI-Anything. |
| drawio | Buat dan edit diagram alur atau arsitektur melalui harness draw.io; perlu aplikasi dan harness yang sesuai. |
| filmcraft | Pengerjaan video dan timeline editing di FilmCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| effectcraft | Pengerjaan efek visual dan motion di EffectCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| photocraft | Pengerjaan dan penyuntingan foto di PhotoCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| lightcraft | Kelola dan kembangkan foto, warna, serta hasil ekspor di LightCraft; perlu aplikasi/adapter dan library foto yang dapat dipakai. |
| soundcraft | Pengerjaan audio, penyuntingan, dan mixing di SoundCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| designcraft | Pengerjaan desain visual dan layout di DesignCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| vectorcraft | Pengerjaan ilustrasi dan grafis vektor di VectorCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| figcraft | Pengerjaan desain antarmuka dan layout di FigCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| wordcraft | Pengerjaan dokumen teks dan pemformatan di WordCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| gridcraft | Pengerjaan tabel dan spreadsheet di GridCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| deckcraft | Pengerjaan slide dan presentasi di DeckCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| pdfcraft | Pengerjaan dokumen PDF di PDFCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| cadcraft | Pengerjaan gambar dan rancangan CAD di CADCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| solidcraft | Pengerjaan model solid dan rancangan 3D di SolidCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| craftanything | Pengerjaan proyek kreatif melalui Craft Anything; fungsi yang dapat dipanggil bergantung aplikasi/adapter terpasang. |
| materialcraft | Pengerjaan material untuk proyek visual/3D di MaterialCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| texturecraft | Pengerjaan tekstur untuk proyek visual/3D di TextureCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| git | Kelola versi source code dan riwayat perubahan lewat Git; push atau penulisan remote tetap memerlukan izin tugas dan akses akun. |
| gitlab | Akses proyek dan data GitLab melalui adapter yang terdaftar; perlu autentikasi serta izin proyek yang sesuai. |
| mcp:gitlab | Akses proyek, issue, dan data GitLab melalui konektor MCP yang terdaftar; autentikasi dan izin proyek diperiksa terpisah, registrasi bukan bukti operasi berhasil. |
| mcp:tinyfish | Gunakan layanan otomasi/pencarian web Tinyfish melalui MCP untuk tugas yang diizinkan; perlu login serta izin kuota/biaya, registrasi bukan bukti koneksi berhasil. |
| node | Jalankan tool/proyek JavaScript dengan Node.js lokal; memilih rute tidak memasang paket atau menjalankan proyek. |
| python | Jalankan tool/proyek Python lokal; memilih rute tidak memasang dependency atau menjalankan kode. |
| graphify | Petakan hubungan file/kode menjadi graf proyek melalui Graphify lokal; perlu runtime serta input proyek yang dipilih. |
| whatsapp-web | Akses WhatsApp Web saat tugas memerlukannya; perlu sesi akun dan izin terikat tugas, pengiriman pesan memerlukan otorisasi. |
| hersona | Kelola personalisasi/persona melalui Hersona CLI; memilih rute tidak mengubah persona atau konfigurasi model. |
| llmtrim | Padatkan payload yang memenuhi syarat melalui llmtrim CLI; manfaat bergantung input dan tidak menjamin penghematan seluruh tagihan token. |
| anicraft | Animasi 2D/layer/shape dan render headless melalui AniCraft; khusus Kiki-Chii pada preset MuZA, perlu aplikasi CLI yang terpasang. |

## Referensi eksternal pada katalog

Ada 61 nama referensi eksternal pada matriks. REA termasuk daftar penemuan ini tetapi pemasangan instruksinya merupakan opsi khusus default OFF. Sejumlah nama historis memuat kata MCP; arsitektur desktop MuZA v3 tetap memakai rute native CLI, sedangkan MCP web yang dipertahankan mengikuti kebijakan layanan. Daftar ini tidak memerintahkan pemasangan semua repo atau server.

| Nama | Fungsi |
| --- | --- |
| addy-agent-skills | Menerapkan praktik engineering pada implementasi dan review. |
| anti-slop | Memeriksa klise, struktur antarmuka, dan pola kode yang berulang. |
| artcraft-anicraft | Animasi dan komposisi bergerak melalui CLI aplikasi lokal sesuai tiket tugas. |
| artcraft-cadcraft | Gunakan adapter aplikasi yang tersedia untuk gambar teknis dan pengerjaan CAD. |
| artcraft-craftanything | Gunakan adapter aplikasi yang tersedia untuk mengoordinasikan pekerjaan kreatif lintas alat. |
| artcraft-deckcraft | Gunakan adapter aplikasi yang tersedia untuk membuat dan menyunting presentasi. |
| artcraft-designcraft | Gunakan adapter aplikasi yang tersedia untuk membuat dan menyunting desain visual. |
| artcraft-effectcraft | Gunakan adapter aplikasi yang tersedia untuk efek visual dan compositing. |
| artcraft-figcraft | Gunakan adapter aplikasi yang tersedia untuk desain antarmuka dan prototipe. |
| artcraft-filmcraft | Gunakan adapter aplikasi yang tersedia untuk merencanakan adegan dan shot. |
| artcraft-gridcraft | Gunakan adapter aplikasi yang tersedia untuk tabel dan perencanaan produksi. |
| artcraft-lightcraft | Gunakan adapter aplikasi yang tersedia untuk mengolah, memotong, dan mengekspor foto. |
| artcraft-materialcraft | Penyusunan material melalui CLI lokal sesuai tiket tugas. |
| artcraft-pdfcraft | Gunakan adapter aplikasi yang tersedia untuk menyiapkan dokumen PDF. |
| artcraft-photocraft | Gunakan adapter aplikasi yang tersedia untuk mengolah dan meninjau foto. |
| artcraft-solidcraft | Gunakan adapter aplikasi yang tersedia untuk membuat model bentuk padat. |
| artcraft-soundcraft | Gunakan adapter aplikasi yang tersedia untuk rancangan suara dan mixing. |
| artcraft-texturecraft | Penyusunan tekstur melalui CLI lokal sesuai tiket tugas. |
| artcraft-vectorcraft | Gunakan adapter aplikasi yang tersedia untuk membuat dan menyunting aset vektor. |
| artcraft-wordcraft | Gunakan adapter aplikasi yang tersedia untuk menulis dokumen produksi. |
| awesome-copilot | Memilih contoh instruksi dan praktik pengembangan yang dapat diadaptasi. |
| bang-motion | Memandu motion graphics berbasis kode sesuai brief. |
| barty-motion-graphics | Memandu komposisi grafis gerak dan animasi berbasis kode. |
| better-design | Membantu tinjauan kualitas dan hierarki desain. |
| blender-mcp | Koordinasikan adegan 3D dan render melalui adapter Blender yang tersedia; setup desktop memakai CLI native. |
| canvas-ui | Menelaah komponen visual berbasis kanvas untuk interaksi khusus. |
| charlie-motion-graphics | Menyusun pendekatan motion graphics dan urutan gerak dari storyboard. |
| cli-anything | Memanggil CLI atau aplikasi melalui adapter yang dipilih untuk tugas aktif. |
| cli-anything-catalog | Direktori untuk menemukan adapter CLI yang relevan dengan tugas. |
| cursify | Memilih interaksi kursor yang sesuai dengan kebutuhan antarmuka. |
| cybersecurity-library | Menemukan panduan keamanan sesuai lingkup audit yang sah. |
| design-taste | Memilih gaya visual, tipografi, dan komposisi yang sesuai. |
| goose | Menjalankan siklus perubahan kode dan pengujian bila harness Goose tersedia. |
| gpt-researcher | Mengumpulkan dan menyusun bahan riset; Val memeriksa sumber sebelum penyerahan. |
| graphify | Membuat peta struktur proyek untuk penelusuran konteks. |
| hermes-jev-skills | Memilih skill dari konteks dengan pengalihan model dinonaktifkan. |
| hermes-steel | Gunakan integrasi browser Steel yang tersedia untuk tugas penjelajahan yang diizinkan. |
| higgsfield-brandkit | Menerapkan sistem visual merek pada produksi aset. |
| higgsfield-faceless-video | Menyiapkan video tanpa tampil wajah dari skrip, tempo, dan aset. |
| higgsfield-generate | Menghasilkan atau mengolah media setelah konsep dan parameter disetujui. |
| higgsfield-marketplace-cards | Menyusun kartu promosi produk dengan pesan dan spesifikasi kanal. |
| higgsfield-product-photoshoot | Mengatur konsep foto produk, pencahayaan, dan framing. |
| higgsfield-soul-id | Mengelola konsistensi subjek dengan referensi yang diizinkan. |
| higgsfield-video-explainer | Mengubah penjelasan konsep menjadi urutan adegan. |
| higgsfield-websites | Memetakan brief produk ke konsep situs dan aset pendukung. |
| higgsfield-youtube-thumbnail | Membuat konsep thumbnail sesuai isi video dan identitas kanal. |
| mindrally-skills | Menemukan panduan implementasi relevan di katalog eksternal. |
| motion-primitives | Merancang gerak antarmuka memakai komponen animasi. |
| paper-shaders | Menyiapkan efek shader yang terukur dan sesuai perangkat. |
| playwright-best-practices | Menguji jalur pengguna dan memperbaiki kestabilan tes E2E. |
| ponytail | Mengurangi kerumitan solusi dan memilih perubahan yang sesuai kebutuhan. |
| rea | Analisis statis JavaScript atau arsip milik pengguna lewat CLI lokal; format native memerlukan engine terpisah. |
| remotion-skills | Merancang komposisi video sebagai kode dan merendernya bila runtime tersedia. |
| reverse-engineer-anything | Memeriksa artefak insiden secara forensik dalam mandat yang jelas. |
| strix | Menguji keamanan target yang lingkup dan izin aksesnya telah disetujui. |
| superdesign-skill | Menilai tata letak, token desain, dan konsistensi antarmuka. |
| superpowers | Menata perencanaan, implementasi, dan validasi perubahan kode. |
| token-monitor | Sumber status kuota tambahan untuk kebijakan anggaran. |
| tokenshield | Gabungkan data penggunaan, estimasi biaya, dan pemeriksaan anggaran; ini bukan batas tagihan keras dari provider. |
| tokentracker | Sumber data penggunaan lokal untuk kebijakan anggaran. |
| unlimited-ocr | Memandu runtime OCR lokal dan indeks halaman. |

## Alias

| Nama alternatif | Skill kanonis |
| --- | --- |
| auto-curiosity-for-film-making | auto-curiousity-for-film-making |

Sumber: [katalog fungsi](https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/blob/84ecd134f01ec65c4848b4f50c597b811f6b3a80/configs/option_help.json), [matriks peran](https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/blob/84ecd134f01ec65c4848b4f50c597b811f6b3a80/configs/bot_role_and_skill_matrix.json), dan [fungsi koneksi](https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/blob/84ecd134f01ec65c4848b4f50c597b811f6b3a80/skills/cli-anything-universal-bridge/scripts/connection_help.json).


# 10. Pegangan cepat dan bahan latihan

## Lima langkah untuk satu sesi

1. Tentukan hasil kecil: file, laporan, perubahan source, preview, atau keputusan.
2. Periksa fungsi dan kesiapan alat yang diperlukan, dengan help/status yang sesuai.
3. Sediakan input, profil, tujuan output baru, serta batas biaya dan izin.
4. Kerjakan satu tahap, kemudian periksa output/receipt sebelum tahap berikutnya.
5. Simpan source yang dapat diedit, keputusan, dan hasil pemeriksaan bersama proyek.

## Referensi cepat

| Kebutuhan | Mulai dari |
| --- | --- |
| Mengerti opsi | `msshi choices rea` atau `msshi choices --kind packs` |
| Membaca fungsi aplikasi | `msshi choices --kind apps` |
| Memeriksa rute | `msshi connect --status` |
| Memilih paket/skill | `msshi select --local` |
| Memeriksa salinan terkelola | `msshi managed status` |
| Mengambil perbaikan paket | `msshi update --skip-upstreams` dengan home yang tepat |
| Memeriksa bukti lokal | `msshi audit --home "PATH_HERMES"` |
| Memastikan sintaks | `msshi COMMAND --help`, lalu bantuan subcommand |

## Berkas yang menyertai modul

PDF menyediakan daftar isi, bookmark, dan penjelasan. Markdown menyediakan command yang mudah disalin dan dicari. Paket ZIP modul menyertakan inventaris parser JSON dan hasil help sebagai bukti sintaks, serta folder latihan sintetis.

Salin isi folder `latihan/` dari paket ke direktori latihan baru. Contoh buku memakai `D:\MSSHI-Latihan`; pengguna lain dapat menggantinya pada seluruh command. Jangan menimpa folder proyek yang sudah berisi pekerjaan pribadi.

| Bahan | Kegunaan | Hasil yang diperiksa |
| --- | --- | --- |
| `saved.html` | Parser lokal Scrapling | Dua judul pada `expected-titles.txt` |
| `series.json` | Input TimesFM | Satu series, 64 titik numerik; forecast memerlukan runtime/model |
| `owned-js/` | REA JavaScript statis | Laporan struktur; target tidak perlu dieksekusi |
| `owned.zip` | Inventaris arsip REA | Nama anggota arsip fixture |
| `MyApp/` | Brief/konsep BRAG | Folder scaffolding/review baru; composition dibuat pada tahap lanjutan |

Latihan tidak dipaksa berjalan saat membuka modul. Model, layanan, dan render berat tetap dijalankan hanya ketika prasyarat tersedia dan tugasnya memang dipilih. Command internal berawalan garis bawah pada inventaris parser merupakan worker implementasi, bukan langkah penggunaan sehari-hari.

## Catatan penyalinan command

PDF dapat membungkus baris panjang agar muat pada halaman. Untuk menyalin URL/path/command panjang secara presisi, gunakan berkas Markdown. Teks placeholder diganti dengan path atau ID yang sesuai; jangan mengetik kurung siku dari format `usage:` sebagai argumen literal.

## Catatan mutu modul

Versi, commit, jumlah skill/sumber, pilihan, dan sintaks dicocokkan dengan source yang menjadi dasar edisi. Pemeriksaan parser dilakukan sebelum aksi command dijalankan. Contoh latihan adalah bahan ajar; tidak diklaim sebagai hasil uji baru terhadap seluruh model, format, layanan, atau aplikasi. Bila source berubah setelah edisi ini, baca `--help` dan dokumentasi commit yang sedang Anda gunakan.
