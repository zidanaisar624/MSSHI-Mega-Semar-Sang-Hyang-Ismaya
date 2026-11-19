# Modul Pelanggan MSSHI v3.1.2

Edisi distribusi Kamis, 19 November 2026 (Asia/Jakarta). Academic Mahasiswa, Academic Dosen dan MuZA; interaksi dua tipe dan MSSHITrim.

Baseline Git `42cb1dd782e19d697fdf08a3207ba9fa619e0383` ditambah revisi kerja v3.1.2 universal. Manifest source publik: `dfc86245a12eef449c6d524f4ec4b0b87cad1887cea4a61b19702f89eafba15b`. PDF dibuat setelah penangkapan parser, tanpa mengeksekusi aksi CLI/model.

# 1. Mulai di sini: bentuk produk dan cara membaca modul

MSSHI (Mega Semar Sang Hyang Ismaya) adalah kumpulan instruksi skill, kerangka persona/peran, dan alat CLI untuk mengelola pemasangan, pembaruan, serta penggunaan alat sesuai tugas. Agen seperti Hermes membaca instruksi tersebut untuk menentukan alur kerja. Aplikasi kreatif, runtime Python/Node, bobot model, dan akun layanan disiapkan menurut fitur yang dipakai.

Modul pelanggan ini menjelaskan **MSSHI 3.1.2**, berdasarkan source v3.1.2 yang ditinjau pada 19 November 2026; baseline Git `42cb1dd782e19d697fdf08a3207ba9fa619e0383` ditambah revisi universal dua tipe, Academic dan MSSHITrim yang dicatat dengan manifest hash. Edisi: **Kamis, 19 November 2026 (Asia/Jakarta)**. Pembaruan mencakup tata letak lima peran Hermes untuk instalasi baru dan lama, koordinasi peran, sapaan pribadi, protokol SOUL, pembagian aplikasi, KAT opsional/default OFF, integrasi kontekstual, dan penyalinan PDF otomatis. Contoh merupakan petunjuk pemakaian; laporan pengujian pada perangkat tertentu disimpan terpisah. Kode dan bantuan versi terpasang menjadi acuan perilaku command.

Jika Hermes sudah disiapkan untuk Anda, mulai dari Bab 3 dan Praktikum 1; gunakan bot/profil yang diberikan saat serah terima. Bab instalasi ditujukan untuk pemasangan baru atau penyesuaian host. Semua path konkret seperti `C:\HermesClient` adalah contoh: sesuaikan dengan folder instalasi pada perangkat Anda.

## Hasil belajar

Setelah menggunakan modul, Anda dapat memilih jalur instalasi, mengenali fungsi fitur, meminta pekerjaan kepada bot yang sesuai, membaca dan menjalankan perintah yang relevan, membedakan status kesiapan, serta mencari penyebab kegagalan tanpa langsung menghabiskan kredit chat. Bab referensi memuat sintaks dan opsi CLI; latihan menunjukkan pemakaiannya pada pekerjaan kecil.

| Jalur baca | Bagian yang dibaca | Hasil yang dituju |
| --- | --- | --- |
| Baru mengenal MSSHI | Bab 1-5, lalu satu latihan | Dapat mulai tanpa memasang semua integrasi |
| Hermes sudah disiapkan | Bab 3-5, alur lima bot, operasional | Memakai instalasi yang ada tanpa mengulang setup |
| Mencari sebuah command | Referensi CLI dan indeks opsi | Menemukan sintaks, efek, dan prasyarat |
| Menambah skill/aplikasi | Pilihan fitur, CLI-Anything, runtime terkait | Menambah komponen yang memang diperlukan |
| Mengatasi error | Bab operasional dan tabel troubleshooting | Memeriksa bukti serta memulihkan lingkup yang tepat |

## Isi versi ini

| Komponen | Jumlah / fungsi |
| --- | --- |
| Skill standar | 67 folder instruksi: 51 inti dan 16 wrapper integrasi |
| Opsi terpisah | REA berada di `optional/rea`, default publik OFF |
| Referensi upstream | 51 sumber; 48 repositori Git dipatok, dua model-card dan satu registry mengikuti metadata sumber |
| Nama pada katalog skill | 127 nama kanonis: 67 bawaan dan 60 referensi eksternal; banyak nama dapat berkaitan dengan sumber yang sama |
| Paket kategori | `core`, `filmmaking`, `business`, `thesis`, `webdev`, `cybersec` |
| Mode setup | Academic Mahasiswa, Academic Dosen, Solo, Custom Multi-Bot, Selective Packs, Preset MuZA |
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
| MCP web | Konektor layanan web; akun disambungkan sendiri melalui host; MSSHI tidak mengaktifkan GitLab/Tinyfish otomatis |
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

Pada Hermes yang didukung, mode `muza-preset --default-bot auto` membedakan instalasi baru dan tim yang sudah ada. Pada instalasi baru, profil **default yang sebenarnya berubah nama/personanya menjadi Yukino**, lalu empat profil spesialis bernama `shizuka`, `val`, `kiki-chii`, dan `shikaku` disiapkan. Pengaturan model/provider milik default tidak dipindah dari profil lain. Pada instalasi lama yang sudah memiliki Yukino bernama dan default tersendiri, mode auto mempertahankan susunan itu. Profil yang sudah ada mempertahankan SOUL kustom, rahasia dan pilihan modelnya; profil baru mendapatkan konfigurasi awal melalui mekanisme host. Pada host selain Hermes, hasil mode tim tetap berupa workspace portabel dan harus dihubungkan sesuai kemampuan host. Instalasi tidak membuat akun, grup Telegram atau Discord secara otomatis.

Jangan menempelkan API key ke Knowledge Bundle, README publik, screenshot laporan, atau GitHub. Gunakan mekanisme rahasia/akun dari host masing-masing.

# 3. Memilih preset dan menuntaskan pekerjaan akademik

## Enam mode, dua jalur kampus

Pada instalasi baru, pilihan awal diarahkan ke **Academic Mahasiswa S1/S2/S3**.
Academic Dosen/Pimpinan Kampus tersedia sebagai pilihan terpisah. Preset MuZA
tetap ada untuk pengguna yang menginginkan tim kreatif, riset dan coding yang
lebih luas. Memilih preset adalah memilih susunan kerja; nama pembuat preset
bukan nama pengguna dan bukan izin untuk menyalin akun pembuatnya.

| Mode | Untuk siapa | Hasil dan batasnya |
| --- | --- | --- |
| Academic Mahasiswa | Mahasiswa Indonesia S1, S2 atau S3 | Lima peran berfokus pada tugas, belajar, bimbingan, penelitian dan penyelesaian naskah; pilihan awal pemasangan baru |
| Academic Dosen/Pimpinan Kampus | Dosen, pembimbing dan pimpinan kampus | Lima peran berfokus pada pengajaran, RPS, penelitian, rapat dan tindak lanjut |
| Solo 1-Bot | Pengguna yang ingin satu agen | Satu agen memilih alur sesuai tugas; tidak membuat tim lima bot |
| Custom Multi-Bot | Pengguna yang ingin merancang tim | Nama, jumlah dan pembagian tanggung jawab dipilih pengguna |
| Selective Packs | Pengguna yang hanya perlu sebagian kemampuan | Memasang kategori yang dipilih dengan fondasi yang diperlukan |
| Preset 5-Bot MuZA | Pengguna yang ingin ekosistem lintas bidang | Yukino, Shizuka, Val, Kiki-Chii dan Shikaku berkolaborasi sesuai matriks MuZA |

Pemasangan ulang dan pembaruan harus mempertahankan instalasi lama. Periksa
rencana target sebelum menerapkan pilihan: jangan membuat home Hermes kedua
hanya untuk menyamai contoh dalam buku ini. Preset Academic tidak diterapkan
diam-diam ke tim MuZA yang sudah ada. Pada laptop yang sudah memiliki lima bot,
gunakan susunan yang ada kecuali memang ingin mengganti preset.

```powershell
msshi setup --platform hermes --mode academic-mahasiswa --lang id
msshi setup --platform hermes --mode academic-dosen --lang id
```

Pilih salah satu sesuai kebutuhan; kedua baris adalah setup nyata, bukan
pemeriksaan status. Alias `academic-mahasiswa-dosen` memilih jalur Mahasiswa.
Isian opsional `--academic-level S1|S2|S3`, `--academic-topic`,
`--academic-deadline`, `--academic-campus-guideline` dan `--preferred-name`
disimpan secara lokal. Pada perintah, pilih satu nilai jenjang yang sesuai;
jangan mengetik tanda `|` sebagai bagian nilai.

## Lima peran Academic

| Bot | Peran | Keluaran yang dapat ditinjau |
| --- | --- | --- |
| Yukino | Koordinator jadwal, ideasi, kerkom dan rapat | Tujuan kecil, urutan prioritas, kartu kesiapan, jadwal yang diusulkan, pembagian tugas |
| Sensei Shizuka | Pembimbing belajar, mentor sidang dan perancang pembelajaran | Penjelasan sederhana, latihan tanya jawab, strategi belajar, rancangan RPS/modul atau struktur argumen |
| Val | Riset skripsi S1, tesis S2, disertasi S3 dan data | Kata kunci, tabel literatur bersumber, gap yang dapat diperiksa, rancangan metode, analisis dan draf dokumen |
| Kiki-Chii | Presentasi sidang, bahan mengajar dan konten edukasi | Storyboard slide, poster, infografis, naskah atau video yang dapat diedit |
| Sir. Robot / Shikaku | Koding riset, olah data dan automasi | Diagnosis error, perubahan kode kecil, pengujian, pipeline data dan catatan cara menjalankan |

Tugas kecil boleh diselesaikan satu bot. Untuk tugas lintas bidang, tentukan
satu pemilik hasil akhir, lalu delegasikan bagian yang mempunyai tujuan jelas.
Handoff membawa input, output yang diminta, bukti, batas biaya, tenggat dan
pertanyaan terbuka. Bila host tidak menyediakan delegasi antarprofil yang
sesungguhnya, bot harus menyatakan batas itu dan memberikan handoff yang bisa
diteruskan; jangan mengklaim bot lain sudah bekerja ketika belum dipanggil.

## Langkah pertama mahasiswa

Sediakan jenjang S1/S2/S3, program studi, tahap naskah, target yang realistis,
pedoman kampus dan arahan pembimbing yang relevan. Isian yang belum diketahui
boleh tetap kosong. Pilih satu hasil yang bisa dinilai dalam satu sesi.

1. Yukino membantu memperjelas masalah dan langkah terdekat.
2. Shizuka menyusun urutan belajar/kerja dan menerjemahkan masukan pembimbing.
3. Val memeriksa literatur, metode, data dan klaim yang diperlukan.
4. Sir. Robot membantu kode/data bila memang dibutuhkan; Kiki membantu visual.
5. Shizuka menggabungkan hasil; pengguna memeriksa terhadap pedoman dan arahan.

> Saya mahasiswa S1, baru mulai skripsi. Bantu saya memilih satu masalah yang
> mungkin dikerjakan dengan data yang tersedia. Hari ini cukup hasilkan tiga
> kandidat, kelemahannya, bukti yang masih perlu dicari, dan satu langkah besok.
> Jangan dulu menulis seluruh bab atau memakai layanan berbayar.

Untuk S2/S3, nyatakan kedalaman kontribusi dan standar pembimbing. Jangan
menganggap memperpanjang teks S1 otomatis menjadi tesis atau disertasi. Bot
harus membedakan temuan literatur, asumsi, klaim baru dan bukti hasil penelitian.

## Langkah pertama dosen dan pimpinan kampus

Mulai dari mata kuliah/agenda, peserta, durasi, hasil pembelajaran/keputusan,
bahan yang tersedia dan batas yang harus dipatuhi. Gunakan data contoh atau
anonim bila identitas mahasiswa/staf tidak diperlukan.

> Siapkan perkuliahan Zoom 60 menit tentang metode penelitian. Shizuka buat
> tujuan belajar dan alur latihan; Kiki susun storyboard delapan slide; Val
> cek contoh dan rujukan. Saya meninjau sebelum dipakai di kelas. Jangan
> mengirim undangan atau merekam apa pun.

RPS, bahan ajar, disposisi staf dan keputusan rapat adalah draf yang perlu
ditinjau pejabat/pengajar yang berwenang. Koneksi kalender, LMS, Zoom, Gmail,
Telegram, Discord dan WhatsApp tidak disediakan melalui akun pembuat MSSHI.

## Tiga keluaran setiap pertemuan

| Tahap | Keluaran | Sumber dan batas |
| --- | --- | --- |
| Sebelum | Kartu kesiapan 30 detik | Inti pertemuan, yang disetujui, sikap/poin bicara, bahan yang kurang, program yang akan berjalan |
| Sebelum/saat | Rundown menit demi menit | Durasi, agenda, pemilik, hasil, jeda dan alternatif jika demo bermasalah |
| Setelah | Notulensi dan tindak lanjut | Catatan/transkrip nyata: keputusan, pemilik tugas, tenggat, pertanyaan terbuka dan draf ringkasan WhatsApp/LMS |

Sebelum pertemuan berlangsung, keluaran notulensi berupa **kerangka kosong**.
Bot tidak boleh mengarang peserta, keputusan, transkrip atau persetujuan.
Menyiapkan draf jadwal bukan membuat undangan kalender. Menghasilkan draf
ringkasan bukan mengirim pesan ke grup. Perekaman, transkripsi dan penggunaan
model saat sesi perlu pengaturan serta persetujuan yang sesuai.

> Yukino dan Shizuka, siapkan kerkom 45 menit. Tujuannya menyepakati batas
> topik dan pembagian kerja. Buat kartu kesiapan, rundown, daftar bahan yang
> masih kurang, serta kerangka notulensi. Jangan mengirim undangan dulu.

Plugin `meeting-copilot-live`, `transcribo` dan `solverforge-planner` merupakan
integrasi opsional. Protokol dan template tidak membuktikan plugin telah
dipasang, kompatibel dengan Windows, mempunyai akses audio, atau bisa membaca
layar Zoom. Gunakan catatan manual bila prasyarat plugin belum tersedia.

## Catatan bawaan, tanpa aplikasi tambahan

Academic menyimpan konteks dan keluaran di workspace bawaan Hermes pada home
yang dipilih installer. Tidak membuat vault Obsidian, mengubah `.geminiignore`,
memasang `obsidian-memory`, atau mengambil akun Drive/NotebookLM pembuat.

Lokasi bawaan adalah `<HermesHome>/workspace/academic`. `--academic-project`
boleh memilih subfolder lain di dalam `<HermesHome>/workspace`, bukan vault
pribadi di luar home. Installer mengutamakan `HERMES_HOME`/instalasi yang sudah
ada. Untuk pemasangan Windows baru, D: yang bisa ditulis dan mempunyai ruang
cukup dapat dipakai; bila tidak tersedia, gunakan data pengguna pada C:.
Lihat lokasi yang dicetak installer. Jangan membuat jalur D: fiktif di laptop
yang hanya mempunyai C: atau menyalin path pribadi dari contoh orang lain.

Template konteks akademik bersih disediakan untuk profil dan status riset.
Status berisi **Sedang Fokus Apa Sekarang**, **Apa yang Sudah Diselesaikan**,
dan **Target Selanjutnya**. Template pertemuan, kelas Zoom dan target harian
dapat dipakai sebagai dokumen biasa. Jangan memasukkan API key atau token
login ke dalam catatan ini. Folder bernama Private tetap dilarang untuk semua
bot; buat ruang ide bersama yang memang diizinkan bila ingin dibantu merapikan.

## Perangkat ringan dan pilihan aplikasi

Academic mendahulukan dokumen, PDF, tabel, slide, Python dan riset harian yang
tersedia di perangkat. Aplikasi Office/ArtCraft tetap memerlukan instalasi atau
aksesnya sendiri. Nama rute tidak berarti aplikasi disertakan dalam MSSHI.
Periksa katalog/kesiapan sebelum menjalankan.

