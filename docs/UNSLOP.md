# Unslop: audit dan perbaikan UI kontekstual

MSSHI v3.1 menambahkan skill `unslop` untuk Kiki-Chii, Val, dan Coder. Upstream [heydamir/unslop](https://github.com/heydamir/unslop) memperbaiki antarmuka yang tampak generik melalui audit layar, arah yang berasal dari produk, dan pass desain berurutan. Ini adalah kemampuan UI; aktivasi tidak membuat seluruh percakapan menjalani penulisan ulang otomatis.

## Cakupan peran

| Bot | Pemakaian | Contoh permintaan |
| --- | --- | --- |
| Kiki-Chii | Audit visual, karakter produk, komposisi, art direction, dan brief | `Unslop layar landing page ini, pertahankan identitas mereknya.` |
| Val | Evaluasi dashboard ilmiah/data: bukti, unit, label, legenda, periode, sumber, ketidakpastian, dan keterbacaan | `Tinjau dashboard eksperimen ini: apakah grafik, unit, dan perbandingannya jelas?` |
| Coder | Perubahan komponen/CSS dalam lingkup tugas, render, pemeriksaan responsif dan kontrol | `Terapkan temuan unslop di dashboard ini dan periksa tampilan mobile.` |

Val tetap menjalankan peran riset. Temuan frontend dapat diserahkan kepada Coder tanpa mengubah persona atau mengaktifkan orkestrasi baru. Skill tersedia melalui discovery normal ketiga profil. Perubahan source publik pada matriks aktivasi mengatur distribusi paket; instalasi live hanya menyalin folder skill ke ketiga profil tersebut.

Alur adaptasi dimulai dari bukti layar dan perbaikan terkecil. Arah baru diperlukan hanya untuk redesign yang memang diminta. Urutan kerja yang dipertahankan: jarak, warna, ikon, copy, tipografi, layout, detail, visual, lalu gerak. Hasil yang sudah baik tidak harus didesain ulang. Brand, fitur, data, serta maksud pengguna dipertahankan.

## Hubungan dengan skill yang sudah ada

- `antislop` tetap menjadi filter kualitas UI yang sudah terpasang. Unslop memberi alur diagnosis dan perbaikan layar tertentu; tidak menambahkan gate kedua, mengganti mode antislop, atau mengubah preferensinya.
- `humanizer-en`, `humanizer-indonesia`, dan `match-my-writing-style` menangani prosa atau suara penulis ketika relevan. Unslop hanya meninjau copy pada antarmuka yang sedang dikerjakan. Gaya native Kiki-Chii, Val, Coder, dan pengguna tetap dipertahankan.
- Browser native, GDrive, Brightdata, dan plugin yang sudah tersedia tidak diganti. Tidak ada desktop MCP baru, daemon, hook, provider, model, fallback, MoA, atau perubahan konfigurasi persona.

## Provenance dan modifikasi

| Item | Nilai |
| --- | --- |
| Upstream | [heydamir/unslop](https://github.com/heydamir/unslop) |
| Revisi yang ditinjau | [`97daa3eb365670ea3f87ed85356cbfcee18105a5`](https://github.com/heydamir/unslop/tree/97daa3eb365670ea3f87ed85356cbfcee18105a5) |
| Penulis upstream | Damir Sokolovsky, [@heydamir](https://x.com/heydamir) |
| Lisensi | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), teks upstream disertakan di [skills/unslop/LICENSE](../skills/unslop/LICENSE) |
| Sumber primer | [README](https://github.com/heydamir/unslop/blob/97daa3eb365670ea3f87ed85356cbfcee18105a5/README.md), [SKILL.md](https://github.com/heydamir/unslop/blob/97daa3eb365670ea3f87ed85356cbfcee18105a5/skills/unslop/SKILL.md), [LICENSE](https://github.com/heydamir/unslop/blob/97daa3eb365670ea3f87ed85356cbfcee18105a5/LICENSE) |

Revisi adalah HEAD `main` aktual yang diverifikasi saat integrasi, bukan asumsi bahwa revisi lama masih terbaru. MSSHI menyertakan adaptasi ringkas berbahasa Indonesia dengan routing peran, scope kontekstual, brand dan gaya pengguna dipertahankan, serta perlindungan makna data ilmiah. Aturan upstream yang memilih satu estetika, meminta jeda persetujuan pada setiap arah, atau menawarkan koneksi layanan gambar tidak disalin sebagai kebijakan global. Kredit, tautan asal, penanda modifikasi, lisensi, dan penafian dipertahankan. Tidak ada klaim dukungan dari pembuat upstream.

Sumber asli disimpan di cache privat untuk audit. Aset gambar referensi, contoh UI, metadata UI Codex, dan skrip upstream `snapshot.mjs`/`story.mjs` tidak didistribusikan atau dijalankan oleh integrasi ini. Folder skill publik/live hanya berisi `SKILL.md` dan `LICENSE`.

## Dependensi dan validasi

Tidak ada dependensi runtime baru untuk alur audit dan brief. Implementasi Coder memerlukan akses source aplikasi dan toolchain proyek terkait. Audit screenshot dapat dilakukan dari gambar yang diberikan; audit visual URL memerlukan browser native yang sudah dikonfigurasi. Jika render tidak tersedia, hasil menyatakan keterbatasan tersebut.

Upstream memiliki mode snapshot yang memerlukan Playwright dan Chromium, serta story video yang juga memerlukan ffmpeg. Mode skrip itu tidak dipasang oleh adaptasi MSSHI ini. Video atau generasi gambar merupakan pekerjaan terpisah sesuai permintaan pengguna dan alat yang tersedia; instalasi skill tidak memakai kredit API atau menjalankan percakapan LLM.

Validasi integrasi mencakup frontmatter, nama folder, tautan lokal, teks atribusi, daftar isi file, ukuran, SHA-256, dan kesamaan salinan pada tiga profil. Karena artefak hanya petunjuk dan lisensi, tidak ada tes kode semu yang meniru implementasi. Bukti audit privat mencatat pin sumber dan hasil penyalinan; cache privat bukan bagian dari paket publik.
