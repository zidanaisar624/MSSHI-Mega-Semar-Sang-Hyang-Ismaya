# Audit pemasangan skill dan plugin pihak ketiga

Diperiksa untuk MSSHI v3.1.2 pada 18 November 2026. Dokumen ini menjelaskan perilaku pemasang publik dan pembagian peran, tanpa menyertakan profil atau data pribadi pembuat.

**Jawaban singkat:** preset lima bot memasang instruksi 67 skill sesuai peran. Seluruh 51 sumber eksternal tidak otomatis menjadi plugin/runtime aktif. Pilihan akun, model besar, jadwal dan program pendamping tetap dijelaskan dan dipasang terpisah.

## Cara membaca status

- **Instruksi otomatis:** file skill ringan disalin pada peran wajib saat memilih preset. Belum berarti program dijalankan atau sebuah layanan tersambung.
- **Kontekstual:** skill dipilih ketika tugas sesuai bidangnya. Bukan aplikasi yang terbuka saat startup.
- **Opsional:** source, dependency, executable atau akun memerlukan langkah terpisah. `--pull-upstreams` menyimpan sumber/cache tanpa mengeksekusi kode sumber tersebut.
- **Shared:** beberapa bot boleh memakai kemampuan yang sama. Model, SOUL, izin dan hasil tiap profil tetap terpisah.

## Instalasi baru dan susunan lama

Pada instalasi baru preset MuZA, profil default yang sebenarnya menjadi Yukino, ditambah empat spesialis. Pada susunan lama, nama dan profil yang sudah ada dipertahankan. Pemetaan peran dipakai pula oleh pemasang upstream terkurasi, Dreaming dan pengaturan suara. Tidak ada pemindahan model, kredensial atau riwayat antarprofil.

## Plugin dan utilitas: apa yang otomatis?