CAD/3D, Blender, OBS dan cyber runtime tidak menjadi pekerjaan startup atau
unduhan wajib pada laptop RAM 4-8 GB. Rute berat hanya dipertimbangkan setelah
pengguna memilihnya dan aplikasi/prasyaratnya terdeteksi. Dataset besar, OCR
model besar, generasi gambar/video dan model lokal perlu penilaian RAM/disk
terpisah; angka RAM rendah bukan jaminan semua fitur akan muat.

## Model, suara dan akun milik pengguna

Paket publik membagikan persona, skill, plugin yang sesuai dan alur kerja.
Pengguna memilih provider, model dan key melalui pengaturan Hermes sendiri.
SOUL menggambarkan cara bekerja dan batas peran, bukan konfigurasi model.
Saran kemampuan bersifat umum: gunakan model teks yang mendukung tool untuk
kerja agen; pisahkan generator gambar/audio/video dari penasihat teks.

MoA/delegasi adalah kemampuan host dan memiliki biaya tambahan ketika
diaktifkan. Jangan memasukkan model gambar atau TTS ke daftar penasihat teks
hanya karena semua layanan mempunyai ID model. OmniVoice bersifat opsional;
kepribadian teks tidak berarti audio otomatis menyala. Suara perlu runtime,
model suara, pengaturan dan uji yang terpisah sebelum disebut siap.

## Kebiasaan yang membantu cepat selesai

Gunakan target kecil yang terukur, misalnya satu pertanyaan riset yang tajam,
satu tabel sintesis, satu bagian metode, satu grafik atau satu latihan sidang.
Tandai bagian yang belum punya bukti dan pertanyaan untuk pembimbing. Bot boleh
mempercepat pencarian, penyusunan dan pemeriksaan, tetapi tidak mengarang
referensi, data, hasil analisis atau persetujuan pembimbing. Status lulus dan
kelayakan naskah tetap ditetapkan kampus.


# 4. Dua tipe interaksi: percakapan, perencanaan dan eksekusi

<!-- FIGURE: two_types -->

Diagram konsep dari Pengguna untuk MSSHI v3.1.2. Gambar membantu memahami
pembagian kerja; gambar bukan bukti panggilan Advisor, Dewan, tools, atau hasil
runtime telah berhasil. Uraian dan status di bawah menjadi batas penggunaannya.

## Peran tetap, mesin dipilih Pengguna

Academic Mahasiswa, Academic Dosen dan MuZA memakai arsitektur dasar yang sama.
Nama peran menjelaskan tanggung jawab, bukan nama model atau provider yang harus
dibeli. Pengguna menyiapkan mesin, endpoint dan kredensial sendiri di host.
SOUL publik tidak memberikan model, API key, base URL/endpoint pribadi, akun, atau konfigurasi laptop
pembuat. Instruksi perilaku tidak menciptakan tool yang belum tersedia.

| Jalur | Bot | Susunan internal | Siapa memimpin hasil |
| --- | --- | --- | --- |
| Tipe 1 | Yukino dan Sensei Shizuka | Main Agent + Sub-Agent Advisor; tanpa Dewan | Main menerima koreksi, memutuskan rencana dan memimpin eksekusi |
| Tipe 2 | Sir. Robot, Val dan Kiki-Chii | Main Agent + Council berisi Reference Agents dan Aggregator; tanpa Sub-Agent terpisah | Main merencanakan, mengaudit di tengah dua putaran dan memimpin eksekusi |

Lima bot tidak harus bekerja pada setiap pesan. Main menjawab sapaan, pertanyaan
cepat, status dan koreksi kecil secara langsung. Untuk proyek penuh, jelaskan
hasil yang diminta, input, batas file/alat/biaya dan cara menilai hasilnya.
Kata "video", "riset" atau "coding" saja tidak mengizinkan pemanggilan semua
penasihat atau dimulainya pekerjaan panjang.

## Saat permintaan masih ambigu

Ada dua jalur klarifikasi yang berbeda:

1. **Langsung:** jika Pengguna berbicara kepada bot pekerja, bot bertanya balik
   pada percakapan itu tentang maksud, skala atau detail yang belum jelas.
2. **Forward berantai:** jika tugas datang dari Yukino/Shizuka, pekerja bertanya
   kepada pengirim terdekat dengan ID tugas dan kekurangannya. Pengirim meluruskan
   dari konteks yang ada, membatalkan salah panggil, atau membawa pertanyaan
   kepada Pengguna. Jawaban kembali melalui rantai yang sama.

Jangan mengarang maksud atau menjalankan putaran hanya untuk mencari kejelasan.
Jangan mengulang pertanyaan tanpa batas. Jika host tidak menyediakan jalur
balasan/delegasi tersebut, kembalikan kartu klarifikasi atau handoff yang dapat
diteruskan. Nyatakan secara jujur bila komunikasi lintas-bot belum dilakukan.

> Saya hanya ingin bertanya singkat tentang beda metode kuantitatif dan
> kualitatif. Jawab langsung; belum perlu proyek atau Dewan.

> Ini tugas penuh: buat rencana penelitian dari pedoman dan data contoh ini.
> Sebelum bekerja, tanyakan hanya bagian yang belum jelas. Tampilkan rencana,
> sumber yang perlu dicari, pembagian kerja, dan perkiraan biaya untuk saya nilai.

## Tipe 1: Main dan Advisor

Yukino menata ide, jadwal dan kesiapan; Shizuka mengajar, menyusun strategi dan
mengoordinasikan tim. Main menulis rencana awal, meminta Advisor menilai celah,
alternatif dan koreksi yang relevan, lalu memeriksa serta memperbaiki rencana.
Main tetap memimpin komunikasi, keputusan operasional, eksekusi dan verifikasi.

Advisor bukan pengganti Pengguna dan bukan Dewan MoA. Pertanyaan kecil tidak
memerlukan Advisor. Untuk tugas penuh yang memerlukan telaah, konsultasi hanya
disebut selesai jika alat host benar-benar mengembalikan hasil. Jika Advisor
belum disiapkan, tampilkan prasyarat; Main dapat memberi bantuan langsung yang
masih sah atau menyiapkan draf dengan label "belum ditinjau Advisor".

## Tipe 2: tepat dua putaran dengan audit Main

| Tahap | Pelaksana | Keluaran dan pemeriksaan |
| --- | --- | --- |
| Initial Plan | Main | Tujuan, modul/bab/konsep, langkah, input, sumber, alat, batas biaya/izin dan kriteria selesai |
| Putaran 1 | Reference Agents, lalu Aggregator | Koreksi, alternatif, gap, bukti yang kurang dan blueprint awal terpusat |
| Audit Main | Main | Cocokkan blueprint dengan proyek, file, perangkat dan sumber nyata; catat koreksi dan bukti tambahan |
| Putaran 2 | Reference Agents, lalu Aggregator | Tinjau ulang audit Main dan susun blueprint akhir beserta sumber, batas dan perubahan dari putaran pertama |
| Persetujuan dan eksekusi | Main | Terima/tolak rancangan, kerjakan, uji, lalu laporkan hasil dan bagian yang belum terverifikasi |

Dua pemanggilan Dewan berturut-turut tanpa audit Main di antaranya bukan alur
ini. Tidak ada putaran ketiga otomatis. Pekerjaan lanjutan yang memerlukan
evaluasi baru adalah siklus baru dengan tujuan dan biaya yang dijelaskan.
Tidak ada Sub-Agent terpisah di dalam jalur Tipe 2; Reference dan Aggregator
adalah komponen Dewan itu sendiri. Handoff lintas profil adalah koordinasi
keahlian, bukan penambahan pekerja anonim yang selalu aktif.

Aggregator bukan sekadar perangkum. Ia menyatukan bukti, menghapus duplikasi,
menandai celah, mengelola sumber, dan menyusun struktur kode/API, matriks riset,
analisis atau desain visual yang terpusat. Bila komponen Dewan tidak mempunyai
tools, ia mengembalikan permintaan sumber terstruktur kepada Main. Main memakai
alat yang tersedia dan diizinkan, memeriksa asal sumber, lalu mengirim bukti
kembali. URL yang tertulis belum membuktikan halaman telah dibaca. Bukti yang
belum tersedia tetap diberi status belum terverifikasi.

Persetujuan Main merupakan keputusan internal atas blueprint. Ia tidak
menggantikan persetujuan Pengguna untuk biaya baru, pengiriman data, perubahan
berisiko, rekaman, review kreatif final, publikasi atau tindakan di luar mandat.

Dua putaran bukan hanya dua panggilan model. Bila ada tiga Reference Agents
dan satu Aggregator pada tiap putaran, Dewan dapat memerlukan delapan completion
tambahan, di luar komunikasi Main, tools, pencarian atau generasi media. Jumlah
nyata mengikuti konfigurasi dan perilaku host. Gunakan jalur jawaban singkat
untuk pertanyaan kecil dan periksa perkiraan biaya sebelum proyek penuh.

## Runtime, konfigurasi dan batas pengujian

Plugin native `msshi-interaction` mencatat rencana, klarifikasi, putaran pertama,
audit Main, putaran kedua dan persetujuan dalam state proyek. Ia berbeda dari
MoA bawaan host yang dapat bersifat satu putaran atau menjadikan Aggregator
sebagai model pelaksana. Memilih preset MoA pada UI tidak otomatis membuktikan
alur dua putaran yang dikendalikan Main telah berjalan.

```powershell
msshi interaction --protocol
msshi interaction --home "C:\HermesClient" --status
```

Pemeriksaan ini tidak mengirim chat, memanggil Dewan atau memakai model. Tool
native, schema, plugin aktif dan binding konfigurasi perlu tersedia pada sesi
Hermes yang dipakai. Jika Reference Agents atau Aggregator belum diatur,
status harus menyatakan kebutuhan konfigurasi dan berhenti sebelum panggilan
berbayar. Pengguna mengatur komponen itu sendiri; pemasang tidak menciptakan
pilihan model atau mengubah model utama.

Pemasangan plugin dapat ditinjau lebih dahulu:

```powershell
msshi interaction --home "C:\HermesClient" --install
```

Tambahkan `--apply` hanya ketika pemasangan itu memang dipilih. Perintah ini
menyiapkan plugin dan receipt, bukan menjalankan Dewan. Reload plugin/sesi
diperlukan agar schema baru terbaca. Penonaktifan eksplisit atau edit plugin
lokal dipertahankan. Baca referensi CLI untuk opsi dan prasyarat host versi ini.

Di dalam sesi yang menawarkan schema plugin, bot memakai
`msshi_interaction_begin`, `msshi_interaction_step` dan
`msshi_interaction_status`. Aksi Tipe 2 harus berurutan: `council_round`, `audit`,
`council_round`, kemudian `approve`. Aksi Advisor milik Tipe 1. Jangan menyalin
nama tool menjadi slash command jika host tidak menawarkan bentuk tersebut.

Permintaan sumber yang belum selesai dapat dipenuhi Main melalui
`resolve_sources`: lampirkan bukti yang telah diperiksa dan pemetaan permintaan
ke sumbernya setelah putaran pertama, audit Main atau putaran kedua. Pencatatan
ini tidak menambah panggilan LLM atau putaran Dewan. Celah sumber yang belum
dituntaskan menahan persetujuan akhir, kecuali Main secara eksplisit menerima
hasil terbatas dan mengungkap keterbatasannya. Klarifikasi setelah putaran
pertama kembali ke tahap yang sama; jangan mengulang putaran yang sudah selesai
hanya untuk melanjutkan jawaban klarifikasi.

Pengujian dengan respons tiruan membuktikan urutan, batas panggilan dan penolakan
state yang salah. Ia tidak membuktikan kualitas jawaban, saldo, autentikasi atau
kompatibilitas provider nyata. Kehadiran plugin dan status konfigurasi tidak
boleh dilaporkan sebagai "seluruh Dewan siap" tanpa uji yang sesuai dan berizin.

## Sensei Learning Mode, desain dan review

Semua bot dapat menjelaskan konsep, alasan pemilihan, langkah, pola yang bisa
ditiru dan latihan kecil ketika Pengguna ingin belajar. Kedalaman mengikuti
tujuan Pengguna; jawaban cepat tetap ringkas. Saat tenaga berkurang, perkecil
target dan tawarkan pilihan ringan tanpa menebak diagnosis atau menekan.

Untuk UI/web/slide/aset, gaya awal adalah modern-minimalis: grid, ruang kosong,
tipografi jelas, kontras terbaca dan tiga sampai empat warna harmonis. Aksen
anime/kartun berizin digunakan seperlunya. Pedoman kampus, identitas merek,
aksesibilitas dan permintaan Pengguna dapat mengubah gaya tersebut.

Kiki-Chii memulai dengan Concepting First. Tinjau konsep, naskah/storyboard,
rough cut, preview dan final. Video 10-40 menit dibagi per bab/segmen. Pengguna
bisa mengkritik atau mengubah rencana/hasil kapan saja; hentikan automasi yang
terdampak, catat keputusan baru, lalu lanjutkan bagian yang masih sah.

## Handoff untuk Antigravity

Sir. Robot menyusun **MASTER PROMPT HANDOFF UNTUK ANTIGRAVITY** ketika proyek
akan diteruskan: tujuan, keputusan, blueprint, status sumber, struktur berkas,
kontrak fungsi/data, desain, langkah kerja, tes, izin/biaya, hasil yang sudah ada,
kendala dan rollback. Pisahkan rencana dari hasil yang sudah diterapkan dan
teruji. Jangan mengklaim dua putaran riil selesai jika baru membuat draf atau
menguji state dengan respons tiruan.

Handoff publik tidak memuat koneksi pribadi, API key, token, konfigurasi model,
file profil atau vault pemilik. Data yang perlu dibawa ke perangkat lain
dipilih Pengguna secara privat; paket GitHub berisi template dan kemampuan umum.

## Skill, plugin dan aplikasi: otomatis yang mana?

| Komponen | Pemicu | Fungsi | Cara memakai dan batas |
| --- | --- | --- | --- |
| SOUL/persona | Profil dipakai | Mandat, triase, sapaan dan tata kerja | Bercakap pada bot yang sesuai; bukan unduhan model |
| Skill spesialis | Konteks tugas cocok atau nama skill dipanggil | Panduan metode, bukti dan hasil | Sebut keluaran; tidak mengeksekusi seluruh 67 skill |
| Advisor/Dewan | Tugas penuh jelas, binding dan izin tersedia | Telaah rencana dan blueprint menurut tipe | Periksa status; tidak dipanggil saat sapaan/status |
| MSSHITrim | Hasil tool JSON memenuhi syarat | Pemadatan lokal dengan pemeriksaan data setara | Hook otomatis bila runtime tersedia; cek counter |
| CLI-Anything | Tugas aplikasi yang diizinkan dan tiket valid | Menjalankan rute sesuai peran/preset | Minta pekerjaan konkret; tidak ada aplikasi autostart |
| Planner | Diminta menyusun jadwal | Usulan agenda, tugas dan blok waktu | Tanyakan rentang waktu setiap rencana; jam rutin hanya jika dipilih Pengguna |
| Meeting/Transcription | Pilihan terpisah dengan izin dan dukungan host | Pendamping sesi atau pengolahan audio | Periksa OS, data yang dikirim dan kuota; template bukan rekaman |
| Dreaming | Perintah atau jadwal yang dipilih | Proposal pembelajaran lokal untuk ditinjau | Tidak mempromosikan memori atau membangunkan model otomatis |
| OmniVoice/media | Diminta menghasilkan suara/gambar/video | Jalur generasi terpisah dari penasihat teks | Runtime, model, hak aset dan biaya perlu disiapkan |
| Hersona | Permintaan katalog/draf persona | Referensi karakter dan penyusunan draf | SOUL tetap sumber persona aktif; tidak menimpa otomatis |

Tidak semua plugin tersedia pada semua OS/host. Planner publik bersifat opsional;
memasang panel tidak membuat kalender panas, jam wajib atau jadwal kerja tetap.
Meeting-Copilot live native dapat membutuhkan komponen desktop yang belum
tersedia di Windows. Transcribo dapat melibatkan layanan hosted dan penagihan;
jangan mengaktifkannya sebagai transkripsi lokal gratis tanpa verifikasi.

