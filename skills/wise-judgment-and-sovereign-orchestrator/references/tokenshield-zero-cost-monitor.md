# TokenShield v2.0

TokenShield is the local preflight in `scripts/cli_anything_sovereign_hub.py` beside this skill. It compares the supplied current balance and estimated cost, in USD, to a USD 1.00 reserve. Obtain the values from provider billing or verified local usage and account data. TokenTracker and token-monitor are optional sources to evaluate, depending on compatibility and freshness.

From the package root:

```bash
python skills/wise-judgment-and-sovereign-orchestrator/scripts/cli_anything_sovereign_hub.py --json token-audit --balance-usd 1.20 --estimated-cost-usd 0.10
```

The example projects USD 1.10 after the task and returns exit 0. Missing inputs or a projected balance under USD 1.00 return exit 2. Pause paid work if either value is absent or stale. Recheck after long jobs or large requests.

Keep fixed instructions stable and extract relevant evidence locally where possible. Any prompt cache savings depend on provider support, prices, and observed usage. Confirm actual costs in the provider dashboard. The check runs on request using supplied inputs. It does not collect live balance, start a daemon, or change routing.
