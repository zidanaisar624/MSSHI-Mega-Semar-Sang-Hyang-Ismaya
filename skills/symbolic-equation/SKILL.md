---
name: symbolic-equation
description: Discovers interpretable scientific equations from data using LLM-guided evolutionary search (LLM-SR).
---

# symbolic-equation

Discovers interpretable scientific equations from data using LLM-guided evolutionary search (LLM-SR).

## Alur kerja

1. Tentukan variabel, unit, domain fisik dan bentuk fungsi yang masuk akal.
2. Pisahkan train/validation/test sebelum menilai ekspresi. Batasi kompleksitas dan hindari operator ilegal.
3. Bandingkan akurasi, interpretabilitas dan perilaku batas terhadap baseline. Laporkan ketidakpastian.
