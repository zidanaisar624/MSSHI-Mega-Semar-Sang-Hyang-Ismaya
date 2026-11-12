# MSSHI v3.1 - instalasi dan batas pengujian

v3.0 dituntaskan dan dipublikasikan lebih dahulu pada commit `a8400c8a44163b097ce0e11e6489dfa381c4eb81`, tag `v3.0.0`. ZIP dan PDF v3.0 adalah arsip tahap tersebut. v3.1 menambahkan empat integrasi standar dan satu opsi REA tanpa mengganti provider/model, MoA, persona, SOUL, memori, atau Creative DNA.

## Setelah memasang CLI v3.1

```powershell
msshi update
msshi managed status
msshi brag doctor
msshi scrapling status
msshi harness2 status
```

`msshi update` memperbarui source/skill yang dikelola dan cache upstream. Ia tidak menjanjikan semua runtime npm/pip pihak ketiga diperbarui otomatis. Setup runtime opsional dijelaskan pada masing-masing panduan. Hindari memasang dependencies/model/repositori ke dalam `skills/`.

## Pemilihan alur

- **Unslop**: perbaikan UI bertahap. Kiki menangani arah visual, Val meninjau bukti/label/unit pada dashboard ilmiah, Shikaku menerapkan perubahan. Skill ini tidak mengubah gaya percakapan atau mengulang audit kualitas pada setiap pesan.
- **BRAG**: Kiki mulai dari konsep, brief, storyboard/timeline, preview, dan review. Tidak mengikuti shortcut upstream yang mengganti model atau melewati storyline/SPEC/review. Musik/SFX mempunyai lisensi terpisah dan tidak disalin ke paket.
- **Scrapling**: Val/Coder mengekstrak HTML lokal dengan CSS/XPath. Wrapper parser tidak menyediakan crawler jaringan, browser stealth, pemecahan CAPTCHA, atau penggunaan profil Chrome personal.
- **Harness²**: Val mengevaluasi bukti perbaikan harness, Coder menguji implementasi. Demo deterministik dan proposal disimpan terpisah; Shizuka dapat menyampaikan hasil untuk review pengguna. Tidak menjalankan benchmark berbayar, gcloud login, Codex executor tanpa sandbox, atau promosi perubahan ke bot aktif.

## Status yang harus dibedakan

Keberadaan skill, dependencies terpasang, uji lokal, autentikasi layanan, dan hasil tugas nyata merupakan status berbeda. Lihat audit pribadi untuk bukti laptop MuZA. Uji parser/demonstrasi sintetis tidak membuktikan seluruh situs atau benchmark model bekerja. Render video perlu RAM/disk yang cukup; status doctor dan keluaran render harus diperiksa, bukan hanya exit code.

Steel tetap menjadi jalur browser umum melalui guard yang sudah terpasang; API key/endpoint belum tersedia pada audit v3.0. Akses browser personal tetap perlu persetujuan terikat tujuan/situs/akun/cakupan. Tinyfish terdaftar pada semua bot tetapi memerlukan login ulang pada audit terakhir. GitLab telah lolos discovery/autentikasi lima profil. BrightData tetap nonaktif.

## Lisensi

Materi orisinal MSSHI mengikuti MIT. Unslop: CC-BY-4.0, atribusi Damir Sokolovsky. BRAG skill: MIT; musik CC-BY-4.0/SFX berlisensi tersendiri tidak dibundel. Scrapling: BSD-3-Clause. Harness²: Apache-2.0; benchmark/third-party memakai ketentuan masing-masing. Runtime Hyperframes juga memakai ketentuan upstream. [Notices](../THIRD_PARTY_NOTICES.md) dan [audit lisensi](../configs/upstream_license_audit.json) mencatat pin sumber.

## Pemulihan

Skill baru terdaftar berdasarkan hash; updater mempertahankan kustomisasi dan memeriksa junction. Cadangan versi sebelumnya berada di luar scanner. Runtime/model/cache berada di folder privat terpisah dan tidak dibundel ke ZIP GitHub. Jangan menimpa `SOUL.md` atau konfigurasi provider untuk memperbaiki kegagalan dependency. [Cakupan updater dan rollback](MANAGED_UPDATES.md).

## REA untuk publik: pilihan tambahan, default tidak aktif

REA sudah tercantum dalam inventaris source lama, sehingga tidak dihitung sebagai repo baru atau dipasang ulang sebagai duplikat. Skill REA berada di `optional/rea/`, di luar folder `skills/` standar. Pemasangan standar, paket portabel, dan jalur Skills CLI yang menunjuk `skills/` tidak mengaktifkan REA. Aktifkan hanya jika pengguna memang memilih analisis reverse engineering:

```powershell
msshi optional list
msshi optional enable rea --target-dir "PATH_TO_CODER_SKILLS" --install-runtime --hermes-home "PATH_TO_HERMES_ROOT"
```

Wizard dapat menawarkan pilihan default Tidak; `--with-rea` merupakan pilihan eksplisit. `--install-runtime` adalah izin memasang runtime npm terisolasi, bukan menambahkan server MCP, provider model, atau engine native berbayar. Pengaturan pribadi MuZA mengaktifkannya untuk Coder sesuai permintaan. Setup GitHub orang lain tetap nonaktif. Updater hanya memelihara opsi yang sudah diaktifkan/terdaftar berdasarkan hash. [Panduan REA](REA.md).
