---
name: academic-plotting
description: "Generates publication-quality figures for ML papers (Workflow 1: Gemini architecture diagrams; Workflow 2: matplotlib/seaborn data charts with Ocean Dusk & Okabe-Ito palettes)."
---

# academic-plotting

Generates publication-quality figures for ML papers (Workflow 1: Gemini architecture diagrams; Workflow 2: matplotlib/seaborn data charts with Ocean Dusk & Okabe-Ito palettes).

## Workflow

1. Identify the figure’s claim, panel type, source data, units, uncertainty definition and target publication constraints. Ask for missing values. Never fill them from visual intuition.
2. For an architecture diagram, list every block, tensor or data flow from the supplied method and source. Draw labeled arrows and a legend. Use a configured diagram tool if authorized, or create editable SVG locally.
3. For a data chart, use a reproducible Matplotlib or seaborn script. Label scales, include sample size and error-bar semantics, and choose Okabe–Ito or another color-safe palette with non-color encoding. Apply Ocean Dusk where contrast and publication rules allow it.
4. Export editable source plus vector PDF/SVG or a raster at the requested resolution. Verify figure at final size, axis values against input, font embedding or legibility, and caption semantics. Record any unverified detail.