## MSSHITrim: hemat pada keluaran yang cocok, tanpa proxy

MSSHITrim adalah nama tampilan plugin native `msshi-auto-trim`, bukan kompresor
kedua. Instalasi baru menyiapkannya pada profil native yang dipilih dan
mengaktifkannya bila binary lokal terverifikasi. Bila runtime belum tersedia,
langkah instalasi dapat mengambil arsip versi yang checksum-nya dipatok. Gagal
mengunduh meninggalkan status pending; aplikasi dan model tidak dijalankan.
Pengguna lama yang sengaja menonaktifkan atau menyunting plugin tetap dihormati.

Hal ini berlaku pada pemasang penuh MSSHI/`msshi setup` untuk Hermes. Jalur
`npx skills add`, tap atau penyalinan Markdown saja belum tentu menjalankan
instalasi plugin native dan binary; selesaikan setup MSSHI bila ingin hook ini.

Hook memeriksa hasil tool berupa JSON object/array yang cukup besar; percakapan,
error, patch, source-file, persona dan konfigurasi tidak dipadatkan. Pemadatan
memakai subprocess lokal `llmtrim compress` dan konfigurasi JSON-only. Kandidat
harus memuat data kanonis yang persis setara. Perubahan nilai, pengubahan array
menjadi TOON, timeout atau error membuat hasil asli diteruskan. Ini fail-open
terhadap kegagalan kompresi, bukan perubahan isi secara diam-diam.

```powershell
msshi trim --status --profile val
msshi trim --install
```

Baris pertama membaca counter, baris kedua hanya pratinjau pemasangan. Untuk
pemasangan yang memang dipilih dan memerlukan unduhan runtime:

```powershell
msshi trim --install --apply --download-runtime
```

`--force-enable` adalah pilihan eksplisit untuk mengaktifkan kembali hook yang
sebelumnya dimatikan. `--profiles` membatasi profil yang dipilih. Lihat help
untuk format argumen yang benar; nama tampilan bot dapat berbeda dari ID folder.
Sesudah reload, slash native `/msshi-trim-status` atau `/msshitrim-status`
menampilkan diagnostik bila host mendaftarkannya. Perintah terminal
`hermes msshi-trim-status` hanya tersedia pada mode plugin in-process yang
mendukung pendaftaran CLI; ia dapat dilewati pada host plugin terisolasi.

Counter menyimpan jumlah dan ukuran byte agregat, bukan isi tool, chat atau
rahasia. Pengurangan byte bukan angka tagihan token provider. Plugin transformer
lain yang berjalan lebih dahulu dapat mengambil prioritas menurut aturan host;
MSSHITrim tidak menimpa core Hermes atau menjamin penghematan setiap giliran.

MSSHITrim tidak menjalankan `llmtrim setup`, TLS proxy, CA/sertifikat, daemon
login atau perubahan provider/model. Dashboard DSH Web UI `llmtrim-stats-plugin`
bukan plugin Hermes atau kompresor dan tidak dipasang. Unduhan dan lisensi
pihak ketiga mengikuti pin paket.


# 5. Dari permintaan percakapan menjadi pekerjaan alat

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

Pada arsitektur v3, aplikasi desktop seperti Lightcraft/Blender diarahkan melalui native CLI. GitLab dan Tinyfish dapat dihubungkan sendiri sebagai MCP web; installer MSSHI tidak memasang koneksinya. Jika sebuah dokumen lama menyebut ArtCraft MCP/Blender MCP, gunakan kebijakan v3 dan rute native saat ini; jangan mengaktifkan ulang server desktop lama hanya karena label historis tersebut.

## Lima bot sebagai pembagian kerja

<!-- FIGURE: roles -->

Yukino membantu menampung ide dan membuat pertanyaan awal. Shizuka menyusun strategi serta menyampaikan hasil riset dalam bahasa yang dapat dipakai. Val menyuplai riset dan bukti. Kiki-Chii mengerjakan ranah kreatif/film/foto/video. Shikaku mengerjakan coding dan evaluasi keamanan sesuai tugas yang diizinkan.

Pada Hermes yang didukung, preset memasang plugin lokal `msshi-team-routing` pada profil. Plugin menambahkan kebijakan koordinasi ke prompt sesi baru dan menawarkan profil hidup melalui backend delegasi native. Bot Chat memakai `message_agent` bila tool itu memang tersedia; fallback memakai `delegate_task` dengan parameter profil yang ditawarkan schema aktual. Backend kustom pengguna dipertahankan. Instalasi tidak mengirim tugas model; percakapan antarbots yang benar-benar dijalankan dapat memakai kredit. Mulai sesi baru setelah plugin dimuat ulang agar aturan baru masuk; riwayat lama tetap disimpan. Host tanpa fasilitas itu dapat memakai paket handoff pada bab praktik.

Setelah tugas, periksa output/receipt dan batas pengujiannya. Pakai bukti yang sudah ada sebelum mengulang render atau operasi web.

# 6. Versi, sumber, dan batas kepercayaan modul

Manifest revisi source publik yang dipakai buku ini: `dfc86245a12eef449c6d524f4ec4b0b87cad1887cea4a61b19702f89eafba15b`. Daftar berkas dan hash berada pada source-manifest.json yang menyertai edisi ini. Teks di-hash sesudah CRLF dinormalkan menjadi LF; biner tetap byte asli. Aturan ini menjaga verifikasi pada Windows dan clone Git. Nomor versi tetap 3.1.2.

`VERSION.json` memuat nomor versi paket. Commit Git menunjukkan isi source yang lebih spesifik. `main` dapat menerima perbaikan penjelasan tanpa menaikkan nomor versi; karena itu dua paket bertuliskan 3.1.2 dapat memiliki commit berbeda.

| Identitas | Nilai edisi ini |
| --- | --- |
| Versi paket | `3.1.2` |
| Commit implementasi yang dijelaskan | `42cb1dd782e19d697fdf08a3207ba9fa619e0383` |
| Edisi modul | 19 November 2026, Asia/Jakarta |
| Manifest | 67 skill fisik, 51 inti, 16 wrapper, 51 sumber |
| Cakupan bukti | Sintaks dan perilaku source; status perangkat/akun diuji tersendiri |

`msshi check/status` membandingkan versi dan menampilkan changelog. Identitas commit membantu membedakan isi source. Nomor v3.1.2 pada buku ini tetap sama; bandingkan commit atau manifest sumber untuk membedakan revisi dalam versi tersebut. Pada versi ini manifest sumber berisi 48 Git, dua model-card, dan satu katalog; jumlah itu berbeda dari jumlah rute aplikasi atau tool.

## Urutan rujukan saat ada perbedaan

1. Parser `--help`, source implementasi, dan output command pada commit yang benar.
2. Manifest/version serta panduan fitur saat ini yang cocok dengan implementasi.
3. Receipt privat untuk fakta yang hanya berlaku pada laptop tersebut.
4. Dokumen historis dan roadmap sebagai konteks, bukan bukti runtime sudah siap.

API key, base URL/endpoint pribadi, cookie, token, akun dan arsip pribadi tidak dicantumkan dalam modul. Pengguna menyiapkan alamat layanan dan kredensialnya sendiri secara privat; contoh format bukan pengaturan milik pembuat. Katalog sumber dan instruksi skill tidak sama dengan telah mengunduh seluruh bahan sumber. Akses akun personal dan koneksi layanan tetap memerlukan mekanisme host yang sesuai.

## Sumber utama

- [Repositori MSSHI](https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya)
- [Commit yang menjadi dasar modul](https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/commit/42cb1dd782e19d697fdf08a3207ba9fa619e0383)
- [README pada commit ini](https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/blob/42cb1dd782e19d697fdf08a3207ba9fa619e0383/README.md)
- [CLI dan panduan pilihan](https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/blob/42cb1dd782e19d697fdf08a3207ba9fa619e0383/docs/CLI.md)
- [Penjelasan seluruh pilihan](https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/blob/42cb1dd782e19d697fdf08a3207ba9fa619e0383/docs/OPTION_GUIDE.md)
- [Lisensi/atribusi pihak ketiga](https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/blob/42cb1dd782e19d697fdf08a3207ba9fa619e0383/THIRD_PARTY_NOTICES.md)

Kode orisinal MSSHI: MIT. Lisensi pihak ketiga tetap berlaku: bobot OmniVoice CC-BY-NC dan instruksi Unslop CC BY 4.0. Periksa ketentuan aset/dependency sebelum penggunaan atau distribusi komersial.


# 7. Menjalankan proyek lewat percakapan dan terminal

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

Contohnya, Blender dengan readiness available berarti executable/adapter tersedia. Itu belum menjadi bukti sebuah adegan tertentu sudah dirender. Layanan web yang registered belum tentu memiliki token login yang masih berlaku; koneksinya disiapkan sendiri oleh pengguna. Jika sebuah uji MP4 satu detik berhasil, itu membuktikan jalur ekspor kecil; ia belum membuktikan seluruh film 40 menit, kualitas suara, atau akun generator video.

### Otomatis, sesuai konteks, dan manual

Pada setup yang memasang plugin lossless Llmtrim, hook dapat memadatkan hasil tool JSON besar yang memenuhi syarat secara otomatis. JSON diperiksa kesetaraannya; percakapan biasa, kode, konfigurasi, persona, serta error dilewati. Penghematan tergantung jenis keluaran, bukan janji persentase pengurangan semua token atau tagihan.

Skill kontekstual dipilih ketika tugas memerlukannya: Unslop untuk layar UI, Scrapling untuk file HTML, TimesFM untuk deret waktu numerik, dan BRAG untuk film peluncuran. Percakapan dan penalaran agen dapat memakai token/kredit sesuai model serta provider yang dipilih. Menjalankan parser lokal tanpa LLM berbeda dari meminta agen menyusun penjelasan panjang tentang hasilnya.

Instalasi dependency, login, penerbitan, unggahan, dan penggunaan layanan berbayar adalah tindakan tersendiri. Sebutkan scope dengan jelas. Contoh: “Baca file HTML lokal ini dan simpan hasil baru” memberi ruang kerja yang lebih jelas daripada “urus semuanya”. Bridge MSSHI memakai auto_open_on_boot:false dan dispatcher mengeksekusi alat untuk tugas aktif melalui tiket dengan umur terbatas. Pengaturan startup mandiri aplikasi atau sistem operasi perlu diperiksa terpisah.

## Memakai satu bot atau lima peran

Preset MSSHI pada Hermes yang didukung membuat atau mengenali lima peran native dengan marker identitas dan pemetaan profil yang benar. Instalasi baru memakai default sebagai Yukino ditambah empat spesialis; instalasi lama dapat mempertahankan default netral dan Yukino bernama. Susunan lama tidak perlu diubah hanya untuk menyerupai contoh baru. Periksa daftar profil di Desktop dan kecocokan folder ketika menerima instalasi. Plugin lokal koordinasi menyuplai aturan kerja ke sesi baru serta rute ke profil hidup. Pada host lain, workspace/persona tetap memerlukan fasilitas koordinasi host masing-masing.

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

Unslop sudah dibundel untuk Val, Kiki dan Coder serta dipanggil sesuai konteks UI. Unslop digunakan pada layar antarmuka: hierarki, ruang, warna, ikon, copy UI, tipografi, layout, detail, visual, dan gerak. Kiki menilai arah visual; Val meninjau grafik ilmiah, unit, label, legenda, sumber, dan ketidakpastian; Shikaku menerapkan perubahan komponen/CSS dan memeriksa hasil.

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

Periksa lisensi source dan bobot OmniVoice secara terpisah sebelum penggunaan komersial; paket instruksi MSSHI bukan pemberian hak atas bobot atau suara. ElevenLabs, SoundCraft, musik, SFX, serta font memiliki akun/lisensi/dependency masing-masing. MSSHI tidak menganggap model ElevenLabs otomatis tersedia setelah kredit Hermes terisi. Sebutkan penyedia suara yang memang disiapkan, lalu tinjau naskah, bahasa, pengucapan, hak suara, dan biaya sebelum produksi.

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

## Browser dan akun yang dipilih pengguna

Wizard menawarkan Chrome, Edge, Firefox atau tidak memilih browser. Label akun
dan profil disimpan secara lokal sebagai petunjuk login manual, bukan token
autentikasi. Setup tidak membuka browser, membaca akun, menyalin cookie,
memindahkan sesi, atau memasang browser cloud. Memilih browser belum membuktikan
host menyediakan kendali browser yang sesuai.

GitLab, Tinyfish, BrightData dan Steel tidak otomatis dipasang/disambungkan.
Pengguna yang memerlukan layanan tersebut menghubungkannya sendiri melalui
pengaturan resmi layanan/host. Jangan membagikan cache OAuth antarorang atau
memasukkan akun pembuat MSSHI ke dalam instalasi pelanggan.

```powershell
msshi browser --status --hermes-home "C:\HermesClient"
msshi services status --hermes-home "C:\HermesClient"
```

Status hanya membaca keadaan lokal. Flag install Steel dan koneksi layanan
lama dipertahankan untuk memberi penjelasan kompatibilitas; tidak melakukan
pemasangan atau login. Bila perlu akses akun pribadi untuk tugas tertentu,
tentukan situs, tujuan dan cakupan; gunakan persetujuan dan kemampuan host yang
benar-benar tersedia. Koneksi Google Drive, NotebookLM, Gmail, Discord atau
Telegram bukan bagian akun publik yang diberikan oleh MSSHI.

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

Versi suite 3.1.2, commit source, versi aplikasi, versi runtime, dan versi model lokal adalah hal berbeda. Baca versi yang dilaporkan tiap komponen. Mengupdate petunjuk skill tidak selalu memperbarui bobot model atau package npm/pip; source cache juga tidak berarti runtime aktif. Pertahankan salinan yang dikustomisasi dan gunakan receipt yang sesuai lingkup ketika melakukan pemulihan. Daftar fitur publik merupakan pilihan kemampuan, bukan pernyataan semuanya sudah aktif pada setiap komputer klien.

Untuk tugas pertama, pilih satu keluaran kecil yang jelas: ringkasan satu sumber, ekstraksi dua judul HTML, audit satu layar, atau scaffold video pendek. Periksa hasil sebelum memperluas ke banyak sumber, model besar, atau film panjang. Setelah itu catat satu pola brief yang berhasil agar dapat digunakan kembali.

Jika tugas macet, simpan command, direktori kerja, profil, pesan error, waktu, dan lokasi output yang diharapkan. Lakukan status/help yang relevan dahulu. Jangan membayar chat berulang hanya untuk menemukan executable yang tidak ada, dan jangan menghapus library aplikasi yang sedang dipakai. Masalah Hermes Desktop, akun layanan, dependency parser, serta mutu video harus dipisahkan agar perbaikannya tepat. Sampaikan status yang benar-benar diperiksa, beserta hal yang masih perlu disiapkan.

## Helper mesin coding opsional dan pilihan model Pengguna

Keluarga command legacy `msshi coder`/`msshi kat` menyiapkan helper terpisah
apabila Pengguna memang memilih deployment yang sesuai. Ia tetap opsional dan
default OFF, termasuk pada MuZA. Tidak ada model/provider wajib dalam peran
Sir. Robot dan tidak ada bobot besar yang diam-diam dipasang pada laptop.

```powershell
msshi coder --home "C:\HermesClient" status
msshi coder --home "C:\HermesClient" presets
```

Status/presets membaca pilihan dan prasyarat lokal; ini bukan inferensi model.
Konfigurasi endpoint, ID model dan key disiapkan sendiri secara privat bila
memang diperlukan. Katalog metadata endpoint belum membuktikan saldo atau
hasil chat. Helper opsional tidak mengubah model utama, Council, pilihan
delegasi biasa atau konfigurasi media. Lihat seluruh flag pada referensi CLI,
tetapi jangan menjalankan configure/activate hanya karena namanya ada di buku.

