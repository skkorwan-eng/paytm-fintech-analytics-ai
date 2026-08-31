from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression

INPUT = "credit_applicants.csv"
OUTPUT = "applicant_risk_pricing.csv"

df = pd.read_csv(INPUT)
df["is_thin_file"] = df["credit_bureau_score"].isna().astype(int)

X = df.drop(columns=["default", "applicant_id"])
y = df["default"]

numeric_features = [
    "age", "monthly_income_inr", "existing_loans_count",
    "credit_utilization_ratio", "upi_monthly_inflow_inr",
    "bounced_payments_count", "credit_bureau_score", "is_thin_file"
]
categorical_features = ["employment_type"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, stratify=y, random_state=42
)

preprocessor = ColumnTransformer([
    ("num", Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ]), numeric_features),
    ("cat", Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ]), categorical_features)
])

model = Pipeline([
    ("preprocessor", preprocessor),
    ("model", LogisticRegression(max_iter=2000, random_state=42))
])
model.fit(X_train, y_train)

df["default_probability"] = model.predict_proba(X)[:, 1]

def risk_band(p):
    if p < 0.10:
        return "Low"
    if p < 0.25:
        return "Medium"
    return "High"

df["risk_band"] = df["default_probability"].apply(risk_band)

def pricing(row):
    p = row["default_probability"]
    band = row["risk_band"]
    if band == "Low":
        lo, hi, apr = 10000, 50000, 12
        frac = np.clip(1 - p / 0.10, 0, 1)
    elif band == "Medium":
        lo, hi, apr = 5000, 25000, 18
        frac = np.clip((0.25 - p) / 0.15, 0, 1)
    else:
        lo, hi, apr = 1000, 10000, 28
        frac = np.clip((0.50 - p) / 0.25, 0, 1)
    limit = int(round(lo + frac * (hi - lo)))
    return pd.Series([limit, apr])

df[["recommended_limit_inr", "recommended_apr_percent"]] = df.apply(pricing, axis=1)

cols = [
    "applicant_id", "default_probability", "risk_band",
    "recommended_limit_inr", "recommended_apr_percent"
]
df[cols].to_csv(OUTPUT, index=False)

summary = (
    df.groupby("risk_band")
      .agg(
          applicants=("applicant_id", "count"),
          avg_default_probability=("default_probability", "mean"),
          avg_recommended_limit_inr=("recommended_limit_inr", "mean"),
          apr_percent=("recommended_apr_percent", "first")
      )
      .reset_index()
)
summary.to_csv("risk_band_summary.csv", index=False)

guide = """# Risk Banding & Pricing Guide

Risk bands:
- Low: predicted default probability < 10%
- Medium: 10% to <25%
- High: >=25%

Illustrative pricing:
- Low: INR 10,000–50,000 limit; 12% APR
- Medium: INR 5,000–25,000 limit; 18% APR
- High: INR 1,000–10,000 limit; 28% APR

Rationale: higher predicted default risk receives a lower recommended limit
and higher APR. These are illustrative policy assumptions and should be
validated using actual loss rates, affordability, cost of funds, regulations,
and fairness monitoring.
"""
Path("risk_pricing_guide.md").write_text(guide, encoding="utf-8")

print("RISK BANDING & PRICING COMPLETE")
print(summary.to_string(index=False))
print("\nSaved:")
print("- applicant_risk_pricing.csv")
print("- risk_band_summary.csv")
print("- risk_pricing_guide.md")
