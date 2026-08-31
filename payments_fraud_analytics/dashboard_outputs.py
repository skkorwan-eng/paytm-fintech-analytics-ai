import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ------------------------------------------------------------
# Paytm Payments & Fraud Analytics — Four-Layer Dashboard
# ------------------------------------------------------------

BASE = Path(".")
OUT = BASE / "dashboard_outputs"
OUT.mkdir(exist_ok=True)

ledger = pd.read_csv(BASE / "ledger.csv")
gateway = pd.read_csv(BASE / "gateway_export.csv")
merchants = pd.read_csv(BASE / "merchants.csv")

ledger["transaction_time"] = pd.to_datetime(ledger["transaction_time"])
gateway["transaction_time"] = pd.to_datetime(gateway["transaction_time"])

# -------------------------
# HEADLINE METRICS
# -------------------------
total_gmv = ledger["amount_inr"].sum()
success_rate = (ledger["status"].eq("captured").sum() / len(ledger)) * 100
chargeback_ratio = (ledger["status"].eq("chargeback").sum() / len(ledger)) * 100

common = pd.merge(
    ledger[["transaction_id", "amount_inr", "status"]],
    gateway[["transaction_id", "amount_inr", "status"]],
    on="transaction_id",
    how="inner",
    suffixes=("_ledger", "_gateway")
)

matched = (
    (common["amount_inr_ledger"] == common["amount_inr_gateway"])
    & (common["status_ledger"] == common["status_gateway"])
).sum()

match_rate = (matched / len(ledger)) * 100

# -------------------------
# LAYER 1 — HEADLINE
# -------------------------
fig = plt.figure(figsize=(12, 6))
fig.patch.set_facecolor("white")
fig.text(0.5, 0.90, "Paytm Payments & Fraud Analytics", ha="center",
         fontsize=22, fontweight="bold")
fig.text(0.5, 0.84, "Headline Layer", ha="center", fontsize=13)

metrics = [
    ("Total GMV", f"₹{total_gmv:,.0f}"),
    ("Overall Success Rate", f"{success_rate:.2f}%"),
    ("Reconciliation Match Rate", f"{match_rate:.2f}%"),
    ("Chargeback Ratio", f"{chargeback_ratio:.2f}%"),
]

for i, (label, value) in enumerate(metrics):
    x = 0.125 + i * 0.25
    fig.text(x, 0.58, value, ha="center", va="center",
             fontsize=24, fontweight="bold")
    fig.text(x, 0.47, label, ha="center", va="center", fontsize=11)

fig.text(
    0.5, 0.20,
    "Interpretation: GMV summarizes the platform-wide transaction value. "
    "The success rate measures captured transactions as a share of all ledger transactions. "
    "The match rate is strict: a transaction counts only when it exists in both files with identical amount and status. "
    "The chargeback ratio is count-based, not amount-based.",
    ha="center", va="center", wrap=True, fontsize=10
)

