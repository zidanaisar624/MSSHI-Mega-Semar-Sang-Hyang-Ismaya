import json
import subprocess
import sys
import os

CLI_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cli_anything_business_sage.py")

def run_cli(*args):
    out = subprocess.check_output([sys.executable, CLI_PATH, "--json", *args], encoding="utf-8", env={**os.environ, "PYTHONUTF8": "1"})
    return json.loads(out)

def test_all():
    r1 = run_cli("unit-economics", "--price", "200000", "--variable-cost", "80000", "--monthly-fixed-cost", "12000000", "--cac", "120000")
    assert r1["status"] == "ok" and r1["contribution_margin_per_unit"] == 120000.0
    assert r1["break_even_units_per_month"] == 100

    r2 = run_cli("indonesia-tax-legal", "--annual-turnover-idr", "400000000", "--annual-net-profit-idr", "80000000", "--entity-type", "wp_op")
    assert r2["status"] == "ok" and r2["tax_comparison_pp_20_2026_idr"]["wp_orang_pribadi_umkm"] == 0.0

    r3 = run_cli("predict-trend", "--sector", "AI Workflow", "--current-adoption-pct", "10")
    assert r3["status"] == "ok" and "OPTIMAL ENTRY WINDOW" in r3["lifecycle_phase"]
    print("All cli-anything-business-sage E2E tests passed!")

if __name__ == "__main__":
    test_all()
