# Optional KAT for Shikaku (Coder)

KAT is an optional **Coder subtask model**, never a replacement for your current primary, MoA or ordinary delegation models. Goose is an external coding agent, not an MoA model ID. Nothing in this setup downloads model weights or starts a model server.

## Choose the actual model and endpoint

| Choice | Endpoint / model | Prerequisites |
| --- | --- | --- |
| Exact open-weight Dev | `Kwaipilot/KAT-Coder-V2.5-Dev`; your OpenAI-compatible deployment URL | A deployment that actually serves this model. Hugging Face lists no Inference Provider for it as checked on 16 November 2026. A model repository URL is not an API endpoint. |
| Official StreamLake pay-as-you-go | `https://vanchin.streamlake.ai/api/gateway/v1/endpoints`; `kat-coder-pro-v2.5` | Your StreamLake account/key and billing. **Pro v2.5 is a different variant from Dev.** DataByte/OpenRouter credentials do not authenticate this service. |
| Keep existing setup | No endpoint added | Coder continues using its current models. |

Sources: [official Dev model card](https://huggingface.co/Kwaipilot/KAT-Coder-V2.5-Dev), [official StreamLake tool integration guide](https://www.streamlake.ai/document/DOC/mg6k6nlp8j6qxicx4c9). Service offerings can change; verify the selected deployment's model catalog. The Dev weights contain 35B total / 3B active parameters: active parameters alone do not determine RAM use. A 16 GB laptop is not certified to host it.

## Configure from a terminal

Use your real Hermes root; the paths below are examples. The five-profile preset creates the named `shikaku` profile and native routing plugin first.

```powershell
msshi coder --home "D:\HermesData" presets
msshi coder --home "D:\HermesData" wizard
msshi coder --home "D:\HermesData" status
```

Selecting KAT in `msshi setup` now invokes this endpoint wizard. Legacy `--kat-mode light`, `ideal` and `cloud` open the same wizard; they no longer imply an automatically installed quantized model. Non-interactive selection prepares a disabled Dev record instead of inventing an endpoint or prompting for a secret.

For an explicitly selected official **Pro** endpoint, a direct command is also available:

```powershell
msshi coder --home "D:\HermesData" configure --preset streamlake-payg --read-key --probe --accept-documented-model --activate
```

`--read-key` asks privately in the terminal; never put the key in a command argument, chat, Git commit or screenshot. `--probe` only requests `GET /models`, with no chat/inference call. Some services do not expose a catalog; `--accept-documented-model` explicitly accepts only the exact official Pro preset model and URL. It cannot bless an arbitrary custom model.

For an exact Dev deployment, choose it in the wizard and supply its real URL. The model must match a returned catalog ID. No fallback to a different model occurs.

## What becomes active

Private state: `HERMES_ROOT/msshi-private/coder/kat.json`. The secret is referenced by `MSSHI_KAT_API_KEY`, stored only in Coder's private `.env` when entered through the wizard. Existing `.env` content is retained and backed up; `config.yaml` and `SOUL.md` are untouched by this helper.

The native `msshi-team` delegation provider exposes `execution: kat` **only inside Shikaku**, when the feature is enabled, the key exists and the selected model has catalog/documentation evidence. A named-profile handoff to Shikaku still uses Shikaku's own primary model. Shikaku may then choose KAT for an explicitly requested coding subtask without also specifying a named profile. Start a new session after configuring it so the host rebuilds its tool schema.

`ready_for_requested_task` describes configuration readiness. `inference_tested: false` remains explicit until a separately authorized real task succeeds; configuration/metadata checks do not prove model quality, account balance or successful generation.

```powershell
msshi coder --home "D:\HermesData" disable
```

Disabling KAT retains the existing primary/delegation models and saved endpoint choices. It starts no processes and spends no inference credits.


## Goose remains a separate optional agent

Install the official CPU/standard CLI following the [official Windows installer](https://github.com/aaif-goose/goose/blob/main/download_cli.ps1). Use `GOOSE_BIN_DIR` for a chosen data-drive folder and `CONFIGURE=false` to install the binary without invoking account/model setup. Goose does not require a CUDA model download to call a remote API. Configure its provider/key in an isolated Goose config only when you choose to use it; never write Goose's provider variables into Hermes config.

`msshi coder status` reports whether its executable exists, separately from KAT readiness. A Goose binary alone is not proof its provider is configured. No Goose model/API session is started by MSSHI setup or this status check.
