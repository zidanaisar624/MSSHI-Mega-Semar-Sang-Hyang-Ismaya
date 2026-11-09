# Audit skill per bot MuZA

Sumber: [matriks bot](../configs/bot_role_and_skill_matrix.json). Jalankan `python scripts/render_bot_audit.py` setelah mengubah matriks.

Katalog berisi **50 skill bundel** dan **63 rujukan eksternal**. Skill bundel disertakan sebagai file instruksi. Rujukan eksternal menunjukkan kemampuan yang dituju dan perlu disiapkan terpisah sesuai host, izin, dan dependensi.

| Bot | Mandat | Bundel | Rujukan eksternal |
| --- | --- | ---: | ---: |
| Yukino Yukinoshita | Partner ideasi awal dan penampung ide | 22 | 14 |
| Sensei Shizuka Hiratsuka | Mastermind dan penerjemah hasil riset Val | 18 | 14 |
| Val | Spesialis riset murni, literatur S1–S3, dan intelijen data | 26 | 15 |
| Kiki-Chii | One-Woman Creative Studio | 9 | 51 |
| Shikaku Nara | Spesialis pemrograman, vibecoding, dan keamanan siber | 13 | 34 |

## Yukino Yukinoshita

Ide mentah, prioritas, energi, pilihan, dan pertanyaan untuk Shizuka. [Baca persona](../configs/personas/yukino.md).