Binary Goose, bila tersedia, adalah agen CLI eksternal, bukan ID model Council.
Kehadiran binary saja tidak membuktikan provider, tool, workspace dan anggaran
siap. Perangkat terbatas sebaiknya memulai dari tugas kecil pada mesin yang
memang telah dipilih Pengguna; memilih peran tidak menjamin model lokal muat.

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

## Praktikum tambahan untuk rilis 3.1.2

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

Bab ini membaca source publik MSSHI pada commit 42cb1dd782e19d697fdf08a3207ba9fa619e0383, bukan mengeksekusi operasi latihan. Referensi fungsi dan batasnya: docs/ALUR_PRESET_MUZA.md, docs/V3_1_UPDATE.md, docs/BRAG.md, docs/SCRAPLING.md, docs/HARNESS2.md, docs/TIMESFM.md, docs/REA.md, docs/UNSLOP.md, docs/CLI_ANYTHING_BRIDGE.md, docs/STEEL_BROWSER_POLICY.md, docs/SERVICE_CONNECTIONS.md, docs/CONTEXTUAL_INTEGRATIONS.md, hermes_plugins/msshi-team-routing/README.md, serta parser helper terkait.

Baseline Git: https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/tree/42cb1dd782e19d697fdf08a3207ba9fa619e0383 . Beberapa halaman integrasi/skill lama masih memakai hitungan v3.0 atau istilah MCP desktop. Untuk modul ini, jumlah 67 skill standar/51 sumber mengikuti VERSION.json terbaru; eksekusi aplikasi desktop mengikuti dispatcher CLI v3, bukan contoh legacy.


# 8. Operasional, pembaruan, dan pemecahan masalah

Bab ini merupakan panduan operasional untuk pelanggan MSSHI v3.1.2, berdasarkan source publik pada commit `42cb1dd782e19d697fdf08a3207ba9fa619e0383`. Semua path `C:\HermesClient` adalah contoh yang harus diganti dengan root instalasi pelanggan. Contoh tidak menyatakan bahwa aplikasi, model, atau akun pelanggan sudah terpasang maupun terhubung. Penyusunan modul tidak menjalankan perbaikan, model, render, atau operasi akun pelanggan.

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
| `msshi browser --status --hermes-home "C:\HermesClient"` | Membaca preferensi browser/kebijakan lokal | Login atau kendali browser nyata berhasil |
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
| Akun/kredensial | Akun model, kalender, browser atau layanan yang dipilih | Pengguna mengatur login/secret sendiri pada host yang sesuai |
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

Versi paket edisi ini adalah 3.1.2, berdasarkan commit implementasi `42cb1dd782e19d697fdf08a3207ba9fa619e0383`. Nomor versi, commit checkout Git, snapshot CLI global, dependency aplikasi, dan bobot model merupakan identitas yang berbeda. Perubahan pada folder pengembangan belum tentu dipakai launcher global sampai instalasi/update menerapkannya.

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

Dreaming bersifat opsional: pilihan plugin membuat laporan lokal deterministik satu kali; jadwal hanya dibuat melalui `msshi dream --register` secara eksplisit. Adapter MSSHI ini tidak memanggil model atau mempromosikan memori otomatis. Watermarks-remover belum dibundel sebagai kemampuan siap pakai; jangan menyimpulkannya terpasang dari percakapan atau daftar rencana lama.

## Cadangan dan rollback: pilih receipt yang tepat

Tidak ada satu perintah yang mengembalikan seluruh laptop. Bedakan backup skill, metadata updater, receipt migrasi runtime, receipt legacy browser, kredensial layanan, dan proyek pengguna. Selalu baca tujuan dan struktur receipt sebelum memulihkan.

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

Bila menemukan receipt browser Steel dari revisi lama, jangan menerapkannya
sebagai receipt migrasi runtime. Paket sekarang menghentikan pemasangan Steel.
Tinjau isi receipt dan cadangan secara privat sebelum pemulihan. Mengembalikan
Git checkout/tag tidak memulihkan akun, database atau seluruh dependency laptop.

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

MSSHI v3.1.2 tidak menyediakan perintah global `msshi remotion`. Proyek Remotion memakai toolchain dan dependency proyeknya. Mulailah dengan komposisi satu detik, resolusi kecil, satu worker, dan file keluaran baru sebelum merender video panjang. Keberhasilan satu contoh kecil belum menjamin seluruh aset dan durasi proyek dapat diproses.

Tinjau bantuan dan script proyek untuk opsi executable browser yang didukung, misalnya `--browser-executable`, serta variabel yang benar-benar dibaca helper, misalnya `CHROME_PATH`. Timeout handshake DevTools saat Chrome diluncurkan berbeda dari timeout render sesudah browser siap. Jika proyek memerlukan perubahan batas 25 detik menjadi 90 detik, penyesuaian harus dilakukan pada launcher yang cocok dengan versi dependency dan ditinjau untuk proses proyek itu; angka tersebut bukan flag global MSSHI atau jaminan kompatibilitas lintas versi.

Jangan menganggap flag timeout render/delayRender otomatis memperpanjang handshake Chrome yang gagal sebelum browser siap. Jangan menganggap `REMOTION_CHROME_EXECUTABLE` atau `PUPPETEER_EXECUTABLE_PATH` sudah dibaca oleh setiap wrapper. Periksa script proyek dan bantuan versi terpasangnya. Setelah mengganti versi Remotion, tinjau kembali kompatibilitas penyesuaian launcher; jangan menyunting `node_modules` secara coba-coba sebagai perbaikan permanen.

Urutan diagnosis: verifikasi path Chrome, baca error peluncuran, cek ruang temp dan RAM/commit, uji komposisi sendiri yang kecil dengan satu worker, lalu periksa MP4 menggunakan metadata video. Baru setelah itu naikkan durasi atau resolusi bertahap. Jangan menyalin path helper dari komputer lain sebagai langkah instalasi; siapkan toolchain pada workspace proyek Anda sendiri.

## Sumber daya, kredit, dan lisensi

Tutup pekerjaan yang memang tidak diperlukan secara normal dan sisakan ruang disk untuk temp, browser, audio/video serta backup. Banyaknya skill berupa teks tidak sama dengan beban semua aplikasi/model sekaligus; beban terbesar muncul ketika runtime benar-benar dijalankan. Tier hardware dan pemeriksaan preflight hanya dasar penjadwalan, bukan kuota RAM sistem operasi yang keras.

BRAG, misalnya, menolak pekerjaan ketika preflight menemukan physical memory/commit/disk di bawah batas minimumnya. Lolos batas minimum tidak berarti film panjang dengan semua aset akan muat. Gunakan preview kecil, satu worker ketika sumber daya terbatas, dan simpan temp/media pada volume yang cukup. Folder runtime di drive D tidak menghilangkan seluruh kebutuhan cache sistem di C.

TokenShield/reserve US$1 bergantung pada data saldo dan estimasi yang tersedia. Batas tagihan keras harus didukung provider; jangan menganggap seluruh akun dijamin berhenti tepat pada satu dolar. Chat perencanaan tetap memakai model yang dipilih pengguna. Eksekusi CLI lokal dapat tanpa kredit LLM, tetapi layanan cloud, asset berbayar, TTS API, dan GPU eksternal mempunyai biaya masing-masing.

Llmtrim otomatis hanya menerima keluaran JSON besar yang memenuhi syarat dan lulus kesetaraan nilai serta tipe. Konfigurasi proses utilitas membatasi transformasi pada kebersihan JSON; serialisasi TOON, deduplikasi, normalisasi Unicode dan pembuangan base64 tidak diandalkan untuk mengganti data hasil tool. Jika data berubah, utilitas gagal atau waktu habis, hasil asli tetap dipakai. Ia tidak memadatkan seluruh percakapan/kode dan tidak menjamin persentase penghematan tagihan yang tetap. Pengurangan byte pada fixture merupakan hasil contoh, bukan pengukuran seluruh token berbayar. OmniVoice lokal memerlukan bobot/runtime dan lisensi bobot yang membatasi penggunaan komersial; lisensi MIT MSSHI tidak menggantikan lisensi model, musik, font, atau aplikasi.

## Browser, akun dan plugin pertemuan

Installer menanyakan pilihan browser dan label profil/akun untuk login manual.
Tidak ada browser terbuka saat startup, transfer cookie atau login cloud yang
dibuat otomatis. GitLab, Tinyfish, BrightData dan Steel tidak disambungkan oleh
setup. Perintah legacy tidak boleh dipakai sebagai bukti layanan sudah siap.

Gmail, Discord, Telegram, Drive, NotebookLM dan konektor pengguna lain tetap
pengaturan pribadi. Paket publik tidak berisi token, OAuth client milik
pembuat, daftar akun pribadi, atau koneksi yang disalin dari laptop pembuat.

Meeting-Copilot, Transcribo dan Planner adalah opsi terpisah. Baca status,
kompatibilitas host, izin audio dan model/budget sebelum memakainya. Bila
plugin belum siap, pakai template dan catatan manual; jangan menyatakan sebuah
pertemuan sudah direkam, dijadwalkan, atau ditranskripsikan tanpa bukti.

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

Sesudah migrasi perangkat, baca status, verifikasi path executable, periksa compatibility runtime, dan uji satu artefak kecil. Nama/path contoh pada modul bukan syarat universal. Anda boleh memilih nama dan folder sendiri. Preset Hermes memakai pemetaan lima peran ke profil native: default menjadi Yukino pada instalasi baru; instalasi lama dapat mempertahankan Yukino bernama. Host lain mengikuti pemasangan workspace dan kemampuan koordinasinya. Ulangi pengenalan profil dan reload plugin yang didukung host sesudah migrasi perangkat.

## Lima peran native: instalasi baru dan tim yang sudah ada

`--default-bot auto` adalah pilihan normal. Pada instalasi baru dari GitHub, profil **default milik Hermes menjadi Yukino** melalui metadata dan template persona yang sesuai; bukan memindahkan config milik bot lain. Empat spesialis dibuat sebagai profil bernama. Pada tim yang sudah mempunyai Yukino bernama, auto mempertahankan susunan itu beserta default yang ada. Instalasi ulang bukan alasan untuk mengganti pengaturan model/provider atau memindahkan riwayat.

| Peran | Profil instalasi baru | Profil tim lama yang dipertahankan |
| --- | --- | --- |
| Yukino, intake dan ide awal | `default` | `yukino`, bila memang sudah ada |
| Shizuka, koordinator dan penyatu hasil | `shizuka` | `shizuka` |
| Val, riset dan data | `val` | `val` |
| Kiki-Chii, seluruh ranah kreatif | `kiki-chii` | `kiki-chii` |
| Shikaku, coding dan audit yang diminta | `shikaku` | `shikaku` |

Root netral pada tim lama boleh tetap menjadi asisten tambahan; ia bukan peran spesialis keenam. Pada preset MuZA, matriks aplikasi tetap: Val empat ArtCraft dokumen/data, Kiki tiga belas kreatif, Shikaku CraftAnything/Figcraft, Yukino/Shizuka/default netral tanpa ArtCraft. Figcraft adalah satu-satunya rute yang dibagi Kiki dan Shikaku.

Untuk instalasi baru yang memang hendak memakai lima peran, jalankan wizard pada root yang benar:

```powershell
msshi setup --platform hermes --mode muza-preset --target-dir "C:\HermesClient\profiles" --default-bot auto
```

Perintah tersebut adalah setup nyata. Untuk tim lama yang sengaja mempertahankan default netral dan Yukino bernama, pilih `--default-bot keep-hermes`. Pilihan `--default-bot yukino` adalah konversi eksplisit default menjadi Yukino; jangan menggunakannya hanya untuk mengecek status tim lama.

Dari checkout source yang benar, installer langsung menyediakan pratinjau dan flag apply:

```powershell
python scripts/install_msshi.py --platform hermes --mode muza-preset --target-dir "C:\HermesClient\profiles" --default-bot auto
```

Tambahkan `--apply` setelah meninjau pratinjau. Pemasangan menjaga SOUL kustom, rahasia dan nilai konfigurasi LLM yang sudah ada. Persona bawaan yang belum dikustomisasi dapat diisi template Yukino sesuai pilihan layout. Pemetaan peran dicatat pada `msshi-runtime/team-layout.json`, sedangkan perubahan profil dan plugin dicatat pada receipt. Profile ID, home dan model/provider tidak boleh disimpulkan hanya dari nama di layar. Hanya konversi `yukino` yang dipilih secara eksplisit boleh menyembunyikan profil Yukino bernama lama dengan marker native yang dapat dipulihkan; file dan riwayatnya tidak dihapus. Mode auto pada tim lama tidak melakukan konversi tersebut.

**Sebelum, saat, dan setelah Hermes dibuka:** installer dapat menyiapkan file/pemetaan tanpa mengirim chat. Bila Hermes sedang terbuka, selesaikan tugas aktif lalu gunakan reload/restart yang didukung host dan mulai sesi baru. Bila pemasangan dilakukan sebelum Hermes pertama kali dibuka, profil baru dikenali saat host mulai. Pemeriksaan metadata/schema lokal tidak memerlukan kredit; tugas nyata antarbots tetap memakai model. Jangan mematikan proses atau menghapus percakapan untuk memaksa roster segar.

Plugin `msshi-team-routing` menyediakan pilihan backend bagi pengguna, tetapi installer tidak pernah memilih backend delegasi secara otomatis. Semua pilihan yang sudah ada, termasuk `default`, dipertahankan. Pengguna memilih backend sendiri bila memerlukannya; periksa schema tool sesi sebelum mengklaim delegasi profil bernama tersedia. `--no-team-routing` pada installer langsung melewati pemasangan backend tersebut. Instalasi tidak mengirim pesan antarbots atau memanggil model.

Setelah pemasangan, restart/reload plugin melalui mekanisme Hermes yang didukung, lalu mulai chat baru. Prompt koordinasi dibangun saat sesi dimulai; chat lama belum tentu memuat tambahan baru walaupun file plugin telah ada. Riwayat percakapan tidak perlu dihapus. Pada Bot Chat gunakan `message_agent` jika tersedia; pada backend ini `delegate_task` dapat menawarkan enum profil hidup. Jangan menambahkan parameter profil yang tidak ditawarkan tool sesi.

Jika Yukino mengerjakan semua spesialisasi sendiri, periksa urutan berikut: apakah chat berada pada profil yang dipetakan ke peran Yukino, apakah plugin termuat, apakah sesi baru, apakah schema delegasi menawarkan target, dan apakah tugas memang perlu spesialis. Jangan menyimpulkan komunikasi rusak hanya dari satu tugas intake sederhana. Satu simulasi/fixture schema juga belum membuktikan pengiriman model antarbots nyata berhasil; pengiriman nyata dapat memakai kredit.

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

## Troubleshooting tambahan 3.1.2

| Gejala | Penyebab yang perlu dibedakan | Tindakan |
| --- | --- | --- |
| Yukino hilang, tetapi folder ada | Marker deleted atau identitas profil tidak ditemukan | Pasang ulang hanya profil yang memang dipilih lewat installer native, lalu rescan host |
| Default berjudul Yukino | Benar pada instalasi baru; pada tim lama perlu membaca pemetaan | Periksa team-layout dan roster. keep-hermes mempertahankan susunan lama; jangan memindahkan model atau riwayat |
| Skill ada, delegasi profil belum muncul | Plugin belum reload, chat lama, atau backend kustom dipertahankan | Periksa plugin/backend dan mulai sesi baru; gunakan schema tool aktual |
| `profile` ditolak oleh tool | Host/backend sesi tidak menawarkan parameter itu | Jangan menebak API; gunakan Bot Chat yang mendukung atau handoff manual |
| Pilihan KAT dahulu tidak melakukan setup | Installer lama hanya menulis preferensi | Pada 3.1.2 gunakan msshi coder wizard; lengkapi endpoint/key/catalog secara nyata |
| KAT pending setelah memilih cloud | Key, ID model, endpoint atau rute belum siap | Baca status reason; Pro v2.5 berbeda dengan Dev dan memerlukan akun sendiri |
| Katalog model berhasil tetapi chat gagal | Bukti metadata belum membuktikan saldo/izin inferensi | Periksa respons layanan saat penggunaan yang diotorisasi; jangan tes berulang otomatis |
| KAT tak muncul pada bot selain Coder | Pembatasan peran memang diterapkan | Delegasikan coding ke Shikaku; model utama bot lain tetap utuh |
| App dipilih tetapi tidak diberi rute | Matriks preset/peran menolak target, aplikasi berat belum opt-in, atau target dinonaktifkan | Jalankan lewat pemilik peran, bukan melonggarkan seluruh profil |
| Cache kontekstual berubah | File cache tidak lagi cocok SHA snapshot | Simpan perubahan yang ingin dipertahankan, tinjau asalnya; jangan memalsukan manifest |
| CareerOps ada tetapi skor personal belum siap | CV/profil belum dipersonalisasi | Siapkan User Layer privat; jangan memakai profil contoh upstream |
| rea-video mengunduh model | Default upstream fitur audio/model belum dinonaktifkan | Gunakan tahap ringan dengan flag no-ASR/no-stems/no-VLM sebelum tugas yang memerlukan model |
| Rebaseline ditolak | Snapshot stale atau penerimaan perubahan belum eksplisit | Ulang preview, tinjau perubahan, baru apply dengan SHA tepat |
| Panduan tidak masuk Downloads | NoPdf/env opt-out, tujuan tidak bisa ditulis atau katalog gagal | Baca pesan installer; coba msshi manual download --dest ke folder yang dapat ditulis |

