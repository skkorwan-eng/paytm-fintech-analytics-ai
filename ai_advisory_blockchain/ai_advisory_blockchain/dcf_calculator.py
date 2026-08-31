import math
from stock_universe import STOCK_UNIVERSE, RISK_FREE_RATE, MARKET_RETURN

# Illustrative hypothetical Paytm business-line assumptions.
EBIT = 120_000_000
TAX_RATE = 0.25
DA = 25_000_000
CAPEX = 30_000_000
DELTA_NWC = 5_000_000
BASE_FCFF = EBIT * (1 - TAX_RATE) + DA - CAPEX - DELTA_NWC  # INR 80m

BETA = STOCK_UNIVERSE["PAYRETAIL"]["beta"]
COST_OF_EQUITY = RISK_FREE_RATE + BETA * (MARKET_RETURN - RISK_FREE_RATE)
AFTER_TAX_COST_OF_DEBT = 0.08 * (1 - TAX_RATE)
EQUITY_WEIGHT = 0.70
DEBT_WEIGHT = 0.30
WACC = EQUITY_WEIGHT * COST_OF_EQUITY + DEBT_WEIGHT * AFTER_TAX_COST_OF_DEBT

GROWTH_RATES = [0.12, 0.10, 0.08, 0.07, 0.06]
TERMINAL_GROWTH = 0.03  # at least 3pp below base WACC
EBITDA = 140_000_000
EV_EBITDA_MULTIPLE = 10.0

def project_fcff():
    fcff = BASE_FCFF
    values = []
    for year, growth in enumerate(GROWTH_RATES, start=1):
        fcff *= (1 + growth)
        values.append(fcff)
    return values

def dcf_value(discount_rate=WACC, terminal_growth=TERMINAL_GROWTH):
    flows = project_fcff()
    pv = sum(cf / ((1 + discount_rate) ** year) for year, cf in enumerate(flows, start=1))
    terminal = flows[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)
    pv_terminal = terminal / ((1 + discount_rate) ** 5)
    return pv + pv_terminal

def sensitivity_table():
    rows = []
    for wacc in [WACC - 0.01, WACC, WACC + 0.01]:
        row = []
        for g in [TERMINAL_GROWTH - 0.01, TERMINAL_GROWTH, TERMINAL_GROWTH + 0.01]:
            assert wacc > g, "Invalid sensitivity cell: WACC must exceed terminal growth."
            row.append(dcf_value(wacc, g))
        rows.append(row)
    return rows

if __name__ == "__main__":
    print("DCF VALUATION")
    print(f"Base FCFF: INR {BASE_FCFF:,.0f}")
    print(f"Cost of equity (CAPM): {COST_OF_EQUITY:.2%}")
    print(f"WACC: {WACC:.2%}")
    print(f"Terminal growth: {TERMINAL_GROWTH:.2%}")
    print("5-year FCFF:", [f"INR {x:,.0f}" for x in project_fcff()])
    print(f"DCF enterprise value: INR {dcf_value():,.0f}")
    print("3x3 sensitivity (rows=WACC -1pp/base/+1pp; cols=g -1pp/base/+1pp):")
    for row in sensitivity_table():
        print([f"INR {x:,.0f}" for x in row])
    ev_ebitda = EBITDA * EV_EBITDA_MULTIPLE
    print(f"EV/EBITDA cross-check: INR {ev_ebitda:,.0f}")
    print("Comparison: the DCF is a cash-flow-based intrinsic-value estimate, while EV/EBITDA is a market-multiple cross-check. Differences are driven by the growth, WACC, terminal-value and multiple assumptions.")
