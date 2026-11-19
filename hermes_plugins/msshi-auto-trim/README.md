# MSSHITrim - automatic local JSON compaction for Hermes

This native plugin runs automatically on Hermes' supported
`transform_tool_result` hook. It uses `llmtrim compress`, never `send`,
MCP, a proxy, or a provider API. It changes no model or provider setting.

Only sufficiently large, valid JSON tool results are eligible. Every candidate
must decode to exactly the same canonical JSON as the original. If Llmtrim
converts data to TOON, drops values, changes text inside a JSON string, times
out, or fails, Hermes keeps the original result. Small results, errors, plain
conversation, source-file tools, patches, persona/config tools, and prompts
remain unchanged. There is no guaranteed saving on every turn or workload.

The bundled `json-only.toml` disables TOON, deduplication and Unicode/base64
rewrites. MSSHI removes `LLMTRIM_PRESET` only inside the compression subprocess
and pins that file with `LLMTRIM_CONFIG`; global settings remain unchanged.
The upstream `safe` preset alone is insufficient: it can replace JSON arrays
with TOON strings, which the exact-data gate correctly rejects. Keep the TOML
beside `__init__.py`; if it is missing, the original result is retained.

Install this directory as `<HERMES_HOME>/plugins/msshi-auto-trim/` and enable
`msshi-auto-trim` under `plugins.enabled`. Set the executable under
`plugins.entries.msshi-auto-trim.settings.binary`. Repeat for each profile.
MSSHI's runtime migrator can handle these steps transactionally.

Diagnostics require no model or API call. Read the selected profile's aggregate
counters from the terminal with the MSSHI adapter:

```powershell
msshi trim --status --profile default
```

Replace `default` with the actual bot profile ID when needed. The adapter reads
only allowlisted aggregate-counter JSON; it does not invoke chat or a model.

The stable plugin ID remains `msshi-auto-trim`; the display name is MSSHITrim.
Do not install a second hook under a different ID. `/msshitrim-status` is an
additional status alias, not another compressor.

## Installation and compatible runtime

New Hermes setup stages this native plugin for all selected profiles and enables
it when the pinned local CLI is available. A missing runtime can be fetched only
as part of an install, from an explicit versioned archive whose SHA-256 is pinned.
Network failure leaves a pending explanation and the rest of setup can continue.
An existing explicit disable or edited plugin is preserved. Installing a plugin
does not launch any creative app or send a model request.

Manual preview and installation:

```powershell
msshi trim --install
msshi trim --install --apply --download-runtime
msshi trim --status --profile yukino
```

`--force-enable` is a separate explicit choice to re-enable a previously disabled
hook. A rollback receipt records changes. Unknown existing binary/plugin edits
are not replaced. The pinned release is llmtrim **0.13.8**, source revision
`7dce1a46c55195f16b2e36cc675581b5ad7006e9`, checked 19 November 2026.
llmtrim is MPL-2.0; this original adapter is MIT. Runtime code is downloaded from
the upstream release, not relabeled as MSSHI-owned code.

The upstream `llmtrim setup` configures a TLS proxy, certificate trust and a login
daemon. MSSHITrim does **not** run that command or change proxy/certificate/model
settings. Its direct CLI subprocess processes eligible tool JSON locally.
The separate `Zenjibad/llmtrim-stats-plugin` is a DSH Web UI dashboard, not a
Hermes plugin and not a compressor. It is not installed into Hermes. MSSHITrim's
native counters report byte reductions, not a promised reduction in provider
billing. Source: [llmtrim](https://github.com/fkiene/llmtrim),
[upstream Hermes guide](https://github.com/fkiene/llmtrim/blob/7dce1a46c55195f16b2e36cc675581b5ad7006e9/HERMES.md),
[DSH stats plugin](https://github.com/Zenjibad/llmtrim-stats-plugin/tree/f16ca99defe48428d19da3c9ff05998dc899f081).

The native `/msshi-trim-status` slash command also returns counters directly in
Hermes chat, including with isolated plugin hosts. The separate terminal command
`hermes msshi-trim-status` is available only with in-process plugin loading;
Hermes skips that CLI registration when isolation uses a host.

The plugin stores only aggregate counts and byte sizes in its profile-scoped
plugin state. It records no tool output, arguments, paths, chat, or secrets.
Byte reductions are real output-size measurements, not provider-billed token
measurements. Counters are best-effort diagnostics across concurrent processes.

Hermes' first-string-return rule means an earlier transforming plugin can take
precedence. This plugin never overrides Hermes core or another plugin. A restart
or supported plugin reload is required after installing or enabling it.
