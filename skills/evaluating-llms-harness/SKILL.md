---
name: evaluating-llms-harness
description: Evaluates LLMs across 60+ academic benchmarks (MMLU, GSM8K, HellaSwag, TruthfulQA, ARC) using EleutherAI lm-evaluation-harness.
---

# evaluating-llms-harness

Evaluates LLMs across 60+ academic benchmarks (MMLU, GSM8K, HellaSwag, TruthfulQA, ARC) using EleutherAI lm-evaluation-harness.

## Alur kerja

1. Pilih task dan versi dataset, pastikan ketersediaan evaluator, lisensi, dan kompatibilitas backend.
2. Tentukan few-shot, seed, template prompt, batch size, batas contoh dan metrik. Mulai dari subset lokal.
3. Laporkan konfigurasi efektif, metrik per task, error, dan risiko kontaminasi.
