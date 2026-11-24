---
name: raea
description: Integrasi opsional RAEA — Render Anything Engine (shinyobjectz/raea) khusus Kiki-Chii (Content Creator / Filmmaker) untuk merender film/motion/3D berbasis kode React/TypeScript + Bevy GPU secara langsung maupun hibrida bersama aset .glb/.gltf dari mcp-for-blender (public_default false).
license: MIT
metadata:
  upstream: https://github.com/shinyobjectz/raea
  upstream_commit: 66eb15448f69ab29a801fe1bde75d3889d34d04e
  upstream_license: FSL-1.1-ALv2 (0 upstream bytes bundled in MSSHI)
  activation: opt-in-creative-render-engine
---

# RAEA — Render Anything Engine (`shinyobjectz/raea` — Opsional Khusus Kiki-Chii)

Integrasi **opsional** ini dimiliki oleh **Kiki-Chii (`kiki-chii` — Content Creator / Filmmaker)** dengan **`public_default: false`** dan **`auto_open_on_boot: false`**. Aktifkan hanya atas pilihan eksplisit pengguna saat setup (`--with-raea`) atau melalui:

```text
msshi optional enable raea --target-dir PATH_TO_SKILLS
```

> **Peringatan Penting Anti-Tertukar (`raea` vs `rea`)**:
> - **`optional/raea`** (`shinyobjectz/raea`) adalah **Render Anything Engine** milik **Kiki-Chii** untuk merender video, motion graphics, shader, dan adegan 3D berbasis kode (React/TypeScript + Rust Bevy GPU).
> - **`optional/rea`** (`morluto/rea`) adalah alat **Reverse Engineer Anything** (analisis statis binari/JS) milik **Coder (`shikaku`)**. Jangan pernah mencampuradukkan keduanya!

## Dua Mode Produksi RAEA pada Kiki-Chii

Setelah *Concepting First* (`filmmaking-videography-photography-s2`) disetujui manusia, Kiki-Chii dapat menjalankan RAEA dalam dua mode:

1. **Mode 1 — Direct Code-to-GPU Render (Tanpa Blender)**:
   - Model AI pilihan pengguna di Hermes menulis adegan deklaratif (React/TypeScript, kamera, tata cahaya, animasi kurva, partikel/shader, audio sync) untuk dirender langsung ke video melalui engine GPU Bevy milik RAEA yang dipasang terpisah oleh pengguna.
2. **Mode 2 — Hybrid 3D Finishing (`mcp-for-blender` -> `.glb`/`.gltf` -> `raea`)**:
   - Gunakan **`optional/mcp-for-blender`** saat proyek membutuhkan *sculpting*, *boolean/modifier* kompleks, atau *rigging* di Blender.
   - Ekspor aset matang ke **`.glb` / `.gltf`**, lalu impor ke proyek RAEA untuk penataan kamera gerak presisi, pencahayaan PBR/post-processing GPU, tipografi gerak, dan ekspor video akhir.

## Kejujuran Perangkat Keras (GPU/RAM) & Lisensi Terpisah

- **Kebutuhan Perangkat Keras**: Engine RAEA membutuhkan GPU kompatibel (Vulkan / Metal / DX12) serta toolchain Rust/Cargo + Node/Bun yang dipasang sendiri oleh pengguna di luar MSSHI.
- **Fallback Ramah Low-RAM (<= 6 GB / Laptop Tanpa GPU Diskrit)**: Jangan memaksakan kompilasi/render Bevy lokal pada mode Low-RAM; alihkan dengan mulus ke komposisi ringan berbasis HTML/Canvas (`brag` / Hyperframes) atau draf naskah & *storyboard*.
- **Batas Lisensi Upstream (`FSL-1.1-ALv2`)**: Repositori upstream `shinyobjectz/raea` berlisensi **Functional Source License 1.1, ALv2 Future License** (Copyright 2026 Shane Murphy; berubah otomatis menjadi Apache-2.0 setelah dua tahun per rilis, dengan batasan layanan komersial bersaing selama masa FSL). **MSSHI tidak menyalin atau memaketkan 1 byte pun kode/aset `raea` ke dalam repositori MIT ini**; wrapper instruksi ini 100% ditulis orisinal (MIT) dan tetap sepenuhnya **model-agnostic** (`0` perubahan pada `config.yaml`, provider, model, atau `SOUL.md`).
