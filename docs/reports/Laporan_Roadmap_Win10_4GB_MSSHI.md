# Laporan Eksekusi Roadmap MSSHI v3.1.2 — Windows 10 RAM 4 GB (Light Build)

- **Tanggal Laporan**: 19 November 2026
- **Baseline Repositori**: `v3.1.2` (commit `3c997aab915352f85d72eea9be8873ddc918c15e`)
- **Branch Isolasi Git**: `feat/win10-4gb-lite-roadmap` (belum di-push ke remote GitHub)
- **Target Perangkat Acuan**: Laptop Windows 10 spesifikasi rendah kelas HP 14s-dq3110TU (Intel Celeron N4500, RAM 4 GB, NVMe 256 GB, single-drive `C:`-only, Windows PowerShell 5.1 bawaan, tanpa WSL2, tanpa Docker, tanpa kewajiban Obsidian)
- **Status Sertifikasi Hardware Riil**: `certified_for_win10_4gb = false` — seluruh pengujian lulus pada lingkungan pengembang & uji sintetis offline; sertifikasi akhir menunggu verifikasi langsung di unit fisik Windows 10 RAM 4 GB sesuai matriks di [WIN10_4GB_LIGHT_BUILD.md](../WIN10_4GB_LIGHT_BUILD.md).

---

## 1. Ringkasan Eksekutif & Status 4 Hard Acceptance Criteria (Before vs After)

Optimasi **MSSHI v3.1.2 Light Build & Low-RAM Edition** telah diimplementasikan secara modular tanpa mengubah arsitektur **2 Tipe Interaksi Bot**, tanpa memodifikasi `VERSION.json` (`3.1.2`, `67` bundled skills = `51` core + `16` wrappers, `51` external sources), dan tanpa menyentuh berkas lokal privat maupun kredensial pengguna.

### Perbandingan Before vs After

