# MSSHI v3.1.0 - Arti setiap pilihan instalasi

[Bahasa Indonesia](OPTION_GUIDE.md) | [English](OPTION_GUIDE_EN.md)

Penjelasan muncul langsung di `msshi setup`, `msshi select`, `msshi optional list`, serta menu/katalog koneksi aplikasi. Revisi ini tetap memakai versi 3.1.0 dan default yang sama. `--lang en` mengganti bahasa penjelasan setup/select; ID dan format input tetap sama.

```sh
msshi choices rea
msshi choices --kind packs
msshi choices --kind skills
msshi choices --kind apps
msshi choices --lang en
msshi optional list --lang en
```

Perintah di atas hanya membaca bantuan: tidak memasang, login, membuka aplikasi, mengambil upstream, atau memanggil LLM. Instruksi skill, aplikasi/runtime, bobot model, akun, dan eksekusi tugas adalah tahap yang berbeda. Menekan Enter mengikuti default yang ditampilkan: REA Tidak/OFF; KAT Lewati. Opsi yang dilewati dapat ditambahkan nanti.

## Mode setup

| ID | Fungsi / prasyarat |
| --- | --- |
| solo | Pasang semua skill standar pada satu agen; REA tetap terpisah dan tidak aktif secara default. |
| custom-bots | Buat jumlah, nama, dan peran bot sendiri, lalu pilih skill masing-masing. |
| selective | Pasang hanya kategori pilihan beserta skill fondasi yang diwajibkan paket. |
| muza-preset | Buat tim Yukino untuk ide, Shizuka untuk koordinasi, Val untuk riset, Kiki untuk kreatif, dan Shikaku untuk kode. |

## Agen tujuan

| ID | Fungsi / prasyarat |
| --- | --- |
| hermes | Pasang ke folder skill Hermes Agent; akun dan model utama tetap milik pengguna. |
| openclaw | Pasang instruksi skill untuk OpenClaw; koneksi layanan mengikuti setup OpenClaw pengguna. |
| claude | Pasang ke folder skill Claude Code; untuk Claude.ai gunakan jalur unggah ZIP yang dijelaskan di README. |
| codex | Pasang ke folder skill Codex; ini bukan unggahan Knowledge ke ChatGPT. |
| antigravity | Pasang instruksi skill ke lokasi Antigravity yang dipilih tanpa mengganti model IDE. |
| manual | Pilih sendiri folder tujuan untuk agen lain yang mendukung SKILL.md. |

## Paket skill

| ID | Fungsi / prasyarat |
| --- | --- |
| core | Fondasi ideasi, gaya tulisan, persona, OCR, koordinasi, dan akses alat sesuai tugas. |
| filmmaking | Perencanaan film/foto, visual, motion graphics, dan video; produksi memakai alat yang disiapkan terpisah. |
| business | Analisis usaha, skenario keuangan, dan perhitungan bisnis lewat harness lokal. |
| thesis | Ide penelitian, literatur, metode, analisis data, penulisan, revisi, dan presentasi skripsi. |
| webdev | Pemetaan proyek, pengembangan web/UI, eksperimen kode, dan pengujian. |
| cybersec | Pemetaan kode dan panduan audit keamanan pada target yang izinnya jelas; engine dipasang terpisah. |

## Fitur opsional dan prasyarat

