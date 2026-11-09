---
name: cli-anything-business-sage
description: CLI-Anything agent-native command-line harness for Business Sage (S1 BBA, S2 MBA, Indonesian Tax/Legal PP 20/2026 & PP 7/2021, DCF Valuation, Unit Economics, Trend Prediction, Profit-Gap Scanner, and Modal Rp0 Bootstrap Engine). Supports deterministic --json output and interactive stateful REPL.
---
# cli-anything-business-sage

Agent-native CLI harness following the [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) contract $H = (S, C, I, R, V, D)$ for deterministic financial, strategic, and Indonesian regulatory calculations.

## Command Groups & Usage (`--json`)

Always pass `--json` when invoking from an AI agent (Hermes, OpenClaw, Claude Code, Codex, or Cursor):

```bash
# 1. Inspect Ph.D. Ledger status and auto-detected Hermes/Agent directories
cli-anything-business-sage --json status

# 2. Run 16-Unit Financial Literacy & 50/30/20 Budget Audit
cli-anything-business-sage --json literacy-audit --monthly-after-tax-income 15000000 --monthly-needs 7000000 --monthly-wants 3500000 --monthly-savings 4500000 --liquid-emergency-cash 30000000 --high-apr-debt 0

# 3. Audit Startup / Product Unit Economics (Contribution Margin, BEP, LTV:CAC, Payback)
cli-anything-business-sage --json unit-economics --price 250000 --variable-cost 100000 --monthly-fixed-cost 15000000 --cac 150000 --monthly-churn-rate 0.05

# 4. Run 5-Year Intrinsic DCF Valuation (Damodaran / Wharton Standard)
cli-anything-business-sage --json valuation-dcf --initial-fcff 500000000 --growth-rate-5yr 0.18 --terminal-growth-rate 0.04 --wacc 0.11 --cash 120000000 --debt 50000000

# 5. Compare Indonesian UMKM Scale (PP 7/2021) & Corporate Tax (PP 20/2026 vs Pasal 31E)
cli-anything-business-sage --json indonesia-tax-legal --annual-turnover-idr 2400000000 --annual-net-profit-idr 300000000 --entity-type pt_perorangan

# 6. Predict Business Trend Phase (Bass Diffusion S-Curve & Geo-Lag Arbitrage)
cli-anything-business-sage --json predict-trend --sector "AI Automation for Indonesian UMKM" --innovation-coeff-p 0.025 --imitation-coeff-q 0.42 --current-adoption-pct 6.5

# 7. Generate Zero-Rupiah (Modal Rp0) Negative-CCC Business Blueprints & WhatsApp Script
cli-anything-business-sage --json zero-rupiah-plan --skill-or-network "Full-Stack Web & Videography" --target-market "Klinik & F&B Lokal" --target-monthly-profit-idr 15000000

# 8. Log New Doctoral Insight into the Eternal Ph.D. Ledger
cli-anything-business-sage --json phd-learn --topic "Negative CCC Pre-Order" --insight "Collecting 50% DP before production eliminates working capital debt" --category "Bootstrap-Method"

# 9. Pull Latest Skill Updates from GitHub into Hermes/OpenClaw/Claude
cli-anything-business-sage --json update
```
