import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, classification_report, confusion_matrix, roc_curve
)

# ------------------------------------------------------------
# Part 2 — Credit Risk & Lending ML
# EDA + preprocessing + Logistic Regression + Decision Tree
# ------------------------------------------------------------

df = pd.read_csv("credit_applicants.csv")

# Task 1: report default rate and create thin-file flag BEFORE imputation.
default_rate = df["default"].mean() * 100
missing_bureau_pct = df["credit_bureau_score"].isna().mean() * 100
df["is_thin_file"] = df["credit_bureau_score"].isna().astype(int)

print("=" * 60)
print("CREDIT RISK EDA")
print("=" * 60)
print(f"Rows: {len(df)}")
print(f"Measured default rate: {default_rate:.2f}%")
print(f"Missing credit_bureau_score: {df['credit_bureau_score'].isna().sum()} "
      f"({missing_bureau_pct:.2f}%)")
print(f"Thin-file applicants: {df['is_thin_file'].sum()}")
print()

# Target and features
X = df.drop(columns=["default", "applicant_id"])
y = df["default"]

numeric_features = [
    "age",
    "monthly_income_inr",
    "existing_loans_count",
    "credit_utilization_ratio",
    "upi_monthly_inflow_inr",
    "bounced_payments_count",
    "credit_bureau_score",
    "is_thin_file",
]
categorical_features = ["employment_type"]

# Task 2: stratified split first; all fitted preprocessing happens after split.
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.20,
    stratify=y,
    random_state=42
)

numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])

categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore")),
])

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features),
    ]
)

models = {
    "Logistic Regression": LogisticRegression(
        max_iter=2000,
        random_state=42
    ),
    "Decision Tree": DecisionTreeClassifier(
        max_depth=5,
        min_samples_leaf=10,
        random_state=42
    ),
}

results = []
roc_data = {}

for name, model in models.items():
    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    pipeline.fit(X_train, y_train)

    pred = pipeline.predict(X_test)
    prob = pipeline.predict_proba(X_test)[:, 1]

    metrics = {
        "model": name,
        "accuracy": accuracy_score(y_test, pred),
        "precision": precision_score(y_test, pred, zero_division=0),
        "recall": recall_score(y_test, pred, zero_division=0),
        "f1": f1_score(y_test, pred, zero_division=0),
        "roc_auc": roc_auc_score(y_test, prob),
    }
    results.append(metrics)

    fpr, tpr, _ = roc_curve(y_test, prob)
    roc_data[name] = (fpr, tpr, metrics["roc_auc"])

    print("-" * 60)
    print(name)
    print(classification_report(y_test, pred, zero_division=0))
    print("Confusion matrix:")
    print(confusion_matrix(y_test, pred))
    print(f"ROC-AUC: {metrics['roc_auc']:.4f}")

results_df = pd.DataFrame(results)
results_df.to_csv("model_comparison.csv", index=False)

print()
print("=" * 60)
print("MODEL COMPARISON")
print("=" * 60)
print(results_df.to_string(index=False))

# Save ROC curve.
plt.figure(figsize=(8, 6))
for name, (fpr, tpr, auc) in roc_data.items():
    plt.plot(fpr, tpr, label=f"{name} (AUC={auc:.3f})")
plt.plot([0, 1], [0, 1], linestyle="--", label="Random baseline")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("Credit Risk Model ROC Curves")
plt.legend()
plt.tight_layout()
plt.savefig("roc_curves.png", dpi=180)
plt.close()

# Save EDA summary.
eda = pd.DataFrame({
    "metric": [
        "rows",
        "default_rate_pct",
        "missing_bureau_count",
        "missing_bureau_pct",
        "thin_file_count",
        "train_rows",
        "test_rows"
    ],
    "value": [
        len(df),
        default_rate,
        df["credit_bureau_score"].isna().sum(),
        missing_bureau_pct,
        df["is_thin_file"].sum(),
        len(X_train),
        len(X_test)
    ]
})
eda.to_csv("eda_summary.csv", index=False)

print()
print("Saved:")
print("- eda_summary.csv")
print("- model_comparison.csv")
print("- roc_curves.png")
