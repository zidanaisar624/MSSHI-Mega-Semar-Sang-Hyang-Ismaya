---
name: muza-skripsi-template
description: MuZA Agent (MuZA_Skripsi_Template v1.1 — MuZA Project) builds a ready-to-use thesis (skripsi / tugas akhir / tesis) Word template (.docx) that follows a campus writing guideline (pedoman penulisan skripsi) accurately — margins, paper, font, spacing, page numbering, cover, front matter, three-line academic tables, hanging-indent subheadings, captions with SEQ fields, equations, blockquotes, and references — with auto-filled Daftar Isi, live online campus lookup (300 DPI RGB logo PNG + Rektor, Dekan, Kaprodi + Kota + Kementerian), interactive ZIP-upload setup menu, 5-stage workflow gate, and optional integration with MuZA_Search v1.1 outputs. Trigger automatically whenever the user uploads this Skill ZIP, invokes /muza-skripsi-template or msshi skripsi, uploads a campus guideline PDF/DOCX, or asks in natural Indonesian/English phrases or typos such as "Buatkan aku template skripsi", "Buatkan aku templete skripsi", "bikin template/templete skripsi", "format skripsi", "format tesis", "pedoman skripsi", "panduan tugas akhir", "cover skripsi kampus", "template word skripsi", "MuZA Agent", "YZ Agent", or "mulai"/"start".
---

# MuZA Agent — MuZA_Skripsi_Template v1.1 (MuZA Project Edition)

Goal: produce `Template_Skripsi_<CampusShort>.docx` whose formatting matches the user's campus guideline accurately, with **verified official names (`Rektor/Direktur`, `Dekan`, `Ketua Program Studi`) + crisp 300 DPI RGB campus logo automatically fetched online**, while keeping **Student Name (`{name}`), NIM (`{nim}`), and Dosen Pembimbing I/II (`{supervisor1}`, `{id1}`, `{supervisor2}`, `{id2}`)** as clean self-editable placeholders (`Ctrl+H`) since advisors are assigned individually and cannot be automated. Every format rule value must come from the guideline whenever stated, and any unstated rule must be visibly marked as a default (`*`).

`<SKILL_DIR>` = the extracted folder containing this `SKILL.md` (auto-locate it if this skill was uploaded as a `.zip` package or bundled under `skills/muza-skripsi-template/`). Keep script edits inside `<SKILL_DIR>` clean and run scripts directly from there (cross-OS compatible: Windows `C:`/`D:` adaptive, Linux, macOS, ChatGPT/Claude sandbox, and Google Colab).

Talk to the user in their language (default Indonesian, casual and friendly). Keep chat replies structured and concise; put the craftsmanship into the `.docx` template. **Never ask the user to supply Student Name (`{name}`), NIM (`{nim}`), or Pembimbing I/II unless they volunteer them** — keep those as clean `Ctrl+H` placeholders (`NAMA LENGKAP MAHASISWA`, `0000000000`, `Nama Pembimbing I, Gelar`, `0000000001`, `Nama Pembimbing II, Gelar`, `0000000002`) and explicitly mention that Pembimbing & identitas mahasiswa diisi sendiri oleh pengguna setelah unduh.

## 5-Stage Guided Workflow (Gate 1 -> Gate 5)

Baik dipanggil lewat upload `.zip`, slash command `/muza-skripsi-template`, `msshi skripsi`, `MULAI_SKRIPSI_DRAG_AND_DROP.bat`, maupun prompt alami (*"Buatkan aku template skripsi!"* / *"Buatkan aku templete skripsi!"*), jalankan 5 tahapan berikut berurutan tanpa mengarang aturan maupun nama pejabat kampus.

## Stage 1 (Gate 1) — Interactive Onboarding Menu (Saat ZIP Di-upload / Mulai Awal)

