# Pemeriksaan sebelum publikasi

Rilis MSSHI v3.1.2 memuat 67 skill bundel (51 inti + 16 wrapper) dan manifest 51 sumber. Perubahan lokal tidak otomatis berarti GitHub sudah diperbarui: cocokkan HEAD dengan origin/main atau gunakan msshi status. Riwayat commit dipertahankan. Tag v3.1.2 diperbarui sesuai permintaan pemilik; tag versi sebelumnya tetap dipertahankan. PDF panduan publik disertakan; audit dan preset pribadi tidak masuk repo publik. [Perubahan v3.1.2](V3_1_2_REPAIR.md).

```sh
python scripts/check_release.py --smoke
```

Pemeriksaan membaca struktur, matriks, audit, tautan lokal, metadata skill, serta SVG. Opsi `--smoke` menguji installer, updater, registrasi rute CLI-Anything, dan aturan akses API katalog dengan data uji sementara. Untuk profil nyata, `msshi audit --home PATH_HERMES` memeriksa kondisi dan bukti lokal. Verdict audit hanya berlaku untuk pemeriksaan yang dicatat; batas performa, keamanan, model opsional, dan layanan yang belum diuji tetap harus dilaporkan. Jalankan dari salinan bersih sebelum membuat commit. Hak penggunaan materi tetap ditinjau oleh pemilik sebelum publikasi.

| Pemeriksaan pemilik | Yang perlu dipastikan |
| --- | --- |
| Cakupan lisensi | [MIT](../LICENSE) sudah ditetapkan untuk materi orisinal MSSHI. Tinjau apakah tambahan pihak ketiga memerlukan izin atau atribusi tersendiri. |
| Persona MuZA | Tentukan apakah akan mempertahankan nama karakter referensi setelah meninjau izin atau memakai alias publik. Audit, matriks, persona dan visual harus menyebut nama yang sama. |
| File yang akan masuk Git | Tinjau daftar file sebelum commit. Simpan notebook, dataset, Voice Card, Creative DNA, dan kredensial di folder privat. |
| Integrasi eksternal | Verifikasi akun, dependensi, biaya dan izin jika akan mengklaim sebuah integrasi sudah berjalan. README memisahkan rujukan, pemasangan dan pengujian. |

Tujuh SVG di paket ini adalah aset visual rilis. Tiga di antaranya menggantikan PNG dari arsip sumber. Panduan asal materi ada di [catatan provenance](PROVENANCE.md). Untuk memeriksa cara GitHub mendeteksi dan menampilkan lisensi, lihat [panduan lisensi GitHub](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).

Arsip publik memuat 67 folder skill dan satu pintu masuk di root. Panduan pemulihan dan installer pribadi disimpan terpisah. Pada instalasi baru, default menjadi Yukino; susunan bot pengguna lama dipertahankan secara otomatis.

## Batas integrasi opsional

MCP aplikasi desktop serta utilitas lokal Hersona/Llmtrim dialihkan ke CLI. GitLab/Tinyfish tetap menjadi MCP web sesuai konfigurasi pengguna. Penghematan Llmtrim otomatis dibatasi pada hasil alat JSON yang memenuhi syarat melalui hook native; periksa penghitung dengan `msshi trim --status --profile default`. Tidak ada klaim seluruh chat otomatis dipadatkan atau persentase penghematan tagihan tertentu.

Rute pemasangan Steel lama dihentikan. Wizard browser hanya menyimpan pilihan dan label pribadi untuk login manual; tidak memindahkan akun/cookie atau memasang konektor layanan otomatis. Lisensi model OmniVoice dan komponen eksternal mengikuti [notices](../THIRD_PARTY_NOTICES.md), termasuk batas CC-BY-NC untuk bobot OmniVoice. Label opsional atau keberadaan instruksi tidak membuktikan runtime eksternal sudah berfungsi.

Uji updater shared/junction: `python scripts/check_managed.py`. [Cakupan pendaftaran dan rollback](MANAGED_UPDATES.md). [Status layanan web](SERVICE_CONNECTIONS.md). [TimesFM](TIMESFM.md).