fig.savefig(OUT / "01_headline.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# -------------------------
# LAYER 2 — TRENDS
# -------------------------
daily = ledger.assign(
    date=ledger["transaction_time"].dt.date
).groupby("date").agg(
    daily_gmv=("amount_inr", "sum"),
    daily_chargebacks=("status", lambda x: (x == "chargeback").sum())
).reset_index()

daily["date"] = pd.to_datetime(daily["date"])

fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.plot(daily["date"], daily["daily_gmv"], marker="o", linewidth=2,
         label="Daily GMV")
ax1.set_xlabel("Date")
ax1.set_ylabel("Daily GMV (INR)")
ax1.tick_params(axis="x", rotation=45)

ax2 = ax1.twinx()
ax2.plot(daily["date"], daily["daily_chargebacks"], marker="s",
         linewidth=2, linestyle="--", label="Daily Chargebacks")
ax2.set_ylabel("Daily Chargeback Count")

ax1.set_title("Trends Layer — Daily GMV and Chargebacks")
fig.tight_layout()

fig.text(
    0.5, -0.05,
    "Interpretation: Daily GMV shows how transaction value changes across the 30-day window. "
    "The chargeback series highlights days with elevated post-transaction disputes. "
    "Comparing both series helps identify whether high-value activity coincides with increased chargeback activity.",
    ha="center", va="top", wrap=True, fontsize=9
)

fig.savefig(OUT / "02_trends.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# -------------------------
# LAYER 3 — BREAKDOWN
# -------------------------
joined = ledger.merge(
    merchants[["merchant_id", "category"]],
    on="merchant_id",
    how="left"
)

by_method = joined.groupby("payment_method")["amount_inr"].sum().sort_values(ascending=False)
by_category = joined.groupby("category")["amount_inr"].sum().sort_values(ascending=False)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

axes[0].bar(by_method.index, by_method.values)
axes[0].set_title("GMV by Payment Method")
axes[0].set_ylabel("GMV (INR)")
axes[0].tick_params(axis="x", rotation=30)

axes[1].bar(by_category.index, by_category.values)
axes[1].set_title("GMV by Merchant Category")
axes[1].set_ylabel("GMV (INR)")
axes[1].tick_params(axis="x", rotation=45)

fig.suptitle("Breakdown Layer", fontsize=18, fontweight="bold")
fig.text(
    0.5, -0.02,
    "Interpretation: The payment-method view shows which payment rails contribute the most GMV. "
    "The category view shows how transaction value is distributed across merchant categories. "
    "These breakdowns can help prioritize payment operations and category-level monitoring.",
    ha="center", va="top", wrap=True, fontsize=9
)

fig.tight_layout()
fig.savefig(OUT / "03_breakdown.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# -------------------------
# LAYER 4 — DETAILS
# -------------------------
merchant_summary = joined.groupby(
    ["merchant_id", "category"], as_index=False
).agg(
    transaction_count=("transaction_id", "count"),
    chargeback_count=("status", lambda x: (x == "chargeback").sum()),
    total_gmv=("amount_inr", "sum")
)

merchant_summary["chargeback_ratio"] = (
    merchant_summary["chargeback_count"]
    / merchant_summary["transaction_count"]
    * 100
)

merchant_summary["flag"] = merchant_summary["chargeback_ratio"].apply(
    lambda x: "HIGH RISK" if x > 1 else ""
)

details = merchant_summary.sort_values(
    "transaction_count", ascending=False
).head(10).copy()

details["merchant"] = details["merchant_id"].map(
    lambda x: f"Merchant_{int(x):03d}"
)

display_cols = [
    "merchant", "category", "transaction_count",
    "chargeback_count", "chargeback_ratio", "flag"
]

fig, ax = plt.subplots(figsize=(14, 6))
ax.axis("off")

table_data = []
for _, row in details.iterrows():
    table_data.append([
        row["merchant"],
        row["category"],
        int(row["transaction_count"]),
        int(row["chargeback_count"]),
        f'{row["chargeback_ratio"]:.2f}%',
        row["flag"]
    ])

table = ax.table(
    cellText=table_data,
    colLabels=[
        "Merchant", "Category", "Txn Count",
        "Chargebacks", "Chargeback Ratio", "Flag"
    ],
    loc="center",
    cellLoc="center"
)
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 1.8)

ax.set_title(
    "Details Layer — Top 10 Merchants by Transaction Count",
    fontsize=17, fontweight="bold", pad=20
)

fig.text(
    0.5, 0.03,
    "Interpretation: This table ranks merchants by total transaction count and reports their count-based "
    "chargeback ratio. A merchant is flagged HIGH RISK when its chargeback ratio exceeds 1%, matching the "
    "assignment definition. The flag is scoped to each merchant and uses all transactions for that merchant.",
    ha="center", va="bottom", wrap=True, fontsize=9
)

fig.savefig(OUT / "04_details.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Save headline metrics for documentation
metrics_df = pd.DataFrame({
    "metric": [
        "total_gmv_inr",
        "overall_success_rate_pct",
        "reconciliation_match_rate_pct",
        "chargeback_ratio_pct"
    ],
    "value": [
        total_gmv,
        success_rate,
        match_rate,
        chargeback_ratio
    ]
})
metrics_df.to_csv(OUT / "headline_metrics.csv", index=False)

print("Dashboard created successfully.")
print(f"Total GMV: ₹{total_gmv:,.2f}")
print(f"Overall success rate: {success_rate:.2f}%")
print(f"Reconciliation match rate: {match_rate:.2f}%")
print(f"Chargeback ratio: {chargeback_ratio:.2f}%")
print("\nSaved files in dashboard_outputs/:")
print("01_headline.png")
print("02_trends.png")
print("03_breakdown.png")
print("04_details.png")
print("headline_metrics.csv")
