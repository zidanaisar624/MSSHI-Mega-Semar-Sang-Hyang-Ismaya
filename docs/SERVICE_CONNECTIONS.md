# GitLab dan Tinyfish pada lima profil Hermes

MSSHI mempertahankan MCP untuk layanan web GitLab dan Tinyfish. Aplikasi desktop tetap memakai CLI berbasis tiket; pemasangan layanan ini tidak mengembalikan Blender, LightCraft, ArtCraft, Llmtrim, atau Hersona menjadi MCP.

## Perintah yang tersedia

```powershell
msshi services status --hermes-home "D:\HermesData"
msshi services install --hermes-home "D:\HermesData"
```

`status` hanya membaca konfigurasi dan keberadaan cache. Status terdaftar bukan bukti bahwa autentikasi atau operasi berhasil. `install` menambahkan entri layanan yang belum ada pada default, Shizuka, Val, Kiki-Chii, dan Shikaku. Entri yang konflik atau sengaja dinonaktifkan tidak ditimpa. Seluruh byte konfigurasi lama dipertahankan; entri MCP baru disisipkan, bukan menulis ulang pengaturan provider/model atau persona.

Endpoint resmi yang digunakan:

| Layanan | Endpoint | Alat yang diizinkan konfigurasi |
|---|---|---|
| GitLab | `https://gitlab.com/api/v4/mcp` | Filter milik pengguna tetap dipertahankan; tidak menjalankan perubahan proyek saat audit |
| Tinyfish | `https://agent.tinyfish.ai/mcp` | Hanya `search` dan `fetch_content`; resources/prompts dimatikan |

Menurut [dokumentasi resmi Tinyfish](https://github.com/tinyfish-io/tinyfish-mcp-server), Search dan Fetch gratis; otomasi browser, sesi browser, dan monitor mempunyai ketentuan biaya tersendiri. MSSHI tidak menjanjikan semua layanan Tinyfish gratis. Alat berbayar tersebut tidak didaftarkan melalui entri MCP Tinyfish ini. Plugin Tinyfish lain yang sudah dimiliki pengguna tetap memiliki pengaturan terpisah; periksa kebijakan kreditnya sebelum memakainya.

## Autentikasi dan cache bersama pada Windows

Hermes menyimpan OAuth secara native dalam `HERMES_HOME/mcp-tokens`. Tidak ditemukan opsi native untuk berbagi cache OAuth antarlima profil. Setup pribadi MuZA memakai junction direktori Windows yang **secara eksplisit berbagi identitas akun lokal yang sama**, bukan fitur pewarisan kredensial Hermes.

```powershell
msshi services install --hermes-home "D:\HermesData" --share-oauth
```

Pilihan ini bersifat opt-in. Helper memverifikasi akun GitLab melalui operasi baca `/oauth/token/info`, menolak konflik akun dan cache layanan lain, mencadangkan cache asli, lalu mengarahkan direktori `mcp-tokens` profil ke direktori default yang sama. Token tidak disalin ke source atau `config.yaml`. ACL direktori dibatasi untuk pengguna Windows yang menjalankan pemasangan dan SYSTEM. Native Hermes tetap mengelola refresh dan atomic replace; semua profil mengakses file serta refresh fence yang sama melalui junction.

Jangan gunakan pilihan ini untuk bot yang membutuhkan akun GitLab/Tinyfish terpisah. Gunakan login per profil sebagai gantinya. Cache Tinyfish independen yang berbeda ditolak, bukan digabungkan diam-diam. Cache dengan token kedaluwarsa perlu disegarkan melalui Hermes sebelum pemeriksaan identitas dapat berjalan.

Jika kredensial belum tersedia, login dilakukan sendiri oleh pengguna pada profil yang tepat:

```powershell
hermes mcp login gitlab
hermes mcp login tinyfish
```

Jangan menempel API key/token ke chat atau GitHub. [GitLab MCP](https://docs.gitlab.com/user/model_context_protocol/mcp_server/) memerlukan izin MCP yang sesuai; token PAT lama berscope `api` saja bukan pengganti OAuth MCP.

## Penemuan alat dan pengujian tanpa chat LLM

Probe otomatis memilih Python lingkungan Hermes dari manifest instalasi lokal dan source `hermes-agent`, sehingga dapat dipanggil melalui CLI global:

```powershell
msshi services probe --hermes-home "D:\HermesData" --service gitlab --read-test
msshi services probe --hermes-home "D:\HermesData" --service tinyfish
```

Probe menonaktifkan alur OAuth interaktif: jika login diperlukan, ia berhenti tanpa membuka browser. GitLab `--read-test` hanya membaca metadata token. Probe Tinyfish hanya initialize/tools-list; tidak memulai otomasi berbayar. Jumlah alat yang diumumkan server dapat berubah dan berbeda dari alat yang lolos filter konfigurasi.

Audit pribadi membedakan empat hasil: **terdaftar**, **discovery berhasil**, **autentikasi berhasil**, dan **operasi baca berhasil**. Pada verifikasi 12 November 2026, GitLab berhasil discovery/autentikasi di kelima profil. Metadata token GitLab juga berhasil dibaca pada default, Val, dan Kiki-Chii; identitas ketiga akun lama terbukti sama sebelum berbagi cache. Tinyfish sempat berhasil discovery/autentikasi pada default, tetapi token tersebut kedaluwarsa saat audit berlanjut dan refresh native meminta login ulang. Discovery Tinyfish pada profil lain belum berhasil; semua profil sudah terdaftar dan memakai cache bersama, tetapi autentikasi terkini tetap **perlu `hermes mcp login tinyfish` sekali pada default**. Jangan menyebut kelimanya sudah terhubung sebelum probe setelah login berhasil.

Uji operasi `fetch_content` nyata tidak dijalankan karena automatic approval review menolak tindakan tersebut sebagai kemungkinan penggunaan kuota/kredit. Audit dilanjutkan dengan initialize/tools-list saja. Tidak ada Search, Fetch, otomasi browser, atau pengeluaran Tinyfish yang sengaja dijalankan dalam pengujian ini. Probe yang gagal menghasilkan exit code nonzero; status cache saja tidak menghasilkan klaim sukses.

## Cadangan dan rollback

Pemasangan menghasilkan `msshi-runtime/backups/<timestamp>-web-services/receipt.json`. Receipt mencatat hash konfigurasi sebelum/sesudah, cadangan konfigurasi, dan lokasi direktori OAuth asli yang dipindahkan. Cadangan berisi data pribadi dan tidak boleh dipublikasikan.

Jika pemasangan gagal, helper mencoba rollback terbatas: konfigurasi hanya dipulihkan bila masih cocok dengan hash hasil pemasangan; junction hanya dilepas bila targetnya persis direktori canonical yang dicatat. Isi direktori canonical tidak dihapus. Untuk rollback manual setelah penggunaan, hentikan koneksi gateway terlebih dahulu, cocokkan receipt, pulihkan konfigurasi yang belum berubah, lepas **junction saja**, kemudian kembalikan direktori cache asli. Jangan menghapus isi `mcp-tokens` default dan jangan memakai recursive delete pada junction.

BrightData tetap nonaktif pada setup pribadi MuZA karena akun/API key belum tersedia. Pemasangan ini tidak mengaktifkan BrightData, membuat zona, atau menjalankan scraping.