- **As soon as the user uploads this Skill `.zip` (or says "mulai"/"start") without giving campus details + guideline file yet:** do NOT just wait silently for an attachment! Immediately present this **interactive menu of choices & short fill-ins** (use an interactive multiple-choice widget if your interface has one, otherwise clean numbered choices in chat):

> **MuZA_Skripsi_Template v1.1 (MuZA Project) siap bekerja!** Pilih atau isi data di bawah ini (cukup balas nomor + isian singkat):
>
> **1. Pilih Universitas / Kampus:**
> - **A.** UNNES *(Universitas Negeri Semarang)*
> - **B.** UNDIP *(Universitas Diponegoro)*
> - **C.** UNWAHAS *(Universitas Wahid Hasyim)*
> - **D.** UIN Walisongo Semarang
> - **E.** POLINES *(Politeknik Negeri Semarang)*
> - **F.** UDINUS *(Universitas Dian Nuswantoro)*
> - **G.** Unika Soegijapranata
> - **H.** UNISSULA *(Universitas Islam Sultan Agung)*
> - **I.** USM *(Universitas Semarang)*
> - **J.** UNIMUS *(Universitas Muhammadiyah Semarang)*
> - **K.** UNISBANK *(Universitas Stikubank)*
> - **L.** Kampus Lain *(tulis nama lengkap perguruan tinggi)*
>
> **2. Isi Fakultas & Program Studi:** *(contoh: Fakultas Teknik — Teknik Informatika)*
>
> **3. Pilih Sumber Pedoman Skripsi:**
> - **1)** Upload file PDF/DOCX Pedoman Skripsi dari kampus sekarang *(paling akurat)*
> - **2)** Biarkan AI mencari PDF Pedoman resmi kampus di internet secara otomatis
>
> **4. Pilih Jenis / Metodologi Penelitian (Preset Struktur Bab):**
> - **1)** Informatika / Ilmu Komputer *(Sistem, AI/ML, Perangkat Lunak)*
> - **2)** Kuantitatif *(Survei, Eksperimen, Uji Hipotesis)*
> - **3)** Kualitatif *(Studi Kasus, Fenomenologi)*
> - **4)** R&D *(Penelitian & Pengembangan: ADDIE / Borg & Gall)*
> - **5)** PTK *(Penelitian Tindakan Kelas — Siklus I & II)*
>
> **5. Opsional:** Upload file `.zip` hasil `MuZA_Search v1.1` bila ingin **Bab 2 Penelitian Terdahulu & Daftar Pustaka** terisi otomatis *(boleh dikosongkan)*.
>
> *(Info otomatis: **Logo kampus, Kota, Kementerian, Gelar, Rektor/Direktur, Dekan, dan Kaprodi** akan dicari & dipasang otomatis oleh AI dari sumber resmi; **Nama, NIM, dan Pembimbing I/II** disiapkan sebagai placeholder rapi untuk diisi sendiri via `Ctrl+H`.)*

Then pause once and wait for the user's reply/uploads.
- **As soon as the user replies with their choices and/or uploads a guideline file (`.pdf`/`.docx`/`.doc`/`.txt`):** execute **Stages 2 -> 5 (Gate 2 -> Gate 5) end-to-end immediately** without asking unnecessary follow-ups!

## Stage 2 (Gate 2) — No guideline? Find it online + Campus Lookup

If the user says they have no guideline (or only a link/photo), ask these three in one message:
1. Universitas apa?
2. Fakultas apa?
3. Program Studi apa?

Search thoroughly across faculty/prodi portals, university libraries, LPPM, or Google Drive (`pedoman penulisan skripsi <universitas> <fakultas>`, `site:<domain> pedoman skripsi filetype:pdf`).
- Prefer the newest edition and most specific unit (prodi > fakultas > universitas). If they conflict, follow faculty/prodi and inform the user.
- Repository theses from the same prodi are only a secondary hint, never a primary substitute — tell the user clearly if only those exist.
- If nothing is found, report where you searched and offer a generic template (using one of the 5 presets in `assets/presets/`) only if the user agrees, marking all rows in `format_summary` with `from_guideline: false`.

