---
name: mcp-for-blender
description: Integrasi opsional MCP for Blender (ahujasid/mcp-for-blender) khusus Kiki-Chii (Content Creator / Filmmaker) untuk pemodelan 3D interaktif dua arah, material, pencahayaan, kamera previz, dan ekspor .glb/.gltf on-demand (public_default false, auto_open_on_boot false).
license: MIT
metadata:
  upstream: https://github.com/ahujasid/mcp-for-blender
  upstream_commit: a5a8acf2c6ae44a73670e0caf34663f16456d645
  upstream_license: MIT
  activation: opt-in-creative-3d-blender-mcp
---

# MCP for Blender (`ahujasid/mcp-for-blender` — Opsional Khusus Kiki-Chii)

Integrasi **opsional** ini dimiliki oleh **Kiki-Chii (`kiki-chii` — Content Creator / Filmmaker)** dengan **`public_default: false`** dan **`auto_open_on_boot: false`**. Wrapper ini hanya terpasang bila dipilih eksplisit saat setup (`--with-blender-mcp`) atau melalui:

```text
msshi optional enable mcp-for-blender --target-dir PATH_TO_SKILLS
```

Pada `MSSHI v3.2.0`, rute Blender **diputus dari `cli-anything`** (seluruh 46 aplikasi lain di `cli-anything` tetap utuh) dan dialihkan ke protokol dua arah **MCP for Blender** (`ahujasid/mcp-for-blender`, sebelumnya dikenal sebagai `blender-mcp`) agar Kiki-Chii dapat menginspeksi *scene*, memodifikasi objek/material/kamera, serta mengekspor aset 3D `.glb`/`.gltf` secara presisi hanya ketika diminta.

## 1. Prasyarat & Setup 2 Langkah oleh Pengguna (On-Demand)

MSSHI tidak pernah menyalakan Blender saat boot atau mengunduh paket diam-diam. Saat pengguna ingin memakai Blender 3D interaktif:

1. **Pasang Addon Socket di Blender (3.0+)**:
   - Unduh `addon.py` dari repositori resmi `https://github.com/ahujasid/mcp-for-blender` (commit terpin `a5a8acf2c6ae44a73670e0caf34663f16456d645`).
   - Buka *Blender -> Edit -> Preferences -> Add-ons -> Install...*, pilih `addon.py`, centang **Interface: Blender MCP**, lalu klik **Connect to MCP server** pada panel sidebar `N` (*BlenderMCP*) hanya saat sesi kerja 3D aktif.
2. **Daftarkan Server MCP Stdio (`uvx`) di Profil `kiki-chii`**:
   - Pastikan `uv` terpasang, lalu tambahkan entri `blender` pada `mcp_servers` profil `kiki-chii` menjalankan `uvx mcp-for-blender` (atau alias kompatibel `uvx blender-mcp`).

## 2. Alur Kerja Sinematik Kiki-Chii & Sinergi dengan `raea`

1. **Concepting First (`filmmaking-videography-photography-s2`)**: Kunci *shot list*, panjang fokus lensa (`24mm`/`35mm`/`50mm`/`85mm`), dan rasio pencahayaan sebelum memanipulasi *scene* Blender.
2. **Inspeksi Sebelum Eksekusi**: Selalu baca info *scene*/objek terlebih dahulu sebelum mengubah geometri atau menjalankan skrip Python di Blender; simpan cadangan `.blend` sebelum operasi destruktif.
3. **Aset Eksternal Berizin**: Unduhan Poly Haven, Sketchfab, atau generasi 3D (Hyper3D Rodin / Hunyuan3D) memerlukan persetujuan eksplisit pengguna serta pemeriksaan lisensi aset.
4. **Jembatan Hibrida ke `optional/raea` (Render Anything Engine)**:
   - Untuk *motion/product film* hibrida, rakit & haluskan model/rigging/material 3D di Blender lewat `mcp-for-blender`, ekspor ke **`.glb` / `.gltf`**, lalu teruskan ke **`optional/raea`** (jika diaktifkan pengguna) untuk komposisi *shader*, tipografi sinematik, dan *rendering* GPU akhir.
   - Pada perangkat **Low-RAM (<= 6 GB / Mode Hemat Windows 10 4 GB)**, jangan menjalankan Blender lokal; arahkan ke alur ringan berbasis kode (`brag` / Hyperframes) atau perencanaan storyboard.

Wrapper MSSHI ini 100% **model-agnostic** (`0` perubahan pada model/provider/`SOUL.md`). Lisensi upstream: **MIT License** (Copyright (c) 2025 Siddharth Ahuja, disimpan di `LICENSE.upstream`).
