# BRAG untuk Kiki-Chii

BRAG mengubah proyek/aplikasi menjadi film peluncuran pendek: sudut cerita, storyboard, komposisi HTML yang dapat diedit, rendering lokal, poster, dan teks berbagi. Integrasi MSSHI ini hanya diaktifkan untuk **Kiki-Chii**. Model, provider, fallback, MoA (termasuk rujukan pertama `claude-fable-5.2`), persona/SOUL/DNA, memori, kredensial, dan konfigurasi browser tetap mengikuti konfigurasi pengguna.

Ini bukan model video generatif. Skill mengarahkan agen yang sudah dipilih pengguna dan menggunakan Hyperframes untuk merender HTML. `brag-slim` upstream mempunyai dispatch untuk model tertentu; integrasi ini tidak memasangnya atau mengubah model agar menyesuaikan dispatch tersebut.

## Alur kreatif

**Concepting First** wajib mendahului produksi. Kiki meninjau sumber yang diizinkan, menyajikan tiga konsep, lalu menunggu pilihan manusia. Berikutnya pengguna meninjau script/storyboard, rough composition, polished preview beserta audio/hak pakai, kemudian hasil ekspor. Catat artefak/versi dan keputusan di `REVIEW.md` pada setiap tahap. Upstream mempunyai jalan pintas yang melewati sebagian review; wrapper MSSHI menggantinya dengan gerbang manusia. Pengujian otomatis dan izin instalasi tidak menjadi persetujuan kreatif.

Durasi awal 15–25 detik, 30 fps, landscape 1920×1080 kecuali diminta lain. Tampilkan produk sebenarnya dan klaim yang mempunyai bukti; samarkan data pribadi. Narasi mati secara default. Upstream menawarkan Kokoro, tetapi integrasi ini tidak mengunduh model suara dan tidak mengubah alur suara pengguna. Musik/SFX harus berasal dari pengguna atau sumber dengan hak dan atribusi yang sudah diperiksa. Publikasi, pengiriman pesan, cloud render, dan generasi berbayar memerlukan instruksi terpisah.

## Pemakaian tanpa Codex

Di Hermes, aktifkan profil Kiki-Chii dan minta `/brag` untuk proyek yang ditunjuk. Skill berada di `<HermesRoot>/profiles/kiki-chii/skills/brag/SKILL.md`. Command helper juga dapat dijalankan langsung dari PowerShell; `<repo>` adalah checkout MSSHI:

```powershell
python "<repo>\skills\brag\scripts\msshi_brag.py" doctor
python "<repo>\skills\brag\scripts\msshi_brag.py" init --project "D:\Projects\MyApp" --output "D:\Projects\MyApp\brag-output-new" --title "My App"
```

CLI MSSHI menyediakan rute yang sama:

```powershell
msshi brag doctor
msshi brag init --project "D:\Projects\MyApp" --output "D:\Projects\MyApp\brag-output-new" --title "My App"
```

`init` hanya membuat `CONCEPT.md`, `REVIEW.md`, dan `request.json` baru. Ia tidak membaca isi proyek, menimpa hasil lama, memanggil LLM, membuat media, atau menganggap persetujuan sudah diberikan. `doctor` lokal melaporkan versi, paket renderer, bukti pengujian, dan anggaran sumber daya; tidak membuka browser.

Setelah konsep, storyboard, rough, dan polished preview yang tepat telah disetujui manusia, periksa komposisi dan ekspor:

```powershell
msshi brag check --project "D:\Projects\MyApp\brag-output-new\composition"
msshi brag render --project "D:\Projects\MyApp\brag-output-new\composition" --output "D:\Projects\MyApp\brag-output-new\brag.mp4" --quality delivery --human-approved-preview
```

Pengganti bila shim `msshi` belum ada: `python "<repo>\skills\brag\scripts\msshi_brag.py"` diikuti argumen yang sama. `render` memerlukan file output baru, menjalankan check sebelum ekspor, hanya memakai render lokal, satu worker, low-memory mode, dan software capture. `--human-approved-preview` adalah pernyataan bahwa pengguna sudah menyetujui preview tersebut, bukan cara melewati review. Tidak ada command penerbitan/akun/cloud yang diteruskan helper.

`check` dan `render` menolak mulai bila RAM tersedia kurang dari 512 MiB, commit tersedia kurang dari 1 GiB, disk runtime kurang dari 1 GiB, atau anggarannya tidak dapat diverifikasi. Batas ini adalah minimum pengaman; film produksi dapat membutuhkan jauh lebih banyak. Pengguna dapat menutup aplikasi yang tidak diperlukan lalu menjalankan `doctor` lagi. Helper tidak menutup aplikasi pengguna atau menghapus cache. `renderer doctor` menjalankan pemeriksaan upstream lengkap dan mempertahankan arti `ok:false`, walaupun CLI upstream keluar dengan kode 0.

## Runtime terpisah dan setup eksplisit

Kebutuhan: Python 3.10+, Node.js 22+, FFmpeg/FFprobe, Chromium lokal, skill Hyperframes yang sesuai, sumber proyek yang diizinkan, dan aset berlisensi. Tidak ada server model, bobot model, akun HeyGen, Docker, MCP desktop, atau proses startup otomatis yang dibutuhkan untuk rendering HTML lokal. Fitur opsional seperti TTS, transcription, music generation, registry downloads, dan cloud tidak diuji/dipasang di sini.

