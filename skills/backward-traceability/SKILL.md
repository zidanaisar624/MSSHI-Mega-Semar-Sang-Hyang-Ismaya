---
name: backward-traceability
description: Makes every number in the final PDF traceable to the exact code line that produced it using LaTeX \hypertarget, \hyperlink, and compile-time \num{formula} evaluation.
---

# backward-traceability

Makes every number in the final PDF traceable to the exact code line that produced it using LaTeX \hypertarget, \hyperlink, and compile-time \num{formula} evaluation.

## Alur kerja

1. Buat daftar semua angka pada tabel, grafik dan klaim naratif.
2. Petakan setiap angka ke file data, filter, fungsi dan parameter penghasilnya. Gunakan ID stabil untuk rujukan silang LaTeX.
3. Uji satu contoh dari keluaran ke data dan balik lagi. Tandai angka yang masih manual.
