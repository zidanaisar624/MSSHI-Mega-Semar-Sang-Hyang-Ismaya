---
name: notebooklm-thinking-datascience
description: Applies thinking models, systems analysis, and reproducible data science to sources the user has authorized from NotebookLM or another knowledge base.
---

# NotebookLM thinking and data science

Use this skill when a task requires reasoning from a supplied collection, modeling a system, or designing a data-science workflow. Work from the notebook sources the user has shared or a permitted export. The public bundle provides the method and example index, while private notebook collections stay with their owners.

## 1. Prepare a source index

Create an entry per source with an ID, title, date, version, and permitted source pointer. Mark summaries separately from originals. Link claims to source IDs and page/section pointers. If a source is missing, ask for it or identify the gap before forming a conclusion.

## 2. Select a thinking tool

- Use first principles to separate requirements from assumptions.
- Use an iceberg or causal-loop diagram to distinguish events, patterns, and feedback.
- Use the Ladder of Inference to show what was observed versus what was inferred.
- Use OODA or a small decision table to compare reversible next steps.
- For socio-informatics, check access, intended benefits, unintended effects, incentives, privacy, and stakeholder accountability.

Choose one or two tools appropriate to the question. Return the assumptions, relevant evidence, and the decision they inform.

## 3. Plan data analysis

1. Describe the unit of observation, outcome, time order, and evaluation goal.
2. Choose the split to match the data-generating process. Keep related records together and use temporal splits for time-dependent targets where appropriate.
3. Fit vectorization, scaling, imputation, and resampling on training folds only. Keep tuning and final evaluation separate. For ML experiments use a baseline before more complex models.
4. Record dataset versions, preprocessing, seeds, and metrics. Check class imbalance, uncertainty, and limits of generalization.
5. Hand the source pointers, analysis choices, and caveats to Val or Shizuka. Preserve the distinction between reported and independently reproduced results.

Example source entry:

```json
{"id":"S01","title":"Authorized reading","version":"v1","locator":"project-sources/reading.pdf#p12","claim":"Add a verified observation here"}
```

Use an example source and a small experiment to verify the workflow before processing a large corpus.