Tidak semua status NEEDS_ATTENTION berarti reinstall seluruh Hermes diperlukan. Contohnya `msshi doctor` dapat melihat helper LibreOffice sebagai informasi lingkungan meskipun rute LibreOffice dilarang pada preset. Paritas skill, dependency skripsi, kesiapan akun, baseline preservasi dan hasil aplikasi merupakan pemeriksaan yang berbeda. Baca field spesifik sebelum mengambil tindakan.

## Menambahkan protokol SOUL tanpa menghapus persona pribadi

Lima template publik menanyakan sapaan pengguna bila belum diketahui. Protokol dua tipe berlaku pada semua preset: Yukino/Shizuka memakai Main dan Advisor; Sir. Robot/Val/Kiki memakai Main dan Council tepat dua putaran dengan audit Main di tengah, tanpa Sub-Agent terpisah. Kontrak input-output, bukti, review dan draf catatan tetap diperlukan. Model yang benar-benar dikonfigurasi pengguna tetap menjadi acuan. Tugas kecil tidak perlu dewan atau subagen, dan instruksi SOUL tidak menciptakan backend MoA atau hak akun yang belum ada.

Untuk SOUL kustom yang sudah ada, helper terpisah dapat menambahkan hanya blok bertanda. Jalankan dari checkout MSSHI yang ditinjau; ini **bukan subcommand global msshi**:

```powershell
python scripts/msshi_soul_protocol.py --home "C:\HermesClient" --profiles shikaku kiki-chii
```

Perintah pertama adalah pratinjau tanpa penulisan. Setelah rencana sesuai:

```powershell
python scripts/msshi_soul_protocol.py --home "C:\HermesClient" --profiles shikaku kiki-chii --apply
```

Byte di luar blok bertanda dipertahankan. Pengulangan tidak menggandakan blok; perubahan bersamaan dan symlink/junction ditolak. Receipt ada di `msshi-runtime/soul-receipts/<id>/`. Helper hanya mengubah SOUL yang dipilih, tanpa model/API, config provider, NotebookLM atau Obsidian.

```powershell
python scripts/msshi_soul_protocol.py --home "C:\HermesClient" --rollback "PATH_RECEIPT"
python scripts/msshi_soul_protocol.py --home "C:\HermesClient" --rollback "PATH_RECEIPT" --apply
```

Rollback pertama juga pratinjau. Bila pengguna mengedit SOUL setelah pemasangan, helper melaporkan konflik agar edit tersebut tidak ditimpa. Mulai sesi baru setelah reload host agar perubahan instruksi terbaca; percakapan lama tidak perlu dihapus.

**Catatan eksternal merupakan pilihan pribadi.** Academic memakai workspace Hermes, tanpa Obsidian otomatis. Bot boleh menyiapkan draf catatan keputusan, temuan, bukti, masalah dan langkah berikut. Menulis ke vault memerlukan persetujuan lokasi, file, isi dan tindakan. Memasang SOUL/preset tidak memberikan izin itu.

## Memulihkan preset pribadi setelah instalasi ulang

Source publik menyediakan kemampuan dan template umum; persona pribadi, pilihan nama, bahan pengguna dan rahasia tidak diunggah bersama repo. Simpan ekspor persona/preferensi secara privat dan tinjau isinya sebelum dipindah. Pada perangkat baru, pasang rilis resmi, pilih layout yang sesuai, lalu pulihkan persona ke **peran yang dipetakan**, bukan menyalin config bot lain menjadi default. Endpoint/key/model milik host tujuan tetap dikelola pengguna. Pastikan alat pemulihan memberi pratinjau, backup dan receipt sebelum apply.

## Doctor: diagnosis dan perbaikan yang terbatas

```powershell
msshi doctor --json
```

Doctor memeriksa paritas skill dan katalog, JSON metadata, dependency dokumen,
profil native yang ditemukan, keberadaan/aktivasi plugin, binary MSSHITrim,
SOUL UTF-8/NUL, folder skill, kebijakan aplikasi dan kesiapan Advisor/Council.
Ia tidak menampilkan nilai model/provider/endpoint/API key atau mencoba login.
Pemeriksaan tidak memanggil model, jaringan atau aplikasi.

`HEALTHY` berarti pemeriksaan yang dijalankan tidak menemukan masalah dalam
lingkupnya, bukan bukti render, chat model atau semua akun telah diuji. Status
`NEEDS_ATTENTION` disertai masalah spesifik dan saran. Exit code 0 menunjukkan
sehat, 1 menunjukkan error inti, 2 menunjukkan peringatan. Native host yang
belum terpasang dilaporkan tersendiri; jangan menyamakannya dengan riwayat bot
yang rusak. Baca lokasi/versi yang diperiksa sebelum melakukan perubahan.

Setelah meninjau diagnosis, Pengguna dapat memilih perbaikan terbatas:

```powershell
msshi doctor --fix
```

`--fix` adalah tindakan tulis, bukan preview. Helper hanya memulihkan **file
hilang yang terbukti milik MSSHI** melalui ownership record atau fingerprint
skill yang dikenal, dan mencatat receipt. Edit kustom, konfigurasi, SOUL,
model/provider/base URL/endpoint/key serta akun tidak ditimpa. Dependency,
pengaturan Council dan kerusakan yang tidak terbukti perlu ditangani melalui
saran yang sesuai; Doctor tidak mengunduh paket atau "memperbaiki apa saja".
Jika pengaman menolak, hentikan dan tinjau receipt/cadangan, bukan memaksa edit.

## Bot Forge: rancang kebutuhan, baru buat profil

Pengguna dapat berdiskusi dengan bot mana saja untuk merancang anggota tim.
Tinjau dahulu apakah tugas cukup ditangani bot yang sudah ada. Pada tim lima
peran, Shizuka dapat mengoordinasikan masukan rekan yang tersedia setelah
Pengguna menyetujui pemakaian model tambahan. Solo/tim kustom menggunakan peran
yang benar-benar ada; jangan mengarang hasil konsultasi atau memanggil semua
bot untuk permintaan sederhana.

```powershell
msshi forge --roster
```

Daftar ini membantu melihat profil dan skill yang terpasang, tanpa membuat
bot atau menampilkan koneksi/model pribadi. Hasil desain memuat nama, mandat,
gap yang belum tercakup, skill minimum, input-output, handoff, alat, izin dan
biaya. Rekomendasi mesin berupa kemampuan yang diperlukan, bukan pengisian
model/provider/key milik orang lain.

Rancangan JSON memakai tepat enam bidang: `id`, `name`, `purpose`, `skills`,
`gap`, dan `reviews`. `reviews` berisi penilaian peran yang benar-benar diterima,
bukan contoh yang dinyatakan seolah sudah terjadi. Simpan sebagai berkas
workspace biasa yang telah diperiksa. Blueprint tidak menerima pengaturan
model, provider, endpoint, base URL atau kredensial.

```powershell
msshi forge --blueprint "C:\MSSHI-Latihan\rancangan.json"
```

Perintah tersebut hanya preview. Untuk membuat profil yang telah disetujui:

```powershell
msshi forge --blueprint "C:\MSSHI-Latihan\rancangan.json" --apply
```

Terminal meminta konfirmasi sebelum membuat profil baru. Hasil native mencakup
SOUL, metadata, skill terpilih dan receipt; MSSHITrim disiapkan bila binary
lokal terverifikasi. Tidak ada pewarisan model/provider, base URL/endpoint,
API key, `.env` rahasia, akun atau memori privat dari bot lain. Pengguna mengatur
mesin sendiri sesudahnya. ID yang sudah ada atau pernah dihapus ditolak agar
riwayat/profil tidak tertimpa.

Adapter lokal ini tidak mengaktifkan kickoff chat, routine, gateway, notifikasi
atau plugin upstream Bot Forge secara diam-diam. Upstream adalah opsi terpisah
yang harus ditinjau; dukungan Windows/gateway/sandbox tidak diasumsikan sama.
Peran/tipe dalam rancangan juga bukan bukti schema Advisor/Council pada profil
baru sudah tersedia. Konfigurasikan host dan periksa sebelum mengklaim proses
tersebut berjalan. Gunakan handoff manual bila kemampuan belum didukung.

Sesudah pembuatan, jalankan Doctor dan status trim yang sesuai, lalu pilih
model/provider sendiri melalui Hermes. Pengaturan backend delegasi tidak
dipilih installer; Pengguna memilihnya secara eksplisit jika memerlukannya.
Pemasangan profil tidak mengirim chat untuk menguji saldo atau model.


## Rujukan bab operasional

Rujukan publik pada commit yang menjadi dasar modul: `scripts/msshi_cli.py`, `scripts/msshi_managed.py`, `scripts/msshi_runtime.py`, `scripts/msshi_desktop.py`, `scripts/msshi_browser_policy.py`, `docs/MANAGED_UPDATES.md`, `docs/V3_MIGRATION.md`, `docs/STEEL_BROWSER_POLICY.md`, `docs/SERVICE_CONNECTIONS.md`, serta `docs/OPTION_GUIDE.md`. Gunakan source dan panduan versi yang sama saat memeriksa perilaku. File akun, bukti lokal, konfigurasi pelanggan dan cadangan privat bukan bagian bahan publik yang harus dimiliki pembaca.


# 9. Referensi lengkap command MSSHI

Referensi ini ditangkap dari parser revisi v3.1.2 pada 19 November 2026; baseline Git `42cb1dd782e19d697fdf08a3207ba9fa619e0383` dan manifest berkas sumber dicatat bersama hasil build. Parser asli menjadi sumber sintaks; penjelasan operasional dibaca dari implementasi. Tidak ada command model, render, login, instalasi, atau layanan yang dijalankan untuk menyusun bagian ini. Tree parser ditangkap sebelum `parse_args` mengeksekusi aksi; `format_help` menghasilkan usage sebenarnya.

## Cara membaca dan menyalin

Contoh `C:\HermesClient` adalah contoh root Hermes yang harus diganti dengan lokasi instalasi Anda; jangan membuat root kedua hanya untuk menyamakan contoh. `C:\MSSHI-Latihan`, `C:\MSSHI-Hasil`, nama input, dan receipt adalah contoh yang harus disiapkan atau diganti. Jangan menyalin placeholder `PATH_*`, `ID_TIKET`, atau `RECEIPT` secara harfiah. Teks command dijalankan di terminal PowerShell, bukan dikirim sebagai slash command di kolom chat bot.

`-h`/`--help` tersedia pada setiap parser dan hanya menampilkan bantuan. Untuk keluarga yang memiliki shared flag, taruh flag sebelum subcommand: `msshi rea --hermes-home "C:\HermesClient" status`. BRAG berbeda: flag `--hermes-root` berada setelah `doctor`, `check`, `render`, atau `renderer`. Runtime menerima `--home` sebelum maupun pada subcommand. Perhatikan usage tiap node, jangan menyeragamkan flag antarfitur.

Status default pada tabel merepresentasikan nilai logis, bukan path fixture ekstraksi. Jika flag home kosong, resolusi mengikuti implementasi/env/host; lebih aman memilih home secara eksplisit pada tindakan yang menulis. `--help` sukses membuktikan sintaks, bukan membuktikan runtime, akun, lisensi, atau kualitas hasil tugas.

Pisahkan empat biaya: token LLM untuk memahami chat; layanan cloud/API; unduhan/storage; CPU/GPU/RAM lokal. Command tanpa LLM masih dapat memakai disk, CPU, jaringan atau kuota layanan. Tidak ada jaminan seluruh tagihan token menjadi nol.

## Peta keluarga command


Bantuan akar: `msshi --help`. Opsi `-h/--help` menampilkan petunjuk dan keluar sebelum aksi command.

