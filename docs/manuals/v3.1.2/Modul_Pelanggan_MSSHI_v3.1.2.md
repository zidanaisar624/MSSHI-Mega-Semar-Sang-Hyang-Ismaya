# Modul Pelanggan Lengkap MSSHI v3.1.2

Edisi distribusi **Minggu, 22 November 2026 (Asia/Jakarta)**. Panduan lengkap 100% model-agnostic untuk 5 Misi Utama, 4 Pilar Sistem Kognitif, Academic Mahasiswa S1-S3, Academic Dosen, Preset MuZA 5 Bot, Interaksi 2 Tipe v0.2.0, MSSHITrim, Light Build Windows 10 RAM 4 GB, dan seluruh 39 keluarga command CLI (109 node).

- **Baseline Commit GitHub:** `f400fbabf2e74638a443b1d51620d90e43c536e7`
- **Source Manifest SHA-256:** `83f2a315daf8d4dd389bace6a4f23198dcdec5bb9e67d29fdc73f22caf9c9bf9` (`source-manifest.json`)
- **Inventaris Terverifikasi:** `75` skill bundel (`53` inti + `22` wrapper), `2` skill opsional (default OFF), `64` upstream terpin, `7` plugin native, `39` keluarga CLI (`109` node), dan `47` rute aplikasi CLI-Anything.

---

## Daftar Isi

- **Bab 1.** Pengenalan MSSHI v3.1.2, 5 Misi Utama & 4 Pilar Sistem Kognitif
- **Bab 2.** Spesifikasi Perangkat, Light Build Windows 10 RAM 4 GB & Instalasi
- **Bab 3.** 6 Mode Setup, Preset Academic (Mahasiswa/Dosen) & Preset MuZA 5 Bot
- **Bab 4.** Arsitektur Interaksi 2 Tipe, Pencari Skill 4-Lapis & MSSHITrim
- **Bab 5.** Panduan Operasional 5 Misi Utama (Belajar, Riset, Kreasi, Coding & Harian)
- **Bab 6.** Integrasi Aplikasi (CLI-Anything), Browser Manual & Keamanan
- **Bab 7.** Operasional Harian, Pembaruan Terkelola, Diagnostik & Troubleshooting
- **Bab 8.** Praktikum Terpandu: 5 Skenario Latihan End-to-End
- **Bab 9.** Referensi Lengkap 39 Keluarga Command CLI (109 Node Aktif)
- **Bab 10.** Katalog Lengkap 75 Skill Bundel, 2 Opsional, 7 Plugin & 6 Paket
- **Bab 11.** Katalog Lengkap 64 Sumber Upstream Terpin & Tata Kelola Lisensi
- **Bab 12.** Identitas Versi, Manifest Sumber, Checklist Serah Terima & Dukungan

# 1. Pengenalan MSSHI v3.1.2, 5 Misi Utama & 4 Pilar Sistem Kognitif

MSSHI (Mega Semar Sang Hyang Ismaya — Multi-Agent Sovereign Sage & Hermes Intelligence) adalah paket orkestrasi skill, kerangka 5 persona spesialis, plugin native hemat token, dan alat CLI lokal untuk Hermes Agent (Desktop maupun CLI). Modul Pelanggan Lengkap edisi Minggu, 22 November 2026 (Asia/Jakarta) ini ditulis ulang secara menyeluruh dari source GitHub aktual pada commit f400fba (versi paket 3.1.2) agar setiap angka, skill, plugin, upstream, dan perintah CLI 100% sesuai dengan repositori terkini.

> **4 Prinsip Keras MSSHI v3.1.2 (Terverifikasi di Kode & Audit)**
> - 1. 100% Model-Agnostic & User-Agnostic: Pengguna memilih sendiri Provider, Model AI, Endpoint/Base URL, dan API Key di Hermes. MSSHI mengunci jev_model_routing: false dan tidak pernah menimpa konfigurasi model, SOUL.md kustom, atau mengirim kredensial ke pihak ketiga.
> - 2. Hemat Token & RAM (Zero-Waste): Dilengkapi MSSHITrim (kompresi JSON tool 20%-55% lossless, 0 LLM calls), Caveman (handoff internal ringkas), interaksi 2 tipe (obrolan singkat 0 agen ekstra), Fast Skill Scanner (p95 <= 2,0 detik), serta cache sumber on-demand di luar folder skills/.
> - 3. Adaptif Semua Drive & Laptop Ringan: Bebas dipasang di Drive C:, D:, E:, atau direktori kustom mana saja; menyediakan Mode Hemat Windows 10 RAM 4 GB (Light Build <= 50 MB, ekstra RAM idle <= 150 MB) tanpa kewajiban Obsidian, Docker, atau WSL2.
> - 4. Terkendali Manusia (Human-Gated): Aplikasi lokal tidak dibuka otomatis saat boot (auto_open_on_boot: false), refleksi memori Dreaming & proposal Harness2 selalu menunggu persetujuan manusia, dan semua tahap kreatif/audit keamanan berizin meminta konfirmasi eksplisit.

## Inventaris Aktual Repositori MSSHI v3.1.2 (Edisi 22 November 2026)

