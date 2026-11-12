# Browsing utama Hermes-Steel

MSSHI memasang plugin resmi [`steel-dev/hermes-steel`](https://github.com/steel-dev/hermes-steel)
bersama plugin native `msshi-steel-policy`. Plugin resmi dipin pada commit
`d8a1e39657d3e3deaa59da37e857be3f14b9dc5b` (MIT). Keduanya berada di
`<HERMES_HOME>/plugins`, bukan di dalam folder scanner `skills`.

## Perilaku nyata

Hermes yang terpasang memiliki fallback otomatis dari provider cloud ke Chromium
lokal ketika pembuatan sesi gagal. Karena pengguna meminta Steel menjadi jalur
utama, middleware MSSHI mengambil alih eksekusi `browser_exec` melalui API plugin
yang didukung. Ia membuat sesi dengan provider Steel resmi lalu memasok CDP
Steel secara eksplisit hanya ke proses anak browser-harness. Resolver fallback
lokal Hermes tidak dipanggil dan source inti Hermes tidak diubah.

Setiap panggilan adalah **satu batch dengan sesi baru**. Gabungkan navigasi,
pengambilan data dan langkah terkait dalam satu panggilan. Variabel/tab tidak
bertahan ke batch berikutnya. Setelah batch sukses/gagal/timeout, adapter mencoba
menghentikan daemon harness ber-ID uniknya dan melepas sesi Steel miliknya dalam
`finally`. Kegagalan pelepasan remote ditampilkan melalui `remote_session_released`;
batas keras sesi Steel 180 detik menjadi pengaman tambahan. Adapter tidak
menghentikan browser atau daemon milik pengguna/pekerjaan lain.

Tidak ada browser atau sesi yang dibuka saat startup, idle, pemeriksaan status,
atau registrasi plugin. Pengaturan `use_real_profile: false` dan
`auto_local_for_private_urls: false` mencegah upgrade diam-diam ke profil personal
atau sidecar lokal. Layanan cloud tetap dapat memakai kuota/biaya akun Steel;
persetujuan manusia ditampilkan sebelum batch dan bukan hard cap tagihan. Proxy,
CAPTCHA berbayar, dan alat scrape langsung diblokir pada kebijakan saat ini.

## Instalasi dan status tanpa kredit LLM

```powershell
msshi browser --install --hermes-home "D:\HermesData"
msshi browser --status --hermes-home "D:\HermesData"
```

Ulangi dengan direktori profil lain. Installer memakai source resmi yang dipin,
menyimpan hash kepemilikan dan receipt rollback, serta menolak menimpa file plugin
yang telah dikustomisasi. Installer juga menyimpan baseline nilai setting browser
yang dikelolanya; bila pengguna mengubah
route atau batas tersebut setelah instalasi, update berhenti dan mempertahankannya.
Loader plugin native harus `in_process`; installer
mempertahankan pilihan isolasi khusus pengguna jika berbeda dan berhenti dengan
penjelasan. `--steel-ready` lama diabaikan: flag tidak membuktikan koneksi.

`configured` berarti file plugin/konfigurasi tersedia. `credentials_present`
memeriksa keberadaan rahasia, tidak menampilkan nilainya. `authenticated` dan
`connected` tetap belum terverifikasi sampai API benar-benar diuji. Pemeriksaan
ini tidak membuka sesi, memakai LLM, atau memotong kuota Steel.

Untuk Steel cloud, buat akun dan masukkan `STEEL_API_KEY` melalui file `.env`
privat profil Hermes atau pengaturan rahasia resmi. Jangan tempel key ke chat,
README atau repo. Endpoint self-hosted resmi yang kompatibel dapat memakai
`browser.steel.base_url`; penyediaan server/biayanya merupakan langkah terpisah.
Setelah mengubah rahasia, mulai ulang/reload plugin sesuai mekanisme Hermes.
Jika key belum ada, browsing umum berhenti dengan petunjuk setup, tanpa fallback
diam-diam ke Chrome. Paket ini tidak menjanjikan browsing seluruhnya gratis.

Rollback tersedia tanpa Codex:

```powershell
msshi browser --rollback "PATH_RECEIPT_STEEL\receipt.json" --hermes-home "PATH_PROFIL"
```

Gunakan receipt dari profil yang sesuai. Hash file saat ini dan cadangan diperiksa
sebelum pemulihan; file yang diubah pengguna setelah instalasi dipertahankan dan
rollback berhenti untuk ditinjau. Mulai ulang/reload plugin setelah rollback.

## Akun personal dan persetujuan

Jika tugas memerlukan akun yang sudah login di browser pengguna, jelaskan situs,
akun, tujuan, akses dan durasi. Gunakan `msshi_personal_browser`: hook native
Hermes meminta persetujuan manusia untuk cakupan tersebut. Alat hanya bisa
menyambung ke CDP yang sudah dipasang operator melalui `/browser connect`; ia
tidak mencari browser, membukanya, menyalin profil/cookie, atau mengaktifkan
`use_real_profile`. Bila endpoint belum tersambung, alat mengembalikan petunjuk
dan berhenti. Kepatuhan batas situs/tindakan tetap harus dijaga agen.

Pemindahan login ke Steel belum diimplementasikan. Tinjau metode sesi resmi atau
login manual yang didukung, jelaskan data yang akan dikirim, akun dan masa akses,
lalu minta persetujuan **terpisah**. Jangan mengambil password/cookie/profil secara
otomatis. Persetujuan akses browser personal bukan persetujuan pemindahan sesi.

## Batas teknis dan uji

Plugin Steel terbaru memanggil helper `sensitive_query_param_name` yang belum ada
pada Hermes stabil di laptop ini. Installer menambahkan adaptor bersyarat pada
entrypoint plugin Steel: bila helper itu belum ada, hanya provider browser yang
didaftarkan. Alat scrape/options opsional tidak dimuat, sesuai kebijakan yang
memblokirnya. Source inti Hermes dan implementasi provider Steel tetap utuh.
File entrypoint yang diadaptasi dilacak oleh hash installer dan lisensi MIT asli
tetap disertakan. Pada Hermes yang telah mempunyai helper tersebut, registrasi
opsional asli tetap tersedia tetapi gate MSSHI tetap memblokirnya.

Adapter menggunakan provider resmi dan child browser-harness terpasang. Versi
berikutnya dapat mengubah API adapter; kegagalan pemeriksaan kompatibilitas akan
berhenti, bukan menjalankan tool asli yang mempunyai fallback lokal. Plugin ini
merupakan kebijakan tool Hermes, bukan sandbox sistem operasi: terminal/Computer
Use terpisah memiliki kebijakan sendiri dan tidak boleh dipakai untuk melewati
route browsing ini.

Preview/sign-in di antarmuka Electron Hermes merupakan jalur terpisah dari tool
agen. Guard ini tidak mengaudit atau mengubah implementasi preview tersebut dan
tidak mengklaim menghentikan seluruh aliran cookie di aplikasi. Jangan memakai
fitur impor login/profil pada preview tanpa persetujuan terpisah; audit UI itu
merupakan pekerjaan tersendiri.

Uji sintetis mencakup kegagalan provider, timeout driver, pelepasan sesi milik
batch, dan gate persetujuan akun. Uji ini tidak membuktikan autentikasi atau sesi
Steel cloud nyata. Lihat audit privat instalasi untuk hasil masing-masing bot.

Dokumentasi resmi: [Hermes-Steel](https://github.com/steel-dev/hermes-steel),
[pengaturan Steel](https://github.com/steel-dev/hermes-steel#configuration), dan
[batas/harga layanan](https://docs.steel.dev/overview/pricinglimits).