```text
usage: msshi [-h]
             {check,status,connect,update,runtime,integrations,desktop,audit,doctor,skripsi,assets,compact,browser,trim,interaction,forge,managed,services,timesfm,brag,scrapling,harness2,optional,rea,choices,manual,dream,voice,kat,coder,setup,select,bootstrap}
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
| `msshi doctor` | Mendiagnosis katalog/dependency, profil native, plugin, MSSHITrim, UTF-8/NUL SOUL, rute dan kesiapan Advisor/Council secara lokal; --fix menyediakan pemulihan terbatas yang terbukti milik MSSHI.. | `msshi doctor --help` |
| `msshi skripsi` | Merakit template skripsi Word dari pedoman, metadata kampus, bahan referensi dan preset metode.. | `msshi skripsi --help` |
| `msshi assets` | Mencari SOUL, sampel suara, nama file terkait katalog Notebook/knowledge base, dan arsip bahan personal pada root yang Anda tentukan.. | `msshi assets --help` |
| `msshi compact` | Meringkas representasi file konteks lokal: menghapus whitespace JSON atau merangkum pengulangan baris log. | `msshi compact --help` |
| `msshi browser` | Membaca status lokal dan menjelaskan penghentian jalur pemasangan Steel lama. | `msshi browser --help` |
| `msshi trim` | MSSHITrim memadatkan hasil tool JSON yang memenuhi syarat secara lokal melalui hook msshi-auto-trim; CLI membaca counter, memadatkan file uji atau menyiapkan plugin/runtime sesuai pilihan.. | `msshi trim --help` |
| `msshi interaction` | Memeriksa atau menyiapkan plugin native pengendali dua tipe: Main/Advisor untuk Yukino-Shizuka dan Main/Council dua putaran untuk Coder-Val-Kiki.. | `msshi interaction --help` |
| `msshi forge` | Meninjau roster dan blueprint bot baru, kemudian membuat profil native hanya setelah pilihan --apply dan konfirmasi interaktif.. | `msshi forge --help` |
| `msshi managed` | Mendaftarkan dan memperbarui salinan MSSHI berdasarkan kecocokan isi/fingerprint, termasuk target fisik yang diakses melalui junction yang telah ditinjau.. | `msshi managed --help` |
| `msshi services` | Membaca status koneksi lokal; tindakan pemasangan/probe/berbagi OAuth lama dihentikan. | `msshi services --help` |
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
| `msshi kat` | Alias legacy untuk helper coding opsional milik Pengguna; membaca status atau menyiapkan opsi deployment yang dipilih sendiri.. | `msshi kat --help` |
| `msshi coder` | Atur model KAT opsional khusus subtask Coder melalui endpoint yang benar, input key privat, dan katalog model.. | `msshi coder --help` |
| `msshi setup` | Wizard enam mode: Academic Mahasiswa (pilihan awal pemasangan baru), Academic Dosen, Solo, tim kustom, paket terpilih, atau MuZA. | `msshi setup --help` |
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

**Batas dan efek.** --catalog/--status tidak membuka aplikasi. Tiket diperlukan untuk eksekusi rute yang dilindungi. MuZA memakai matriks ArtCraft 4/2/13; Academic memakai kebijakan ringan tersendiri. Rute berat Academic hanya dapat dipilih eksplisit bila aplikasi terdeteksi. Registrasi bukan bukti aplikasi atau akun siap.

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

Mendiagnosis katalog/dependency, profil native, plugin, MSSHITrim, UTF-8/NUL SOUL, rute dan kesiapan Advisor/Council secara lokal; --fix menyediakan pemulihan terbatas yang terbukti milik MSSHI.

**Prasyarat.** CLI MSSHI pada source yang benar; pemeriksaan native mengikuti instalasi Hermes yang terdeteksi. Pemeriksaan tidak memerlukan akun model atau aplikasi dibuka.

**Mulai dari.**

```powershell
msshi doctor --json
```

**Batas dan efek.** Default dan --json read-only. --fix menulis hanya file hilang yang fingerprint kepemilikannya terbukti, dengan receipt; edit kustom, SOUL, konfigurasi, model/provider/endpoint/key dan akun dipertahankan. Tidak mengunduh dependency, memanggil model, menjalankan aplikasi atau memperbaiki seluruh masalah secara otomatis. Exit 0 sehat, 1 error inti, 2 peringatan. NEEDS_COUNCIL_CONFIG memerlukan pilihan Pengguna, bukan model bawaan.

### `msshi doctor`

Efek: Baca lokal; --fix adalah penulisan pemulihan terbatas yang dipilih eksplisit, tanpa jaringan atau peluncuran aplikasi.

```text
usage: msshi doctor [-h] [--json] [--fix]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--json` | opsional; default Tidak/OFF | Print JSON output. |
| `--fix` | opsional; default Tidak/OFF | Restore missing files proven MSSHI-owned; preserve custom edits and all model/provider/endpoint/account settings. No downloads or app launches. |

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

Membaca status lokal dan menjelaskan penghentian jalur pemasangan Steel lama. Preferensi browser manual dipilih lewat msshi setup.

**Prasyarat.** Home Hermes yang ingin diperiksa. Status tidak memerlukan akun browser cloud.

**Mulai dari.**

```powershell
msshi browser --hermes-home "C:\HermesClient" --status
```

**Batas dan efek.** Flag install Steel lama tidak memasang plugin/layanan. Tidak membuka browser, memindahkan akun atau menyalin cookie. Rollback legacy hanya untuk receipt yang benar-benar cocok bila masih didukung; baca help/status versi terpasang.

| Pemilih tindakan | Fungsi | Efek |
| --- | --- | --- |
| --status | Baca status/kebijakan lokal tanpa sesi cloud. | baca lokal |
| --install | Flag legacy: pemasangan Steel dihentikan. | penjelasan lokal |

### `msshi browser`

Efek: Pemeriksaan/penjelasan lokal; bukan sesi browsing atau login otomatis.

```text
usage: msshi browser [-h] [--hermes-home HERMES_HOME] [--status] [--install]
                     [--rollback ROLLBACK]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--hermes-home` | opsional; default HERMES_HOME / default host | Home/root Hermes yang dipilih; gunakan nilai eksplisit agar tidak mengarah ke profil lain. |
| `--status` | opsional; default Tidak/OFF | Tampilkan status lokal; efek tepat mengikuti penjelasan keluarga. |
| `--install` | opsional; default Tidak/OFF | Retired compatibility no-op; no plugin or account is installed. |
| `--rollback` | opsional; default tidak diisi | Restore a verified historical Steel receipt; explicit action only. |
| `--steel-source` | opsional; default tidak diisi | Opsi parser; ikuti nama dan nilai sah yang tercantum. |
| `--steel-ready` | opsional; default Tidak/OFF | Opsi parser; ikuti nama dan nilai sah yang tercantum. |
| `--personal-account` | opsional; default Tidak/OFF | Tandai kebutuhan akses akun personal agar guard menuntut persetujuan terikat tugas. |
| `--account-transfer` | opsional; default Tidak/OFF | Flag legacy tanpa tindakan; tidak memindahkan akun atau cookie. |
| `--approved` | opsional; default Tidak/OFF | Flag legacy tanpa tindakan pada helper browser ini; tidak membentuk login. |
| `--approval-note` | opsional; default teks kosong | Catat situs/akun/tujuan/cakupan persetujuan nyata; tidak boleh berisi rahasia akun. |

## 14. `msshi trim`

MSSHITrim memadatkan hasil tool JSON yang memenuhi syarat secara lokal melalui hook msshi-auto-trim; CLI membaca counter, memadatkan file uji atau menyiapkan plugin/runtime sesuai pilihan.

**Prasyarat.** Binary llmtrim terverifikasi dan host dengan hook transform_tool_result untuk automasi. Setup penuh menyiapkannya bagi profil terpilih; penyalinan skill saja tidak memasang runtime.

**Mulai dari.**

```powershell
msshi trim --home "C:\HermesClient" --status --profile default
```

**Batas dan efek.** Hanya JSON object/array besar yang lolos pemeriksaan data kanonis setara. Percakapan/error/patch/source/persona/config dilewati; kegagalan/time-out mempertahankan hasil asli. --install preview, --apply menulis, --download-runtime memilih unduhan pin; --force-enable terpisah untuk override disable eksplisit. Tidak memasang proxy/CA atau mengubah model/provider. Counter byte bukan tagihan token provider.

| Pemilih tindakan | Fungsi | Efek |
| --- | --- | --- |
| --status | Baca agregat penghitung hook otomatis pada profil. | baca lokal |
| --input FILE | Kompresi request JSON lokal; stdout atau file baru via --output. | utilitas lokal/tulis opsional |

### `msshi trim`

Efek: Status membaca lokal tanpa model. Install --apply menulis plugin/receipt; download-runtime dapat memakai jaringan. Input/output menjalankan kompresor lokal, bukan inferensi.

```text
usage: msshi trim [-h] [--home HOME] [--binary BINARY]
                  (--input INPUT | --status | --install) [--profile PROFILE]
                  [--profiles PROFILES] [--apply] [--download-runtime]
                  [--force-enable] [--output OUTPUT]
                  [--provider {openai,anthropic,google,gemini}]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--home` | opsional; default tidak diisi | Home data yang dituju; lihat catatan keluarga karena managed memakai state MSSHI, bukan home Hermes. |
| `--binary` | opsional; default tidak diisi | Path executable llmtrim yang telah dipasang; bukan model/provider LLM. |
| `--input` | opsional; default tidak diisi | Path input lokal sesuai format command; pilih file terkontrol yang telah disiapkan. |
| `--status` | opsional; default Tidak/OFF | Tampilkan status lokal; efek tepat mengikuti penjelasan keluarga. |
| `--install` | opsional; default Tidak/OFF | Prepare/enable MSSHITrim on native profiles; preview until --apply |
| `--profile` | opsional; default default | ID folder profil Hermes, misalnya default atau kiki-chii; bukan selalu nama tampilan. |
| `--profiles` | opsional; default all | Installation only: all or comma-separated real profile IDs |
| `--apply` | opsional; default Tidak/OFF | Terapkan rencana yang didukung command ini; tanpa flag managed tetap merencanakan. |
| `--download-runtime` | opsional; default Tidak/OFF | Installation only: allow checksum-pinned CLI download |
| `--force-enable` | opsional; default Tidak/OFF | Installation only: explicitly override a previous trim disable |
| `--output` | opsional; default tidak diisi | Tujuan output baru. Jangan memakai file input/config/proof yang belum ditinjau sebagai target overwrite. |
| `--provider` | opsional; default openai | Bentuk request JSON (openai/anthropic/google/gemini); tidak mengubah konfigurasi provider Hermes. Nilai: openai, anthropic, google, gemini. |

Wajib satu dari: `--input`, `--status`, `--install`.

## 15. `msshi interaction`

Memeriksa atau menyiapkan plugin native pengendali dua tipe: Main/Advisor untuk Yukino-Shizuka dan Main/Council dua putaran untuk Coder-Val-Kiki.

**Prasyarat.** Hermes yang mendukung plugin/schema versi yang ditentukan manifest. Binding Advisor/Council dipilih Pengguna sendiri; tidak ada model atau provider bawaan publik.

**Mulai dari.**

```powershell
msshi interaction --home "C:\HermesClient" --status
```

**Batas dan efek.** Status/protocol/install tidak menjalankan Advisor atau Council. --install adalah pratinjau; --apply menyiapkan plugin/receipt. Val atau bot lain tanpa binding akan melaporkan NEEDS_COUNCIL_CONFIG, bukan diisi model otomatis. Reload/schema native diperlukan. Pengujian state dengan tiruan bukan uji provider nyata.

### `msshi interaction`

Efek: Status/protocol membaca/cetak lokal; install --apply menulis plugin dan pendaftaran yang dipilih tanpa mengganti model/provider atau memanggil model.

```text
usage: msshi interaction [-h] [--home HOME] [--source SOURCE] [--status]
                         [--install] [--apply]
                         [--profiles {default,yukino,shizuka,val,kiki-chii,shikaku} [{default,yukino,shizuka,val,kiki-chii,shikaku} ...]]
                         [--protocol]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--home` | opsional; default HERMES_HOME / default host | Home data yang dituju; lihat catatan keluarga karena managed memakai state MSSHI, bukan home Hermes. |
| `--source` | opsional; default root paket aktif | Source yang dituju; artinya bergantung command, dijelaskan pada catatan keluarga. |
| `--status` | opsional; default Tidak/OFF | Tampilkan status lokal; efek tepat mengikuti penjelasan keluarga. |
| `--install` | opsional; default Tidak/OFF | Opsi parser; ikuti nama dan nilai sah yang tercantum. |
| `--apply` | opsional; default Tidak/OFF | Terapkan rencana yang didukung command ini; tanpa flag managed tetap merencanakan. |
| `--profiles` | opsional; default tidak diisi | Opsi parser; ikuti nama dan nilai sah yang tercantum. Nilai: default, yukino, shizuka, val, kiki-chii, shikaku. |
| `--protocol` | opsional; default Tidak/OFF | Opsi parser; ikuti nama dan nilai sah yang tercantum. |

## 16. `msshi forge`

Meninjau roster dan blueprint bot baru, kemudian membuat profil native hanya setelah pilihan --apply dan konfirmasi interaktif.

**Prasyarat.** Home Hermes yang benar dan rancangan JSON berisi id, name, purpose, skills, gap, reviews. Rancangan memakai skill bundel serta penilaian peran yang benar-benar diterima.

**Mulai dari.**

```powershell
msshi forge --roster
```

**Batas dan efek.** Roster/preview tidak membuat bot atau memanggil model. Apply menyiapkan SOUL, metadata dan skill, bukan model/provider/base URL/endpoint/API key atau akun dari bot lain. ID lama/dihapus tidak dipakai ulang. Upstream Bot Forge dan kickoff chat/gateway/notifikasi tidak diaktifkan. Windows upstream belum dijamin; adapter native MSSHI memakai transaksi terpisah. Percakapan desain/review dapat memakai model bila Pengguna memintanya.

### `msshi forge`

Efek: Roster/preview membaca lokal. --apply menulis profil dan receipt setelah konfirmasi, menyiapkan trim bila binary lokal siap, tanpa inferensi, gateway atau unduhan runtime.

```text
usage: msshi forge [-h] [--home HOME] [--roster] [--blueprint BLUEPRINT]
                   [--apply]
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `--home` | opsional; default tidak diisi | Home data yang dituju; lihat catatan keluarga karena managed memakai state MSSHI, bukan home Hermes. |
| `--roster` | opsional; default Tidak/OFF | List IDs and installed skill names only. |
| `--blueprint` | opsional; default tidak diisi | Preview a JSON design; no profile is created by default. |
| `--apply` | opsional; default Tidak/OFF | Terapkan rencana yang didukung command ini; tanpa flag managed tetap merencanakan. |

## 17. `msshi managed`

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

## 18. `msshi services`

Membaca status koneksi lokal; tindakan pemasangan/probe/berbagi OAuth lama dihentikan. Layanan dihubungkan sendiri lewat host bila diperlukan.

**Prasyarat.** Home/profil yang ingin diperiksa; MSSHI tidak menyediakan akun atau key layanan.

**Mulai dari.**

```powershell
msshi services status --hermes-home "C:\HermesClient"
```

**Batas dan efek.** GitLab/Tinyfish/BrightData tidak dipasang atau diberi akun secara otomatis. Flag lama memberi penjelasan kompatibilitas dan tidak membuat koneksi, melakukan probe, atau membagikan cache OAuth.

| Pemilih tindakan | Fungsi | Efek |
| --- | --- | --- |
| status | Baca registrasi lokal. | baca lokal |
| install/probe | Tindakan legacy dihentikan; hubungkan layanan sendiri di host. | penjelasan lokal |

### `msshi services`

Efek: Baca status/penjelasan; tidak mengubah login atau koneksi.

```text
usage: msshi services [-h] [--hermes-home HERMES_HOME] [--share-oauth]
                      [--service {gitlab,tinyfish,brightdata_public}]
                      [--read-test]
                      {status,install,probe}
```

| Argumen/flag | Kebutuhan/default | Fungsi |
| --- | --- | --- |
| `action` | wajib; default tidak diisi | Pilih tindakan yang tercantum; bukan nama file atau profil. Nilai: status, install, probe. |
| `--hermes-home` | opsional; default HERMES_HOME / default host | Home/root Hermes yang dipilih; gunakan nilai eksplisit agar tidak mengarah ke profil lain. |
| `--share-oauth` | opsional; default Tidak/OFF | Flag legacy tanpa tindakan; tidak membagikan kredensial atau cache OAuth. |
| `--service` | opsional; default tinyfish | Nama layanan untuk penjelasan tindakan legacy; tidak membuat koneksi. Nilai: gitlab, tinyfish, brightdata_public. |
| `--hermes-source` | opsional; default tidak diisi | Flag legacy untuk kompatibilitas; tidak menjalankan transport/probe. |
| `--read-test` | opsional; default Tidak/OFF | Flag legacy tanpa tindakan; tidak melakukan probe atau permintaan jaringan. |

## 19. `msshi timesfm`

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

## 20. `msshi brag`

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

## 21. `msshi scrapling`

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

## 22. `msshi harness2`

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

## 23. `msshi optional`

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

## 24. `msshi rea`

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

## 25. `msshi choices`

Membaca fungsi, status instruksi, dan prasyarat mode, platform, paket, skill, fitur dan aplikasi. Cocok sebelum memilih opsi yang belum dikenal.

**Prasyarat.** Hanya paket lokal; tidak perlu akun, model, aplikasi kreatif, atau internet.

**Mulai dari.**

```powershell
msshi choices rea
msshi choices --kind apps --lang id
```

**Batas dan efek.** Katalog memiliki 127 nama kanonis: 67 instruksi bawaan dan 60 referensi eksternal; bukan jumlah repositori. Manifest berisi 51 sumber. Alias bukan skill tambahan; daftar kemampuan tidak membuktikan runtime sudah aktif.

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

## 26. `msshi manual`

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

## 27. `msshi dream`

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

## 28. `msshi voice`

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

## 29. `msshi kat`

Alias legacy untuk helper coding opsional milik Pengguna; membaca status atau menyiapkan opsi deployment yang dipilih sendiri.

**Prasyarat.** Status membaca konfigurasi lokal. Aktivasi membutuhkan profil Shikaku, backend native, endpoint nyata, key akun dan bukti ID model. Dev memerlukan deployment sendiri; preset resmi StreamLake Pro v2.5 adalah varian berbeda dengan penagihan akun sendiri.

**Mulai dari.**

```powershell
msshi kat --home "C:\HermesClient" --mode status
```

**Batas dan efek.** Default OFF; tidak menetapkan model untuk peran Sir. Robot, tidak mengunduh bobot otomatis dan tidak mengubah Main/Council. Model/key/endpoint dipilih privat. Baca status sebelum configure; metadata endpoint bukan bukti inferensi berhasil.

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

## 30. `msshi coder`

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

## 31. `msshi setup`

