# Nama pengguna dan protokol kolaborasi SOUL

Preset MuZA adalah nama topologi lima peran, bukan nama orang yang sedang memakai bot. Kelima template publik menanyakan nama/sapaan sekali bila belum diketahui, memakai ejaan lengkap yang diberikan, serta mengikuti gaya singkatan pilihan pengguna. Sapaan yang sudah disetujui boleh disampaikan melalui handoff agar bot lain tidak menanyakan ulang. Tidak ada identitas pribadi yang otomatis disalin dari pembuat proyek atau contoh dokumentasi.

## Dua protokol spesialis

- **Sir. Robot / Shikaku:** Main memahami proyek, menulis inti dan integrasi; tugas kompleks memakai MoA yang benar-benar tersedia untuk blueprint; eksekutor mendapat modul terisolasi dengan kontrak teknis; Main memeriksa, menggabungkan dan memverifikasi hasil.
- **Kiki-Chii:** Concepting First, dewan kreatif yang tersedia untuk rancangan kompleks, Main memegang produksi, hasil editabel dan preview bertahap. Pengguna dapat mengubah arah kapan saja. Catatan keputusan disiapkan sebagai draf.

Nama model pada runtime milik pengguna tetap menjadi acuan. Teks SOUL tidak memasang MoA, menciptakan tool, membeli endpoint, atau mengganti provider/model. Tugas kecil tidak perlu dewan atau subagen. Jika host tidak mendukung pembagian yang diminta, bot menjelaskan keterbatasan dan memakai alur yang jujur. KAT opsional/default OFF, termasuk pada preset MuZA.

**Obsidian:** protokol menyiapkan format dokumentasi, tetapi tidak memberi izin menulis ke vault. Lokasi, file, isi dan tindakan perlu izin terpisah. Helper di bawah tidak menyentuh vault, aplikasi Obsidian, NotebookLM, sinkronisasi/akun, atau config model.

## Instalasi baru dan SOUL yang sudah dikustomisasi

Instalasi baru memakai template persona yang sudah berisi kebijakan nama. Installer mempertahankan SOUL lama yang dikustomisasi. Untuk menambahkan hanya blok protokol bertanda pada dua profil yang sudah ada, jalankan dari checkout sumber yang telah ditinjau:

```powershell
python scripts/msshi_soul_protocol.py --home "C:\HermesClient" --profiles shikaku kiki-chii
```

Itu pratinjau, tanpa penulisan. Setelah rencana sesuai, terapkan:

```powershell
python scripts/msshi_soul_protocol.py --home "C:\HermesClient" --profiles shikaku kiki-chii --apply
```

Ganti root contoh dengan root Hermes yang benar. `--profiles` juga menerima `yukino`, `shizuka`, atau `val` bila hanya ingin menambahkan kebijakan sapaan pada profil tersebut. SOUL harus sudah ada. Helper tidak menyalin seluruh template di atas persona pribadi: byte di luar blok bertanda tetap dipertahankan. Penerapan berulang tidak menggandakan blok.

Cadangan dan receipt disimpan di `HERMES_ROOT/msshi-runtime/soul-receipts/<id>/`. Receipt mencatat hash, bukan isi config atau secret. Rollback hanya memulihkan SOUL yang masih cocok dengan hash hasil pemasangan; perubahan pengguna sesudahnya dilaporkan sebagai konflik.

```powershell
python scripts/msshi_soul_protocol.py --home "C:\HermesClient" --rollback "PATH_RECEIPT"
python scripts/msshi_soul_protocol.py --home "C:\HermesClient" --rollback "PATH_RECEIPT" --apply
```

Perintah pertama kembali merupakan pratinjau. Helper memakai daftar profil yang diizinkan, menolak symlink/junction, memeriksa perubahan bersamaan sebelum menulis, dan tidak memanggil model/API. Mulai sesi baru sesuai mekanisme host agar instruksi SOUL baru terbaca; jangan menghapus percakapan lama untuk melakukan ini.
