---
name: timesfm-forecasting
description: Val's on-demand local TimesFM 2.5 CPU forecasting for regularly spaced numeric time series. Use when the task needs a future horizon, chronological backtesting, demand/pageview/usage forecasting, or comparisons with naive and seasonal baselines. Does not change Hermes' conversational model and never starts on boot.
---

# TimesFM forecasting — Val

Use this skill in response to a forecasting task. Do not run it for ordinary conversation, generic literature review, startup, or idle activity. TimesFM is a separate numeric model, not a chat provider. This wrapper intentionally selects the Apache-2.0 TimesFM **2.5** checkpoint. Downloaded TimesFM 3.0 weights have different non-commercial, non-production terms and must not be substituted silently.

## Intake before inference

Confirm the target variable and units, observation interval, timestamp ordering, missing-data policy, desired horizon, and what decision the forecast supports. Ask only for missing material details. Prefer a local CSV/JSON supplied by the user; do not upload it or scrape a source without authorization. Never invent observations. Aggregate/reindex irregular timestamps explicitly, explain the operation, and request agreement when it changes meaning. Keep all preprocessing and a chronological holdout separate from the forecast inputs to avoid leakage.

## Execution

1. Run `msshi timesfm status`. It reads readiness only and does not load the model, open an application, call an API, or consume Hermes credits. If the global wrapper is unavailable, run `python <this-skill-directory>/scripts/msshi_timesfm.py status`.
2. If the runtime is missing, explain that setup downloads a CPU runtime and about **925 MB** of model weights (plus dependencies). Run `msshi timesfm install` only when installation is authorized. The files live outside `skills/`, under `<Hermes-root>/msshi-private/timesfm-runtime/`. Never put a venv, model cache, repository, or `node_modules` inside the skill scanner.
3. Write a new UTF-8 input JSON in the task workspace: `{"series":[[32 or more numeric observations]]}`. The wrapper accepts 1–4 univariate series, 32–1024 observations each, and a horizon of 1–128 steps. Values must be finite. A step is the user's observation interval; the model does not infer timestamps or units.
4. Run `msshi timesfm forecast --input <absolute-input.json> --output <new-absolute-result.json> --horizon 12`. The output must not exist. Inference is offline, CPU only, single active process, two computation threads, and a 300-second subprocess timeout. The process exits and releases the model afterward; do not schedule a background daemon.
5. Inspect point forecasts and quantiles, preserve the exact result artifact, and explain assumptions. Use a chronological holdout and compare with last-value / seasonal-naive baselines where the data permits. Report empirical error and limitations; do not claim that passing a synthetic smoke test establishes predictive accuracy. Probabilistic quantiles are model outputs, not guaranteed confidence coverage.

`msshi timesfm smoke` runs only a generated 64-point example, four-step forecast, and writes an audit. It makes no LLM calls or cloud inference requests. It is an explicit diagnostic, not something to run on each conversation.

## Collaboration and safety

Val owns research, data validation, benchmarking, and uncertainty reporting. Share the findings with Shizuka for synthesis or ask Shikaku for an approved data-preparation implementation. Other bots may delegate this capability to Val. Do not modify `provider`, chat `model`, fallback/MoA, SOUL/persona, memory, or creative DNA. Do not enable Google Cloud billing or remote model endpoints. Financial/medical forecasts require domain review and are not decisions or advice by themselves.

Source: [Google Research TimesFM](https://github.com/google-research/timesfm). Code commit: `e51928e27119cb17bebc005be2696b75e0a9e688`. Model: [google/timesfm-2.5-200m-pytorch](https://huggingface.co/google/timesfm-2.5-200m-pytorch), revision `1d952420fba87f3c6dee4f240de0f1a0fbc790e3`. Model and source: Apache-2.0. MSSHI wrapper: MIT; upstream attribution and licenses remain applicable.