| Komponen Paket | Jumlah Aktual | Keterangan & Aturan Pengelolaan |
| --- | --- | --- |
| Skill Bundel Aktif | 75 skill (53 inti + 22 wrapper) | Seluruh folder skills/*/SKILL.md yang teraudit 0-orphan pada bot_role_and_skill_matrix.json & msshi_cognitive_system.json. |
| Skill Opsional (Opt-In) | 2 skill (default publik OFF) | optional/rea (khusus Shikaku/Coder) dan optional/imagination-studio (khusus Kiki-Chii/Filmmaker). |
| Total Katalog Kanonis | 136 nama (75 bundel + 61 rujukan) | Rujukan eksternal menunjukkan alat/sumber terhubung yang disiapkan terpisah sesuai kebutuhan & lisensi. |
| Sumber Upstream Terpin | 64 sumber (61 Git, 2 model-card, 1 katalog) | Disimpan di luar pemindai skills/ (upstreams/ atau msshi-private/context-sources/), cek update read-only via msshi upstreams check. |
| Plugin Native Hermes | 7 plugin (6 aktif/tersedia + 1 retired) | msshi-auto-trim (MSSHITrim), msshi-interaction v0.2.0, msshi-team-routing, chalk, spacewise, sharewise; msshi-steel-policy berstatus retired. |
| Keluarga CLI & Subperintah | 39 keluarga (109 node CLI) | Seluruh 39 perintah utama (+ alias status) & 70 subperintah diverifikasi langsung dari parser aktual scripts/msshi_cli.py. |
| Mode Setup & Paket Kategori | 6 mode · 6 paket kategori | Mode: academic-mahasiswa, academic-dosen, muza-preset, solo, custom-bots, selective. Paket: core, filmmaking, business, thesis, webdev, cybersec. |
| Peran Bot Hirarki | 5 spesialis + profil default netral | Yukino Yukinoshita, Sensei Shizuka Hiratsuka, Val, Kiki-Chii, dan Shikaku Nara (Sir. Robot). |

## 5 Misi Utama & 4 Pilar Sistem Kognitif Tertutup

*(Diagram vektor `missions_pillars` disertakan penuh pada edisi PDF.)*

| Misi Utama | Lead & Koordinator | Spesialis Pendukung | Alur & Skill Kunci |
| --- | --- | --- | --- |
| 1. Belajar (Personal Tutor) | Shizuka + Yukino | Val (teori/math), Shikaku (kode), Kiki-Chii (visual) | belajar-pemula (tanpa /command, 1 konsep/giliran), parenting-6d-gad-mdd, Chalk, LearnLoop (opt-in), CodeCoach/Shikaku, & koneksi OSSU CS (63 matkul). |
| 2. Tugas, Skripsi, Tesis & Disertasi | Val + Shizuka | Yukino (ideasi), Kiki-Chii (plot/slide), Shikaku (skrip) | Lima Lapis Konteks, riset-mendalam-nusantara-global (khusus Val), deep-research, literature-review, novelty-assessment, MuZA Skripsi v1.1 (.docx), Unlimited-OCR-2, TimesFM 2.5. |
| 3. Konten Kreasi (Studio) | Kiki-Chii + Shizuka | Yukino (hook), Val (fakta), Shikaku (kode web/motion) | Concepting First + review manusia: filmmaking-videography-photography-s2, Higgsfield 9 modul, lemo-opuscar (15 kat/99 gaya), motion-graphics-suite, brag, rea-video, unslop, slide-generation, opsional Imagination Studio. |
| 4. Coding & Cybersec Berizin | Shikaku + Shizuka | Val (benchmark), Kiki-Chii (polish UI) | analyze-project -> explore-code + mattpocock-engineering (TDD) -> rust-anything (porting Rust terverifikasi) -> grim-prompter (read-only) -> claude-bughunter (khusus aset berizin) -> Harness2 / opsional REA. |
| 5. Teman Curhat & Harian | Yukino (Main-Only) | 0 bot ekstra (kecuali diminta eksplisit) | Obrolan hangat hemat token (fast_main_only), parenting-6d-gad-mdd, focus-my-energy, prep-for-meetings, Spacewise & Sharewise untuk higienitas file lokal. |

## Lima Status Kesiapan & Matriks Biaya/Efek Perintah

Dalam operasional sehari-hari, penting membedakan lima lapis kesiapan agar tidak menyamakan 'instruksi tersedia' dengan 'tugas sudah terbukti berjalan': (1) Instruksi ditemukan (SKILL.md terbaca), (2) Rute terdaftar di registri CLI-Anything/plugin, (3) Runtime atau dependensi terpasang (Python/Node/FFmpeg/PyTorch), (4) Akun & izin siap (login/key milik pengguna), dan (5) Tugas terbukti berhasil pada input nyata atau fixture.

| Jenis Tindakan | Kredit LLM | Efek Sistem & Prasyarat |
| --- | --- | --- |
| Bantuan, audit & routing lokal | 0 kredit AI | --help, msshi choices, msshi doctor, msshi system status/route, msshi find, msshi light status: 100% lokal & read-only. |
| Cek versi & cek upstream | 0 kredit AI | msshi check dan msshi upstreams check: hanya membaca metadata GitHub secara read-only (butuh internet, 0 perubahan file). |
| Setup, update, fetch cache | 0 kredit AI | msshi setup/update/integrations source --fetch: menulis file lokal, registri, atau cache terpin dengan cadangan otomatis. |
| Refleksi Dreaming & Skrip Lokal | 0 kredit AI | msshi dream, msshi trim, msshi skripsi, msshi scrapling, msshi timesfm, msshi voice: berjalan lokal di CPU/disk perangkat. |
| Chat, Advisor & Dewan MoA | Sesuai model user | Hanya berjalan saat pengguna mengirim pesan ke bot di Hermes; mengikuti provider, model, & kuota yang diatur sendiri oleh pengguna. |
| Layanan web / render GPU lokal | Kuota terpisah | Higgsfield, Imagination Studio, Blender, atau layanan MCP web memiliki syarat akun, lisensi, atau RAM/GPU terpisah. |

# 2. Spesifikasi Perangkat, Light Build Windows 10 RAM 4 GB & Instalasi

Hermes Agent (Desktop maupun CLI) berperan sebagai rumah agen AI, sedangkan MSSHI adalah lapisan orkestrasi ringan di atasnya. Instalasi paling bersih selalu mengikuti urutan empat langkah: (A) Pasang Hermes Agent & isi provider/model mandiri -> (B) Pasang MSSHI v3.1.2 -> (C) Selesaikan Wizard 4+1 Tahap -> (D) Verifikasi dengan msshi doctor & buka New Chat.

## Spesifikasi Perangkat & Rincian Pemakaian Disk/RAM

| Komponen | Minimum (Mode Hemat / Light) | Rekomendasi (Standar) | Lengkap (Full + ML Lokal & Kreatif) |
| --- | --- | --- | --- |
| Sistem Operasi | Windows 10/11 64-bit (PS 5.1+), Linux, macOS | Windows 10/11 64-bit, Linux, macOS | Windows 10/11 (+ WSL2 untuk CodeCoach) / Linux / macOS |
| Prosesor (CPU) | Dual-core (Intel Celeron N4500 / Core i3) | Quad-core (Core i5 / Ryzen 5) | 6-8 core (Core i5/i7 / Ryzen 5/7) |
| Memori (RAM) | 4 GB (auto Mode Hemat <= 6 GB; Hermes CLI, ekstra MSSHI <= 150 MB) | 8-16 GB (Hermes Desktop + 5 profil + MSSHITrim + Dreaming) | 16-32 GB (TimesFM 2.5, OmniVoice, Dewan 2 putaran, Blender/video) |
| Storage Bebas | >= 2 GB (Hermes CLI + MSSHI Light <= 50 MB) | >= 10-15 GB (Hermes Desktop + tools ~6 GB + ruang kerja) | >= 20-25 GB (termasuk TimesFM, OmniVoice, REA, cache & media) |
| Drive C: (Windows) | Min. 3-5 GB bebas (Windows, pagefile, temp) | Min. 5-10 GB bebas (data bebas di D:/E:) | Min. 10+ GB bebas (data besar disarankan di D:/E:) |
| GPU | Tidak wajib (model AI via API/cloud) | Tidak wajib (model AI via API/cloud) | Opsional VRAM 6-12 GB+ (hanya untuk LLM/render 3D/Studio lokal) |

| Komponen MSSHI & Add-on | Ukuran di Disk | RAM Idle | Catatan Operasional Saat Dipakai |
| --- | --- | --- | --- |
| MSSHI Core (1 rilis + 75 skill + 7 plugin) | ~33 MB (Light ZIP <= 50 MB) | ~20-35 MB | Fast Skill Scanner p95 < 0,05 detik (target <= 2,0 s). |
| Hermes Desktop + Tools (Python/Node/Git/FFmpeg) | ~5,6 GB | ~300-800 MB | ~500 MB-1,5 GB saat aktif (Hermes CLI hanya ~100-250 MB). |
| 5 Profil Preset MuZA/Academic + Plugin Inti | ~35-60 MB | 0 MB ekstra | 0 panggilan LLM di latar belakang; 0 proses daemon. |
| Cache context-sources on-demand | 0 MB awal (~40-60 MB penuh) | 0 MB | lemo-opuscar, rust-anything, claude-bughunter, grim-prompter, ossu. |
| Hermes-Dreaming lokal (msshi dream) | ~2 MB | 0 MB | <= 64 MB saat dijalankan secara offline (0 LLM call). |
| REA — analisis statis JS/arsip (opsional) | ~150-180 MB | 0 MB | ~100-250 MB saat dipakai; khusus Shikaku. |
| Imagination Studio wrapper (opsional) | < 1 MB (app lokal terpisah) | 0 MB | Terhubung via http://127.0.0.1:7870 hanya saat dibuka. |
| TimesFM 2.5 — forecasting CPU offline (opsional) | ~1,5-2,0 GB (PyTorch + 925 MB) | 0 MB | Wajib >= 2,5 GiB commit RAM saat run; unload otomatis selesai. |
| OmniVoice — TTS CPU offline (opsional) | ~1,5-3,0 GB (PyTorch + TTS) | 0 MB | ~1,5-2,5 GB saat sintesis suara; auto_start: false, unload otomatis. |

## Cara Pasang MSSHI v3.1.2 (Windows PowerShell 5.1, macOS/Linux, ZIP & Chat Agen)

```text
# 1. Windows PowerShell 5.1+ (Interaktif: pilih Standar/Hemat & bebas Drive C:/D:/E:):
$u = 'https://raw.githubusercontent.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/main/install.ps1'
irm $u | iex

# 2. Windows PowerShell — Mode Hemat Win10 RAM 4 GB ke drive/folder bebas pilihan (mis. E:\):
& ([scriptblock]::Create((irm $u))) -Light -LowRam -InstallDir "E:\MSSHI" -HermesHome "E:\HermesData" -Mode academic-mahasiswa -Platform hermes -Yes

# 3. macOS / Linux Terminal (Bash/Zsh):
U='https://raw.githubusercontent.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya/main/install.sh'
curl -fsSL "$U" | bash

# 4. Paket ZIP Klien (Windows Klik 2x):
#    Ekstrak ZIP MSSHI -> klik ganda MULAI_DI_SINI_PEMULA.bat
# 5. Via Chat Agen AI (Hermes / Antigravity / Claude Code):
#    Minta agen membaca docs/guides/INSTALL_FOR_AGENTS.md lalu memasang tanpa mengubah provider/model.
```

> **Dua Tips Kritis Pengguna Windows (Drive C: Sempit & Anti Admin-Lock)**
> - 1. Drive C: Sempit (< 5 GB bebas): Sebelum menjalankan installer atau mengunduh runtime PyTorch (TimesFM/OmniVoice), arahkan folder temp ke Drive D:/E: ($env:TEMP='D:\HermesData\temp'; $env:TMP='D:\HermesData\temp') dan pastikan Windows Virtual Memory (paging file) aktif pada drive yang lega.
> - 2. JANGAN Jalankan Perintah msshi di PowerShell 'Run as Administrator': Pada Windows, direktori profil Hermes memakai kepemilikan akun standar. Menjalankan msshi setup / msshi voice --enable sebagai Administrator dapat mengubah pemilik file config.yaml menjadi Administrators sehingga Hermes Desktop gagal start (Errno 13 Permission denied). Selalu gunakan PowerShell pengguna biasa!

## Alur Wizard Setup 4+1 Tahap & Light Build Windows 10 RAM 4 GB

| Tahap Wizard | Komponen yang Diatur | Rekomendasi Praktis & Flag Otomasi |
| --- | --- | --- |
| Mode & Lokasi | Pilih 1 dari 6 mode setup + drive/direktori bebas (C:/D:/E:) | --mode academic-mahasiswa\|academic-dosen\|muza-preset\|solo\|custom-bots\|selective |
| [1/4] Skills & Opsional | Extra packs/skills + wrapper opt-in REA (Coding) & Imagination Studio (Kreasi) | --extra-packs, --extra-skills, --with-rea, --with-imagination-studio |
| [2/4] Plugin & Add-on | MSSHITrim (otomatis + UI Desktop), Interaksi 2 Tipe, KAT-Coder, Dreaming, OmniVoice | --stage-auto-trim (disarankan ON); KAT-Coder & OmniVoice opsional |
| [3/4] Browser & Layanan | Label browser manual (Chrome/Edge/Firefox, 0 salin cookie) & koneksi layanan manual | Login tetap manual & aman; BrightData & GDrive terkunci OFF |
| [4/4] Bot -> Apps | Pemetaan bot ke aplikasi lokal CLI-Anything (FFmpeg, Git, Node, Blender, ArtCraft) | --connect-apps auto-reconnect --connect-bots all (auto_open_on_boot: false) |
| [5/5] Mode Resource | Standar (RAM >= 8 GB) vs Mode Hemat Win10 RAM 4 GB (Low-RAM <= 150 MB) | --low-ram atau --resource-profile auto\|light\|normal |

Pada Mode Hemat (Light Build, configs/light_build_manifest.json), paket ZIP deterministik inti berukuran <= 50 MB (uji lokal ~0,74 MB), konsumsi RAM proses idle MSSHI <= 150 MB, Fast Skill Scanner memakai os.scandir stat-first dengan manifest cache JSON (0 baca file saat cache hit, baca frontmatter <= 4096 byte saat miss, p95 <= 2,0 detik), dan secara otomatis memblokir paralelisme MoA berat serta target render grafis berat (blender, obs, cadcraft, filmcraft, anicraft, dll.). Pada laptop RAM 4 GB, jalankan msshi desktop --prefer-cli untuk panduan fallback ke Hermes CLI.

# 3. 6 Mode Setup, Preset Academic (Mahasiswa/Dosen) & Preset MuZA 5 Bot

MSSHI tidak memaksa satu pola kerja untuk semua orang. Pengguna dapat memilih mulai dari satu profil sederhana hingga tim 5 bot spesialis terpadu melalui enam mode setup resmi.

| Mode Setup | Target Pengguna | Struktur Profil & Cakupan Skill |
| --- | --- | --- |
| academic-mahasiswa (Default baru) | Mahasiswa S1, S2, S3 | 5 profil native kampus ringan: Yukino (16), Shizuka (17), Val (26), Kiki-Chii (17), Shikaku/Sir. Robot (20) + koneksi OSSU CS + template akademik (tanpa wajib Obsidian). |
| academic-dosen | Dosen, Pembimbing, Pimpinan Kampus | 5 profil native pengajaran & riset: Yukino (16), Shizuka (18), Val (28, +rebuttal-writing & creative-thinking), Kiki-Chii (17), Shikaku/Sir. Robot (20). |
| muza-preset | Pengguna Lengkap (5 Misi Terpadu) | 5 profil MuZA penuh: Yukino (26), Shizuka (30), Val (42), Kiki-Chii (26), Shikaku (30) + semua 75 skill terdistribusi presisi + 6 plugin aktif. |
| solo | Pengguna 1 Bot Mandiri | Menyalin seluruh 75 skill bundel ke 1 profil target pilihan (cocok untuk eksperimen atau pengguna yang hanya ingin 1 chat). |
| selective | Keperluan Spesifik (1-2 Bidang) | Memilih 1 atau beberapa dari 6 paket kategori (core, filmmaking, business, thesis, webdev, cybersec) + skill fondasi wajib. |
| custom-bots | Tim Kustom (2-4+ Bot Nama Sendiri) | Membentuk profil bot dengan nama, peran, dan daftar skill buatan pengguna sendiri (didukung oleh msshi forge). |

## Peran 5 Bot Hirarki & Alokasi Skill Aktual per Preset

| Bot & Gelar | Mandat Operasional | Interaksi | MuZA | Mhs | Dosen |
| --- | --- | --- | --- | --- | --- |
| 1. Yukino Yukinoshita (Idea Sparring & Daily) | Menampung ide mentah, curhat harian, pacing energi, jadwal, kesiapan meeting, & menyusun brief awal. | Tier 0 / Tipe 1 (Advisor) | 26 | 16 | 16 |
| 2. Sensei Shizuka Hiratsuka (Mastermind & Tutor) | Orkestrator strategi, guru belajar pemula (Chalk/LearnLoop/OSSU), konsultasi bisnis/pajak, & sintesis akhir. | Tipe 1 (Main + Advisor) | 30 | 17 | 18 |
| 3. Val (Deep Research & Prediksi) | Riset murni Nusantara & Global, literatur S1-S3, Skripsi .docx, OCR, data statistik, & prediksi TimesFM 2.5. | Tipe 2 (Dewan 2 Putaran) | 42 | 26 | 28 |
| 4. Kiki-Chii (One-Woman Creative Studio) | Concepting First, film/foto/video, Higgsfield 9 modul, Lemo-Opuscar 99 gaya, motion, slide, BRAG, opsional Studio. | Tipe 2 (Dewan 2 Putaran) | 26 | 17 | 17 |
| 5. Shikaku / Sir. Robot (Architect, Coder & Cybersec) | Arsitektur kode, TDD mattpocock, porting Rust (rust-anything), Grim Prompter, BugHunter berizin, opsional REA/KAT. | Tipe 2 (Dewan 2 Putaran) | 30 | 20 | 20 |

## Workspace Native Hermes, Bot Forge & Preservasi Instalasi Lama

- Profil Default Netral (--default-bot keep-hermes): Instalasi baru secara default menjaga profil root Hermes tetap netral sambil menata 5 profil spesialis di profiles/{yukino,shizuka,val,kiki-chii,shikaku}; seluruh 6 profil mendapat akses tool msshi_find_skill dan MSSHITrim.
- Tiga Keluaran Pertemuan Akademik (Academic Mahasiswa/Dosen): Setiap sesi bimbingan, kuliah, atau rapat diarahkan menghasilkan (1) Ringkasan keputusan & poin kunci, (2) Daftar tindak lanjut dengan tenggat & penanggung jawab, dan (3) Catatan standar Markdown siap simpan di workspace native Hermes tanpa memaksa aplikasi tambahan.
- Bot Forge (msshi forge): Menampilkan roster profil yang terpasang, status resource_profile/low_ram_mode, serta merancang profil baru (--apply) tanpa menyentuh konfigurasi model/API key atau file SOUL.md milik profil lain.
- Preservasi SOUL & Konfigurasi: Menjalankan ulang msshi setup atau msshi update membuat cadangan terpisah di <MSSHI_HOME>/backups/ dan tidak pernah menimpa provider, model, SOUL.md kustom, atau user_creative_dna.json.

# 4. Arsitektur Interaksi 2 Tipe, Pencari Skill 4-Lapis & MSSHITrim

Salah satu keunggulan terbesar MSSHI v3.1.2 adalah pemisahan tegas antara jabatan kerja (SOUL & protokol) dengan mesin model, sehingga pengguna mendapat kualitas kolaborasi multi-agen pada proyek besar sambil tetap hemat token pada percakapan sehari-hari.

*(Diagram vektor `interaction_two_types` disertakan penuh pada edisi PDF.)*

## Tier 0, Tipe 1 (Advisor) & Tipe 2 (Dewan MoA 2 Putaran + Audit Main)

- Tier 0 — Fast Main-Only (0 Agen Ekstra): Sapaan, curhat harian, pertanyaan singkat, klarifikasi cepat, dan cek status dijawab langsung oleh Main Agent tanpa membangunkan Advisor maupun Dewan. Menyebut kata 'riset' atau 'video' secara santai tidak otomatis memicu pipeline berat.
- Tipe 1 — Main Agent + Sub-Agent Advisor (Yukino & Sensei Shizuka): Main berkomunikasi dan menyusun rencana awal -> Advisor meninjau celah, risiko, dan alternatif -> Main memilih perbaikan terbaik dan memimpin eksekusi. Jalur Tipe 1 tidak memanggil Dewan MoA.
- Tipe 2 — Main Agent + Dewan MoA 2 Putaran + Audit Main Wajib (Val, Kiki-Chii & Shikaku): (1) Main menetapkan tujuan, batas, izin, dan kriteria verifikasi; (2) Putaran 1: Reference Agents mengoreksi & memperluas rencana, lalu Aggregator menyusun blueprint terpusat & menandai celah bukti; (3) Audit Main Wajib: Main memeriksa hasil Putaran 1 terhadap berkas/data nyata dan menulis catatan audit; (4) Putaran 2: Reference Agents & Aggregator merevisi blueprint berdasarkan catatan audit Main (maksimal 2 putaran — tidak ada putaran ke-3 otomatis); (5) Main memutuskan persetujuan akhir dan memimpin eksekusi.
- Pembaruan msshi-interaction v0.2.0: Kini memiliki bagian prompt terpisah (msshi.interaction-protocol, terpisah dari msshi-team-routing), pemulihan stale lock (recover_lock) agar kegagalan sesi tidak mengulang panggilan berbayar diam-diam, ringkasan job terisolasi per sesi (msshi_interaction_status) dengan retensi opt-in, serta dossier Dewan ringkas (goal, constraints, evidence_refs, delta_since_round_1, open_risks) yang memangkas pemborosan token.
- Pagar Mode Low-RAM: Bila resource-profile.json aktif pada mode light (RAM <= 6 GB), panggilan MoA/delegasi paralel otomatis diblokir (LIGHT_MODE_MOA_DISABLED) dan dialihkan ke jalur sekuensial satu inferensi agar laptop tidak freeze.

## Pencari Skill 4-Lapis Otomatis (msshi find & Tool Native msshi_find_skill)

*(Diagram vektor `finder_readiness` disertakan penuh pada edisi PDF.)*

Alih-alih menumpuk ratusan skill atau ribuan file referensi di satu bot (yang membuat context window bengkak dan lambat), MSSHI menyediakan mesin pencarian 4 lapis yang berjalan 100% lokal (0 panggilan LLM) baik melalui terminal (msshi find) maupun tool internal msshi_find_skill pada seluruh 6 profil Hermes:

| Lapis | Sumber yang Dipindai | Perilaku Hemat Token |
| --- | --- | --- |
| Lapis 1 | Skill aktif di profil bot yang sedang diajak bicara | Langsung memakai skill yang sudah terpasang di bot tersebut. |
| Lapis 2 | Bot spesialis lain (Yukino/Shizuka/Val/Kiki-Chii/Shikaku) | Memberi tahu bot pemilik spesialis yang tepat tanpa melanggar batas peran (mis. riset skripsi ke Val, porting Rust ke Shikaku). |
| Lapis 3 | Sumber & kurikulum terhubung (context-sources & OSSU) | Menemukan modul di grim-prompter, claude-bughunter, rust-anything, lemo-opuscar, rea-video, mattpocock, dan OSSU CS. |
| Lapis 4 | Brankas arsip skill impor lokal (msshi-private/archived-skill-imports/) | Mengindeks ratusan hingga ribuan skill arsip (lewati folder .bak) dan membaca tepat 1 file SKILL.md hanya ketika diminta (--open). |

## MSSHITrim, Caveman & TokenShield ($1.00)

- MSSHITrim (hermes_plugins/msshi-auto-trim): Bekerja lokal pada hook transform_tool_result. Hanya memadatkan output tool JSON valid berukuran >= 2048 karakter dengan penghematan tipikal 20%-55%, dan hanya menerima hasil bila kesetaraan JSON kanonik 100% terverifikasi (fail-open, 0 LLM calls, tanpa TLS proxy/CA/daemon). Dilengkapi antarmuka pengaturan Desktop (desktop_ui.js) di Settings > Plugins yang menyinkronkan pengaturan ke seluruh 6 profil.
- Caveman (msshi compact): Memadatkan handoff internal antar-bot dan log terstruktur secara lossless tanpa mengubah gaya bahasa alami ke pengguna akhir serta menjaga 100% sitasi, DOI, URL, angka, dan blok kode.
- TokenShield ($1.00 Zero-Waste Reserve): Memeriksa estimasi biaya terhadap saldo aktual sebelum langkah berbiaya tinggi dan menghentikan langkah berbiaya bila proyeksi saldo jatuh di bawah cadangan USD 1,00 (exit code 2).

# 5. Panduan Operasional 5 Misi Utama (Belajar, Riset, Kreasi, Coding & Harian)

Bab ini merangkum alur kerja nyata untuk kelima misi MSSHI v3.1.2, mencakup seluruh pembaruan besar terkini: Mode Belajar Pemula & OSSU, Riset Nusantara-Global + Skripsi v1.1 + TimesFM 2.5, Higgsfield 9 Modul + Lemo-Opuscar 99 Gaya + Imagination Studio, Rust-Anything + Grim Prompter + Claude-BugHunter, serta Spacewise, Sharewise, Dreaming, Harness2, dan OmniVoice.

## 5.1 Misi 1 — Belajar Pemula Total, Chalk, LearnLoop, CodeCoach & OSSU CS

- Belajar Tanpa /command (belajar-pemula): Pengguna cukup berkata alami ('Aku pemula, ajari statistika dari nol pelan-pelan'). Bot (Shizuka/Yukino) menanyakan 1 hal penentu level/energi, mengajarkan tepat 1 konsep per giliran (intuisi -> analogi -> contoh nyata -> istilah formal), memberi 1 latihan kecil, lalu menyimpulkan progres.
- Papan Tulis Visual Chalk (plugin native MIT): Bila pengguna meminta 'gambarkan cara kerjanya', Shizuka dapat memakai tool papan tulis visual Chalk atau diagram terstruktur.
- Latihan Adaptif LearnLoop (opt-in eksternal AGPL-3.0): Tidak divendor ke repo MIT; pengguna yang menginginkan latihan spaced-repetition/active recall dapat memasangnya secara eksplisit via msshi learn install.
- Latihan Coding Pemula (CodeCoach & Fallback Windows): CodeCoach upstream mensyaratkan Linux/WSL2 (modul resource + bubblewrap). Pada Windows native, MSSHI secara jujur dan otomatis mengarahkan latihan coding pemula ke tutor interaktif Shikaku tanpa memunculkan error sandbox.
- Universitas Computer Science Open-Source OSSU (msshi ossu): Dimodelkan sebagai kurikulum eksternal terhubung (63 mata kuliah ilmu komputer di https://cs.ossu.dev — bukan skill bot). Cek jalur belajar kapan saja tanpa kredit AI via msshi ossu fetch, msshi ossu roadmap, msshi ossu courses, dan msshi ossu open pemula.

## 5.2 Misi 2 — Riset Mendalam, Skripsi/Tesis/Disertasi & TimesFM 2.5 (Val + Shizuka)

- Pembatasan Ruang Lingkup (Val & Shizuka): Skill skripsi dan riset jurnal terkonsentrasi pada Val (pencarian bukti, metodologi, data, prediksi) dan Shizuka (strategi bimbingan, sintesis bahasa akademik, struktur argumen) agar profil lain tetap ramping.
- Riset Mendalam Nusantara & Global (khusus Val — riset-mendalam-nusantara-global): Memadukan 3 mode adaptif (Quick 1 putaran / Standard / Deep 10 tahap lengkap: Rencana -> Tesis -> Riset + Adequacy Gate -> Kerangka -> Draf -> Kritik Mandiri -> Devil's Advocate -> Audit Klaim -> Audit Sitasi/DOI -> Revisi skor mutu) dengan standar akademik Indonesia (Bab I-V, SINTA 1-6, Garuda, RAMA, EYD V) dan global (Scopus/WoS, PRISMA 2020, CONSORT/STROBE/COREQ, verifikasi DOI). Memuat hanya 1-2 file references/ per sesi agar hemat token.
- Lima Lapis Konteks + Backward Traceability + Unlimited-OCR-2: Membaca daftar isi/abstrak dulu sebelum mengekstrak halaman relevan, dan menautkan setiap angka/klaim kembali ke doc#halaman atau DOI. Dilarang mengarang DOI/sitasi; sumber belum terverifikasi wajib ditandai [PERLU VERIFIKASI SUMBER].
- MuZA Skripsi Starter v1.1 (Drag-and-Drop + Colab): Seret file ZIP hasil MuZA_Search.ipynb dan/atau PDF pedoman kampus ke MULAI_SKRIPSI_DRAG_AND_DROP.bat (atau jalankan msshi skripsi) untuk merakit template Word (.docx) sesuai margin, font, halaman depan, dan struktur bab kampus. Dilengkapi dua notebook resmi di notebooks/skripsi/ (MuZA_Search.ipynb & MuZA_Skripsi_Builder.ipynb).
- Prediksi Deret Waktu Offline (TimesFM 2.5 — msshi timesfm): Menggunakan bobot Apache-2.0 google/timesfm-2.5-200m-pytorch lokal CPU khusus Val (tersedia di semua preset). Wajib memisahkan chronological holdout, membandingkan terhadap baseline naive & seasonal-naive, serta melaporkan metrik error dan interval kuantil secara transparan. Syarat: >= 2,5 GiB commit RAM bebas saat eksekusi; unload otomatis setelah selesai.
- Ekstraksi HTML Lokal (Scrapling — msshi scrapling): Parser CSS/XPath lokal terisolasi untuk berkas HTML yang sudah diunduh; tidak menjalankan crawler jaringan otomatis.

## 5.3 Misi 3 — Konten Kreasi: Higgsfield 9 Modul, Lemo-Opuscar 99 Gaya & Studio (Kiki-Chii)

*(Diagram vektor `creative_pipeline` disertakan penuh pada edisi PDF.)*

- Aturan Wajib Concepting First: Kiki-Chii selalu mengunci Emosi (51%), Cerita (23%), Hook 0-3 detik, format, referensi berizin, dan review manusia antar-tahap sebelum menjalankan render berat atau langkah berbiaya.
- Higgsfield Unified Suite (9 Modul di bawah Kiki-Chii): Menyatukan (1) higgsfield-generate (cinema/video/foto/3D/audio multi-model + Marketing Studio + Virality Predictor), (2) higgsfield-soul-id (kunci konsistensi wajah/karakter dari 5-20 foto referensi), (3) higgsfield-product-photoshoot (10 mode foto produk komersial/editorial), (4) higgsfield-brandkit (logo SVG, palet, tipografi, mockup, brandbook), (5) higgsfield-marketplace-cards (foto utama & visual A+ e-commerce), (6) higgsfield-faceless-video (dokumenter/esai tanpa wajah), (7) higgsfield-video-explainer (blok 10 detik sinkron narasi), (8) higgsfield-youtube-thumbnail (thumbnail 4K & cover 9:16), dan (9) higgsfield-websites (kolaborasi Kiki-Chii x Shikaku untuk hero video loop & web interaktif). Catatan jujur: akun/kredit layanan Higgsfield dikelola terpisah oleh pengguna.
- Lemo-Opuscar (lemo-opuscar — 15 Kategori, 99 Gaya Film Berbasis Kode): Wajib mengikuti Section 0 sebelum menulis kode: Kiki-Chii terlebih dahulu menjelaskan ringkas 15 kategori gaya (Edit & Documentary, Painting, Sketch & Board, Traditional Crafts, Printmaking, Graphic & Type, Line Diagrams, Cartoons, Games, Film & Tape, Screens & Interfaces, Light & Lines, 3D & Miniature, Instruments & Evidence, Data & Maps), merekomendasikan 3-5 gaya terbaik sesuai brief, lalu menunggu konfirmasi pengguna sebelum memuat tepat 1 file STYLE.md on-demand dari cache terpin (0 aset media berat di folder skills/). Film hasil buatan pengguna 100% milik pengguna (termasuk komersial), sedangkan file dokumentasi upstream tetap mengikuti lisensi CC BY-NC 4.0 Lemomo.
- Motion Graphics, BRAG, Rea-Video, Unslop & Slide: Memadukan motion-graphics-suite (Remotion/Hyperframes), brag (video peluncuran produk berbasis Hyperframes via msshi brag), rea-video (bedah video referensi per shot ke VIDEO.md dengan --no-vlm ringan dulu), unslop (audit & polish UI), dan slide-generation.
- Add-on Opsional Imagination Studio (msshi studio, default publik OFF): Menghubungkan Kiki-Chii ke antrean render lokal Imagination Studio (http://127.0.0.1:7870, Apache-2.0) untuk Slate planning dan render gambar/klip/suara. Pada laptop 4-16 GB RAM, gunakan untuk Slate planning atau tetap memakai jalur ArtCraft/Motion-as-Code/Higgsfield.

## 5.4 Misi 4 — Coding, Porting Rust & Audit Keamanan Terotorisasi (Shikaku / Sir. Robot)

- Fondasi Engineering & TDD: Mulai dengan analyze-project (memetakan risiko & titik masuk), lanjutkan implementasi terisolasi via explore-code + mattpocock-engineering (TDD, debugging sistematis, spesifikasi ketat), dan uji regresi penuh.
- Porting Terverifikasi ke Rust (rust-anything): Memigrasikan fungsi panas atau seluruh aplikasi dari TypeScript/JS, Python, C, Go, Ruby, atau Java ke Rust secara bertahap unit-per-unit: profile -> plan -> bridge -> record ground truth -> port -> diff -> bench -> shadow -> gate (unit selesai hanya jika differential verification & gate lulus). Cache panduan terpin diambil via msshi integrations source --name rust-anything --fetch; toolchain rustc/cargo & CLI/MCP rust-anything dipasang terpisah oleh pengguna.
- Pemodelan Ancaman Read-Only (grim-prompter): Pustaka 36 arsitektur (quick & deep), 29 metode (STRIDE, PASTA, LINDDUN, Attack Trees, STPA-Sec, DREAD), dan analisis privasi (GDPR/CCPA) yang bekerja 100% read-only terhadap kode sumber proyek untuk menghasilkan laporan bukti di folder threat-model/.
- Audit Kerentanan Terotorisasi (claude-bughunter, pin 8258d297): Pustaka 83 skill keamanan, 15 panduan command, 681 pola, dan 433 laporan terungkap bersitasi terverifikasi (36 berkas pustaka pola) di cache terpin. WAJIB melewati Gerbang Otorisasi: hanya untuk aset milik sendiri, program bug bounty in-scope tertulis, atau lab/CTF berizin. Tidak pernah memasang scanner/MCP otomatis.
- Add-on Opsional REA (msshi rea, default OFF) & KAT-Coder (msshi coder, default OFF): REA menyediakan analisis statis reverse engineering JavaScript/arsip/native secara terisolasi. KAT-Coder membuka wizard endpoint/key privat opsional khusus Shikaku tanpa mengubah model utama.
- Master Prompt Handoff untuk Antigravity: Bila implementasi besar dilanjutkan di Antigravity, Shikaku menghasilkan paket handoff terstruktur (tujuan, blueprint, status verifikasi sumber, kontrak file/API, tes, batas izin, dan rollback) tanpa membocorkan kredensial atau path privat.

## 5.5 Misi 5 — Curhat Harian, Utilitas Lokal (Spacewise/Sharewise), Dreaming, Harness2 & OmniVoice

- Daily Chat & Energi (Yukino Main-Only): Obrolan hangat empatik tanpa memanggil bot lain (0 overhead token ekstra), mengatur jadwal/to-do sesuai energi lewat focus-my-energy & parenting-6d-gad-mdd (bukan pengganti layanan klinis profesional).
- Spacewise (Plugin & Skill MIT — Semua Bot): Pemindaian penyimpanan lokal 100% offline pada tepat 1 folder yang disebutkan pengguna menjadi 3 tier: Green (duplikat persis & installer sisa), Amber (foto mirip/buram — tinjau visual dulu), dan Grey (video/file besar — hanya dilaporkan). Kejujuran platform: di macOS/Linux mendukung scan, preview, trash, & undo; di Windows mendukung scan & preview pada subfolder home pengguna (pemindahan ke Recycle Bin & drive non-home dibatasi oleh guard.py upstream).
- Sharewise (Plugin & Skill MIT — Semua Bot): Pemeriksaan privasi foto & video lokal sebelum dibagikan di bawah Wall T1 (hanya melaporkan hitungan ya/tidak untuk GPS, waktu, perangkat, thumbnail, riwayat edit — tanpa membocorkan koordinat/data asli ke LLM), membuat halaman review HTML lokal untuk menandai area sensor, lalu membangun salinan bersih tanpa menyentuh file asli.
- Hermes-Dreaming (msshi dream): Refleksi sesi lokal deterministik yang menulis proposal pelajaran ke memories/DREAMS.md (0 panggilan LLM, tidak auto-terjadwal). Promosi ke MEMORY.md selalu menunggu keputusan manusia.
- Harness2 (msshi harness2 — Tersedia di Semua 5 Bot): Kerangka Google Research Propose-Probe-Compose untuk memperbaiki prompt/skill/script pada salinan terisolasi memakai baseline vs holdout; diaudit Val (bukti), Shikaku (diff), dan Shizuka (sintesis) sebelum persetujuan manusia.
- OmniVoice (msshi voice — TTS CPU Offline, CC-BY-NC): Prosodi suara lokal per persona bot dengan auto_start: false dan unload otomatis setelah sintesis (tidak pernah berbunyi otomatis di setiap chat). Periksa ketentuan lisensi CC-BY-NC sebelum penggunaan komersial.

# 6. Integrasi Aplikasi (CLI-Anything), Browser Manual & Keamanan

Pada arsitektur MSSHI v3.x, 22 server MCP lokal yang dulu memakan RAM besar pada laptop diputus total dan digantikan oleh CLI-Anything Universal Bridge. Aplikasi desktop seperti Blender, FFmpeg, maupun rangkaian ArtCraft (13 modul Kiki-Chii, 4 modul Val, 2 modul Shikaku, dengan figcraft berbagi khusus Kiki-Chii & Shikaku) hanya dijalankan sesuai tiket tugas on-demand (msshi runtime ticket & msshi runtime run) dengan auto_open_on_boot: false.

## Kebijakan Browser Manual, Layanan Eksternal & Keamanan

- Browser Lokal Manual (msshi browser): Hanya menyimpan preferensi browser utama (Chrome/Edge/Firefox) dan label akun agar bot tahu browser mana yang Anda gunakan. Tidak pernah menyalin cookie, password, profil sesi, atau memaksa login otomatis.
- Layanan Web & MCP Eksternal (msshi services): Koneksi seperti GitLab, Tinyfish, atau layanan API lainnya disambungkan sendiri oleh pengguna di host Hermes. BrightData dan GDrive pada setup publik terkunci OFF secara default; plugin msshi-steel-policy berstatus retired.
- Otorisasi Tiket Tugas: Setiap eksekusi alat melalui CLI-Anything menggunakan tiket tugas terbatas ruang lingkup dan anggaran; registrasi rute di msshi connect --status bukanlah pembukaan aplikasi otomatis.

## Katalog Lengkap 47 Target Aplikasi & Rute CLI-Anything

| ID Target Aplikasi / Rute | Fungsi & Batas Operasional (Sumber: connection_help.json) |
| --- | --- |
| anicraft | Animasi 2D/layer/shape dan render headless melalui AniCraft; khusus Kiki-Chii pada preset MuZA, perlu aplikasi CLI yang terpasang. |
| antigravity | Gunakan IDE Antigravity untuk workspace coding yang dipilih; IDE harus terpasang dan baru dibuka saat ada tugas. |
| artcraft | Daftarkan kelompok 15 aplikasi kreatif ArtCraft untuk video, gambar, audio, desain, dokumen, dan 3D; aplikasi/runtime dipasang terpisah. |
| audacity | Edit dan olah audio lewat harness Audacity; perlu Audacity dan harness CLI-Anything. |
| blender | Pengerjaan scene, model, animasi, dan render 3D di Blender melalui rute yang terdaftar; perlu Blender dan adapter yang sesuai. |
| blender-cli | Kendalikan Blender lewat harness CLI-Anything untuk tugas 3D/render; perlu Blender dan executable cli-anything-blender. |
| cadcraft | Pengerjaan gambar dan rancangan CAD di CADCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| cli-hub | Cari dan kelola harness CLI-Anything; menampilkan katalog tidak memasang atau menjalankan harness/aplikasi lain. |
| craftanything | Pengerjaan proyek kreatif melalui Craft Anything; fungsi yang dapat dipanggil bergantung aplikasi/adapter terpasang. |
| deckcraft | Pengerjaan slide dan presentasi di DeckCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| designcraft | Pengerjaan desain visual dan layout di DesignCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| drawio | Buat dan edit diagram alur atau arsitektur melalui harness draw.io; perlu aplikasi dan harness yang sesuai. |
| effectcraft | Pengerjaan efek visual dan motion di EffectCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| existing | Daftarkan ulang konektor Hermes yang sudah aktif pada profil ini; login dan keberhasilan operasi tetap perlu diperiksa terpisah. |
| ffmpeg | Konversi, potong, gabungkan, atau periksa media audio/video lewat CLI lokal; perlu executable FFmpeg. |
| figcraft | Pengerjaan desain antarmuka dan layout di FigCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| filmcraft | Pengerjaan video dan timeline editing di FilmCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| gdrive-web | Akses file Google Drive melalui web ketika tugas memerlukannya; perlu login dan izin akun, mengikuti kebijakan browser aktif. |
| gimp | Tidak diaktifkan pada kebijakan preset MuZA; gunakan aplikasi ArtCraft yang sesuai peran. |
| git | Kelola versi source code dan riwayat perubahan lewat Git; push atau penulisan remote tetap memerlukan izin tugas dan akses akun. |
| gitlab | Akses proyek dan data GitLab melalui adapter yang terdaftar; perlu autentikasi serta izin proyek yang sesuai. |
| graphify | Petakan hubungan file/kode menjadi graf proyek melalui Graphify lokal; perlu runtime serta input proyek yang dipilih. |
| gridcraft | Pengerjaan tabel dan spreadsheet di GridCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| hersona | Kelola personalisasi/persona melalui Hersona CLI; memilih rute tidak mengubah persona atau konfigurasi model. |
| inkscape | Buat dan edit grafis vektor/SVG melalui harness Inkscape; perlu Inkscape dan harness CLI-Anything. |
| kdenlive | Susun dan edit timeline video melalui harness Kdenlive; perlu Kdenlive dan harness CLI-Anything. |
| krita | Ilustrasi dan lukisan digital melalui harness Krita; perlu Krita dan harness CLI-Anything. |
| libreoffice | Tidak diaktifkan pada kebijakan preset MuZA; gunakan aplikasi ArtCraft yang sesuai peran. |
| lightcraft | Kelola dan kembangkan foto, warna, serta hasil ekspor di LightCraft; perlu aplikasi/adapter dan library foto yang dapat dipakai. |
| llmtrim | Padatkan payload yang memenuhi syarat melalui llmtrim CLI; manfaat bergantung input dan tidak menjamin penghematan seluruh tagihan token. |
| materialcraft | Pengerjaan material untuk proyek visual/3D di MaterialCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| mcp:gitlab | Akses proyek, issue, dan data GitLab melalui konektor MCP yang terdaftar; autentikasi dan izin proyek diperiksa terpisah, registrasi bukan bukti operasi berhasil. |
| mcp:tinyfish | Gunakan layanan otomasi/pencarian web Tinyfish melalui MCP untuk tugas yang diizinkan; perlu login serta izin kuota/biaya, registrasi bukan bukti koneksi berhasil. |
| node | Jalankan tool/proyek JavaScript dengan Node.js lokal; memilih rute tidak memasang paket atau menjalankan proyek. |
| obs | Atur scene dan rekaman/streaming OBS melalui harness; mulai merekam atau siaran tetap merupakan tindakan tugas terpisah. |
| pdfcraft | Pengerjaan dokumen PDF di PDFCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| perplexity | Riset dan pencarian melalui Perplexity; akses web/aplikasi serta batas akun diperiksa saat dipakai, tanpa membuka aplikasi sekarang. |
| photocraft | Pengerjaan dan penyuntingan foto di PhotoCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| python | Jalankan tool/proyek Python lokal; memilih rute tidak memasang dependency atau menjalankan kode. |
| solidcraft | Pengerjaan model solid dan rancangan 3D di SolidCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| soundcraft | Pengerjaan audio, penyuntingan, dan mixing di SoundCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| texturecraft | Pengerjaan tekstur untuk proyek visual/3D di TextureCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| tiktok | Riset konten TikTok melalui web/aplikasi; login, izin akun, dan kebijakan browser tetap berlaku. |
| vectorcraft | Pengerjaan ilustrasi dan grafis vektor di VectorCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| whatsapp-web | Akses WhatsApp Web saat tugas memerlukannya; perlu sesi akun dan izin terikat tugas, pengiriman pesan memerlukan otorisasi. |
| wordcraft | Pengerjaan dokumen teks dan pemformatan di WordCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| youtube-chrome | Akses YouTube untuk riset video melalui rute yang tersedia; browser personal memerlukan izin sesuai tugas dan kebijakan aktif. |

# 7. Operasional Harian, Pembaruan Terkelola, Diagnostik & Troubleshooting

Seluruh perawatan harian MSSHI dapat dijalankan secara lokal tanpa menghabiskan kredit AI. Gunakan perintah pemeriksaan sebelum mengubah konfigurasi agar setiap perbaikan tepat sasaran dan dapat di-rollback.

## Perintah Operasional & Perawatan Rutin (0 Kredit AI)

```text
# 1. Cek kesehatan menyeluruh (RAM, Drive C:/D:/E:, paritas 75 skill, low_ram_diagnostics):
msshi doctor
msshi doctor --json

# 2. Perbaikan aman berkas milik MSSHI (tidak pernah mengubah SOUL.md / config.yaml / .env):
msshi doctor --fix

# 3. Cek update rilis GitHub & cek update 64 upstream tanpa auto-apply:
msshi check
msshi upstreams check

# 4. Perbarui MSSHI ke rilis terbaru (otomatis membuat backup SOUL & Creative DNA):
msshi update
msshi update --skip-upstreams       # update kode/skill saja tanpa tarik 64 upstream
msshi update --light                # update mode hemat tanpa aset berat/PDF otomatis

# 5. Audit sistem 4 pilar, rute hemat token, dan pencarian skill 4 lapis:
msshi system status --json
msshi system route --task "Tulis kebutuhan Anda di sini"
msshi find "skripsi"

# 6. Pemulihan layar abu-abu (Grey Screen) Hermes Desktop atau pindah ke CLI ringan:
msshi desktop --software-rendering
msshi desktop --prefer-cli
```

## Tabel Troubleshooting Lengkap (10 Kendala Nyata & Solusi Terverifikasi)

| Kendala / Gejala | Penyebab Umum | Solusi Cepat & Aman |
| --- | --- | --- |
| Hermes Desktop terus minta restart gateway / Errno 13 Permission denied pada config.yaml | Perintah msshi (mis. voice --enable / setup) sempat dijalankan di PowerShell Run as Administrator sehingga pemilik file berubah ke Administrators. | Tutup Hermes Desktop, buka PowerShell Admin sekali untuk mengembalikan kepemilikan ke user biasa: takeown /F "<HERMES_HOME>\profiles" /R /D Y lalu icacls "<HERMES_HOME>\profiles" /grant "%USERNAME%:(OI)(CI)F" /T /C. Selanjutnya selalu jalankan msshi di PowerShell biasa. |
| Error disk full / os error 1455 (paging file too small) saat install atau uji OmniVoice/TimesFM | Drive C: hampir penuh (< 2-5 GB bebas) sehingga %TEMP% dan Windows pagefile.sys kehabisan ruang saat memuat bobot model. | Kosongkan 3-5 GB di Drive C:, set $env:TEMP='D:\HermesData\temp'; $env:TMP='D:\HermesData\temp', dan aktifkan Windows Virtual Memory (System managed size) di Drive D:/E:. |
| Layar Hermes Desktop abu-abu (Grey Screen) meski gateway berjalan | Konflik akselerasi GPU/Chromium pada driver grafis Windows. | Tutup Hermes Desktop sepenuhnya lalu jalankan msshi desktop --software-rendering. |
| Laptop Windows 10 RAM 4-6 GB terasa lambat / lag berat | Menjalankan Hermes Desktop Electron + banyak tab + mode paralel MoA bersamaan. | Aktifkan Mode Hemat: msshi light mode --set light --apply, lalu gunakan Hermes CLI (msshi desktop --prefer-cli). |
| msshi doctor melaporkan NEEDS_ATTENTION pada Advisor/Dewan | Model untuk Advisor (Yukino/Shizuka) atau Dewan (Val/Kiki-Chii/Shikaku) belum diatur di Settings Hermes (wajar pada instalasi baru). | Atur sendiri provider/model Advisor/Dewan di Settings Hermes sesuai kebutuhan, atau gunakan mode Main-only jika hanya memakai 1 model. |
| Plugin msshi_find_skill atau MSSHITrim belum muncul di chat Hermes | Masih menggunakan sesi chat lama yang dibuat sebelum instalasi/update plugin. | Restart gateway Hermes bila perlu, tutup sesi lama, lalu buka New Chat agar schema plugin baru termuat. |
| CodeCoach tidak aktif di Windows native | CodeCoach upstream mensyaratkan Linux/WSL2 (modul resource & bubblewrap/bwrap). | Gunakan fallback resmi Shikaku di Windows native (otomatis diarahkan oleh belajar-pemula), atau jalankan Hermes di WSL2/Linux. |
| Spacewise / Sharewise menolak folder di Drive D: di Windows | Batasan keamanan guard.py upstream yang mengunci pemindaian pada subfolder home pengguna (C:\Users\<User>\...). | Salin sementara folder yang ingin diperiksa ke subfolder di dalam direktori home pengguna, jalankan pemeriksaan, lalu pindahkan salinan bersihnya. |
| Katalog lemo-opuscar / rust-anything / claude-bughunter / grim-prompter belum terisi | Cache context-sources sengaja kosong di awal (0 MB) agar instalasi tetap ramping. | Tarik hanya sumber yang sedang dibutuhkan: msshi integrations source --name <nama> --fetch. |
| Mismatch baseline preservasi setelah user sengaja mengganti model/provider | Pengguna memodifikasi config.yaml sendiri sesudah baseline dicatat. | Tinjau pratinjau via msshi runtime rebaseline --home <HERMES_HOME>, lalu terapkan eksplisit dengan --apply --expected-snapshot <SHA> --accept-current-llm-settings --reason "alasan". |

# 8. Praktikum Terpandu: 5 Skenario Latihan End-to-End

Kerjakan salah satu praktikum di bawah ini untuk membuktikan instalasi Anda berfungsi dari terminal (0 kredit AI) hingga percakapan nyata di Hermes. Ganti <HERMES_HOME> dengan folder data Hermes Anda (mis. D:\HermesData atau ~/.hermes).

## Praktikum 1 — Verifikasi Sistem & Belajar Pemula + OSSU (0 Kredit -> Chat Shizuka)

```text
# Langkah 1 (Terminal, 0 kredit AI): cek kesehatan, status belajar, dan peta OSSU
msshi doctor
msshi learn status
msshi learn start "statistika dasar dari nol"
msshi ossu fetch
msshi ossu roadmap
# Langkah 2 (New Chat di Shizuka):
# Ketik: "Aku pemula total, ajari dasar statistika dari nol pelan-pelan, 1 konsep dulu dan beri 1 latihan kecil." 
```

## Praktikum 2 — Riset Terverifikasi, Template Skripsi v1.1 & TimesFM 2.5 (Val)

```text
# Langkah 1 (Terminal, 0 kredit AI): uji rute sistem & pencari skill untuk skripsi
msshi system route --task "Petakan research gap dan buat template skripsi .docx sesuai pedoman kampus"
msshi find "skripsi"
msshi timesfm status
# Langkah 2 (Drag-and-Drop): seret PDF pedoman kampus + ZIP MuZA_Search ke MULAI_SKRIPSI_DRAG_AND_DROP.bat
# Langkah 3 (New Chat di Val):
# Ketik: "Bantu susun rumusan masalah & peta literatur standar SINTA/Scopus untuk topik [X] dengan sitasi DOI terverifikasi." 
```

## Praktikum 3 — Konten Kreasi dengan Lemo-Opuscar 99 Gaya & Higgsfield (Kiki-Chii)

```text
# Langkah 1 (Terminal, 0 kredit AI): tarik katalog ringan lemo-opuscar (0 aset berat) & cek status
msshi integrations source --name lemo-opuscar --fetch
msshi integrations source --name lemo-opuscar --list
msshi brag doctor
# Langkah 2 (New Chat di Kiki-Chii):
# Ketik: "Saya mau membuat video explainer 45 detik berbasis kode memakai lemo-opuscar untuk produk [X]. Jelaskan dulu pilihan kategorinya dan rekomendasikan 3-5 gaya terbaik sebelum menulis kode." 
```

## Praktikum 4 — Porting Rust & Audit Keamanan Read-Only (Shikaku / Sir. Robot)

```text
# Langkah 1 (Terminal, 0 kredit AI): tarik cache panduan terpin khusus Shikaku
msshi integrations source --name rust-anything --fetch
msshi integrations source --name grim-prompter --fetch
msshi integrations source --name claude-bughunter --fetch
# Langkah 2 (New Chat di Shikaku):
# Ketik: "Lakukan threat modeling STRIDE secara read-only pada repositori API lokal milik saya ini dulu, lalu susun rencana porting modul parser hot-path ke Rust memakai alur rust-anything." 
```

## Praktikum 5 — Refleksi Offline Dreaming, Harness2 & Cek Hemat Token

```text
# Langkah 1 (Terminal, 0 kredit AI): cek statistik MSSHITrim, jalankan Dreaming offline & demo Harness2
msshi trim --status --profile default
msshi dream --run-now
msshi harness2 status
msshi harness2 demo
msshi system status --json
```

# 9. Referensi Lengkap 39 Keluarga Command CLI (109 Node Aktif)

Seluruh daftar perintah, subperintah, dan opsi pada bab ini diekstrak langsung dari parser argparse aktual pada scripts/msshi_cli.py dan modul-modul helper-nya pada commit f400fba (39 keluarga perintah utama + 70 subperintah bersarang = 109 node CLI). Semua perintah CLI di bawah berjalan dengan 0 kredit model AI.

## Peta Ringkas 39 Keluarga Command CLI MSSHI v3.1.2

| Perintah | Subperintah | Efek Utama | Fungsi Ringkas |
| --- | --- | --- | --- |
| 1. msshi check | (langsung) | Read-only (jaringan GitHub) | Bandingkan versi lokal dengan GitHub main, tampilkan changelog dan ringkasan koneksi. |
| 2. msshi connect | (langsung) | Baca/tulis registri lokal | Kelola pemetaan aplikasi CLI-Anything per profil bot (auto-reconnect, select, status). |
| 3. msshi update | (langsung) | Tulis lokal + jaringan GitHub | Perbarui rilis MSSHI, skill terkelola, profil, serta cache upstream (dukung --light & --skip-upstreams). |
| 4. msshi runtime | migrate, status, hardware, guardian-install, rebaseline, ticket, run, guardian, scan, rollback | Audit/tiket/eksekusi alat | Migrasi profil v3, deteksi hardware, tiket tugas, eksekusi CLI-Anything, rebaseline & rollback. |
| 5. msshi integrations | install, dream, voice, kat, source | Baca/tulis cache & runtime | Kelola integrasi opsional (dream, voice, kat) dan cache sumber kontekstual terpin (--name ... --fetch). |
| 6. msshi desktop | (langsung) | Status/peluncur GUI atau CLI | Cek status Hermes Desktop, pemulihan Grey Screen (--software-rendering), atau fallback CLI (--prefer-cli). |
| 7. msshi audit | (langsung) | Read-only (tulis --output opsional) | Jalankan auditor v3.1 (check_release_v31) terhadap paket, profil, dan bukti tanpa panggilan model. |
| 8. msshi doctor | (langsung) | Read-only (atau --fix terarah) | Diagnosis lengkap: RAM, Drive C:/D:/E:, paritas 75 skill, low_ram_diagnostics, dan perbaikan aman --fix. |
| 9. msshi light | status, mode, index, build, benchmark, cli-fallback | Read-only / profil Low-RAM | Light Build Windows 10 RAM 4 GB: status, aktivasi Low-RAM atomik, indeks lazy, build ZIP <=50 MB, benchmark. |
| 10. msshi system | status, route, cycle | 100% lokal & deterministik | Sistem Interaksi Cerdas 4 Pilar: audit 0-orphan (status), rute hemat token (route), dan siklus riset/belajar (cycle). |
| 11. msshi find | (langsung) | 100% lokal (indeks/cari) | Pencari skill 4 lapis (bot aktif, spesialis lain, sumber terhubung, arsip lokal) dengan baca 1 SKILL.md on-demand. |
| 12. msshi ossu | status, fetch, roadmap, guides, courses, open | Lokal / --fetch GitHub OSSU | Koneksi Universitas Computer Science Open-Source OSSU (63 mata kuliah, roadmap, guides, courses, open). |
| 13. msshi learn | status, start, install | Lokal / pasang plugin belajar | Mode belajar pemula total tanpa /command: cek status plugin belajar, rekomendasi topik, pasang Chalk/LearnLoop/CodeCoach. |
| 14. msshi upstreams | check, integrity, install-ponytail | Read-only jaringan / audit | Cek pembaruan 64 upstream GitHub tanpa auto-apply (check), audit Caveman/Ponytail, & pasang Ponytail opsional. |
| 15. msshi skripsi | (langsung) | Tulis .docx ke folder output | Rakit template Word (.docx) skripsi/tugas akhir drag-and-drop dari PDF pedoman kampus & ZIP MuZA_Search v1.1. |
| 16. msshi assets | (langsung) | Read-only (cari bahan lokal) | Cari bahan persona pribadi di direktori lokal pilihan pengguna secara read-only. |
| 17. msshi compact | (langsung) | Lokal (padatkan JSON/teks) | Padatkan data/handoff internal via Caveman filter tanpa merusak sitasi, angka, atau blok kode. |
| 18. msshi browser | (langsung) | Tulis preferensi lokal | Simpan pilihan browser (Chrome/Edge/Firefox) dan label akun untuk login manual; tanpa salin cookie. |
| 19. msshi trim | (langsung) | Lokal (MSSHITrim JSON) | Cek statistik MSSHITrim per profil atau padatkan file JSON secara lossless (kesetaraan kanonik 100%). |
| 20. msshi interaction | (langsung) | Lokal (status/install plugin) | Kelola plugin msshi-interaction v0.2.0: status Tier 0/1/2, protokol terpisah, recover_lock, & ringkasan job. |
| 21. msshi forge | (langsung) | Read-only / --apply profil baru | Tinjau roster bot dan rancang profil bot baru secara aman tanpa menyentuh provider/model. |
| 22. msshi managed | (langsung) | Lokal (kelola skill terkelola) | Periksa & segarkan salinan skill yang cocok dengan fingerprint terkelola tanpa menimpa edit kustom. |
| 23. msshi services | (langsung) | Lokal (kompatibilitas MCP) | Kompatibilitas status layanan eksternal; koneksi akun/MCP tetap diatur sendiri oleh pengguna. |
| 24. msshi timesfm | status, install, smoke, forecast | Lokal CPU (unduh saat install) | Peramalan deret waktu CPU offline TimesFM 2.5 (Apache-2.0): status, install, smoke, forecast dengan holdout. |
| 25. msshi brag | doctor, init, renderer, check, render | Lokal (Hyperframes render) | Alur video peluncuran produk berbasis Hyperframes (doctor, init, renderer, check, render) dengan Concepting First. |
| 26. msshi scrapling | status, install, selftest, parse | Lokal HTML (tanpa crawler) | Parser CSS/XPath lokal terisolasi untuk berkas HTML lokal (status, install, selftest, parse). |
| 27. msshi harness2 | status, install, demo, plan | Lokal terisolasi | Evaluasi harness Google Research Propose-Probe-Compose (status, install, demo deterministik, plan). |
| 28. msshi optional | list, enable | Read-only / enable opt-in | Lihat dan aktifkan skill opsional publik default OFF (rea untuk Shikaku, imagination-studio untuk Kiki-Chii). |
| 29. msshi rea | status, install, selftest, javascript, inspect, native | Lokal statis (opsional Coder) | Analisis reverse engineering statis JavaScript/arsip/native khusus Shikaku (status, install, selftest, javascript, inspect, native). |
| 30. msshi studio | status, plan | Lokal / probe 127.0.0.1:7870 | Status dan rencana Slate kolaborasi opsional Imagination Studio untuk Kiki-Chii (status, plan). |
| 31. msshi choices | (langsung) | 100% read-only lokal | Baca fungsi dan prasyarat seluruh 136 skill, 6 paket, 6 mode, 43 fitur, dan 47 aplikasi tanpa memasang apa pun. |
| 32. msshi manual | list, download | Lokal / unduh PDF GitHub | Daftar katalog PDF resmi (list) dan unduh manual versi pilihan dengan verifikasi SHA-256 (download). |
| 33. msshi dream | (langsung) | Lokal offline (tulis DREAMS.md) | Susun proposal refleksi pelajaran lokal ke memories/DREAMS.md; promosi ke MEMORY.md selalu menunggu manusia. |
| 34. msshi voice | (langsung) | Lokal CPU (unduh saat install) | Status, pasang runtime, dan aktifkan TTS offline OmniVoice per profil (auto_start: false, unload otomatis). |
| 35. msshi kat | (langsung) | Tulis konfigurasi privat Coder | Pintasan wizard endpoint/key opsional KAT-Coder khusus Shikaku (tidak mengubah model utama). |
| 36. msshi coder | status, presets, wizard, disable, configure | Tulis konfigurasi privat Coder | Kelola konfigurasi opsional KAT-Coder khusus Shikaku (status, presets, wizard, disable, configure). |
| 37. msshi setup | (langsung) | Wizard setup 4+1 tahap | Pasang dan konfigurasi 6 mode (Academic Mahasiswa/Dosen, MuZA, Solo, Custom, Selective) + Low-RAM + 4+1 tahap. |
| 38. msshi select | (langsung) | Tulis skill/paket pilihan | Tambah skill atau paket tertentu ke profil/direktori pilihan dengan pratinjau rencana terlebih dahulu. |
| 39. msshi bootstrap | (langsung) | Pasang launcher global PATH | Pasang launcher perintah global msshi dari rilis lokal (mendukung --light dan --no-path). |

## Rincian Sintaks, Subperintah & Opsi per Keluarga Command

### 9.1  msshi check — Read-only (jaringan GitHub) (0 LLM)

Bandingkan versi lokal dengan GitHub main, tampilkan changelog dan ringkasan koneksi.

```text
Sintaks: msshi check [-h] [--hermes-home HERMES_HOME] [--profile PROFILE] [--state-dir STATE_DIR]
```

- --hermes-home HERMES_HOME — Folder Hermes untuk pemeriksaan koneksi.
- --profile PROFILE — Profil Hermes untuk pemeriksaan koneksi.
- --state-dir STATE_DIR — Folder penyimpanan koneksi yang akan diperiksa.

### 9.2  msshi connect — Baca/tulis registri lokal (0 LLM)

Kelola pemetaan aplikasi CLI-Anything per profil bot (auto-reconnect, select, status).

```text
Sintaks: msshi connect [-h] [--hermes-home HERMES_HOME] [--profile PROFILE] [--state-dir STATE_DIR] [--json] [--dry-run] [--targets TARGETS] [--query QUERY] [--ticket TICKET] [--mode {auto-reconnect,select} | --catalog | --status | --add TARGET | --remove TARGET | --open TARGET | --run TARGET]
```

- --hermes-home HERMES_HOME — Folder Hermes atau profil aktif.
- --profile PROFILE — Nama profil Hermes, atau default.
- --state-dir STATE_DIR — Folder alternatif registri per profil.
- --json — Tampilkan hasil dalam JSON.
- --dry-run — Pratinjau perubahan tanpa menulis registri.
- --targets TARGETS — ID target dipisah koma untuk --mode select.
- --query QUERY — Kueri web atau path workspace Antigravity saat --open.
- --ticket TICKET — One-use task ticket from msshi runtime ticket.
- --mode {auto-reconnect,select} — Pilih mode koneksi.
- --catalog — Lihat pilihan target yang dikenal.

### 9.3  msshi update — Tulis lokal + jaringan GitHub (0 LLM)

Perbarui rilis MSSHI, skill terkelola, profil, serta cache upstream (dukung --light & --skip-upstreams).

```text
Sintaks: msshi update [-h] [--skip-upstreams] [--light] [--hermes-home HERMES_HOME] [--source SOURCE] [--download-pdf] [--no-pdf] [--pdf-version PDF_VERSION] [--pdf-dest PDF_DEST]
```

- --skip-upstreams — Hanya perbarui MSSHI dan skill bundel.
- --light — Stage Light Build ringan (<= 50 MB) tanpa aset berat, PDF otomatis, dan upstream cache.
- --hermes-home HERMES_HOME — Folder Hermes untuk migrasi v3.
- --source SOURCE — Pakai kandidat lokal yang sudah diperiksa.
- --download-pdf — Unduh Buku Panduan PDF lengkap untuk versi ini.
- --no-pdf — Lewati penyalinan otomatis panduan PDF.
- --pdf-version PDF_VERSION — Versi PDF panduan yang diunduh (latest, v3.1.0, v3.0).
- --pdf-dest PDF_DEST — Folder tujuan simpan PDF panduan.

### 9.4  msshi runtime — Audit/tiket/eksekusi alat (0 LLM)

Migrasi profil v3, deteksi hardware, tiket tugas, eksekusi CLI-Anything, rebaseline & rollback.

```text
Sintaks: msshi runtime [-h] [--home HOME] {migrate,status,hardware,guardian-install,rebaseline,ticket,run,guardian,scan,rollback} ...
```

- --home HOME — Hermes data root

| Subperintah | Fungsi / Deskripsi Resmi | Opsi & Argumen Utama |
| --- | --- | --- |
| msshi runtime migrate | msshi runtime migrate [-h] [--home SUB_HOME] [--json] | --home SUB_HOME; --json |
| msshi runtime status | msshi runtime status [-h] [--home SUB_HOME] [--json] | --home SUB_HOME; --json |
| msshi runtime hardware | msshi runtime hardware [-h] [--home SUB_HOME] [--json] | --home SUB_HOME; --json |
| msshi runtime guardian-install | msshi runtime guardian-install [-h] [--home SUB_HOME] [--json] | --home SUB_HOME; --json |
| msshi runtime rebaseline | Preview or accept a stable current config/SOUL baseline without changing their values | --home SUB_HOME; --apply; --expected-snapshot EXPECTED_SNAPSHOT; --accept-current-llm-settings; --reason REASON |
| msshi runtime ticket | msshi runtime ticket [-h] [--home SUB_HOME] [--profile PROFILE] --target TARGET --task TASK [--source {direct,context}] [--ttl TTL] | --home SUB_HOME; --profile PROFILE; --target TARGET; --task TASK; --source {direct,context}; --ttl TTL |
| msshi runtime run | msshi runtime run [-h] [--home SUB_HOME] [--profile PROFILE] --ticket TICKET [--timeout TIMEOUT] target ... | --home SUB_HOME; --profile PROFILE; --ticket TICKET; --timeout TIMEOUT; target; arguments |
| msshi runtime guardian | msshi runtime guardian [-h] [--home SUB_HOME] [--once] [--interval INTERVAL] [--scan-root SCAN_ROOT] | --home SUB_HOME; --once; --interval INTERVAL; --scan-root SCAN_ROOT |
| msshi runtime scan | msshi runtime scan [-h] [--home SUB_HOME] path | path; --home SUB_HOME |
| msshi runtime rollback | msshi runtime rollback [-h] [--home SUB_HOME] receipt | receipt; --home SUB_HOME |

### 9.5  msshi integrations — Baca/tulis cache & runtime (0 LLM)

Kelola integrasi opsional (dream, voice, kat) dan cache sumber kontekstual terpin (--name ... --fetch).

```text
Sintaks: msshi integrations [-h] {install,dream,voice,kat,source} ...
```

| Subperintah | Fungsi / Deskripsi Resmi | Opsi & Argumen Utama |
| --- | --- | --- |
| msshi integrations install | msshi integrations install [-h] [--home HOME] [--antigravity ANTIGRAVITY] | --home HOME; --antigravity ANTIGRAVITY |
| msshi integrations dream | msshi integrations dream [-h] [--home HOME] (--run-now \| --register) | --home HOME; --run-now; --register |
| msshi integrations voice | msshi integrations voice [-h] [--home HOME] [--status] [--enable] [--install-runtime] [--role {yukino,shizuka,val,kiki-chii,shikaku}] [--state {normal,calm,tired,incident}] | --home HOME; --status; --enable; --install-runtime; --role {yukino,shizuka,val,kiki-chii,shikaku}; --state {normal,calm,tired,incident} |
| msshi integrations kat | msshi integrations kat [-h] [--home HOME] [--mode {skip,cloud,light,ideal,status}] | --home HOME; --mode {skip,cloud,light,ideal,status} |
| msshi integrations source | Pinned contextual sources, local directory/skill reads and explicit runtime setup. | arguments |

### 9.6  msshi desktop — Status/peluncur GUI atau CLI (0 LLM)

Cek status Hermes Desktop, pemulihan Grey Screen (--software-rendering), atau fallback CLI (--prefer-cli).

```text
Sintaks: msshi desktop [-h] [--hermes-home HERMES_HOME] [--timeout TIMEOUT] [--check-only] [--prefer-cli] [--software-rendering] [--install-shortcut]
```

- --hermes-home HERMES_HOME
- --timeout TIMEOUT
- --check-only
- --prefer-cli — Print Hermes CLI core fallback commands and UI limits for low-RAM devices without opening Desktop
- --software-rendering — Use Hermes' supported GPU fallback for this Desktop launch only
- --install-shortcut — Back up existing Hermes shortcuts and use gateway prewarming on future launches

### 9.7  msshi audit — Read-only (tulis --output opsional) (0 LLM)

Jalankan auditor v3.1 (check_release_v31) terhadap paket, profil, dan bukti tanpa panggilan model.

```text
Sintaks: msshi audit [-h] [--home HOME] [--repo REPO] [--output OUTPUT] [--package-only] [--baseline BASELINE]
```

- --home HOME
- --repo REPO
- --output OUTPUT
- --package-only
- --baseline BASELINE — Legacy provider/model baseline override; the v3.1 full-file baseline remains separate

### 9.8  msshi doctor — Read-only (atau --fix terarah) (0 LLM)

Diagnosis lengkap: RAM, Drive C:/D:/E:, paritas 75 skill, low_ram_diagnostics, dan perbaikan aman --fix.

```text
Sintaks: msshi doctor [-h] [--json] [--fix]
```

- --json — Print JSON output.
- --fix — Restore missing files proven MSSHI-owned; preserve custom edits and all model/provider/endpoint/account settings. No downloads or app launches.

### 9.9  msshi light — Read-only / profil Low-RAM (0 LLM)

Light Build Windows 10 RAM 4 GB: status, aktivasi Low-RAM atomik, indeks lazy, build ZIP <=50 MB, benchmark.

```text
Sintaks: msshi light [-h] {status,mode,index,build,benchmark,cli-fallback} ...
```

| Subperintah | Fungsi / Deskripsi Resmi | Opsi & Argumen Utama |
| --- | --- | --- |
| msshi light status | Inspect hardware tier, build profile, and active light-mode settings (read-only). | --home HOME; --json |
| msshi light mode | Preview or apply light/normal/auto resource profile without touching model/provider config. | --set {auto,light,normal}; --home HOME; --apply; --json |
| msshi light index | Build or inspect lazy per-role skill index cache with excluded-dir hygiene. | --home HOME; --profile PROFILE; --verify-hashes; --no-write; --json |
| msshi light build | Build a deterministic <= 50 MB light bootstrap ZIP from MSSHI 3.1.2. | --output OUTPUT; --manifest MANIFEST; --source SOURCE; --json |
| msshi light benchmark | Run offline synthetic benchmark comparing no_msshi vs light vs full. | --iterations ITERATIONS; --output OUTPUT; --source SOURCE; --json |
| msshi light cli-fallback | Print Hermes CLI core commands and explicit UI limitations for low-RAM machines. | --home HOME; --json |

### 9.10  msshi system — 100% lokal & deterministik (0 LLM)

Sistem Interaksi Cerdas 4 Pilar: audit 0-orphan (status), rute hemat token (route), dan siklus riset/belajar (cycle).

```text
Sintaks: msshi system [-h] {status,route,cycle} ...
```

| Subperintah | Fungsi / Deskripsi Resmi | Opsi & Argumen Utama |
| --- | --- | --- |
| msshi system status | Inspect readiness of all 4 MSSHI Cognitive System pillars (0 LLM calls). | --home HOME; --json |
| msshi system route | Deterministically choose the minimal token-efficient bot/skill pipeline. | --task TASK; --low-ram; --json |
| msshi system cycle | Generate a closed-loop Research, Prediction & Harness2/Dreaming cycle brief. | --home HOME; --goal GOAL; --domain {general,learning,research,prediction,coding,security,creative,daily}; --json |

### 9.11  msshi find — 100% lokal (indeks/cari) (0 LLM)

Pencari skill 4 lapis (bot aktif, spesialis lain, sumber terhubung, arsip lokal) dengan baca 1 SKILL.md on-demand.

```text
Sintaks: msshi find [-h] [--profile PROFILE] [--home HOME] [--top TOP] [--open OPEN_SLUG] [--reindex] [--json] [query ...]
```

- query — Deskripsi tugas atau kata kunci (mis. 'bikin presentasi statistik').
- --profile PROFILE — Profil bot yang sedang bertanya (otomatis terdeteksi dari sesi Hermes jika dikosongkan).
- --home HOME — Folder Hermes home.
- --top TOP — Jumlah maksimal hasil per kategori (default: 5).
- --open OPEN_SLUG — Baca langsung 1 SKILL.md dari brankas arsip berdasarkan slug.
- --reindex — Bangun ulang indeks arsip skill lokal.
- --json — Keluaran JSON.

### 9.12  msshi ossu — Lokal / --fetch GitHub OSSU (0 LLM)

Koneksi Universitas Computer Science Open-Source OSSU (63 mata kuliah, roadmap, guides, courses, open).

```text
Sintaks: msshi ossu [-h] {status,fetch,roadmap,guides,courses,open} ...
```

| Subperintah | Fungsi / Deskripsi Resmi | Opsi & Argumen Utama |
| --- | --- | --- |
| msshi ossu status | Cek koneksi OSSU Open-Source CS University & status cache lokal. | --home HOME; --json |
| msshi ossu fetch | Tarik & verifikasi cache lokal kurikulum OSSU CS terpin (MIT). | --home HOME; --json; --refresh |
| msshi ossu roadmap | Tampilkan peta kurikulum lengkap S1 Computer Science OSSU. | --home HOME; --json |
| msshi ossu guides | Daftar panduan & halaman mata kuliah lokal OSSU yang bisa langsung dibuka. | --home HOME; --json |
| msshi ossu courses | Lihat daftar mata kuliah OSSU per jalur atau cari berdasarkan kata kunci. | track; --search, -s SEARCH; --home HOME; --json |
| msshi ossu open | Buka langsung materi/coursepage dasar OSSU atau detail & link mata kuliah. | target; --browser; --home HOME; --json |

### 9.13  msshi learn — Lokal / pasang plugin belajar (0 LLM)

Mode belajar pemula total tanpa /command: cek status plugin belajar, rekomendasi topik, pasang Chalk/LearnLoop/CodeCoach.

```text
Sintaks: msshi learn [-h] {status,start,install} ...
```

| Subperintah | Fungsi / Deskripsi Resmi | Opsi & Argumen Utama |
| --- | --- | --- |
| msshi learn status | Lihat status alat belajar pemula (Chalk, LearnLoop, CodeCoach, OSSU, MSSHITrim). | --home HOME; --json |
| msshi learn start | Rekomendasikan jalur belajar paling sederhana untuk topik tertentu (0 LLM). | topic; --home HOME; --json |
| msshi learn install | Pasang plugin belajar (Chalk MIT, LearnLoop AGPL opt-in, CodeCoach MIT). | --chalk; --learnloop; --codecoach; --force-stage-codecoach; --home HOME; --json |

### 9.14  msshi upstreams — Read-only jaringan / audit (0 LLM)

Cek pembaruan 64 upstream GitHub tanpa auto-apply (check), audit Caveman/Ponytail, & pasang Ponytail opsional.

```text
Sintaks: msshi upstreams [-h] {check,integrity,install-ponytail} ...
```

| Subperintah | Fungsi / Deskripsi Resmi | Opsi & Argumen Utama |
| --- | --- | --- |
| msshi upstreams check | Cek apakah ada commit baru di GitHub upstream tanpa memasang apa pun. | --id ID; --limit LIMIT; --json |
| msshi upstreams integrity | Audit integritas lokal Caveman, Ponytail, dan cache context-sources (offline). | --home HOME; --json |
| msshi upstreams install-ponytail | Pasang Ponytail (MIT, pin 96608e07) ke profil Shikaku saja. | --home HOME; --json |

### 9.15  msshi skripsi — Tulis .docx ke folder output (0 LLM)

Rakit template Word (.docx) skripsi/tugas akhir drag-and-drop dari PDF pedoman kampus & ZIP MuZA_Search v1.1.

```text
Sintaks: msshi skripsi [-h] [--universitas UNIVERSITAS] [--fakultas FAKULTAS] [--prodi PRODI] [--preset {informatika_ilkom,kuantitatif,kualitatif,rnd,ptk}] [--out-dir OUT_DIR] [--out OUT] [--no-online] [--find-pedoman] [--install-deps] [--no-open] [--non-interactive] [paths ...]
```

- paths — File yang di-drag-and-drop: .zip (MuZA_Search), .pdf/.docx (Pedoman), .ris, .csv/.xlsx, .json, atau .png logo.
- --universitas UNIVERSITAS — Nama universitas (mis. Universitas Negeri Semarang).
- --fakultas FAKULTAS — Nama fakultas.
- --prodi PRODI — Nama program studi.
- --preset {informatika_ilkom,kuantitatif,kualitatif,rnd,ptk}
- --out-dir OUT_DIR — Folder output kustom (default: D:\HermesData\Skripsi_Output atau ~/Documents/MuZA_Skripsi_Output).
- --out OUT — Path file .docx output lengkap.
- --no-online — Nonaktifkan pencarian logo/pejabat online.
- --find-pedoman — Cari juga tautan PDF pedoman kampus saat lookup online.
- --install-deps — Otomatis pasang python-docx/lxml ke folder adaptif HermesData/skripsi-pylibs bila belum ada.

### 9.16  msshi assets — Read-only (cari bahan lokal) (0 LLM)

Cari bahan persona pribadi di direktori lokal pilihan pengguna secara read-only.

```text
Sintaks: msshi assets [-h] --root ROOT [--output OUTPUT]
```

- --root ROOT
- --output OUTPUT

### 9.17  msshi compact — Lokal (padatkan JSON/teks) (0 LLM)

Padatkan data/handoff internal via Caveman filter tanpa merusak sitasi, angka, atau blok kode.

```text
Sintaks: msshi compact [-h] [--format {json,log,auto}] [--max-bytes MAX_BYTES] file
```

- file
- --format {json,log,auto}
- --max-bytes MAX_BYTES

### 9.18  msshi browser — Tulis preferensi lokal (0 LLM)

Simpan pilihan browser (Chrome/Edge/Firefox) dan label akun untuk login manual; tanpa salin cookie.

```text
Sintaks: msshi browser [-h] [--home HOME] [--status] [--browser {chrome,edge,firefox,none}] [--profile-label PROFILE_LABEL] [--account-label ACCOUNT_LABEL] [--rollback ROLLBACK] [--apply]
```

- --home, --hermes-home HOME
- --status — Read the saved choice without accessing a browser/account.
- --browser {chrome,edge,firefox,none} — Save the requested browser; none opts out.
- --profile-label PROFILE_LABEL — Profile label only; no profile directory/cookies are read.
- --account-label ACCOUNT_LABEL — Account label only; sign in manually in the selected browser.
- --rollback ROLLBACK — Preview restoring only this browser-preference receipt.
- --apply — Apply a selected preference rollback; otherwise preview only.

### 9.19  msshi trim — Lokal (MSSHITrim JSON) (0 LLM)

Cek statistik MSSHITrim per profil atau padatkan file JSON secara lossless (kesetaraan kanonik 100%).

```text
Sintaks: msshi trim [-h] [--home HOME] [--binary BINARY] (--input INPUT | --status | --install) [--profile PROFILE] [--profiles PROFILES] [--apply] [--download-runtime] [--force-enable] [--output OUTPUT] [--provider {openai,anthropic,google,gemini}]
```

- --home HOME — Hermes data root; otherwise detect the existing local installation
- --binary BINARY
- --input INPUT — Provider-shaped JSON request; local file only
- --status — Read only aggregate automatic hook counters
- --install — Prepare/enable MSSHITrim on native profiles; preview until --apply
- --profile PROFILE — Hermes profile ID for status
- --profiles PROFILES — Installation only: all or comma-separated real profile IDs
- --apply — Installation only: apply with rollback receipt
- --download-runtime — Installation only: allow checksum-pinned CLI download
- --force-enable — Installation only: explicitly override a previous trim disable

### 9.20  msshi interaction — Lokal (status/install plugin) (0 LLM)

Kelola plugin msshi-interaction v0.2.0: status Tier 0/1/2, protokol terpisah, recover_lock, & ringkasan job.

```text
Sintaks: msshi interaction [-h] [--home HOME] [--source SOURCE] [--status] [--install] [--apply] [--profiles {default,yukino,shizuka,val,kiki-chii,shikaku} [{default,yukino,shizuka,val,kiki-chii,shikaku} ...]] [--protocol] [--prune-terminal] [--max-age-days MAX_AGE_DAYS] [--keep-recent KEEP_RECENT]
```

- --home HOME
- --source SOURCE
- --status
- --install
- --apply
- --profiles {default,yukino,shizuka,val,kiki-chii,shikaku}
- --protocol
- --prune-terminal — Preview (or with --apply, prune) unlocked terminal interaction jobs older than --max-age-days.
- --max-age-days MAX_AGE_DAYS
- --keep-recent KEEP_RECENT

### 9.21  msshi forge — Read-only / --apply profil baru (0 LLM)

Tinjau roster bot dan rancang profil bot baru secara aman tanpa menyentuh provider/model.

```text
Sintaks: msshi forge [-h] [--home HOME] [--roster] [--blueprint BLUEPRINT] [--apply]
```

- --home HOME
- --roster — List IDs and installed skill names only.
- --blueprint BLUEPRINT — Preview a JSON design; no profile is created by default.
- --apply — Create the approved profile after interactive confirmation.

### 9.22  msshi managed — Lokal (kelola skill terkelola) (0 LLM)

Periksa & segarkan salinan skill yang cocok dengan fingerprint terkelola tanpa menimpa edit kustom.

```text
Sintaks: msshi managed [-h] [--source SOURCE] [--baseline BASELINE] [--skills-dir SKILLS_DIR] [--home HOME] [--apply] [--include-optional {rea}] {register,status,update}
```

- {register,status,update}
- --source SOURCE
- --baseline BASELINE
- --skills-dir SKILLS_DIR
- --home HOME
- --apply
- --include-optional {rea} — Explicitly enroll exact copies of this optional wrapper; default is none.

### 9.23  msshi services — Lokal (kompatibilitas MCP) (0 LLM)

Kompatibilitas status layanan eksternal; koneksi akun/MCP tetap diatur sendiri oleh pengguna.

```text
Sintaks: msshi services [-h] [--hermes-home HERMES_HOME] [--share-oauth] [--service {gitlab,tinyfish,brightdata_public}] [--read-test] {status,install,probe}
```

- {status,install,probe}
- --hermes-home HERMES_HOME
- --share-oauth — Retired no-op; credentials are never shared.
- --service {gitlab,tinyfish,brightdata_public}
- --read-test — Retired no-op; no network request is made.

### 9.24  msshi timesfm — Lokal CPU (unduh saat install) (0 LLM)

Peramalan deret waktu CPU offline TimesFM 2.5 (Apache-2.0): status, install, smoke, forecast dengan holdout.

```text
Sintaks: msshi timesfm [-h] [--hermes-home HERMES_HOME] {status,install,smoke,forecast} ...
```

- --hermes-home HERMES_HOME

| Subperintah | Fungsi / Deskripsi Resmi | Opsi & Argumen Utama |
| --- | --- | --- |
| msshi timesfm status | msshi timesfm status [-h] [--verify] | --verify |
| msshi timesfm install | msshi timesfm install [-h] | - |
| msshi timesfm smoke | msshi timesfm smoke [-h] | - |
| msshi timesfm forecast | msshi timesfm forecast [-h] --input INPUT --output OUTPUT [--horizon 1..128] | --input INPUT; --output OUTPUT; --horizon 1..128 |

### 9.25  msshi brag — Lokal (Hyperframes render) (0 LLM)

Alur video peluncuran produk berbasis Hyperframes (doctor, init, renderer, check, render) dengan Concepting First.

```text
Sintaks: msshi brag [-h] {doctor,init,renderer,check,render} ...
```

| Subperintah | Fungsi / Deskripsi Resmi | Opsi & Argumen Utama |
| --- | --- | --- |
| msshi brag doctor | Read local tool/version/verification status; no downloads or browser launch | --hermes-root HERMES_ROOT; --runtime RUNTIME |
| msshi brag init | Create a new concept/review scaffold without reading project contents | --project PROJECT; --output OUTPUT; --title TITLE; --duration DURATION; --format {landscape,vertical,square}; --tone TONE |
| msshi brag renderer | Run only the pinned local doctor/check/render, with an isolated process home | {doctor,check,render}; --hermes-root HERMES_ROOT; --runtime RUNTIME; --project PROJECT; --output OUTPUT; --quality {draft,delivery}; --human-approved-preview |
| msshi brag check | Run the pinned local check with resource checks | --hermes-root HERMES_ROOT; --runtime RUNTIME; --project PROJECT; --output OUTPUT; --quality {draft,delivery}; --human-approved-preview |
| msshi brag render | Run the pinned local render with resource checks | --hermes-root HERMES_ROOT; --runtime RUNTIME; --project PROJECT; --output OUTPUT; --quality {draft,delivery}; --human-approved-preview |

### 9.26  msshi scrapling — Lokal HTML (tanpa crawler) (0 LLM)

Parser CSS/XPath lokal terisolasi untuk berkas HTML lokal (status, install, selftest, parse).

```text
Sintaks: msshi scrapling [-h] [--hermes-home HERMES_HOME] {status,install,selftest,parse} ...
```

- --hermes-home HERMES_HOME

| Subperintah | Fungsi / Deskripsi Resmi | Opsi & Argumen Utama |
| --- | --- | --- |
| msshi scrapling status | msshi scrapling status [-h] [--verify] | --verify |
| msshi scrapling install | Explicit network install of hash-locked parser wheels only | - |
| msshi scrapling selftest | Offline synthetic HTML extraction and safety checks | - |
| msshi scrapling parse | Extract a local UTF-8 HTML file | --input INPUT; --output OUTPUT; --css CSS; --xpath XPATH; --limit 1..1000 |

### 9.27  msshi harness2 — Lokal terisolasi (0 LLM)

Evaluasi harness Google Research Propose-Probe-Compose (status, install, demo deterministik, plan).

```text
Sintaks: msshi harness2 [-h] [--hermes-home HERMES_HOME] {status,install,demo,plan} ...
```

- --hermes-home HERMES_HOME

| Subperintah | Fungsi / Deskripsi Resmi | Opsi & Argumen Utama |
| --- | --- | --- |
| msshi harness2 status | msshi harness2 status [-h] [--verify] | --verify |
| msshi harness2 install | msshi harness2 install [-h] [--source SOURCE] | --source SOURCE |
| msshi harness2 demo | msshi harness2 demo [-h] [--output OUTPUT] | --output OUTPUT |
| msshi harness2 plan | msshi harness2 plan [-h] [--goal GOAL] | --goal GOAL |

### 9.28  msshi optional — Read-only / enable opt-in (0 LLM)

Lihat dan aktifkan skill opsional publik default OFF (rea untuk Shikaku, imagination-studio untuk Kiki-Chii).

```text
Sintaks: msshi optional [-h] [--source SOURCE] {list,enable} ...
```

- --source SOURCE

| Subperintah | Fungsi / Deskripsi Resmi | Opsi & Argumen Utama |
| --- | --- | --- |
| msshi optional list | Lihat fungsi, peran, dan prasyarat opsi; semua default publik OFF. | --lang {id,en} |
| msshi optional enable | Pasang wrapper opsional (rea untuk Coder, imagination-studio untuk Kiki-Chii/Content Creator). Semua default publik OFF; runtime & aplikasi eksternal dipasang terpisah. | {rea,imagination-studio}; --target-dir TARGET_DIR; --install-runtime; --hermes-home HERMES_HOME |

### 9.29  msshi rea — Lokal statis (opsional Coder) (0 LLM)

Analisis reverse engineering statis JavaScript/arsip/native khusus Shikaku (status, install, selftest, javascript, inspect, native).

```text
Sintaks: msshi rea [-h] [--hermes-home HERMES_HOME] {status,install,selftest,javascript,inspect,native} ...
```

- --hermes-home HERMES_HOME

| Subperintah | Fungsi / Deskripsi Resmi | Opsi & Argumen Utama |
| --- | --- | --- |
| msshi rea status | msshi rea status [-h] | - |
| msshi rea install | msshi rea install [-h] | - |
| msshi rea selftest | msshi rea selftest [-h] | - |
| msshi rea javascript | Static extracted JavaScript/Electron directory or ASAR inspection | path; --output OUTPUT; --analysis-timeout-ms 1000..120000 |
| msshi rea inspect | Read-only local artifact routes; no extraction or target execution | {archive,managed,pe-imports,pe-certificates,go,rust,model,wasm}; path; --output OUTPUT |
| msshi rea native | Explicit installed native engine; may launch that local engine | {analyze,search,function,decompile,xrefs,trace}; path; --provider {ghidra,hopper,kuna}; --query QUERY; --output OUTPUT |

### 9.30  msshi studio — Lokal / probe 127.0.0.1:7870 (0 LLM)

Status dan rencana Slate kolaborasi opsional Imagination Studio untuk Kiki-Chii (status, plan).

```text
Sintaks: msshi studio [-h] [--hermes-home HERMES_HOME] {status,plan} ...
```

- --hermes-home HERMES_HOME — Hermes data root (auto-detected if omitted).

| Subperintah | Fungsi / Deskripsi Resmi | Opsi & Argumen Utama |
| --- | --- | --- |
| msshi studio status | Inspect Imagination Studio wrapper & Kiki-Chii Filmmaker readiness. | --url URL; --probe; --json |
| msshi studio plan | Generate a 5-phase Filmmaker x Imagination Studio collaboration blueprint. | --concept CONCEPT; --format {short,youtube,cinema}; --json |

### 9.31  msshi choices — 100% read-only lokal (0 LLM)

Baca fungsi dan prasyarat seluruh 136 skill, 6 paket, 6 mode, 43 fitur, dan 47 aplikasi tanpa memasang apa pun.

```text
Sintaks: msshi choices [-h] [--kind {all,modes,platforms,packs,skills,features,apps}] [--lang {id,en}] [--json] [item]
```

- item — ID fitur/skill/paket, misalnya rea, kat, filmmaking atau unslop.
- --kind {all,modes,platforms,packs,skills,features,apps} — Batasi daftar ke jenis pilihan tertentu.
- --lang {id,en} — Bahasa penjelasan: id atau en.
- --json — Keluarkan katalog penjelasan sebagai JSON.

### 9.32  msshi manual — Lokal / unduh PDF GitHub (0 LLM)

Daftar katalog PDF resmi (list) dan unduh manual versi pilihan dengan verifikasi SHA-256 (download).

```text
Sintaks: msshi manual [-h] {list,download} ...
```

| Subperintah | Fungsi / Deskripsi Resmi | Opsi & Argumen Utama |
| --- | --- | --- |
| msshi manual list | Tampilkan daftar Buku Panduan PDF per versi. | - |
| msshi manual download | Unduh Buku Panduan PDF versi pilihan dengan verifikasi SHA256. | --version VERSION; --dest DEST; --json |

### 9.33  msshi dream — Lokal offline (tulis DREAMS.md) (0 LLM)

Susun proposal refleksi pelajaran lokal ke memories/DREAMS.md; promosi ke MEMORY.md selalu menunggu manusia.

```text
Sintaks: msshi dream [-h] [--home HOME] (--run-now | --register)
```

- --home HOME
- --run-now
- --register

### 9.34  msshi voice — Lokal CPU (unduh saat install) (0 LLM)

Status, pasang runtime, dan aktifkan TTS offline OmniVoice per profil (auto_start: false, unload otomatis).

```text
Sintaks: msshi voice [-h] [--home HOME] [--status] [--enable] [--install-runtime] [--role {yukino,shizuka,val,kiki-chii,shikaku}] [--state {normal,calm,tired,incident}]
```

- --home HOME
- --status
- --enable
- --install-runtime
- --role {yukino,shizuka,val,kiki-chii,shikaku}
- --state {normal,calm,tired,incident}

### 9.35  msshi kat — Tulis konfigurasi privat Coder (0 LLM)

Pintasan wizard endpoint/key opsional KAT-Coder khusus Shikaku (tidak mengubah model utama).

```text
Sintaks: msshi kat [-h] [--home HOME] [--mode {skip,cloud,light,ideal,status}]
```

- --home HOME
- --mode {skip,cloud,light,ideal,status}

### 9.36  msshi coder — Tulis konfigurasi privat Coder (0 LLM)

Kelola konfigurasi opsional KAT-Coder khusus Shikaku (status, presets, wizard, disable, configure).

```text
Sintaks: msshi coder [-h] [--home HOME] [--mode {status,skip,cloud,light,ideal}] {status,presets,wizard,disable,configure} ...
```

- --home, --hermes-home HOME
- --mode {status,skip,cloud,light,ideal} — Legacy KAT mode; selected setup performs the endpoint wizard.

| Subperintah | Fungsi / Deskripsi Resmi | Opsi & Argumen Utama |
| --- | --- | --- |
| msshi coder status | Read optional Coder KAT/Goose readiness without an API call. | - |
| msshi coder presets | Show verified endpoint choices and model variant differences. | - |
| msshi coder wizard | Configure the optional Coder endpoint and hidden credential input. | - |
| msshi coder disable | Disable only KAT routing; keep primary models and saved settings. | - |
| msshi coder configure | Prepare or activate KAT with explicit endpoint credentials and catalog evidence. | --preset {exact-dev,streamlake-payg,custom}; --base-url BASE_URL; --model MODEL; --api-key-env API_KEY_ENV; --read-key; --probe; --activate |

### 9.37  msshi setup — Wizard setup 4+1 tahap (0 LLM)

Pasang dan konfigurasi 6 mode (Academic Mahasiswa/Dosen, MuZA, Solo, Custom, Selective) + Low-RAM + 4+1 tahap.

```text
Sintaks: msshi setup [-h] [--platform {hermes,openclaw,claude,codex,antigravity,manual}] [--target-dir TARGET_DIR] [--lang {id,en}] [--mode {solo,custom-bots,selective,muza-preset,academic-mahasiswa,academic-dosen,academic-mahasiswa-dosen}] [--yes] [--default-bot {auto,yukino,keep-hermes}] [--extra-packs EXTRA_PACKS [EXTRA_PACKS ...]] [--extra-skills EXTRA_SKILLS [EXTRA_SKILLS ...]] [--kat-mode {light,ideal,cloud,skip}] [--stage-auto-trim] [--install-steel] [--connect-services {skip,per-profile,share-oauth}] [--academic-project ACADEMIC_PROJECT] [--academic-level ACADEMIC_LEVEL] [--academic-topic ACADEMIC_TOPIC] [--academic-deadline ACADEMIC_DEADLINE] [--academic-campus-guideline ACADEMIC_CAMPUS_GUIDELINE] [--preferred-name PREFERRED_NAME] [--browser {chrome,edge,firefox,none}] [--browser-profile-label BROWSER_PROFILE_LABEL] [--browser-account-label BROWSER_ACCOUNT_LABEL] [--connect-apps {skip,auto-reconnect,select}] [--connect-bots CONNECT_BOTS] [--connect-targets CONNECT_TARGETS] [--with-rea] [--with-imagination-studio] [--with-learnloop] [--with-codecoach] [--low-ram] [--resource-profile {auto,light,normal}] [--download-pdf] [--no-pdf] [--pdf-version PDF_VERSION] [--pdf-dest PDF_DEST]
```

- --platform {hermes,openclaw,claude,codex,antigravity,manual}
- --target-dir TARGET_DIR
- --lang {id,en} — Bahasa penjelasan pilihan (id/en); format input tetap sama.
- --mode {solo,custom-bots,selective,muza-preset,academic-mahasiswa,academic-dosen,academic-mahasiswa-dosen} — Pilih mode langsung tanpa prompt.
- --yes, -y — Konfirmasi otomatis tanpa prompt.
- --default-bot {auto,yukino,keep-hermes} — auto: baru = default Yukino + 4 spesialis; existing dipertahankan. yukino: ubah default tanpa memindahkan model/chat. keep-hermes: default netral + 5 profil bernama.
- --extra-packs EXTRA_PACKS — Tambahkan extra packs di langkah [1/4] Skills.
- --extra-skills EXTRA_SKILLS — Tambahkan extra skill slugs di langkah [1/4] Skills.
- --kat-mode {light,ideal,cloud,skip} — Buka wizard endpoint KAT khusus Coder (light/ideal/cloud alias kompatibilitas); skip menonaktifkan KAT saja. Tidak mengunduh model.
- --stage-auto-trim — Stage plugin fail-open msshi-auto-trim ke profil Hermes di langkah [2/4] Plugin.

### 9.38  msshi select — Tulis skill/paket pilihan (0 LLM)

Tambah skill atau paket tertentu ke profil/direktori pilihan dengan pratinjau rencana terlebih dahulu.

```text
Sintaks: msshi select [-h] [--platform {hermes,openclaw,claude,codex,antigravity,manual}] [--target-dir TARGET_DIR] [--lang {id,en}] [--local]
```

- --platform {hermes,openclaw,claude,codex,antigravity,manual}
- --target-dir TARGET_DIR
- --lang {id,en} — Bahasa penjelasan pilihan (id/en); format input tetap sama.
- --local — Pilih dari rilis lokal tanpa mengakses GitHub.

### 9.39  msshi bootstrap — Pasang launcher global PATH (0 LLM)

Pasang launcher perintah global msshi dari rilis lokal (mendukung --light dan --no-path).

```text
Sintaks: msshi bootstrap [-h] [--no-path] [--light] [--no-pdf] [--pdf-version PDF_VERSION] [--pdf-dest PDF_DEST]
```

- --no-path — Jangan ubah PATH user.
- --light — Stage Light Build ringan (<= 50 MB) tanpa aset besar atau penyalinan PDF otomatis.
- --no-pdf — Lewati penyalinan otomatis panduan PDF.
- --pdf-version PDF_VERSION — Pilih versi panduan; default latest.
- --pdf-dest PDF_DEST — Folder PDF; default Downloads/MSSHI_Manuals.

# 10. Katalog Lengkap 75 Skill Bundel, 2 Opsional, 7 Plugin & 6 Paket

Bab ini mendaftarkan 100% isi katalog aktif MSSHI v3.1.2 langsung dari bot_role_and_skill_matrix.json, option_help.json, optional/manifest.json, dan msshi_cognitive_system.json: tepat 75 skill bundel (53 inti + 22 wrapper integrasi), 2 skill opsional publik default OFF, 7 plugin native Hermes, dan 6 paket kategori.

## 10.1 Enam Paket Kategori (Mode Selective)

| Paket | Jumlah | Cakupan & Kegunaan |
| --- | --- | --- |
| core | 21 | Fondasi ideasi, gaya tulisan, persona, OCR, koordinasi, dan akses alat sesuai tugas. |
| filmmaking | 10 | Perencanaan film/foto, visual, motion graphics, dan video; produksi memakai alat yang disiapkan terpisah. |
| business | 4 | Analisis usaha, skenario keuangan, dan perhitungan bisnis lewat harness lokal. |
| thesis | 41 | Ide penelitian, literatur, metode, analisis data, penulisan, revisi, dan presentasi skripsi. |
| webdev | 12 | Pemetaan proyek, pengembangan web/UI, eksperimen kode, dan pengujian. |
| cybersec | 7 | Pemetaan kode dan panduan audit keamanan pada target yang izinnya jelas; engine dipasang terpisah. |

## 10.2 Daftar Lengkap 75 Skill Bundel Aktif (53 Inti + 22 Wrapper)

| Slug Skill | Jenis | Paket | Peran Bot (MuZA) | Fungsi Resmi & Mode Muat |
| --- | --- | --- | --- | --- |
| 1. academic-plotting | Inti | filmmaking, thesis | Kiki-Chii | Menghasilkan figur publikasi dari data dan spesifikasi yang disepakati. [on_demand_skill] |
| 2. ai-research-explore | Inti | - | Shikaku | Merancang eksperimen kandidat yang terpisah dari baseline. [on_demand_skill] |
| 3. ai-research-reproduction | Inti | cybersec | Shikaku | Menetapkan target reproduksi penelitian yang dapat dibuktikan. [on_demand_skill] |
| 4. analyze-project | Inti | webdev, cybersec | Shikaku | Memetakan struktur proyek, konfigurasi, titik masuk, dan risiko perubahan. [on_demand_skill] |
| 5. antigravity-webdev-cybersec | Wrapper | webdev, cybersec | Shikaku | Hubungkan pengerjaan web dan evaluasi keamanan terotorisasi dengan Antigravity, Goose, dan alat lokal. [on_demand_skill] |
| 6. auto-curiousity-for-film-making | Inti | filmmaking, thesis | Kiki-Chii | Menguji kemampuan alat kreatif dan teknik produksi dalam eksperimen terpisah. [on_demand_skill] |
| 7. autoresearch | Inti | core, thesis | Shizuka | Mengoordinasikan siklus eksperimen dan sintesis dengan batas berhenti. [on_demand_skill] |
| 8. backward-traceability | Inti | thesis | Yukino, Shizuka, Val | Menautkan angka dan hasil laporan kembali ke data, skrip, atau perhitungan. [core_always_light] |
| 9. belajar-pemula | Inti | core | Semua 5 Bot | Mode belajar ramah pemula total ('tinggal ngobrol' tanpa /command): cek level & energi, ajarkan 1 konsep per balasan, pilih otomatis LearnLoop, Chalk (papan tulis visual), CodeCoach/Shikaku, atau OSSU. [core_always_light] |
| 10. brag | Wrapper | filmmaking | Kiki-Chii | Rancang video peluncuran produk yang dapat diedit dengan Hyperframes, dimulai dari konsep dan review manusia. [opt_in_runtime] |
| 11. brainstorming-research-ideas | Inti | core, thesis | Yukino | Memakai kerangka ideasi terstruktur untuk menemukan pertanyaan layak. [on_demand_skill] |
| 12. business-sage | Inti | business | Yukino, Shizuka, Val, Kiki-Chii | Menyusun analisis usaha, skenario finansial, dan pertanyaan verifikasi aturan yang relevan. [on_demand_skill] |
| 13. career-ops | Wrapper | business | Semua 5 Bot | Bantu CV-lowongan, strategi karier, tracker dan wawancara; source, runtime dan CV pengguna terpisah. [lazy_context_source] |
| 14. chatgpt-hermes-portability-kit | Inti | core, thesis | Yukino, Shizuka, Val | Memandu adaptasi metode dan profil ke platform lain menggunakan sumber yang sah. [on_demand_skill] |
| 15. claude-bughunter | Wrapper | webdev, cybersec | Shikaku | Audit kerentanan, triage, validasi bukti, dan pelaporan keamanan terotorisasi (83 skill, 15 command, 681 pola, 433 laporan terungkap bersitasi terverifikasi) untuk Coder pada aset/scope berizin. [lazy_context_source] |
| 16. cli-anything-business-sage | Inti | business | Yukino, Shizuka, Val, Kiki-Chii | Menjalankan perhitungan bisnis terstruktur melalui harness lokal yang tersedia. [on_demand_skill] |
| 17. cli-anything-universal-bridge | Wrapper | core | Semua 5 Bot | Daftarkan, periksa, dan jalankan rute aplikasi, browser, serta alat agen yang tersedia saat dibutuhkan. [core_always_light] |
| 18. creative-thinking-for-research | Inti | core, thesis | Yukino | Mencoba reframing, analogi, dan kombinasi konsep untuk membuka pilihan. [on_demand_skill] |
| 19. data-analysis | Inti | thesis | Val | Memeriksa kualitas data, asumsi, uji statistik, dan ketidakpastian. [on_demand_skill] |
| 20. deep-research | Inti | thesis | Shizuka, Val | Menyusun pertanyaan, menelusuri literatur, dan mensintesis bukti yang dapat diperiksa. [on_demand_skill] |
| 21. evaluating-code-models | Inti | webdev, cybersec | Shikaku | Menguji keluaran model kode dengan tugas dan tolok ukur yang relevan. [on_demand_skill] |
| 22. evaluating-llms-harness | Inti | - | Shikaku | Rencanakan evaluasi LLM memakai harness yang kompatibel dan anggaran yang disepakati. [on_demand_skill] |
| 23. explore-code | Inti | webdev | Shikaku | Mengembangkan perubahan eksperimen dalam ruang kerja terisolasi. [on_demand_skill] |
| 24. explore-run | Inti | webdev | Shikaku | Menjalankan uji terbatas dengan anggaran dan catatan hasil yang jelas. [on_demand_skill] |
| 25. filmmaking-videography-photography-s2 | Inti | filmmaking, thesis | Kiki-Chii | Menyatukan konsep, pengarahan, kamera, foto, penyuntingan, warna, dan suara. [on_demand_skill] |
| 26. firecrawl-competitive-intel | Inti | thesis | Val | Membandingkan perubahan produk, harga, dan fitur dengan bukti bertanggal. [on_demand_skill] |
| 27. firecrawl-dashboard-reporting | Inti | thesis | Val | Mengambil dan memeriksa indikator dasbor untuk pelaporan. [on_demand_skill] |
| 28. firecrawl-deep-research | Inti | thesis | Val | Mengumpulkan bukti web untuk sintesis dengan atribusi. [on_demand_skill] |
| 29. firecrawl-knowledge-base | Inti | thesis | Val | Menyiapkan koleksi dokumen, potongan, serta metadata asalnya. [on_demand_skill] |
| 30. firecrawl-research-papers | Inti | thesis | Val | Menemukan dan memeriksa makalah pada sumber akademik yang relevan. [on_demand_skill] |
| 31. focus-my-energy | Inti | core, thesis | Yukino | Menyesuaikan beban tugas dan langkah awal dengan energi yang dilaporkan pengguna. [core_always_light] |
| 32. generate-fresh-ideas | Inti | core, thesis | Yukino | Menghasilkan alternatif dari beberapa lensa kreatif untuk disaring pengguna. [on_demand_skill] |
| 33. get-more-perspectives | Inti | core, thesis | Shizuka | Menguji keputusan dari beberapa sudut pandang sebelum memilih. [on_demand_skill] |
| 34. github-research | Inti | thesis | Val | Menelaah lisensi, rancangan, pemeliharaan, dan kesiapan repositori. [on_demand_skill] |
| 35. grim-prompter | Wrapper | webdev, cybersec | Shikaku | Pemodelan ancaman berbasis bukti (36 arsitektur, 29 metode, STRIDE/PASTA/LINDDUN, dan analisis privasi GDPR/CCPA) untuk Coder secara read-only. [lazy_context_source] |
| 36. harness2 | Wrapper | thesis, webdev | Semua 5 Bot | Kelima bot dapat menyusun proposal dan demo evaluasi harness; tidak mempromosikan perubahan otomatis. [opt_in_runtime] |
| 37. higgsfield-skills | Wrapper | filmmaking | Kiki-Chii | Rutekan kebutuhan produksi kreatif ke modul Higgsfield yang sesuai setelah konsep disetujui. [on_demand_skill] |
| 38. humanizer-en | Wrapper | core | Semua 5 Bot | Sunting prosa bahasa Inggris agar terasa alami sambil menjaga makna, suara penulis, dan sitasi. [on_demand_skill] |
| 39. humanizer-indonesia | Wrapper | core | Semua 5 Bot | Sunting prosa bahasa Indonesia sesuai ragam pembaca sambil menjaga makna, istilah, dan sitasi. [on_demand_skill] |
| 40. idea-generation | Inti | core, thesis | Yukino | Mengembangkan dan menyaring gagasan penelitian dalam beberapa putaran. [on_demand_skill] |
| 41. langsmith-observability | Inti | - | Shikaku | Memandu observabilitas dan evaluasi LangSmith pada lingkungan yang disetujui. [on_demand_skill] |
| 42. lemo-opuscar | Wrapper | filmmaking | Kiki-Chii | Khusus Kiki-Chii (Content Creator/Filmmaker): katalog 15 kategori & 99 gaya film pendek berbasis kode (Lemo-Opuscar) dengan cache teks terpin on-demand (0 aset media berat di folder skills/) dan Concepting First. [lazy_context_source] |
| 43. literature-review | Inti | thesis | Shizuka, Val | Membangun tinjauan pustaka dengan beberapa perspektif dan jejak sumber. [on_demand_skill] |
| 44. match-my-writing-style | Inti | core | Semua 5 Bot | Menerapkan Voice Card yang disediakan pengguna sesuai audiens dan jenis tulisan. [core_always_light] |
| 45. math-reasoning | Inti | thesis | Val | Memeriksa langkah penalaran matematika dan syarat berlakunya. [on_demand_skill] |
| 46. mattpocock-engineering | Wrapper | webdev, cybersec | Semua 5 Bot | Pilih disiplin TDD, debugging dan domain model; orkestrator/spec publish hanya saat diminta. [lazy_context_source] |
| 47. motion-graphics-suite | Wrapper | filmmaking | Kiki-Chii | Pilih dan hubungkan empat rujukan motion graphics untuk komposisi yang tetap dapat diedit. [on_demand_skill] |
| 48. muza-skripsi-template | Inti | thesis | Shizuka, Val | Menyusun template Word (.docx) skripsi/tugas akhir sesuai aturan pedoman kampus, mencari logo & pejabat resmi otomatis, dan menyuntikkan hasil MuZA_Search. [on_demand_skill] |
| 49. nemo-evaluator-sdk | Inti | - | Shikaku | Memandu evaluasi dengan NeMo Evaluator SDK jika dependensinya tersedia. [on_demand_skill] |
| 50. notebooklm-thinking-datascience | Inti | thesis | Yukino, Shizuka, Val | Terapkan metode berpikir sistem dan data science dari indeks sumber milik pengguna. [on_demand_skill] |
| 51. novelty-assessment | Inti | thesis | Shizuka, Val | Menguji klaim kebaruan terhadap studi terdekat dan batas pencarian. [on_demand_skill] |
| 52. paper-context-resolver | Inti | thesis | Val | Mengikat klaim reproduksi pada bagian, gambar, tabel, atau lampiran makalah. [on_demand_skill] |
| 53. paper-revision | Inti | thesis | Shizuka, Val | Memetakan catatan revisi ke perubahan konkret dan bukti perbaikan. [on_demand_skill] |
| 54. paper-writing-section | Inti | thesis | Shizuka, Val | Menyusun dan menyunting bagian naskah akademik dengan dua tahap pemeriksaan. [on_demand_skill] |
| 55. parenting-6d-gad-mdd | Inti | core | Semua 5 Bot | Dukung percakapan dengan empati, struktur, dan otonomi; panduan ini tidak menggantikan perawatan klinis. [core_always_light] |
| 56. persona-shizuka-yukino-shikaku | Inti | core | Semua 5 Bot | Menjaga karakter, kontrak serah terima, dan batas kepemilikan tugas lima bot. [core_always_light] |
| 57. phoenix-observability | Inti | - | Shikaku | Memandu tracing dan evaluasi Phoenix tanpa memindahkan data di luar lingkup. [on_demand_skill] |
| 58. prep-for-meetings | Inti | core, thesis | Yukino | Menyusun ringkasan pertemuan dari catatan dan tujuan yang tersedia. [on_demand_skill] |
| 59. prep-for-meetings-2 | Inti | core, thesis | Yukino | Memadatkan bahan pertemuan menjadi pokok bahasan dan kartu pengingat. [on_demand_skill] |
| 60. rea-video | Wrapper | filmmaking | Kiki-Chii | Kiki membedah referensi video ke VIDEO.md; VLM, audio-model dan remake adalah pilihan terpisah. [lazy_context_source] |
| 61. rebuttal-writing | Inti | thesis | Shizuka, Val | Menyusun jawaban poin demi poin untuk masukan pembimbing atau reviewer. [on_demand_skill] |
| 62. remote-jobs | Wrapper | business | Semua 5 Bot | Cari perusahaan remote dari direktori lokal terpin; lowongan aktif tetap diverifikasi terpisah. [lazy_context_source] |
| 63. research-paper-writing | Inti | thesis | Shizuka, Val | Memeriksa struktur argumen dan hubungan antara klaim, bukti, serta pembahasan. [on_demand_skill] |
| 64. riset-mendalam-nusantara-global | Inti | thesis | Val | Khusus Val: pipeline riset mendalam 10 tahap (Quick/Standard/Deep, adequacy gate, devil's advocate, audit klaim & sitasi) dengan metodologi akademik Indonesia (Bab I-V, SINTA 1-6, Garuda, RAMA, EYD V) & global (Scopus/WoS, PRISMA 2020). [on_demand_skill] |
| 65. rust-anything | Wrapper | webdev | Shikaku | Khusus Coder (Shikaku): migrasi & porting bertahap kode TS/JS/Python/C/Go/Ruby/Java ke Rust dengan rekaman ground-truth, diff, benchmark, shadow, dan gate kelulusan (CLI/MCP rust-anything terpisah). [lazy_context_source] |
| 66. scrapling | Wrapper | thesis, webdev | Val, Shikaku | Ekstraksi CSS/XPath dari HTML lokal dalam runtime parser terisolasi. [opt_in_runtime] |
| 67. sharewise | Wrapper | core | Semua 5 Bot | Pemeriksaan privasi foto & video lokal sebelum dibagikan (laporan ya/tidak saja, tanpa membocorkan GPS/waktu/perangkat) plus salinan bersih terverifikasi. [on_demand_skill] |
| 68. slide-generation | Inti | filmmaking, thesis | Kiki-Chii | Menyusun presentasi dari argumen, hasil, dan visual yang dapat diverifikasi. [on_demand_skill] |
| 69. spacewise | Wrapper | core | Semua 5 Bot | Pembersihan ruang penyimpanan lokal aman (duplikat, installer sisa, foto mirip/buram, laporan file besar) dengan pratinjau lokal dan persetujuan eksplisit. [on_demand_skill] |
| 70. symbolic-equation | Inti | thesis | Val | Mencari kandidat persamaan yang dapat ditafsirkan dan diuji. [on_demand_skill] |
| 71. table-generation | Inti | thesis | Val | Membangun tabel akademik dari hasil terverifikasi beserta satuan dan catatan. [on_demand_skill] |
| 72. timesfm-forecasting | Wrapper | thesis | Val | Prediksi deret waktu numerik secara lokal memakai TimesFM 2.5 setelah setup runtime dan bobot terpisah. [opt_in_runtime] |
| 73. unlimited-ocr-2 | Wrapper | core | Semua 5 Bot | Rutekan ekstraksi dokumen dan gambar berhalaman ke OCR yang tersedia dengan penunjuk bukti. [on_demand_skill] |
| 74. unslop | Wrapper | filmmaking, thesis, webdev | Val, Kiki-Chii, Shikaku | Tinjau dan perbaiki desain antarmuka; skill ini mengubah UI, bukan gaya prosa bot. [on_demand_skill] |
| 75. wise-judgment-and-sovereign-orchestrator | Inti | core, thesis | Shizuka | Mengatur pilihan alur, anggaran, persetujuan, delegasi, dan sintesis hasil Val. [core_always_light] |

## 10.3 Skill Opsional Terpisah (2 Skill — Public Default OFF)

| Slug Opsional | Default | Peran Target | Lokasi | Fungsi & Batas |
| --- | --- | --- | --- | --- |
| rea | OFF (Opt-in) | shikaku | optional/rea | Analisis statis JavaScript atau arsip milik pengguna lewat CLI lokal; format native memerlukan engine terpisah. |
| imagination-studio | OFF (Opt-in) | kiki-chii | optional/imagination-studio | Opsional khusus Kiki-Chii/Content Creator: jembatan Slate & antrean render lokal Imagination Studio (gambar, klip video+suara, voice, musik, SFX) yang bekerja sama dengan Filmmaker saat dipilih. |

## 10.4 Tujuh Plugin Native Hermes & Alias Skill

| ID Plugin | Status | Pilar | Peran & Jaminan Keamanan |
| --- | --- | --- | --- |
| msshi-auto-trim | active_default | token_efficiency | Lossless local JSON compaction (MSSHITrim) for eligible >= 2048-char tool results; fail-open, 0 LLM calls. (Hook: transform_tool_result) |
| msshi-team-routing | active_default | governance_and_routing | Native named-profile delegation, 5-Mission + 4-Pillar Cognitive Loop prompt, zero-LLM 4-layer skill finder tool (msshi_find_skill) on all 6 profiles including default, and opt-in Shikaku KAT routing. (Hook: delegation_provider + system_prompt_section + tool (msshi_find_skill)) |
| msshi-interaction | active_default_named_bots | token_efficiency | Dedicated interaction prompt protocol + controller: Tier 0 Main-only, Type 1 Advisor (Yukino/Shizuka), Type 2 2-round Council with compact dossiers (Val/Kiki-Chii/Shikaku), stale-lock recovery (recover_lock), and session-isolated job summaries with explicit opt-in retention. (Hook: pre_tool_call + system_prompt_section + tools (msshi_interaction_begin/step/status, msshi_advisor_context)) |
| msshi-steel-policy | retired_legacy_not_installed | governance_and_routing | Retired from installer; replaced by user-selected local browser via msshi browser without cookie extraction or account transfer. (Hook: retired) |
| spacewise | active_default | governance_and_routing | Local-only safe storage cleanup with literal-folder guard, local HTML preview, and human-approved undoable Trash (MIT, ardianreffa). (Hook: pre_tool_call + tools (spacewise_scan/preview/trash/undo)) |
| sharewise | active_default | governance_and_routing | Local-only photo/video privacy check (Wall T1 yes/no counts only), manual/Vision review page, and clean redacted copies (MIT, ardianreffa). (Hook: pre_tool_call + tools (sharewise_check/review/share/look)) |
| chalk | active_default | governance_and_routing | Visual chalkboard teaching in Hermes Desktop/CLI using user's configured TTS (MIT, NNADI Joshua); outputs >= 2048 chars compacted by MSSHITrim. (Hook: transform_llm_output + tool (chalk_teach)) |

| Alias Masukan | Slug Kanonis | Catatan |
| --- | --- | --- |
| auto-curiosity-for-film-making | auto-curiousity-for-film-making | Alias otomatis diarahkan ke slug kanonis saat setup/select. |

# 11. Katalog Lengkap 64 Sumber Upstream Terpin & Tata Kelola Lisensi

Seluruh 64 sumber eksternal (61 repositori Git terpin commit SHA, 2 model-card, dan 1 katalog) dikelola di luar folder skills/ (cache upstreams/ atau msshi-private/context-sources/) sehingga pemindaian skill tetap secepat kilat. Gunakan msshi upstreams check untuk memeriksa pembaruan upstream secara read-only tanpa auto-apply.

> **Ringkasan Tata Kelola Lisensi & Kepatuhan Pihak Ketiga**
> - • Kode & wrapper orisinal MSSHI berlisensi MIT License (bebas dipakai & diadaptasi dengan atribusi).
> - • Sumber dengan lisensi non-komersial/khusus dipisahkan & dinyatakan transparan: bobot OmniVoice (CC-BY-NC), instruksi Unslop (CC BY 4.0), dokumentasi Claude-BugHunter (CC BY 4.0; kode MIT), dokumentasi Lemo-Opuscar (CC BY-NC 4.0 dengan izin pembuatan film komersial oleh pengguna; kode MIT), dan plugin eksternal LearnLoop (AGPL-3.0 — opt-in terpisah, tidak pernah divendor ke repo MIT).
> - • Selalu periksa THIRD_PARTY_NOTICES.md dan CREDITS.md sebelum distribusi komersial aset/bobot pihak ketiga.

| ID Upstream | Tipe | Lisensi | Peran | Pin | Kapan Dipakai / Cakupan |
| --- | --- | --- | --- | --- | --- |
| 1. higgsfield-skills | git | MIT | kiki-chii | 2700040207 | Pilih generasi gambar/video/foto produk atau brand kit dari treatment Kiki-Chii. |
| 2. remotion-skills | git | Unresolved at audited revision; do not redistribute without permission | kiki-chii | 1af7e69a2a | Pilih video yang memerlukan timing, rendering terprogram atau subtitle yang dapat diedit. |
| 3. barty-motion-graphics | git | MIT | kiki-chii | 3d83d987d6 | Pilih iklan motion dari kode dan sound pass terstruktur. |
| 4. charlie-motion-graphics | git | MIT | kiki-chii | 229022ebca | Pilih motion peluncuran yang seluruh frame-nya dibangun dengan kode. |
| 5. bang-motion | git | MIT | kiki-chii | c1aa65e921 | Pilih opener, promo, teks bergerak atau explainer HTML. |
| 6. humanizer-en | git | MIT | all | b48c832f0f | Sunting tulisan Inggris sambil menjaga fakta, kutipan dan suara penulis. |
| 7. humanizer-indonesia | git | MIT | all | 62fe1aed59 | Sunting tulisan Indonesia menurut ragam akademik, ajar atau semiformal. |
| 8. anti-slop | git | MIT | all | 3b75daa1fb | Tinjau kebiasaan generik pada prose, UI atau kode sesuai output yang diminta. |
| 9. goose | git | Apache-2.0 | shikaku | 0bf8b62407 | Delegasikan vibecoding pada workspace yang dipilih. |
| 10. superpowers | git | MIT | shikaku-nara | 22f0b463e7 | Gunakan planning, debugging dan verifikasi untuk perubahan bertahap. |
| 11. ponytail | git | MIT | shikaku-nara | 96608e078b | Tinjau solusi yang terlalu kompleks dan kurangi perubahan yang tidak perlu. |
| 12. addy-agent-skills | git | MIT | shikaku-nara | 301b02b12b | Pilih playbook coding, delivery, atau review sesuai fase. |
| 13. graphify | git | Apache-2.0 | all | 5eedffa874 | Petakan kode, dokumentasi dan dependensi sebelum membuka banyak file. |
| 14. mindrally-skills | git | Apache-2.0 | shikaku-nara | 7682ca7771 | Muat keahlian framework atau bahasa yang cocok dengan proyek. |
| 15. playwright-best-practices | git | MIT | shikaku-nara | 0b75b5835a | Rancang tes E2E dengan locator, isolasi dan debugging yang dapat diulang. |
| 16. awesome-copilot | git | MIT | shikaku-nara | 227949a754 | Cari agen, instruksi atau skill Copilot yang sesuai dengan tugas. |
| 17. superdesign-skill | git | MIT | kiki-chii, shikaku-nara, antigravity | f9f05cd988 | Tetapkan gaya, alur antarmuka dan standar visual sebelum implementasi. |
| 18. better-design | git | MIT | kiki-chii, shikaku-nara, antigravity | 175e7ba49b | Cari tema, token desain, atau komponen UI siap adaptasi. |
| 19. design-taste | git | MIT | kiki-chii, shikaku-nara, antigravity | c4a6bff087 | Pilih identitas visual yang cocok dengan brief dan konsistensi antarlayar. |
| 20. paper-shaders | git | Apache-2.0 | kiki-chii, shikaku-nara, antigravity | b6e6e7f73f | Gunakan shader canvas untuk elemen visual saat efek tersebut diperlukan. |
| 21. canvas-ui | git | MIT + Commons Clause | kiki-chii, shikaku-nara, antigravity | a0be3b7e1f | Gunakan komponen WebGL/canvas pada UI dengan anggaran performa yang sesuai. |
| 22. motion-primitives | git | Unresolved at audited revision; do not redistribute without permission | kiki-chii, shikaku-nara, antigravity | 120f64f6ca | Pilih komponen animasi UI yang bisa disunting dan diuji. |
| 23. cursify | git | Unresolved at audited revision; do not redistribute without permission | kiki-chii, shikaku-nara, antigravity | b3a173c33f | Pilih efek kursor React/Next.js bila menambah nilai interaksi. |
| 24. strix | git | Apache-2.0 | shikaku-nara | e05948080b | Tinjau keamanan aplikasi hanya pada target dan metode yang telah diotorisasi. |
| 25. cybersecurity-library | git | Apache-2.0 | shikaku-nara | 54a798831d | Cari satu playbook sesuai hardening, forensik, deteksi atau audit. |
| 26. reverse-engineer-anything | git | MIT | shikaku-nara | e762e32afb | Rujuk alur pemeriksaan artefak pada scope yang disetujui. |
| 27. rea | git | MIT | shikaku | a8527d43b8 | Coder investigates authorized local JavaScript/apps/artifacts; native engines require existing supported provider. |
| 28. unlimited-ocr-2 | model-card | MIT according to official model card | all | model-card | Baca PDF scan/buku/gambar panjang dalam jendela halaman, simpan jejak halaman. |
| 29. unlimited-ocr | git | MIT | all | 64e6f06602 | Jalankan pipeline OCR untuk model yang sesuai versi dokumentasinya. |
| 30. tokentracker | git | MIT | all | fba54de8e8 | Ambil perkiraan pemakaian token dan biaya dari runtime yang didukung. |
| 31. token-monitor | git | MIT | all | 43e21135d9 | Gunakan data biaya atau aktivitas sesi sebagai masukan meter lokal. |
| 32. hermes-jev-skills | git | MIT | all | 8316358bf6 | Pilih kemampuan skill selection hanya bila versi host mendukung dan pengguna mengaktifkan. |
| 33. cli-anything | git | Apache-2.0 | all | 34f519533b | Cari harness resmi yang cocok, lalu rencanakan perintah dan jalur kerja. |
| 34. cli-anything-catalog | registry-site | External registry terms; no blanket sublicense | all | registry-site | Temukan harness dan dokumentasi upstream, kemudian tinjau commit dan lisensinya. |
| 35. gpt-researcher | git | Apache-2.0 | val | ddd4db3620 | Susun riset mendalam dengan pencarian, ekstraksi dan daftar sumber. |
| 36. remote-jobs | git | ISC (project), MIT (Cube Boilerplate), SIL OFL (fonts) | yukino, shizuka, val, kiki-chii, shikaku | 155939ad93 | Cari perusahaan remote, lalu verifikasi lowongan aktif di laman resmi perusahaan. |
| 37. caveman | git | Apache-2.0 | all | 3dc497a7f8 | Skill only. Proxy, model Auto routing and paid memory compression are excluded. |
| 38. hyperframes | git | Apache-2.0 | kiki-chii, shikaku-nara | 3ad7611f9f | Nine published skills. Pro-only features remain account-dependent. |
| 39. ui-ux-pro-max | git | MIT | kiki-chii, shikaku-nara | 6ae86f61f5 | Local BM25 scripts and curated data are stored outside skill scanner roots. |
| 40. anthropic-skills | git | Apache-2.0 for each selected skill | all | 2c5958ecac | Eight selected official skills installed with distinct anthology names. |
| 41. hermes-omnivoice | git | Apache-2.0 declared by pyproject.toml; no standalone LICENSE | all | 21d2900c39 | Runtime and model weights separate; activate only after local synthesis verification. |
| 42. hermes-dreaming | git | MIT | all | 21878d3ec8 | Pinned deterministic reporting only. No LLM wake or automatic fact promotion. |
| 43. kat-coder-v2-5-dev | model-card | Apache-2.0 according to official model card | shikaku | 7be56fe773 | Explicit coding subtask only; never replace the primary model. |
| 44. timesfm | git | Apache-2.0 code and selected TimesFM2.5 weights; TimesFM3 weights noncommercial/nonproduction excluded | val | e51928e271 | Data numerik terurut waktu, forecasting dan baseline evaluasi; bukan chatbot atau model provider Hermes. |
| 45. unslop | git | CC-BY-4.0 | kiki-chii, val, shikaku | 97daa3eb36 | Audit dan perbaikan UI bertahap; Kiki arah visual, Val bukti dashboard, Coder implementasi. |
| 46. brag | git | MIT; music and SFX have separate licenses and are not bundled | kiki-chii | 669ab9286a | Video peluncuran produk berbasis Hyperframes dengan Concepting First dan review manusia. |
| 47. scrapling | git | BSD-3-Clause | val, shikaku | 3a4bb5b0a0 | Ekstraksi CSS/XPath dari HTML lokal dalam runtime parser terisolasi. |
| 48. harness2 | git | Apache-2.0 | yukino, shizuka, val, kiki-chii, shikaku | 6868817518 | Kelima bot dapat mengusulkan evaluasi harness sesuai konteks; demo deterministik dan promosi perubahan tetap terpisah. |
| 49. career-ops | git | MIT; employers data CC-BY-4.0 | yukino, shizuka, val, kiki-chii, shikaku | c687a6f89a | Bantu strategi karier, CV/JD, skor kecocokan 1-5, tracker dan wawancara saat diminta. |
| 50. mattpocock-skills | git | MIT | yukino, shizuka, val, kiki-chii, shikaku | 5863806dd4 | Pilih disiplin engineering/TDD/domain model saat konteks sesuai; orkestrator dan publikasi tetap dipanggil eksplisit. |
| 51. rea-video | git | Apache-2.0 | kiki-chii | 820d661e80 | Bedah video referensi per shot ke VIDEO.md dan rencana pembuatan ulang dengan review Kiki. |
| 52. grim-prompter | git | MIT | shikaku | 2a94457c7b | Susun threat model berbasis bukti (36 arsitektur, 29 metode, STRIDE/PASTA/LINDDUN, dan privasi GDPR/CCPA) secara read-only pada repositori yang dipilih. |
| 53. claude-bughunter | git | MIT (code); CC-BY-4.0 (documentation and skill content) | shikaku | 8258d29726 | Audit kerentanan, triage, validasi bukti, dan pelaporan keamanan terotorisasi (83 skill, 15 command, 681 pola laporan, 433 laporan terungkap bersitasi terverifikasi) pada aset milik sendiri, program bug bounty in-scope, atau lab/CTF berizin. |
| 54. imagination-studio | git | Apache-2.0 (credit Keys github.com/drowzeys & Sam Wasserman / Wasserman Productions); ships no model weights | kiki-chii | 16f00b462a | Opsional untuk Kiki-Chii (Filmmaker/Content Creator): perencanaan Slate dan antrean render lokal (gambar, klip video+suara, voice, musik, SFX) via plugin Hermes atau stdio MCP pada 127.0.0.1:7870 setelah Concepting First. |
| 55. spacewise | git | MIT | yukino, shizuka, val, kiki-chii, shikaku | 8e4f39aa49 | Bersihkan ruang penyimpanan secara lokal (duplikat, installer sisa, foto mirip/buram, laporan file besar) dengan pratinjau lokal dan gerbang persetujuan manusia. |
| 56. sharewise | git | MIT | yukino, shizuka, val, kiki-chii, shikaku | dd82698f25 | Periksa metadata sensitif foto/video sebelum dibagikan (laporan ya/tidak tanpa membocorkan nilai) dan buat salinan bersih dengan redaksi piksel. |
| 57. ossu-computer-science | git | MIT | yukino, shizuka, val, kiki-chii, shikaku | 8f8272b1d3 | Koneksi langsung ke Universitas Computer Science Open-Source OSSU (Intro CS, Core CS, Advanced CS, Final Project) agar mahasiswa dapat membuka materi dasar CS dan belajar bertahap lewat Hermes. |
| 58. chalk | git | MIT | yukino, shizuka, val, kiki-chii, shikaku | 694af892f3 | Mengajar konsep secara visual di papan tulis Hermes Desktop (diagram, flow, grafik, persamaan, sketsa) + narasi TTS pengguna. |
| 59. codecoach | git | MIT | shikaku, shizuka | 68cbfb6a78 | Belajar coding langkah demi langkah (C/C++/Python/JS/Rust/Go/dll.) di sandbox bubblewrap pada Linux/WSL2; pada Windows native fallback otomatis ke tutor coding interaktif Shikaku. |
| 60. learnloop | git | AGPL-3.0-only | shizuka, yukino | fdcf3d1acf | Pelajaran terstruktur probe -> plan -> teach -> practice (hint ladder + knowledge graph) di dalam Hermes. |
| 61. hermes-researcher | git | MIT | val | e19cb3e20f | Inspirasi arsitektur pipeline riset 10 tahap (Quick/Standard/Deep, adequacy gate, devil's advocate, audit klaim & sitasi, quality gate) pada skill Val `riset-mendalam-nusantara-global`. |
| 62. peditx-research-methodology | git | NOASSERTION (unlicensed; 0 text copied) | val | c9226f37c1 | Referensi taksonomi topik metodologi umum saja (0 teks disalin); skill Val `riset-mendalam-nusantara-global` ditulis 100% orisinal khusus standar Indonesia & global. |
| 63. rust-anything | git | MIT | shikaku | 584e638884 | Migrasi dan porting bertahap kode TS/JS/Python/C/Go/Ruby/Java ke Rust dengan rekaman ground-truth, diff, benchmark, shadow, dan gate kelulusan khusus Shikaku. |
| 64. lemo-opuscar | git | MIT (code); CC-BY-NC-4.0 with film-making permission (docs); CC-BY-4.0 (demo films/pictures); third-party marks/Clawd excluded | kiki-chii | f9e2042939 | Katalog 15 kategori & 99 gaya film pendek berbasis kode untuk Kiki-Chii (baca 1 STYLE.md on-demand dari cache terpin; Concepting First + review manusia). |

# 12. Identitas Versi, Manifest Sumber, Checklist Serah Terima & Dukungan

Bab penutup ini memuat identitas kriptografis sumber publik yang menjadi dasar penyusunan modul ini, urutan rujukan kebenaran jika terjadi perbedaan di masa mendatang, checklist serah terima 6 langkah bagi klien, serta tautan resmi repositori dan dukungan pengembangan open-source.

| Identitas Modul | Nilai Terverifikasi Edisi Ini |
| --- | --- |
| Versi Paket (VERSION.json) | v3.1.2 (release, MIT License) |
| Tanggal Edisi Modul Lengkap | Minggu, 22 November 2026 (Asia/Jakarta) |
| Baseline Commit GitHub | f400fbabf2e74638a443b1d51620d90e43c536e7 |
| SHA-256 Source Manifest (payload) | 83f2a315daf8d4dd389bace6a4f23198dcdec5bb9e67d29fdc73f22caf9c9bf9 |
| SHA-256 Berkas source-manifest.json | 2819c822433cedb1d444dc2c03317d7194e348e9fce940ce7719829dd093d3b0 |
| Jumlah Berkas Terindeks di Manifest | 320 berkas publik (scripts, configs, skills, optional, hermes_plugins, root) |
| Inventaris Terverifikasi | 75 skill bundel (53 inti + 22 wrapper), 2 opsional, 64 upstream, 7 plugin, 39 keluarga CLI (109 node) |
| Cakupan & Kejujuran Bukti | Seluruh fakta diambil langsung dari source & parser commit ini; status akun, kuota model, dan runtime perangkat diverifikasi terpisah di perangkat pengguna. |

## Urutan Rujukan Kebenaran & Checklist Serah Terima Klien (6 Langkah)

- Urutan Rujukan Saat Ada Perbedaan: (1) Output --help & source implementasi pada commit terpasang -> (2) VERSION.json, bot_role_and_skill_matrix.json, & msshi_cognitive_system.json -> (3) Receipt privat di perangkat pengguna -> (4) Dokumen historis/roadmap sebagai konteks.
- Langkah 1: Buka Hermes Desktop/CLI dan atur sendiri Provider, Model AI, Endpoint/Base URL, dan API Key pada setiap profil aktif.
- Langkah 2: (Opsional Multi-Model) Atur Advisor (Yukino/Shizuka) & Dewan (Val/Kiki-Chii/Shikaku) di Settings Hermes agar status interaksi menjadi HEALTHY.
- Langkah 3: Jalankan msshi doctor & msshi system status di terminal (0 kredit AI) — pastikan Skills Parity: True dan Provider/Model Lock: True.
- Langkah 4: Tutup sesi lama dan mulai New Chat di Hermes agar plugin msshi_find_skill, msshi-interaction v0.2.0, dan MSSHITrim termuat penuh.
- Langkah 5: Uji pencarian lokal 0 kredit: msshi find "skripsi" & msshi system route --task "...".
- Langkah 6: Tarik cache sumber (msshi integrations source --name <x> --fetch) hanya saat benar-benar dibutuhkan agar disk tetap ramping.

> **Repositori Resmi & Dukungan Pengembangan Open-Source**
> - • Repositori Resmi MSSHI (MIT License): https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya
> - • Dokumentasi Resmi Hermes Agent: https://hermes-agent.nousresearch.com/
> - • Dukung Pengembangan via Saweria: https://saweria.co/muzas — Proyek inti MSSHI tetap 100% open-source (MIT); dukungan sukarela membantu riset berkelanjutan, audit keamanan upstream, dan pembaruan rutin.
