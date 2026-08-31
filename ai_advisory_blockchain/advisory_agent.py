import os
import math
from stock_universe import STOCK_UNIVERSE, RISK_FREE_RATE, MARKET_RETURN
from investor_profiles import INVESTOR_PROFILES

ALLOCATION = {
    "Conservative": ["PAYBOND", "PAYGOLD", "PAYRETAIL"],
    "Moderate": ["PAYRETAIL", "PAYINFRA", "PAYGOLD"],
    "Aggressive": ["PAYTECH", "PAYFIN", "PAYINFRA"],
}

def get_stock_data(ticker):
    return STOCK_UNIVERSE[ticker]

def capm_return(beta):
    return RISK_FREE_RATE + beta * (MARKET_RETURN - RISK_FREE_RATE)

def portfolio_metrics(tickers, rho=0.3):
    w = 1 / len(tickers)
    data = [get_stock_data(t) for t in tickers]
    expected = sum(w * capm_return(d["beta"]) for d in data)
    variance = sum((w ** 2) * (d["std_dev"] ** 2) for d in data)
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            cov = rho * data[i]["std_dev"] * data[j]["std_dev"]
            variance += 2 * w * w * cov
    return expected, variance, math.sqrt(variance)

def narrative(profile, result):
    if os.getenv("MOCK_LLM", "1") == "0":
        return f"For {profile['risk_tolerance']} investor {profile['investor_id']}, the recommended equal-weight allocation is {', '.join(result['allocation'])}; CAPM expected return is {result['expected_return']:.1%} and volatility is {result['portfolio_std']:.1%}."
    return f"For {profile['risk_tolerance']} investor {profile['investor_id']}, we recommend an equal-weight allocation across {', '.join(result['allocation'])} with an expected portfolio return of {result['expected_return']:.1%} and volatility of {result['portfolio_std']:.1%}."

def run_agent(profile):
    # THINK: choose the prescribed allocation.
    allocation = ALLOCATION[profile["risk_tolerance"]]

    # ACT: use the local get_stock_data tool for each ticker.
    tool_data = {ticker: get_stock_data(ticker) for ticker in allocation}

    # OBSERVE: calculate CAPM return, variance and escalation.
    expected, variance, std = portfolio_metrics(allocation)
    result = {
        "investor_id": profile["investor_id"],
        "risk_tolerance": profile["risk_tolerance"],
        "allocation": allocation,
        "expected_return": expected,
        "portfolio_variance": variance,
        "portfolio_std": std,
        "escalation": "ESCALATED_TO_HUMAN_ADVISOR" if std > 0.20 else "FINALIZED",
        "tool_data": tool_data,
    }
    result["narrative"] = narrative(profile, result)
    return result

if __name__ == "__main__":
    print("AI-ADVISORY AGENT | MOCK_LLM baseline")
    for profile in INVESTOR_PROFILES:
        r = run_agent(profile)
        print(f"{r['investor_id']}: allocation={r['allocation']}, CAPM_return={r['expected_return']:.2%}, std={r['portfolio_std']:.2%}, {r['escalation']}")
        print(" ", r["narrative"])