Wizard enam mode: Academic Mahasiswa (pilihan awal pemasangan baru), Academic Dosen, Solo, tim kustom, paket terpilih, atau MuZA. Instalasi lama mempertahankan preset yang terdeteksi bila mode tidak dipilih eksplisit.

**Prasyarat.** Pilih host dan home yang benar. Academic memakai root/workspace/academic di HermesData; tidak membuat vault Obsidian atau memindahkan akun.

**Mulai dari.**

```powershell
msshi setup --platform hermes --lang id
```

**Batas dan efek.** Model/provider/API key diatur pengguna sendiri. Profil akademik opsional memuat jenjang, topik, tenggat, pedoman dan sapaan. Browser disimpan sebagai pilihan/label untuk login manual, tanpa membuka aplikasi atau menyalin cookie. Rute berat Academic membutuhkan pilihan eksplisit dan aplikasi terdeteksi. Helper coding/REA/voice tetap opsional. MSSHITrim disiapkan otomatis oleh setup native penuh bila runtime terverifikasi; disable/edit pengguna dipertahankan.

### `msshi setup`

Efek: Menulis skill, profil, workspace/template dan receipt sesuai rencana. Tidak memanggil model, membuat login, mengaktifkan TTS atau mengganti preset lama secara diam-diam.