| ID | Fungsi / prasyarat |
| --- | --- |
| rea | Analisis statis JavaScript/arsip milik pengguna melalui CLI; berguna untuk memahami aplikasi dan artefak. Default Tidak; pilihan ini hanya memasang wrapper, bukan runtime atau engine native. |
| rea-runtime | Pasang dependency npm REA ke runtime terisolasi; memerlukan Node/npm yang kompatibel dan unduhan internet. Engine seperti Ghidra dipasang terpisah; tidak menambahkan server MCP. |
| pull-upstreams | Unduh repositori referensi eksternal ke cache untuk modul tambahan. Memakai internet dan ruang disk; tidak otomatis menjalankan kode atau menjamin dependency/akun siap. |
| custom-display-names | Ubah nama tampilan bot pada preset; pembagian peran dan ID folder tetap sama. |
| artcraft | Aplikasi kreatif opsional untuk foto, video, audio, desain, dan dokumen melalui adapter yang tersedia. Boleh dilewati; aplikasi, lisensi, atau akun layanan disiapkan terpisah dan tidak dibuka saat boot. |
| kat | Subagen coding tambahan untuk pekerjaan kode, terpisah dari model utama. Pilihan di sini hanya menyimpan preferensi kesiapan; tidak mengunduh model dan belum mengaktifkan subagen. |
| kat-light | Rencana KAT lokal dengan kuantisasi IQ2_XS/IQ3_XXS untuk jejak memori lebih kecil. Perlu file model dan pemeriksaan RAM nyata; memilihnya tidak mengunduh atau memuat model. |
| kat-ideal | Rencana KAT lokal dengan kuantisasi Q4_K_M yang umumnya lebih berat dari opsi ringan. Perlu file model dan RAM cukup; memilihnya tidak mengunduh atau memuat model. |
| kat-cloud | Rencana memakai endpoint API terpisah untuk subagen coding. Perlu akun/endpoint dan persetujuan biaya; pilihan ini tidak membuat panggilan API atau mengganti model utama. |
| kat-skip | Lewati konfigurasi KAT; coding tetap dapat memakai agen dan model utama yang sudah diatur. |
| skill-vs-pack | Paket memilih kelompok skill sesuai bidang; skill individual memberi kontrol satu per satu. Skill fondasi wajib tetap disertakan, dan referensi eksternal belum tentu siap dijalankan. |
| voice | Suara lokal OmniVoice untuk audio atau baca-nyaring yang diminta; tidak otomatis menyuarakan setiap chat. Perlu bobot, RAM, dan setup audio; lisensi bobot membatasi penggunaan komersial. |
| dream | Buat proposal rangkuman/pelajaran secara lokal dan deterministik dari bahan terpilih. Tidak memanggil LLM atau otomatis memasukkan proposal ke memori aktif. |
| steel | Browser utama untuk penjelajahan umum jika key/endpoint sudah disiapkan; layanan dapat berbiaya. Akses akun personal perlu persetujuan sesuai tugas, dan login browser lain tidak disalin otomatis. |
| gitlab | Akses proyek GitLab melalui MCP web dengan autentikasi dan izin akun yang sesuai. Baca hanya data dalam lingkup tugas; perubahan proyek memerlukan instruksi yang jelas. |
| tinyfish | Cari atau ambil informasi web melalui MCP web setelah login layanan. Operasi dapat memakai kuota/kredit; registrasi koneksi saja tidak membuktikan autentikasi atau tugas berhasil. |
| brightdata | Layanan pengambilan data web opsional; tetap nonaktif tanpa akun dan API key. Pemakaian perlu setup layanan dan pemeriksaan biaya/kuota sebelum dijalankan. |
| llmtrim | Padatkan keluaran JSON besar yang memenuhi syarat tanpa kehilangan nilai, dengan pemeriksaan kesetaraan. Tidak memadatkan semua chat atau menjamin persentase penghematan tagihan tertentu. |
| hersona | Cari referensi persona dan siapkan draf penyesuaian karakter melalui CLI. Persona aktif tetap mengikuti SOUL native; draf tidak otomatis menimpa pengaturan pengguna. |
| timesfm-runtime | Siapkan dependency dan bobot TimesFM untuk prediksi deret waktu lokal. Memerlukan unduhan, ruang disk, dan RAM cukup; uji kecil bukan jaminan akurasi pada data pengguna. |
| brag-runtime | Siapkan Hyperframes untuk memvalidasi dan merender video lokal dari komposisi HTML yang dapat diedit. Perlu Node, browser/FFmpeg yang sesuai, RAM/disk, dan hak aset; font dapat memerlukan unduhan. |
| scrapling-runtime | Siapkan parser terisolasi untuk ekstraksi CSS/XPath dari file HTML lokal. Memerlukan dependency Python yang kompatibel; opsi ini tidak menyediakan browser stealth atau crawler jaringan. |
| harness2-runtime | Siapkan framework untuk demo perbaikan harness yang deterministik dan proposal eksperimen. Perlu Python/dependency yang kompatibel; benchmark berbasis model dan promosi perubahan ke bot tidak otomatis aktif. |
| managed-update | Perbarui salinan skill yang terdaftar dan fingerprint-nya cocok; pertahankan edit lokal yang berbeda. Pendaftaran ini bukan izin mengganti SOUL, provider/model, atau semua dependency runtime. |
| upstream-cache | Simpan checkout referensi eksternal di luar folder skill agar dapat diperiksa atau diintegrasikan terpisah. Cache memakai internet/disk dan tidak sama dengan fitur yang sudah terpasang atau aktif. |

