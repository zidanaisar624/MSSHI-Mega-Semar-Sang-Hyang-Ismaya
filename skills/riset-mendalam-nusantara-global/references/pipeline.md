# Pipeline Riset Mendalam 10 Tahap (Adaptif & Hemat Token)

Alur ini mengadopsi disiplin *multi-phase research pipeline* (rencana terstruktur, *adequacy gate*, kritik mandiri, *devil's advocate*, audit klaim/sitasi, dan *quality gate*) tanpa memerlukan server web, database vektor berat, atau UI eksternal — berjalan penuh di dalam percakapan Hermes bersama Val.

---

## Ringkasan 3 Mode Operasi

| Mode | Kapan Dipakai | Tahap yang Dijalankan | Perkiraan Hemat Token |
| --- | --- | --- | --- |
| **Quick** | Cek 1 konsep/metode atau 1–3 referensi cepat | Tahap 1 ringkas + 3 singkat + 9 | 1 giliran utama |
| **Standard** | Makalah kuliah, bab tinjauan pustaka, desain metode | Tahap 1, 3, 4, 5, 8, 9 | Ringkas, tanpa putaran revisi berulang |
| **Deep** | Skripsi/Tesis/Disertasi, jurnal SINTA/Scopus, systematic review | Tahap 1 s.d. 10 penuh (maks. 2 putaran revisi) | *Token-efficient chaining* (kirim ringkasan terstruktur, bukan tempel ulang teks mentah) |

---

## 10 Tahap Pipeline Mode Deep

### Tahap 1 — Perencanaan Riset (*Research Plan*)
Rumuskan dalam blok ringkas (maks. 12 baris):
1. **Pertanyaan riset utama** (PICO / SPIDER / RQ spesifik) dan batasan ruang lingkup (geografis Indonesia vs global, rentang tahun, mis. 5–10 tahun terakhir + karya klasik seminal).
2. **Sub-pertanyaan terpecah (3–5 cabang):** latar belakang & konteks lokal, landasan teori, studi empiris terkini, metode & instrumen, serta kontra-argumen/keterbatasan.
3. **Target keluaran:** Bab Skripsi/Tesis/Disertasi, naskah SINTA 1–6, atau artikel Scopus/WoS.

### Tahap 2 — Tesis Kerja & Peta Perspektif (*Working Thesis & Perspectives*)
- Susun **tesis kerja sementara** (*falsifiable*, bukan kesimpulan kaku sebelum bukti terkumpul).
- Daftar minimal **3 sudut pandang pemangku kepentingan / mazhab keilmuan** (mis. akademis teoretis, praktisi/kebijakan di Indonesia, dan kritik metodologis global) agar pencarian tidak bias konfirmasi.

### Tahap 3 — Investigasi Terarah & *Adequacy Gate*
- Jalankan pencarian per sub-pertanyaan secara bertahap (pada perangkat RAM rendah, lakukan berurutan bukan paralel masif).
- Terapkan **Lima Lapis Konteks**: baca judul → abstrak → metode & temuan → ekstrak hanya halaman yang relevan (`doc#halaman`).
- **Gerbang Kecukupan (*Adequacy Gate*):** sebelum menyusun draf, cek 4 syarat:
  1. Setiap sub-pertanyaan punya minimal 2 sumber primer/jurnal tepercaya?
  2. Ada sumber mutakhir (≤ 5 tahun) dan konteks Indonesia/global sesuai target?
  3. Ada data/bukti pembanding yang menentang tesis kerja?
  4. Jika ada celah nyata, lakukan **1 putaran pencarian tambahan** tepat di celah tersebut — jangan mengulang cabang yang sudah cukup.

### Tahap 4 — Kerangka Argumentasi (*Outline*)
- Susun struktur bab/bagian dengan **alur narasi sebab-akibat** (*problem → gap → framework → evidence → synthesis → limitation*), bukan sekadar daftar ringkasan artikel ("A mengatakan X, B mengatakan Y").
- Petakan penunjuk bukti (`[Penulis, Tahun | DOI / doc#hal]`) ke setiap sub-bab sebelum menulis paragraf.

### Tahap 5 — Penyusunan Draf (*Synthesized Draft*)
- Tulis draf sintesis dengan bahasa ilmiah jernih (EYD V untuk Indonesia atau *academic English* untuk global).
- Gunakan kalimat topik yang jelas di awal tiap paragraf, bandingkan antar-studi (kesepakatan, kontradiksi, celah metode), dan pisahkan tegas antara **fakta empiris** vs **interpretasi peneliti**.

### Tahap 6 — Kritik Mandiri Ketat (*Strict Self-Critique*)
Evaluasi draf secara objektif terhadap 5 sumbu:
1. **Ketajaman pertanyaan & koherensi argumen** — apakah setiap bagian menjawab RQ?
2. **Kedalaman metodologis** — apakah desain, sampel, variabel/tema, dan analisis selaras?
3. **Keseimbangan konteks Indonesia & global** — apakah teori internasional kontekstual dengan data/regulasi lokal?
4. **Kejelasan keterbatasan** — ancaman validitas internal/eksternal sudah diakui?
5. **Keringkasan** — buang repetisi, frasa klise, dan klaim berlebihan.

### Tahap 7 — Uji *Devil's Advocate* (Penantang Kritis)
- Posisikan diri sebagai **penguji sidang kritis / *reviewer* Q1 yang skeptis**.
- Ajukan 3–5 serangan terkuat:
  - *"Mengapa hasil ini tidak bisa dijelaskan oleh variabel pengganggu X?"*
  - *"Apa bukti bahwa celah riset ini benar-benar baru dan bukan keterbatasan pencarian kata kunci?"*
  - *"Apakah kesimpulan masih bertahan jika sampel atau konteks wilayah diubah?"*
- Jika tesis kerja goyah terhadap bukti penantang, **perbaiki tesis kerja secara jujur** sebelum lanjut.

### Tahap 8 — Audit Klaim (*Claim Audit*)
Periksa setiap klaim angka, persentase, tren, dan pernyataan kausal:
- `TERVERIFIKASI`: punya rujukan primer + angka/konteks cocok.
- `OVERCLAIM`: bukti korelasional ditulis seolah kausal → turunkan redaksi menjadi asosiatif/indikatif.
- `TIDAK BERBUKTI`: hapus atau tandai `[PERLU VERIFIKASI SUMBER]`.

### Tahap 9 — Audit Sitasi & DOI (*Citation Audit*)
- Pastikan setiap sitasi di tubuh teks muncul di daftar pustaka dan sebaliknya (*1-to-1 match*).
- Cek konsistensi tahun, ejaan nama penulis, nama jurnal, volume/nomor, dan format gaya selingkung (APA 7 / IEEE / Vancouver / Chicago sesuai target).
- Pastikan **0 DOI palsu** dan **0 artikel rekaan**. Tautan atau catatan sumber lokal dicatat jelas.

### Tahap 10 — Revisi Terarah & *Quality Gate* (Skor 1–10)
- Gabungkan temuan Tahap 6–9 ke dalam revisi bersih.
- Beri skor transparan (1–10) pada: *Akurasi Bukti*, *Ketajaman Metodologi*, *Sintesis & Kebaruan*, *Kepatuhan Standar Target*, dan *Keterbacaan*.
- **Aturan Berhenti (*Quality Gate*):** jika skor rata-rata ≥ 8 dan tidak ada temuan kritis di Audit Klaim/Sitasi → **SELESAI** dan serahkan hasil ke pengguna / Shizuka. Jika < 8, lakukan maksimal **1–2 putaran revisi** terfokus pada bagian terlemah saja (jangan menulis ulang dari nol agar hemat token).

---

## Aturan *Token-Efficient Chaining*
- Pada Tahap 6–10, rujuk nomor paragraf/klaim dan ringkasan tabel temuan, bukan menyalin ulang keseluruhan dokumen mentah di setiap giliran.
- Saat Val menyerahkan dossier ke Shizuka untuk dirakit ke Word (`muza-skripsi-template`), padatkan catatan internal seperlunya sambil mempertahankan **100% angka, kutipan langsung, penunjuk `doc#halaman`, dan DOI**.
