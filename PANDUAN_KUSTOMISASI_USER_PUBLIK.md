# Panduan setup dan kustomisasi MSSHI

Buka terminal di folder hasil ekstrak yang berisi `README.md`. Gunakan Python 3.10 atau lebih baru. Python 3.12 disarankan. Bila diperlukan, ganti `python` menjadi `python3` di macOS/Linux atau `py -3` di Windows jika tersedia. Pastikan versi dengan `python --version` dan jalankan `python scripts/check_release.py` dari root paket. Semua contoh pertama adalah pratinjau. Tinjau tujuan yang dicetak sebelum mengulang perintah dengan `--apply`.

| Saya ingin… | Perintah pratinjau |
| --- | --- |
| Satu agen untuk semua skill | `python scripts/install_msshi.py --mode solo --platform hermes` |
| Tim dengan nama dan peran sendiri | `python scripts/install_msshi.py --mode custom-bots --matrix ./matrix-lokal.json --target-dir ./my-msshi-team` |
| Memasang beberapa paket | `python scripts/install_msshi.py --mode selective --packs core,filmmaking --platform hermes` |
| Kru lima bot MuZA | `python scripts/install_msshi.py --mode muza-preset --target-dir ./my-msshi-team` |

Gunakan `--platform openclaw`, `claude`, `antigravity`, `chatgpt`, atau `manual` sesuai kebutuhan. Tanpa tujuan eksplisit, installer memilih folder skill yang terdeteksi atau folder ekspor di lokasi kerja. Pada Windows, `D:\HermesData` merupakan salah satu kandidat Hermes. Lokasi lain dapat dipilih dengan `HERMES_HOME` atau `--target-dir`. Saat mode tim aktif, `--target-dir` menunjuk ke induk workspace, bukan folder skill global. [Panduan platform](docs/platforms.md).

## Mencoba di folder lokal

```sh
python scripts/install_msshi.py --mode selective --packs core --platform manual --target-dir ./msshi-demo-skills
```

Setelah tujuan sesuai, ulangi perintah itu dengan `--apply` untuk menyalin paket inti ke folder tersebut. Buka `msshi-demo-skills` dan periksa salah satu `SKILL.md`. Hubungkan folder tersebut ke host pilihanmu atau ikuti contoh pengecekan salinan di [panduan CLI](docs/CLI.md). Mode manual berguna untuk memeriksa file sebelum memasukkannya ke profil aplikasi.

## Menyiapkan tim sendiri

1. Salin [matriks](configs/bot_role_and_skill_matrix.json) sebagai `matrix-lokal.json` dan pertahankan bagian katalog skill serta paket.
2. Edit daftar bot. Tentukan ID unik seperti `riset` atau `kreatif`, nama tampilan, peran, persona, rute serah terima, dan daftar skill. Untuk tim dua orang, hapus tiga entri lain dan sesuaikan rujukan antar-ID. Untuk menambah bot, duplikasi satu entri dengan ID baru.
3. Lihat contoh [persona di paket](configs/personas). Simpan persona kustom di dalam checkout, lalu pakai path yang relatif terhadap checkout. Jika ingin mengubah persona setelah ekspor, edit `SOUL.md` di workspace bot dan sesuaikan `AGENTS.md` bila mengubah rute.
4. Jalankan pratinjau mode `custom-bots`. Periksa nama tujuan, skill bawaan, dan integrasi opsional yang masih memerlukan penyiapan. Ulangi dengan `--apply`.
5. Pasangkan workspace yang dihasilkan dengan profil host. Di Hermes, gunakan pengelolaan profil untuk membuat atau memilih bot, lalu pindahkan instruksi dan skill sesuai tujuan profil. Konfirmasi dukungan delegasi host sebelum mengandalkan handoff otomatis.

Mode preset memakai matriks lima bot bawaan. Mode selektif menerima `core`, `filmmaking`, `business`, `thesis`, `webdev`, dan `cybersec`. Cek ringkasan pratinjau untuk melihat slug yang masuk setiap pilihan. Pemilihan paket mengatur file yang disalin, sedangkan kemampuan integrasi eksternal mengikuti akun dan instalasi host.

## Menyesuaikan bahasa dan suara

1. Buat Voice Card dengan 2–3 sampel yang boleh dipakai. Catat panjang kalimat, sapaan, tingkat formalitas, istilah yang dipertahankan, dan frasa yang ingin dihindari. Simpan lokal, misalnya `local/voice-card.local.md`.
2. Minta `match-my-writing-style` membandingkan draf dengan Voice Card. Tinjau satu paragraf dulu untuk memastikan maksud, angka, dan sumbernya tetap tepat.
3. Jika kamu memasang `adhiprib/humanizer-indonesia`, simpan sampel yang telah dibersihkan di `references/voice-namaanda-id.md` pada salinan skill. Pilih ragam akademik, ajar, atau semiformal berdasarkan audiens. Jalankan `scripts/metrik.py --help` dari versi yang dipasang untuk memeriksa opsi metriknya.
4. Untuk visual, salin `configs/user_creative_dna.json` ke penyimpanan privat. Tambahkan hanya keputusan yang kamu setujui, seperti kontras, palet, ritme cut, dan gaya narasi.

Untuk ChatGPT, masukkan instruksi dan referensi pilihan sesuai batas unggah. Untuk Custom GPT Actions, backend HTTPS, autentikasi, dan pengujian kontrak diperlukan. Untuk proyek akademik dan kreatif, gunakan data contoh saat membagikan repositori. Periksa [pembaruan dan pemulihan](docs/CLI.md), [audit per bot](docs/AUDIT_SKILLS_PER_BOT.md), dan [katalog integrasi](docs/INTEGRASI.md).
