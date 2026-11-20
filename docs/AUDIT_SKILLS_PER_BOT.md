# Audit skill per bot MuZA

Sumber: [matriks bot](../configs/bot_role_and_skill_matrix.json). Jalankan `python scripts/render_bot_audit.py` setelah mengubah matriks.

Katalog berisi **69 skill bundel** dan **61 rujukan eksternal**. Skill bundel disertakan sebagai file instruksi. Rujukan eksternal menunjukkan kemampuan yang dituju dan perlu disiapkan terpisah sesuai host, izin, dan dependensi.

| Bot | Mandat | Bundel | Rujukan eksternal |
| --- | --- | ---: | ---: |
| Yukino Yukinoshita | Partner ideasi awal dan penampung ide | 23 | 9 |
| Sensei Shizuka Hiratsuka | Mastermind dan penerjemah hasil riset Val | 27 | 9 |
| Val | Spesialis riset murni, literatur S1–S3, dan intelijen data | 38 | 14 |
| Kiki-Chii | One-Woman Creative Studio | 22 | 44 |
| Shikaku Nara | Spesialis pemrograman, vibecoding, dan keamanan siber | 26 | 32 |

## Yukino Yukinoshita

Ide mentah, prioritas, energi, pilihan, dan pertanyaan untuk Shizuka. [Baca persona](../configs/personas/yukino.md).

