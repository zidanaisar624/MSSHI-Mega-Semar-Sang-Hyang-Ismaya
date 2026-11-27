---
name: meshy-3d-generation
description: Generasi model 3D dari teks atau gambar (GLB, FBX, OBJ, USDZ), penteksturan, remeshing, rigging/animasi, dan persiapan cetak 3D melalui Meshy CLI (meshy-cli@0.8) & Meshy 3D Agent untuk Kiki-Chii dengan alur sign-in device code satu kali.
license: MIT
metadata:
  upstream: https://github.com/meshy-dev/meshy-3d-agent
  upstream_commit: 7f8e33196db4e9e26cbaa0da4fcc14104ccda81d
  cli_package: "meshy-cli@0.8"
  activation: contextual-opt-in-kiki-3d
---

# Generasi & Pencetakan Model 3D Meshy (`meshy-3d-generation`)

Gunakan skill opt-in ini pada peran **Content Creator (`kiki-chii`)** maupun **Solo / Antigravity** ketika pengguna meminta pembuatan aset 3D (`GLB`, `FBX`, `OBJ`, `USDZ`, atau persiapan *3D printing* `STL`/`3MF`) dari deskripsi teks ataupun gambar referensi menggunakan **Meshy AI**.

## 1. Prasyarat Runtime & Pemberitahuan Paket Berbayar

1. **Node.js `>= 22.12`** dan **`meshy-cli@0.8`** (`npm install -g meshy-cli@0.8`, atau panggil lewat `npm exec --yes --package=meshy-cli@0.8.6 -- meshy ...`).
2. **Pemberitahuan Penting Sebelum Login**: Pembuatan tugas generasi 3D di Meshy memerlukan paket berbayar (**Meshy Pro atau di atasnya**). Akun *Free* tetap dapat *sign-in* dan mengecek saldo, tetapi pembuatan tugas generasi akan ditolak API dengan `HTTP 402 plan_upgrade_required` (exit code `9`). Sampaikan informasi ini secara jujur kepada pengguna sebelum menjalankan alur *sign-in*.

## 2. Alur Autentikasi *Device Flow* (Tampilkan Tautan & Kode Satu Kali)

Jangan pernah meminta pengguna menempelkan API key mentah ke kolom percakapan. Gunakan alur resmi *device code*:

1. Periksa status login tanpa memeriksa update otomatis:
   ```bash
   meshy auth status --format json --no-update-check
   ```
2. Bila belum `"authenticated": true`, jalankan login perangkat:
   ```bash
   meshy auth login --device --format json --no-update-check
   ```
3. Dalam beberapa detik CLI akan mencetak baris pada `stderr` seperti:
   ```text
   Enter code WXYZ-1234 at https://www.meshy.ai/device
   ```
   **Wajib tampilkan tautan (`https://www.meshy.ai/device`) dan kode satu kali (`WXYZ-1234`) persis seperti yang tercetak kepada pengguna**, lalu biarkan proses CLI menunggu hingga pengguna menyetujui di browser (berlaku 10 menit; jangan memulai login kedua secara paralel).
4. Setelah disetujui, periksa saldo kredit tanpa membelanjakan apa pun:
   ```bash
   meshy balance --format json --no-update-check
   ```

## 3. Alur Kerja Produksi 3D & Sinergi Lintas-Alat

1. **Concepting First**: Sepakati siluet objek, gaya permukaan (*realistic*, *stylized*, *low-poly*, *PBR*), target poligon, format ekspor (`GLB`/`FBX`/`OBJ`/`USDZ`/`STL`), dan estimasi kredit sebelum membuat tugas berbayar.
2. **Eksekusi & Pratinjau**: Jalankan generasi *text-to-3d* atau *image-to-3d*, pantau hingga selesai, unduh model ke workspace proyek, dan tawarkan pratinjau (`meshy view` bila didukung lingkungan lokal).
3. **Sinergi dengan `mcp-for-blender` & `raea`**: File `.glb` / `.fbx` hasil Meshy dapat langsung diteruskan ke Blender (`--with-blender-mcp`) untuk tata adegan/kamera atau ke `raea` (`--with-raea`) untuk komposisi motion video real-time.

Rujukan hulu resmi: [`meshy-dev/meshy-3d-agent`](https://github.com/meshy-dev/meshy-3d-agent) (`7f8e33196db4e9e26cbaa0da4fcc14104ccda81d`) dan [`meshy-dev/meshy-cli`](https://github.com/meshy-dev/meshy-cli). Wrapper MSSHI ini 100% teks orisinal berlisensi MIT.
