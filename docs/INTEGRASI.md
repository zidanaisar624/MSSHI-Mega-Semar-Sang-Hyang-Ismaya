# Integrasi eksternal MSSHI Tahap 1

Katalog memuat **37 tautan sumber** dari brief. Itu terdiri dari 35 repositori GitHub, satu kartu model Hugging Face dan satu situs katalog. Masing-masing dicocokkan dengan paket, peran, kegunaan, prasyarat dan lisensinya. Inventaris mesin tersedia di [configs/upstreams.json](../configs/upstreams.json).

Status `external-opt-in` berarti operator memilih sendiri integrasi yang akan dipasang atau dijalankan. Pemeriksaan dokumentasi tidak menguji seluruh runtime pada tiap host. Tahap ini menyiapkan rute dan rujukan. Pemilihan akun, penggunaan provider/model, pemasangan pihak ketiga dan aktivasi layanan berada di luar eksekusi Tahap 1.

## Memilih dan memeriksa integrasi

1. Cocokkan keluaran dengan `use_when`. Dalam tim MuZA ikuti matriks pemilik tugas. Dalam Solo, agen yang sama memilih rute sesuai konteks.
2. Catat commit/release yang akan dipakai. Baca lisensi, notice aset, prasyarat OS dan versi host. Cek `requires` sebelum menjalankan sesuatu.
3. Untuk skill Markdown, salin hanya folder yang dipilih dan referensinya. Untuk plugin, aplikasi, model, registry atau pustaka, tinjau dependensi dan cara pemasangan upstream pada tahap terpisah. Jaga rahasia di secret store lokal dan catat anggaran yang disetujui.
4. Uji operasi terkecil yang relevan, misalnya deteksi perintah lokal, daftar tool tanpa panggilan model, satu halaman OCR publik atau ekspor klip uji dengan aset milik sendiri. Catat hasil dan batas uji.
5. Jika prasyarat gagal, gunakan rute lokal yang tersedia dan laporkan langkah tertunda. Hindari penggantian model/provider, aktivasi layanan atau unggahan otomatis.

## Rute kerja

- **Kreatif.** Kiki-Chii memulai dari konsep, penonton, format, brief visual dan persetujuan. Higgsfield dipilih untuk generasi hosted apabila akun dan anggaran tersedia. Bang Motion cocok untuk opener HTML. Barty-Bart dan Charlie memberi resep motion berbasis kode. Remotion dipakai untuk perakitan, subtitle dan render terprogram. FilmCraft/SoundCraft atau Blender dapat dipakai untuk polishing jika sudah terpasang. Periksa izin aset, biaya dan preview pada tiap tahap.
- **Tulisan.** Pilih humanizer sesuai bahasa dan gaya penulis. Gunakan anti-slop pada bagian prose, UI atau kode yang relevan. Pertahankan fakta, sitasi dan kutipan. Simpan sampel suara pribadi di luar repo publik. Gunakan preset `scripts/metrik.py` hanya setelah mengecek versi yang tersedia.
- **Engineering dan web.** Shikaku Nara dapat memilih Goose setelah konfigurasi lokal, Superpowers untuk perubahan bertahap, Ponytail untuk mengurangi kompleksitas, Graphify untuk pemetaan, lalu satu skill yang cocok dengan stack. Pilih sistem visual berdasarkan brief. Uji komponen, efek dan browser sesuai aksesibilitas, performa, lisensi serta izin lingkungan.
- **Cybersecurity.** Mulai dari audit lokal read-only dan satu playbook relevan. Strix dan REA memakai target serta metode yang berada dalam otorisasi pengguna. Dalam keadaan darurat, beri alert, lakukan triase lokal yang sudah diotorisasi, lalu laporkan bukti dan detail. Pemindaian aktif, perubahan sistem dan transfer artefak memerlukan otorisasi yang mencakup tindakan itu. Pilih satu revisi REA yang sesuai.
- **OCR dan konteks.** Ekstrak lapisan teks PDF secara lokal bila tersedia. Untuk scan, cocokkan versi runtime, model dan hardware. Bagi dokumen per jendela halaman, simpan nomor halaman dan hash sumber, lalu ukur waktu dan puncak memori. OCR lokal dapat menghindari biaya API pada tahap ekstraksi. Penggunaan memori, durasi dan biaya LLM sesudah OCR bergantung pada mesin serta konfigurasi. Teruskan hasil ke indeks, Graphify untuk kode, ringkasan bertingkat dan checkpoint. Jev dipertimbangkan untuk pemilihan skill setelah opsi upstream diperiksa, dengan `jev_model_routing: false` sebagai intent paket.
- **Anggaran.** TokenTracker dan token-monitor adalah sumber perkiraan pemakaian. TokenShield memakai saldo aktual yang tersedia dan taksiran biaya sebelum mengizinkan panggilan berbayar. Ambang cadangan di brief adalah USD 1,00. Bila nilai penting belum tersedia, tahan operasi berbayar atau minta angka yang diperlukan. Telemetri pemakaian tidak menjamin saldo provider.
- **Riset dan karier.** Val memakai GPT Researcher apabila provider, retriever dan batas biaya sudah disepakati. Periksa rujukan dan tanggal. Remote Jobs memberi daftar perusahaan untuk disaring. Konfirmasi lowongan aktif, wilayah, zona waktu dan persyaratan di halaman karier resmi.

