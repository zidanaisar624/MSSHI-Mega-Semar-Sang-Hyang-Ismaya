#!/usr/bin/env python3
"""
cli-anything-business-sage: Agent-Native CLI Harness for Business Sage (S1 BBA -> S2 MBA -> Eternal Ph.D.)
Compatible with https://github.com/HKUDS/CLI-Anything, Hermes Agent, OpenClaw, Claude Code, and ChatGPT.
"""
import argparse
import json
import math
import os
import platform
import sys
from datetime import datetime, timezone

VERSION = "1.0.0"

def get_state_dir():
    base = os.environ.get("BUSINESS_SAGE_HOME", os.path.join(os.path.expanduser("~"), ".business-sage"))
    os.makedirs(base, exist_ok=True)
    os.makedirs(os.path.join(base, "phd_business_ledger"), exist_ok=True)
    return base

def load_session():
    path = os.path.join(get_state_dir(), "session.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "version": VERSION,
        "phd_level": "Eternal Ph.D. Candidate (S1 BBA + S2 MBA Mastered)",
        "history": [],
        "learned_insights": []
    }

def save_session(state):
    path = os.path.join(get_state_dir(), "session.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def discover_agent_skill_dirs():
    """Auto-discovers Hermes, OpenClaw, and Claude skill directories on any user's machine."""
    found = []
    home = os.path.expanduser("~")
    candidates = []

    # 1. Environment variables
    for env_var in ["HERMES_HOME", "HERMES_DATA", "HERMES_ROOT", "OPENCLAW_HOME"]:
        val = os.environ.get(env_var)
        if val:
            candidates.append(os.path.join(val, "skills"))
            candidates.append(val)

    # 2. Standard user home paths
    candidates.extend([
        os.path.join(home, ".hermes", "skills"),
        os.path.join(home, "HermesData", "skills"),
        os.path.join(home, "Hermes", "skills"),
        os.path.join(home, ".openclaw", "skills"),
        os.path.join(home, ".claude", "skills"),
    ])

    # 3. Windows drive scanning (C:, D:, E:, F:, etc.) for Hermes installations
    if platform.system() == "Windows":
        for drive_letter in "CDEFGH":
            drive = f"{drive_letter}:\\"
            if os.path.exists(drive):
                candidates.extend([
                    os.path.join(drive, "HermesData", "skills"),
                    os.path.join(drive, "Hermes", "skills"),
                    os.path.join(drive, "ProgramData", "Hermes", "skills"),
                ])
                # Scan 1 level of top folders for *Hermes*
                try:
                    for entry in os.scandir(drive):
                        if entry.is_dir() and "hermes" in entry.name.lower():
                            candidates.append(os.path.join(entry.path, "skills"))
                except Exception:
                    pass

    for c in candidates:
        parent = os.path.dirname(c) if c.endswith("skills") else c
        if os.path.exists(c) or (os.path.exists(parent) and "hermes" in parent.lower()):
            norm = os.path.abspath(c)
            if norm not in found:
                found.append(norm)

    return found

def cmd_status(args):
    session = load_session()
    skill_dirs = discover_agent_skill_dirs()
    return {
        "status": "ok",
        "tool": "cli-anything-business-sage",
        "version": VERSION,
        "phd_status": session.get("phd_level"),
        "state_dir": get_state_dir(),
        "detected_agent_skill_dirs": skill_dirs,
        "learned_insights_count": len(session.get("learned_insights", [])),
        "history_count": len(session.get("history", [])),
    }

def cmd_literacy_audit(args):
    income = float(args.monthly_after_tax_income)
    needs = float(args.monthly_needs)
    wants = float(args.monthly_wants)
    savings = float(args.monthly_savings)
    liquid_cash = float(args.liquid_emergency_cash)
    high_apr_debt = float(args.high_apr_debt)

    needs_pct = round((needs / income) * 100, 2) if income > 0 else 0
    wants_pct = round((wants / income) * 100, 2) if income > 0 else 0
    savings_pct = round((savings / income) * 100, 2) if income > 0 else 0
    emergency_months = round(liquid_cash / needs, 2) if needs > 0 else 99.0

    recs = []
    if emergency_months < 3.0:
        recs.append(f"Prioritas 1: Bangun Dana Darurat hingga minimal 3-6x biaya pokok ({3*needs:,.0f} - {6*needs:,.0f}). Saat ini baru {emergency_months} bulan.")
    if high_apr_debt > 0:
        recs.append(f"Prioritas 2: Lunasi utang berbunga tinggi ({high_apr_debt:,.0f}) dengan metode Avalanche (bunga tertinggi dulu) sebelum investasi berisiko.")
    if needs_pct > 50:
        recs.append(f"Optimasi Needs: Porsi kebutuhan pokok ({needs_pct}%) melebihi patokan 50%. Audit biaya tetap & terapkan Per-Unit Pricing.")
    if savings_pct < 20:
        recs.append(f"Tingkatkan Tabungan/Investasi: Porsi tabungan ({savings_pct}%) di bawah target 20%.")
    if not recs:
        recs.append("Fondasi literasi keuangan sangat sehat (Siap mengalokasikan modal ke instrumen investasi / ekspansi bisnis).")

    return {
        "status": "ok",
        "command": "literacy-audit",
        "budget_50_30_20_breakdown": {
            "needs_pct": needs_pct,
            "wants_pct": wants_pct,
            "savings_pct": savings_pct,
            "target_rule": "50% Needs / 30% Wants / 20% Savings",
        },
        "emergency_runway_months": emergency_months,
        "ready_for_risk_investment": (emergency_months >= 3.0 and high_apr_debt == 0),
        "recommendations": recs,
    }

def cmd_unit_economics(args):
    price = float(args.price)
    var_cost = float(args.variable_cost)
    fixed_cost = float(args.monthly_fixed_cost)
    cac = float(args.cac)
    churn = float(args.monthly_churn_rate)

    cm = price - var_cost
    cm_pct = round((cm / price) * 100, 2) if price > 0 else 0.0
    bep_units = math.ceil(fixed_cost / cm) if cm > 0 else None
    ltv = round(cm / churn, 2) if churn > 0 else round(cm * 24, 2)
    ltv_cac = round(ltv / cac, 2) if cac > 0 else 999.0
    payback_months = round(cac / cm, 2) if cm > 0 else 999.0

    verdict = "HEALTHY_SCALABLE" if (ltv_cac >= 3.0 and payback_months <= 12.0 and cm > 0) else "NEEDS_OPTIMIZATION"
    return {
        "status": "ok",
        "command": "unit-economics",
        "contribution_margin_per_unit": round(cm, 2),
        "contribution_margin_pct": cm_pct,
        "break_even_units_per_month": bep_units,
        "gross_margin_ltv": ltv,
        "cac": cac,
        "ltv_to_cac_ratio": ltv_cac,
        "cac_payback_months": payback_months,
        "verdict": verdict,
        "benchmark_notes": "Target LTV:CAC >= 3.0x and CAC Payback <= 12 months (computed strictly on Contribution Margin, not Gross Revenue).",
    }

def cmd_valuation_dcf(args):
    fcff = float(args.initial_fcff)
    g_stage1 = float(args.growth_rate_5yr)
    g_terminal = float(args.terminal_growth_rate)
    wacc = float(args.wacc)
    cash = float(args.cash)
    debt = float(args.debt)

    if wacc <= g_terminal:
        return {"status": "error", "error": "WACC must be strictly greater than terminal_growth_rate."}

    pv_flows = []
    curr = fcff
    for t in range(1, 6):
        curr = curr * (1.0 + g_stage1)
        pv = curr / ((1.0 + wacc) ** t)
        pv_flows.append({"year": t, "projected_fcff": round(curr, 2), "present_value": round(pv, 2)})

    sum_pv = sum(x["present_value"] for x in pv_flows)
    tv = (curr * (1.0 + g_terminal)) / (wacc - g_terminal)
    pv_tv = tv / ((1.0 + wacc) ** 5)
    ev = sum_pv + pv_tv
    eq_val = ev + cash - debt

    return {
        "status": "ok",
        "command": "valuation-dcf",
        "five_year_cashflows": pv_flows,
        "pv_of_5yr_fcff": round(sum_pv, 2),
        "terminal_value_year_5": round(tv, 2),
        "pv_of_terminal_value": round(pv_tv, 2),
        "enterprise_value": round(ev, 2),
        "equity_value": round(eq_val, 2),
    }

def cmd_indonesia_tax_legal(args):
    omzet = float(args.annual_turnover_idr)
    net_profit = float(args.annual_net_profit_idr)
    entity = args.entity_type.lower()

    if not (math.isfinite(omzet) and math.isfinite(net_profit)) or omzet < 0:
        return {"status": "error", "command": "indonesia-tax-legal",
                "error": "Omzet harus non-negatif dan kedua masukan harus berupa angka terbatas."}

    # Scale under PP 7 Tahun 2021
    if omzet <= 2_000_000_000:
        scale = "Usaha Mikro (PP No. 7 Tahun 2021: Omzet <= Rp2 Miliar)"
        sak = "SAK EMKM (Ikatan Akuntan Indonesia)"
    elif omzet <= 15_000_000_000:
        scale = "Usaha Kecil (PP No. 7 Tahun 2021: Omzet >Rp2 Miliar s/d Rp15 Miliar)"
        sak = "SAK EMKM / SAK Entitas Privat (SAK EP)"
    elif omzet <= 50_000_000_000:
        scale = "Usaha Menengah (PP No. 7 Tahun 2021: Omzet >Rp15 Miliar s/d Rp50 Miliar)"
        sak = "SAK Entitas Privat (SAK EP)"
    else:
        scale = "Usaha Besar (Omzet > Rp50 Miliar)"
        sak = "SAK Indonesia (PSAK / Konvergensi IFRS)"

    # Calculate Tax under PP No. 20 Tahun 2026 & Pasal 31E UU PPh
    tax_op = 0.0
    if omzet <= 500_000_000:
        tax_op = 0.0
    elif omzet <= 4_800_000_000:
        tax_op = (omzet - 500_000_000) * 0.005
    else:
        tax_op = None

    # Under PP 20/2026, newly registered CV / PT Biasa use Pasal 31E (11% of net profit up to Rp4.8B)
    if net_profit <= 0:
        tax_pt_biasa_or_cv = 0.0
    elif omzet <= 4_800_000_000:
        tax_pt_biasa_or_cv = net_profit * 0.11
    elif omzet <= 50_000_000_000:
        fasilitas_portion = (4_800_000_000 / omzet) * net_profit
        non_fasilitas = net_profit - fasilitas_portion
        tax_pt_biasa_or_cv = (fasilitas_portion * 0.11) + (non_fasilitas * 0.22)
    else:
        tax_pt_biasa_or_cv = net_profit * 0.22

    tax_pt_perorangan = omzet * 0.005 if omzet <= 4_800_000_000 else tax_pt_biasa_or_cv
    threshold_crossed = omzet > 4_800_000_000

    return {
        "status": "ok",
        "command": "indonesia-tax-legal",
        "selected_entity": entity,
        "umkm_scale_pp_7_2021": scale,
        "recommended_accounting_standard": sak,
        "pkp_turnover_threshold_crossed": threshold_crossed,
        "calculation_basis": "Simulasi tahunan untuk omzet yang diasumsikan memenuhi skema. Untuk badan, masukan laba dianggap sebagai penghasilan kena pajak fiskal.",
        "reference": "https://pajak.go.id/en/node/120099",
        "tax_comparison_pp_20_2026_idr": {
            "wp_orang_pribadi_umkm": round(tax_op, 2) if tax_op is not None else None,
            "pt_perorangan_umk": round(tax_pt_perorangan, 2),
            "cv_atau_pt_biasa_pasal_31e": round(tax_pt_biasa_or_cv, 2),
        },
        "strategic_advisory": (
            "Periksa eligibilitas, agregasi omzet, jenis penghasilan, masa transisi dan status PKP. "
            "Simulasi WP orang pribadi di luar skema final perlu PTKP dan tarif progresif. "
            "Verifikasi angka dan ketentuan sebelum pelaporan pajak."
        ),
    }

def cmd_predict_trend(args):
    sector = args.sector
    p = float(args.innovation_coeff_p)
    q = float(args.imitation_coeff_q)
    current_adoption = float(args.current_adoption_pct) / 100.0

    # Bass Diffusion peak time t* = ln(q/p) / (p+q)
    t_peak = round(math.log(q / p) / (p + q), 2) if (p > 0 and q > p) else 0.0
    instantaneous_velocity = (p + q * current_adoption) * (1.0 - current_adoption)

    if current_adoption < 0.025:
        phase = "Phase 1: Innovators (<2.5%) - High R&D risk, educate market via low-cost content."
    elif current_adoption <= 0.16:
        phase = "Phase 2: Golden Early-Adopter Inflection (2.5% - 16%) - OPTIMAL ENTRY WINDOW! Word-of-mouth (q) is accelerating while CAC is still low."
    elif current_adoption <= 0.50:
        phase = "Phase 3: Early Majority (16% - 50%) - Compete on specialized niche positioning, B2B picks-and-shovels, or Tier-2/3 geographic arbitrage."
    else:
        phase = "Phase 4: Late Majority / Saturation (>50%) - High CAC, margin compression; pivot to unbundling or cost-leadership."

    return {
        "status": "ok",
        "command": "predict-trend",
        "sector": sector,
        "bass_diffusion_metrics": {
            "p_innovation": p,
            "q_imitation": q,
            "current_adoption_pct": round(current_adoption * 100, 2),
            "years_to_peak_adoption_t_star": t_peak,
            "adoption_velocity_index": round(instantaneous_velocity * 100, 3),
        },
        "lifecycle_phase": phase,
        "profit_gap_arbitrage_angles": [
            f"Geo-Lag Arbitrage: Adapt proven US/China/Japan playbooks in '{sector}' for Indonesian Tier-1/Tier-2 cities with QRIS & WhatsApp closing.",
            f"Picks & Shovels: Supply B2B tools, compliance (OSS-RBA/Halal/Tax), or fulfillment to other players entering '{sector}'.",
            f"Unbundling Gap: Strip out the single highest-margin service in '{sector}' and offer it as a fast fixed-price package.",
        ],
    }

def cmd_zero_rupiah_plan(args):
    skill_or_asset = args.skill_or_network
    target_market = args.target_market
    target_monthly_income = float(args.target_monthly_profit_idr)

    # Calculate 3 pricing tiers to hit target_monthly_income
    tier_b2b_price = 2_500_000.0
    clients_needed = math.ceil(target_monthly_income / tier_b2b_price)
    po_unit_margin = 100_000.0
    po_units_needed = math.ceil(target_monthly_income / po_unit_margin)

    return {
        "status": "ok",
        "command": "zero-rupiah-plan",
        "core_leverage": skill_or_asset,
        "target_market": target_market,
        "target_monthly_profit_idr": target_monthly_income,
        "mathematical_principle": "Negative Cash Conversion Cycle (CCC < 0): Collect 50-100% customer cash BEFORE incurring COGS.",
        "blueprints": [
            {
                "model": "1. B2B Done-For-You Service / Automation Retainer (Modal Rp0)",
                "offer": f"Paket solusi '{skill_or_asset}' untuk {target_market} dengan garansi hasil terukur.",
                "pricing_idr": tier_b2b_price,
                "upfront_dp_pct": 50,
                "sales_target": f"Cukup akuisisi {clients_needed} klien/bulan (@ Rp{tier_b2b_price:,.0f}) untuk mencapai Rp{target_monthly_income:,.0f}/bulan.",
            },
            {
                "model": "2. Batch Pre-Order (PO) / Back-to-Back Offtaker Arbitrage (Modal Rp0)",
                "offer": f"Kurasi produk/paket khusus bagi {target_market} dengan sistem PO Batch terbatas (DP 100% di muka).",
                "margin_per_unit_idr": po_unit_margin,
                "sales_target": f"Jual {po_units_needed} slot PO/bulan (@ margin bersih Rp{po_unit_margin:,.0f}/unit) menggunakan uang pelanggan untuk membayar supplier.",
            },
            {
                "model": "3. Idle-Capacity Revenue Share (Rainmaker Partnership - Modal Rp0)",
                "offer": f"Kerja sama bagi hasil 30%:70% dengan pemilik tempat/fasilitas di pasar {target_market} pada jam sepi (off-peak).",
                "capital_required_idr": 0,
            },
        ],
        "whatsapp_closing_script_id": (
            f"Halo Kak/Pak/Bu [Nama], saya melihat [Nama Bisnis/Target] di {target_market} punya potensi besar untuk meningkatkan [Manfaat Utama]. "
            f"Kebetulan kami sedang membuka 3 slot pilot untuk membantu lewat [{skill_or_asset}] tanpa biaya instalasi awal. "
            f"Boleh saya kirimkan 1 halaman simulasi singkatnya di sini, Kak?"
        ),
    }

def cmd_phd_learn(args):
    session = load_session()
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "topic": args.topic,
        "hypothesis_or_insight": args.insight,
        "category": args.category,
    }
    session.setdefault("learned_insights", []).append(entry)
    session.setdefault("history", []).append({"cmd": "phd-learn", "topic": args.topic, "ts": entry["timestamp"]})
    save_session(session)

    ledger_md = os.path.join(get_state_dir(), "phd_business_ledger", "dissertation_notes.md")
    with open(ledger_md, "a", encoding="utf-8") as f:
        f.write(f"\n## [{entry['timestamp'][:10]}] ({args.category}) {args.topic}\n- **Insight / Hypothesis**: {args.insight}\n")

    return {
        "status": "ok",
        "command": "phd-learn",
        "message": "Insight permanently recorded in Eternal Ph.D. Ledger.",
        "ledger_file": ledger_md,
        "total_phd_insights": len(session["learned_insights"]),
        "entry": entry,
    }