| Kriteria Penerimaan | Target Wajib | Baseline (Before — v3.1.2) | Hasil Optimasi (After — Light Build) | Status Uji Lokal/Sintetis |
| :--- | :--- | :--- | :--- | :--- |
| **1. Ukuran Paket Light Installer** | `<= 50 MB` | `28.28 MB` (ZIP v3.1.2) / `32.53 MB` (repo tree) | **`0.741 MB`** (ZIP deterministik) / `2.122 MB` (uncompressed) — turun **97.4%** | **LULUS** |
| **2. Konsumsi RAM Proses Idle** | `<= 150 MB` | `26.30 MB` WorkingSet / `17.94 MB` Commit (CLI) | **`27.92 MB`** WorkingSet / **`16.74 MB`** Commit (`msshi light`); **`30.00 MB`** WS / **`18.74 MB`** Commit (`msshi doctor`) | **LULUS** |
| **3. Kecepatan Skill Scan (`p95`)** | `<= 2.0 detik` (`>= 20` iters, 67+ skills) | `0.0512 s` uncached (`os.walk` penuh, baca semua `SKILL.md`, tanpa filter dir berat) | **`0.0447 s`** p95 warm 67 skills (`25` iters, `67/67` cache hit, `0` baca disk); `0.1095 s` p95 5-profil; `0.0299 s` quick doctor probe | **LULUS** |
| **4. Kompatibilitas Win10 & `C:`-Only** | PS 5.1 + `C:` adaptif, tanpa Obsidian/Docker/WSL2 | `artcraft_root()` hardcode `D:\`; `doctor`/`skripsi_drop` cek `D:\` mentah; wrapper belum pakai `py -3 -B -X utf8` | **0 error AST PowerShell 5.1** (0 sintaks PS7+); seluruh resolver adaptif `C:`-only & aman spasi/apostrof; Academic Mahasiswa & Dosen utuh tanpa Obsidian | **LULUS** |

**Metrik Pendukung Tambahan**:
- **Overhead Startup CLI MSSHI** (`light status` dikurangi no-op Python `0.0690 s`): **`0.2926 s`** (target `<= 5.0 s`).
- **Konsumsi Model & Jaringan pada Uji/Audit**: **`0` LLM calls**, **`0` network requests**, **`0` aplikasi dibuka otomatis** (`auto_open_on_boot: false`).

---

## 2. Temuan Audit Baseline (Fase 1 — Before)

Pengukuran awal pada checkout baseline `v3.1.2` mengidentifikasi empat titik penyumbang ukuran dan bottleneck utama:

1. **10 Berkas & Folder Penyumbang Ukuran Terbesar (Repo Tracked `32.53 MB`, `393` file)**:
   - Folder terbesar: `assets/` (`14.80 MB`), `docs/` (`14.21 MB`), `notebooks/` (`1.08 MB`), `scripts/` (`0.95 MB`), `skills/` (`0.86 MB`), `configs/` (`0.37 MB`), `hermes_plugins/` (`0.06 MB`).
   - 10 berkas terbesar:
     1. `assets/avatars/hero-muza-banner.png` (`5.25 MB`)
     2. `docs/pdf-guides/Laporan_Eksekusi_Hydrogen_MSSHI_v3.1.0_Memeable_dan_Skripsi.pdf` (`5.10 MB`)
     3. `docs/manuals/v3.1.2/Modul_Pelanggan_MSSHI_v3.1.2.pdf` (`3.36 MB`)
     4. `docs/manuals/latest/Modul_Pelanggan_MSSHI_v3.1.2.pdf` (`3.36 MB`)
     5. `assets/interaction-two-types.jpg` (`2.31 MB`)
     6. `assets/showcases/showcase-creative-convergence.png` (`1.55 MB`)
     7. `notebooks/skripsi/MuZA_Skripsi_Builder.ipynb` (`0.64 MB`)
     8. `assets/showcases/showcase-hermes-ecosystem.png` (`0.64 MB`)
     9. `notebooks/skripsi/MuZA_Search.ipynb` (`0.43 MB`)
     10. `docs/manuals/v3.1.1/Modul_Pelanggan_MSSHI_v3.1.1.pdf` (`0.42 MB`)
2. **Pemindaian Skill Tanpa Cache & Tanpa Filter Direktori Berat**: `install_msshi.indexed_skills()` menelusuri direktori dengan `os.walk` dan membuka seluruh `SKILL.md` di setiap pemanggilan tanpa melewati direktori berat (`node_modules`, `.git`, `model`, `checkpoint`, `video`, `eval`, `cache`, `upstreams`).
3. **Belum Ada Pagar Profil Low-RAM**: Belum tersedia sakelar `--low-ram` / auto-detect RAM `<= 6 GB` untuk menonaktifkan MoA/delegasi paralel, membatasi proses tunggal aktif, dan memblokir target aplikasi grafis/render berat pada mesin 4 GB.
4. **Asumsi Drive `D:` & Wrapper Lama**: `artcraft_root()` di `msshi_bridge_runtime.py` mengembalikan `D:/Program/ArtCraft Apps` secara tetap di Windows; `msshi_doctor.py` dan `msshi_skripsi_drop.py` mengecek `Path("D:/").exists()` langsung alih-alih helper `has_writable_drive_d()`; `install_business_sage.ps1` dan `msshi-update.cmd` belum memiliki fallback `py -3` serta bendera `-B -X utf8`.

---

## 3. Daftar Lengkap Berkas yang Dibuat & Diubah

### A. Berkas Baru (8 Berkas)

1. [configs/light_build_manifest.json](../../configs/light_build_manifest.json) — Manifes batas bundel Light Build (`<= 50 MB`), daftar direktori/berkas inti, kategori modul berat yang ditunda (*on-demand*), daftar direktori yang dikecualikan scanner, ambang RAM `6.0 GiB`, batas konkurensi Low-RAM, dan target aplikasi berat yang diblokir saat mode `light`.
2. [scripts/msshi_skill_index.py](../../scripts/msshi_skill_index.py) — Fast Skill Scanner berbasis `os.scandir` *stat-first* dengan manifest cache JSON per profil (`mtime_ns`, `size`, `head_sha256`), batas pembacaan frontmatter `<= 4096 B` saat miss, `0` baca file saat hit, invalidasi tertarget (add/edit/delete), filter & peringatan kebersihan direktori berat, penolakan symlink/junction, serta pemuatan isi/referensi secara *lazy* (`load_skill_content`).
3. [scripts/msshi_light.py](../../scripts/msshi_light.py) — Mesin utama Light Build & CLI `msshi light` (`status`, `mode`, `index`, `build`, `benchmark`, `cli-fallback`), pengukuran memori proses Windows (`K32GetProcessMemoryInfo`), deteksi hardware `<= 6 GB`, penerapan atomik `resource-profile.json` dengan rollback receipt, builder ZIP deterministik (`<= 50 MB`), dan harness benchmark offline (`no_msshi` vs `light` vs `full`).
4. [hermes_plugins/msshi-auto-trim/desktop_ui.js](../../hermes_plugins/msshi-auto-trim/desktop_ui.js) — Permukaan pengaturan Desktop (`Settings > Plugins`) untuk **MSSHITrim** berbasis `@hermes/plugin-sdk` murni (0 LLM/MCP calls) yang selalu muncul dan menyinkronkan pengaturan `MSSHITrim` di seluruh 6 profil bot (`Hermes`, `Kiki-Chii`, `Sir. Robot`, `Sensei Shizuka Hiratsuka`, `Val`, `Yukino Yukinoshita`).
5. [docs/WIN10_4GB_LIGHT_BUILD.md](../WIN10_4GB_LIGHT_BUILD.md) — Dokumentasi teknis Light Build Win10 RAM 4 GB, panduan fallback Hermes CLI & batasan UI, Proposal Upstream Hermes PR (lazy plugin discovery & profil memori rendah Electron), serta Matriks Validasi Hardware Riil.
6. [scripts/tests/test_win10_4gb_lite.py](../../scripts/tests/test_win10_4gb_lite.py) — Suite pengujian otomatis khusus Roadmap Win10 4 GB (14 kasus uji komprehensif termasuk dukungan direktori/drive bebas & pemilihan interaktif Mode Hemat saat instalasi).
7. [docs/reports/Laporan_Roadmap_Win10_4GB_MSSHI.md](Laporan_Roadmap_Win10_4GB_MSSHI.md) — Laporan lengkap eksekusi dalam format Markdown.
8. [docs/reports/Laporan_Roadmap_Win10_4GB_MSSHI.pdf](Laporan_Roadmap_Win10_4GB_MSSHI.pdf) — Versi PDF resmi laporan eksekusi untuk dokumentasi & serah terima.

### B. Berkas yang Dimodifikasi Secara Bedah (21 Berkas)

1. [scripts/install_msshi.py](../../scripts/install_msshi.py) — Integrasi daftar pengecualian direktori berat pada `indexed_skills()` serta dukungan variabel lingkungan `MSSHI_WINDOWS_D_DRIVE` pada `host_roots()`.
2. [skills/cli-anything-universal-bridge/scripts/msshi_bridge_runtime.py](../../skills/cli-anything-universal-bridge/scripts/msshi_bridge_runtime.py) — Perbaikan `artcraft_root()` agar jatuh balik secara aman ke `%LOCALAPPDATA%\ArtCraft Apps` (non-admin) pada mesin Windows `C:`-only.
3. [scripts/msshi_skripsi_drop.py](../../scripts/msshi_skripsi_drop.py) — Peralihan `adaptive_data_home()`, `adaptive_output_dir()`, dan `ensure_pylibs()` agar mendukung direktori/drive bebas (`MSSHI_SKRIPSI_OUTPUT` / `HERMES_HOME` kustom di drive mana saja) serta fallback adaptif `has_writable_drive_d()` / `C:`.
4. [scripts/msshi_manuals.py](../../scripts/msshi_manuals.py) — Pada instalasi Light Build (`configs/light_build_active.json`), menunda penyalinan/unduhan PDF panduan otomatis kecuali pengguna meminta eksplisit (`--download-pdf` / `msshi manual download`).
5. [scripts/msshi_runtime.py](../../scripts/msshi_runtime.py) & salinan sinkron [skills/cli-anything-universal-bridge/scripts/msshi_runtime.py](../../skills/cli-anything-universal-bridge/scripts/msshi_runtime.py) — Penambahan deteksi `low_ram_detected` (`<= 6.0 GiB`) pada `hardware()`, pembacaan `resource-profile.json` di `status()`, pemblokiran target grafis/render berat saat mode `light` pada `ticket()` & `run_target()`, serta pengecekan batas minimal ruang disk kosong (`16 MB`) sebelum membuat tiket.
6. [hermes_plugins/msshi-interaction/__init__.py](../../hermes_plugins/msshi-interaction/__init__.py) — Integrasi sadar mode Low-RAM: tetap mempertahankan murni Arsitektur 2 Tipe pada mode normal; saat `resource-profile.json` bernilai `light`, menonaktifkan MoA/delegasi paralel (`LIGHT_MODE_MOA_DISABLED` / `LIGHT_MODE_PARALLEL_DELEGATION_DISABLED`) dan mengizinkan jalur sekuensial satu inferensi.
7. [scripts/msshi_desktop.py](../../scripts/msshi_desktop.py) — Penambahan opsi `--prefer-cli` untuk menampilkan panduan fallback Hermes CLI & batasan UI tanpa membuka Desktop, serta petunjuk non-blocking saat profil `light` aktif.
8. [scripts/msshi_doctor.py](../../scripts/msshi_doctor.py) — Penambahan blok diagnostik read-only `low_ram_diagnostics` (RAM perangkat, ruang disk, status Light Build/Low-RAM, memori proses `WorkingSet`/`Commit`, ukuran cache indeks, uji cepat skill scan `p95`, dan `SKILL_SCAN_HYGIENE_WARNING`), dukungan Light Build agar notebook Colab opsional tidak menimbulkan error palsu, serta dukungan output Skripsi di drive/folder bebas (`MSSHI_SKRIPSI_OUTPUT` / `HERMES_HOME`) maupun adaptif `C:`-only tanpa mengubah keamanan `doctor --fix`.
9. [scripts/msshi_forge.py](../../scripts/msshi_forge.py) — Penggunaan lazy skill indexer pada `roster()`, pemaparan status `resource_profile`/`low_ram_mode`/`single_active_runtime_advised`, dan penyegaran cache indeks profil baru saat `--apply`.
10. [scripts/msshi_cli.py](../../scripts/msshi_cli.py) — Registrasi subperintah `msshi light`, dukungan `--light` pada `bootstrap` dan `update`, prompt lokasi folder bebas di `choose_targets()`, tahap interaktif `[5/5] Mode Resource Perangkat` (Standar vs Mode Hemat Win10 RAM 4 GB) & flag `--low-ram` / `--resource-profile` pada `setup`, serta penyegaran cache indeks skill setelah setup.
11. [install.ps1](../../install.ps1) — Penambahan parameter `-Light`, `-LowRam`, `-ResourceProfile`, `-InstallDir`, `-HermesHome`, `-TargetDir` beserta prompt interaktif memilih **Mode Standar vs Mode Hemat Windows 10 RAM 4 GB** dan **direktori/drive instalasi bebas (`C:`, `D:`, `E:`, dll.)** dalam 100% sintaks Windows PowerShell 5.1.
12. [install.sh](../../install.sh) — Penambahan opsi `--light`, `--low-ram`, `--resource-profile`, `--install-dir`, `--hermes-home`, `--target-dir` beserta pilihan interaktif mode hemat & direktori bebas + *sparse checkout* ringan.
13. [MULAI_DI_SINI_PEMULA.bat](../../MULAI_DI_SINI_PEMULA.bat) — Penambahan menu langsung untuk pemasangan Standar, Mode Hemat Windows 10 RAM 4 GB (`--low-ram --no-pdf`), input folder instalasi MSSHI bebas, dan pintasan Mode CLI Hemat RAM (`desktop --prefer-cli`).
14. [scripts/installers/install_business_sage.ps1](../../scripts/installers/install_business_sage.ps1) — Penguatan deteksi Python (`py -3` / `python` / `python3`) dengan `-B -X utf8` dalam sintaks PS 5.1.
15. [scripts/msshi-update.cmd](../../scripts/msshi-update.cmd) — Penguatan fallback `py -3 -B -X utf8` ke `python -B -X utf8`.
16. [configs/option_help.json](../../configs/option_help.json) — Penambahan penjelasan dwibahasa (`id` dan `en`) untuk fitur `light-build`.
17. [VERSION.json](../../VERSION.json) — Penambahan `"light"` pada daftar `update_modes` tanpa mengubah nomor versi (`3.1.2`) maupun hitungan skill/upstream.
18. [docs/CLI.md](../CLI.md) — Dokumentasi subperintah `msshi light`, pilihan interaktif mode hemat & direktori bebas, flag `--light`/`--low-ram`/`--resource-profile`, dan `msshi desktop --prefer-cli`.
19. [hermes_plugins/msshi-auto-trim/plugin.yaml](../../hermes_plugins/msshi-auto-trim/plugin.yaml) — Peningkatan ke `manifest_version: 2` dengan label ramah pengguna untuk `MSSHITrim` dan seluruh 5 field `config_schema`.
20. [scripts/msshi_trim_setup.py](../../scripts/msshi_trim_setup.py) & [scripts/tests/test_msshi_trim_install.py](../../scripts/tests/test_msshi_trim_install.py) — Staging otomatis permukaan pengaturan Desktop `MSSHITrim` (`<home>/desktop-plugins/msshi-auto-trim/plugin.js`) beserta pengenalan checksum upgrade v0.2.0 secara aman di seluruh 6 profil bot.

---

## 4. Hasil Lengkap Test Suite, Benchmark & Audit Keamanan (Fase 3)

### A. Ringkasan Eksekusi Pengujian Otomatis

- **Full Offline Unit Test Suite (`unittest discover -s scripts/tests`)**: **200 tests PASS** (`186` baseline v3.1.2 + `14` baru `test_win10_4gb_lite.py`, `0` failures, `0` errors, `1` skipped bawaan).
- **Release Static & Smoke Verification (`scripts/check_release.py --smoke`)**: **PASS** (validasi paritas 67 skills, 51 upstreams, 8 SVG, seluruh tautan markdown lokal, Python 3.10 AST, `render_bot_audit.py --check`, dan smoke install/update).
- **Release Package Checks (`check_release_v3.py --package-only` & `check_release_v31.py --package-only`)**: **PASS_SUCCESS** (`failures = []`).
- **Secret & Privacy Scan (`scripts/secret_scan.py`)**: **PASS** (`findings = 0`, 100% model-agnostic & user-agnostic).
- **PowerShell 5.1 AST & Syntax Lint**: Seluruh berkas `.ps1` repositori lulus `[System.Management.Automation.Language.Parser]::ParseFile` pada Windows PowerShell 5.1 dengan **0 error** dan **0 operator PS7+**.
- **Live Read-Only `msshi doctor --json`**: **`status = HEALTHY`**, **`core_status = HEALTHY`**, **`exit_code = 0`**, **`issues = []`**, **`checks_read_only = true`**.

### B. Ringkasan Angka Benchmark (`msshi_light.py benchmark --iterations 25 --json`)

- **Paket Light ZIP Deterministik**: `0.741 MB` (`777 KB`), uncompressed `2.122 MB` (bandingkan: full source `32.594 MB`, full release ZIP `28.28 MB`).
- **Scan 67 Bundled Skills (`25` iterasi)**:
  - Cold: `0.0436 s`
  - Warm Min: `0.0202 s` | Warm Median: `0.0331 s` | **Warm p95: `0.0447 s`** | Warm Max: `0.0488 s`
  - Cache Hit Rate (warm): `67 / 67` (`100%`, `0` baca file `SKILL.md` dari disk)
- **Scan 5-Profil Academic Mahasiswa (`25` iterasi)**: Cold `0.0532 s`, **Warm p95 `0.1095 s`**.
- **Memori Proses Aktif MSSHI (Windows `K32GetProcessMemoryInfo`)**:
  - `msshi_light.py`: `WorkingSet = 27.92 MB`, `Peak = 28.23 MB`, `Private Commit = 16.74 MB`.
  - `msshi_doctor.py`: `WorkingSet = 30.00–30.70 MB`, `Peak = 30.91 MB`, `Private Commit = 18.74–19.81 MB`.
- **Overhead Startup CLI MSSHI**: `0.2926 s` (`light status` vs baseline no-op Python `0.0690 s`).

---

## 5. Konfirmasi Audit Keamanan Jembatan & Data Lokal (DO NOT TOUCH)

Verifikasi checksum SHA-256 dan stempel waktu (`mtime_ns`) sebelum Fase 1 dan sesudah Fase 3 memastikan seluruh komponen lokal yang dilindungi **100% tidak tersentuh (identik byte-for-byte)**:

| Komponen Lokal Terlindungi | Ukuran (Bytes) | SHA-256 (16 hex awal) | Status Integritas |
| :--- | :--- | :--- | :--- |
| `D:\HermesData\data\bin\nlm.exe` | `47,104` | `2ac01379ea66279e` | Identik (Tidak Tersentuh) |
| `D:\HermesData\data\bin\notebooklm-mcp.exe` | `47,104` | `84b9f623c199eebe` | Identik (Tidak Tersentuh) |
| `D:\HermesData\config.yaml` | `132,587` | `06a8954d7c0e3262` | Identik (Tidak Tersentuh) |
| `D:\HermesData\SOUL.md` | `2,827` | `ea1b8e1453507e22` | Identik (Tidak Tersentuh) |
| `D:\HermesData\profiles\yukino\SOUL.md` | `11,250` | `61f9767dfb275219` | Identik (Tidak Tersentuh) |
| `D:\HermesData\profiles\shizuka\SOUL.md` | `11,120` | `f3210febe26cd896` | Identik (Tidak Tersentuh) |
| `D:\HermesData\profiles\val\SOUL.md` | `13,780` | `f79ef2593dac517c` | Identik (Tidak Tersentuh) |
| `D:\HermesData\profiles\kiki-chii\SOUL.md` | `13,962` | `8293ac23cd4f829f` | Identik (Tidak Tersentuh) |
| `D:\HermesData\profiles\shikaku\SOUL.md` | `14,265` | `0dc6adf61bcd03a8` | Identik (Tidak Tersentuh) |
| `D:\HermesProject\` (Vault Obsidian & sub-folder privat) | Direktori aktif | `mtime_ns = 1794995505330468400` | Identik (Tidak Tersentuh) |
| Konfigurasi `rclone` (`gdrive:`) & `D:\MSSHI\state.json` | Aktif | Tidak dimodifikasi | Identik (Tidak Tersentuh) |

---

## 6. Rekomendasi Langkah Review & Git Commit Sebelum Push

Sesuai prinsip isolasi Git aman, tidak ada `git commit` maupun `git push` otomatis yang dilakukan. Setelah Anda meninjau diff dan laporan ini, jalankan langkah berikut dari root checkout repositori:

```powershell
# 1. Tinjau ulang branch aktif dan ringkasan perubahan
git branch --show-current
git status
git diff --stat

# 2. (Opsional) Bangun artefak uji Light Installer ZIP secara lokal di luar repo
python -B -X utf8 scripts/msshi_light.py build --output "$env:TEMP\msshi-v3.1.2-light.zip" --json

# 3. Stage dan commit perubahan ke branch isolasi feat/win10-4gb-lite-roadmap
git add VERSION.json MULAI_DI_SINI_PEMULA.bat install.ps1 install.sh configs/light_build_manifest.json configs/option_help.json docs/CLI.md docs/WIN10_4GB_LIGHT_BUILD.md docs/reports/Laporan_Roadmap_Win10_4GB_MSSHI.md docs/reports/Laporan_Roadmap_Win10_4GB_MSSHI.pdf hermes_plugins/msshi-interaction/__init__.py scripts/ skills/cli-anything-universal-bridge/scripts/
git commit -m "feat(win10-lite): add Windows 10 4GB Light Build, Low-RAM mode, lazy skill index, and C:-only PS5.1 hardening"

# 4. Setelah siap publikasi, push branch fitur untuk Pull Request / review
git push -u origin feat/win10-4gb-lite-roadmap
```
