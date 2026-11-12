# Automatic local Llmtrim for Hermes

This native plugin runs automatically on Hermes' supported
`transform_tool_result` hook. It uses `llmtrim compress`, never `send`,
MCP, a proxy, or a provider API. It changes no model or provider setting.

Only sufficiently large, valid JSON tool results are eligible. Every candidate
must decode to exactly the same canonical JSON as the original. If Llmtrim
converts data to TOON, drops values, changes text inside a JSON string, times
out, or fails, Hermes keeps the original result. Small results, errors, plain
conversation, source-file tools, patches, persona/config tools, and prompts
remain unchanged. There is no guaranteed saving on every turn or workload.

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
