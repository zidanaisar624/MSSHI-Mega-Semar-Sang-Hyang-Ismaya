---
name: harness2
description: Buat proposal evaluasi harness dan jalankan demo deterministik Harness² di ruang privat. Untuk Val menilai bukti eksperimen dan Coder menyiapkan kandidat terisolasi; tanpa perubahan otomatis pada persona, memori, konfigurasi, atau harness Hermes aktif.
license: MIT
metadata:
  upstream: https://github.com/google-research/harness2
  upstream_commit: 6868817518876de8fd170c6a8354daca273b6191
  upstream_license: Apache-2.0
---

# Harness²: proposal, bukti, dan demo lokal

[Harness² dari Google Research](https://github.com/google-research/harness2/tree/6868817518876de8fd170c6a8354daca273b6191) mengoptimalkan sistem di sekitar model melalui Propose–Probe–Compose dengan bobot model tetap. Delapan komponen yang dipelajari upstream adalah system prompt, guardrails, memory, tool guidance, subagents, skills, scripts, dan plugins. Daftar itu menjelaskan permukaan eksperimen pada salinan terisolasi, bukan izin mengubah Hermes aktif.

**Val** merumuskan hipotesis, baseline, data evaluasi terpisah, ukuran keberhasilan, ketidakpastian, dan interpretasi bukti. **Coder** menyiapkan kandidat dalam workspace eksperimen, diff yang dapat ditinjau, probe yang dapat diulang, dan rencana rollback. Ringkasan untuk Shizuka berisi tujuan, perubahan yang diusulkan, bukti, kegagalan, biaya, dan keputusan yang masih memerlukan tinjauan manusia; gunakan rute koordinasi yang sudah diotorisasi.

Pertahankan provider, model, fallback, MoA, persona, SOUL, DNA, memori, plugin, dan gaya native pengguna. Jangan mempromosikan proposal atau lesson demo ke konfigurasi atau memori persisten. Tugas ini tidak mengaktifkan model self-training atau pengubahan bobot.

## Perintah yang tersedia

Gunakan CLI MSSHI bila tersedia, atau helper mandiri di folder skill ini. Ganti `HERMES_ROOT` dengan direktori data bersama, bukan direktori profil.

```text
python scripts/msshi_harness2.py --hermes-home HERMES_ROOT status --verify
python scripts/msshi_harness2.py --hermes-home HERMES_ROOT plan --goal "Uji hipotesis sempit dengan baseline dan holdout"
python scripts/msshi_harness2.py --hermes-home HERMES_ROOT install --source PINNED_CHECKOUT
python scripts/msshi_harness2.py --hermes-home HERMES_ROOT demo
```

Jalankan dari folder skill atau gunakan path absolut helper. `status` membaca kesiapan; `plan` mengeluarkan proposal JSON tanpa menjalankan eksperimen. `install` adalah setup eksplisit Python 3.12: core upstream dari commit yang dipin, tanpa extras atau dependensi model, di `HERMES_ROOT/msshi-private/harness2-runtime`. Instalasi dapat mengunduh build tools Python yang dipin. Ia tidak mengonfigurasi Google Cloud, Codex, atau endpoint LLM.

`demo` menjalankan entry point resmi `harness2-demo` dengan `--k 2 --mode both` melalui worker anak yang dibatasi. Demo menggunakan editor deterministik dan program ledger Python/CSV/Decimal; tidak memakai kredensial atau kredit API. Output baru berada di subfolder privat `demo-runs`, tidak menimpa hasil lama. Lingkungan anak memakai allowlist, CWD baru tanpa `.env`, jaringan dinonaktifkan, dan hanya eksekusi program ledger yang sudah ditinjau diperbolehkan. Kompatibilitas Windows hanya diterapkan di proses demo anak untuk lock ringkasan dan normalisasi key path; source upstream terpasang tetap utuh.

## Menilai proposal

Mulai dari satu kegagalan yang dapat diamati dan hipotesis perubahan kecil. Simpan baseline serta kandidat pada salinan terpisah; gunakan tugas probe yang sama dan holdout yang tidak bocor ke perancangan. Compose berdasarkan perbedaan perilaku yang teramati. Laporkan diff, bukti, hasil negatif, ketidakpastian, biaya, dan rollback sebelum meminta keputusan manusia. Demo ledger menunjukkan alur rekursi, bukan bukti peningkatan kemampuan Val/Coder pada pekerjaan nyata.

Wrapper hanya menyediakan `status`, `install`, `demo`, dan `plan`. Jangan memanggil benchmark, judge, bridge, setup executor, Vertex/gcloud, atau executor Codex upstream sebagai kelanjutan otomatis. Benchmark bermodel membutuhkan setup, pembatasan jaringan/answer leakage, anggaran API, dan otorisasi terpisah; upstream menargetkan Linux dan executor Codex menonaktifkan sandbox. Kesiapan demo lokal tidak membuktikan kesiapan benchmark penuh.

Core upstream mengikuti [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0), disertakan sebagai [LICENSE.upstream](LICENSE.upstream); wrapper dan petunjuk MSSHI mengikuti lisensi materi orisinal MSSHI. Proyek upstream bukan produk Google yang didukung resmi.
