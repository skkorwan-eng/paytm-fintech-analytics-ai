from stock_universe import STOCK_UNIVERSE

def debate(ticker="PAYTECH"):
    d = STOCK_UNIVERSE[ticker]
    bull = (
        f"Bull: With an analyst reference return of {d['analyst_expected_return']:.1%} "
        f"and beta of {d['beta']:.2f}, {ticker} offers attractive upside if the higher market sensitivity is rewarded."
    )
    bear = (
        f"Bear: {ticker} carries {d['std_dev']:.1%} standalone volatility and beta {d['beta']:.2f}, "
        f"so the downside risk can be substantial when market conditions weaken."
    )
    synth = (
        f"Overall, {ticker} combines a {d['analyst_expected_return']:.1%} analyst reference return with "
        f"{d['std_dev']:.1%} volatility. The opportunity is meaningful, but the risk profile supports diversification and suitability checks."
    )
    return {"ticker": ticker, "bull": bull, "bear": bear, "synthesizer": synth}

if __name__ == "__main__":
    result = debate()
    for k, v in result.items():
        print(f"{k}: {v}")
