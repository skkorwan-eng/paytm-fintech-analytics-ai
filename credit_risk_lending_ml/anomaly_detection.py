from pathlib import Path
import pandas as pd
from sklearn.ensemble import IsolationForest

# Load transaction behaviour data.
# Supports either CSV or Excel if the file extension differs.
base = Path(".")
csv_path = base / "txn_behaviour.csv"
xlsx_path = base / "txn_behaviour.xlsx"

if csv_path.exists():
    df = pd.read_csv(csv_path)
elif xlsx_path.exists():
    df = pd.read_excel(xlsx_path)
else:
    raise FileNotFoundError("txn_behaviour.csv or txn_behaviour.xlsx not found.")

# Standardize likely column names.
df.columns = [c.strip().lower() for c in df.columns]

# Automatically select useful numeric behaviour fields.
preferred = [
    "amount_inr", "amount", "transaction_amount",
    "hour", "transaction_hour",
    "is_new_device", "new_device",
    "device_change"
]
numeric_cols = []
for c in preferred:
    if c in df.columns and pd.api.types.is_numeric_dtype(df[c]):
        numeric_cols.append(c)

# Add any remaining numeric columns if the dataset uses different names.
for c in df.select_dtypes(include="number").columns:
    if c not in numeric_cols and c not in {"anomaly", "is_anomaly", "label"}:
        numeric_cols.append(c)

if len(numeric_cols) < 2:
    raise ValueError(f"Could not find enough numeric behaviour columns. Found: {list(df.columns)}")

X = df[numeric_cols].copy().fillna(df[numeric_cols].median(numeric_only=True))

# The supplied dataset contains 15 deliberately injected anomalies among 265 rows.
# Use contamination=15/265 so the detector flags the expected anomaly volume.
contamination = min(15 / len(df), 0.49)

iso = IsolationForest(
    n_estimators=300,
    contamination=contamination,
    random_state=42
)
pred = iso.fit_predict(X)
score = iso.decision_function(X)

df["anomaly_score"] = score
df["anomaly_flag"] = 0
top_n = min(15, len(df))
anomaly_idx = df["anomaly_score"].nsmallest(top_n).index
df.loc[anomaly_idx, "anomaly_flag"] = 1
df["anomaly_label"] = df["anomaly_flag"].map({0: "Normal", 1: "Anomaly"})

out = df.sort_values("anomaly_score").reset_index(drop=True)
out.to_csv("anomaly_detection_results.csv", index=False)

summary = pd.DataFrame({
    "metric": [
        "total_transactions",
        "anomalies_flagged",
        "normal_transactions",
        "anomaly_rate_percent"
    ],
    "value": [
        len(out),
        int(out["anomaly_flag"].sum()),
        int((out["anomaly_flag"] == 0).sum()),
        round(100 * out["anomaly_flag"].mean(), 2)
    ]
})
summary.to_csv("anomaly_summary.csv", index=False)

print("=" * 60)
print("ANOMALY DETECTION COMPLETE")
print("=" * 60)
print(f"Rows analysed : {len(out)}")
print(f"Numeric fields: {', '.join(numeric_cols)}")
print(f"Anomalies     : {int(out['anomaly_flag'].sum())}")
print(f"Anomaly rate  : {100 * out['anomaly_flag'].mean():.2f}%")
print()
print("Saved:")
print("- anomaly_detection_results.csv")
print("- anomaly_summary.csv")