## Step 3 — Extract & Read the Whole Guideline

```bash
python <SKILL_DIR>/scripts/extract_guideline.py <guideline_file>
```

On Windows/Linux/macOS/Colab, `extract_guideline.py` automatically saves the extracted text (with `=== PAGE n ===` markers) to `<tempdir>/guideline.txt`, ranks the top keyword-dense pages, prints **`AUTO-DETECTED GUIDELINE CANDIDATES`** (paper, margins, font, spacing, indent, numbering, citation style, chapters, and sample appendix page numbers), and optionally exports `--json rules.json`.

- Verify EVERY candidate rule against the full text and page citations (never trust regex blindly without checking the page).
- Inspect sample layout pages (contoh sampul, halaman judul, lembar persetujuan/pengesahan, pernyataan keaslian, abstrak, daftar isi, daftar pustaka) visually by rendering PDF pages to PNG if needed.
- If `LOW TEXT` is reported (scanned PDF), render pages to images and inspect visually.

Rule checklist:
paper size & weight; margin order (top/left/bottom/right); font family & sizes (cover, chapter, sub-headings, body, captions, footnotes/tables); line spacing (body, abstract, blockquote/kutipan langsung, captions, bibliography, table); paragraph indent; alignment; chapter title format (`BAB I` on 1 vs 2 lines); sub-heading numbering (`1.1`/`1.1.1` vs `A.`/`1.`/`a.`) & hanging/tiered indent; page-number format & position for front matter, chapter first pages, continuing pages, and back matter (`continue` / `none` / `prefix` e.g. `L-1`); unprinted counted pages; front-matter page order & `in_toc` rules; table style (`three_line` 3-line booktabs vs `grid`); caption numbering & source lines; citation style (`APA 7th`, `IEEE`, `Harvard`, `Vancouver`); abstract word limit & keywords.

## Step 4 — Build `spec.json` & Select Methodology Preset

Read `references/spec_schema.md`, copy `assets/example_spec.json` to a working `spec.json`, and fill every value from the guideline.
- **5 Built-in Methodology Presets (`assets/presets/`):**
  - `preset_kuantitatif.json`
  - `preset_kualitatif.json`
  - `preset_rnd.json`
  - `preset_informatika_ilkom.json`
  - `preset_ptk.json`
  If the guideline separates chapters by research methodology (or if the user has not specified prodi-specific chapter headings), ask the user which methodology fits best or pass `--preset <name>` to `build_template.py`.
- Fill EVERY required page with realistic sample content using `{tokens}` for student/advisor data (`{title}`, `{name}`, `{nim}`, `{supervisor1}`, `{id1}`, `{supervisor2}`, `{id2}`, `{dean}`, `{city}`, `{date}`, `{year}`) — no `"[...]"` brackets in visible text.
- Use `blockquote` (`Kutipan Langsung`), `equation` (`Rumus`), and `table` (`three_line` academic booktabs by default, unless guideline requires full grid) where helpful.
- Put guideline instructions into `hint` (becomes Word margin comments authored by **MuZA Agent**).
- Mark `from_guideline: false` on every `format_summary` row that used a default value.

## Step 5 — Build `.docx` (Default `--auto-online`, Optional Integrate `MuZA_Search v1.1`)

```bash
python <SKILL_DIR>/scripts/build_template.py spec.json Template_Skripsi_<CampusShort>.docx --auto-online
```

