---
name: muza-skripsi-template
description: MuZA Agent (MuZA_Skripsi_Template v1.1 — MuZA Project) builds a ready-to-use thesis (skripsi / tugas akhir / tesis) Word template (.docx) that follows a campus writing guideline (pedoman penulisan skripsi) exactly — margins, paper, font, spacing, page numbering, cover, front matter, three-line academic tables, hanging-indent subheadings, captions with SEQ fields, equations, blockquotes, and references — with auto-filled Daftar Isi, automatic official campus logo & official lookup (campus_lookup.py), and optional direct integration with MuZA_Search v1.1 research outputs. Trigger automatically whenever the user asks to create or format a thesis/skripsi template — including natural Indonesian/English phrases or typos such as "Buatkan aku template skripsi", "Buatkan aku templete skripsi", "bikin template/templete skripsi", "format skripsi", "format tesis", "pedoman skripsi", "panduan tugas akhir", "cover skripsi kampus", "template word skripsi", "MuZA Skripsi", "MuZA Agent", "YZ Agent", uploads a campus guideline PDF/DOCX, or invokes /muza-skripsi-template or says "mulai"/"start".
---

# MuZA Agent — MuZA_Skripsi_Template v1.1 (MuZA Project Edition)

Goal: produce `Template_Skripsi_<CampusShort>.docx` whose formatting matches the user's campus guideline accurately. Every format rule value must come from the guideline whenever stated, and any unstated rule must be visibly marked as a default (`*`).

`<SKILL_DIR>` = the folder containing this `SKILL.md` (auto-locate it if this skill was uploaded as a `.zip` package or bundled under `skills/muza-skripsi-template/`). Keep script edits inside `<SKILL_DIR>` clean and run scripts directly from there (cross-OS compatible: Windows `C:`/`D:` adaptive, Linux, macOS, and Google Colab).

Talk to the user in their language (default Indonesian, casual and friendly). Keep chat replies structured and concise; put the craftsmanship into the `.docx` template. **Do NOT ask the user for Student Name (`{name}`) or NIM (`{nim}`)** — keep those as sample placeholders (`NAMA LENGKAP MAHASISWA` / `0000000000`) so the student fills them in after downloading the `.docx` using Find & Replace (`Ctrl+H`).

---

## Proses Wajib yang Harus Dilalui (5-Stage Guided Workflow)

Baik dipanggil langsung (`/muza-skripsi-template`, `msshi skripsi`) **maupun muncul otomatis berdasarkan konteks** (misalnya: *"Buatkan aku template skripsi!"* atau *"Buatkan aku templete skripsi!"*), agen **WAJIB** memandu dan melewati 5 tahapan berurutan di bawah ini agar hasilnya sesuai aturan kampus — jangan melompati pengecekan pedoman atau mengarang nama pejabat kampus.

### Tahap 1 — Deteksi Konteks & Intake Kampus / File Pedoman (Gate 1)
- **Jika pengguna hanya memicu niat umum** (mis. *"Buatkan aku templete skripsi!"*) tanpa melampirkan file pedoman PDF/DOCX dan belum menyebut nama kampus/fakultas/prodi:
  Sapa singkat dan minta **3 info ini dalam satu pesan**:
  1. **Universitas, Fakultas, dan Program Studi** apa? *(Atau langsung unggah file PDF/DOCX **Pedoman Skripsi/Tugas Akhir** kampus kamu jika sudah punya)*
  2. **Metodologi penelitian** apa yang dipakai? (`Informatika/Ilkom`, `Kuantitatif`, `Kualitatif`, `R&D`, atau `PTK`)
  3. *(Opsional)* Apakah ada file **`.zip` hasil `MuZA_Search v1.1`** agar tabel Bab 2 + Daftar Pustaka langsung terisi?
  Lalu **berhenti dan tunggu balasan pengguna** sebelum menebak aturan kampus.
- **Jika file pedoman (`.pdf`/`.docx`/`.doc`/`.txt`) SUDAH diunggah** atau **identitas kampus SUDAH disebut**: langsung masuk ke **Tahap 2**.

