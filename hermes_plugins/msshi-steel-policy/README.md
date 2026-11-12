# MSSHI strict Steel policy

This native Hermes plugin uses the supported `pre_tool_call`, `tool_execution`
middleware and prompt-section registration APIs. It makes no network request at
registration/startup and does not modify Hermes core or use MCP.

Hermes currently falls back to local Chromium when a cloud provider fails.
This plugin intercepts `browser_exec`, creates a remote session through the pinned
official Steel provider and invokes Hermes' installed browser-harness in a child
process with an explicit `BU_CDP_WS`. It bypasses the native fallback resolver.
Each call is one batch: its owned remote session is released in `finally`, and
its uniquely named harness daemon is stopped on a best-effort basis. Remote
release failure is reported; the configured Steel hard timeout remains insurance.
No personal browser is opened, discovered or copied.

The native human approval gate asks before each Steel batch because remote
browsing can use account quota or money. Missing credentials block before any
network request. Proxy/CAPTCHA upgrades and direct `steel_scrape` are blocked.
The budget prompt is a gate, not a provider-side spending cap.

Personal account access uses the separate `msshi_personal_browser` tool. It needs
site, account, purpose, access and duration and passes through a fresh human
approval. It can attach only to an endpoint the operator has already connected;
it never launches Chrome or copies its profile. Transferring a session/login into
Steel is not implemented; it requires a supported method and separate consent.

Install using `msshi browser --install --hermes-home PROFILE`. The helper installs
official plugin files at pinned commit `d8a1e39657d3e3deaa59da37e857be3f14b9dc5b`,
records ownership hashes, preserves unrelated configuration and writes rollback
receipts. In-process native plugin loading is required. If a future Hermes update
changes the browser-harness adapter API, execution returns an error instead of
falling back to the original local browser tool.

This adapter routes official browser tools; it is not an OS security boundary.
Terminal/computer tools have their own authorization policies. Do not bypass the
route with an ad-hoc browser command. Browser code is powerful and personal-site
scope still requires the agent's compliance with the approved task.

The official entrypoint has a version-guarded compatibility adaptation: on Hermes
without `tools.url_safety.sensitive_query_param_name`, it registers only the
unmodified official provider, skipping optional scrape/options imports. Those
tools are blocked by this policy in either case. No Hermes core file is patched;
the adapted plugin entrypoint is tracked in installer ownership hashes.
