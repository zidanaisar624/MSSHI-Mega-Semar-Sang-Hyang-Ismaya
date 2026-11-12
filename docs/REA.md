# REA: optional Coder CLI integration

REA is **OFF by default for public MSSHI installations**. The source wrapper is `optional/rea/SKILL.md`; it is not part of the default `skills/` discovery tree. The existing source inventory entry `rea` refers to the same upstream and is not duplicated. On the owner's explicitly authorized personal installation, only profile `nyenyenye-ya-gw-coder` has the new `rea` wrapper enabled. Its older physical `reverse-engineer-anything` folder is retained.

## Explicit opt in

From the MSSHI CLI, choose the destination skills directory explicitly:

```text
msshi optional enable rea --target-dir /absolute/path/to/coder/skills
msshi rea status
```

To install the separate runtime at the same time, add `--install-runtime`. Alternatively run `msshi rea install` explicitly after enabling the skill. Existing conflicting skill folders must be reviewed rather than overwritten. A supported Node.js/npm installation is required before runtime installation; no Node installation, MCP registration, global npm installation or app startup is performed by this integration.

All REA subcommands also work through `python /absolute/path/to/MSSHI/scripts/msshi_rea.py` or the identical `scripts/msshi_rea.py` inside the enabled skill. The optional `--hermes-home PATH` is placed before the subcommand. A profile home is normalized to its shared Hermes root. The runtime location is `<Hermes root>/msshi-private/rea-runtime`, outside the skill scanner. The adapter's `install` uses npm with `--ignore-scripts --omit=dev --omit=optional --no-audit --no-fund --save-exact`; the release bundles its production dependencies. Optional Frida, native engines and browser downloads are excluded.

## Pinned provenance

| Item | Reviewed value |
| --- | --- |
| Official source | [morluto/rea](https://github.com/morluto/rea) |
| Source inspection pin | [`a8527d43b8439476f5c9d1497315dfe7dd5e1f38`](https://github.com/morluto/rea/tree/a8527d43b8439476f5c9d1497315dfe7dd5e1f38) |
| CLI distribution | `rea-agents@6.9.0`, official npm package linked by the source README |
| npm integrity | `sha512-KqDn1UR5BMqHoQ3MGAnPuWiSKwgdFaz1L/uUNgrKt+1W8kPtgYP8AWEOXIF1lDIOBVyPuYIIst2iamo1Wf3r8g==` |
| License | [MIT, Copyright (c) 2026 morluto](https://github.com/morluto/rea/blob/a8527d43b8439476f5c9d1497315dfe7dd5e1f38/LICENSE) |
| Node requirement | `^22.23.4 || ^24.22.1 || >=26.12.1` |

The source inspection pin and published npm integrity are separate provenance facts: npm does not advertise a `gitHead` for this release. The integration does not claim that the npm tarball is byte-for-byte the checked-out repository. REA code and dependencies remain in the user's isolated runtime; the public wrapper and adapter are original MSSHI code. Keep upstream and bundled third-party license notices with any redistributed runtime.

The reviewed primary references are the pinned [README](https://github.com/morluto/rea/blob/a8527d43b8439476f5c9d1497315dfe7dd5e1f38/README.md), [CLI/Evidence guide](https://github.com/morluto/rea/blob/a8527d43b8439476f5c9d1497315dfe7dd5e1f38/docs/getting-started/cli.md), [static-analysis example](https://github.com/morluto/rea/blob/a8527d43b8439476f5c9d1497315dfe7dd5e1f38/docs/ci-analysis.md), package manifest, CLI entrypoint and local analysis command source. Source instructions are reference material; they do not authorize additional configuration changes.

## Commands and readiness

```text
msshi rea status
msshi rea selftest
msshi rea javascript /absolute/path/to/extracted-app --output /absolute/path/to/new-app.json
msshi rea inspect archive /absolute/path/to/owned.zip --output /absolute/path/to/new-archive.json
msshi rea native analyze /absolute/path/to/authorized-program --provider ghidra --output /absolute/path/to/new-native.json
```

`javascript` statically inspects an extracted application directory or ASAR; it does not execute its JavaScript and requires no LLM/native engine. `--analysis-timeout-ms` defaults to 30,000 and accepts 1,000–120,000 ms. The process receives an isolated home plus OS/runtime and explicit `REA_*` provider variables, rather than the agent's API credentials. `inspect` offers read-only archive, managed, PE import/certificate, Go/Rust binary metadata, model artifact and WebAssembly routes. These routes are format-dependent; only operations named in the actual smoke evidence are verified.

Native commands require an existing supported engine (`ghidra`, `hopper`, `kuna`), the engine's required Java/license/platform dependencies and its explicit `REA_*` configuration. Consult the pinned upstream provider guide for that engine. Upstream IDA requires a separate IDA MCP bridge, so this CLI-only wrapper excludes it. The adapter does not configure or install an engine. Engine launch is distinct from target execution; live processes, debugger/dynamic instrumentation, browser sessions, Android device operations and extraction are outside this wrapper. Missing engines do not block distributing the optional static CLI workflow.

On this Windows host the inspected Java executable exists, but no Ghidra, Hopper, IDA or JADX was discovered on PATH or in the few conventional installation locations inspected. This is an inventory result, not a complete disk search. The pinned upstream Windows Ghidra P0 guide requires Windows x64, appropriate NTFS/ReFS volumes, operator-installed Ghidra 12.1+ and a compatible full 64-bit JDK (21+ for the documented current Ghidra 12.1 releases). Its supported target/operation boundary is narrower than the general upstream feature list. No native-engine investigation was run for this integration.

Reports are new JSON files outside the input tree. The original command output and diagnostics are retained, and nonzero exit codes propagate. A successful command may still contain incomplete coverage or limitations; review its Evidence before making claims. `selftest` stores a private proof including the full evidence from owned benign JavaScript and ZIP fixtures, checks expected module/member names and confirms that an execution sentinel was not created.

## Preserved settings

No upstream `setup`, MCP registration, registration repair, global update, automatic Hopper download, app auto-start, provider/model/fallback/MoA mutation or LLM/paid API test is performed. Existing SOUL/persona/memory/DNA, credentials, Google Drive OFF, Brightdata OFF and Steel consent policy remain outside the adapter. Source cache, runtime, reports and private audits are excluded from the public package.