| Skill atau rujukan | Status | Fungsi |
| --- | --- | --- |
| [`backward-traceability`](../skills/backward-traceability/SKILL.md) | Bundel | Menautkan angka dan hasil laporan kembali ke data, skrip, atau perhitungan. |
| [`brainstorming-research-ideas`](../skills/brainstorming-research-ideas/SKILL.md) | Bundel | Memakai kerangka ideasi terstruktur untuk menemukan pertanyaan layak. |
| [`business-sage`](../skills/business-sage/SKILL.md) | Bundel | Menyusun analisis usaha, skenario finansial, dan pertanyaan verifikasi aturan yang relevan. |
| [`chatgpt-hermes-portability-kit`](../skills/chatgpt-hermes-portability-kit/SKILL.md) | Bundel | Memandu adaptasi metode dan profil ke platform lain menggunakan sumber yang sah. |
| [`cli-anything-business-sage`](../skills/cli-anything-business-sage/SKILL.md) | Bundel | Menjalankan perhitungan bisnis terstruktur melalui harness lokal yang tersedia. |
| [`cli-anything-universal-bridge`](../skills/cli-anything-universal-bridge/SKILL.md) | Bundel | Daftarkan, periksa, dan jalankan rute aplikasi, browser, harness CLI-Anything, atau MCP Hermes saat tugas membutuhkannya. |
| [`creative-thinking-for-research`](../skills/creative-thinking-for-research/SKILL.md) | Bundel | Mencoba reframing, analogi, dan kombinasi konsep untuk membuka pilihan. |
| [`focus-my-energy`](../skills/focus-my-energy/SKILL.md) | Bundel | Menyesuaikan beban tugas dan langkah awal dengan energi yang dilaporkan pengguna. |
| [`generate-fresh-ideas`](../skills/generate-fresh-ideas/SKILL.md) | Bundel | Menghasilkan alternatif dari beberapa lensa kreatif untuk disaring pengguna. |
| [`humanizer-en`](../skills/humanizer-en/SKILL.md) | Bundel | Sunting prosa bahasa Inggris agar terasa alami sambil menjaga makna, suara penulis, dan sitasi. |
| [`humanizer-indonesia`](../skills/humanizer-indonesia/SKILL.md) | Bundel | Sunting prosa bahasa Indonesia sesuai ragam pembaca sambil menjaga makna, istilah, dan sitasi. |
| [`idea-generation`](../skills/idea-generation/SKILL.md) | Bundel | Mengembangkan dan menyaring gagasan penelitian dalam beberapa putaran. |
| [`match-my-writing-style`](../skills/match-my-writing-style/SKILL.md) | Bundel | Menerapkan Voice Card yang disediakan pengguna sesuai audiens dan jenis tulisan. |
| [`notebooklm-thinking-datascience`](../skills/notebooklm-thinking-datascience/SKILL.md) | Bundel | Mengadaptasi metode berpikir sistem dan data science dari indeks sumber milik pengguna. |
| [`parenting-6d-gad-mdd`](../skills/parenting-6d-gad-mdd/SKILL.md) | Bundel | Memandu percakapan dengan empati, struktur, dan dukungan otonomi. |
| [`persona-shizuka-yukino-shikaku`](../skills/persona-shizuka-yukino-shikaku/SKILL.md) | Bundel | Menjaga karakter, kontrak serah terima, dan batas kepemilikan tugas lima bot. |
| [`prep-for-meetings`](../skills/prep-for-meetings/SKILL.md) | Bundel | Menyusun ringkasan pertemuan dari catatan dan tujuan yang tersedia. |
| [`prep-for-meetings-2`](../skills/prep-for-meetings-2/SKILL.md) | Bundel | Memadatkan bahan pertemuan menjadi pokok bahasan dan kartu pengingat. |
| [`unlimited-ocr-2`](../skills/unlimited-ocr-2/SKILL.md) | Bundel | Rutekan ekstraksi dokumen dan gambar berhalaman ke OCR yang tersedia dengan penunjuk bukti. |
| [`career-ops`](../skills/career-ops/SKILL.md) | Bundel | Bantu karier, CV-lowongan skor 1-5, tracker dan wawancara sesuai konteks. |
| [`remote-jobs`](../skills/remote-jobs/SKILL.md) | Bundel | Saring direktori perusahaan remote, lalu periksa lowongan aktif ketika diminta. |
| [`mattpocock-engineering`](../skills/mattpocock-engineering/SKILL.md) | Bundel | Disiplin engineering, TDD, debugging dan spesifikasi; orkestrator/publikasi eksplisit. |
| [`harness2`](../skills/harness2/SKILL.md) | Bundel | Evaluasi harness Propose-Probe-Compose menggunakan demo deterministik dan proposal yang ditinjau manusia. |
| [`anti-slop`](https://github.com/miqdadbadjuber/anti-slop) | Eksternal | Memeriksa klise, struktur antarmuka, dan pola kode yang berulang. |
| [`cli-anything`](https://github.com/HKUDS/CLI-Anything) | Eksternal | Memanggil CLI atau aplikasi melalui adapter yang dipilih untuk tugas aktif. |
| [`cli-anything-catalog`](https://clianything.cc/) | Eksternal | Direktori untuk menemukan adapter CLI yang relevan dengan tugas. |
| [`graphify`](https://github.com/Graphify-Labs/graphify) | Eksternal | Membuat peta struktur proyek untuk penelusuran konteks. |
| [`hermes-jev-skills`](https://github.com/kerpopule/hermes-jev-skills) | Eksternal | Memilih skill dari konteks dengan pengalihan model dinonaktifkan. |
| [`token-monitor`](https://github.com/Javis603/token-monitor) | Eksternal | Sumber status kuota tambahan untuk kebijakan anggaran. |
| `tokenshield` | Eksternal | Menyatukan estimasi biaya, pembacaan penggunaan, dan batas cadangan berdasarkan data aktual. |
| [`tokentracker`](https://github.com/xiufengsun/TokenTracker) | Eksternal | Sumber data penggunaan lokal untuk kebijakan anggaran. |
| [`unlimited-ocr`](https://github.com/baidu/Unlimited-OCR) | Eksternal | Memandu runtime OCR lokal dan indeks halaman. |

## Sensei Shizuka Hiratsuka

Strategi, delegasi, pemilihan alur kerja, dan penjelasan akhir kepada pengguna. [Baca persona](../configs/personas/shizuka.md).

| Skill atau rujukan | Status | Fungsi |
| --- | --- | --- |
| [`autoresearch`](../skills/autoresearch/SKILL.md) | Bundel | Mengoordinasikan siklus eksperimen dan sintesis dengan batas berhenti. |
| [`backward-traceability`](../skills/backward-traceability/SKILL.md) | Bundel | Menautkan angka dan hasil laporan kembali ke data, skrip, atau perhitungan. |
| [`business-sage`](../skills/business-sage/SKILL.md) | Bundel | Menyusun analisis usaha, skenario finansial, dan pertanyaan verifikasi aturan yang relevan. |
| [`chatgpt-hermes-portability-kit`](../skills/chatgpt-hermes-portability-kit/SKILL.md) | Bundel | Memandu adaptasi metode dan profil ke platform lain menggunakan sumber yang sah. |
| [`cli-anything-business-sage`](../skills/cli-anything-business-sage/SKILL.md) | Bundel | Menjalankan perhitungan bisnis terstruktur melalui harness lokal yang tersedia. |
| [`cli-anything-universal-bridge`](../skills/cli-anything-universal-bridge/SKILL.md) | Bundel | Daftarkan, periksa, dan jalankan rute aplikasi, browser, harness CLI-Anything, atau MCP Hermes saat tugas membutuhkannya. |
| [`deep-research`](../skills/deep-research/SKILL.md) | Bundel | Menyusun pertanyaan, menelusuri literatur, dan mensintesis bukti yang dapat diperiksa. |
| [`get-more-perspectives`](../skills/get-more-perspectives/SKILL.md) | Bundel | Menguji keputusan dari beberapa sudut pandang sebelum memilih. |
| [`humanizer-en`](../skills/humanizer-en/SKILL.md) | Bundel | Sunting prosa bahasa Inggris agar terasa alami sambil menjaga makna, suara penulis, dan sitasi. |
| [`humanizer-indonesia`](../skills/humanizer-indonesia/SKILL.md) | Bundel | Sunting prosa bahasa Indonesia sesuai ragam pembaca sambil menjaga makna, istilah, dan sitasi. |
| [`literature-review`](../skills/literature-review/SKILL.md) | Bundel | Membangun tinjauan pustaka dengan beberapa perspektif dan jejak sumber. |
| [`match-my-writing-style`](../skills/match-my-writing-style/SKILL.md) | Bundel | Menerapkan Voice Card yang disediakan pengguna sesuai audiens dan jenis tulisan. |
| [`notebooklm-thinking-datascience`](../skills/notebooklm-thinking-datascience/SKILL.md) | Bundel | Mengadaptasi metode berpikir sistem dan data science dari indeks sumber milik pengguna. |
| [`novelty-assessment`](../skills/novelty-assessment/SKILL.md) | Bundel | Menguji klaim kebaruan terhadap studi terdekat dan batas pencarian. |
| [`paper-revision`](../skills/paper-revision/SKILL.md) | Bundel | Memetakan catatan revisi ke perubahan konkret dan bukti perbaikan. |
| [`paper-writing-section`](../skills/paper-writing-section/SKILL.md) | Bundel | Menyusun dan menyunting bagian naskah akademik dengan dua tahap pemeriksaan. |
| [`parenting-6d-gad-mdd`](../skills/parenting-6d-gad-mdd/SKILL.md) | Bundel | Memandu percakapan dengan empati, struktur, dan dukungan otonomi. |
| [`persona-shizuka-yukino-shikaku`](../skills/persona-shizuka-yukino-shikaku/SKILL.md) | Bundel | Menjaga karakter, kontrak serah terima, dan batas kepemilikan tugas lima bot. |
| [`rebuttal-writing`](../skills/rebuttal-writing/SKILL.md) | Bundel | Menyusun jawaban poin demi poin untuk masukan pembimbing atau reviewer. |
| [`research-paper-writing`](../skills/research-paper-writing/SKILL.md) | Bundel | Memeriksa struktur argumen dan hubungan antara klaim, bukti, serta pembahasan. |
| [`unlimited-ocr-2`](../skills/unlimited-ocr-2/SKILL.md) | Bundel | Rutekan ekstraksi dokumen dan gambar berhalaman ke OCR yang tersedia dengan penunjuk bukti. |
| [`wise-judgment-and-sovereign-orchestrator`](../skills/wise-judgment-and-sovereign-orchestrator/SKILL.md) | Bundel | Mengatur pilihan alur, anggaran, persetujuan, delegasi, dan sintesis hasil Val. |
| [`muza-skripsi-template`](../skills/muza-skripsi-template/SKILL.md) | Bundel | Menyusun template Word (.docx) skripsi/tugas akhir sesuai pedoman kampus, lookup logo & pejabat resmi, ekstrak aturan PDF, serta injeksi hasil MuZA_Search v1.1. |
| [`career-ops`](../skills/career-ops/SKILL.md) | Bundel | Bantu karier, CV-lowongan skor 1-5, tracker dan wawancara sesuai konteks. |
| [`remote-jobs`](../skills/remote-jobs/SKILL.md) | Bundel | Saring direktori perusahaan remote, lalu periksa lowongan aktif ketika diminta. |
| [`mattpocock-engineering`](../skills/mattpocock-engineering/SKILL.md) | Bundel | Disiplin engineering, TDD, debugging dan spesifikasi; orkestrator/publikasi eksplisit. |
| [`harness2`](../skills/harness2/SKILL.md) | Bundel | Evaluasi harness Propose-Probe-Compose menggunakan demo deterministik dan proposal yang ditinjau manusia. |
| [`anti-slop`](https://github.com/miqdadbadjuber/anti-slop) | Eksternal | Memeriksa klise, struktur antarmuka, dan pola kode yang berulang. |
| [`cli-anything`](https://github.com/HKUDS/CLI-Anything) | Eksternal | Memanggil CLI atau aplikasi melalui adapter yang dipilih untuk tugas aktif. |
| [`cli-anything-catalog`](https://clianything.cc/) | Eksternal | Direktori untuk menemukan adapter CLI yang relevan dengan tugas. |
| [`graphify`](https://github.com/Graphify-Labs/graphify) | Eksternal | Membuat peta struktur proyek untuk penelusuran konteks. |
| [`hermes-jev-skills`](https://github.com/kerpopule/hermes-jev-skills) | Eksternal | Memilih skill dari konteks dengan pengalihan model dinonaktifkan. |
| [`token-monitor`](https://github.com/Javis603/token-monitor) | Eksternal | Sumber status kuota tambahan untuk kebijakan anggaran. |
| `tokenshield` | Eksternal | Menyatukan estimasi biaya, pembacaan penggunaan, dan batas cadangan berdasarkan data aktual. |
| [`tokentracker`](https://github.com/xiufengsun/TokenTracker) | Eksternal | Sumber data penggunaan lokal untuk kebijakan anggaran. |
| [`unlimited-ocr`](https://github.com/baidu/Unlimited-OCR) | Eksternal | Memandu runtime OCR lokal dan indeks halaman. |

## Val

Bukti, metode, batas kepastian, serta dossier untuk Shizuka. [Baca persona](../configs/personas/val.md).

| Skill atau rujukan | Status | Fungsi |
| --- | --- | --- |
| [`backward-traceability`](../skills/backward-traceability/SKILL.md) | Bundel | Menautkan angka dan hasil laporan kembali ke data, skrip, atau perhitungan. |
| [`business-sage`](../skills/business-sage/SKILL.md) | Bundel | Menyusun analisis usaha, skenario finansial, dan pertanyaan verifikasi aturan yang relevan. |
| [`chatgpt-hermes-portability-kit`](../skills/chatgpt-hermes-portability-kit/SKILL.md) | Bundel | Memandu adaptasi metode dan profil ke platform lain menggunakan sumber yang sah. |
| [`cli-anything-business-sage`](../skills/cli-anything-business-sage/SKILL.md) | Bundel | Menjalankan perhitungan bisnis terstruktur melalui harness lokal yang tersedia. |
| [`cli-anything-universal-bridge`](../skills/cli-anything-universal-bridge/SKILL.md) | Bundel | Daftarkan, periksa, dan jalankan rute aplikasi, browser, harness CLI-Anything, atau MCP Hermes saat tugas membutuhkannya. |
| [`data-analysis`](../skills/data-analysis/SKILL.md) | Bundel | Memeriksa kualitas data, asumsi, uji statistik, dan ketidakpastian. |
| [`deep-research`](../skills/deep-research/SKILL.md) | Bundel | Menyusun pertanyaan, menelusuri literatur, dan mensintesis bukti yang dapat diperiksa. |
| [`firecrawl-competitive-intel`](../skills/firecrawl-competitive-intel/SKILL.md) | Bundel | Membandingkan perubahan produk, harga, dan fitur dengan bukti bertanggal. |
| [`firecrawl-dashboard-reporting`](../skills/firecrawl-dashboard-reporting/SKILL.md) | Bundel | Mengambil dan memeriksa indikator dasbor untuk pelaporan. |
| [`firecrawl-deep-research`](../skills/firecrawl-deep-research/SKILL.md) | Bundel | Mengumpulkan bukti web untuk sintesis dengan atribusi. |
| [`firecrawl-knowledge-base`](../skills/firecrawl-knowledge-base/SKILL.md) | Bundel | Menyiapkan koleksi dokumen, potongan, serta metadata asalnya. |
| [`firecrawl-research-papers`](../skills/firecrawl-research-papers/SKILL.md) | Bundel | Menemukan dan memeriksa makalah pada sumber akademik yang relevan. |
| [`github-research`](../skills/github-research/SKILL.md) | Bundel | Menelaah lisensi, rancangan, pemeliharaan, dan kesiapan repositori. |
| [`humanizer-en`](../skills/humanizer-en/SKILL.md) | Bundel | Sunting prosa bahasa Inggris agar terasa alami sambil menjaga makna, suara penulis, dan sitasi. |
| [`humanizer-indonesia`](../skills/humanizer-indonesia/SKILL.md) | Bundel | Sunting prosa bahasa Indonesia sesuai ragam pembaca sambil menjaga makna, istilah, dan sitasi. |
| [`literature-review`](../skills/literature-review/SKILL.md) | Bundel | Membangun tinjauan pustaka dengan beberapa perspektif dan jejak sumber. |
| [`match-my-writing-style`](../skills/match-my-writing-style/SKILL.md) | Bundel | Menerapkan Voice Card yang disediakan pengguna sesuai audiens dan jenis tulisan. |
| [`math-reasoning`](../skills/math-reasoning/SKILL.md) | Bundel | Memeriksa langkah penalaran matematika dan syarat berlakunya. |
| [`notebooklm-thinking-datascience`](../skills/notebooklm-thinking-datascience/SKILL.md) | Bundel | Mengadaptasi metode berpikir sistem dan data science dari indeks sumber milik pengguna. |
| [`novelty-assessment`](../skills/novelty-assessment/SKILL.md) | Bundel | Menguji klaim kebaruan terhadap studi terdekat dan batas pencarian. |
| [`paper-context-resolver`](../skills/paper-context-resolver/SKILL.md) | Bundel | Mengikat klaim reproduksi pada bagian, gambar, tabel, atau lampiran makalah. |
| [`paper-revision`](../skills/paper-revision/SKILL.md) | Bundel | Memetakan catatan revisi ke perubahan konkret dan bukti perbaikan. |
| [`paper-writing-section`](../skills/paper-writing-section/SKILL.md) | Bundel | Menyusun dan menyunting bagian naskah akademik dengan dua tahap pemeriksaan. |
| [`parenting-6d-gad-mdd`](../skills/parenting-6d-gad-mdd/SKILL.md) | Bundel | Memandu percakapan dengan empati, struktur, dan dukungan otonomi. |
| [`persona-shizuka-yukino-shikaku`](../skills/persona-shizuka-yukino-shikaku/SKILL.md) | Bundel | Menjaga karakter, kontrak serah terima, dan batas kepemilikan tugas lima bot. |
| [`rebuttal-writing`](../skills/rebuttal-writing/SKILL.md) | Bundel | Menyusun jawaban poin demi poin untuk masukan pembimbing atau reviewer. |
| [`research-paper-writing`](../skills/research-paper-writing/SKILL.md) | Bundel | Memeriksa struktur argumen dan hubungan antara klaim, bukti, serta pembahasan. |
| [`symbolic-equation`](../skills/symbolic-equation/SKILL.md) | Bundel | Mencari kandidat persamaan yang dapat ditafsirkan dan diuji. |
| [`table-generation`](../skills/table-generation/SKILL.md) | Bundel | Membangun tabel akademik dari hasil terverifikasi beserta satuan dan catatan. |
| [`unlimited-ocr-2`](../skills/unlimited-ocr-2/SKILL.md) | Bundel | Rutekan ekstraksi dokumen dan gambar berhalaman ke OCR yang tersedia dengan penunjuk bukti. |
| [`timesfm-forecasting`](../skills/timesfm-forecasting/SKILL.md) | Bundel | Prediksi deret waktu numerik lokal dengan TimesFM 2.5, validasi data dan evaluasi terpisah. |
| [`unslop`](../skills/unslop/SKILL.md) | Bundel | Audit dan perbaikan UI bertahap; Kiki arah visual, Val bukti dashboard, Coder implementasi. |
| [`scrapling`](../skills/scrapling/SKILL.md) | Bundel | Ekstraksi CSS/XPath dari HTML lokal dalam runtime parser terisolasi. |
| [`harness2`](../skills/harness2/SKILL.md) | Bundel | Evaluasi harness Propose-Probe-Compose menggunakan demo deterministik dan proposal yang ditinjau manusia. |
| [`muza-skripsi-template`](../skills/muza-skripsi-template/SKILL.md) | Bundel | Menyusun template Word (.docx) skripsi/tugas akhir sesuai pedoman kampus, lookup logo & pejabat resmi, ekstrak aturan PDF, serta injeksi hasil MuZA_Search v1.1. |
| [`career-ops`](../skills/career-ops/SKILL.md) | Bundel | Bantu karier, CV-lowongan skor 1-5, tracker dan wawancara sesuai konteks. |
| [`remote-jobs`](../skills/remote-jobs/SKILL.md) | Bundel | Saring direktori perusahaan remote, lalu periksa lowongan aktif ketika diminta. |
| [`mattpocock-engineering`](../skills/mattpocock-engineering/SKILL.md) | Bundel | Disiplin engineering, TDD, debugging dan spesifikasi; orkestrator/publikasi eksplisit. |
| [`anti-slop`](https://github.com/miqdadbadjuber/anti-slop) | Eksternal | Memeriksa klise, struktur antarmuka, dan pola kode yang berulang. |
| [`cli-anything`](https://github.com/HKUDS/CLI-Anything) | Eksternal | Memanggil CLI atau aplikasi melalui adapter yang dipilih untuk tugas aktif. |
| [`cli-anything-catalog`](https://clianything.cc/) | Eksternal | Direktori untuk menemukan adapter CLI yang relevan dengan tugas. |
| [`gpt-researcher`](https://github.com/assafelovic/gpt-researcher) | Eksternal | Mengumpulkan dan menyusun bahan riset; Val memeriksa sumber sebelum penyerahan. |
| [`graphify`](https://github.com/Graphify-Labs/graphify) | Eksternal | Membuat peta struktur proyek untuk penelusuran konteks. |
| [`hermes-jev-skills`](https://github.com/kerpopule/hermes-jev-skills) | Eksternal | Memilih skill dari konteks dengan pengalihan model dinonaktifkan. |
| [`token-monitor`](https://github.com/Javis603/token-monitor) | Eksternal | Sumber status kuota tambahan untuk kebijakan anggaran. |
| `tokenshield` | Eksternal | Menyatukan estimasi biaya, pembacaan penggunaan, dan batas cadangan berdasarkan data aktual. |
| [`tokentracker`](https://github.com/xiufengsun/TokenTracker) | Eksternal | Sumber data penggunaan lokal untuk kebijakan anggaran. |
| [`unlimited-ocr`](https://github.com/baidu/Unlimited-OCR) | Eksternal | Memandu runtime OCR lokal dan indeks halaman. |
| `artcraft-pdfcraft` | Eksternal | Membaca dan menyiapkan dokumen PDF riset melalui CLI lokal sesuai tiket tugas. |
| `artcraft-gridcraft` | Eksternal | Mengolah tabel/data spreadsheet melalui CLI lokal sesuai tiket tugas. |
| `artcraft-wordcraft` | Eksternal | Menyusun dokumen riset melalui CLI lokal sesuai tiket tugas. |
| `artcraft-deckcraft` | Eksternal | Menyusun presentasi riset melalui CLI lokal sesuai tiket tugas. |

## Kiki-Chii

Konsep, produksi kreatif, identitas visual, dan penyerahan aset. [Baca persona](../configs/personas/kiki-chii.md).

| Skill atau rujukan | Status | Fungsi |
| --- | --- | --- |
| [`academic-plotting`](../skills/academic-plotting/SKILL.md) | Bundel | Menghasilkan figur publikasi dari data dan spesifikasi yang disepakati. |
| [`auto-curiousity-for-film-making`](../skills/auto-curiousity-for-film-making/SKILL.md) | Bundel | Menguji kemampuan alat kreatif dan teknik produksi dalam eksperimen terpisah. |
| [`business-sage`](../skills/business-sage/SKILL.md) | Bundel | Menyusun analisis usaha, skenario finansial, dan pertanyaan verifikasi aturan yang relevan. |
| [`cli-anything-business-sage`](../skills/cli-anything-business-sage/SKILL.md) | Bundel | Menjalankan perhitungan bisnis terstruktur melalui harness lokal yang tersedia. |
| [`cli-anything-universal-bridge`](../skills/cli-anything-universal-bridge/SKILL.md) | Bundel | Daftarkan, periksa, dan jalankan rute aplikasi, browser, harness CLI-Anything, atau MCP Hermes saat tugas membutuhkannya. |
| [`filmmaking-videography-photography-s2`](../skills/filmmaking-videography-photography-s2/SKILL.md) | Bundel | Menyatukan konsep, pengarahan, kamera, foto, penyuntingan, warna, dan suara. |
| [`higgsfield-skills`](../skills/higgsfield-skills/SKILL.md) | Bundel | Rutekan kebutuhan produksi kreatif ke modul Higgsfield yang sesuai setelah konsep disetujui. |
| [`humanizer-en`](../skills/humanizer-en/SKILL.md) | Bundel | Sunting prosa bahasa Inggris agar terasa alami sambil menjaga makna, suara penulis, dan sitasi. |
| [`humanizer-indonesia`](../skills/humanizer-indonesia/SKILL.md) | Bundel | Sunting prosa bahasa Indonesia sesuai ragam pembaca sambil menjaga makna, istilah, dan sitasi. |
| [`match-my-writing-style`](../skills/match-my-writing-style/SKILL.md) | Bundel | Menerapkan Voice Card yang disediakan pengguna sesuai audiens dan jenis tulisan. |
| [`motion-graphics-suite`](../skills/motion-graphics-suite/SKILL.md) | Bundel | Pilih dan hubungkan empat rujukan motion graphics untuk komposisi yang tetap dapat diedit. |
| [`parenting-6d-gad-mdd`](../skills/parenting-6d-gad-mdd/SKILL.md) | Bundel | Memandu percakapan dengan empati, struktur, dan dukungan otonomi. |
| [`persona-shizuka-yukino-shikaku`](../skills/persona-shizuka-yukino-shikaku/SKILL.md) | Bundel | Menjaga karakter, kontrak serah terima, dan batas kepemilikan tugas lima bot. |
| [`slide-generation`](../skills/slide-generation/SKILL.md) | Bundel | Menyusun presentasi dari argumen, hasil, dan visual yang dapat diverifikasi. |
| [`unlimited-ocr-2`](../skills/unlimited-ocr-2/SKILL.md) | Bundel | Rutekan ekstraksi dokumen dan gambar berhalaman ke OCR yang tersedia dengan penunjuk bukti. |
| [`unslop`](../skills/unslop/SKILL.md) | Bundel | Audit dan perbaikan UI bertahap; Kiki arah visual, Val bukti dashboard, Coder implementasi. |
| [`brag`](../skills/brag/SKILL.md) | Bundel | Video peluncuran produk berbasis Hyperframes dengan Concepting First dan review manusia. |
| [`career-ops`](../skills/career-ops/SKILL.md) | Bundel | Bantu karier, CV-lowongan skor 1-5, tracker dan wawancara sesuai konteks. |
| [`remote-jobs`](../skills/remote-jobs/SKILL.md) | Bundel | Saring direktori perusahaan remote, lalu periksa lowongan aktif ketika diminta. |
| [`mattpocock-engineering`](../skills/mattpocock-engineering/SKILL.md) | Bundel | Disiplin engineering, TDD, debugging dan spesifikasi; orkestrator/publikasi eksplisit. |
| [`harness2`](../skills/harness2/SKILL.md) | Bundel | Evaluasi harness Propose-Probe-Compose menggunakan demo deterministik dan proposal yang ditinjau manusia. |
| [`rea-video`](../skills/rea-video/SKILL.md) | Bundel | Kiki membedah video referensi per shot ke VIDEO.md; model dan generasi merupakan opt-in terpisah. |
| [`anti-slop`](https://github.com/miqdadbadjuber/anti-slop) | Eksternal | Memeriksa klise, struktur antarmuka, dan pola kode yang berulang. |
| [`bang-motion`](https://github.com/bangtutorial/bang-motion) | Eksternal | Memandu motion graphics berbasis kode sesuai brief. |
| [`barty-motion-graphics`](https://github.com/Barty-Bart/motion-graphics) | Eksternal | Memandu komposisi grafis gerak dan animasi berbasis kode. |
| [`better-design`](https://github.com/marvkr/better-design) | Eksternal | Membantu tinjauan kualitas dan hierarki desain. |
| `blender-mcp` | Eksternal | Blender melalui CLI/native harness sesuai tiket tugas; nama katalog historis ini tidak mengaktifkan server MCP. |
| [`canvas-ui`](https://github.com/DavidHDev/canvas-ui) | Eksternal | Menelaah komponen visual berbasis kanvas untuk interaksi khusus. |
| [`charlie-motion-graphics`](https://github.com/charlie947/motion-graphics-skills) | Eksternal | Menyusun pendekatan motion graphics dan urutan gerak dari storyboard. |
| [`cli-anything`](https://github.com/HKUDS/CLI-Anything) | Eksternal | Memanggil CLI atau aplikasi melalui adapter yang dipilih untuk tugas aktif. |
| [`cli-anything-catalog`](https://clianything.cc/) | Eksternal | Direktori untuk menemukan adapter CLI yang relevan dengan tugas. |
| [`cursify`](https://github.com/ui-layouts/cursify) | Eksternal | Memilih interaksi kursor yang sesuai dengan kebutuhan antarmuka. |
| [`design-taste`](https://github.com/madebymustafa/design-taste) | Eksternal | Memilih gaya visual, tipografi, dan komposisi yang sesuai. |
| [`graphify`](https://github.com/Graphify-Labs/graphify) | Eksternal | Membuat peta struktur proyek untuk penelusuran konteks. |
| [`hermes-jev-skills`](https://github.com/kerpopule/hermes-jev-skills) | Eksternal | Memilih skill dari konteks dengan pengalihan model dinonaktifkan. |
| [`higgsfield-brandkit`](https://github.com/higgsfield-ai/skills) | Eksternal | Menerapkan sistem visual merek pada produksi aset. |
| [`higgsfield-faceless-video`](https://github.com/higgsfield-ai/skills) | Eksternal | Menyiapkan video tanpa tampil wajah dari skrip, tempo, dan aset. |
| [`higgsfield-generate`](https://github.com/higgsfield-ai/skills) | Eksternal | Menghasilkan atau mengolah media setelah konsep dan parameter disetujui. |
| [`higgsfield-marketplace-cards`](https://github.com/higgsfield-ai/skills) | Eksternal | Menyusun kartu promosi produk dengan pesan dan spesifikasi kanal. |
| [`higgsfield-product-photoshoot`](https://github.com/higgsfield-ai/skills) | Eksternal | Mengatur konsep foto produk, pencahayaan, dan framing. |
| [`higgsfield-soul-id`](https://github.com/higgsfield-ai/skills) | Eksternal | Mengelola konsistensi subjek dengan referensi yang diizinkan. |
| [`higgsfield-video-explainer`](https://github.com/higgsfield-ai/skills) | Eksternal | Mengubah penjelasan konsep menjadi urutan adegan. |
| [`higgsfield-websites`](https://github.com/higgsfield-ai/skills) | Eksternal | Memetakan brief produk ke konsep situs dan aset pendukung. |
| [`higgsfield-youtube-thumbnail`](https://github.com/higgsfield-ai/skills) | Eksternal | Membuat konsep thumbnail sesuai isi video dan identitas kanal. |
| [`motion-primitives`](https://github.com/ibelick/motion-primitives) | Eksternal | Merancang gerak antarmuka memakai komponen animasi. |
| [`paper-shaders`](https://github.com/paper-design/shaders) | Eksternal | Menyiapkan efek shader yang terukur dan sesuai perangkat. |
| [`remotion-skills`](https://github.com/remotion-dev/skills) | Eksternal | Merancang komposisi video sebagai kode dan merendernya bila runtime tersedia. |
| [`superdesign-skill`](https://github.com/superdesigndev/superdesign-skill) | Eksternal | Menilai tata letak, token desain, dan konsistensi antarmuka. |
| [`token-monitor`](https://github.com/Javis603/token-monitor) | Eksternal | Sumber status kuota tambahan untuk kebijakan anggaran. |
| `tokenshield` | Eksternal | Menyatukan estimasi biaya, pembacaan penggunaan, dan batas cadangan berdasarkan data aktual. |
| [`tokentracker`](https://github.com/xiufengsun/TokenTracker) | Eksternal | Sumber data penggunaan lokal untuk kebijakan anggaran. |
| [`unlimited-ocr`](https://github.com/baidu/Unlimited-OCR) | Eksternal | Memandu runtime OCR lokal dan indeks halaman. |
| `artcraft-anicraft` | Eksternal | Animasi dan komposisi bergerak melalui CLI aplikasi lokal sesuai tiket tugas. |
| `artcraft-filmcraft` | Eksternal | Penyuntingan dan komposisi video melalui CLI lokal sesuai tiket tugas. |
| `artcraft-effectcraft` | Eksternal | Efek visual/compositing melalui CLI lokal sesuai tiket tugas. |
| `artcraft-soundcraft` | Eksternal | Penyuntingan dan pengolahan audio melalui CLI lokal sesuai tiket tugas. |
| `artcraft-photocraft` | Eksternal | Penyuntingan foto/gambar melalui CLI lokal sesuai tiket tugas. |
| `artcraft-lightcraft` | Eksternal | Pengolahan foto/RAW melalui CLI lokal sesuai tiket tugas; aplikasi tidak dibuka saat boot. |
| `artcraft-designcraft` | Eksternal | Desain aset visual melalui CLI lokal sesuai tiket tugas. |
| `artcraft-figcraft` | Eksternal | Rancangan UI/prototipe melalui CLI lokal; hanya Shikaku dan Kiki-Chii berbagi rute ini. |
| `artcraft-vectorcraft` | Eksternal | Penyuntingan aset vektor melalui CLI lokal sesuai tiket tugas. |
| `artcraft-cadcraft` | Eksternal | Rancangan CAD melalui CLI lokal sesuai tiket tugas. |
| `artcraft-solidcraft` | Eksternal | Pemodelan bentuk padat melalui CLI lokal sesuai tiket tugas. |
| `artcraft-materialcraft` | Eksternal | Penyusunan material melalui CLI lokal sesuai tiket tugas. |
| `artcraft-texturecraft` | Eksternal | Penyusunan tekstur melalui CLI lokal sesuai tiket tugas. |
| [`imagination-studio`](https://github.com/Keys-Wasserman/Imagination-Studio-by-keys-Wasserman) | Eksternal | Opsional untuk Kiki-Chii (Content Creator / Filmmaker): kolaborasi Slate & antrean render lokal Imagination Studio (gambar, klip+suara, voice, musik, SFX) via plugin Hermes atau stdio MCP (127.0.0.1:7870). |

## Shikaku Nara

Arsitektur, kode, pengujian, serta pemeriksaan keamanan dalam lingkup yang diizinkan. [Baca persona](../configs/personas/shikaku.md).

| Skill atau rujukan | Status | Fungsi |
| --- | --- | --- |
| [`ai-research-explore`](../skills/ai-research-explore/SKILL.md) | Bundel | Merancang eksperimen kandidat yang terpisah dari baseline. |
| [`ai-research-reproduction`](../skills/ai-research-reproduction/SKILL.md) | Bundel | Menetapkan target reproduksi penelitian yang dapat dibuktikan. |
| [`analyze-project`](../skills/analyze-project/SKILL.md) | Bundel | Memetakan struktur proyek, konfigurasi, titik masuk, dan risiko perubahan. |
| [`antigravity-webdev-cybersec`](../skills/antigravity-webdev-cybersec/SKILL.md) | Bundel | Hubungkan pengerjaan web dan evaluasi keamanan terotorisasi dengan Antigravity, Goose, dan alat lokal. |
| [`cli-anything-universal-bridge`](../skills/cli-anything-universal-bridge/SKILL.md) | Bundel | Daftarkan, periksa, dan jalankan rute aplikasi, browser, harness CLI-Anything, atau MCP Hermes saat tugas membutuhkannya. |
| [`evaluating-code-models`](../skills/evaluating-code-models/SKILL.md) | Bundel | Menguji keluaran model kode dengan tugas dan tolok ukur yang relevan. |
| [`evaluating-llms-harness`](../skills/evaluating-llms-harness/SKILL.md) | Bundel | Mengatur dan menilai evaluasi LLM dengan harness pengujian yang kompatibel. |
| [`explore-code`](../skills/explore-code/SKILL.md) | Bundel | Mengembangkan perubahan eksperimen dalam ruang kerja terisolasi. |
| [`explore-run`](../skills/explore-run/SKILL.md) | Bundel | Menjalankan uji terbatas dengan anggaran dan catatan hasil yang jelas. |
| [`humanizer-en`](../skills/humanizer-en/SKILL.md) | Bundel | Sunting prosa bahasa Inggris agar terasa alami sambil menjaga makna, suara penulis, dan sitasi. |
| [`humanizer-indonesia`](../skills/humanizer-indonesia/SKILL.md) | Bundel | Sunting prosa bahasa Indonesia sesuai ragam pembaca sambil menjaga makna, istilah, dan sitasi. |
| [`langsmith-observability`](../skills/langsmith-observability/SKILL.md) | Bundel | Memandu observabilitas dan evaluasi LangSmith pada lingkungan yang disetujui. |
| [`match-my-writing-style`](../skills/match-my-writing-style/SKILL.md) | Bundel | Menerapkan Voice Card yang disediakan pengguna sesuai audiens dan jenis tulisan. |
| [`nemo-evaluator-sdk`](../skills/nemo-evaluator-sdk/SKILL.md) | Bundel | Memandu evaluasi dengan NeMo Evaluator SDK jika dependensinya tersedia. |
| [`parenting-6d-gad-mdd`](../skills/parenting-6d-gad-mdd/SKILL.md) | Bundel | Memandu percakapan dengan empati, struktur, dan dukungan otonomi. |
| [`persona-shizuka-yukino-shikaku`](../skills/persona-shizuka-yukino-shikaku/SKILL.md) | Bundel | Menjaga karakter, kontrak serah terima, dan batas kepemilikan tugas lima bot. |
| [`phoenix-observability`](../skills/phoenix-observability/SKILL.md) | Bundel | Memandu tracing dan evaluasi Phoenix tanpa memindahkan data di luar lingkup. |
| [`unlimited-ocr-2`](../skills/unlimited-ocr-2/SKILL.md) | Bundel | Rutekan ekstraksi dokumen dan gambar berhalaman ke OCR yang tersedia dengan penunjuk bukti. |
| [`unslop`](../skills/unslop/SKILL.md) | Bundel | Audit dan perbaikan UI bertahap; Kiki arah visual, Val bukti dashboard, Coder implementasi. |
| [`scrapling`](../skills/scrapling/SKILL.md) | Bundel | Ekstraksi CSS/XPath dari HTML lokal dalam runtime parser terisolasi. |
| [`harness2`](../skills/harness2/SKILL.md) | Bundel | Evaluasi harness Propose-Probe-Compose menggunakan demo deterministik dan proposal yang ditinjau manusia. |
| [`career-ops`](../skills/career-ops/SKILL.md) | Bundel | Bantu karier, CV-lowongan skor 1-5, tracker dan wawancara sesuai konteks. |
| [`remote-jobs`](../skills/remote-jobs/SKILL.md) | Bundel | Saring direktori perusahaan remote, lalu periksa lowongan aktif ketika diminta. |
| [`mattpocock-engineering`](../skills/mattpocock-engineering/SKILL.md) | Bundel | Disiplin engineering, TDD, debugging dan spesifikasi; orkestrator/publikasi eksplisit. |
| [`grim-prompter`](../skills/grim-prompter/SKILL.md) | Bundel | Pemodelan ancaman berbasis bukti (36 arsitektur, 29 metode, STRIDE/PASTA/LINDDUN/privasi) untuk Coder secara read-only. |
| [`claude-bughunter`](../skills/claude-bughunter/SKILL.md) | Bundel | Audit kerentanan, triage, validasi bukti, dan pelaporan keamanan terotorisasi (83 skill, 15 command, 681 pola laporan) untuk Coder. |
| [`addy-agent-skills`](https://github.com/addyosmani/agent-skills) | Eksternal | Menerapkan praktik engineering pada implementasi dan review. |
| [`anti-slop`](https://github.com/miqdadbadjuber/anti-slop) | Eksternal | Memeriksa klise, struktur antarmuka, dan pola kode yang berulang. |
| [`awesome-copilot`](https://github.com/github/awesome-copilot) | Eksternal | Memilih contoh instruksi dan praktik pengembangan yang dapat diadaptasi. |
| [`bang-motion`](https://github.com/bangtutorial/bang-motion) | Eksternal | Memandu motion graphics berbasis kode sesuai brief. |
| [`better-design`](https://github.com/marvkr/better-design) | Eksternal | Membantu tinjauan kualitas dan hierarki desain. |
| [`canvas-ui`](https://github.com/DavidHDev/canvas-ui) | Eksternal | Menelaah komponen visual berbasis kanvas untuk interaksi khusus. |
| [`cli-anything`](https://github.com/HKUDS/CLI-Anything) | Eksternal | Memanggil CLI atau aplikasi melalui adapter yang dipilih untuk tugas aktif. |
| [`cli-anything-catalog`](https://clianything.cc/) | Eksternal | Direktori untuk menemukan adapter CLI yang relevan dengan tugas. |
| [`cursify`](https://github.com/ui-layouts/cursify) | Eksternal | Memilih interaksi kursor yang sesuai dengan kebutuhan antarmuka. |
| [`cybersecurity-library`](https://github.com/mukul975/anthropic-cybersecurity-skills) | Eksternal | Menemukan panduan keamanan sesuai lingkup audit yang sah. |
| [`design-taste`](https://github.com/madebymustafa/design-taste) | Eksternal | Memilih gaya visual, tipografi, dan komposisi yang sesuai. |
| [`goose`](https://github.com/aaif-goose/goose) | Eksternal | Menjalankan siklus perubahan kode dan pengujian bila harness Goose tersedia. |
| [`graphify`](https://github.com/Graphify-Labs/graphify) | Eksternal | Membuat peta struktur proyek untuk penelusuran konteks. |
| [`hermes-jev-skills`](https://github.com/kerpopule/hermes-jev-skills) | Eksternal | Memilih skill dari konteks dengan pengalihan model dinonaktifkan. |
| [`higgsfield-websites`](https://github.com/higgsfield-ai/skills) | Eksternal | Memetakan brief produk ke konsep situs dan aset pendukung. |
| [`mindrally-skills`](https://github.com/mindrally/skills) | Eksternal | Menemukan panduan implementasi relevan di katalog eksternal. |
| [`motion-primitives`](https://github.com/ibelick/motion-primitives) | Eksternal | Merancang gerak antarmuka memakai komponen animasi. |
| [`paper-shaders`](https://github.com/paper-design/shaders) | Eksternal | Menyiapkan efek shader yang terukur dan sesuai perangkat. |
| [`playwright-best-practices`](https://github.com/currents-dev/playwright-best-practices-skill) | Eksternal | Menguji jalur pengguna dan memperbaiki kestabilan tes E2E. |
| [`ponytail`](https://github.com/dietrichgebert/ponytail) | Eksternal | Mengurangi kerumitan solusi dan memilih perubahan yang sesuai kebutuhan. |
| [`rea`](https://github.com/morluto/rea) | Eksternal | Opsional: analisis reverse engineering lokal melalui CLI dengan bukti dan batas provider native. |
| [`remotion-skills`](https://github.com/remotion-dev/skills) | Eksternal | Merancang komposisi video sebagai kode dan merendernya bila runtime tersedia. |
| [`reverse-engineer-anything`](https://github.com/NabilRFG12/Reverse-Engineer-anything) | Eksternal | Memeriksa artefak insiden secara forensik dalam mandat yang jelas. |
| [`strix`](https://github.com/usestrix/strix) | Eksternal | Menguji keamanan target yang lingkup dan izin aksesnya telah disetujui. |
| [`superdesign-skill`](https://github.com/superdesigndev/superdesign-skill) | Eksternal | Menilai tata letak, token desain, dan konsistensi antarmuka. |
| [`superpowers`](https://github.com/obra/superpowers) | Eksternal | Menata perencanaan, implementasi, dan validasi perubahan kode. |
| [`token-monitor`](https://github.com/Javis603/token-monitor) | Eksternal | Sumber status kuota tambahan untuk kebijakan anggaran. |
| `tokenshield` | Eksternal | Menyatukan estimasi biaya, pembacaan penggunaan, dan batas cadangan berdasarkan data aktual. |
| [`tokentracker`](https://github.com/xiufengsun/TokenTracker) | Eksternal | Sumber data penggunaan lokal untuk kebijakan anggaran. |
| [`unlimited-ocr`](https://github.com/baidu/Unlimited-OCR) | Eksternal | Memandu runtime OCR lokal dan indeks halaman. |
| `artcraft-craftanything` | Eksternal | Menggunakan agen aplikasi lokal untuk tugas coding yang dipilih; tidak menjalankan setup --client hermes atau mode MCP. |
| `artcraft-figcraft` | Eksternal | Rancangan UI/prototipe melalui CLI lokal; hanya Shikaku dan Kiki-Chii berbagi rute ini. |

## Kelompok distribusi

### Semua bot

- **Yukino Yukinoshita, Sensei Shizuka Hiratsuka, Val, Kiki-Chii, Shikaku Nara** — [`anti-slop`](https://github.com/miqdadbadjuber/anti-slop), [`career-ops`](../skills/career-ops/SKILL.md), [`cli-anything`](https://github.com/HKUDS/CLI-Anything), [`cli-anything-catalog`](https://clianything.cc/), [`cli-anything-universal-bridge`](../skills/cli-anything-universal-bridge/SKILL.md), [`graphify`](https://github.com/Graphify-Labs/graphify), [`harness2`](../skills/harness2/SKILL.md), [`hermes-jev-skills`](https://github.com/kerpopule/hermes-jev-skills), [`humanizer-en`](../skills/humanizer-en/SKILL.md), [`humanizer-indonesia`](../skills/humanizer-indonesia/SKILL.md), [`match-my-writing-style`](../skills/match-my-writing-style/SKILL.md), [`mattpocock-engineering`](../skills/mattpocock-engineering/SKILL.md), [`parenting-6d-gad-mdd`](../skills/parenting-6d-gad-mdd/SKILL.md), [`persona-shizuka-yukino-shikaku`](../skills/persona-shizuka-yukino-shikaku/SKILL.md), [`remote-jobs`](../skills/remote-jobs/SKILL.md), [`token-monitor`](https://github.com/Javis603/token-monitor), `tokenshield`, [`tokentracker`](https://github.com/xiufengsun/TokenTracker), [`unlimited-ocr`](https://github.com/baidu/Unlimited-OCR), [`unlimited-ocr-2`](../skills/unlimited-ocr-2/SKILL.md)

### Beberapa bot

- **Kiki-Chii, Shikaku Nara** — `artcraft-figcraft`, [`bang-motion`](https://github.com/bangtutorial/bang-motion), [`better-design`](https://github.com/marvkr/better-design), [`canvas-ui`](https://github.com/DavidHDev/canvas-ui), [`cursify`](https://github.com/ui-layouts/cursify), [`design-taste`](https://github.com/madebymustafa/design-taste), [`higgsfield-websites`](https://github.com/higgsfield-ai/skills), [`motion-primitives`](https://github.com/ibelick/motion-primitives), [`paper-shaders`](https://github.com/paper-design/shaders), [`remotion-skills`](https://github.com/remotion-dev/skills), [`superdesign-skill`](https://github.com/superdesigndev/superdesign-skill)
- **Yukino Yukinoshita, Sensei Shizuka Hiratsuka, Val** — [`backward-traceability`](../skills/backward-traceability/SKILL.md), [`chatgpt-hermes-portability-kit`](../skills/chatgpt-hermes-portability-kit/SKILL.md), [`notebooklm-thinking-datascience`](../skills/notebooklm-thinking-datascience/SKILL.md)
- **Yukino Yukinoshita, Sensei Shizuka Hiratsuka, Val, Kiki-Chii** — [`business-sage`](../skills/business-sage/SKILL.md), [`cli-anything-business-sage`](../skills/cli-anything-business-sage/SKILL.md)
- **Sensei Shizuka Hiratsuka, Val** — [`deep-research`](../skills/deep-research/SKILL.md), [`literature-review`](../skills/literature-review/SKILL.md), [`muza-skripsi-template`](../skills/muza-skripsi-template/SKILL.md), [`novelty-assessment`](../skills/novelty-assessment/SKILL.md), [`paper-revision`](../skills/paper-revision/SKILL.md), [`paper-writing-section`](../skills/paper-writing-section/SKILL.md), [`rebuttal-writing`](../skills/rebuttal-writing/SKILL.md), [`research-paper-writing`](../skills/research-paper-writing/SKILL.md)
- **Val, Shikaku Nara** — [`scrapling`](../skills/scrapling/SKILL.md)
- **Val, Kiki-Chii, Shikaku Nara** — [`unslop`](../skills/unslop/SKILL.md)

### Khusus satu bot

- **Kiki-Chii** — [`academic-plotting`](../skills/academic-plotting/SKILL.md), `artcraft-anicraft`, `artcraft-cadcraft`, `artcraft-designcraft`, `artcraft-effectcraft`, `artcraft-filmcraft`, `artcraft-lightcraft`, `artcraft-materialcraft`, `artcraft-photocraft`, `artcraft-solidcraft`, `artcraft-soundcraft`, `artcraft-texturecraft`, `artcraft-vectorcraft`, [`auto-curiousity-for-film-making`](../skills/auto-curiousity-for-film-making/SKILL.md), [`barty-motion-graphics`](https://github.com/Barty-Bart/motion-graphics), `blender-mcp`, [`brag`](../skills/brag/SKILL.md), [`charlie-motion-graphics`](https://github.com/charlie947/motion-graphics-skills), [`filmmaking-videography-photography-s2`](../skills/filmmaking-videography-photography-s2/SKILL.md), [`higgsfield-brandkit`](https://github.com/higgsfield-ai/skills), [`higgsfield-faceless-video`](https://github.com/higgsfield-ai/skills), [`higgsfield-generate`](https://github.com/higgsfield-ai/skills), [`higgsfield-marketplace-cards`](https://github.com/higgsfield-ai/skills), [`higgsfield-product-photoshoot`](https://github.com/higgsfield-ai/skills), [`higgsfield-skills`](../skills/higgsfield-skills/SKILL.md), [`higgsfield-soul-id`](https://github.com/higgsfield-ai/skills), [`higgsfield-video-explainer`](https://github.com/higgsfield-ai/skills), [`higgsfield-youtube-thumbnail`](https://github.com/higgsfield-ai/skills), [`imagination-studio`](https://github.com/Keys-Wasserman/Imagination-Studio-by-keys-Wasserman), [`motion-graphics-suite`](../skills/motion-graphics-suite/SKILL.md), [`rea-video`](../skills/rea-video/SKILL.md), [`slide-generation`](../skills/slide-generation/SKILL.md)
- **Shikaku Nara** — [`addy-agent-skills`](https://github.com/addyosmani/agent-skills), [`ai-research-explore`](../skills/ai-research-explore/SKILL.md), [`ai-research-reproduction`](../skills/ai-research-reproduction/SKILL.md), [`analyze-project`](../skills/analyze-project/SKILL.md), [`antigravity-webdev-cybersec`](../skills/antigravity-webdev-cybersec/SKILL.md), `artcraft-craftanything`, [`awesome-copilot`](https://github.com/github/awesome-copilot), [`claude-bughunter`](../skills/claude-bughunter/SKILL.md), [`cybersecurity-library`](https://github.com/mukul975/anthropic-cybersecurity-skills), [`evaluating-code-models`](../skills/evaluating-code-models/SKILL.md), [`evaluating-llms-harness`](../skills/evaluating-llms-harness/SKILL.md), [`explore-code`](../skills/explore-code/SKILL.md), [`explore-run`](../skills/explore-run/SKILL.md), [`goose`](https://github.com/aaif-goose/goose), [`grim-prompter`](../skills/grim-prompter/SKILL.md), [`langsmith-observability`](../skills/langsmith-observability/SKILL.md), [`mindrally-skills`](https://github.com/mindrally/skills), [`nemo-evaluator-sdk`](../skills/nemo-evaluator-sdk/SKILL.md), [`phoenix-observability`](../skills/phoenix-observability/SKILL.md), [`playwright-best-practices`](https://github.com/currents-dev/playwright-best-practices-skill), [`ponytail`](https://github.com/dietrichgebert/ponytail), [`rea`](https://github.com/morluto/rea), [`reverse-engineer-anything`](https://github.com/NabilRFG12/Reverse-Engineer-anything), [`strix`](https://github.com/usestrix/strix), [`superpowers`](https://github.com/obra/superpowers)
- **Val** — `artcraft-deckcraft`, `artcraft-gridcraft`, `artcraft-pdfcraft`, `artcraft-wordcraft`, [`data-analysis`](../skills/data-analysis/SKILL.md), [`firecrawl-competitive-intel`](../skills/firecrawl-competitive-intel/SKILL.md), [`firecrawl-dashboard-reporting`](../skills/firecrawl-dashboard-reporting/SKILL.md), [`firecrawl-deep-research`](../skills/firecrawl-deep-research/SKILL.md), [`firecrawl-knowledge-base`](../skills/firecrawl-knowledge-base/SKILL.md), [`firecrawl-research-papers`](../skills/firecrawl-research-papers/SKILL.md), [`github-research`](../skills/github-research/SKILL.md), [`gpt-researcher`](https://github.com/assafelovic/gpt-researcher), [`math-reasoning`](../skills/math-reasoning/SKILL.md), [`paper-context-resolver`](../skills/paper-context-resolver/SKILL.md), [`symbolic-equation`](../skills/symbolic-equation/SKILL.md), [`table-generation`](../skills/table-generation/SKILL.md), [`timesfm-forecasting`](../skills/timesfm-forecasting/SKILL.md)
- **Sensei Shizuka Hiratsuka** — [`autoresearch`](../skills/autoresearch/SKILL.md), [`get-more-perspectives`](../skills/get-more-perspectives/SKILL.md), [`wise-judgment-and-sovereign-orchestrator`](../skills/wise-judgment-and-sovereign-orchestrator/SKILL.md)
- **Yukino Yukinoshita** — [`brainstorming-research-ideas`](../skills/brainstorming-research-ideas/SKILL.md), [`creative-thinking-for-research`](../skills/creative-thinking-for-research/SKILL.md), [`focus-my-energy`](../skills/focus-my-energy/SKILL.md), [`generate-fresh-ideas`](../skills/generate-fresh-ideas/SKILL.md), [`idea-generation`](../skills/idea-generation/SKILL.md), [`prep-for-meetings`](../skills/prep-for-meetings/SKILL.md), [`prep-for-meetings-2`](../skills/prep-for-meetings-2/SKILL.md)

## Pemetaan untuk Antigravity

Target kerja Shikaku dengan dukungan kreatif Kiki-Chii.

- **Bundel** — [`ai-research-explore`](../skills/ai-research-explore/SKILL.md), [`ai-research-reproduction`](../skills/ai-research-reproduction/SKILL.md), [`analyze-project`](../skills/analyze-project/SKILL.md), [`antigravity-webdev-cybersec`](../skills/antigravity-webdev-cybersec/SKILL.md), [`evaluating-code-models`](../skills/evaluating-code-models/SKILL.md), [`evaluating-llms-harness`](../skills/evaluating-llms-harness/SKILL.md), [`explore-code`](../skills/explore-code/SKILL.md), [`explore-run`](../skills/explore-run/SKILL.md), [`filmmaking-videography-photography-s2`](../skills/filmmaking-videography-photography-s2/SKILL.md), [`humanizer-en`](../skills/humanizer-en/SKILL.md), [`humanizer-indonesia`](../skills/humanizer-indonesia/SKILL.md), [`langsmith-observability`](../skills/langsmith-observability/SKILL.md), [`match-my-writing-style`](../skills/match-my-writing-style/SKILL.md), [`nemo-evaluator-sdk`](../skills/nemo-evaluator-sdk/SKILL.md), [`parenting-6d-gad-mdd`](../skills/parenting-6d-gad-mdd/SKILL.md), [`persona-shizuka-yukino-shikaku`](../skills/persona-shizuka-yukino-shikaku/SKILL.md), [`phoenix-observability`](../skills/phoenix-observability/SKILL.md), [`unlimited-ocr-2`](../skills/unlimited-ocr-2/SKILL.md), [`muza-skripsi-template`](../skills/muza-skripsi-template/SKILL.md), [`mattpocock-engineering`](../skills/mattpocock-engineering/SKILL.md), [`career-ops`](../skills/career-ops/SKILL.md), [`grim-prompter`](../skills/grim-prompter/SKILL.md), [`claude-bughunter`](../skills/claude-bughunter/SKILL.md)
- **Rujukan eksternal** — [`addy-agent-skills`](https://github.com/addyosmani/agent-skills), [`anti-slop`](https://github.com/miqdadbadjuber/anti-slop), [`awesome-copilot`](https://github.com/github/awesome-copilot), [`bang-motion`](https://github.com/bangtutorial/bang-motion), [`better-design`](https://github.com/marvkr/better-design), [`canvas-ui`](https://github.com/DavidHDev/canvas-ui), [`cli-anything`](https://github.com/HKUDS/CLI-Anything), [`cli-anything-catalog`](https://clianything.cc/), [`cursify`](https://github.com/ui-layouts/cursify), [`cybersecurity-library`](https://github.com/mukul975/anthropic-cybersecurity-skills), [`design-taste`](https://github.com/madebymustafa/design-taste), [`goose`](https://github.com/aaif-goose/goose), [`graphify`](https://github.com/Graphify-Labs/graphify), [`hermes-jev-skills`](https://github.com/kerpopule/hermes-jev-skills), [`higgsfield-websites`](https://github.com/higgsfield-ai/skills), [`mindrally-skills`](https://github.com/mindrally/skills), [`motion-primitives`](https://github.com/ibelick/motion-primitives), [`paper-shaders`](https://github.com/paper-design/shaders), [`playwright-best-practices`](https://github.com/currents-dev/playwright-best-practices-skill), [`ponytail`](https://github.com/dietrichgebert/ponytail), [`rea`](https://github.com/morluto/rea), [`remotion-skills`](https://github.com/remotion-dev/skills), [`reverse-engineer-anything`](https://github.com/NabilRFG12/Reverse-Engineer-anything), [`strix`](https://github.com/usestrix/strix), [`superdesign-skill`](https://github.com/superdesigndev/superdesign-skill), [`superpowers`](https://github.com/obra/superpowers), [`token-monitor`](https://github.com/Javis603/token-monitor), `tokenshield`, [`tokentracker`](https://github.com/xiufengsun/TokenTracker), [`unlimited-ocr`](https://github.com/baidu/Unlimited-OCR)

Pemetaan ini menjelaskan ruang kerja yang dituju. Ikuti panduan host untuk lokasi pemasangan dan gunakan skill yang diaktifkan untuk proyek.
