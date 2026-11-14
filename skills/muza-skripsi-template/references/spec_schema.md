# spec.json schema (MuZA_Skripsi_Template v1.1)

Goal: the output must look FINISHED. Every page gets realistic sample content the student only replaces.
No `"[...]"` brackets in visible text: use `{tokens}` for personal data (replaced by neat sample text listed in the tutorial Find & Replace table), `sample_paragraph` blocks for body text, and `hint` for guideline instructions (inserted as Word margin comments by **MuZA Agent**).

Copy `assets/example_spec.json` (or combine with a methodology preset in `assets/presets/`), then replace EVERY value with what the campus guideline specifies.
Units: lengths in `cm`, font size and paragraph spacing in `pt`, `line_spacing` as a multiple.

## Converting guideline wording
| Guideline says | Spec value |
|---|---|
| "spasi 2" / "double" / "dua spasi" | `line_spacing: 2.0` |
| "spasi 1,5" | `1.5` |
| "spasi 1" / "single" / "rapat" | `1.0` |
| "jarak 4 spasi antara judul bab dan teks" (font 12, single base) | `space_after: 36`–`48` and note it |
| "menjorok 5 ketukan / 5 karakter" | `first_indent_cm: 1.25` (≈ 0.25 cm per ketukan at 12 pt) |
| "menjorok 1 tab" | `1.27` |
| Kertas A4 / Kuarto / F4 (Folio) | `paper: "A4" / "KUARTO" / "F4"`, or exact `width_cm`, `height_cm` |
| Margin "4-4-3-3" | top 4, left 4, bottom 3, right 3 cm (confirm order in guideline) |
| Nomor halaman romawi kecil (i, ii) | `"lowerRoman"`; Arab = `"decimal"`; ROMAWI BESAR = `"upperRoman"` |
| Position "tengah bawah" / "kanan atas" / "kanan bawah" | `bottom_center` / `top_right` / `bottom_right` (also `top_center`, `top_left`, `bottom_left`, `none`) |

## Top-level keys
- `auto_lookup`: boolean (default `false`). When `true` (or when `--auto-online` is passed), `scripts/campus_lookup.py` automatically searches Wikipedia/Wikidata/ROR/OpenAlex and official `*.ac.id` pages for the campus logo (downloaded and placed on Cover & Halaman Judul), `city`, `ministry`, `degree`, `rector`, `dean`, and `head_program` (plus optional `id_rector`, `id_dean`, `id_head`).
- `campus`: `university`, `short`, `faculty`, `program`, plus optional `degree`, `ministry`, `website`.
- `citation_style`: `"APA 7th"` (default) | `"IEEE"` | `"Harvard"` | `"Vancouver"`. Used when formatting references from `MuZA_Search v1.0`+.
- `table_style`: `"three_line"` (default — Indonesian/APA academic 3-line booktabs without vertical borders + `<w:tblHeader/>` repeat header) | `"grid"` | `"none"`.
- `tiered_heading_indent`: boolean (default `false`). When `true`, `Heading 2–4` automatically cascade horizontally (e.g. `A.` at 0 cm, `1.` aligned under text at 0.65 cm, `a.` at 1.30 cm) unless explicitly overridden.
- `preset`: optional preset name (`"kuantitatif"`, `"kualitatif"`, `"rnd"`, `"informatika_ilkom"`, `"ptk"`) or path to JSON preset if `body.chapters` should inherit from a preset.
- `muza_search_integration`: optional dict `{ "zip_path": "...", "bab2_path": "...", "ris_path": "..." }` (can also be supplied via CLI `--muza-zip`, `--muza-bab2`, `--muza-ris`).
- `placeholders`: list of `{key, sample, label}`. Built-in keys: `title`, `name`, `nim`, `supervisor1`, `id1`, `supervisor2`, `id2`, `city`, `date`, `year`. `{name}` and `{nim}` stay as template placeholders for the student to fill in after downloading `.docx`. Official keys populated when verified online: `dean`, `id_dean`, `head_program`, `id_head`, `rector`, `id_rector`, `degree`, `ministry`.
- `source_document`: `title` (with year), `url`.
- `page`: `paper`, `width_cm`, `height_cm`, `margins_cm{top,bottom,left,right}`, `gutter_cm`, `header_distance_cm`, `footer_distance_cm`.
- `font`: `name`, `size`.
- `body_text`: `line_spacing`, `align` (`left|center|right|justify`), `first_indent_cm`, `space_before`, `space_after`.
- `styles`: per-element format dicts. Supported keys:
  `chapter` (`Heading 1`), `h2`, `h3`, `h4`, `front_title`, `table_caption`, `figure_caption`, `appendix_caption`, `caption_source` (`Keterangan Sumber`), `blockquote` (`Kutipan Langsung`), `equation` (`Rumus`), `bibliography` (`Daftar Pustaka`), `table_text` (`Teks Tabel`), `toc`, `abstract` (`Abstrak`), `cover` (`Sampul`), `page_number`.
  - Format dict keys: `font`, `size`, `bold`, `italic`, `caps`, `underline`, `align`, `line_spacing`, `space_before`, `space_after`, `first_indent`, `left_indent`, `right_indent`, `hanging_indent` (supports float in cm or `"auto"`), `keep_with_next`.