## Bridge CLI-Anything sesuai permintaan

Pembantu lokal adalah [cli_anything_sovereign_hub.py](../skills/persona-shizuka-yukino-shikaku/scripts/cli_anything_sovereign_hub.py). Default manifest `auto_open_on_boot: false`. Jalankan preview dari akar repo untuk memeriksa rute.

```console
python skills/persona-shizuka-yukino-shikaku/scripts/cli_anything_sovereign_hub.py --json bridge --target perplexity --query "pertanyaan publik"
```

| Target | Rute | Prasyarat atau batas |
|---|---|---|
| `gdrive-web` | Google Drive di browser | Membuka situs/pencarian. Login, akses file dan API diurus terpisah. |
| `perplexity` | Desktop bila ditemukan dan memori memadai, atau web | Periksa rute preview. Query web memakai URL pencarian. |
| `youtube-chrome` | YouTube di browser | Gunakan browser desktop yang tersedia. Fitur ini bukan konektor akun atau downloader. |
| `tiktok` | TikTok di browser | Gunakan situs resmi dengan sesi yang diizinkan pengguna. |
| `antigravity` | Antigravity yang ditemukan di mesin | Isi direktori proyek melalui `--query`. Tinjau path sebelum meluncurkan. |

Tambahkan `--open` hanya atas permintaan eksplisit untuk membuka target. Periksa apakah query boleh dikirim. Untuk eksekusi harness, pilih versi dan tinjau kode pada tahap terpisah. [Dokumentasi CLI-Anything](https://github.com/HKUDS/CLI-Anything)

Hermes Steel merupakan opsi browser cloud terpisah. Simpan `STEEL_API_KEY` di konfigurasi rahasia lokal, pilih backend hanya atas permintaan, lalu cek data dan biaya layanan. [Dokumentasi Hermes Steel](https://github.com/steel-dev/hermes-steel)

## Inventaris 37 sumber

Lisensi yang tercatat berasal dari README, metadata atau kartu model. Periksa `LICENSE` pada commit terpilih sebelum mendistribusikan kode, contoh, font, suara, bobot, merek atau dependensi.

| ID dan sumber | Fungsi saat dipilih | Lisensi atau catatan distribusi |
|---|---|---|
| [`higgsfield-skills`](https://github.com/higgsfield-ai/skills) | Pilih generasi gambar/video/foto produk atau brand kit dari treatment Kiki-Chii. | MIT untuk skill; akun, kredit dan hasil media tunduk pada ketentuan layanan. |
| [`remotion-skills`](https://github.com/remotion-dev/skills) | Pilih video yang memerlukan timing, rendering terprogram atau subtitle yang dapat diedit. | Lisensi paket skill perlu diperiksa pada revisi; lisensi runtime Remotion terpisah. |
| [`barty-motion-graphics`](https://github.com/Barty-Bart/motion-graphics) | Pilih iklan motion dari kode dan sound pass terstruktur. | MIT; Geist OFL, ikon Lucide ISC, SFX tertentu CC0. Ikuti notice per aset. |
| [`charlie-motion-graphics`](https://github.com/charlie947/motion-graphics-skills) | Pilih motion peluncuran yang seluruh frame-nya dibangun dengan kode. | MIT. |
| [`bang-motion`](https://github.com/bangtutorial/bang-motion) | Pilih opener, promo, teks bergerak atau explainer HTML. | MIT; periksa izin aset dan CDN yang dipakai proyek. |
| [`humanizer-en`](https://github.com/blader/humanizer) | Sunting tulisan Inggris sambil menjaga fakta, kutipan dan suara penulis. | MIT. |
| [`humanizer-indonesia`](https://github.com/adhiprib/humanizer-indonesia) | Sunting tulisan Indonesia menurut ragam akademik, ajar atau semiformal. | MIT. Jangan sertakan sampel suara pribadi di repo publik. |
| [`anti-slop`](https://github.com/miqdadbadjuber/anti-slop) | Tinjau kebiasaan generik pada prose, UI atau kode sesuai output yang diminta. | MIT. |
| [`goose`](https://github.com/aaif-goose/goose) | Delegasikan vibecoding pada workspace yang dipilih. | Apache-2.0. Kebijakan provider dan ekstensi terpisah. |
| [`superpowers`](https://github.com/obra/superpowers) | Gunakan planning, debugging dan verifikasi untuk perubahan bertahap. | MIT. |
| [`ponytail`](https://github.com/dietrichgebert/ponytail) | Tinjau solusi yang terlalu kompleks dan kurangi perubahan yang tidak perlu. | MIT. |
| [`addy-agent-skills`](https://github.com/addyosmani/agent-skills) | Pilih playbook coding, delivery, atau review sesuai fase. | MIT. |
| [`graphify`](https://github.com/Graphify-Labs/graphify) | Petakan kode, dokumentasi dan dependensi sebelum membuka banyak file. | Repo menampilkan Apache-2.0 dan MIT; cek cakupan per file dan revisi. |
| [`mindrally-skills`](https://github.com/mindrally/skills) | Muat keahlian framework atau bahasa yang cocok dengan proyek. | Apache-2.0. |
| [`playwright-best-practices`](https://github.com/currents-dev/playwright-best-practices-skill) | Rancang tes E2E dengan locator, isolasi dan debugging yang dapat diulang. | MIT. |
| [`awesome-copilot`](https://github.com/github/awesome-copilot) | Cari agen, instruksi atau skill Copilot yang sesuai dengan tugas. | MIT; periksa atribusi dan dependensi entry pilihan. |
| [`superdesign-skill`](https://github.com/superdesigndev/superdesign-skill) | Tetapkan gaya, alur antarmuka dan standar visual sebelum implementasi. | MIT untuk repo; layanan eksternal terpisah. |
| [`better-design`](https://github.com/marvkr/better-design) | Cari tema, token desain, atau komponen UI siap adaptasi. | MIT untuk repo; cek dependensi dan merek pihak ketiga. |
| [`design-taste`](https://github.com/madebymustafa/design-taste) | Pilih identitas visual yang cocok dengan brief dan konsistensi antarlayar. | MIT. |
| [`paper-shaders`](https://github.com/paper-design/shaders) | Gunakan shader canvas untuk elemen visual saat efek tersebut diperlukan. | Apache-2.0. |
| [`canvas-ui`](https://github.com/DavidHDev/canvas-ui) | Gunakan komponen WebGL/canvas pada UI dengan anggaran performa yang sesuai. | MIT + Commons Clause menurut upstream; pembatasan menjual library. Tidak disalin ke MSSHI. |
| [`motion-primitives`](https://github.com/ibelick/motion-primitives) | Pilih komponen animasi UI yang bisa disunting dan diuji. | MIT. |
| [`cursify`](https://github.com/ui-layouts/cursify) | Pilih efek kursor React/Next.js bila menambah nilai interaksi. | Lisensi belum terkonfirmasi dari sumber yang dibaca. Jangan vendor sebelum dicek. |
| [`strix`](https://github.com/usestrix/strix) | Tinjau keamanan aplikasi hanya pada target dan metode yang telah diotorisasi. | Apache-2.0 untuk repo; platform cloud dan biaya terpisah. |
| [`cybersecurity-library`](https://github.com/mukul975/anthropic-cybersecurity-skills) | Cari satu playbook sesuai hardening, forensik, deteksi atau audit. | Apache-2.0. Proyek komunitas; bukan produk resmi Anthropic. |
| [`reverse-engineer-anything`](https://github.com/NabilRFG12/Reverse-Engineer-anything?tab=readme-ov-file) | Rujuk alur pemeriksaan artefak pada scope yang disetujui. | MIT menurut LICENSE repo; lisensi debugger dan alat dekompilasi terpisah. |
| [`rea`](https://github.com/morluto/rea) | Gunakan upstream untuk analisis perilaku, file atau binary dalam scope. | MIT; alat eksternal dapat berlisensi terpisah. |
| [`unlimited-ocr-2`](https://huggingface.co/baidu/Unlimited-OCR-2) | Baca PDF scan/buku/gambar panjang dalam jendela halaman, simpan jejak halaman. | MIT menurut model card. Review custom code dan dependency sebelum menjalankan. |
| [`unlimited-ocr`](https://github.com/baidu/Unlimited-OCR) | Jalankan pipeline OCR untuk model yang sesuai versi dokumentasinya. | MIT. |
| [`tokentracker`](https://github.com/xiufengsun/TokenTracker) | Ambil perkiraan pemakaian token dan biaya dari runtime yang didukung. | MIT. Catatan token bukan bukti saldo tersisa. |
| [`token-monitor`](https://github.com/Javis603/token-monitor) | Gunakan data biaya atau aktivitas sesi sebagai masukan meter lokal. | MIT. Catatan biaya bukan jaminan saldo. |
| [`hermes-jev-skills`](https://github.com/kerpopule/hermes-jev-skills) | Pilih kemampuan skill selection hanya bila versi host mendukung dan pengguna mengaktifkan. | MIT. Jangan aktifkan mutasi model/provider melalui konfigurasi paket. |
| [`cli-anything`](https://github.com/HKUDS/CLI-Anything) | Cari harness resmi yang cocok, lalu rencanakan perintah dan jalur kerja. | Apache-2.0 untuk framework. Lisensi aplikasi dan harness yang berbeda perlu diperiksa. |
| [`cli-anything-catalog`](https://clianything.cc/) | Temukan harness dan dokumentasi upstream, kemudian tinjau commit dan lisensinya. | Situs referensi. Lisensi framework tidak otomatis mencakup paket pihak ketiga. |
| [`hermes-steel`](https://github.com/steel-dev/hermes-steel) | Pilih browser cloud hanya bila cakupan data dan biaya disetujui. | MIT untuk plugin; layanan Steel, jaringan, proxy dan biaya terpisah. |
| [`gpt-researcher`](https://github.com/assafelovic/gpt-researcher) | Susun riset mendalam dengan pencarian, ekstraksi dan daftar sumber. | Apache-2.0 untuk repo; API eksternal terpisah. |
| [`remote-jobs`](https://github.com/remoteintech/remote-jobs) | Cari perusahaan remote, lalu verifikasi lowongan aktif di laman resmi perusahaan. | ISC menurut README upstream. Hak atas nama, merek, serta data pihak ketiga terpisah. |
