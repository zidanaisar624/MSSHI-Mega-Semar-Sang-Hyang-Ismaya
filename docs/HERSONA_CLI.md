# Hersona lokal melalui CLI

Hersona membantu menyusun atribut gaya bicara dan resep persona. MSSHI dapat memakai executable `hersona` yang sudah terpasang sebagai proses CLI singkat. Katalog tidak membutuhkan server MCP, daemon, API key, atau panggilan LLM untuk perintah pratinjau di bawah.

Persona native Hermes yang sudah dipilih dan teks `SOUL.md` tetap menjadi sumber perilaku bot. Membaca katalog atau mengekspor resep tidak otomatis mengganti keduanya.

## Jalur MSSHI v3

Jalankan migrasi MSSHI yang telah diperiksa agar route `hersona` terdaftar. Jika runtime Hersona belum tersedia, status harus menjelaskan prasyaratnya. Keberadaan panduan ini sendiri bukan bukti Hersona sudah terpasang.

```powershell
msshi runtime status
$ticket = msshi runtime ticket --profile default --target hersona --task "Lihat atribut persona lokal yang diminta pengguna"
msshi runtime run --profile default --ticket $ticket hersona -- list
```

Setiap eksekusi membutuhkan tiket baru. Pilih profil bot yang sedang mengerjakan tugas. Route harus menyetel `PYTHONUTF8=1` dan `PYTHONDONTWRITEBYTECODE=1` hanya pada proses anak. UTF-8 diperlukan agar katalog Unicode dapat ditampilkan di Windows.

## Perintah pratinjau

Argumen berikut dikirim setelah `hersona --` pada perintah `msshi runtime run`.

| Tujuan | Argumen CLI | Keluaran |
| --- | --- | --- |
| Daftar atribut | `list` | Nama atribut menurut kategori |
| Satu atribut | `show personality/kuudere` | Detail atribut terpilih |
| Rancangan blend | `blend personality/kuudere speech/soft --compact` | Teks prompt sebagai draf |
| Draf portabel JSON | `export personality/kuudere speech/soft --format json` | Objek dengan `hersona`, `system_prompt`, `conflicts`, dan `attributes` |
| Pratinjau blend | `preview personality/kuudere speech/soft` | Prompt dan contoh frasa lokal |
| Perbandingan | `diff personality/kuudere personality/stoic` | Persamaan dan perbedaan atribut |
| Matriks | `matrix --json` | Matriks kompatibilitas lengkap |

Dispatcher MSSHI dapat membungkus hasil eksekusi dalam laporan JSON. Data asli CLI berada pada keluaran stdout yang dicatat dispatcher. Jangan menyalin seluruh matriks ke konteks LLM jika satu atribut sudah cukup. Pada revisi yang diuji, matriks lengkap berukuran sekitar 117 KB.

## Batas perubahan

- Keluaran blend/export adalah draf untuk diperiksa. Jangan memasukkannya ke system prompt secara otomatis.
- Route katalog harus memakai daftar perintah yang diizinkan. Jangan menjalankan `soul`, `persistent`, `create`, `save`, `personas install`, `personas use`, `update`, atau `decide` melalui route pratinjau.
- Penyimpanan preferensi persona tetap memakai mekanisme native Hermes atau helper persona yang memiliki backup dan cakupan perubahan yang jelas, setelah pengguna memintanya.
- Penilaian intensity/bench bersifat leksikal dan dapat tidak mendukung Bahasa Indonesia. Nilainya tidak mengukur empati atau kondisi kesehatan pengguna.
- CLI tidak perlu dijalankan pada setiap balasan. Persona yang telah disimpan tetap digunakan oleh Hermes; katalog dipanggil saat tugas membutuhkan pemeriksaan atau rancangan baru.

## Hasil uji lokal MuZA

Pada 11 November 2026, executable native Hersona yang sudah terpasang berhasil menjalankan `list`, `show`, `matrix --json`, `blend --compact`, `export --format json`, dan `personas list`, semuanya dengan exit code 0. Katalog memuat 346 atribut. Hash 12 berkas `SOUL.md` dan teks persona sama sebelum/sesudah uji. Tidak ada server MCP atau panggilan LLM yang dijalankan.

Hasil tersebut memverifikasi perintah baca/pratinjau pada instalasi lokal yang diuji. Ia tidak membuktikan seluruh kombinasi atribut, semua versi upstream, atau pemilihan skill oleh model percakapan.

Sumber API dan CLI: [Hersona](https://github.com/shiro-0x/hersona) pada revisi lokal yang dipin `75146c9126e1614750eeead3da165d61a3fc2188`.
