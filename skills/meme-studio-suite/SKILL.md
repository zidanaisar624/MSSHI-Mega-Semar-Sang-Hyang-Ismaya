---
name: meme-studio-suite
description: Studio pembuatan meme Rp0 khusus Kiki-Chii yang menyatukan 4 alur open-source MIT: (1) makememe (URL/PNG instan tanpa API key lewat memegen.link), (2) awesome-meme (27+ template programmer & klasik via Pillow + YAML lokal dengan dukungan Impact/CJK), (3) meme-lord (pola viral Hall of Fame, ironic contrast, Two-Step Clean-Scene + Impact Overlay, serta evaluasi A/B lokal 6 dimensi — TANPA Visa CLI, Exa berbayar, StableUpload, atau fal.ai), dan (4) createa-meme-skill (caption-craft 'find the turn' 2-6 kata per baris + MCP opsional @createa/meme-mcp hanya jika Pengguna membawa CAM_API_KEY kuota gratis 20/bulan tanpa kartu).
license: MIT
---

# Meme Studio Suite — Studio Meme Rp0 Kiki-Chii (`v3.2.1`)

Skill khusus **Kiki-Chii** yang menggabungkan empat mesin meme open-source berlisensi **MIT** menjadi alur kerja **Rp0 (tanpa API key berbayar wajib)**:

1. **`dhruvmehra/makememe`** — URL & PNG meme instan via `api.memegen.link` (200+ template klasik, Python stdlib murni, 0 API key).
2. **`edwinjhlee/awesome-meme`** — 27+ template programmer & klasik dengan render lokal presisi (`Pillow` + `YAML`, deteksi font `Impact` Windows/macOS + fallback CJK otomatis).
3. **`csmoove530/meme-lord` (Edisi Bersih Rp0)** — HANYA mengadopsi *Hall of Fame*, 8 Pola Sukses Universal, *Two-Step Clean-Scene + Impact Overlay*, dan papan evaluasi A/B lokal 6 dimensi (`meme-rating/`). **SKIP TOTAL:** Visa CLI, pencarian Exa berbayar, StableUpload, dan `fal.ai`.
4. **`RiskAverseTech/createa-meme-skill`** — Disiplin *Caption Craft* (*"The one rule: find the turn"*, 2–6 kata per baris, 1 ide tunggal per meme); server `@createa/meme-mcp` bersifat **100% opsional BYOK** hanya bila Pengguna sudah memiliki `CAM_API_KEY` (kuota gratis 20 meme/bulan tanpa kartu kredit).

---

## 1. Aturan Emas Penulisan Caption (*Caption Craft* + *Anti-Slop*)

Sebelum menyentuh template atau merender gambar, Kiki-Chii **WAJIB** menguji konsep lelucon:

1. **Temukan Titik Balik (*Find The Turn*):**
   - Meme bekerja dari **kontras tajam** antara dua sisi: *ekspektasi vs realita*, *apa yang diucapkan vs apa yang dirasakan*, *percaya diri di awal vs panik di akhir*, atau *solusi over-engineered vs masalah sepele*.
   - Jika belum ada kontras (*turn*), itu baru pernyataan biasa — bukan meme.
2. **2–6 Kata per Baris & Satu Ide per Meme:**
   - Baris pendek terbaca dalam `< 1.5` detik saat audiens *scrolling*.
   - Buang kata pengisi (*"ketika kamu sedang mencoba untuk..."* -> langsung *"Deploy Jumat 17:55"*).
3. **Spesifik Mengalahkan Umum (*Specificity Wins*):**
   - Buruk: *"Ketika kodenya banyak bug."*
   - Tajam: *"Ubah 1 baris CSS" / "47 unit test ikut merah."*
4. **Etika & Anti-Slop MSSHI:**
   - Humor menertawakan situasi, absurditas teknis, atau *relatable pain* sehari-hari — bukan menyerang individu pribadi atau SARA.

Lihat tabel lengkap pola viral dan pemetaan template di `references/caption-and-viral-patterns.md`.

---

## 2. Empat Jalur Produksi Meme (Pilih Sesuai Kebutuhan)

Helper CLI deterministik tersedia langsung di:
`python skills/meme-studio-suite/scripts/msshi_meme_studio.py`

### Jalur A — Instan Tanpa Dependency (`makememe` / `memegen.link`, Rp0)
Cocok saat Pengguna meminta meme klasik cepat atau tautan PNG siap pakai tanpa menyiapkan aset lokal:

