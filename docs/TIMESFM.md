# TimesFM for Val / TimesFM untuk Val

TimesFM is Google's pretrained numeric time-series forecasting model. MSSHI adds an **on-demand local CPU tool**, with Val as its research owner. It does not replace the chat model, add an MCP server, start at login, or use Hermes/API credits. Internet download and local disk/RAM/electricity still have a cost.

TimesFM adalah model peramalan deret waktu numerik. Val menggunakannya ketika konteks tugas memerlukan prediksi dan data yang sesuai, setelah interval, variabel, horizon, serta kebijakan data hilang dipastikan. Percakapan biasa tidak memuat model ini.

## Version and license decision

The upstream repository currently presents TimesFM 3.0, but the downloaded 3.0 pretrained weights are **non-commercial and non-production**. This package intentionally uses **TimesFM 2.5 200M** (231,289,280 parameters including forecast heads), whose code and weights are Apache-2.0. It does not enable BigQuery, Vertex, or any paid cloud service. See the [official license notice](https://github.com/google-research/timesfm#license-notice-for-pretrained-weights) and [2.5 model card](https://huggingface.co/google/timesfm-2.5-200m-pytorch).

Pinned source: `e51928e27119cb17bebc005be2696b75e0a9e688` from `google-research/timesfm` (package reports 3.0.2 and retains the 2.5 API).

Pinned checkpoint: `1d952420fba87f3c6dee4f240de0f1a0fbc790e3` from `google/timesfm-2.5-200m-pytorch`.

`model.safetensors`: 925,181,104 bytes; SHA-256 `2f776efe6245e42b24bc4153ffdf61810140210e4bd3b01fb21f7aa779ab6ce8`.

## Commands

```powershell
msshi timesfm status
msshi timesfm install
msshi timesfm smoke
msshi timesfm forecast --input C:\work\series.json --output C:\work\forecast-new.json --horizon 12
msshi timesfm status --verify
```

The standalone equivalent is `python scripts/msshi_timesfm.py --hermes-home D:\HermesData <action>`. Hermes can call the lightweight copy in Val's `skills/timesfm-forecasting/scripts/` through its normal terminal tool. Public installations should substitute their own Hermes root; profile paths such as `<root>/profiles/val` resolve to the shared runtime root.

The local validation target is Windows x64 with Python 3.12. The explicit CPU-wheel installer has not been verified on other OS/architectures; macOS and unsupported CPU-wheel platforms need an adapted dependency installation. General MSSHI portability does not imply that this optional numeric runtime was tested everywhere.

Example input (32 equally spaced observations):

```json
{"series": [[10, 11, 12, 13, 12, 11, 10, 11, 12, 13, 14, 13, 12, 11, 12, 13, 14, 15, 14, 13, 12, 13, 14, 15, 16, 15, 14, 13, 14, 15, 16, 17]]}
```

`smoke` creates a valid 64-point synthetic series automatically.

## Runtime boundaries

- `<Hermes-root>/msshi-private/timesfm-runtime/venv/`: separate Python environment, CPU PyTorch `2.8.0+cpu`; OmniVoice and the Hermes environment are untouched.
- `model/`: pinned model/config/model card. Model files are excluded from the public ZIP and skill scanner.
- `INSTALLATION.json`: package inventory, source/model provenance, weights checksum, and last smoke result.
- Forecasting sets Hugging Face offline mode and disables CUDA/telemetry. No account or token is needed for the public checkpoint.
- Bounds: 1–4 independent univariate series, 32–1024 values, horizon 1–128, 1 MiB JSON input, two CPU threads, one inference at a time, 300-second child timeout, no output overwrite.
- Windows workers are launched suspended, assigned to a kill-on-close Job Object, then resumed; this owns venv redirector descendants too. Unix workers use a private process group. Timeout/exit cleanup applies only to the worker tree, never to unrelated applications.
- `status` does not import PyTorch or load weights. `status --verify` reads the large model file to recompute SHA-256.
- Install/download needs internet access and several GB of free disk. Real RAM/time depend on hardware and context. These are modest input limits, not an OS memory quota.
- Before model loading, Windows must report at least 2.5 GiB of available system commit (physical memory plus pagefile-backed capacity). The result records available physical and commit memory. This preflight is not a RAM ceiling; Windows can still page if physical memory is low. The tool refuses insufficient commit and does not close other applications.

The wrapper emits raw forecasts, ten quantile channels, revision, and timing. Backtesting, frequency handling, missing-data preparation, and baseline comparison remain explicit analysis steps; no automatic accuracy or savings promise is made. The installed smoke result proves executable compatibility only. Output is experimental and must not be treated as guaranteed events or financial advice.

The wrapper disables Torch compilation and flip-invariance averaging for a smaller CPU workload. It does not infer non-negativity from positive history or silently clamp predictions. Review model options and apply any domain constraints explicitly during analysis.

## Maintenance / rollback

Normal skill updates replace only managed lightweight wrappers. They do not silently change a pinned model, download model weights, or modify user data. Run explicit `install` after reviewing a model/runtime change. `install` refuses an unowned or mismatched runtime. After shutdown, the wrapper recovers an old `install.lock` / `forecast.lock` only after the OS confirms that its recorded process no longer exists. An unverifiable lock fails safely and needs inspection; active locks are never removed.

Disable the skill by removing its managed Val skill directory after saving any custom edits. Runtime data can be archived separately after all TimesFM processes have exited. No provider/model or SOUL rollback is necessary because this integration does not edit those files.
