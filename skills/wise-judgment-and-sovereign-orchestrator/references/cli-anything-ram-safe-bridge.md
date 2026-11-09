# On-demand web and app bridge

The bundled `cli_anything_sovereign_hub.py` exposes a local `bridge` command for selected web search URLs and optional desktop app launch. Adapters from [CLI-Anything](https://github.com/HKUDS/CLI-Anything) can be configured separately.

From the package root:

```bash
python skills/wise-judgment-and-sovereign-orchestrator/scripts/cli_anything_sovereign_hub.py --json bridge --target youtube-chrome --query "example public query"
```

This shows the intended action without launching the app. Use `--open` when the user asked to open the target and the query may be sent to that service. The bridge supports these target IDs:

| Target | Behavior |
| --- | --- |
| `gdrive-web` | Open a Drive URL or search in the system browser. Account access depends on the user session. |
| `perplexity` | Use a detected desktop installation if free-memory telemetry permits, or open the web search. |
| `youtube-chrome` | Open the resolved YouTube URL via the system browser. |
| `tiktok` | Open TikTok web or search via the system browser. |
| `antigravity` | Use a detected executable. An optional local directory selects the workspace. |

Use `auto_open_on_boot: false`. Treat ArtCraft, Blender, Steel, OCR, and additional app connectors as optional, separately configured integrations. For tasks requiring retrieval, uploads, API calls, or authenticated writes, use a connector with the relevant capability and authorization.
