---
name: phoenix-observability
description: Sets up Arize Phoenix OpenTelemetry tracing, LLM-as-judge evaluators, datasets, and experiments.
---

# phoenix-observability

Sets up Arize Phoenix OpenTelemetry tracing, LLM-as-judge evaluators, datasets, and experiments.

## Alur kerja

1. Pilih alur lokal atau server yang diizinkan. Tentukan span, metrik, data uji dan kebijakan penyimpanan.
2. Rancang trace OpenTelemetry, redaksi dan evaluator. Aktifkan ekspor hanya sesuai izin.
3. Verifikasi satu trace sintetis dan bandingkan evaluasi terhadap contoh berlabel.
