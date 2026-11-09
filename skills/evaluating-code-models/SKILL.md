---
name: evaluating-code-models
description: Evaluates code generation models across HumanEval, MBPP, MultiPL-E (18 languages), APPS, and DS-1000 with pass@k metrics.
---

# evaluating-code-models

Evaluates code generation models across HumanEval, MBPP, MultiPL-E (18 languages), APPS, and DS-1000 with pass@k metrics.

## Alur kerja

1. Pilih benchmark dan commit evaluator. Tentukan isolasi eksekusi dan cegah akses jaringan atau rahasia dari kode kandidat.
2. Catat konfigurasi sampling, `n`, `k`, batas waktu dan lingkungan. Jalankan kandidat hanya setelah lingkungan dan biaya diperiksa.
3. Laporkan pass@k dengan ukuran sampel dan jenis kegagalan. Bandingkan hanya setup yang setara.