def cmd_update(args):
    return {
        "status": "manual_step",
        "command": "update",
        "instruction": "Use scripts/msshi_update.py from a reviewed MSSHI release with --mode check and --skills-dir.",
    }


def build_parser():
    parser = argparse.ArgumentParser(
        prog="cli-anything-business-sage",
        description="MSSHI — Mega Semar Sang Hyang Ismaya: Sovereign Sage | Business Sage"
    )
    parser.add_argument("--json", action="store_true", help="Emit deterministic machine-readable JSON output")
    sub = parser.add_subparsers(dest="subcommand")

    # status
    p_status = sub.add_parser("status", help="Inspect Business Sage Ph.D. ledger status and detected Hermes/Agent paths")
    p_status.set_defaults(func=cmd_status)

    # literacy-audit
    p_lit = sub.add_parser("literacy-audit", help="Run 16-Unit Financial Literacy & 50/30/20 audit")
    p_lit.add_argument("--monthly-after-tax-income", required=True, type=float)
    p_lit.add_argument("--monthly-needs", required=True, type=float)
    p_lit.add_argument("--monthly-wants", required=True, type=float)
    p_lit.add_argument("--monthly-savings", required=True, type=float)
    p_lit.add_argument("--liquid-emergency-cash", required=True, type=float)
    p_lit.add_argument("--high-apr-debt", default=0.0, type=float)
    p_lit.set_defaults(func=cmd_literacy_audit)

    # unit-economics
    p_ue = sub.add_parser("unit-economics", help="Compute Contribution Margin, BEP, Gross-Margin LTV, CAC & Payback")
    p_ue.add_argument("--price", required=True, type=float)
    p_ue.add_argument("--variable-cost", required=True, type=float)
    p_ue.add_argument("--monthly-fixed-cost", required=True, type=float)
    p_ue.add_argument("--cac", required=True, type=float)
    p_ue.add_argument("--monthly-churn-rate", default=0.05, type=float)
    p_ue.set_defaults(func=cmd_unit_economics)

    # valuation-dcf
    p_dcf = sub.add_parser("valuation-dcf", help="Compute 5-year Intrinsic DCF Enterprise & Equity Valuation")
    p_dcf.add_argument("--initial-fcff", required=True, type=float)
    p_dcf.add_argument("--growth-rate-5yr", required=True, type=float)
    p_dcf.add_argument("--terminal-growth-rate", default=0.03, type=float)
    p_dcf.add_argument("--wacc", required=True, type=float)
    p_dcf.add_argument("--cash", default=0.0, type=float)
    p_dcf.add_argument("--debt", default=0.0, type=float)
    p_dcf.set_defaults(func=cmd_valuation_dcf)

    # indonesia-tax-legal
    p_id = sub.add_parser("indonesia-tax-legal", help="Evaluate Indonesian UMKM tier (PP 7/2021) & Tax (PP 20/2026 vs Pasal 31E)")
    p_id.add_argument("--annual-turnover-idr", required=True, type=float)
    p_id.add_argument("--annual-net-profit-idr", required=True, type=float)
    p_id.add_argument("--entity-type", default="pt_perorangan", choices=["wp_op", "pt_perorangan", "cv", "pt_biasa", "koperasi"])
    p_id.set_defaults(func=cmd_indonesia_tax_legal)

    # predict-trend
    p_tr = sub.add_parser("predict-trend", help="Forecast trend adoption phase using Bass Diffusion & Geo-Lag Arbitrage")
    p_tr.add_argument("--sector", required=True)
    p_tr.add_argument("--innovation-coeff-p", default=0.02, type=float)
    p_tr.add_argument("--imitation-coeff-q", default=0.38, type=float)
    p_tr.add_argument("--current-adoption-pct", default=8.0, type=float)
    p_tr.set_defaults(func=cmd_predict_trend)

    # zero-rupiah-plan
    p_zr = sub.add_parser("zero-rupiah-plan", help="Generate Modal Rp0 business blueprints with Negative CCC (<0)")
    p_zr.add_argument("--skill-or-network", required=True)
    p_zr.add_argument("--target-market", required=True)
    p_zr.add_argument("--target-monthly-profit-idr", default=10000000.0, type=float)
    p_zr.set_defaults(func=cmd_zero_rupiah_plan)

    # phd-learn
    p_phd = sub.add_parser("phd-learn", help="Record a new business method, trend, or customer insight in the Eternal Ph.D. Ledger")
    p_phd.add_argument("--topic", required=True)
    p_phd.add_argument("--insight", required=True)
    p_phd.add_argument("--category", default="Business-Method")
    p_phd.set_defaults(func=cmd_phd_learn)

    # update
    p_up = sub.add_parser("update", help="Show how to run the MSSHI updater")
    p_up.set_defaults(func=cmd_update)

    return parser

def repl_loop(parser):
    print(f"=== Business Sage CLI-Anything REPL v{VERSION} (Eternal Ph.D. Business Advisor) ===")
    print("Type a subcommand (e.g., 'status', 'update', 'help', or 'exit').")
    while True:
        try:
            line = input("business-sage> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line or line in ("exit", "quit"):
            break
        if line == "help":
            parser.print_help()
            continue
        try:
            args = parser.parse_args(line.split())
            if hasattr(args, "func"):
                res = args.func(args)
                print(json.dumps(res, indent=2, ensure_ascii=False))
            else:
                parser.print_help()
        except SystemExit:
            pass
        except Exception as e:
            print(json.dumps({"status": "error", "error": str(e)}, indent=2))

def main():
    parser = build_parser()
    if len(sys.argv) == 1:
        repl_loop(parser)
        return
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    res = args.func(args)
    if args.json or True:
        print(json.dumps(res, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