Runtime privat berada di `<HermesRoot>/msshi-private/brag-runtime`; paket skill hanya berisi instruksi, helper standard library, dan provenance ringan. Cache upstream berada di `<HermesRoot>/msshi-private/v3.1-sources/brag`, di luar pemindai skill. Tidak ada musik/SFX upstream yang disalin ke skill aktif atau distribusi MSSHI.

Untuk setup baru yang eksplisit, jalankan perintah berikut setelah menetapkan root Hermes yang benar:

```powershell
$taskHermesRoot = 'D:\HermesData'
$taskRuntime = Join-Path $taskHermesRoot 'msshi-private\brag-runtime'
New-Item -ItemType Directory -Path $taskRuntime -Force | Out-Null
npm install --prefix $taskRuntime --ignore-scripts --no-audit --no-fund --save-exact hyperframes@0.9.38
python "<repo>\skills\brag\scripts\msshi_brag.py" doctor --hermes-root $taskHermesRoot
```

Pertahankan `package-lock.json` hasil setup untuk mengunci dependensi transitif. Paket utama dipin ke `0.9.38`; lifecycle scripts dimatikan. Helper tidak memakai `npx` dan tidak mengunduh browser secara otomatis. Pada layout lain gunakan `--hermes-root`/`--runtime`; jika Chromium tidak ditemukan otomatis, set `HYPERFRAMES_BROWSER_PATH` ke executable Chromium lokal yang dipercaya. Path executable bukan profil browser. Helper merender dengan profil bersih sementara dan process home/config/cache/temp privat, serta menonaktifkan telemetry dan update check. `CI=1` pada proses anak menonaktifkan daemon warm-check upstream yang biasanya bertahan lima menit setelah command non-TTY. Ia tidak menyalin cookies atau kredensial dari home/profil browser pengguna.

Rendering lokal tidak otomatis berarti bebas jaringan. Hyperframes dapat mengambil font publik saat keluarga font belum dilokalkan; untuk kerja offline, siapkan `@font-face` dan seluruh media/dependensi secara lokal dengan lisensi yang sesuai. Sumber HTML tetap harus diperiksa sebelum dijalankan. Jangan memakai proyek yang mengambil layanan privat/berbayar pada waktu render tanpa otorisasi terpisah.

## Provenance dan batas bukti

Upstream utama: [latent-spaces/brag pada commit 669ab9286aa28b6c3ee30e75f181ee74319d012a](https://github.com/latent-spaces/brag/tree/669ab9286aa28b6c3ee30e75f181ee74319d012a). Kode/instruksi upstream berlisensi MIT, copyright 2026 Shunit Haviv Hakimi. Integrasi ini menggunakan instruksi/helper MSSHI asli; tidak menyalin aset upstream. README musik upstream secara terpisah menyatakan CC BY 4.0 untuk musik Sascha Ende, bukan MIT. SFX dikreditkan ke Kenney, tetapi lisensi tiap aset belum dipastikan oleh integrasi ini, sehingga tidak dibundel/didistribusikan.

Renderer: paket npm `hyperframes@0.9.38`, metadata lisensi Apache-2.0, source gitHead `1ec03c4e190fb7262c8ad65884dfd576a81f1ebd`; [sumber Hyperframes](https://github.com/heygen-com/hyperframes). Integritas npm: `sha512-3KC2Nrl5IduLXVdEJhaS5BP5rAX48nIjioaNxRkNGyVsTIffs5pl/0hJFFksI71DreR+2i0DrIWhfluzQMrWcA==`. Dependensi, media, font, dan GSAP vendored mempunyai ketentuan sendiri; metadata Apache-2.0 paket utama bukan izin untuk mendistribusikan semua aset/model di dalam ekosistem tersebut. Tidak ada bobot model yang dipasang. Provenance yang dapat dibaca mesin ada pada `skills/brag/references/provenance.json`.

Pada verifikasi pemasangan v3.1, paket renderer, Node, FFmpeg, Chromium terdeteksi dan komposisi diagnostik asli 320×180 berdurasi satu detik menghasilkan laporan Hyperframes check: lint/runtime/layout lulus, contrast 5/5; ada satu peringatan waktu baca karena fixture sengaja hanya satu detik dan tanpa audio. Pengujian awal sempat dihentikan saat sumber daya rendah. Setelah anggaran kembali cukup, satu ekspor lokal dengan satu worker berhasil: **H.264, 320×180, 30 fps, 30 frame, 1,000 detik, 5.874 byte**. Dua frame hasil decode diperiksa dan menunjukkan animasi bar yang benar. Check/render mengambil font Inter publik secara otomatis, sehingga diagnostik ini tidak diklaim sepenuhnya offline. Hyperframes sempat melaporkan penutupan browser lambat dan memaksa penutupan browser render miliknya; ekspor tetap lulus dan bukti artefak disimpan privat. Ini membuktikan jalur ekspor kecil, belum membuktikan film produksi atau fitur suara/akun/cloud. Tidak ada LLM credits, API berbayar, atau konten proyek pribadi yang dipakai dalam diagnostik.
