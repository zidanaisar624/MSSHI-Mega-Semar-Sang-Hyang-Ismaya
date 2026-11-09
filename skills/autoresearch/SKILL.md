---
name: autoresearch
description: Orchestrates end-to-end autonomous AI research projects using a two-loop architecture (fast inner loop for experiments + reflective outer loop for synthesis into findings.md).
---

# autoresearch

Orchestrates end-to-end autonomous AI research projects using a two-loop architecture (fast inner loop for experiments + reflective outer loop for synthesis into findings.md).

## Alur kerja

1. Tetapkan satu hipotesis dan metrik beserta baseline, batas waktu, data dan anggaran.
2. Untuk tiap eksperimen yang disetujui, catat perubahan tunggal, seed, komando, hasil, dan kondisi berhenti.
3. Tulis `findings.md` dengan hasil, ketidakpastian, dan eksperimen lanjutan yang perlu persetujuan.
