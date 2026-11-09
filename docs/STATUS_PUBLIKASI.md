# Pemeriksaan sebelum publikasi

Paket ini adalah kandidat rilis MSSHI Tahap 1. Ekstrak ke folder baru, masuk ke folder yang memuat README, lalu jalankan pemeriksaan lokal dengan Python 3.10 atau lebih baru.

```sh
python scripts/check_release.py --smoke
```

Pemeriksaan membaca struktur, matriks, audit, tautan lokal, metadata skill, serta SVG. Opsi `--smoke` menguji keempat mode installer, ketiga mode updater, dan aturan akses API katalog dengan data uji sementara. Jalankan dari salinan bersih sebelum membuat commit. Hak penggunaan materi tetap ditinjau oleh pemilik sebelum publikasi.

| Pemeriksaan pemilik | Yang perlu dipastikan |
| --- | --- |
| Cakupan lisensi | [MIT](../LICENSE) sudah ditetapkan untuk materi orisinal MSSHI. Tinjau apakah tambahan pihak ketiga memerlukan izin atau atribusi tersendiri. |
| Persona MuZA | Tentukan apakah akan mempertahankan nama karakter referensi setelah meninjau izin atau memakai alias publik. Audit, matriks, persona dan visual harus menyebut nama yang sama. |
| File yang akan masuk Git | Tinjau daftar file sebelum commit. Simpan notebook, dataset, Voice Card, Creative DNA, dan kredensial di folder privat. |
| Integrasi eksternal | Verifikasi akun, dependensi, biaya dan izin jika akan mengklaim sebuah integrasi sudah berjalan. README memisahkan rujukan, pemasangan dan pengujian. |

Tujuh SVG di paket ini adalah aset visual rilis. Tiga di antaranya menggantikan PNG dari arsip sumber. Panduan asal materi ada di [catatan provenance](PROVENANCE.md). Untuk memeriksa cara GitHub mendeteksi dan menampilkan lisensi, lihat [panduan lisensi GitHub](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).