Flags & workflow notes:
- `--auto-online` *(recommended default right after reading the uploaded pedoman)* + optional `--universitas "..."`, `--fakultas "..."`, `--prodi "..."`, `--find-pedoman`: automatically queries Wikipedia/Wikidata/ROR/OpenAlex, official `*.ac.id` portals/sitemaps, and public web indexes via `scripts/campus_lookup.py` to download & embed the official campus logo (300 DPI RGB PNG) onto Cover & Halaman Judul, verify `city`, `short`, `ministry`, `degree`, and extract verified official names (`rector`, `dean`, `head_program` + optional `NIP`/`NIDN`) with Word comment source attribution. Student `{name}`, `{nim}`, and Pembimbing I/II (`{supervisor1}`, `{id1}`, `{supervisor2}`, `{id2}`) are intentionally preserved as placeholders for self-editing via Ctrl+H because advisors cannot be automated.
- **Offline / restricted AI-sandbox fallback**: If outbound network access is blocked inside the AI container, do not crash or stall—use your built-in web search (if enabled) or pass `--logo <campus_logo.png>` manually, keep unverified officials as clean `[Nama ...]` placeholders inside `spec.json`, and run `build_template.py spec.json Template_Skripsi_<CampusShort>.docx` without `--auto-online`. Never bypass WAF/CAPTCHA checks.
- `--muza-zip <MuZA_Search_Output.zip>` *(supports `MuZA_Search v1.1` packages containing `03_METADATA_MUZA_SKRIPSI.json`, Bab 2 CSV/XLSX, and `.ris`)* or `--muza-bab2 <csv/xlsx>` + `--muza-ris <file.ris>`: automatically injects the extracted **Bab 2 Research Synthesis Table** into Chapter II (`Penelitian Terdahulu` / `Penelitian Relevan`) AND formats all RIS references into `Daftar Pustaka` according to the campus citation style (`APA 7th` / `IEEE` / `Harvard`).
- `--preset <kuantitatif|kualitatif|rnd|informatika_ilkom|ptk>`
- `--logo <campus_logo.png>`
- `--table-style <three_line|grid|none>`
- Jalur lokal drag-and-drop Windows: pengguna dapat juga memakai **`MULAI_SKRIPSI_DRAG_AND_DROP.bat`** atau `msshi skripsi` yang menyimpan hasil ke `D:\HermesData\Skripsi_Output` (atau fallback `%USERPROFILE%\Documents\MuZA_Skripsi_Output` pada laptop yang hanya memiliki Drive `C:`).

The builder:
- Uses LibreOffice (`soffice`) when installed (up to 3 passes) to populate real page numbers in Daftar Isi/Tabel/Gambar/Lampiran, OR falls back smoothly to the **Analytical Page Estimator** when LibreOffice is absent so lists are STILL pre-filled while remaining live Word fields.
- Embeds a redesigned **MuZA_Skripsi_Template v1.1** tutorial guide page first (with Campus Lookup Verification table, Find & Replace table, Quick Guide shortcut cheat-sheet, and rule summary table) and renders hardened 300 DPI solid-RGB PNG logos compatible with Word Protected View.

## Stage 5 (Gate 5) — Audit Kualitas & Serah Terima `.docx`
- Verifikasi file `.docx` benar-benar terbentuk, berukuran wajar, dan tampil bersih (termasuk logo PNG & placeholder halaman pengesahan).
- Laporkan ringkas kepada pengguna:
  1. Lokasi file hasil (`Template_Skripsi_<CampusShort>.docx`).
  2. Ringkasan format yang dikunci + transparansi item `from_guideline: true` vs `false` (`*Default`) serta nama pejabat yang berhasil/belum ditemukan.
  3. Panduan cepat **`Ctrl+H`** menggunakan tabel halaman pertama untuk mengisi `{name}`, `{nim}`, `{supervisor1}`, `{id1}`, `{supervisor2}`, `{id2}`, dan `{title}`.

## Honesty Rules
- Never claim a value is from the guideline if it is not. Never invent page numbers, university officials' names, or `NIP`/`NIDN`. Only write official names/NIPs returned by verified sources or provided by the user.
- If a margin rule like `"4-3-3-3"` is ambiguous about order, document the interpretation in `format_summary` and ask the user to verify with their prodi/advisor.
- Warn the user if the guideline PDF is 5+ years old or belongs to a parent university rather than their specific faculty/prodi.