| Skill atau rujukan | Status | Fungsi |
| --- | --- | --- |
| [`backward-traceability`](../skills/backward-traceability/SKILL.md) | Bundel | Menautkan angka dan hasil laporan kembali ke data, skrip, atau perhitungan. |
| [`brainstorming-research-ideas`](../skills/brainstorming-research-ideas/SKILL.md) | Bundel | Memakai kerangka ideasi terstruktur untuk menemukan pertanyaan layak. |
| [`business-sage`](../skills/business-sage/SKILL.md) | Bundel | Menyusun analisis usaha, skenario finansial, dan pertanyaan verifikasi aturan yang relevan. |
| [`chatgpt-hermes-portability-kit`](../skills/chatgpt-hermes-portability-kit/SKILL.md) | Bundel | Memandu adaptasi metode dan profil ke platform lain menggunakan sumber yang sah. |
| [`cli-anything-business-sage`](../skills/cli-anything-business-sage/SKILL.md) | Bundel | Menjalankan perhitungan bisnis terstruktur melalui harness lokal yang tersedia. |
| [`creative-thinking-for-research`](../skills/creative-thinking-for-research/SKILL.md) | Bundel | Mencoba reframing, analogi, dan kombinasi konsep untuk membuka pilihan. |
| [`deep-research`](../skills/deep-research/SKILL.md) | Bundel | Menyusun pertanyaan, menelusuri literatur, dan mensintesis bukti yang dapat diperiksa. |
| [`focus-my-energy`](../skills/focus-my-energy/SKILL.md) | Bundel | Menyesuaikan beban tugas dan langkah awal dengan energi yang dilaporkan pengguna. |
| [`generate-fresh-ideas`](../skills/generate-fresh-ideas/SKILL.md) | Bundel | Menghasilkan alternatif dari beberapa lensa kreatif untuk disaring pengguna. |
| [`idea-generation`](../skills/idea-generation/SKILL.md) | Bundel | Mengembangkan dan menyaring gagasan penelitian dalam beberapa putaran. |
| [`literature-review`](../skills/literature-review/SKILL.md) | Bundel | Membangun tinjauan pustaka dengan beberapa perspektif dan jejak sumber. |
| [`match-my-writing-style`](../skills/match-my-writing-style/SKILL.md) | Bundel | Menerapkan Voice Card yang disediakan pengguna sesuai audiens dan jenis tulisan. |
| [`notebooklm-thinking-datascience`](../skills/notebooklm-thinking-datascience/SKILL.md) | Bundel | Mengadaptasi metode berpikir sistem dan data science dari indeks sumber milik pengguna. |
| [`novelty-assessment`](../skills/novelty-assessment/SKILL.md) | Bundel | Menguji klaim kebaruan terhadap studi terdekat dan batas pencarian. |
| [`paper-revision`](../skills/paper-revision/SKILL.md) | Bundel | Memetakan catatan revisi ke perubahan konkret dan bukti perbaikan. |
| [`paper-writing-section`](../skills/paper-writing-section/SKILL.md) | Bundel | Menyusun dan menyunting bagian naskah akademik dengan dua tahap pemeriksaan. |
| [`parenting-6d-gad-mdd`](../skills/parenting-6d-gad-mdd/SKILL.md) | Bundel | Memandu percakapan dengan empati, struktur, dan dukungan otonomi. |
| [`persona-shizuka-yukino-shikaku`](../skills/persona-shizuka-yukino-shikaku/SKILL.md) | Bundel | Menjaga karakter, kontrak serah terima, dan batas kepemilikan tugas lima bot. |
| [`prep-for-meetings`](../skills/prep-for-meetings/SKILL.md) | Bundel | Menyusun ringkasan pertemuan dari catatan dan tujuan yang tersedia. |
| [`prep-for-meetings-2`](../skills/prep-for-meetings-2/SKILL.md) | Bundel | Memadatkan bahan pertemuan menjadi pokok bahasan dan kartu pengingat. |
| [`rebuttal-writing`](../skills/rebuttal-writing/SKILL.md) | Bundel | Menyusun jawaban poin demi poin untuk masukan pembimbing atau reviewer. |
| [`research-paper-writing`](../skills/research-paper-writing/SKILL.md) | Bundel | Memeriksa struktur argumen dan hubungan antara klaim, bukti, serta pembahasan. |
| [`anti-slop`](https://github.com/miqdadbadjuber/anti-slop) | Eksternal | Memeriksa klise, struktur antarmuka, dan pola kode yang berulang. |
| [`cli-anything`](https://github.com/HKUDS/CLI-Anything) | Eksternal | Memanggil CLI atau aplikasi melalui adapter yang dipilih untuk tugas aktif. |
| [`cli-anything-catalog`](https://clianything.cc/) | Eksternal | Direktori untuk menemukan adapter CLI yang relevan dengan tugas. |
| [`graphify`](https://github.com/Graphify-Labs/graphify) | Eksternal | Membuat peta struktur proyek untuk penelusuran konteks. |
| [`hermes-jev-skills`](https://github.com/kerpopule/hermes-jev-skills) | Eksternal | Memilih skill dari konteks dengan pengalihan model dinonaktifkan. |
| [`hermes-steel`](https://github.com/steel-dev/hermes-steel) | Eksternal | Membuka peramban untuk langkah yang diminta jika plugin tersedia. |
| [`humanizer-en`](https://github.com/blader/humanizer) | Eksternal | Menyunting naskah bahasa Inggris dengan menjaga arti dan sitasi. |
| [`humanizer-indonesia`](https://github.com/adhiprib/humanizer-indonesia) | Eksternal | Menyunting bahasa Indonesia dengan EYD/KBBI dan metrik jika tersedia. |
| [`remote-jobs`](https://github.com/remoteintech/remote-jobs) | Eksternal | Menyaring perusahaan remote, lalu memeriksa syarat lokasi dan lowongan langsung. |
| [`token-monitor`](https://github.com/Javis603/token-monitor) | Eksternal | Sumber status kuota tambahan untuk kebijakan anggaran. |
| `tokenshield` | Eksternal | Menyatukan estimasi biaya, pembacaan penggunaan, dan batas cadangan berdasarkan data aktual. |
| [`tokentracker`](https://github.com/xiufengsun/TokenTracker) | Eksternal | Sumber data penggunaan lokal untuk kebijakan anggaran. |
| [`unlimited-ocr`](https://github.com/baidu/Unlimited-OCR) | Eksternal | Memandu runtime OCR lokal dan indeks halaman. |
| [`unlimited-ocr-2`](https://huggingface.co/baidu/Unlimited-OCR-2) | Eksternal | Menyiapkan ekstraksi dokumen/gambar berhalaman bila bobot dan perangkat tersedia. |

## Sensei Shizuka Hiratsuka

Strategi, delegasi, pemilihan alur kerja, dan penjelasan akhir kepada pengguna. [Baca persona](../configs/personas/shizuka.md).

| Skill atau rujukan | Status | Fungsi |
| --- | --- | --- |
| [`autoresearch`](../skills/autoresearch/SKILL.md) | Bundel | Mengoordinasikan siklus eksperimen dan sintesis dengan batas berhenti. |
| [`backward-traceability`](../skills/backward-traceability/SKILL.md) | Bundel | Menautkan angka dan hasil laporan kembali ke data, skrip, atau perhitungan. |
| [`business-sage`](../skills/business-sage/SKILL.md) | Bundel | Menyusun analisis usaha, skenario finansial, dan pertanyaan verifikasi aturan yang relevan. |
| [`chatgpt-hermes-portability-kit`](../skills/chatgpt-hermes-portability-kit/SKILL.md) | Bundel | Memandu adaptasi metode dan profil ke platform lain menggunakan sumber yang sah. |
| [`cli-anything-business-sage`](../skills/cli-anything-business-sage/SKILL.md) | Bundel | Menjalankan perhitungan bisnis terstruktur melalui harness lokal yang tersedia. |
| [`deep-research`](../skills/deep-research/SKILL.md) | Bundel | Menyusun pertanyaan, menelusuri literatur, dan mensintesis bukti yang dapat diperiksa. |
| [`get-more-perspectives`](../skills/get-more-perspectives/SKILL.md) | Bundel | Menguji keputusan dari beberapa sudut pandang sebelum memilih. |
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
| [`wise-judgment-and-sovereign-orchestrator`](../skills/wise-judgment-and-sovereign-orchestrator/SKILL.md) | Bundel | Mengatur pilihan alur, anggaran, persetujuan, delegasi, dan sintesis hasil Val. |
| [`anti-slop`](https://github.com/miqdadbadjuber/anti-slop) | Eksternal | Memeriksa klise, struktur antarmuka, dan pola kode yang berulang. |
| [`cli-anything`](https://github.com/HKUDS/CLI-Anything) | Eksternal | Memanggil CLI atau aplikasi melalui adapter yang dipilih untuk tugas aktif. |
| [`cli-anything-catalog`](https://clianything.cc/) | Eksternal | Direktori untuk menemukan adapter CLI yang relevan dengan tugas. |
| [`graphify`](https://github.com/Graphify-Labs/graphify) | Eksternal | Membuat peta struktur proyek untuk penelusuran konteks. |
| [`hermes-jev-skills`](https://github.com/kerpopule/hermes-jev-skills) | Eksternal | Memilih skill dari konteks dengan pengalihan model dinonaktifkan. |
| [`hermes-steel`](https://github.com/steel-dev/hermes-steel) | Eksternal | Membuka peramban untuk langkah yang diminta jika plugin tersedia. |
| [`humanizer-en`](https://github.com/blader/humanizer) | Eksternal | Menyunting naskah bahasa Inggris dengan menjaga arti dan sitasi. |
| [`humanizer-indonesia`](https://github.com/adhiprib/humanizer-indonesia) | Eksternal | Menyunting bahasa Indonesia dengan EYD/KBBI dan metrik jika tersedia. |
| [`remote-jobs`](https://github.com/remoteintech/remote-jobs) | Eksternal | Menyaring perusahaan remote, lalu memeriksa syarat lokasi dan lowongan langsung. |
| [`token-monitor`](https://github.com/Javis603/token-monitor) | Eksternal | Sumber status kuota tambahan untuk kebijakan anggaran. |
| `tokenshield` | Eksternal | Menyatukan estimasi biaya, pembacaan penggunaan, dan batas cadangan berdasarkan data aktual. |
| [`tokentracker`](https://github.com/xiufengsun/TokenTracker) | Eksternal | Sumber data penggunaan lokal untuk kebijakan anggaran. |
| [`unlimited-ocr`](https://github.com/baidu/Unlimited-OCR) | Eksternal | Memandu runtime OCR lokal dan indeks halaman. |
| [`unlimited-ocr-2`](https://huggingface.co/baidu/Unlimited-OCR-2) | Eksternal | Menyiapkan ekstraksi dokumen/gambar berhalaman bila bobot dan perangkat tersedia. |

## Val

Bukti, metode, batas kepastian, serta dossier untuk Shizuka. [Baca persona](../configs/personas/val.md).

| Skill atau rujukan | Status | Fungsi |
| --- | --- | --- |
| [`backward-traceability`](../skills/backward-traceability/SKILL.md) | Bundel | Menautkan angka dan hasil laporan kembali ke data, skrip, atau perhitungan. |
| [`business-sage`](../skills/business-sage/SKILL.md) | Bundel | Menyusun analisis usaha, skenario finansial, dan pertanyaan verifikasi aturan yang relevan. |
| [`chatgpt-hermes-portability-kit`](../skills/chatgpt-hermes-portability-kit/SKILL.md) | Bundel | Memandu adaptasi metode dan profil ke platform lain menggunakan sumber yang sah. |
| [`cli-anything-business-sage`](../skills/cli-anything-business-sage/SKILL.md) | Bundel | Menjalankan perhitungan bisnis terstruktur melalui harness lokal yang tersedia. |
| [`data-analysis`](../skills/data-analysis/SKILL.md) | Bundel | Memeriksa kualitas data, asumsi, uji statistik, dan ketidakpastian. |
| [`deep-research`](../skills/deep-research/SKILL.md) | Bundel | Menyusun pertanyaan, menelusuri literatur, dan mensintesis bukti yang dapat diperiksa. |
| [`firecrawl-competitive-intel`](../skills/firecrawl-competitive-intel/SKILL.md) | Bundel | Membandingkan perubahan produk, harga, dan fitur dengan bukti bertanggal. |
| [`firecrawl-dashboard-reporting`](../skills/firecrawl-dashboard-reporting/SKILL.md) | Bundel | Mengambil dan memeriksa indikator dasbor untuk pelaporan. |
| [`firecrawl-deep-research`](../skills/firecrawl-deep-research/SKILL.md) | Bundel | Mengumpulkan bukti web untuk sintesis dengan atribusi. |
| [`firecrawl-knowledge-base`](../skills/firecrawl-knowledge-base/SKILL.md) | Bundel | Menyiapkan koleksi dokumen, potongan, serta metadata asalnya. |
| [`firecrawl-research-papers`](../skills/firecrawl-research-papers/SKILL.md) | Bundel | Menemukan dan memeriksa makalah pada sumber akademik yang relevan. |
| [`github-research`](../skills/github-research/SKILL.md) | Bundel | Menelaah lisensi, rancangan, pemeliharaan, dan kesiapan repositori. |
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
| [`anti-slop`](https://github.com/miqdadbadjuber/anti-slop) | Eksternal | Memeriksa klise, struktur antarmuka, dan pola kode yang berulang. |
| [`cli-anything`](https://github.com/HKUDS/CLI-Anything) | Eksternal | Memanggil CLI atau aplikasi melalui adapter yang dipilih untuk tugas aktif. |
| [`cli-anything-catalog`](https://clianything.cc/) | Eksternal | Direktori untuk menemukan adapter CLI yang relevan dengan tugas. |
| [`gpt-researcher`](https://github.com/assafelovic/gpt-researcher) | Eksternal | Mengumpulkan dan menyusun bahan riset; Val memeriksa sumber sebelum penyerahan. |
| [`graphify`](https://github.com/Graphify-Labs/graphify) | Eksternal | Membuat peta struktur proyek untuk penelusuran konteks. |
| [`hermes-jev-skills`](https://github.com/kerpopule/hermes-jev-skills) | Eksternal | Memilih skill dari konteks dengan pengalihan model dinonaktifkan. |
| [`hermes-steel`](https://github.com/steel-dev/hermes-steel) | Eksternal | Membuka peramban untuk langkah yang diminta jika plugin tersedia. |
| [`humanizer-en`](https://github.com/blader/humanizer) | Eksternal | Menyunting naskah bahasa Inggris dengan menjaga arti dan sitasi. |
| [`humanizer-indonesia`](https://github.com/adhiprib/humanizer-indonesia) | Eksternal | Menyunting bahasa Indonesia dengan EYD/KBBI dan metrik jika tersedia. |
| [`remote-jobs`](https://github.com/remoteintech/remote-jobs) | Eksternal | Menyaring perusahaan remote, lalu memeriksa syarat lokasi dan lowongan langsung. |
| [`token-monitor`](https://github.com/Javis603/token-monitor) | Eksternal | Sumber status kuota tambahan untuk kebijakan anggaran. |
| `tokenshield` | Eksternal | Menyatukan estimasi biaya, pembacaan penggunaan, dan batas cadangan berdasarkan data aktual. |
| [`tokentracker`](https://github.com/xiufengsun/TokenTracker) | Eksternal | Sumber data penggunaan lokal untuk kebijakan anggaran. |
| [`unlimited-ocr`](https://github.com/baidu/Unlimited-OCR) | Eksternal | Memandu runtime OCR lokal dan indeks halaman. |
| [`unlimited-ocr-2`](https://huggingface.co/baidu/Unlimited-OCR-2) | Eksternal | Menyiapkan ekstraksi dokumen/gambar berhalaman bila bobot dan perangkat tersedia. |

## Kiki-Chii

Konsep, produksi kreatif, identitas visual, dan penyerahan aset. [Baca persona](../configs/personas/kiki-chii.md).

| Skill atau rujukan | Status | Fungsi |
| --- | --- | --- |
| [`academic-plotting`](../skills/academic-plotting/SKILL.md) | Bundel | Menghasilkan figur publikasi dari data dan spesifikasi yang disepakati. |
| [`auto-curiousity-for-film-making`](../skills/auto-curiousity-for-film-making/SKILL.md) | Bundel | Menguji kemampuan alat kreatif dan teknik produksi dalam eksperimen terpisah. |
| [`business-sage`](../skills/business-sage/SKILL.md) | Bundel | Menyusun analisis usaha, skenario finansial, dan pertanyaan verifikasi aturan yang relevan. |
| [`cli-anything-business-sage`](../skills/cli-anything-business-sage/SKILL.md) | Bundel | Menjalankan perhitungan bisnis terstruktur melalui harness lokal yang tersedia. |
| [`filmmaking-videography-photography-s2`](../skills/filmmaking-videography-photography-s2/SKILL.md) | Bundel | Menyatukan konsep, pengarahan, kamera, foto, penyuntingan, warna, dan suara. |
| [`match-my-writing-style`](../skills/match-my-writing-style/SKILL.md) | Bundel | Menerapkan Voice Card yang disediakan pengguna sesuai audiens dan jenis tulisan. |
| [`parenting-6d-gad-mdd`](../skills/parenting-6d-gad-mdd/SKILL.md) | Bundel | Memandu percakapan dengan empati, struktur, dan dukungan otonomi. |
| [`persona-shizuka-yukino-shikaku`](../skills/persona-shizuka-yukino-shikaku/SKILL.md) | Bundel | Menjaga karakter, kontrak serah terima, dan batas kepemilikan tugas lima bot. |
| [`slide-generation`](../skills/slide-generation/SKILL.md) | Bundel | Menyusun presentasi dari argumen, hasil, dan visual yang dapat diverifikasi. |
| [`anti-slop`](https://github.com/miqdadbadjuber/anti-slop) | Eksternal | Memeriksa klise, struktur antarmuka, dan pola kode yang berulang. |
| `artcraft-cadcraft` | Eksternal | Nama adapter opsional dalam rancangan ArtCraft untuk rancangan teknis. |
| `artcraft-craftanything` | Eksternal | Nama adapter opsional dalam rancangan ArtCraft untuk otomasi kreatif lintas alat. |
| `artcraft-deckcraft` | Eksternal | Nama adapter opsional dalam rancangan ArtCraft untuk presentasi kreatif. |
| `artcraft-designcraft` | Eksternal | Nama adapter opsional dalam rancangan ArtCraft untuk desain aset visual. |
| `artcraft-effectcraft` | Eksternal | Nama adapter opsional dalam rancangan ArtCraft untuk efek visual dan compositing. |
| `artcraft-figcraft` | Eksternal | Nama adapter opsional dalam rancangan ArtCraft untuk rancangan UI dan prototipe. |
| `artcraft-filmcraft` | Eksternal | Nama adapter opsional dalam rancangan ArtCraft untuk perencanaan adegan dan shot. |
| `artcraft-gridcraft` | Eksternal | Nama adapter opsional dalam rancangan ArtCraft untuk tabel dan perencanaan produksi. |
| `artcraft-lightcraft` | Eksternal | Nama adapter opsional dalam rancangan ArtCraft untuk rancangan pencahayaan. |
| `artcraft-pdfcraft` | Eksternal | Nama adapter opsional dalam rancangan ArtCraft untuk paket dokumen PDF. |
| `artcraft-photocraft` | Eksternal | Nama adapter opsional dalam rancangan ArtCraft untuk pengolahan dan evaluasi foto. |
| `artcraft-solidcraft` | Eksternal | Nama adapter opsional dalam rancangan ArtCraft untuk model bentuk padat. |
| `artcraft-soundcraft` | Eksternal | Nama adapter opsional dalam rancangan ArtCraft untuk rancangan suara dan mixing. |
| `artcraft-vectorcraft` | Eksternal | Nama adapter opsional dalam rancangan ArtCraft untuk aset vektor. |
| `artcraft-wordcraft` | Eksternal | Nama adapter opsional dalam rancangan ArtCraft untuk dokumen produksi. |
| [`bang-motion`](https://github.com/bangtutorial/bang-motion) | Eksternal | Memandu motion graphics berbasis kode sesuai brief. |
| [`barty-motion-graphics`](https://github.com/Barty-Bart/motion-graphics) | Eksternal | Memandu komposisi grafis gerak dan animasi berbasis kode. |
| [`better-design`](https://github.com/marvkr/better-design) | Eksternal | Membantu tinjauan kualitas dan hierarki desain. |
| `blender-mcp` | Eksternal | Menghubungkan tahap komposisi 3D, render, dan pemeriksaan adegan dengan adapter Blender yang tersedia. |
| [`canvas-ui`](https://github.com/DavidHDev/canvas-ui) | Eksternal | Menelaah komponen visual berbasis kanvas untuk interaksi khusus. |
| [`charlie-motion-graphics`](https://github.com/charlie947/motion-graphics-skills) | Eksternal | Menyusun pendekatan motion graphics dan urutan gerak dari storyboard. |
| [`cli-anything`](https://github.com/HKUDS/CLI-Anything) | Eksternal | Memanggil CLI atau aplikasi melalui adapter yang dipilih untuk tugas aktif. |
| [`cli-anything-catalog`](https://clianything.cc/) | Eksternal | Direktori untuk menemukan adapter CLI yang relevan dengan tugas. |
| [`cursify`](https://github.com/ui-layouts/cursify) | Eksternal | Memilih interaksi kursor yang sesuai dengan kebutuhan antarmuka. |
| [`design-taste`](https://github.com/madebymustafa/design-taste) | Eksternal | Memilih gaya visual, tipografi, dan komposisi yang sesuai. |
| [`graphify`](https://github.com/Graphify-Labs/graphify) | Eksternal | Membuat peta struktur proyek untuk penelusuran konteks. |
| [`hermes-jev-skills`](https://github.com/kerpopule/hermes-jev-skills) | Eksternal | Memilih skill dari konteks dengan pengalihan model dinonaktifkan. |
| [`hermes-steel`](https://github.com/steel-dev/hermes-steel) | Eksternal | Membuka peramban untuk langkah yang diminta jika plugin tersedia. |
| [`higgsfield-brandkit`](https://github.com/higgsfield-ai/skills) | Eksternal | Menerapkan sistem visual merek pada produksi aset. |
| [`higgsfield-faceless-video`](https://github.com/higgsfield-ai/skills) | Eksternal | Menyiapkan video tanpa tampil wajah dari skrip, tempo, dan aset. |
| [`higgsfield-generate`](https://github.com/higgsfield-ai/skills) | Eksternal | Menghasilkan atau mengolah media setelah konsep dan parameter disetujui. |
| [`higgsfield-marketplace-cards`](https://github.com/higgsfield-ai/skills) | Eksternal | Menyusun kartu promosi produk dengan pesan dan spesifikasi kanal. |
| [`higgsfield-product-photoshoot`](https://github.com/higgsfield-ai/skills) | Eksternal | Mengatur konsep foto produk, pencahayaan, dan framing. |
| [`higgsfield-skills`](https://github.com/higgsfield-ai/skills) | Eksternal | Katalog integrasi Higgsfield untuk produksi visual dan video. |
| [`higgsfield-soul-id`](https://github.com/higgsfield-ai/skills) | Eksternal | Mengelola konsistensi subjek dengan referensi yang diizinkan. |
| [`higgsfield-video-explainer`](https://github.com/higgsfield-ai/skills) | Eksternal | Mengubah penjelasan konsep menjadi urutan adegan. |
| [`higgsfield-websites`](https://github.com/higgsfield-ai/skills) | Eksternal | Memetakan brief produk ke konsep situs dan aset pendukung. |
| [`higgsfield-youtube-thumbnail`](https://github.com/higgsfield-ai/skills) | Eksternal | Membuat konsep thumbnail sesuai isi video dan identitas kanal. |
| [`humanizer-en`](https://github.com/blader/humanizer) | Eksternal | Menyunting naskah bahasa Inggris dengan menjaga arti dan sitasi. |
| [`humanizer-indonesia`](https://github.com/adhiprib/humanizer-indonesia) | Eksternal | Menyunting bahasa Indonesia dengan EYD/KBBI dan metrik jika tersedia. |
| [`motion-primitives`](https://github.com/ibelick/motion-primitives) | Eksternal | Merancang gerak antarmuka memakai komponen animasi. |
| [`paper-shaders`](https://github.com/paper-design/shaders) | Eksternal | Menyiapkan efek shader yang terukur dan sesuai perangkat. |
| [`remote-jobs`](https://github.com/remoteintech/remote-jobs) | Eksternal | Menyaring perusahaan remote, lalu memeriksa syarat lokasi dan lowongan langsung. |
| [`remotion-skills`](https://github.com/remotion-dev/skills) | Eksternal | Merancang komposisi video sebagai kode dan merendernya bila runtime tersedia. |
| [`superdesign-skill`](https://github.com/superdesigndev/superdesign-skill) | Eksternal | Menilai tata letak, token desain, dan konsistensi antarmuka. |
| [`token-monitor`](https://github.com/Javis603/token-monitor) | Eksternal | Sumber status kuota tambahan untuk kebijakan anggaran. |
| `tokenshield` | Eksternal | Menyatukan estimasi biaya, pembacaan penggunaan, dan batas cadangan berdasarkan data aktual. |
| [`tokentracker`](https://github.com/xiufengsun/TokenTracker) | Eksternal | Sumber data penggunaan lokal untuk kebijakan anggaran. |
| [`unlimited-ocr`](https://github.com/baidu/Unlimited-OCR) | Eksternal | Memandu runtime OCR lokal dan indeks halaman. |
| [`unlimited-ocr-2`](https://huggingface.co/baidu/Unlimited-OCR-2) | Eksternal | Menyiapkan ekstraksi dokumen/gambar berhalaman bila bobot dan perangkat tersedia. |

## Shikaku Nara

Arsitektur, kode, pengujian, serta pemeriksaan keamanan dalam lingkup yang diizinkan. [Baca persona](../configs/personas/shikaku.md).

| Skill atau rujukan | Status | Fungsi |
| --- | --- | --- |
| [`ai-research-explore`](../skills/ai-research-explore/SKILL.md) | Bundel | Merancang eksperimen kandidat yang terpisah dari baseline. |
| [`ai-research-reproduction`](../skills/ai-research-reproduction/SKILL.md) | Bundel | Menetapkan target reproduksi penelitian yang dapat dibuktikan. |
| [`analyze-project`](../skills/analyze-project/SKILL.md) | Bundel | Memetakan struktur proyek, konfigurasi, titik masuk, dan risiko perubahan. |
| [`evaluating-code-models`](../skills/evaluating-code-models/SKILL.md) | Bundel | Menguji keluaran model kode dengan tugas dan tolok ukur yang relevan. |
| [`evaluating-llms-harness`](../skills/evaluating-llms-harness/SKILL.md) | Bundel | Mengatur dan menilai evaluasi LLM dengan harness pengujian yang kompatibel. |
| [`explore-code`](../skills/explore-code/SKILL.md) | Bundel | Mengembangkan perubahan eksperimen dalam ruang kerja terisolasi. |
| [`explore-run`](../skills/explore-run/SKILL.md) | Bundel | Menjalankan uji terbatas dengan anggaran dan catatan hasil yang jelas. |
| [`langsmith-observability`](../skills/langsmith-observability/SKILL.md) | Bundel | Memandu observabilitas dan evaluasi LangSmith pada lingkungan yang disetujui. |
| [`match-my-writing-style`](../skills/match-my-writing-style/SKILL.md) | Bundel | Menerapkan Voice Card yang disediakan pengguna sesuai audiens dan jenis tulisan. |
| [`nemo-evaluator-sdk`](../skills/nemo-evaluator-sdk/SKILL.md) | Bundel | Memandu evaluasi dengan NeMo Evaluator SDK jika dependensinya tersedia. |
| [`parenting-6d-gad-mdd`](../skills/parenting-6d-gad-mdd/SKILL.md) | Bundel | Memandu percakapan dengan empati, struktur, dan dukungan otonomi. |
| [`persona-shizuka-yukino-shikaku`](../skills/persona-shizuka-yukino-shikaku/SKILL.md) | Bundel | Menjaga karakter, kontrak serah terima, dan batas kepemilikan tugas lima bot. |
| [`phoenix-observability`](../skills/phoenix-observability/SKILL.md) | Bundel | Memandu tracing dan evaluasi Phoenix tanpa memindahkan data di luar lingkup. |
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
| [`hermes-steel`](https://github.com/steel-dev/hermes-steel) | Eksternal | Membuka peramban untuk langkah yang diminta jika plugin tersedia. |
| [`higgsfield-websites`](https://github.com/higgsfield-ai/skills) | Eksternal | Memetakan brief produk ke konsep situs dan aset pendukung. |
| [`humanizer-en`](https://github.com/blader/humanizer) | Eksternal | Menyunting naskah bahasa Inggris dengan menjaga arti dan sitasi. |
| [`humanizer-indonesia`](https://github.com/adhiprib/humanizer-indonesia) | Eksternal | Menyunting bahasa Indonesia dengan EYD/KBBI dan metrik jika tersedia. |
| [`mindrally-skills`](https://github.com/mindrally/skills) | Eksternal | Menemukan panduan implementasi relevan di katalog eksternal. |
| [`motion-primitives`](https://github.com/ibelick/motion-primitives) | Eksternal | Merancang gerak antarmuka memakai komponen animasi. |
| [`paper-shaders`](https://github.com/paper-design/shaders) | Eksternal | Menyiapkan efek shader yang terukur dan sesuai perangkat. |
| [`playwright-best-practices`](https://github.com/currents-dev/playwright-best-practices-skill) | Eksternal | Menguji jalur pengguna dan memperbaiki kestabilan tes E2E. |
| [`ponytail`](https://github.com/dietrichgebert/ponytail) | Eksternal | Mengurangi kerumitan solusi dan memilih perubahan yang sesuai kebutuhan. |
| [`rea`](https://github.com/morluto/rea) | Eksternal | Mendukung langkah forensik yang diizinkan dan mencatat hasil. |
| [`remotion-skills`](https://github.com/remotion-dev/skills) | Eksternal | Merancang komposisi video sebagai kode dan merendernya bila runtime tersedia. |
| [`reverse-engineer-anything`](https://github.com/NabilRFG12/Reverse-Engineer-anything) | Eksternal | Memeriksa artefak insiden secara forensik dalam mandat yang jelas. |
| [`strix`](https://github.com/usestrix/strix) | Eksternal | Menguji keamanan target yang lingkup dan izin aksesnya telah disetujui. |
| [`superdesign-skill`](https://github.com/superdesigndev/superdesign-skill) | Eksternal | Menilai tata letak, token desain, dan konsistensi antarmuka. |
| [`superpowers`](https://github.com/obra/superpowers) | Eksternal | Menata perencanaan, implementasi, dan validasi perubahan kode. |
| [`token-monitor`](https://github.com/Javis603/token-monitor) | Eksternal | Sumber status kuota tambahan untuk kebijakan anggaran. |
| `tokenshield` | Eksternal | Menyatukan estimasi biaya, pembacaan penggunaan, dan batas cadangan berdasarkan data aktual. |
| [`tokentracker`](https://github.com/xiufengsun/TokenTracker) | Eksternal | Sumber data penggunaan lokal untuk kebijakan anggaran. |
| [`unlimited-ocr`](https://github.com/baidu/Unlimited-OCR) | Eksternal | Memandu runtime OCR lokal dan indeks halaman. |
| [`unlimited-ocr-2`](https://huggingface.co/baidu/Unlimited-OCR-2) | Eksternal | Menyiapkan ekstraksi dokumen/gambar berhalaman bila bobot dan perangkat tersedia. |

## Kelompok distribusi

### Semua bot

- **Yukino Yukinoshita, Sensei Shizuka Hiratsuka, Val, Kiki-Chii, Shikaku Nara** — [`anti-slop`](https://github.com/miqdadbadjuber/anti-slop), [`cli-anything`](https://github.com/HKUDS/CLI-Anything), [`cli-anything-catalog`](https://clianything.cc/), [`graphify`](https://github.com/Graphify-Labs/graphify), [`hermes-jev-skills`](https://github.com/kerpopule/hermes-jev-skills), [`hermes-steel`](https://github.com/steel-dev/hermes-steel), [`humanizer-en`](https://github.com/blader/humanizer), [`humanizer-indonesia`](https://github.com/adhiprib/humanizer-indonesia), [`match-my-writing-style`](../skills/match-my-writing-style/SKILL.md), [`parenting-6d-gad-mdd`](../skills/parenting-6d-gad-mdd/SKILL.md), [`persona-shizuka-yukino-shikaku`](../skills/persona-shizuka-yukino-shikaku/SKILL.md), [`token-monitor`](https://github.com/Javis603/token-monitor), `tokenshield`, [`tokentracker`](https://github.com/xiufengsun/TokenTracker), [`unlimited-ocr`](https://github.com/baidu/Unlimited-OCR), [`unlimited-ocr-2`](https://huggingface.co/baidu/Unlimited-OCR-2)

### Beberapa bot

- **Yukino Yukinoshita, Sensei Shizuka Hiratsuka, Val** — [`backward-traceability`](../skills/backward-traceability/SKILL.md), [`chatgpt-hermes-portability-kit`](../skills/chatgpt-hermes-portability-kit/SKILL.md), [`deep-research`](../skills/deep-research/SKILL.md), [`literature-review`](../skills/literature-review/SKILL.md), [`notebooklm-thinking-datascience`](../skills/notebooklm-thinking-datascience/SKILL.md), [`novelty-assessment`](../skills/novelty-assessment/SKILL.md), [`paper-revision`](../skills/paper-revision/SKILL.md), [`paper-writing-section`](../skills/paper-writing-section/SKILL.md), [`rebuttal-writing`](../skills/rebuttal-writing/SKILL.md), [`research-paper-writing`](../skills/research-paper-writing/SKILL.md)
- **Kiki-Chii, Shikaku Nara** — [`bang-motion`](https://github.com/bangtutorial/bang-motion), [`better-design`](https://github.com/marvkr/better-design), [`canvas-ui`](https://github.com/DavidHDev/canvas-ui), [`cursify`](https://github.com/ui-layouts/cursify), [`design-taste`](https://github.com/madebymustafa/design-taste), [`higgsfield-websites`](https://github.com/higgsfield-ai/skills), [`motion-primitives`](https://github.com/ibelick/motion-primitives), [`paper-shaders`](https://github.com/paper-design/shaders), [`remotion-skills`](https://github.com/remotion-dev/skills), [`superdesign-skill`](https://github.com/superdesigndev/superdesign-skill)
- **Yukino Yukinoshita, Sensei Shizuka Hiratsuka, Val, Kiki-Chii** — [`business-sage`](../skills/business-sage/SKILL.md), [`cli-anything-business-sage`](../skills/cli-anything-business-sage/SKILL.md), [`remote-jobs`](https://github.com/remoteintech/remote-jobs)

### Khusus satu bot

- **Kiki-Chii** — [`academic-plotting`](../skills/academic-plotting/SKILL.md), `artcraft-cadcraft`, `artcraft-craftanything`, `artcraft-deckcraft`, `artcraft-designcraft`, `artcraft-effectcraft`, `artcraft-figcraft`, `artcraft-filmcraft`, `artcraft-gridcraft`, `artcraft-lightcraft`, `artcraft-pdfcraft`, `artcraft-photocraft`, `artcraft-solidcraft`, `artcraft-soundcraft`, `artcraft-vectorcraft`, `artcraft-wordcraft`, [`auto-curiousity-for-film-making`](../skills/auto-curiousity-for-film-making/SKILL.md), [`barty-motion-graphics`](https://github.com/Barty-Bart/motion-graphics), `blender-mcp`, [`charlie-motion-graphics`](https://github.com/charlie947/motion-graphics-skills), [`filmmaking-videography-photography-s2`](../skills/filmmaking-videography-photography-s2/SKILL.md), [`higgsfield-brandkit`](https://github.com/higgsfield-ai/skills), [`higgsfield-faceless-video`](https://github.com/higgsfield-ai/skills), [`higgsfield-generate`](https://github.com/higgsfield-ai/skills), [`higgsfield-marketplace-cards`](https://github.com/higgsfield-ai/skills), [`higgsfield-product-photoshoot`](https://github.com/higgsfield-ai/skills), [`higgsfield-skills`](https://github.com/higgsfield-ai/skills), [`higgsfield-soul-id`](https://github.com/higgsfield-ai/skills), [`higgsfield-video-explainer`](https://github.com/higgsfield-ai/skills), [`higgsfield-youtube-thumbnail`](https://github.com/higgsfield-ai/skills), [`slide-generation`](../skills/slide-generation/SKILL.md)
- **Shikaku Nara** — [`addy-agent-skills`](https://github.com/addyosmani/agent-skills), [`ai-research-explore`](../skills/ai-research-explore/SKILL.md), [`ai-research-reproduction`](../skills/ai-research-reproduction/SKILL.md), [`analyze-project`](../skills/analyze-project/SKILL.md), [`awesome-copilot`](https://github.com/github/awesome-copilot), [`cybersecurity-library`](https://github.com/mukul975/anthropic-cybersecurity-skills), [`evaluating-code-models`](../skills/evaluating-code-models/SKILL.md), [`evaluating-llms-harness`](../skills/evaluating-llms-harness/SKILL.md), [`explore-code`](../skills/explore-code/SKILL.md), [`explore-run`](../skills/explore-run/SKILL.md), [`goose`](https://github.com/aaif-goose/goose), [`langsmith-observability`](../skills/langsmith-observability/SKILL.md), [`mindrally-skills`](https://github.com/mindrally/skills), [`nemo-evaluator-sdk`](../skills/nemo-evaluator-sdk/SKILL.md), [`phoenix-observability`](../skills/phoenix-observability/SKILL.md), [`playwright-best-practices`](https://github.com/currents-dev/playwright-best-practices-skill), [`ponytail`](https://github.com/dietrichgebert/ponytail), [`rea`](https://github.com/morluto/rea), [`reverse-engineer-anything`](https://github.com/NabilRFG12/Reverse-Engineer-anything), [`strix`](https://github.com/usestrix/strix), [`superpowers`](https://github.com/obra/superpowers)
- **Sensei Shizuka Hiratsuka** — [`autoresearch`](../skills/autoresearch/SKILL.md), [`get-more-perspectives`](../skills/get-more-perspectives/SKILL.md), [`wise-judgment-and-sovereign-orchestrator`](../skills/wise-judgment-and-sovereign-orchestrator/SKILL.md)
- **Yukino Yukinoshita** — [`brainstorming-research-ideas`](../skills/brainstorming-research-ideas/SKILL.md), [`creative-thinking-for-research`](../skills/creative-thinking-for-research/SKILL.md), [`focus-my-energy`](../skills/focus-my-energy/SKILL.md), [`generate-fresh-ideas`](../skills/generate-fresh-ideas/SKILL.md), [`idea-generation`](../skills/idea-generation/SKILL.md), [`prep-for-meetings`](../skills/prep-for-meetings/SKILL.md), [`prep-for-meetings-2`](../skills/prep-for-meetings-2/SKILL.md)
- **Val** — [`data-analysis`](../skills/data-analysis/SKILL.md), [`firecrawl-competitive-intel`](../skills/firecrawl-competitive-intel/SKILL.md), [`firecrawl-dashboard-reporting`](../skills/firecrawl-dashboard-reporting/SKILL.md), [`firecrawl-deep-research`](../skills/firecrawl-deep-research/SKILL.md), [`firecrawl-knowledge-base`](../skills/firecrawl-knowledge-base/SKILL.md), [`firecrawl-research-papers`](../skills/firecrawl-research-papers/SKILL.md), [`github-research`](../skills/github-research/SKILL.md), [`gpt-researcher`](https://github.com/assafelovic/gpt-researcher), [`math-reasoning`](../skills/math-reasoning/SKILL.md), [`paper-context-resolver`](../skills/paper-context-resolver/SKILL.md), [`symbolic-equation`](../skills/symbolic-equation/SKILL.md), [`table-generation`](../skills/table-generation/SKILL.md)

## Pemetaan untuk Antigravity

Target kerja Shikaku dengan dukungan kreatif Kiki-Chii.

- **Bundel** — [`ai-research-explore`](../skills/ai-research-explore/SKILL.md), [`ai-research-reproduction`](../skills/ai-research-reproduction/SKILL.md), [`analyze-project`](../skills/analyze-project/SKILL.md), [`evaluating-code-models`](../skills/evaluating-code-models/SKILL.md), [`evaluating-llms-harness`](../skills/evaluating-llms-harness/SKILL.md), [`explore-code`](../skills/explore-code/SKILL.md), [`explore-run`](../skills/explore-run/SKILL.md), [`filmmaking-videography-photography-s2`](../skills/filmmaking-videography-photography-s2/SKILL.md), [`langsmith-observability`](../skills/langsmith-observability/SKILL.md), [`match-my-writing-style`](../skills/match-my-writing-style/SKILL.md), [`nemo-evaluator-sdk`](../skills/nemo-evaluator-sdk/SKILL.md), [`parenting-6d-gad-mdd`](../skills/parenting-6d-gad-mdd/SKILL.md), [`persona-shizuka-yukino-shikaku`](../skills/persona-shizuka-yukino-shikaku/SKILL.md), [`phoenix-observability`](../skills/phoenix-observability/SKILL.md)
- **Rujukan eksternal** — [`addy-agent-skills`](https://github.com/addyosmani/agent-skills), [`anti-slop`](https://github.com/miqdadbadjuber/anti-slop), [`awesome-copilot`](https://github.com/github/awesome-copilot), [`bang-motion`](https://github.com/bangtutorial/bang-motion), [`better-design`](https://github.com/marvkr/better-design), [`canvas-ui`](https://github.com/DavidHDev/canvas-ui), [`cli-anything`](https://github.com/HKUDS/CLI-Anything), [`cli-anything-catalog`](https://clianything.cc/), [`cursify`](https://github.com/ui-layouts/cursify), [`cybersecurity-library`](https://github.com/mukul975/anthropic-cybersecurity-skills), [`design-taste`](https://github.com/madebymustafa/design-taste), [`goose`](https://github.com/aaif-goose/goose), [`graphify`](https://github.com/Graphify-Labs/graphify), [`hermes-jev-skills`](https://github.com/kerpopule/hermes-jev-skills), [`hermes-steel`](https://github.com/steel-dev/hermes-steel), [`higgsfield-websites`](https://github.com/higgsfield-ai/skills), [`humanizer-en`](https://github.com/blader/humanizer), [`humanizer-indonesia`](https://github.com/adhiprib/humanizer-indonesia), [`mindrally-skills`](https://github.com/mindrally/skills), [`motion-primitives`](https://github.com/ibelick/motion-primitives), [`paper-shaders`](https://github.com/paper-design/shaders), [`playwright-best-practices`](https://github.com/currents-dev/playwright-best-practices-skill), [`ponytail`](https://github.com/dietrichgebert/ponytail), [`rea`](https://github.com/morluto/rea), [`remotion-skills`](https://github.com/remotion-dev/skills), [`reverse-engineer-anything`](https://github.com/NabilRFG12/Reverse-Engineer-anything), [`strix`](https://github.com/usestrix/strix), [`superdesign-skill`](https://github.com/superdesigndev/superdesign-skill), [`superpowers`](https://github.com/obra/superpowers), [`token-monitor`](https://github.com/Javis603/token-monitor), `tokenshield`, [`tokentracker`](https://github.com/xiufengsun/TokenTracker), [`unlimited-ocr`](https://github.com/baidu/Unlimited-OCR), [`unlimited-ocr-2`](https://huggingface.co/baidu/Unlimited-OCR-2)

Pemetaan ini menjelaskan ruang kerja yang dituju. Ikuti panduan host untuk lokasi pemasangan dan gunakan skill yang diaktifkan untuk proyek.