```bash
# Cari katalog template bawaan (100% offline, 0 jaringan)
python skills/meme-studio-suite/scripts/msshi_meme_studio.py templates --query coding

# Buat URL PNG memegen.link ter-escape secara deterministik (dan unduh opsional dengan --download)
python skills/meme-studio-suite/scripts/msshi_meme_studio.py url drake "Tulis dokumentasi" "Refactor jam 2 pagi"
python skills/meme-studio-suite/scripts/msshi_meme_studio.py url fine "RAM tinggal 200 MB" "Masih buka 40 tab" --download meme_fine.png
```

Aturan escape `memegen.link` ditangani otomatis (`_` -> `__`, `-` -> `--`, spasi -> `_`, `?` -> `~q`, `%` -> `~p`, `#` -> `~h`, `/` -> `~s`, `"` -> `''`, `\n` -> `~n`).

### Jalur B — Template Programmer & Render Lokal Pillow (`awesome-meme`, Rp0)
Cocok untuk meme developer (`vim-exit`, `it-works-why`, `wtf-per-minute`, `code-review-guy`, `monday-deploy`, `stackoverflow-copy`, `bug-feature`, `lgtm`, `programmer-drink`, `distracted-boyfriend`, `chill-guy`) atau menempel teks di atas gambar lokal milik Pengguna:

```bash
# Render teks Impact putih ber-stroke hitam di atas gambar lokal (mendukung Latin & CJK otomatis)
python skills/meme-studio-suite/scripts/msshi_meme_studio.py render-local --image base.png --top "KATANYA CUMA HOTFIX" --bottom "3 REPO IKUT REBUILD" --output out_meme.png

# Atau buat kartu meme 2-panel / kanvas lokal cepat tanpa gambar eksternal
python skills/meme-studio-suite/scripts/msshi_meme_studio.py render-local --canvas 900x600 --top "RENCANA: TIDUR JAM 10" --bottom "REALITA: DEBUG SAMPAI SUBUH" --output card_meme.png
```

### Jalur C — *Two-Step Custom Scene* + Papan A/B 6 Dimensi (`meme-lord` Lokal, Rp0)
Jika Pengguna ingin visual orisinal (bukan template stok):
1. **Langkah 1 (Clean Image Tanpa Teks):** Buat adegan visual ekspresif **tanpa teks sama sekali** memakai alat visual pilihan Pengguna sendiri (misal Blender MCP, kanvas lokal, atau generator gambar yang sudah disambungkan Pengguna). Jangan minta model gambar mengeja kalimat panjang agar bebas salah ketik.
2. **Langkah 2 (Local Impact Overlay):** Tempel caption presisi memakai `render-local`.
3. **Langkah 3 (A/B Testing Lokal 2–3 Kandidat):** Hasilkan 2–3 variasi caption/visual lalu buat lembar review HTML interaktif lokal:

```bash
python skills/meme-studio-suite/scripts/msshi_meme_studio.py ab-rate-html --title "Uji A/B Meme Rilis" --candidate "Varian A:meme_a.png:Kontras Ironis" --candidate "Varian B:meme_b.png:Deadpan Developer" --output ab_meme_review.html
```

Bobot evaluasi 6 dimensi: **Concept (`30%`) + Visual Quality (`25%`) + Meme Fit (`20%`) + Consistency (`15%`) + Speed (`5%`) + Cost (`5%`)**.

### Jalur D — Opsional BYOK `@createa/meme-mcp` (`createa-meme-skill`)
- **HANYA digunakan jika Pengguna secara sukarela sudah memasang `CAM_API_KEY`** (kuota gratis 20 meme/bulan tanpa kartu kredit dari `https://createameme.org`).
- Jika `CAM_API_KEY` belum ada, **jangan memaksa pendaftaran** — langsung layani lewat Jalur A, B, atau C yang 100% gratis tanpa akun.

---

## 3. Kolaborasi Antar-Bot MSSHI

- **Yukino (`Tipe 1`):** Menangkap keluhan harian, momen kampus/kerja, atau ide mentah yang *relatable*.
- **Val (`Tipe 2`):** Menyuplai fakta akurat, tren topik, atau istilah teknis agar *punchline* cerdas dan valid.
- **Kiki-Chii (`Lead`):** Merumuskan *the turn*, memilih template paling pas, merender PNG, dan menyajikan 2–3 opsi A/B.
- **Sensei Shizuka (`Orkestrator`):** Menjaga keselarasan *brand voice* Pengguna dan gerbang anti-slop sebelum dipublikasikan.