| Komponen | Pembagian | Perilaku pemasangan / pemicu |
| --- | --- | --- |
| msshi-team-routing | Lima peran; asisten default netral pada susunan lama juga dapat bekerja sama | Pemasang mendaftarkan plugin native; backend delegasi dipilih pengguna. Sebelum konfigurasi Hermes tersedia, plugin tetap staged. Tidak menjalankan percakapan model saat setup. |
| msshi-auto-trim / [LLMtrim](https://github.com/fkiene/llmtrim) | Semua profil yang dipasang dan mempunyai binary | Plugin dapat disiapkan lewat wizard/flag; migrasi mengaktifkan hook jika binary lokal tersedia. Binary tidak otomatis muncul hanya karena skill terpasang. Setelah siap, hasil tool JSON besar dipadatkan otomatis dengan pemeriksaan kesetaraan data. |
| [Hersona](https://github.com/shiro-0x/hersona) | Pendamping bersama sesuai tugas persona | CLI terpisah, dipakai untuk katalog atau draf bila diminta; tidak menimpa SOUL. Binary dan dependensi perlu tersedia. |
| Hermes-Dreaming | Lima peran, diproses terpisah | Pilihan plugin 3 membuat laporan offline sekali. Jadwal Windows pukul 03.00 WIB hanya dibuat melalui `msshi dream --register`. Tidak membangunkan model atau mempromosikan memori otomatis pada adapter MSSHI. |
| OmniVoice | Lima peran, dengan pengaturan suara masing-masing | Runtime dan bobot perlu dipasang terpisah; baru aktif setelah sintesis lokal terverifikasi. Tidak otomatis menyuarakan setiap chat. |
| Browser pilihan pengguna | Per tugas yang diizinkan | Chrome, Edge, Firefox, atau none; label profil/akun hanya preferensi pribadi, login manual, tanpa penyalinan cookie atau browser cloud otomatis. |
| Layanan web eksternal | Pilihan masing-masing pengguna | GitLab, Tinyfish, BrightData dan Steel tidak didaftarkan oleh installer. Sambungkan sendiri jika diperlukan; status lokal bukan bukti operasi layanan berhasil. |
| Aplikasi desktop / CLI-Anything | Sesuai pembagian spesialis | Rute native dan tiket tugas; aplikasi tidak dibuka saat startup. Ditemukannya executable bukan bukti seluruh operasi editing telah diuji. |

LLMtrim dan Hersona merupakan utilitas pendamping yang dicatat terpisah dari 51 entri manifest sumber. Tidak ada janji seluruh chat bebas token atau seluruh runtime eksternal otomatis tersedia.

## Dreaming dan Unslop

Dreaming yang dipakai MSSHI dipatok pada revisi `21878d3ec8752283dd7ee69a803c63bb989c1740`. Dokumentasi upstream menyediakan plugin portabel dan pemasang gate/cron sendiri; jalur upstream lengkap dapat menjalankan giliran agen bila diperlukan, sedangkan judge cloud merupakan pilihan terpisah. Adapter MSSHI memilih laporan lokal deterministik tanpa giliran agen. [Dokumentasi pinned](https://raw.githubusercontent.com/itpartypattaya/hermes-dreaming/21878d3ec8752283dd7ee69a803c63bb989c1740/README.md), [marketplace resmi](https://hermes-agent.nousresearch.com/marketplace/hermes-dreaming).

Unslop sudah menjadi instruksi bundel wajib untuk **Val, Kiki dan Coder**. Kiki menilai arah visual, Val menilai bukti/kejelasan dashboard, dan Coder mengimplementasikan perbaikan. Pemicu adalah pekerjaan UI yang relevan; bukan pengubahan otomatis gaya persona atau seluruh jawaban.

## Fitur yang belum dibundel

[Watermarks Remover](https://github.com/guillaumemeyer/watermarks-remover) belum menjadi bagian installer MSSHI ini. Proyek upstream mempunyai pilihan skill berbasis layanan HTTP dan pilihan teks mandiri. Kemungkinan integrasi khusus berikutnya dapat dibagi menurut tugas tulisan, media Kiki dan pemeliharaan Coder, tetapi dokumen ini tidak mengklaim komponen itu telah terpasang atau seluruh jenis watermark dapat ditangani.

## Seluruh 51 sumber eksternal

Seluruh 49 repositori Git dalam manifest dipatok pada commit. Model-card KAT mempunyai revisi tersendiri; model-card Unlimited-OCR-2 belum dipatok revisinya. Registry CLI-Anything merupakan situs, bukan repositori Git. Mengambil model-card hanya mengunduh keterangan, bukan bobot model.

| Sumber | Peran | Pemicu | Pemasangan baru | Prasyarat |
| --- | --- | --- | --- | --- |
| [higgsfield-skills](https://github.com/higgsfield-ai/skills) | Kiki | Konteks tugas/perintah eksplisit, setelah memeriksa prasyarat yang diminta. | Pembungkus higgsfield-skills disalin ke peran wajib. Source/runtime penuh tetap langkah terpisah. | Skill lokal yang ditinjau, akun dan akses Higgsfield, anggaran, aset yang boleh dikirim. |
| [remotion-skills](https://github.com/remotion-dev/skills) | Kiki | Konteks tugas/perintah eksplisit, setelah memeriksa prasyarat yang diminta. | Pembungkus motion-graphics-suite disalin ke peran wajib. Source/runtime penuh tetap langkah terpisah. | Skill yang relevan dan proyek Node/Remotion yang sudah dipilih. |
| [barty-motion-graphics](https://github.com/Barty-Bart/motion-graphics) | Kiki | Konteks tugas/perintah eksplisit, setelah memeriksa prasyarat yang diminta. | Pembungkus motion-graphics-suite disalin ke peran wajib. Source/runtime penuh tetap langkah terpisah. | Pilih skill dan aset yang dibutuhkan, cek runtime render dari resep. |
| [charlie-motion-graphics](https://github.com/charlie947/motion-graphics-skills) | Kiki | Konteks tugas/perintah eksplisit, setelah memeriksa prasyarat yang diminta. | Pembungkus motion-graphics-suite disalin ke peran wajib. Source/runtime penuh tetap langkah terpisah. | Tinjau resep skill dan siapkan runtime/render proyek yang dipilih. |
| [bang-motion](https://github.com/bangtutorial/bang-motion) | Kiki | Konteks tugas/perintah eksplisit, setelah memeriksa prasyarat yang diminta. | Pembungkus motion-graphics-suite disalin ke peran wajib. Source/runtime penuh tetap langkah terpisah. | Browser untuk HTML. Node, Puppeteer dan FFmpeg bila perlu MP4. |
| [humanizer-en](https://github.com/blader/humanizer) | Yukino, Shizuka, Val, Kiki, Coder | Konteks tugas/perintah eksplisit, setelah memeriksa prasyarat yang diminta. | Pembungkus humanizer-en disalin ke peran wajib. Source/runtime penuh tetap langkah terpisah. | Skill yang direview; salinan teks yang pengguna izinkan untuk disunting. |
| [humanizer-indonesia](https://github.com/adhiprib/humanizer-indonesia) | Yukino, Shizuka, Val, Kiki, Coder | Konteks tugas/perintah eksplisit, setelah memeriksa prasyarat yang diminta. | Pembungkus humanizer-indonesia disalin ke peran wajib. Source/runtime penuh tetap langkah terpisah. | Skill dan referensi suara milik sendiri. Cek opsi scripts/metrik.py pada revisi yang dipakai. |
| [anti-slop](https://github.com/miqdadbadjuber/anti-slop) | Yukino, Shizuka, Val, Kiki, Coder | Dipilih sesuai konteks setelah sumber/runtime yang kompatibel tersedia. | Referensi eksternal, bukan pemasangan runtime otomatis. --pull-upstreams hanya menyimpan source/cache. | Pilih aturan untuk target proyek, bukan seluruh aturan lintas domain. |
| [goose](https://github.com/aaif-goose/goose) | Coder | Konteks tugas/perintah eksplisit, setelah memeriksa prasyarat yang diminta. | Pembungkus antigravity-webdev-cybersec disalin ke peran wajib. Source/runtime penuh tetap langkah terpisah. | Goose adalah agen CLI terpisah, bukan ID model MoA. Endpoint/provider dan izin tool terisolasi diperlukan; tidak autostart. |
| [superpowers](https://github.com/obra/superpowers) | Coder | Dipilih sesuai konteks setelah sumber/runtime yang kompatibel tersedia. | Referensi eksternal, bukan pemasangan runtime otomatis. --pull-upstreams hanya menyimpan source/cache. | Pilih skill atau plugin yang kompatibel dengan host. Tinjau hook bootstrap sebelum mengaktifkan plugin. |
| [ponytail](https://github.com/dietrichgebert/ponytail) | Coder | Dipilih sesuai konteks setelah sumber/runtime yang kompatibel tersedia. | Referensi eksternal, bukan pemasangan runtime otomatis. --pull-upstreams hanya menyimpan source/cache. | Skill/instruksi yang cocok dengan host dan aturan repo. |
| [addy-agent-skills](https://github.com/addyosmani/agent-skills) | Coder | Dipilih sesuai konteks setelah sumber/runtime yang kompatibel tersedia. | Referensi eksternal, bukan pemasangan runtime otomatis. --pull-upstreams hanya menyimpan source/cache. | Salin skill yang diperlukan dengan referensinya; dependensi bervariasi per skill. |
| [graphify](https://github.com/Graphify-Labs/graphify) | Yukino, Shizuka, Val, Kiki, Coder | Dipilih sesuai konteks setelah sumber/runtime yang kompatibel tersedia. | Referensi eksternal, bukan pemasangan runtime otomatis. --pull-upstreams hanya menyimpan source/cache. | CLI dan parser lokal sesuai format. Periksa tahap mana yang memakai model/API. |
| [mindrally-skills](https://github.com/mindrally/skills) | Coder | Dipilih sesuai konteks setelah sumber/runtime yang kompatibel tersedia. | Referensi eksternal, bukan pemasangan runtime otomatis. --pull-upstreams hanya menyimpan source/cache. | Pilih satu playbook berdasarkan stack; cek runtime masing-masing. |
| [playwright-best-practices](https://github.com/currents-dev/playwright-best-practices-skill) | Coder | Dipilih sesuai konteks setelah sumber/runtime yang kompatibel tersedia. | Referensi eksternal, bukan pemasangan runtime otomatis. --pull-upstreams hanya menyimpan source/cache. | Proyek Playwright dan browser test. Gunakan lingkungan dan akun uji yang diizinkan. |
| [awesome-copilot](https://github.com/github/awesome-copilot) | Coder | Dipilih sesuai konteks setelah sumber/runtime yang kompatibel tersedia. | Referensi eksternal, bukan pemasangan runtime otomatis. --pull-upstreams hanya menyimpan source/cache. | Ambil entry yang relevan; terjemahkan fitur yang khusus Copilot bila host berbeda. |
| [superdesign-skill](https://github.com/superdesigndev/superdesign-skill) | Kiki, Coder, Antigravity | Dipilih sesuai konteks setelah sumber/runtime yang kompatibel tersedia. | Referensi eksternal, bukan pemasangan runtime otomatis. --pull-upstreams hanya menyimpan source/cache. | Skill yang dipilih, brief dan proyek UI. Fitur layanan perlu akun jika dipakai. |
| [better-design](https://github.com/marvkr/better-design) | Kiki, Coder, Antigravity | Dipilih sesuai konteks setelah sumber/runtime yang kompatibel tersedia. | Referensi eksternal, bukan pemasangan runtime otomatis. --pull-upstreams hanya menyimpan source/cache. | Server MCP atau registry yang ditinjau. Pin versi; cek dependency dan lisensi komponen yang diambil. |
| [design-taste](https://github.com/madebymustafa/design-taste) | Kiki, Coder, Antigravity | Dipilih sesuai konteks setelah sumber/runtime yang kompatibel tersedia. | Referensi eksternal, bukan pemasangan runtime otomatis. --pull-upstreams hanya menyimpan source/cache. | Gunakan satu profil genre atau pola yang relevan. |
| [paper-shaders](https://github.com/paper-design/shaders) | Kiki, Coder, Antigravity | Dipilih sesuai konteks setelah sumber/runtime yang kompatibel tersedia. | Referensi eksternal, bukan pemasangan runtime otomatis. --pull-upstreams hanya menyimpan source/cache. | Paket npm sesuai framework dan kemampuan GPU/WebGL. Uji fallback dan aksesibilitas. |
| [canvas-ui](https://github.com/DavidHDev/canvas-ui) | Kiki, Coder, Antigravity | Dipilih sesuai konteks setelah sumber/runtime yang kompatibel tersedia. | Referensi eksternal, bukan pemasangan runtime otomatis. --pull-upstreams hanya menyimpan source/cache. | Framework target dan browser WebGL. Baca batas Commons Clause sebelum distribusi. |
| [motion-primitives](https://github.com/ibelick/motion-primitives) | Kiki, Coder, Antigravity | Dipilih sesuai konteks setelah sumber/runtime yang kompatibel tersedia. | Referensi eksternal, bukan pemasangan runtime otomatis. --pull-upstreams hanya menyimpan source/cache. | Framework dan motion runtime yang diminta komponen. Tambahkan reduced-motion. |
| [cursify](https://github.com/ui-layouts/cursify) | Kiki, Coder, Antigravity | Dipilih sesuai konteks setelah sumber/runtime yang kompatibel tersedia. | Referensi eksternal, bukan pemasangan runtime otomatis. --pull-upstreams hanya menyimpan source/cache. | React/Next.js, tes pointer, sentuhan dan reduced-motion. |
| [strix](https://github.com/usestrix/strix) | Coder | Konteks tugas/perintah eksplisit, setelah memeriksa prasyarat yang diminta. | Pembungkus antigravity-webdev-cybersec disalin ke peran wajib. Source/runtime penuh tetap langkah terpisah. | Scope tertulis, target uji, runtime lokal sesuai docs, isolasi dan model milik pengguna bila perlu. |
| [cybersecurity-library](https://github.com/mukul975/anthropic-cybersecurity-skills) | Coder | Konteks tugas/perintah eksplisit, setelah memeriksa prasyarat yang diminta. | Pembungkus antigravity-webdev-cybersec disalin ke peran wajib. Source/runtime penuh tetap langkah terpisah. | Indeks lokal dan tools sesuai playbook; review scope sebelum eksekusi. |
| [reverse-engineer-anything](https://github.com/NabilRFG12/Reverse-Engineer-anything?tab=readme-ov-file) | Coder | Konteks tugas/perintah eksplisit, setelah memeriksa prasyarat yang diminta. | Pembungkus antigravity-webdev-cybersec disalin ke peran wajib. Source/runtime penuh tetap langkah terpisah. | Salinan artefak lokal, izin analisis, alat platform yang relevan. Periksa hubungan fork/revisi. |
| [rea](https://github.com/morluto/rea) | Coder | Analisis artefak berizin setelah pengguna memilih REA. | Instruksi opsional --with-rea; runtime Node/native tidak otomatis. | Artefak milik pengguna/diotorisasi; pilih alat sesuai platform dan batas pemeriksaan. |
| [unlimited-ocr-2](https://huggingface.co/baidu/Unlimited-OCR-2) | Yukino, Shizuka, Val, Kiki, Coder | Konteks tugas/perintah eksplisit, setelah memeriksa prasyarat yang diminta. | Pembungkus unlimited-ocr-2 disalin ke peran wajib. Source/runtime penuh tetap langkah terpisah. | Checkpoint yang dipin, runtime kompatibel, ruang disk/VRAM yang cukup dan review kode model. |
| [unlimited-ocr](https://github.com/baidu/Unlimited-OCR) | Yukino, Shizuka, Val, Kiki, Coder | Dipilih sesuai konteks setelah sumber/runtime yang kompatibel tersedia. | Referensi eksternal, bukan pemasangan runtime otomatis. --pull-upstreams hanya menyimpan source/cache. | Dependensi dan hardware sesuai upstream. Cocokkan versi repo, checkpoint dan format PDF/gambar. |
| [tokentracker](https://github.com/xiufengsun/TokenTracker) | Yukino, Shizuka, Val, Kiki, Coder | Dipilih sesuai konteks setelah sumber/runtime yang kompatibel tersedia. | Referensi eksternal, bukan pemasangan runtime otomatis. --pull-upstreams hanya menyimpan source/cache. | Aplikasi/sumber data yang tersedia. Rekonsiliasi dengan biaya provider dan saldo resmi bila ada. |
| [token-monitor](https://github.com/Javis603/token-monitor) | Yukino, Shizuka, Val, Kiki, Coder | Dipilih sesuai konteks setelah sumber/runtime yang kompatibel tersedia. | Referensi eksternal, bukan pemasangan runtime otomatis. --pull-upstreams hanya menyimpan source/cache. | Widget/ekspor atau API yang benar-benar tersedia; matikan sinkronisasi bila tidak dibutuhkan. |
| [hermes-jev-skills](https://github.com/kerpopule/hermes-jev-skills) | Yukino, Shizuka, Val, Kiki, Coder | Dipilih sesuai konteks setelah sumber/runtime yang kompatibel tersedia. | Referensi eksternal, bukan pemasangan runtime otomatis. --pull-upstreams hanya menyimpan source/cache. | Hermes kompatibel; konfirmasi nama opsi upstream. Routing model MSSHI dinonaktifkan. |
| [cli-anything](https://github.com/HKUDS/CLI-Anything) | Yukino, Shizuka, Val, Kiki, Coder | Konteks tugas/perintah eksplisit, setelah memeriksa prasyarat yang diminta. | Pembungkus cli-anything-universal-bridge disalin ke peran wajib. Source/runtime penuh tetap langkah terpisah. | Harness telah diaudit dan terpasang, aplikasi target, path yang dipilih pengguna. |
| [cli-anything-catalog](https://clianything.cc/) | Yukino, Shizuka, Val, Kiki, Coder | Konteks tugas/perintah eksplisit, setelah memeriksa prasyarat yang diminta. | Pembungkus cli-anything-universal-bridge disalin ke peran wajib. Source/runtime penuh tetap langkah terpisah. | Akses web untuk pencarian dokumentasi. Registry tidak membuktikan tool sudah terpasang. |
| [hermes-steel](https://github.com/steel-dev/hermes-steel) | Yukino, Shizuka, Val, Kiki, Coder | Tugas browsing setelah opt-in plugin, endpoint/key dan izin anggaran tersedia. | Plugin perlu --install-steel atau msshi browser --install; bukan koneksi akun otomatis. | Plugin Hermes, konfigurasi browser eksplisit dan STEEL_API_KEY dari secret store lokal. |
| [gpt-researcher](https://github.com/assafelovic/gpt-researcher) | Val | Dipilih sesuai konteks setelah sumber/runtime yang kompatibel tersedia. | Referensi eksternal, bukan pemasangan runtime otomatis. --pull-upstreams hanya menyimpan source/cache. | Runtime dan penyedia model/pencarian yang dipilih. Batasi durasi dan biaya. |
| [remote-jobs](https://github.com/remoteintech/remote-jobs) | Yukino, Shizuka, Val, Kiki, Coder | Konteks tugas/perintah eksplisit, setelah memeriksa prasyarat yang diminta. | Pembungkus remote-jobs disalin ke peran wajib. Source/runtime penuh tetap langkah terpisah. | Akses direktori dan laman karier. Cek lokasi, zona waktu dan hak kerja per posisi. |
| [caveman](https://github.com/JuliusBrussee/caveman) | Yukino, Shizuka, Val, Kiki, Coder | Muat skill relevan setelah paket terkurasi dipasang. | msshi integrations install memasang pilihan terkurasi; msshi update menindaklanjuti sumber bila tidak --skip-upstreams. Bukan semua source otomatis diaktifkan pada setup awal. | Reviewed local runtime and active task when executing tools. |
| [hyperframes](https://github.com/heygen-com/hyperframes) | Kiki, Coder | Muat skill relevan setelah paket terkurasi dipasang. | msshi integrations install memasang pilihan terkurasi; msshi update menindaklanjuti sumber bila tidak --skip-upstreams. Bukan semua source otomatis diaktifkan pada setup awal. | Reviewed local runtime and active task when executing tools. |
| [ui-ux-pro-max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | Kiki, Coder | Muat skill relevan setelah paket terkurasi dipasang. | msshi integrations install memasang pilihan terkurasi; msshi update menindaklanjuti sumber bila tidak --skip-upstreams. Bukan semua source otomatis diaktifkan pada setup awal. | Reviewed local runtime and active task when executing tools. |
| [anthropic-skills](https://github.com/anthropics/skills) | Yukino, Shizuka, Val, Kiki, Coder | Muat skill relevan setelah paket terkurasi dipasang. | msshi integrations install memasang pilihan terkurasi; msshi update menindaklanjuti sumber bila tidak --skip-upstreams. Bukan semua source otomatis diaktifkan pada setup awal. | Reviewed local runtime and active task when executing tools. |
| [hermes-omnivoice](https://github.com/ThaungThanHan/hermes-omnivoice) | Yukino, Shizuka, Val, Kiki, Coder | Audio diminta; aktivasi hanya setelah sintesis lokal terverifikasi. | Source/aturan suara dapat disiapkan terpisah; runtime+bobot tidak diunduh otomatis. | Reviewed local runtime and active task when executing tools. |
| [hermes-dreaming](https://github.com/itpartypattaya/hermes-dreaming) | Yukino, Shizuka, Val, Kiki, Coder | Pilihan plugin 3 menjalankan satu laporan lokal; jadwal hanya lewat msshi dream --register. | Tidak aktif atau terjadwal otomatis pada setup default. Bukan pemasangan penuh plugin resmi. | Reviewed local runtime and active task when executing tools. |
| [kat-coder-v2-5-dev](https://huggingface.co/Kwaipilot/KAT-Coder-V2.5-Dev) | Coder | Hanya pilihan KAT eksplisit pada Coder, dengan endpoint/key yang valid. | Default OFF pada seluruh preset; tanpa bobot/endpoint otomatis. | Model text-only 35B total/3B aktif. Pada RAM16GB/RTX3050 utamakan endpoint remote yang benar; jangan menjanjikan Q4 muat atau mengubah model utama. |
| [timesfm](https://github.com/google-research/timesfm) | Val | Konteks tugas/perintah eksplisit, setelah memeriksa prasyarat yang diminta. | Pembungkus timesfm-forecasting disalin ke peran wajib. Source/runtime penuh tetap langkah terpisah. | Explicit isolated Python CPU runtime installation and TimesFM2.5 pinned model download. |
| [unslop](https://github.com/heydamir/unslop) | Kiki, Val, Coder | Konteks audit/perbaikan UI; bukan penyuntingan semua jawaban. | Adaptasi instruksi sudah bundel untuk Val, Kiki dan Coder; tidak perlu runtime Unslop tersendiri. | Sumber UI atau URL yang diakses dengan izin; tidak memasang browser/snapshot scripts upstream. |
| [brag](https://github.com/latent-spaces/brag) | Kiki | Konteks tugas/perintah eksplisit, setelah memeriksa prasyarat yang diminta. | Pembungkus brag disalin ke peran wajib. Source/runtime penuh tetap langkah terpisah. | Node22+, runtime Hyperframes terpisah, FFmpeg, aset berizin; tidak mengganti model Kiki. |
| [scrapling](https://github.com/D4Vinci/Scrapling) | Val, Coder | Konteks tugas/perintah eksplisit, setelah memeriksa prasyarat yang diminta. | Pembungkus scrapling disalin ke peran wajib. Source/runtime penuh tetap langkah terpisah. | Setup parser terisolasi; wrapper tidak mengaktifkan browser, stealth, CAPTCHA, atau akses akun. |
| [harness2](https://github.com/google-research/harness2) | Yukino, Shizuka, Val, Kiki, Coder | Konteks tugas/perintah eksplisit, setelah memeriksa prasyarat yang diminta. | Pembungkus harness2 disalin ke peran wajib. Source/runtime penuh tetap langkah terpisah. | Python3.12 runtime terpisah; benchmark model berbayar dan promosi harness aktual tidak dijalankan wrapper. |
| [career-ops](https://github.com/career-ops-hq/career-ops) | Yukino, Shizuka, Val, Kiki, Coder | Konteks tugas/perintah eksplisit, setelah memeriksa prasyarat yang diminta. | Pembungkus career-ops disalin ke peran wajib. Source/runtime penuh tetap langkah terpisah. | Source workflow lengkap dengan AGENTS.md dan modes/, Node sesuai upstream; CV/data pengguna privat. Browser dan panggilan model terpisah. |
| [mattpocock-skills](https://github.com/mattpocock/skills) | Yukino, Shizuka, Val, Kiki, Coder | Konteks tugas/perintah eksplisit, setelah memeriksa prasyarat yang diminta. | Pembungkus mattpocock-engineering disalin ke peran wajib. Source/runtime penuh tetap langkah terpisah. | Source cache terpisah; hormati disable-model-invocation dan workspace/issue tracker yang dipilih. |
| [rea-video](https://github.com/JuneYaooo/rea-video) | Kiki | Konteks tugas/perintah eksplisit, setelah memeriksa prasyarat yang diminta. | Pembungkus rea-video disalin ke peran wajib. Source/runtime penuh tetap langkah terpisah. | Python 3.10+ dan FFmpeg/ffprobe; runtime, OCR/ASR/stems/VLM/model download dan generasi ulang merupakan opt-in terpisah. |

## Seluruh 67 skill bundel

Kolom peran menunjukkan pembagian wajib preset lima bot. Pada mode solo, custom atau paket selektif, pengguna memilih susunan yang berbeda. Tool, dependency dan akun mengikuti prasyarat masing-masing.

| Skill | Peran wajib | Fungsi | Pemicu |
| --- | --- | --- | --- |
| academic-plotting | Kiki | Menghasilkan figur publikasi dari data dan spesifikasi yang disepakati. | Konteks tugas atau pemanggilan langsung. |
| ai-research-explore | Coder | Merancang eksperimen kandidat yang terpisah dari baseline. | Konteks tugas atau pemanggilan langsung. |
| ai-research-reproduction | Coder | Menetapkan target reproduksi penelitian yang dapat dibuktikan. | Konteks tugas atau pemanggilan langsung. |
| analyze-project | Coder | Memetakan struktur proyek, konfigurasi, titik masuk, dan risiko perubahan. | Konteks tugas atau pemanggilan langsung. |
| antigravity-webdev-cybersec | Coder | Hubungkan pengerjaan web dan evaluasi keamanan terotorisasi dengan Antigravity, Goose, dan alat lokal. | Konteks tugas atau pemanggilan langsung. |
| auto-curiousity-for-film-making | Kiki | Menguji kemampuan alat kreatif dan teknik produksi dalam eksperimen terpisah. | Konteks tugas atau pemanggilan langsung. |
| autoresearch | Shizuka | Mengoordinasikan siklus eksperimen dan sintesis dengan batas berhenti. | Konteks tugas atau pemanggilan langsung. |
| backward-traceability | Yukino, Shizuka, Val | Menautkan angka dan hasil laporan kembali ke data, skrip, atau perhitungan. | Konteks tugas atau pemanggilan langsung. |
| brainstorming-research-ideas | Yukino | Memakai kerangka ideasi terstruktur untuk menemukan pertanyaan layak. | Konteks tugas atau pemanggilan langsung. |
| business-sage | Yukino, Shizuka, Val, Kiki | Menyusun analisis usaha, skenario finansial, dan pertanyaan verifikasi aturan yang relevan. | Konteks tugas atau pemanggilan langsung. |
| chatgpt-hermes-portability-kit | Yukino, Shizuka, Val | Memandu adaptasi metode dan profil ke platform lain menggunakan sumber yang sah. | Konteks tugas atau pemanggilan langsung. |
| cli-anything-business-sage | Yukino, Shizuka, Val, Kiki | Menjalankan perhitungan bisnis terstruktur melalui harness lokal yang tersedia. | Konteks tugas atau pemanggilan langsung. |
| cli-anything-universal-bridge | Yukino, Shizuka, Val, Kiki, Coder | Daftarkan, periksa, dan jalankan rute aplikasi, browser, harness CLI-Anything, atau MCP Hermes saat tugas membutuhkannya. | Konteks tugas atau pemanggilan langsung. |
| creative-thinking-for-research | Yukino | Mencoba reframing, analogi, dan kombinasi konsep untuk membuka pilihan. | Konteks tugas atau pemanggilan langsung. |
| data-analysis | Val | Memeriksa kualitas data, asumsi, uji statistik, dan ketidakpastian. | Konteks tugas atau pemanggilan langsung. |
| deep-research | Yukino, Shizuka, Val | Menyusun pertanyaan, menelusuri literatur, dan mensintesis bukti yang dapat diperiksa. | Konteks tugas atau pemanggilan langsung. |
| evaluating-code-models | Coder | Menguji keluaran model kode dengan tugas dan tolok ukur yang relevan. | Konteks tugas atau pemanggilan langsung. |
| evaluating-llms-harness | Coder | Mengatur dan menilai evaluasi LLM dengan harness pengujian yang kompatibel. | Konteks tugas atau pemanggilan langsung. |
| explore-code | Coder | Mengembangkan perubahan eksperimen dalam ruang kerja terisolasi. | Konteks tugas atau pemanggilan langsung. |
| explore-run | Coder | Menjalankan uji terbatas dengan anggaran dan catatan hasil yang jelas. | Konteks tugas atau pemanggilan langsung. |
| filmmaking-videography-photography-s2 | Kiki | Menyatukan konsep, pengarahan, kamera, foto, penyuntingan, warna, dan suara. | Konteks tugas atau pemanggilan langsung. |
| firecrawl-competitive-intel | Val | Membandingkan perubahan produk, harga, dan fitur dengan bukti bertanggal. | Konteks tugas atau pemanggilan langsung. |
| firecrawl-dashboard-reporting | Val | Mengambil dan memeriksa indikator dasbor untuk pelaporan. | Konteks tugas atau pemanggilan langsung. |
| firecrawl-deep-research | Val | Mengumpulkan bukti web untuk sintesis dengan atribusi. | Konteks tugas atau pemanggilan langsung. |
| firecrawl-knowledge-base | Val | Menyiapkan koleksi dokumen, potongan, serta metadata asalnya. | Konteks tugas atau pemanggilan langsung. |
| firecrawl-research-papers | Val | Menemukan dan memeriksa makalah pada sumber akademik yang relevan. | Konteks tugas atau pemanggilan langsung. |
| focus-my-energy | Yukino | Menyesuaikan beban tugas dan langkah awal dengan energi yang dilaporkan pengguna. | Konteks tugas atau pemanggilan langsung. |
| generate-fresh-ideas | Yukino | Menghasilkan alternatif dari beberapa lensa kreatif untuk disaring pengguna. | Konteks tugas atau pemanggilan langsung. |
| get-more-perspectives | Shizuka | Menguji keputusan dari beberapa sudut pandang sebelum memilih. | Konteks tugas atau pemanggilan langsung. |
| github-research | Val | Menelaah lisensi, rancangan, pemeliharaan, dan kesiapan repositori. | Konteks tugas atau pemanggilan langsung. |
| higgsfield-skills | Kiki | Rutekan kebutuhan produksi kreatif ke modul Higgsfield yang sesuai setelah konsep disetujui. | Konteks tugas atau pemanggilan langsung. |
| humanizer-en | Yukino, Shizuka, Val, Kiki, Coder | Sunting prosa bahasa Inggris agar terasa alami sambil menjaga makna, suara penulis, dan sitasi. | Konteks tugas atau pemanggilan langsung. |
| humanizer-indonesia | Yukino, Shizuka, Val, Kiki, Coder | Sunting prosa bahasa Indonesia sesuai ragam pembaca sambil menjaga makna, istilah, dan sitasi. | Konteks tugas atau pemanggilan langsung. |
| idea-generation | Yukino | Mengembangkan dan menyaring gagasan penelitian dalam beberapa putaran. | Konteks tugas atau pemanggilan langsung. |
| langsmith-observability | Coder | Memandu observabilitas dan evaluasi LangSmith pada lingkungan yang disetujui. | Konteks tugas atau pemanggilan langsung. |
| literature-review | Yukino, Shizuka, Val | Membangun tinjauan pustaka dengan beberapa perspektif dan jejak sumber. | Konteks tugas atau pemanggilan langsung. |
| match-my-writing-style | Yukino, Shizuka, Val, Kiki, Coder | Menerapkan Voice Card yang disediakan pengguna sesuai audiens dan jenis tulisan. | Konteks tugas atau pemanggilan langsung. |
| math-reasoning | Val | Memeriksa langkah penalaran matematika dan syarat berlakunya. | Konteks tugas atau pemanggilan langsung. |
| motion-graphics-suite | Kiki | Pilih dan hubungkan empat rujukan motion graphics untuk komposisi yang tetap dapat diedit. | Konteks tugas atau pemanggilan langsung. |
| muza-skripsi-template | Yukino, Shizuka, Val | Menyusun template Word (.docx) skripsi/tugas akhir sesuai pedoman kampus, lookup logo & pejabat resmi, ekstrak aturan PDF, serta injeksi hasil MuZA_Search v1.1. | Konteks tugas atau pemanggilan langsung. |
| nemo-evaluator-sdk | Coder | Memandu evaluasi dengan NeMo Evaluator SDK jika dependensinya tersedia. | Konteks tugas atau pemanggilan langsung. |
| notebooklm-thinking-datascience | Yukino, Shizuka, Val | Mengadaptasi metode berpikir sistem dan data science dari indeks sumber milik pengguna. | Konteks tugas atau pemanggilan langsung. |
| novelty-assessment | Yukino, Shizuka, Val | Menguji klaim kebaruan terhadap studi terdekat dan batas pencarian. | Konteks tugas atau pemanggilan langsung. |
| paper-context-resolver | Val | Mengikat klaim reproduksi pada bagian, gambar, tabel, atau lampiran makalah. | Konteks tugas atau pemanggilan langsung. |
| paper-revision | Yukino, Shizuka, Val | Memetakan catatan revisi ke perubahan konkret dan bukti perbaikan. | Konteks tugas atau pemanggilan langsung. |
| paper-writing-section | Yukino, Shizuka, Val | Menyusun dan menyunting bagian naskah akademik dengan dua tahap pemeriksaan. | Konteks tugas atau pemanggilan langsung. |
| parenting-6d-gad-mdd | Yukino, Shizuka, Val, Kiki, Coder | Memandu percakapan dengan empati, struktur, dan dukungan otonomi. | Konteks tugas atau pemanggilan langsung. |
| persona-shizuka-yukino-shikaku | Yukino, Shizuka, Val, Kiki, Coder | Menjaga karakter, kontrak serah terima, dan batas kepemilikan tugas lima bot. | Konteks tugas atau pemanggilan langsung. |
| phoenix-observability | Coder | Memandu tracing dan evaluasi Phoenix tanpa memindahkan data di luar lingkup. | Konteks tugas atau pemanggilan langsung. |
| prep-for-meetings | Yukino | Menyusun ringkasan pertemuan dari catatan dan tujuan yang tersedia. | Konteks tugas atau pemanggilan langsung. |
| prep-for-meetings-2 | Yukino | Memadatkan bahan pertemuan menjadi pokok bahasan dan kartu pengingat. | Konteks tugas atau pemanggilan langsung. |
| rebuttal-writing | Yukino, Shizuka, Val | Menyusun jawaban poin demi poin untuk masukan pembimbing atau reviewer. | Konteks tugas atau pemanggilan langsung. |
| research-paper-writing | Yukino, Shizuka, Val | Memeriksa struktur argumen dan hubungan antara klaim, bukti, serta pembahasan. | Konteks tugas atau pemanggilan langsung. |
| slide-generation | Kiki | Menyusun presentasi dari argumen, hasil, dan visual yang dapat diverifikasi. | Konteks tugas atau pemanggilan langsung. |
| symbolic-equation | Val | Mencari kandidat persamaan yang dapat ditafsirkan dan diuji. | Konteks tugas atau pemanggilan langsung. |
| table-generation | Val | Membangun tabel akademik dari hasil terverifikasi beserta satuan dan catatan. | Konteks tugas atau pemanggilan langsung. |
| unlimited-ocr-2 | Yukino, Shizuka, Val, Kiki, Coder | Rutekan ekstraksi dokumen dan gambar berhalaman ke OCR yang tersedia dengan penunjuk bukti. | Konteks tugas atau pemanggilan langsung. |
| wise-judgment-and-sovereign-orchestrator | Shizuka | Mengatur pilihan alur, anggaran, persetujuan, delegasi, dan sintesis hasil Val. | Konteks tugas atau pemanggilan langsung. |
| timesfm-forecasting | Val | Prediksi deret waktu numerik lokal dengan TimesFM 2.5, validasi data dan evaluasi terpisah. | Konteks tugas atau pemanggilan langsung. |
| unslop | Val, Kiki, Coder | Audit dan perbaikan UI bertahap; Kiki arah visual, Val bukti dashboard, Coder implementasi. | Konteks tugas atau pemanggilan langsung. |
| brag | Kiki | Video peluncuran produk berbasis Hyperframes dengan Concepting First dan review manusia. | Konteks tugas atau pemanggilan langsung. |
| scrapling | Val, Coder | Ekstraksi CSS/XPath dari HTML lokal dalam runtime parser terisolasi. | Konteks tugas atau pemanggilan langsung. |
| harness2 | Yukino, Shizuka, Val, Kiki, Coder | Evaluasi harness Propose-Probe-Compose menggunakan demo deterministik dan proposal yang ditinjau manusia. | Konteks tugas atau pemanggilan langsung. |
| career-ops | Yukino, Shizuka, Val, Kiki, Coder | Bantu karier, CV-lowongan skor 1-5, tracker dan wawancara sesuai konteks. | Konteks tugas atau pemanggilan langsung. |
| remote-jobs | Yukino, Shizuka, Val, Kiki, Coder | Saring direktori perusahaan remote, lalu periksa lowongan aktif ketika diminta. | Konteks tugas atau pemanggilan langsung. |
| mattpocock-engineering | Yukino, Shizuka, Val, Kiki, Coder | Disiplin engineering, TDD, debugging dan spesifikasi; orkestrator/publikasi eksplisit. | Konteks tugas atau pemanggilan langsung. |
| rea-video | Kiki | Kiki membedah video referensi per shot ke VIDEO.md; model dan generasi merupakan opt-in terpisah. | Konteks tugas atau pemanggilan langsung. |

## Apa yang diperiksa

Audit membaca matriks peran/skill, manifest sumber, audit lisensi, pilihan terminal, kebijakan aktivasi dan kode pemasang. Daftar peran Harness2 dan Graphify diselaraskan; jalur model-card mengikuti revisi bila ada; integrasi terkurasi mengenali Yukino pada profil default maupun profil bernama. Uji struktur tidak menjalankan benchmark atau percakapan model.

Dokumen ini membedakan pemasangan instruksi, tersedianya rute, tersedianya runtime, izin akun dan keberhasilan hasil tugas. Kemampuan model memilih atau memakai skill pada percakapan nyata tetap bergantung host dan tugas; keberadaan file saja tidak membuktikan kualitas hasil atau penghematan tagihan.

Rujukan lokal: [matriks peran dan skill](../configs/bot_role_and_skill_matrix.json), [51 sumber](../configs/upstreams.json), [kebijakan pemicu](../configs/manifests/skill_activation_matrix.json), [penjelasan pilihan terminal](../configs/option_help.json), [catatan perbaikan](V3_1_2_REPAIR.md).