## Pilihan koneksi aplikasi

Pilihan ini hanya mengatur registri rute. Aplikasi, runtime, login, izin akun, dan biaya layanan merupakan prasyarat terpisah; tidak ada aplikasi yang dibuka saat boot.

| ID | Fungsi |
| --- | --- |
| auto-reconnect | Daftarkan rute yang sudah terdeteksi/terkonfigurasi; tidak membuka aplikasi, melakukan login, atau membuktikan operasi layanan berhasil. |
| select | Pilih rute satu per satu untuk registri profil ini; hanya yang dipilih ditambahkan, aplikasi tetap dibuka saat ada tugas. |

| ID | Fungsi / prasyarat |
| --- | --- |
| existing | Daftarkan ulang konektor Hermes yang sudah aktif pada profil ini; login dan keberhasilan operasi tetap perlu diperiksa terpisah. |
| artcraft | Daftarkan kelompok 15 aplikasi kreatif ArtCraft untuk video, gambar, audio, desain, dokumen, dan 3D; aplikasi/runtime dipasang terpisah. |
| gdrive-web | Akses file Google Drive melalui web ketika tugas memerlukannya; perlu login dan izin akun, mengikuti kebijakan browser aktif. |
| perplexity | Riset dan pencarian melalui Perplexity; akses web/aplikasi serta batas akun diperiksa saat dipakai, tanpa membuka aplikasi sekarang. |
| youtube-chrome | Akses YouTube untuk riset video melalui rute yang tersedia; browser personal memerlukan izin sesuai tugas dan kebijakan aktif. |
| tiktok | Riset konten TikTok melalui web/aplikasi; login, izin akun, dan kebijakan browser tetap berlaku. |
| antigravity | Gunakan IDE Antigravity untuk workspace coding yang dipilih; IDE harus terpasang dan baru dibuka saat ada tugas. |
| blender | Pengerjaan scene, model, animasi, dan render 3D di Blender melalui rute yang terdaftar; perlu Blender dan adapter yang sesuai. |
| blender-cli | Kendalikan Blender lewat harness CLI-Anything untuk tugas 3D/render; perlu Blender dan executable cli-anything-blender. |
| ffmpeg | Konversi, potong, gabungkan, atau periksa media audio/video lewat CLI lokal; perlu executable FFmpeg. |
| cli-hub | Cari dan kelola harness CLI-Anything; menampilkan katalog tidak memasang atau menjalankan harness/aplikasi lain. |
| libreoffice | Olah dokumen, spreadsheet, dan presentasi lewat harness LibreOffice; perlu aplikasi dan harness CLI-Anything. |
| gimp | Edit gambar raster dan komposisi melalui harness GIMP; perlu GIMP dan harness CLI-Anything. |
| obs | Atur scene dan rekaman/streaming OBS melalui harness; mulai merekam atau siaran tetap merupakan tindakan tugas terpisah. |
| audacity | Edit dan olah audio lewat harness Audacity; perlu Audacity dan harness CLI-Anything. |
| inkscape | Buat dan edit grafis vektor/SVG melalui harness Inkscape; perlu Inkscape dan harness CLI-Anything. |
| krita | Ilustrasi dan lukisan digital melalui harness Krita; perlu Krita dan harness CLI-Anything. |
| kdenlive | Susun dan edit timeline video melalui harness Kdenlive; perlu Kdenlive dan harness CLI-Anything. |
| drawio | Buat dan edit diagram alur atau arsitektur melalui harness draw.io; perlu aplikasi dan harness yang sesuai. |
| filmcraft | Pengerjaan video dan timeline editing di FilmCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| effectcraft | Pengerjaan efek visual dan motion di EffectCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| photocraft | Pengerjaan dan penyuntingan foto di PhotoCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| lightcraft | Kelola dan kembangkan foto, warna, serta hasil ekspor di LightCraft; perlu aplikasi/adapter dan library foto yang dapat dipakai. |
| soundcraft | Pengerjaan audio, penyuntingan, dan mixing di SoundCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| designcraft | Pengerjaan desain visual dan layout di DesignCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| vectorcraft | Pengerjaan ilustrasi dan grafis vektor di VectorCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| figcraft | Pengerjaan desain antarmuka dan layout di FigCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| wordcraft | Pengerjaan dokumen teks dan pemformatan di WordCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| gridcraft | Pengerjaan tabel dan spreadsheet di GridCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| deckcraft | Pengerjaan slide dan presentasi di DeckCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| pdfcraft | Pengerjaan dokumen PDF di PDFCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| cadcraft | Pengerjaan gambar dan rancangan CAD di CADCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| solidcraft | Pengerjaan model solid dan rancangan 3D di SolidCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| craftanything | Pengerjaan proyek kreatif melalui Craft Anything; fungsi yang dapat dipanggil bergantung aplikasi/adapter terpasang. |
| materialcraft | Pengerjaan material untuk proyek visual/3D di MaterialCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| texturecraft | Pengerjaan tekstur untuk proyek visual/3D di TextureCraft; perlu aplikasi serta adapter CLI yang tersedia. |
| git | Kelola versi source code dan riwayat perubahan lewat Git; push atau penulisan remote tetap memerlukan izin tugas dan akses akun. |
| gitlab | Akses proyek dan data GitLab melalui adapter yang terdaftar; perlu autentikasi serta izin proyek yang sesuai. |
| mcp:gitlab | Akses proyek, issue, dan data GitLab melalui konektor MCP yang terdaftar; autentikasi dan izin proyek diperiksa terpisah, registrasi bukan bukti operasi berhasil. |
| mcp:tinyfish | Gunakan layanan otomasi/pencarian web Tinyfish melalui MCP untuk tugas yang diizinkan; perlu login serta izin kuota/biaya, registrasi bukan bukti koneksi berhasil. |
| node | Jalankan tool/proyek JavaScript dengan Node.js lokal; memilih rute tidak memasang paket atau menjalankan proyek. |
| python | Jalankan tool/proyek Python lokal; memilih rute tidak memasang dependency atau menjalankan kode. |
| graphify | Petakan hubungan file/kode menjadi graf proyek melalui Graphify lokal; perlu runtime serta input proyek yang dipilih. |
| whatsapp-web | Akses WhatsApp Web saat tugas memerlukannya; perlu sesi akun dan izin terikat tugas, pengiriman pesan memerlukan otorisasi. |
| hersona | Kelola personalisasi/persona melalui Hersona CLI; memilih rute tidak mengubah persona atau konfigurasi model. |
| llmtrim | Padatkan payload yang memenuhi syarat melalui llmtrim CLI; manfaat bergantung input dan tidak menjamin penghematan seluruh tagihan token. |