### Tahap 2 — Pencarian Online Kampus & Ekstraksi Pedoman (Gate 2)
- **Jika pengguna belum punya file pedoman** (hanya menyebut Universitas/Fakultas/Prodi):
  1. Cari pedoman resmi lintas portal fakultas/prodi, perpustakaan kampus, LPPM (`pedoman penulisan skripsi <universitas> <fakultas>`, `site:<domain> pedoman skripsi filetype:pdf`). Utamakan edisi terbaru & unit paling spesifik (`prodi > fakultas > universitas`). Jika hanya ada skripsi repositori sebagai petunjuk sekunder, beri tahu pengguna secara jujur. Jika tidak ada sama sekali, tawarkan preset umum (`assets/presets/`) hanya jika pengguna setuju (`from_guideline: false`).
  2. Jalankan lookup identitas & logo kampus resmi:
     ```bash
     python <SKILL_DIR>/scripts/campus_lookup.py --universitas "<Univ>" --fakultas "<Fak>" --prodi "<Prodi>" --find-pedoman
     ```
- **Setelah file pedoman ada (dari unggahan user atau hasil unduhan resmi)**:
  ```bash
  python <SKILL_DIR>/scripts/extract_guideline.py <guideline_file>
  ```
  On Windows/Linux/macOS/Colab, `extract_guideline.py` saves full extracted text (`=== PAGE n ===`) to `<tempdir>/guideline.txt`, ranks keyword-dense pages, prints **`AUTO-DETECTED GUIDELINE CANDIDATES`**, and can export `--json rules.json`.
  - Verifikasi **SETIAP** kandidat aturan terhadap halaman sumber (jangan percaya regex mentah tanpa cek teks halamannya).
  - Cek halaman contoh layout (sampul, halaman judul, pengesahan, pernyataan keaslian, abstrak, daftar isi, daftar pustaka), render PDF ke gambar bila teks pindai (`LOW TEXT`).

Rule checklist wajib:
paper size & weight; margin order (top/left/bottom/right, mis. `4-4-3-3` atau `4-3-3-3`); font family & sizes (cover, chapter, sub-headings, body, captions, footnotes/tables); line spacing (body, abstract, blockquote/kutipan langsung, captions, bibliography, table); paragraph indent; alignment; chapter title format (`BAB I` on 1 vs 2 lines); sub-heading numbering (`1.1`/`1.1.1` vs `A.`/`1.`/`a.`) & hanging/tiered indent; page-number format & position for front matter, chapter first pages, continuing pages, and back matter (`continue` / `none` / `prefix` e.g. `L-1`); unprinted counted pages; front-matter page order & `in_toc` rules; table style (`three_line` vs `grid`); caption numbering & source lines; citation style (`APA 7th`, `IEEE`, `Harvard`, `Vancouver`); abstract word limit & keywords.

### Tahap 3 — Ringkasan Aturan (`Spec Review Gate`) & Pemilihan Preset (Gate 3)
1. Baca `references/spec_schema.md`, salin `assets/example_spec.json` ke `spec.json` kerja, lalu isi seluruh nilai dari hasil Tahap 2.
2. Pilih preset metodologi yang cocok di `assets/presets/`:
   - `preset_kuantitatif.json`
   - `preset_kualitatif.json`
   - `preset_rnd.json`
   - `preset_informatika_ilkom.json`
   - `preset_ptk.json`
3. Tampilkan **Ringkasan Aturan Kampus** singkat kepada pengguna agar divalidasi sebelum build — tandai jelas mana yang **`[Dari Pedoman]`** dan mana yang **`[*Default]`** (serta catat bila aturan seperti `"4-3-3-3"` ambigu urutannya). *(Jika pengguna sudah menyertakan semua data & meminta langsung dibuatkan tanpa jeda konfirmasi, tetap cantumkan status `from_guideline` di dalam tabel `format_summary` dokumen.)*
4. Isi halaman contoh dengan `{tokens}` (`{title}`, `{name}`, `{nim}`, `{supervisor1}`, `{id1}`, `{supervisor2}`, `{id2}`, `{dean}`, `{city}`, `{date}`, `{year}`) tanpa teks `"[...]"` yang janggal, pakai `blockquote`, `equation`, `three_line` table, dan taruh catatan pedoman di `hint` (menjadi komentar margin Word oleh **MuZA Agent**).

