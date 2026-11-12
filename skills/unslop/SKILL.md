---
name: unslop
description: Tinjau dan poles layar UI yang tampak generik berdasarkan produk dan bukti visual. Gunakan untuk permintaan unslop, audit atau perbaikan dashboard, aplikasi, dan landing page; bukan penyuntingan prosa umum atau perubahan gaya persona.
license: CC-BY-4.0
metadata:
  author: Damir Sokolovsky
  upstream: https://github.com/heydamir/unslop
  upstream_commit: 97daa3eb365670ea3f87ed85356cbfcee18105a5
  adaptation: MSSHI v3.1
---

# Unslop untuk Hermes

Adaptasi ringkas dari [Unslop karya Damir Sokolovsky (@heydamir)](https://github.com/heydamir/unslop/tree/97daa3eb365670ea3f87ed85356cbfcee18105a5), berlisensi [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Teks lisensi dan penafian tersedia di [LICENSE](LICENSE). MSSHI mengubah petunjuk menjadi alur UI kontekstual, membatasi peran, dan tidak menyertakan skrip atau aset upstream. Adaptasi ini tidak menyiratkan dukungan dari pembuat upstream.

## Kapan dan siapa

Aktifkan saat tugas menyangkut tampilan layar, hierarki, keterbacaan, atau UI yang perlu dipoles. Permintaan langsung `unslop layar ini` dapat memilih alur ini. Dalam pekerjaan UI yang sedang berlangsung, gunakan pemeriksaan yang relevan secara kontekstual; jangan membuka proyek desain baru hanya karena sebuah jawaban menyebut dashboard.

- **Kiki-Chii:** audit visual, karakter produk, komposisi, art direction, dan brief perbaikan.
- **Val:** evaluasi dashboard sains/data: makna grafik, unit, label sumbu, legenda, periode dan pembanding, sumber, ketidakpastian, serta keterbacaan. Pertahankan peran riset; serahkan implementasi frontend kepada Coder bila dibutuhkan.
- **Coder:** telusuri komponen/CSS dan terapkan perubahan UI yang masuk lingkup tugas; periksa hasil render dan perilakunya.

Skill ini tidak mengubah persona, bahasa, nada pengguna, atau gaya percakapan. Penyuntingan copy hanya berlaku pada teks antarmuka yang ditinjau. Gunakan humanizer atau match-my-writing-style hanya bila tugas memang memerlukan penyuntingan prosa. Jika antislop sudah memimpin pekerjaan UI, gunakan Unslop sebagai alur diagnosis dan perbaikan layar yang sama, tanpa menggandakan gate, mengubah mode, atau menimpa preferensinya. Brief dan sistem desain yang dipilih pengguna tetap menjadi dasar keputusan.

## Alur layar

1. Lihat layar atau screenshot dan temukan sumbernya jika tersedia. Catat bagian yang tidak dapat diamati. Untuk URL tanpa kode, hasilkan audit atau prototipe lokal yang diberi label jelas; jangan menganggap situs produksi sudah berubah. Gunakan browser/screenshot native yang sudah tersedia.
2. Susun temuan konkret: lokasi, masalah yang terlihat, akibat bagi pengguna, dan perbaikan terkecil. Cari ritme jarak yang tidak konsisten, warna tanpa makna, dekorasi yang bersaing, hierarki tipografi lemah, ikon campuran, copy kabur, kontrol tidak jelas, dan gerakan tanpa tujuan. Gradien atau warna tertentu bukan otomatis kesalahan jika punya fungsi atau identitas yang disengaja.
3. Tentukan tingkat intervensi. Layar yang sudah baik cukup diberi temuan kecil atau dinyatakan baik. Pada polish ringan, pertahankan layout, palet, font, dan aset; ubah bagian yang terbukti bermasalah. Untuk redesign luas, jelaskan arah ringkas dari produk, audiens, karakter, dunia/material visual, satu atau dua fokus konten, dan satu detail khas. Gunakan arah yang sudah disepakati; bila pengguna telah mengizinkan pengerjaan mandiri, lanjutkan perubahan yang relevan tanpa meminta konfirmasi berulang.
4. Untuk implementasi yang diminta, kerjakan lapisan yang diperlukan dalam urutan: **jarak, warna, ikon, copy, tipografi, layout, detail kontrol/grafik, visual, gerak**. Pertahankan fitur, data, urutan konten, merek, dan maksud pengguna kecuali perubahan itu memang diminta. Jangan memaksa sembilan pass jika hanya satu masalah perlu diperbaiki.
5. Bandingkan hasil dengan temuan awal. Coder memeriksa breakpoint relevan, fokus keyboard, kontras, overflow, dan kontrol yang berubah menggunakan alat serta pemeriksaan proyek yang tersedia. Laporkan perubahan dan batas verifikasi dengan bukti yang benar-benar diamati.

## Keputusan yang menjaga kualitas

- Gunakan skala jarak konsisten, ukuran berulang yang selaras, dan hierarki yang mudah dipindai. Ambil token dari proyek; jangan mengganti sistem desain dengan token universal.
- Jadikan navigasi dan kontrol cukup tenang agar konten utama terbaca. Warna semantik dan beberapa seri grafik boleh memakai warna berbeda ketika maknanya jelas dan tetap dapat dibedakan tanpa warna saja.
- Pertahankan copy, angka, kutipan, klaim, dan istilah yang memiliki makna. Jangan mengarang pelanggan, fitur, metrik, testimoni, atau hasil ilmiah. Tandai data demo sebagai demo; dashboard riset memakai data dan sumber aslinya.
- Untuk Val, kejelasan bukti mendahului pengurangan dekorasi: jangan hilangkan seri, error bar, CI, unit, baseline, peringatan, atau presisi yang diperlukan agar layar terlihat lebih sederhana. Usulkan jenis grafik berdasarkan pertanyaan dan struktur datanya.
- Gunakan visual produk yang nyata dan aset yang sudah diizinkan. Jangan mengaktifkan layanan gambar, menambah MCP, mengunduh model, atau memulai generasi berbayar sebagai efek samping audit. Video before/after hanya jika diminta dan alat yang diperlukan tersedia.
- Hormati kebutuhan aksesibilitas dan preferensi reduced motion. Pertahankan detail ekspresif yang disengaja; tujuan alur ini adalah keputusan desain yang beralasan, bukan menyeragamkan semua layar.
