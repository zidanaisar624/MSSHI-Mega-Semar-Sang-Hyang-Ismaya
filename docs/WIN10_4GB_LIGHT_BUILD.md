# MSSHI Windows 10 RAM 4 GB — Light Build & Low-RAM Guide

Panduan teknis untuk membangun, memasang, dan mengoperasikan **MSSHI v3.1.2 (Light Build)** secara ringan pada perangkat **Windows 10 spesifikasi rendah** (kelas referensi **HP 14s-dq3110TU**, Intel Celeron N4500, RAM 4 GB, NVMe 256 GB, drive tunggal `C:`-only, Windows PowerShell 5.1 bawaan, tanpa WSL2, tanpa Docker, dan tanpa kewajiban Obsidian).

> **Catatan Kejujuran Sertifikasi Hardware**: Target penerimaan di bawah ini telah diverifikasi secara otomatis pada lingkungan pengembangan/uji sintetis offline (`certified_for_win10_4gb: false` sampai seluruh Matriks Validasi Hardware Riil di bagian akhir dokumen ini dijalankan pada unit fisik Windows 10 RAM 4 GB).

---

## 1. Angka Anggaran & Target Penerimaan (Acceptance Targets)

Seluruh optimasi didefinisikan secara eksplisit di [light_build_manifest.json](../configs/light_build_manifest.json):