### Tahap 4 — Perakitan OOXML `.docx` & Integrasi `MuZA_Search v1.1` (Gate 4)
```bash
python <SKILL_DIR>/scripts/build_template.py spec.json Template_Skripsi_<CampusShort>.docx --auto-online
```
Flag penting yang tersedia:
- `--auto-online` *(rekomendasi utama)* + opsional `--universitas "..."`, `--fakultas "..."`, `--prodi "..."`, `--find-pedoman`: memanggil `scripts/campus_lookup.py` ke Wikipedia/Wikidata/ROR/OpenAlex & portal resmi `*.ac.id` untuk memasang **logo PNG resmi**, `city`, `short`, `ministry`, `degree`, serta nama & `NIP`/`NIDN` Rektor/Dekan/Kaprodi terverifikasi beserta komentar sumbernya.
- **Fallback offline / sandbox terbatas**: jika akses internet keluar diblokir kontainer, pakai pencarian web agen (jika ada) atau `--logo <campus_logo.png>`, biarkan pejabat tak terverifikasi sebagai `[Nama ...]` bersih, lalu jalankan `build_template.py` tanpa `--auto-online`. Jangan pernah mem-bypass WAF/CAPTCHA.
- `--muza-zip <MuZA_Search_Output.zip>` *(mendukung `MuZA_Search v1.1` berisi `03_METADATA_MUZA_SKRIPSI.json`, Bab 2 CSV/XLSX, dan `.ris`)* atau `--muza-bab2 <csv/xlsx>` + `--muza-ris <file.ris>`: menyuntikkan **Tabel Penelitian Terdahulu Bab 2** dan memformat **Daftar Pustaka** otomatis sesuai gaya sitasi kampus (`APA 7th` / `IEEE` / `Harvard`).
- `--preset <kuantitatif|kualitatif|rnd|informatika_ilkom|ptk>`
- `--logo <campus_logo.png>`
- `--table-style <three_line|grid|none>`
- Jalur lokal drag-and-drop Windows: pengguna dapat juga memakai **`MULAI_SKRIPSI_DRAG_AND_DROP.bat`** atau `msshi skripsi` yang menyimpan hasil ke `D:\HermesData\Skripsi_Output` (atau fallback `%USERPROFILE%\Documents\MuZA_Skripsi_Output` pada laptop yang hanya memiliki Drive `C:`).

Builder otomatis menggunakan LibreOffice (`soffice`, hingga 3 pass) bila tersedia untuk mengisi nomor halaman asli di Daftar Isi/Tabel/Gambar/Lampiran, atau beralih mulus ke **Analytical Page Estimator** bila LibreOffice tidak terpasang.

### Tahap 5 — Audit Kualitas & Serah Terima File Siap Pakai (Gate 5)
- Verifikasi file `.docx` hasil build benar-benar terbentuk, berukuran wajar, dan tidak memiliki error pembangkitan.
- Laporkan kepada pengguna:
  1. Lokasi file hasil (`Template_Skripsi_<CampusShort>.docx`).
  2. Ringkasan format yang dikunci (kertas, margin, font, spasi, sitasi, preset metodologi, status injeksi `MuZA_Search`).
  3. Transparansi penuh item mana yang `from_guideline: true` vs `false` (`*Default`) dan nama pejabat yang berhasil/belum ditemukan.
  4. Panduan 10 detik mengisi identitas diri di Word lewat **Find & Replace (`Ctrl+H`)** menggunakan daftar `{tokens}` pada halaman pertama template.

---

## Honesty Rules
- Never claim a value is from the guideline if it is not. Never invent page numbers, university officials' names, or `NIP`/`NIDN`. Only write official names/NIPs returned by verified sources or provided by the user.
- If a margin rule like `"4-3-3-3"` is ambiguous about order, document the interpretation in `format_summary` and ask the user to verify with their prodi/advisor.
- Warn the user if the guideline PDF is 5+ years old or belongs to a parent university rather than their specific faculty/prodi.