- `toc.levels`: heading levels included in Daftar Isi (usually `2` or `3`).
- `cover`: `vertical_align` (`auto|top|center|both`), `lines`: ordered list of text items, logos (`{"type":"logo","width_cm":4,"path":...}`), or `fields`. Text items also support `"inverted_pyramid": true` for Indonesian inverted-pyramid title cover formatting.
- `front_matter`: `number_format`, `number_position`, `start_at`, `pages[]` (`title`, `hint`, `lines`, `vertical_align`, `kind`: `page|toc|list_of_tables|list_of_figures|list_of_appendices`, `in_toc`, `show_number`, `blocks`).
- `body`: `number_format`, `start_at`, `chapter_first_page_position`, `other_pages_position`, `chapter_heading_two_lines`, `tiered_heading_indent`, `chapters[]`.
- `captions`: `live_seq_fields` (default `true` — embeds Word `SEQ` field with `\r 1` reset per first item while preserving full rendered text), `table_example`, `figure_example`, `table_source`, `figure_source`.
- `back_matter`: `first_page_position`, `other_pages_position`, `pages[]` with `numbering_mode` (`"continue"` | `"none"` | `"prefix"` with optional `"page_prefix": "L-"`).
- `format_summary`: list of `{item, value, source, from_guideline}`.
- `credit`: footer note on the tutorial page.

## Block types (for `blocks` arrays)
- `{"type":"text","text":"...","style":"Isi Paragraf","align":"center","bold":true,"italic":false,"no_indent":true}`
- `{"type":"blockquote","text":"...","style":"Kutipan Langsung","italic":false,"hint":"..."}` — direct quotation block (single spacing, indented left).
- `{"type":"equation","formula":"y = a + bx + e","number":"(2.1)","italic":true,"hint":"..."}` — centered formula with right-aligned equation number using style `Rumus`.
- `{"type":"sample_paragraph","topic":"latar belakang","count":1,"style":"Isi Paragraf"}`
- `{"type":"hint","text":"..."}`
- `{"type":"blank","lines":1}`
- `{"type":"fields","rows":[["Judul","{title}"],["Nama","{name}"]],"label_width_cm":3.5}`
- `{"type":"signature","columns":[...],"position":"right","underline_names":true}`
- `{"type":"table","rows":[[...]],"header":true,"table_style":"three_line","widths_cm":[...]}`
- `{"type":"caption","style":"Judul Tabel","text":"Tabel 2.1 ..."}`
- `{"type":"keywords","label":"Kata kunci: ","text":"...","italic":false,"style":"Abstrak"}`
- `{"type":"page_break"}`

## Styles present in generated .docx
`Heading 1`–`Heading 4`, `Isi Paragraf`, `Kutipan Langsung`, `Rumus`, `Judul Bagian`, `Judul Bagian Tanpa Daftar Isi`, `Judul Tabel`, `Judul Gambar`, `Judul Lampiran`, `Keterangan Sumber`, `Daftar Pustaka`, `Teks Tabel`, `Abstrak`, `Sampul`, `Nomor Halaman`, `Petunjuk`.
