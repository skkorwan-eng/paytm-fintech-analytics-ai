import numpy as np
import pandas as pd

np.random.seed(42)

# -----------------------------
# Credit applicant dataset
# -----------------------------
N = 400

age = np.random.randint(21, 60, N)
monthly_income = np.random.randint(15000, 150001, N)
existing_loans = np.random.randint(0, 5, N)
credit_utilization = np.round(np.random.uniform(0.05, 0.95, N), 2)
upi_inflow = np.random.randint(2000, 120001, N)
bounced_payments = np.random.poisson(1.2, N)
employment_type = np.random.choice(
    ["salaried", "self_employed", "gig"],
    size=N,
    p=[0.55, 0.30, 0.15]
)

credit_score = np.random.randint(300, 901, N).astype(float)

# 20% new-to-credit / thin-file applicants
thin_file_idx = np.random.choice(N, size=int(0.20 * N), replace=False)
credit_score[thin_file_idx] = np.nan

# Risk score
score_for_risk = np.where(np.isnan(credit_score), 600, credit_score)

risk_score = (
    0.35 * (900 - score_for_risk) / 600
    + 0.20 * credit_utilization
    + 0.15 * existing_loans / 4
    + 0.15 * bounced_payments / 5
    + 0.10 * (1 - monthly_income / 150000)
    + 0.05 * (employment_type == "gig")
)

# Add noise
risk_score += np.random.normal(0, 0.04, N)

# Force approximately 15–25% defaults
default_threshold = np.quantile(risk_score, 0.80)
default_flag = (risk_score >= default_threshold).astype(int)

credit_applicants = pd.DataFrame({
    "applicant_id": [f"A{i:04d}" for i in range(1, N + 1)],
    "age": age,
    "monthly_income_inr": monthly_income,
    "existing_loans_count": existing_loans,
    "credit_utilization_ratio": credit_utilization,
    "upi_monthly_inflow_inr": upi_inflow,
    "bounced_payments_count": bounced_payments,
    "employment_type": employment_type,
    "credit_bureau_score": credit_score,
    "default_flag": default_flag
})

credit_applicants.to_csv("credit_applicants.csv", index=False)

# -----------------------------
# Transaction behaviour dataset
# -----------------------------
normal_n = 250
anomaly_n = 15
total_n = normal_n + anomaly_n

timestamps = pd.date_range(
    "2026-01-01",
    periods=normal_n,
    freq="2h"
)

txn = pd.DataFrame({
    "transaction_id": [f"T{i:04d}" for i in range(1, normal_n + 1)],
    "user_id": np.random.choice(
        [f"U{i:04d}" for i in range(1, 101)],
        normal_n
    ),
    "amount_inr": np.round(np.random.uniform(100, 5000, normal_n), 2),
    "hour": timestamps.hour,
    "new_device": np.random.choice([0, 1], normal_n, p=[0.9, 0.1])
})

txn["unusual_hour"] = ((txn["hour"] < 6) | (txn["hour"] >= 23)).astype(int)

# Add 15 deliberately injected anomalies:
# new device + unusual hour + high amount
anomaly_indices = np.random.choice(
    normal_n,
    size=anomaly_n,
    replace=False
)

anomalies = txn.loc[anomaly_indices].copy()

anomalies["transaction_id"] = [
    f"T{i:04d}" for i in range(normal_n + 1, total_n + 1)
]
anomalies["amount_inr"] = np.round(
    np.random.uniform(25000, 75000, anomaly_n), 2
)
anomalies["hour"] = np.random.choice(
    [0, 1, 2, 3, 4, 5, 23],
    anomaly_n
)
anomalies["new_device"] = 1
anomalies["unusual_hour"] = 1

txn_behaviour = pd.concat(
    [txn, anomalies],
    ignore_index=True
)

txn_behaviour["high_amount"] = (
    txn_behaviour["amount_inr"] >= 20000
).astype(int)

txn_behaviour["is_anomaly"] = (
    (txn_behaviour["new_device"] == 1)
    & (txn_behaviour["unusual_hour"] == 1)
    & (txn_behaviour["high_amount"] == 1)
).astype(int)

txn_behaviour.to_csv("txn_behaviour.csv", index=False)

print("Data generation completed successfully.")
print(f"Applicants: {len(credit_applicants)}")
print(
    f"Missing bureau scores: "
    f"{credit_applicants['credit_bureau_score'].isna().sum()}"
)
print(
    f"Default rate: "
    f"{credit_applicants['default_flag'].mean() * 100:.2f}%"
)
print(f"Transaction rows: {len(txn_behaviour)}")
print(
    f"Injected anomalies: "
    f"{txn_behaviour['is_anomaly'].sum()}"
)