- **Ukuran Paket Light Installer**: `<= 50 MB` (berkas ZIP deterministik inti tanpa aset visual besar, PDF panduan massal, notebook Colab, atau cache upstream).
- **Konsumsi RAM Proses Idle**: `<= 150 MB` (`WorkingSet` dan `PrivateMemory` / commit charge proses aktif MSSHI).
- **Kecepatan Skill Scan (`p95`)**: `<= 2.0 detik` (minimal 20 iterasi warm/cold terhadap seluruh 67+ bundled skills dengan manifest cache & invalidasi tertarget).
- **Overhead Startup CLI MSSHI**: `<= 5.0 detik`.
- **Kompatibilitas Penuh Windows 10 & Drive `C:`-Only**:
  - 100% kompatibel **Windows PowerShell 5.1** (tanpa operator PS7 seperti `??`, `&&`, `||`, ternary, atau `-Parallel`).
  - Seluruh path default adaptif terhadap mesin `C:`-only (tanpa hardcode `D:\`, tanpa hak Administrator, aman terhadap spasi/apostrof di path profil pengguna).
  - Preset publik **Academic Mahasiswa** (default instalasi baru) dan **Academic Dosen** utuh 100% tanpa memaksa instalasi Obsidian, Docker, atau WSL2.
- **100% Model-Agnostic & User-Agnostic**:
  - Tidak ada nama model AI tertentu, API key, token, atau path pribadi yang ditulis ke preset publik, `SOUL.md`, installer, maupun konfigurasi mode Low-RAM.
  - Arsitektur **2 Tipe Interaksi Bot** (Tipe 1: Main + Sub-Agent Advisor pada `yukino` & `shizuka`; Tipe 2: Main + Dewan MoA `[Ref + Aggregator]` pada `shikaku`, `val`, `kiki-chii`) tetap terjaga penuh pada mode normal, dan dilengkapi pagar aman sekuensial pada mode `light`.

---

## 2. Batas Bundel Inti vs Modul Berat Opsional

Manifes [light_build_manifest.json](../configs/light_build_manifest.json) memisahkan komponen wajib dari aset berat yang diambil sesuai permintaan (*on-demand / lazy fetch*):

- **Disertakan di Light Build Core**:
  - `scripts/` (CLI, runtime, doctor, forge, skill indexer, light packager, academic & skripsi builders; mengecualikan test suite & generator PDF/aset).
  - `configs/` (matriks peran & skill, preset Academic Mahasiswa & Dosen, bantuan pilihan, manifes Light Build).
  - `skills/` (seluruh 67 bundled skills termasuk `muza-skripsi-template` dan `cli-anything-universal-bridge`).
  - `hermes_plugins/` (`msshi-auto-trim`, `msshi-interaction`, dan `msshi-team-routing`).
  - `templates/`, `business-sage/`, `docs/manuals/pdf_catalog.json`, `optional/manifest.json`, dan skrip peluncur root (`install.ps1`, `install.sh`, `*.bat`, `VERSION.json`).
  - Marker rilis `configs/light_build_active.json` yang menandai instalasi Light Build agar `msshi doctor` dan `msshi manual` tidak memicu kesalahan palsu atau unduhan otomatis.
- **Ditunda (On-Demand / Lazy Fetch)**:
  - **Cache Upstream (51 sumber)**: ambil terpisah saat dibutuhkan via `msshi update` (di luar folder `skills/`).
  - **Buku Panduan PDF Lengkap**: unduh sesuai permintaan dengan verifikasi SHA-256 via `msshi manual download --version latest`.
  - **Aset Visual Resolusi Tinggi (`assets/`) & Notebook Colab (`notebooks/`)**: tersedia di repositori lengkap apabila dibutuhkan.
  - **Runtime Berat Lokal** (Hyperframes/Remotion video render, TimesFM weights, OCR lokal berat, OmniVoice weights, REA npm runtime): tidak pernah dipasang otomatis pada Light Build.

---

## 3. Cara Instalasi & Perintah CLI Utama

### Instalasi Interaktif (Bebas Pilih Mode Hemat & Drive/Folder Mana Saja)

Saat menjalankan `.\install.ps1` (atau klik ganda `MULAI_DI_SINI_PEMULA.bat`), pemasang akan menanyakan secara interaktif:
1. **Mode Instalasi**: `1. Standar / Lengkap` atau `2. Mode Hemat Windows 10 RAM 4 GB (Light Build <= 50 MB + Low-RAM)` (otomatis menyarankan `2` bila RAM `<= 6 GB`, namun pengguna di perangkat apa pun bebas memilih `1` atau `2`).
2. **Lokasi Direktori Instalasi Bebas**: tidak terkunci di drive `C:` atau `D:` — Anda bebas memilih drive mana saja (`C:\MSSHI`, `D:\MSSHI`, `E:\Tools\MSSHI`, `F:\MSSHI`, SSD eksternal, atau folder Linux/macOS mana pun) beserta lokasi `HERMES_HOME` pilihan.

### Instalasi Light Build + Low-RAM via Parameter Langsung (Windows PowerShell 5.1)

```powershell
# Contoh 1: Instalasi otomatis Mode Hemat ke folder default adaptif
.\install.ps1 -SourcePath . -Light -LowRam -Mode academic-mahasiswa -Platform hermes -Yes

# Contoh 2: Instalasi Mode Hemat ke drive/folder bebas pilihan Anda (misalnya drive E:\)
.\install.ps1 -SourcePath . -Light -LowRam -InstallDir "E:\MSSHI" -HermesHome "E:\HermesData" -Mode academic-mahasiswa -Platform hermes -Yes

# Contoh 3: Interaktif penuh dari GitHub (pilih Standar/Hemat + ketik drive/folder bebas)
.\install.ps1
```

### Instalasi Light Build + Low-RAM (Bash / macOS / Linux)

```sh
sh install.sh --source-dir . --light --low-ram --install-dir "$HOME/MSSHI" --hermes-home "$HOME/HermesData" --mode academic-mahasiswa --platform hermes --yes
```

### Subperintah `msshi light`

```powershell
# 1. Periksa status hardware, mode resource aktif, memori proses, & fallback CLI (read-only)
msshi light status --json

# 2. Preview lalu aktifkan mode Low-RAM secara eksplisit (atomik + rollback receipt, 0 sentuhan ke config.yaml/SOUL.md)
msshi light mode --set auto --json
msshi light mode --set light --apply --json

# 3. Bangun / segarkan cache indeks skill lazy per profil
msshi light index --json

# 4. Bangun artefak Light Installer ZIP deterministik (otomatis menolak jika > 50 MB)
msshi light build --output .\dist\msshi-light-v3.1.2.zip --manifest .\dist\msshi-light-v3.1.2.manifest.json --json

# 5. Jalankan benchmark offline (no_msshi vs light vs full, 0 LLM calls, 0 jaringan)
msshi light benchmark --iterations 25 --json

# 6. Tampilkan perintah fallback Hermes CLI beserta batasan UI-nya
msshi light cli-fallback --json
msshi desktop --prefer-cli
```

### Integrasi `msshi doctor` dan `msshi forge`

- `msshi doctor` / `msshi doctor --json` sekarang melaporkan blok `low_ram_diagnostics` secara read-only: deteksi RAM perangkat (`<= 6.0 GiB`), ruang kosong drive target (`C:` adaptif), status `build_profile` (`light` vs `full`), status `resource_profile`, konsumsi memori proses (`WorkingSet` & `Commit` vs anggaran `<= 150 MB`), ukuran cache indeks skill, uji cepat skill scan `p95` (`20` iterasi vs `<= 2.0 s`), serta peringatan kebersihan (`SKILL_SCAN_HYGIENE_WARNING`) jika ada folder berat terselip di dalam `skills/`.
- `msshi doctor --fix` tetap aman: hanya memulihkan berkas milik MSSHI yang memiliki bukti kepemilikan/receipt; tidak pernah menyentuh `SOUL.md`, `config.yaml`, `.env`, `auth.json`, atau edit kustom pengguna.
- `msshi forge` memakai lazy skill indexer saat membaca roster, menyertakan status `resource_profile` / `low_ram_mode` (`single_active_runtime_advised`), dan menyegarkan cache indeks profil baru saat `--apply`.

---

## 4. Mode Low-RAM (`resource-profile.json`) & Fast Skill Scanner

### Perilaku Mode Low-RAM

Disimpan secara atomik (dengan rollback receipt) pada `<HERMES_HOME>/msshi-runtime/resource-profile.json` tanpa menyentuh `config.yaml`, `.env`, `auth.json`, ataupun `SOUL.md`:

- **Auto-detect**: jika RAM fisik `<= 6.0 GiB`, `msshi light mode --set auto` dan `msshi setup` interaktif merekomendasikan profil `light`.
- **Single Active Runtime & Batas Konkurensi**:
  - `single_active_bot_runtime: true`, `lazy_bot_spawn: true` (bot dijalankan sesuai permintaan, bukan memuat 5 proses bot sekaligus ke RAM).
  - `max_active_inference: 1`, `max_active_jobs: 1`, `max_browser_tabs: 1`, `max_writer_or_render_subprocesses: 1`.
  - `background_file_watcher: false`, `memory_cache_max_mb: 16`, `auto_open_on_boot: false`.
- **Pagar Plugin Interaksi (`msshi-interaction`)**:
  - Saat `profile == "light"`, putaran MoA paralel (`council_round`) dan delegasi paralel (`advisor`) diblokir secara eksplisit (`LIGHT_MODE_MOA_DISABLED` / `LIGHT_MODE_PARALLEL_DELEGATION_DISABLED`) dan digantikan jalur sekuensial satu inferensi agar tidak memicu lonjakan memori/proses paralel.
- **Pagar Runtime Dispatcher (`msshi-runtime`)**:
  - Target aplikasi grafis/render berat (`blender`, `blender-cli`, `obs`, `cadcraft`, `solidcraft`, `materialcraft`, `texturecraft`, `filmcraft`, `effectcraft`, `anicraft`) ditolak saat profil `light` aktif.

### Fast Skill Scanner (`scripts/msshi_skill_index.py`)

- Memindai folder skill memakai `os.scandir` berbasis metadata `stat()` (`mtime_ns` dan `size`) dengan cache JSON per profil di `<HERMES_HOME>/msshi-runtime/skill-index/<profile>.json`.
- Pada *cache hit*, tidak ada satu pun file `SKILL.md` yang dibuka dari disk (0 read I/O pada file skill).
- Pada *cache miss* (skill baru, diubah, atau pertama kali), hanya membaca maksimal `4096 byte` awal untuk mengekstrak `name`, `description`, dan `head_sha256` frontmatter. Isi penuh `SKILL.md` dan `references/` dimuat secara *lazy* hanya ketika diminta (`load_skill_content`).
- Invalidasi bersifat tertarget: menambah, menyunting, atau menghapus satu skill hanya memproses ulang skill tersebut.
- Direktori berat yang selalu dilewati: `.git`, `node_modules`, `model`, `models`, `checkpoint`, `checkpoints`, `video`, `videos`, `eval`, `evals`, `cache`, `.cache`, `venv`, `.venv`, `__pycache__`, `upstreams`, dan `context-sources`.

---

## 5. Panduan Fallback Hermes CLI & Batasan UI

Pada perangkat RAM 4 GB, proses renderer Chromium/Electron milik Hermes Desktop dapat mengambil porsi besar dari RAM fisik. MSSHI menyediakan jalur fallback CLI resmi tanpa mengubah instalasi Hermes host:

```powershell
# Cek perintah dan batasan UI tanpa membuka Desktop
msshi desktop --prefer-cli

# Mulai sesi interaktif langsung via Hermes CLI (hemat RAM)
hermes --home "<HERMES_HOME>" chat

# Audit rutin, indeks skill, dan status plugin tanpa GUI
msshi doctor --json
msshi light status --json
msshi trim --status --profile default
msshi interaction --status
```

**Batasan UI Eksplisit pada Mode Fallback CLI**:
- Tidak ada antarmuka grafis Electron/Chromium, sidebar visual, maupun tombol klik ganti profil.
- Tidak ada panel pratinjau gambar, video, atau HTML tertanam (hasil dibuka di berkas lokal terpisah bila diperlukan).
- Perpindahan profil dilakukan secara eksplisit lewat argumen CLI.
- Paket host Hermes merupakan proyek upstream terpisah dan **tidak pernah dimodifikasi secara diam-diam oleh MSSHI**.

---

## 6. Proposal Upstream Hermes PR (Untuk Optimasi Host Tanpa Mutasi Diam-Diam)

Karena MSSHI menjaga batas ketat untuk tidak mem-patch kode instalasi Hermes host secara diam-diam, dua perbaikan memori berikut diusulkan sebagai kontribusi resmi ke repositori upstream Hermes Agent:

1. **PR #1 — Lazy Plugin Discovery & Deferred Schema Import**:
   - *Masalah*: Saat startup, pemuatan eager seluruh modul plugin beserta dependensi opsionalnya meningkatkan baseline RSS/WorkingSet Python dan memperlambat waktu mulai pada CPU Celeron N4500.
   - *Usulan*: Indeks metadata `plugin.yaml` terlebih dahulu secara *stat-first*, impor `__init__.py` hanya untuk plugin yang berstatus `enabled` pada profil aktif, dan sediakan opsi `HERMES_LAZY_PLUGINS=1`.
   - *Dampak yang diharapkan*: Mengurangi RAM idle gateway dan waktu startup dingin pada perangkat `<= 4 GB` tanpa mengubah perilaku plugin yang aktif.
2. **PR #2 — Electron Desktop Low-Memory Profile & Cache Cap**:
   - *Masalah*: Chromium disk/GPU shader cache dan beberapa renderer background pada Hermes Desktop dapat dengan cepat menghabiskan sisa RAM pada Windows 10 4 GB.
   - *Usulan*: Tambahkan flag resmi `--low-memory` (atau deteksi otomatis RAM `<= 6 GB`) yang meneruskan pembatasan cache Chromium (`--disk-cache-size`, menonaktifkan pre-render tab tersembunyi, serta menawarkan tombol cepat *Switch to CLI* bila memori sistem kritis).
   - *Dampak yang diharapkan*: Mencegah thrashing pagefile pada laptop 4 GB NVMe sekaligus tetap menjaga pengalaman Desktop bagi pengguna perangkat berspesifikasi lebih tinggi.

---

## 7. Matriks Validasi Hardware Riil (Windows 10 RAM 4 GB)

Sebelum mendeklarasikan sertifikasi penuh pada laptop kelas **HP 14s-dq3110TU (Celeron N4500, 4 GB RAM, 256 GB NVMe, Windows 10, `C:`-only, PowerShell 5.1)**, jalankan daftar cek berikut pada unit fisik:

1. **Instalasi Bersih PowerShell 5.1 (`C:`-only, Non-Admin)**:
   - Jalankan `.\install.ps1 -Light -LowRam -Mode academic-mahasiswa -Platform hermes -Yes` pada akun standar Windows 10 tanpa drive `D:\` dan dengan nama folder pengguna mengandung spasi.
   - Pastikan ukuran unduhan awal `<= 50 MB` dan seluruh path terbentuk di `C:\Users\<User>\AppData\Local\...` tanpa error izin.
2. **Uji Kecepatan Skill Scan di NVMe Celeron N4500**:
   - Jalankan `msshi light benchmark --iterations 25 --json` dan `msshi doctor --json`.
   - Verifikasi `warm_p95_seconds <= 2.0` detik dan status `HEALTHY` (exit code `0`).
3. **Uji Konsumsi RAM Idle Nyata (Task Manager / `Get-Process`)**:
   - Ukur `WorkingSet64` dan `PrivateMemorySize64` proses aktif MSSHI dalam kondisi standby selama 5 menit; verifikasi `<= 150 MB`.
4. **Uji Mode Fallback CLI & Ketahanan Memori**:
   - Uji alur kerja penuh Academic Mahasiswa (pembuatan draf, `msshi skripsi`, `msshi trim`, `msshi interaction --status`) menggunakan `hermes --home ... chat` tanpa lonjakan pagefile berlebih.
5. **Uji Pemulihan & Keamanan**:
   - Uji simulasi ruang disk rendah, eksekusi offline, dan `msshi doctor --fix` untuk memastikan file kustom dan `SOUL.md` tidak pernah tertimpa.

Lihat pula panduan perintah lengkap di [CLI.md](CLI.md).
