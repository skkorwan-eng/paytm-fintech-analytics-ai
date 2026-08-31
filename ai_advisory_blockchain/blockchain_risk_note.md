# Blockchain / Crypto Risk Appendix — Paytm Money

## 1. Paytm Crypto Insights: stablecoin and DeFi/DAO governance risk

A hypothetical **Paytm Crypto Insights** watchlist should be informational and risk-first rather than promotional. Before a retail user sees a token, the feature should clearly distinguish **fiat-collateralized stablecoins** from **algorithmic stablecoins**. A fiat-collateralized design aims to maintain a reference value through reserves such as cash or short-duration liquid assets; an algorithmic design may instead depend heavily on market incentives, collateral mechanisms, supply changes or a second token. The second structure can be more exposed to reflexive runs, liquidity shocks and loss of the intended peg.

The watchlist should therefore show the stablecoin type, reserve/collateral model, redemption mechanism, concentration of reserves, audit/attestation status where available, liquidity and major depeg history. It should avoid presenting “stable” as “risk-free.” For DeFi and DAO projects, the product should surface smart-contract audit status, upgrade/admin-key concentration, governance participation, token distribution, treasury exposure, oracle dependence, bridge dependence and material changes to tokenomics. A DAO label does not by itself mean decentralized control: a small number of wallets, delegates or insiders can sometimes exercise effective voting power.

## 2. Crypto allocation recommendation

For a retail advisory product, my recommended **maximum strategic crypto allocation is 0% by default**. This is deliberately conservative. Standard CAPM-style portfolio theory is built around expected returns, covariance and assets with conventional economic claims; a cryptocurrency generally lacks a direct intrinsic cash-flow claim such as dividends or contractual interest. Although crypto can exhibit low or negative correlation with some traditional assets at particular times and can show heavy-tailed, positively skewed returns, those properties do not guarantee reliable diversification.

There are also important implementation concerns: survivorship bias can make successful tokens look more representative than the full historical universe, while high transaction costs, spreads, liquidity differences, custody risks and extreme drawdowns can reduce realized investor outcomes. A retail product that cannot demonstrate a robust suitability case should therefore not automatically place crypto inside an optimal portfolio. A future version could permit a small, explicitly optional satellite allocation after legal, suitability, liquidity and risk controls are established, but the baseline recommendation here remains **zero allocation**.

## 3. T.A.N.G. social-engineering analysis

Two risk vectors are especially relevant to a UPI/wallet + lending + wealth platform.

**Authority + Temptation: impersonated support or investment officials.** An attacker can pose as a bank, wallet or wealth adviser and create urgency around a “security check,” refund or high-return investment. A real-time bank-side defense should combine device binding, behavioural anomaly scoring and step-up authentication: a new device plus unusual beneficiary plus urgent high-value transfer should trigger a transaction hold and independent in-app confirmation rather than relying on a phone call from the supposed official.

**Need + Greed: emergency-loan and guaranteed-return scams.** A fraudster can exploit a user's urgent need for credit or greed for unusually high investment returns, then persuade the user to send a fee, OTP or funds to a fraudulent account. A real-time defense should use risk-based transaction monitoring with beneficiary reputation, velocity, device and session signals, plus a cooling-off/confirmation step for first-time beneficiaries and suspicious high-value transfers. The bank should also display a clear warning that OTPs, PINs and remote-access requests are never required for support.

The key design principle is that the platform should treat social engineering as a transaction-risk problem, not merely a customer-education problem: controls should interrupt suspicious actions at the moment risk is detected.
