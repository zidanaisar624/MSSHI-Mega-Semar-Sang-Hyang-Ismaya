---
name: meme-studio-suite
description: Studio meme Kiki-Chii untuk mencari 28 konsep template, merender gambar dengan Pillow, membuat URL memegen, dan membandingkan caption lewat papan penilaian A/B lokal. Empat sumber MIT dan integrasi Create a Meme opsional.
license: MIT
---

# Meme Studio Suite — Studio Meme Rp0 Kiki-Chii (`v3.2.1`)

Skill khusus **Kiki-Chii** yang menggabungkan empat mesin meme open-source berlisensi **MIT** menjadi alur kerja **Rp0 (tanpa API key berbayar wajib)**:

1. **`dhruvmehra/makememe`** — Susun URL memegen dengan Python. Saat tautan dibuka atau `--download` digunakan, layanan memegen menerima teks caption. Pilih render lokal untuk naskah pribadi.
2. **`edwinjhlee/awesome-meme`** — Katalog MSSHI berisi 28 konsep programmer dan klasik. Perintah `templates` menampilkan ID, jumlah slot, dan makna. Untuk memakai foto atau ilustrasi tertentu, berikan gambar lokal dengan `--image`. `render-local` memakai Pillow dan font yang terpasang. Aset gambar dan definisi YAML upstream dikelola terpisah.
3. **`csmoove530/meme-lord` (Edisi Bersih Rp0)** — HANYA mengadopsi *Hall of Fame*, 8 Pola Sukses Universal, *Two-Step Clean-Scene + Impact Overlay*, dan papan evaluasi A/B lokal 6 dimensi (`meme-rating/`). **SKIP TOTAL:** Visa CLI, pencarian Exa berbayar, StableUpload, dan `fal.ai`.
4. **`RiskAverseTech/createa-meme-skill`** — Tulis satu gagasan dan cari titik baliknya dalam 2–6 kata per baris. Pengguna yang memilih integrasi `@createa/meme-mcp` menyediakan kunci miliknya sendiri.

---

## 1. Aturan Emas Penulisan Caption (*Caption Craft* + *Anti-Slop*)

Sebelum menyentuh template atau merender gambar, Kiki-Chii **WAJIB** menguji konsep lelucon:

1. **Temukan Titik Balik (*Find The Turn*):**
   - Meme bekerja dari **kontras tajam** antara dua sisi: *ekspektasi vs realita*, *apa yang diucapkan vs apa yang dirasakan*, *percaya diri di awal vs panik di akhir*, atau *solusi over-engineered vs masalah sepele*.
   - Jika belum ada kontras (*turn*), itu baru pernyataan biasa — bukan meme.
2. **2–6 Kata per Baris & Satu Ide per Meme:**
   - Baca kedua baris pada ukuran layar ponsel. Pangkas kata yang sekadar mengulang ekspresi di gambar.
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
Cari gagasan lewat `templates --query programmer`. Untuk merender teks, siapkan Pillow (`python -m pip install Pillow` jika belum tersedia), lalu gunakan gambar yang boleh dipakai atau pilih kanvas kosong. Untuk URL eksternal, lihat ID yang tersedia di [katalog memegen](https://api.memegen.link/templates/).

```bash
# Render teks Impact putih ber-stroke hitam di atas gambar lokal (mendukung Latin & CJK otomatis)
python skills/meme-studio-suite/scripts/msshi_meme_studio.py render-local --image base.png --top "KATANYA CUMA HOTFIX" --bottom "3 REPO IKUT REBUILD" --output out_meme.png

# Buat kartu meme dengan caption atas dan bawah pada kanvas kosong
python skills/meme-studio-suite/scripts/msshi_meme_studio.py render-local --canvas 900x600 --top "RENCANA: TIDUR JAM 10" --bottom "REALITA: DEBUG SAMPAI SUBUH" --output card_meme.png
```

### Jalur C — *Two-Step Custom Scene* + Papan A/B 6 Dimensi (`meme-lord` Lokal, Rp0)
Jika Pengguna ingin visual orisinal (bukan template stok):
1. **Langkah 1 (Clean Image Tanpa Teks):** Buat adegan visual ekspresif **tanpa teks sama sekali** memakai alat visual pilihan Pengguna sendiri (misal Blender MCP, kanvas lokal, atau generator gambar yang sudah disambungkan Pengguna). Jangan minta model gambar mengeja kalimat panjang agar bebas salah ketik.
2. **Langkah 2 (Local Impact Overlay):** Tempel caption presisi memakai `render-local`.
3. **Langkah 3 (A/B Testing Lokal 2–3 Kandidat):** Hasilkan 2–3 variasi caption/visual lalu buat lembar review HTML interaktif lokal:

```bash
python skills/meme-studio-suite/scripts/msshi_meme_studio.py ab-rate-html --title "Uji A/B Meme Rilis" --entry "Varian A" "meme_a.png" "Kontras ironis" --entry "Varian B" "meme_b.png" "Reaksi datar" --output ab_meme_review.html
```

Buka `ab_meme_review.html` di browser, lalu isi keenam angka 1–10 pada tiap gambar. Nilai konsep (30%), kualitas visual (25%), kecocokan format meme (20%), konsistensi (15%), kecepatan (5%), dan biaya (5%) menghasilkan skor gabungan. Angka awal dibiarkan kosong agar pilihanmu menentukan hasil. Pilih **Cetak hasil** untuk menyimpan PDF sebelum menutup halaman. Papan membaca gambar dari disk. Jika dibagikan, sertakan file gambarnya bersama HTML dengan susunan folder yang sama.

### Jalur D — Opsional BYOK `@createa/meme-mcp` (`createa-meme-skill`)
- Aktifkan ketika pengguna memilih layanan tersebut dan sudah memasang `CAM_API_KEY` miliknya. Kuota layanan mengikuti ketentuan penyedia.
- Jika `CAM_API_KEY` belum ada, **jangan memaksa pendaftaran** — langsung layani lewat Jalur A, B, atau C yang 100% gratis tanpa akun.

---

## 3. Kolaborasi Antar-Bot MSSHI

- **Yukino (`Tipe 1`):** Menangkap keluhan harian, momen kampus/kerja, atau ide mentah yang *relatable*.
- **Val (`Tipe 2`):** Menyuplai fakta akurat, tren topik, atau istilah teknis agar *punchline* cerdas dan valid.
- **Kiki-Chii (`Lead`):** Merumuskan *the turn*, memilih template paling pas, merender PNG, dan menyajikan 2–3 opsi A/B.
- **Sensei Shizuka (`Orkestrator`):** Menjaga keselarasan *brand voice* Pengguna dan gerbang anti-slop sebelum dipublikasikan.
