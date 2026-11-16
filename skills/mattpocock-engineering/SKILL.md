---
name: mattpocock-engineering
description: Gunakan disiplin engineering Matt Pocock ketika membahas desain, spesifikasi, TDD, debugging atau domain model; kelima bot dapat membaca bagian relevan. Orkestrator grill-me/to-spec dan publikasi issue tetap memerlukan permintaan eksplisit; tidak memasang hook atau mengubah model otomatis.
license: MIT
metadata:
  upstream: https://github.com/mattpocock/skills
  upstream_commit: 5863806dd4e15c63174bee4e7515a4256792ecfa
  activation: context-or-explicit
---

# Skills for Real Engineers, dimuat sesuai kebutuhan

Tersedia pada kelima bot untuk diskusi arsitektur/spesifikasi. Shikaku menangani
implementasi; Val memeriksa bukti dan pengujian; Shizuka mengoordinasikan keputusan;
Yukino/Kiki dapat memakai disiplin yang relevan bagi ide atau proyek UI/kreatif.

```text
msshi integrations source --home HERMES_ROOT --name mattpocock-skills
msshi integrations source --home HERMES_ROOT --name mattpocock-skills --fetch
msshi integrations source --home HERMES_ROOT --name mattpocock-skills --list
msshi integrations source --home HERMES_ROOT --name mattpocock-skills --skill tdd
```

Default/status/list/read tidak mengunduh atau menjalankan model. Cache berada di luar
pemindai skill; baca satu entrypoint dan referensi yang dibutuhkan, bukan semua koleksi.
`--list` menyatakan `explicit_only` dan `in_progress`. Bahan in-progress dipakai hanya
ketika secara sengaja diminta dan ditinjau, bukan sebagai standar diam-diam.

Disiplin model-invoked seperti TDD, domain-modeling, diagnosing-bugs, codebase-design,
research dan writing-for-agents dapat dipilih menurut konteks. Hormati frontmatter
`disable-model-invocation: true`: grill-me, to-spec, triage, implement-spec dan
orkestrator lain bukan alasan memulai wawancara, publikasi atau perubahan source
tanpa permintaan pengguna. Nama slash upstream hanya dapat dipakai bila host benar-benar
mendaftarkannya; pada Hermes wrapper ini dapat diminta melalui percakapan biasa.

Defaultkan hasil ke draf/spec/proposal lokal ketika target publikasi belum diminta.
`to-spec` upstream dapat menerbitkan issue, dan setup dapat menyentuh tracker/label;
gunakan tindakan itu hanya dalam lingkup yang telah diotorisasi. Pertahankan provider,
model, SOUL, MoA, memori dan kustomisasi. Tidak ada pengujian atau hook otomatis pada boot.

Source MIT, hak cipta Matt Pocock; lisensi disertakan sebagai LICENSE.upstream.
