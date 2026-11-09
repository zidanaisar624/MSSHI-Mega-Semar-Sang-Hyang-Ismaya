---
name: langsmith-observability
description: Configures LangSmith tracing, dataset evaluation, CI/CD regression testing, and production monitoring for LLM applications.
---

# langsmith-observability

Configures LangSmith tracing, dataset evaluation, CI/CD regression testing, and production monitoring for LLM applications.

## Alur kerja

1. Petakan alur, metrik dan titik kegagalan yang akan dipantau. Pilih data uji sintetis atau yang sudah disamarkan.
2. Rancang trace, evaluasi, dan aturan redaksi. Konfigurasi layanan eksternal hanya setelah persetujuan.
3. Uji satu trace dan satu evaluasi. Pastikan payload dan kunci tidak bocor sebelum menjalankan batch.
