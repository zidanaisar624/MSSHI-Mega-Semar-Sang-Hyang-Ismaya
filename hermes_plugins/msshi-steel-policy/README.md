# Retired browser policy

This compatibility stub does not install, start or route through Steel. It does not
register tools, hooks, prompt sections or browser providers. Existing browser
accounts and credentials are not read, moved or deleted.

Choose a browser with `msshi browser --browser chrome` (or `edge`, `firefox`,
`none`). This stores a preference only. Connect and sign in manually in Hermes
when a task needs the browser; no profile or cookie transfer is performed.

The legacy `scripts/msshi_browser_policy.py --status` command reads only local
registration. `--install` is a no-op. Historical receipt rollback remains an
explicit, fingerprint-checked recovery action.