Nama aplikasi menjelaskan kegunaannya; deteksi atau registrasi saja tidak membuktikan login maupun keberhasilan tugas. Ekstensi CLI dan konektor MCP yang belum dikenal mendapat penjelasan umum sampai dokumentasinya diperiksa. Bahasa menu koneksi mengikuti `MSSHI_LANG=en` (PowerShell: `$env:MSSHI_LANG="en"`) atau locale `LANG` berbahasa Inggris.

## Katalog skill individual

Katalog berisi 121 nama kanonis: 62 folder instruksi bawaan dan 59 referensi eksternal. Ini bukan 121 repositori; manifest upstream tetap berisi 49 sumber. Alias adalah nama alternatif, bukan skill tambahan. “Dibundel” berarti instruksinya tersedia, bukan aplikasi, akun, atau runtime-nya sudah terpasang. REA terlihat dalam katalog tetapi tetap berada di luar paket standar dan default OFF.

| Skill | Status | Fungsi |
| --- | --- | --- |
| academic-plotting | Instruksi dibundel | Menghasilkan figur publikasi dari data dan spesifikasi yang disepakati. |
| addy-agent-skills | Eksternal; setup terpisah | Menerapkan praktik engineering pada implementasi dan review. |
| ai-research-explore | Instruksi dibundel | Merancang eksperimen kandidat yang terpisah dari baseline. |
| ai-research-reproduction | Instruksi dibundel | Menetapkan target reproduksi penelitian yang dapat dibuktikan. |
| analyze-project | Instruksi dibundel | Memetakan struktur proyek, konfigurasi, titik masuk, dan risiko perubahan. |
| anti-slop | Eksternal; setup terpisah | Memeriksa klise, struktur antarmuka, dan pola kode yang berulang. |
| antigravity-webdev-cybersec | Instruksi dibundel | Hubungkan pengerjaan web dan evaluasi keamanan terotorisasi dengan Antigravity, Goose, dan alat lokal. |
| artcraft-cadcraft | Eksternal; setup terpisah | Gunakan adapter aplikasi yang tersedia untuk gambar teknis dan pengerjaan CAD. |
| artcraft-craftanything | Eksternal; setup terpisah | Gunakan adapter aplikasi yang tersedia untuk mengoordinasikan pekerjaan kreatif lintas alat. |
| artcraft-deckcraft | Eksternal; setup terpisah | Gunakan adapter aplikasi yang tersedia untuk membuat dan menyunting presentasi. |
| artcraft-designcraft | Eksternal; setup terpisah | Gunakan adapter aplikasi yang tersedia untuk membuat dan menyunting desain visual. |
| artcraft-effectcraft | Eksternal; setup terpisah | Gunakan adapter aplikasi yang tersedia untuk efek visual dan compositing. |
| artcraft-figcraft | Eksternal; setup terpisah | Gunakan adapter aplikasi yang tersedia untuk desain antarmuka dan prototipe. |
| artcraft-filmcraft | Eksternal; setup terpisah | Gunakan adapter aplikasi yang tersedia untuk merencanakan adegan dan shot. |
| artcraft-gridcraft | Eksternal; setup terpisah | Gunakan adapter aplikasi yang tersedia untuk tabel dan perencanaan produksi. |
| artcraft-lightcraft | Eksternal; setup terpisah | Gunakan adapter aplikasi yang tersedia untuk mengolah, memotong, dan mengekspor foto. |
| artcraft-pdfcraft | Eksternal; setup terpisah | Gunakan adapter aplikasi yang tersedia untuk menyiapkan dokumen PDF. |
| artcraft-photocraft | Eksternal; setup terpisah | Gunakan adapter aplikasi yang tersedia untuk mengolah dan meninjau foto. |
| artcraft-solidcraft | Eksternal; setup terpisah | Gunakan adapter aplikasi yang tersedia untuk membuat model bentuk padat. |
| artcraft-soundcraft | Eksternal; setup terpisah | Gunakan adapter aplikasi yang tersedia untuk rancangan suara dan mixing. |
| artcraft-vectorcraft | Eksternal; setup terpisah | Gunakan adapter aplikasi yang tersedia untuk membuat dan menyunting aset vektor. |
| artcraft-wordcraft | Eksternal; setup terpisah | Gunakan adapter aplikasi yang tersedia untuk menulis dokumen produksi. |
| auto-curiousity-for-film-making | Instruksi dibundel | Menguji kemampuan alat kreatif dan teknik produksi dalam eksperimen terpisah. |
| autoresearch | Instruksi dibundel | Mengoordinasikan siklus eksperimen dan sintesis dengan batas berhenti. |
| awesome-copilot | Eksternal; setup terpisah | Memilih contoh instruksi dan praktik pengembangan yang dapat diadaptasi. |
| backward-traceability | Instruksi dibundel | Menautkan angka dan hasil laporan kembali ke data, skrip, atau perhitungan. |
| bang-motion | Eksternal; setup terpisah | Memandu motion graphics berbasis kode sesuai brief. |
| barty-motion-graphics | Eksternal; setup terpisah | Memandu komposisi grafis gerak dan animasi berbasis kode. |
| better-design | Eksternal; setup terpisah | Membantu tinjauan kualitas dan hierarki desain. |
| blender-mcp | Eksternal; setup terpisah | Koordinasikan adegan 3D dan render melalui adapter Blender yang tersedia; setup desktop memakai CLI native. |
| brag | Instruksi dibundel | Rancang video peluncuran produk yang dapat diedit dengan Hyperframes, dimulai dari konsep dan review manusia. |
| brainstorming-research-ideas | Instruksi dibundel | Memakai kerangka ideasi terstruktur untuk menemukan pertanyaan layak. |
| business-sage | Instruksi dibundel | Menyusun analisis usaha, skenario finansial, dan pertanyaan verifikasi aturan yang relevan. |
| canvas-ui | Eksternal; setup terpisah | Menelaah komponen visual berbasis kanvas untuk interaksi khusus. |
| charlie-motion-graphics | Eksternal; setup terpisah | Menyusun pendekatan motion graphics dan urutan gerak dari storyboard. |
| chatgpt-hermes-portability-kit | Instruksi dibundel | Memandu adaptasi metode dan profil ke platform lain menggunakan sumber yang sah. |
| cli-anything | Eksternal; setup terpisah | Memanggil CLI atau aplikasi melalui adapter yang dipilih untuk tugas aktif. |
| cli-anything-business-sage | Instruksi dibundel | Menjalankan perhitungan bisnis terstruktur melalui harness lokal yang tersedia. |
| cli-anything-catalog | Eksternal; setup terpisah | Direktori untuk menemukan adapter CLI yang relevan dengan tugas. |
| cli-anything-universal-bridge | Instruksi dibundel | Daftarkan, periksa, dan jalankan rute aplikasi, browser, serta alat agen yang tersedia saat dibutuhkan. |
| creative-thinking-for-research | Instruksi dibundel | Mencoba reframing, analogi, dan kombinasi konsep untuk membuka pilihan. |
| cursify | Eksternal; setup terpisah | Memilih interaksi kursor yang sesuai dengan kebutuhan antarmuka. |
| cybersecurity-library | Eksternal; setup terpisah | Menemukan panduan keamanan sesuai lingkup audit yang sah. |
| data-analysis | Instruksi dibundel | Memeriksa kualitas data, asumsi, uji statistik, dan ketidakpastian. |
| deep-research | Instruksi dibundel | Menyusun pertanyaan, menelusuri literatur, dan mensintesis bukti yang dapat diperiksa. |
| design-taste | Eksternal; setup terpisah | Memilih gaya visual, tipografi, dan komposisi yang sesuai. |
| evaluating-code-models | Instruksi dibundel | Menguji keluaran model kode dengan tugas dan tolok ukur yang relevan. |
| evaluating-llms-harness | Instruksi dibundel | Rencanakan evaluasi LLM memakai harness yang kompatibel dan anggaran yang disepakati. |
| explore-code | Instruksi dibundel | Mengembangkan perubahan eksperimen dalam ruang kerja terisolasi. |
| explore-run | Instruksi dibundel | Menjalankan uji terbatas dengan anggaran dan catatan hasil yang jelas. |
| filmmaking-videography-photography-s2 | Instruksi dibundel | Menyatukan konsep, pengarahan, kamera, foto, penyuntingan, warna, dan suara. |
| firecrawl-competitive-intel | Instruksi dibundel | Membandingkan perubahan produk, harga, dan fitur dengan bukti bertanggal. |
| firecrawl-dashboard-reporting | Instruksi dibundel | Mengambil dan memeriksa indikator dasbor untuk pelaporan. |
| firecrawl-deep-research | Instruksi dibundel | Mengumpulkan bukti web untuk sintesis dengan atribusi. |
| firecrawl-knowledge-base | Instruksi dibundel | Menyiapkan koleksi dokumen, potongan, serta metadata asalnya. |
| firecrawl-research-papers | Instruksi dibundel | Menemukan dan memeriksa makalah pada sumber akademik yang relevan. |
| focus-my-energy | Instruksi dibundel | Menyesuaikan beban tugas dan langkah awal dengan energi yang dilaporkan pengguna. |
| generate-fresh-ideas | Instruksi dibundel | Menghasilkan alternatif dari beberapa lensa kreatif untuk disaring pengguna. |
| get-more-perspectives | Instruksi dibundel | Menguji keputusan dari beberapa sudut pandang sebelum memilih. |
| github-research | Instruksi dibundel | Menelaah lisensi, rancangan, pemeliharaan, dan kesiapan repositori. |
| goose | Eksternal; setup terpisah | Menjalankan siklus perubahan kode dan pengujian bila harness Goose tersedia. |
| gpt-researcher | Eksternal; setup terpisah | Mengumpulkan dan menyusun bahan riset; Val memeriksa sumber sebelum penyerahan. |
| graphify | Eksternal; setup terpisah | Membuat peta struktur proyek untuk penelusuran konteks. |
| harness2 | Instruksi dibundel | Evaluasi harness Propose-Probe-Compose menggunakan demo deterministik dan proposal yang ditinjau manusia. |
| hermes-jev-skills | Eksternal; setup terpisah | Memilih skill dari konteks dengan pengalihan model dinonaktifkan. |
| hermes-steel | Eksternal; setup terpisah | Gunakan integrasi browser Steel yang tersedia untuk tugas penjelajahan yang diizinkan. |
| higgsfield-brandkit | Eksternal; setup terpisah | Menerapkan sistem visual merek pada produksi aset. |
| higgsfield-faceless-video | Eksternal; setup terpisah | Menyiapkan video tanpa tampil wajah dari skrip, tempo, dan aset. |
| higgsfield-generate | Eksternal; setup terpisah | Menghasilkan atau mengolah media setelah konsep dan parameter disetujui. |
| higgsfield-marketplace-cards | Eksternal; setup terpisah | Menyusun kartu promosi produk dengan pesan dan spesifikasi kanal. |
| higgsfield-product-photoshoot | Eksternal; setup terpisah | Mengatur konsep foto produk, pencahayaan, dan framing. |
| higgsfield-skills | Instruksi dibundel | Rutekan kebutuhan produksi kreatif ke modul Higgsfield yang sesuai setelah konsep disetujui. |
| higgsfield-soul-id | Eksternal; setup terpisah | Mengelola konsistensi subjek dengan referensi yang diizinkan. |
| higgsfield-video-explainer | Eksternal; setup terpisah | Mengubah penjelasan konsep menjadi urutan adegan. |
| higgsfield-websites | Eksternal; setup terpisah | Memetakan brief produk ke konsep situs dan aset pendukung. |
| higgsfield-youtube-thumbnail | Eksternal; setup terpisah | Membuat konsep thumbnail sesuai isi video dan identitas kanal. |
| humanizer-en | Instruksi dibundel | Sunting prosa bahasa Inggris agar terasa alami sambil menjaga makna, suara penulis, dan sitasi. |
| humanizer-indonesia | Instruksi dibundel | Sunting prosa bahasa Indonesia sesuai ragam pembaca sambil menjaga makna, istilah, dan sitasi. |
| idea-generation | Instruksi dibundel | Mengembangkan dan menyaring gagasan penelitian dalam beberapa putaran. |
| langsmith-observability | Instruksi dibundel | Memandu observabilitas dan evaluasi LangSmith pada lingkungan yang disetujui. |
| literature-review | Instruksi dibundel | Membangun tinjauan pustaka dengan beberapa perspektif dan jejak sumber. |
| match-my-writing-style | Instruksi dibundel | Menerapkan Voice Card yang disediakan pengguna sesuai audiens dan jenis tulisan. |
| math-reasoning | Instruksi dibundel | Memeriksa langkah penalaran matematika dan syarat berlakunya. |
| mindrally-skills | Eksternal; setup terpisah | Menemukan panduan implementasi relevan di katalog eksternal. |
| motion-graphics-suite | Instruksi dibundel | Pilih dan hubungkan empat rujukan motion graphics untuk komposisi yang tetap dapat diedit. |
| motion-primitives | Eksternal; setup terpisah | Merancang gerak antarmuka memakai komponen animasi. |
| nemo-evaluator-sdk | Instruksi dibundel | Memandu evaluasi dengan NeMo Evaluator SDK jika dependensinya tersedia. |
| notebooklm-thinking-datascience | Instruksi dibundel | Terapkan metode berpikir sistem dan data science dari indeks sumber milik pengguna. |
| novelty-assessment | Instruksi dibundel | Menguji klaim kebaruan terhadap studi terdekat dan batas pencarian. |
| paper-context-resolver | Instruksi dibundel | Mengikat klaim reproduksi pada bagian, gambar, tabel, atau lampiran makalah. |
| paper-revision | Instruksi dibundel | Memetakan catatan revisi ke perubahan konkret dan bukti perbaikan. |
| paper-shaders | Eksternal; setup terpisah | Menyiapkan efek shader yang terukur dan sesuai perangkat. |
| paper-writing-section | Instruksi dibundel | Menyusun dan menyunting bagian naskah akademik dengan dua tahap pemeriksaan. |
| parenting-6d-gad-mdd | Instruksi dibundel | Dukung percakapan dengan empati, struktur, dan otonomi; panduan ini tidak menggantikan perawatan klinis. |
| persona-shizuka-yukino-shikaku | Instruksi dibundel | Menjaga karakter, kontrak serah terima, dan batas kepemilikan tugas lima bot. |
| phoenix-observability | Instruksi dibundel | Memandu tracing dan evaluasi Phoenix tanpa memindahkan data di luar lingkup. |
| playwright-best-practices | Eksternal; setup terpisah | Menguji jalur pengguna dan memperbaiki kestabilan tes E2E. |
| ponytail | Eksternal; setup terpisah | Mengurangi kerumitan solusi dan memilih perubahan yang sesuai kebutuhan. |
| prep-for-meetings | Instruksi dibundel | Menyusun ringkasan pertemuan dari catatan dan tujuan yang tersedia. |
| prep-for-meetings-2 | Instruksi dibundel | Memadatkan bahan pertemuan menjadi pokok bahasan dan kartu pengingat. |
| rea | Opsional OFF; runtime terpisah | Analisis statis JavaScript atau arsip milik pengguna lewat CLI lokal; format native memerlukan engine terpisah. |
| rebuttal-writing | Instruksi dibundel | Menyusun jawaban poin demi poin untuk masukan pembimbing atau reviewer. |
| remote-jobs | Eksternal; setup terpisah | Menyaring perusahaan remote, lalu memeriksa syarat lokasi dan lowongan langsung. |
| remotion-skills | Eksternal; setup terpisah | Merancang komposisi video sebagai kode dan merendernya bila runtime tersedia. |
| research-paper-writing | Instruksi dibundel | Memeriksa struktur argumen dan hubungan antara klaim, bukti, serta pembahasan. |
| reverse-engineer-anything | Eksternal; setup terpisah | Memeriksa artefak insiden secara forensik dalam mandat yang jelas. |
| scrapling | Instruksi dibundel | Ekstraksi CSS/XPath dari HTML lokal dalam runtime parser terisolasi. |
| slide-generation | Instruksi dibundel | Menyusun presentasi dari argumen, hasil, dan visual yang dapat diverifikasi. |
| strix | Eksternal; setup terpisah | Menguji keamanan target yang lingkup dan izin aksesnya telah disetujui. |
| superdesign-skill | Eksternal; setup terpisah | Menilai tata letak, token desain, dan konsistensi antarmuka. |
| superpowers | Eksternal; setup terpisah | Menata perencanaan, implementasi, dan validasi perubahan kode. |
| symbolic-equation | Instruksi dibundel | Mencari kandidat persamaan yang dapat ditafsirkan dan diuji. |
| table-generation | Instruksi dibundel | Membangun tabel akademik dari hasil terverifikasi beserta satuan dan catatan. |
| timesfm-forecasting | Instruksi dibundel | Prediksi deret waktu numerik secara lokal memakai TimesFM 2.5 setelah setup runtime dan bobot terpisah. |
| token-monitor | Eksternal; setup terpisah | Sumber status kuota tambahan untuk kebijakan anggaran. |
| tokenshield | Eksternal; setup terpisah | Gabungkan data penggunaan, estimasi biaya, dan pemeriksaan anggaran; ini bukan batas tagihan keras dari provider. |
| tokentracker | Eksternal; setup terpisah | Sumber data penggunaan lokal untuk kebijakan anggaran. |
| unlimited-ocr | Eksternal; setup terpisah | Memandu runtime OCR lokal dan indeks halaman. |
| unlimited-ocr-2 | Instruksi dibundel | Rutekan ekstraksi dokumen dan gambar berhalaman ke OCR yang tersedia dengan penunjuk bukti. |
| unslop | Instruksi dibundel | Tinjau dan perbaiki desain antarmuka; skill ini mengubah UI, bukan gaya prosa bot. |
| wise-judgment-and-sovereign-orchestrator | Instruksi dibundel | Mengatur pilihan alur, anggaran, persetujuan, delegasi, dan sintesis hasil Val. |

### Alias

| Alias | Nama kanonis |
| --- | --- |
| auto-curiosity-for-film-making | auto-curiousity-for-film-making |

Sumber teks menu: [option_help.json](../configs/option_help.json), [bantuan aplikasi](../skills/cli-anything-universal-bridge/scripts/connection_help.json). Lihat juga [CLI](CLI.md), [REA](REA.md), dan [lisensi pihak ketiga](../THIRD_PARTY_NOTICES.md).