```text
usage: msshi setup [-h]
                   [--platform {hermes,openclaw,claude,codex,antigravity,manual}]
                   [--target-dir TARGET_DIR] [--lang {id,en}]
                   [--mode {solo,custom-bots,selective,muza-preset,academic-mahasiswa,academic-dosen,academic-mahasiswa-dosen}]
                   [--yes] [--default-bot {auto,yukino,keep-hermes}]
                   [--extra-packs EXTRA_PACKS [EXTRA_PACKS ...]]
                   [--extra-skills EXTRA_SKILLS [EXTRA_SKILLS ...]]
                   [--kat-mode {light,ideal,cloud,skip}] [--stage-auto-trim]
                   [--install-steel]
                   [--connect-services {skip,per-profile,share-oauth}]
                   [--academic-project ACADEMIC_PROJECT]
                   [--academic-level ACADEMIC_LEVEL]
                   [--academic-topic ACADEMIC_TOPIC]
                   [--academic-deadline ACADEMIC_DEADLINE]
                   [--academic-campus-guideline ACADEMIC_CAMPUS_GUIDELINE]
                   [--preferred-name PREFERRED_NAME]
                   [--browser {chrome,edge,firefox,none}]
                   [--browser-profile-label BROWSER_PROFILE_LABEL]
                   [--browser-account-label BROWSER_ACCOUNT_LABEL]
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
| `--mode` | opsional; default tidak diisi | Pilih mode operasi; daftar nilai sah dan artinya ada pada tabel tindakan. Nilai: solo, custom-bots, selective, muza-preset, academic-mahasiswa, academic-dosen, academic-mahasiswa-dosen. |
| `--yes/-y` | opsional; default Tidak/OFF | Konfirmasi otomatis tanpa prompt. |
| `--default-bot` | opsional; default auto | auto: instalasi baru memakai default sebagai Yukino, tim lama dipertahankan. keep-hermes: pertahankan default netral dan Yukino bernama. yukino: konversi default eksplisit. Model/provider tidak dipindah antarprofil. Nilai: auto, yukino, keep-hermes. |
| `--extra-packs` | opsional; default tidak diisi | Tambahkan extra packs di langkah [1/4] Skills. |
| `--extra-skills` | opsional; default tidak diisi | Tambahkan extra skill slugs di langkah [1/4] Skills. |
| `--kat-mode` | opsional; default tidak diisi | Pilihan kompatibilitas light/ideal/cloud membuka wizard endpoint; skip menonaktifkan KAT saja. Tidak ada unduhan model lokal. Nilai: light, ideal, cloud, skip. |
| `--stage-auto-trim` | opsional; default Tidak/OFF | Stage plugin fail-open msshi-auto-trim ke profil Hermes di langkah [2/4] Plugin. |
| `--install-steel` | opsional; default Tidak/OFF | Deprecated: diterima sebagai no-op; tidak memasang Steel. |
| `--connect-services` | opsional; default tidak diisi | Deprecated: no-op; layanan eksternal dihubungkan sendiri oleh pengguna. Nilai: skip, per-profile, share-oauth. |
| `--academic-project` | opsional; default tidak diisi | Workspace Academic harus berada di dalam root/workspace pada home Hermes. |
| `--academic-level` | opsional; default teks kosong | Jenjang opsional S1, S2 atau S3. |
| `--academic-topic` | opsional; default teks kosong | Topik riset pengguna, disimpan lokal; tidak memanggil model. |
| `--academic-deadline` | opsional; default teks kosong | Target/tenggat yang dipilih pengguna; bukan undangan kalender. |
| `--academic-campus-guideline` | opsional; default teks kosong | Label/lokasi pedoman kampus yang dipilih, bukan izin memindai semua dokumen. |
| `--preferred-name` | opsional; default teks kosong | Sapaan pilihan pengguna dengan ejaan persis; bukan nama pembuat preset. |
| `--browser` | opsional; default tidak diisi | Pilihan Chrome, Edge, Firefox atau none; tidak membuka browser atau login. Nilai: chrome, edge, firefox, none. |
| `--browser-profile-label` | opsional; default teks kosong | Label profil browser untuk pengguna; bukan direktori atau cookie. |
| `--browser-account-label` | opsional; default teks kosong | Label akun untuk login manual; jangan isi password/API key. |
| `--connect-apps` | opsional; default tidak diisi | Sambungkan Bot -> CLI-Anything -> Apps di langkah [4/4]. Nilai: skip, auto-reconnect, select. |
| `--connect-bots` | opsional; default tidak diisi | Daftar bot (dipisah koma atau 'all') untuk langkah [4/4]. |
| `--connect-targets` | opsional; default tidak diisi | Daftar app target (dipisah koma atau 'detected') untuk langkah [4/4]. |
| `--with-rea` | opsional; default Tidak/OFF | Opt-in analisis statis JavaScript/arsip: pasang instruksi REA; runtime Node/npm dan engine native terpisah. Default OFF. |
| `--download-pdf` | opsional; default Tidak/OFF | Minta pengiriman PDF secara eksplisit; rilis ini juga mengirim otomatis kecuali opt-out. |
| `--no-pdf` | opsional; default Tidak/OFF | Lewati salinan otomatis PDF sesudah instalasi/update; tidak membatalkan pemasangan skill. |
| `--pdf-version` | opsional; default tidak diisi | Versi panduan yang ada di katalog, default latest; PDF berbeda dari pemasangan runtime. |
| `--pdf-dest` | opsional; default tidak diisi | Folder tujuan PDF panduan; default Downloads/MSSHI_Manuals atau folder manual data MSSHI. |

## 32. `msshi select`

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

## 33. `msshi bootstrap`

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

Sesudah update, periksa `--help` versi aktif dan cocokkan jenis receipt sebelum rollback.



# 10. Katalog fungsi skill, pilihan fitur, dan aplikasi

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

## Pembagian instruksi menurut preset

Angka ini berasal dari manifest publik, bukan hitungan laptop pembuat. Satu
skill dapat dibagi beberapa bot; jumlah per kolom tidak dijumlahkan untuk
mendapat katalog unik. Academic sengaja memasang pilihan ringan sesuai peran,
bukan memaksakan seluruh runtime atau seluruh 67 skill pada setiap bot.

| Preset | Yukino | Shizuka | Val | Kiki | Coder | Skill unik |
| --- | --- | --- | --- | --- | --- | --- |
| Academic Mahasiswa | 13 | 13 | 19 | 12 | 13 | 35 |
| Academic Dosen | 13 | 14 | 21 | 12 | 13 | 36 |
| MuZA | 31 | 27 | 38 | 22 | 24 | 67 |

Koleksi lama/kustom, integrasi terkurasi, alias dan wrapper opsional dapat
membuat jumlah folder pada komputer berbeda. Source/cache eksternal bukan
tambahan skill aktif otomatis. REA opsional berada terpisah dan default OFF.

## Seluruh 67 skill standar

Untuk setiap nama pada tabel, Pengguna dapat menyebut hasil yang ingin dibuat
atau berkata "Gunakan skill [nama] untuk [hasil] dengan input ini". Nama skill
bukan selalu slash command. Agen hanya memuat panduan yang relevan, kemudian
memeriksa prasyarat aktual; memasang instruksi bukan mengeksekusi program.

| Skill | Fungsi singkat | Pemicu / prasyarat yang perlu disiapkan |
| --- | --- | --- |
| academic-plotting | Menghasilkan figur publikasi dari data dan spesifikasi yang disepakati. | Berikan data, unit, tujuan figur dan format; renderer plotting/generasi diagram harus tersedia, generasi hosted terpisah. |
| ai-research-explore | Merancang eksperimen kandidat yang terpisah dari baseline. | Repo, batas eksperimen, data dan anggaran komputasi yang disetujui; exploration bukan pekerjaan startup. |
| ai-research-reproduction | Menetapkan target reproduksi penelitian yang dapat dibuktikan. | README/paper, target reproduksi kecil, dependency dan dataset berizin; jangan menjalankan seluruh training tanpa mandat. |
| analyze-project | Memetakan struktur proyek, konfigurasi, titik masuk, dan risiko perubahan. | Source lokal yang dipilih dan tujuan audit; mulai read-only sebelum perubahan. |
| antigravity-webdev-cybersec | Hubungkan pengerjaan web dan evaluasi keamanan terotorisasi dengan Antigravity, Goose, dan alat lokal. | Workspace coding, stack, lingkungan uji dan target keamanan yang diotorisasi; bukan scan jaringan otomatis. |
| auto-curiousity-for-film-making | Menguji kemampuan alat kreatif dan teknik produksi dalam eksperimen terpisah. | Aplikasi/tugas baru yang dipilih; baca help/docs dan buat uji kecil. Pengetahuan source tidak menggantikan runtime/akun. |
| autoresearch | Mengoordinasikan siklus eksperimen dan sintesis dengan batas berhenti. | Proposal, data, batas eksperimen dan biaya; model/training dijalankan hanya bila benar-benar dipilih. |
| backward-traceability | Menautkan angka dan hasil laporan kembali ke data, skrip, atau perhitungan. | Angka hasil, kode dan sumber yang sah; menjaga jejak ke artefak pembentuk, bukan mengarang bukti. |
| brag | Rancang video peluncuran produk yang dapat diedit dengan Hyperframes, dimulai dari konsep dan review manusia. | msshi brag doctor/init; init hanya brief. Komposisi editable, renderer dan preview perlu sebelum render MP4. |
| brainstorming-research-ideas | Memakai kerangka ideasi terstruktur untuk menemukan pertanyaan layak. | Sebut nama skill atau hasil yang diinginkan; sediakan input dan sumber yang diizinkan. Panggilan model/tool mengikuti host dan batas biaya. |
| business-sage | Menyusun analisis usaha, skenario finansial, dan pertanyaan verifikasi aturan yang relevan. | Skenario dan angka yang dipilih; fakta pasar/aturan perlu sumber terkini. Bukan jaminan untung atau pengganti profesional. |
| career-ops | Bantu CV-lowongan, strategi karier, tracker dan wawancara; source, runtime dan CV pengguna terpisah. | msshi integrations source career-ops; data CV/profil privat dan runtime Node jika dipilih, tanpa melamar otomatis. |
| chatgpt-hermes-portability-kit | Memandu adaptasi metode dan profil ke platform lain menggunakan sumber yang sah. | Bahan konteks milik Pengguna yang dibagikan secara sadar; akun/vault/knowledge pribadi pembuat tidak ikut paket. |
| cli-anything-business-sage | Menjalankan perhitungan bisnis terstruktur melalui harness lokal yang tersedia. | Harness bsage/CLI terpisah jika dipasang; periksa --help dan fungsi deterministik sebelum mengirim data. |
| cli-anything-universal-bridge | Daftarkan, periksa, dan jalankan rute aplikasi, browser, serta alat agen yang tersedia saat dibutuhkan. | msshi connect --catalog/--status; app harus tersedia sesuai preset, task ticket untuk eksekusi; tidak autostart. |
| creative-thinking-for-research | Mencoba reframing, analogi, dan kombinasi konsep untuk membuka pilihan. | Sebut nama skill atau hasil yang diinginkan; sediakan input dan sumber yang diizinkan. Panggilan model/tool mengikuti host dan batas biaya. |
| data-analysis | Memeriksa kualitas data, asumsi, uji statistik, dan ketidakpastian. | Dataset, definisi variabel dan pertanyaan statistik; Python/paket analisis tersedia, simpan data asli. |
| deep-research | Menyusun pertanyaan, menelusuri literatur, dan mensintesis bukti yang dapat diperiksa. | Sebut nama skill atau hasil yang diinginkan; sediakan input dan sumber yang diizinkan. Panggilan model/tool mengikuti host dan batas biaya. |
| evaluating-code-models | Menguji keluaran model kode dengan tugas dan tolok ukur yang relevan. | Harness, dataset dan mesin model yang dipilih; benchmark dapat mahal dan harus dibatasi. |
| evaluating-llms-harness | Rencanakan evaluasi LLM memakai harness yang kompatibel dan anggaran yang disepakati. | Harness, dataset berizin, model serta anggaran komputasi/API; tidak menguji semua model otomatis. |
| explore-code | Mengembangkan perubahan eksperimen dalam ruang kerja terisolasi. | Workspace terisolasi/branch, rencana perubahan dan tes penerimaan; edit harus dalam mandat. |
| explore-run | Menjalankan uji terbatas dengan anggaran dan catatan hasil yang jelas. | Rencana eksperimen, dependency, data dan budget; batasi matriks percobaan sebelum run. |
| filmmaking-videography-photography-s2 | Menyatukan konsep, pengarahan, kamera, foto, penyuntingan, warna, dan suara. | Brief, hak aset dan review konsep; aplikasi/model generasi tidak otomatis disertakan. |
| firecrawl-competitive-intel | Membandingkan perubahan produk, harga, dan fitur dengan bukti bertanggal. | Alat pencarian/Firecrawl yang benar-benar tersedia dan izin sumber; akun/kuota layanan terpisah, tidak mengirim data otomatis. |
| firecrawl-dashboard-reporting | Mengambil dan memeriksa indikator dasbor untuk pelaporan. | Alat pencarian/Firecrawl yang benar-benar tersedia dan izin sumber; akun/kuota layanan terpisah, tidak mengirim data otomatis. |
| firecrawl-deep-research | Mengumpulkan bukti web untuk sintesis dengan atribusi. | Alat pencarian/Firecrawl yang benar-benar tersedia dan izin sumber; akun/kuota layanan terpisah, tidak mengirim data otomatis. |
| firecrawl-knowledge-base | Menyiapkan koleksi dokumen, potongan, serta metadata asalnya. | Alat pencarian/Firecrawl yang benar-benar tersedia dan izin sumber; akun/kuota layanan terpisah, tidak mengirim data otomatis. |
| firecrawl-research-papers | Menemukan dan memeriksa makalah pada sumber akademik yang relevan. | Alat pencarian/Firecrawl yang benar-benar tersedia dan izin sumber; akun/kuota layanan terpisah, tidak mengirim data otomatis. |
| focus-my-energy | Menyesuaikan beban tugas dan langkah awal dengan energi yang dilaporkan pengguna. | Kondisi tenaga/waktu yang dinyatakan Pengguna; bukan diagnosis atau aturan jam tetap. |
| generate-fresh-ideas | Menghasilkan alternatif dari beberapa lensa kreatif untuk disaring pengguna. | Sebut nama skill atau hasil yang diinginkan; sediakan input dan sumber yang diizinkan. Panggilan model/tool mengikuti host dan batas biaya. |
| get-more-perspectives | Menguji keputusan dari beberapa sudut pandang sebelum memilih. | Sebut nama skill atau hasil yang diinginkan; sediakan input dan sumber yang diizinkan. Panggilan model/tool mengikuti host dan batas biaya. |
| github-research | Menelaah lisensi, rancangan, pemeliharaan, dan kesiapan repositori. | Sebut nama skill atau hasil yang diinginkan; sediakan input dan sumber yang diizinkan. Panggilan model/tool mengikuti host dan batas biaya. |
| harness2 | Kelima bot dapat menyusun proposal dan demo evaluasi harness; tidak mempromosikan perubahan otomatis. | msshi harness2 status/plan; demo deterministik atau eksperimen terpilih, bukan auto-upgrade model bot. |
| higgsfield-skills | Rutekan kebutuhan produksi kreatif ke modul Higgsfield yang sesuai setelah konsep disetujui. | Source/modul sesuai tugas, akun dan kredit layanan bila memakai generasi hosted; belum berarti runtime/generasi siap. |
| humanizer-en | Sunting prosa bahasa Inggris agar terasa alami sambil menjaga makna, suara penulis, dan sitasi. | Draf Inggris dan gaya yang dipilih; jaga fakta, kutipan dan atribusi, tanpa menjanjikan lolos detektor. |
| humanizer-indonesia | Sunting prosa bahasa Indonesia sesuai ragam pembaca sambil menjaga makna, istilah, dan sitasi. | Draf Indonesia serta ragam akademik/ajar yang dipilih; pertahankan makna dan sitasi. |
| idea-generation | Mengembangkan dan menyaring gagasan penelitian dalam beberapa putaran. | Sebut nama skill atau hasil yang diinginkan; sediakan input dan sumber yang diizinkan. Panggilan model/tool mengikuti host dan batas biaya. |
| langsmith-observability | Memandu observabilitas dan evaluasi LangSmith pada lingkungan yang disetujui. | Proyek trace/evaluasi dan akun/deployment yang dipilih; periksa izin data sebelum mengirim telemetri. |
| literature-review | Membangun tinjauan pustaka dengan beberapa perspektif dan jejak sumber. | Sebut nama skill atau hasil yang diinginkan; sediakan input dan sumber yang diizinkan. Panggilan model/tool mengikuti host dan batas biaya. |
| match-my-writing-style | Menerapkan Voice Card yang disediakan pengguna sesuai audiens dan jenis tulisan. | Sampel gaya yang Pengguna izinkan; jangan menyalin suara/profil pribadi pembuat. |
| math-reasoning | Memeriksa langkah penalaran matematika dan syarat berlakunya. | Sebut nama skill atau hasil yang diinginkan; sediakan input dan sumber yang diizinkan. Panggilan model/tool mengikuti host dan batas biaya. |
| mattpocock-engineering | Pilih disiplin TDD, debugging dan domain model; orkestrator/spec publish hanya saat diminta. | Workflow engineering yang sesuai; bagian explicit-only memerlukan permintaan, bukan semua slash otomatis tersedia. |
| motion-graphics-suite | Pilih dan hubungkan empat rujukan motion graphics untuk komposisi yang tetap dapat diedit. | Pilih alur Bang Motion/Remotion/Hyperframes sesuai proyek; Node/browser/FFmpeg/font/aset perlu tersedia. |
| muza-skripsi-template | Menyusun template Word (.docx) skripsi/tugas akhir sesuai aturan pedoman kampus, mencari logo & pejabat resmi otomatis, dan menyuntikkan hasil MuZA_Search. | msshi skripsi --help; pedoman kampus dan input sendiri. DOCX/RIS perlu dependency; hasil wajib ditinjau. |
| nemo-evaluator-sdk | Memandu evaluasi dengan NeMo Evaluator SDK jika dependensinya tersedia. | SDK/harness, dataset dan model yang dipilih; kebutuhan hardware dan biaya terpisah dari instruksi. |
| notebooklm-thinking-datascience | Terapkan metode berpikir sistem dan data science dari indeks sumber milik pengguna. | Bahan/notebook milik Pengguna jika disediakan; tidak memberi akses ke akun atau 600 sumber pribadi pembuat. |
| novelty-assessment | Menguji klaim kebaruan terhadap studi terdekat dan batas pencarian. | Sebut nama skill atau hasil yang diinginkan; sediakan input dan sumber yang diizinkan. Panggilan model/tool mengikuti host dan batas biaya. |
| paper-context-resolver | Mengikat klaim reproduksi pada bagian, gambar, tabel, atau lampiran makalah. | Sebut nama skill atau hasil yang diinginkan; sediakan input dan sumber yang diizinkan. Panggilan model/tool mengikuti host dan batas biaya. |
| paper-revision | Memetakan catatan revisi ke perubahan konkret dan bukti perbaikan. | Sebut nama skill atau hasil yang diinginkan; sediakan input dan sumber yang diizinkan. Panggilan model/tool mengikuti host dan batas biaya. |
| paper-writing-section | Menyusun dan menyunting bagian naskah akademik dengan dua tahap pemeriksaan. | Sebut nama skill atau hasil yang diinginkan; sediakan input dan sumber yang diizinkan. Panggilan model/tool mengikuti host dan batas biaya. |
| parenting-6d-gad-mdd | Dukung percakapan dengan empati, struktur, dan otonomi; panduan ini tidak menggantikan perawatan klinis. | Dukungan belajar sesuai konteks yang dinyatakan; bukan diagnosis, layanan klinis atau penyalinan profil kesehatan. |
| persona-shizuka-yukino-shikaku | Menjaga karakter, kontrak serah terima, dan batas kepemilikan tugas lima bot. | SOUL aktif serta interaksi dua tipe menjadi acuan; referensi karakter bukan pengaturan model atau voice otomatis. |
| phoenix-observability | Memandu tracing dan evaluasi Phoenix tanpa memindahkan data di luar lingkup. | Deployment/trace data yang diotorisasi; akun, paket dan kebijakan pengiriman data diperiksa terpisah. |
| prep-for-meetings | Menyusun ringkasan pertemuan dari catatan dan tujuan yang tersedia. | Tujuan, peserta, bahan dan rentang waktu; hasilkan kesiapan/rundown. Notulensi hanya dari catatan nyata. |
| prep-for-meetings-2 | Memadatkan bahan pertemuan menjadi pokok bahasan dan kartu pengingat. | Gunakan variasi brief yang paling cocok, bukan dua proses berulang; jangan menjadwalkan/mengirim otomatis. |
| rea-video | Kiki membedah referensi video ke VIDEO.md; VLM, audio-model dan remake adalah pilihan terpisah. | msshi integrations source rea-video; FFmpeg/ffprobe dan input berizin. OCR/ASR/stems/VLM/generasi merupakan opt-in terpisah. |
| rebuttal-writing | Menyusun jawaban poin demi poin untuk masukan pembimbing atau reviewer. | Sebut nama skill atau hasil yang diinginkan; sediakan input dan sumber yang diizinkan. Panggilan model/tool mengikuti host dan batas biaya. |
| remote-jobs | Cari perusahaan remote dari direktori lokal terpin; lowongan aktif tetap diverifikasi terpisah. | Cache direktori melalui integrations source; konfirmasi lowongan di halaman resmi, daftar bukan lowongan pasti aktif. |
| research-paper-writing | Memeriksa struktur argumen dan hubungan antara klaim, bukti, serta pembahasan. | Sebut nama skill atau hasil yang diinginkan; sediakan input dan sumber yang diizinkan. Panggilan model/tool mengikuti host dan batas biaya. |
| scrapling | Ekstraksi CSS/XPath dari HTML lokal dalam runtime parser terisolasi. | msshi scrapling status/parse; menerima HTML lokal dan CSS/XPath, bukan URL/crawler/login. |
| slide-generation | Menyusun presentasi dari argumen, hasil, dan visual yang dapat diverifikasi. | Materi/paper yang sudah diperiksa dan target audiens; LaTeX/renderer atau aplikasi slide perlu tersedia. |
| symbolic-equation | Mencari kandidat persamaan yang dapat ditafsirkan dan diuji. | Data numerik dan batas pencarian persamaan; runtime/eksperimen/model dipilih terpisah. |
| table-generation | Membangun tabel akademik dari hasil terverifikasi beserta satuan dan catatan. | Hasil/angka terverifikasi dan format tabel; bukan sumber hasil eksperimen baru. |
| timesfm-forecasting | Prediksi deret waktu numerik secara lokal memakai TimesFM 2.5 setelah setup runtime dan bobot terpisah. | msshi timesfm status; peramalan numerik memakai runtime/bobot lokal yang dipilih, bukan pencarian literatur. |
| unlimited-ocr-2 | Rutekan ekstraksi dokumen dan gambar berhalaman ke OCR yang tersedia dengan penunjuk bukti. | Dokumen berizin; gunakan ekstraksi teks lokal dulu. OCR model membutuhkan runtime/bobot/RAM terpisah. |
| unslop | Tinjau dan perbaiki desain antarmuka; skill ini mengubah UI, bukan gaya prosa bot. | Layar UI atau output visual yang ingin diperbaiki; audit/gagasan dulu, implementasi oleh pemilik kode. |
| wise-judgment-and-sovereign-orchestrator | Mengatur pilihan alur, anggaran, persetujuan, delegasi, dan sintesis hasil Val. | Tujuan, izin dan kontrak handoff; tidak memanggil seluruh tim untuk setiap pesan. |

## Plugin native yang disertakan source MSSHI

| ID plugin | Fungsi / kapan bekerja | Pemakaian / batas |
| --- | --- | --- |
| msshi-interaction | State dan tool protokol Tipe 1/2; tidak memanggil model pada status/startup. | msshi interaction --status/--protocol. Proyek penuh perlu binding Pengguna, tools host dan izin biaya. |
| msshi-auto-trim (MSSHITrim) | Hook otomatis pada hasil tool JSON yang lolos ukuran/format/kesetaraan. | Setup penuh menyiapkan profil native; msshi trim --status. Tidak mengubah chat, proxy, sertifikat atau provider. |
| msshi-team-routing | Pemetaan/handoff peran sesuai backend yang aktif. | Gunakan schema delegasi host yang tersedia. Backend eksplisit dipertahankan; jangan menganggap teks SOUL menciptakan transport. |
| msshi-steel-policy (legacy) | Source kompatibilitas lama yang jalur pemasangannya dihentikan. | Tidak dipasang atau diaktifkan oleh setup; tidak perlu menyalakannya untuk memilih Chrome/Edge/Firefox. |

Plugin lain seperti Planner, Meeting-Copilot, Transcribo, Dreaming upstream dan
OmniVoice mengikuti prasyarat/aktivasi masing-masing. Adapter Dreaming offline
MSSHI bukan bukti plugin upstream penuh dipasang. Tidak ada akun kalender,
Discord, Telegram, Gmail, Google Drive atau NotebookLM pembuat dalam paket.
Status terpasang, terkonfigurasi, terautentikasi dan tugas riil berhasil
dilaporkan terpisah. Plugin pribadi di laptop seorang pengguna tidak otomatis
menjadi bagian rilis publik.

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
| steel | Dihentikan dari pemasang MSSHI. Pilih browser lokal dan lakukan login sendiri; tidak ada transfer akun/cookie. |
| gitlab | GitLab tidak disambungkan atau diberi kredensial oleh installer MSSHI. Hubungkan sendiri melalui pengaturan resmi layanan bila diperlukan; biaya dan izin mengikuti akun pengguna. |
| tinyfish | Tinyfish tidak disambungkan atau diberi kredensial oleh installer MSSHI. Hubungkan sendiri melalui pengaturan resmi layanan bila diperlukan; biaya dan izin mengikuti akun pengguna. |
| brightdata | BrightData tidak disambungkan atau diberi kredensial oleh installer MSSHI. Hubungkan sendiri melalui pengaturan resmi layanan bila diperlukan; biaya dan izin mengikuti akun pengguna. |
| llmtrim | Padatkan keluaran JSON besar yang memenuhi syarat tanpa kehilangan nilai, dengan pemeriksaan kesetaraan. Tidak memadatkan semua chat atau menjamin persentase penghematan tagihan tertentu. |
| hersona | Cari referensi persona dan siapkan draf penyesuaian karakter melalui CLI. Persona aktif tetap mengikuti SOUL native; draf tidak otomatis menimpa pengaturan pengguna. |
| timesfm-runtime | Siapkan dependency dan bobot TimesFM untuk prediksi deret waktu lokal. Memerlukan unduhan, ruang disk, dan RAM cukup; uji kecil bukan jaminan akurasi pada data pengguna. |
| brag-runtime | Siapkan Hyperframes untuk memvalidasi dan merender video lokal dari komposisi HTML yang dapat diedit. Perlu Node, browser/FFmpeg yang sesuai, RAM/disk, dan hak aset; font dapat memerlukan unduhan. |
| scrapling-runtime | Siapkan parser terisolasi untuk ekstraksi CSS/XPath dari file HTML lokal. Memerlukan dependency Python yang kompatibel; opsi ini tidak menyediakan browser stealth atau crawler jaringan. |
| harness2-runtime | Siapkan framework untuk demo perbaikan harness yang deterministik dan proposal eksperimen. Perlu Python/dependency yang kompatibel; benchmark berbasis model dan promosi perubahan ke bot tidak otomatis aktif. |
| managed-update | Perbarui salinan skill yang terdaftar dan fingerprint-nya cocok; pertahankan edit lokal yang berbeda. Pendaftaran ini bukan izin mengganti SOUL, provider/model, atau semua dependency runtime. |
| upstream-cache | Simpan checkout referensi eksternal di luar folder skill agar dapat diperiksa atau diintegrasikan terpisah. Cache memakai internet/disk dan tidak sama dengan fitur yang sudah terpasang atau aktif. |
| setup-skills | Tambahkan paket atau skill individual ekstra dan kelola skill opsional REA per bot saat setup tanpa mengubah skill kustom yang sudah ada. |
| setup-plugins | Kelola addon lokal opsional seperti auto-trim, KAT, laporan Dreaming offline dan OmniVoice bila telah diverifikasi. Tidak memasang browser cloud atau koneksi layanan otomatis. |
| setup-services | Pilih Chrome, Edge, Firefox, atau tidak memilih browser; simpan label profil/akun untuk login manual. Tidak memasang layanan eksternal, membuka browser, membaca akun, atau menyalin cookie. |
| setup-bot-apps | Hubungkan tiap profil bot ke jembatan CLI-Anything dan aplikasi lokal atau web secara on-demand memakai tiket tugas, dengan auto_open_on_boot tetap nonaktif. |
| context-sources | Cache source terpin CareerOps, direktori remote, Matt Pocock dan rea-video di luar skills; default status tidak mengunduh atau menjalankan model. |
| career-ops-runtime | Pasang dependency Node secara eksplisit tanpa lifecycle scripts atau unduhan Chromium; CV/data pengguna tetap privat, tugas dan akun terpisah. |
| rea-video-runtime | Pasang runtime Python terisolasi; analisis lokal dapat melewati OCR/ASR/stems/VLM. Fitur model, unduhan bobot dan generasi tidak otomatis aktif. |
| interaction | Tipe 1: Main berkonsultasi ke Advisor untuk proyek yang jelas. Tipe 2: Main memakai Dewan dua putaran dengan audit Main di antaranya, tanpa subagen terpisah. Pertanyaan singkat tidak memicu proses berat. Panggilan model memerlukan konfigurasi dan persetujuan biaya; status/pemasangan tidak memanggil model. |

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

Ada 60 nama referensi eksternal pada matriks. REA termasuk daftar penemuan ini tetapi pemasangan instruksinya merupakan opsi khusus default OFF. Sejumlah nama historis memuat kata MCP; arsitektur desktop MuZA v3 tetap memakai rute native CLI, sedangkan koneksi MCP web disiapkan sendiri oleh pengguna bila diperlukan. Daftar ini tidak memerintahkan pemasangan semua repo atau server.

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

Sumber: [katalog fungsi](https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/blob/v3.1.2/configs/option_help.json), [matriks peran](https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/blob/v3.1.2/configs/bot_role_and_skill_matrix.json), dan [fungsi koneksi](https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/blob/v3.1.2/skills/cli-anything-universal-bridge/scripts/connection_help.json).


# 11. Pegangan cepat dan bahan latihan

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
