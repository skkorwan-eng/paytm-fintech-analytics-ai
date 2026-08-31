# Paytm Payments & Fraud Analytics

## Project Overview

This project analyzes a synthetic Paytm-style payments dataset covering merchants, users, transactions, gateway reconciliation, payment trends, and fraud-related patterns.

The project is organized into:
- Part 1: Payments & Fraud Analytics
- Part 2: Credit Risk ML
- Part 3: AI Advisory & Blockchain/Crypto Risk

## Part 1 — Current Status

The following data files were generated and used:

- `merchants.csv` — 40 merchants
- `users.csv` — established users plus newly created burner accounts
- `ledger.csv` — 547 transactions
- `gateway_export.csv` — deliberately discrepant gateway copy
- `paytm_payments.db` — normalized SQLite database
- `sql_queries.sql` — SQL analysis queries
- `sql_outputs.txt` — saved SQL outputs
- `reconcile.py` — ledger/gateway reconciliation script
- `dashboard.py` — dashboard generation script

## SQLite Database

Database: `paytm_payments.db`

Main normalized tables:
- `merchants(merchant_id PRIMARY KEY, ...)`
- `users(user_id PRIMARY KEY, signup_date)`
- `transactions(transaction_id PRIMARY KEY, user_id FOREIGN KEY, merchant_id FOREIGN KEY, ...)`

Foreign keys and indexes are used for transaction/user/merchant relationships and transaction-time access.

## Reconciliation

Run:

```bash
python reconcile.py
```

The script compares `ledger.csv` with `gateway_export.csv` using `transaction_id` and reports:

- Missing transactions in gateway
- Extra transactions in gateway
- Amount mismatches
- Status mismatches

It also saves:

- `missing_in_gateway.csv`
- `extra_in_gateway.csv`
- `amount_mismatches.csv`
- `status_mismatches.csv`

The generated reconciliation run produced:

- Ledger transactions: 547
- Gateway transactions: 530
- Missing in gateway: 27
- Extra in gateway: 10
- Amount mismatches: 16
- Status mismatches: 9

## Dashboard

Run:

```bash
python dashboard.py
```

The script creates the `dashboard_outputs/` directory containing:

- `01_headline.png`
- `02_trends.png`
- `03_breakdown.png`
- `04_details.png`
- `headline_metrics.csv`

The current dashboard run produced:

- Total GMV: ₹382,603
- Overall success rate: 85.56%
- Reconciliation match rate: 90.49%
- Chargeback ratio: 5.12%

### Dashboard Layers

1. **Headline** — GMV, success rate, reconciliation match rate, and chargeback ratio.
2. **Trends** — daily GMV and daily chargebacks.
3. **Breakdown** — GMV by payment method and merchant category.
4. **Details** — top merchants by transaction count and a high-risk flag for merchants with chargeback ratio above 1%.

## Python Setup

Python 3 is required.

Install the dashboard dependency with:

```bash
python -m pip install matplotlib
```

The data-generation and reconciliation scripts use pandas/numpy.

## Data Generation

Run:

```bash
python generate_data.py
```

This generates the core CSV datasets, including the deliberately discrepant `gateway_export.csv`.

## Project Structure

```text
payments_fraud_analytics/
├── generate_data.py
├── merchants.csv
├── users.csv
├── ledger.csv
├── gateway_export.csv
├── paytm_payments.db
├── sql_queries.sql
├── sql_outputs.txt
├── reconcile.py
├── missing_in_gateway.csv
├── extra_in_gateway.csv
├── amount_mismatches.csv
├── status_mismatches.csv
├── dashboard.py
└── dashboard_outputs/
    ├── 01_headline.png
    ├── 02_trends.png
    ├── 03_breakdown.png
    ├── 04_details.png
    └── headline_metrics.csv
```

## Design Notes

- The dataset is synthetic and reproducible using random seed `42`.
- The gateway export intentionally contains missing rows, extra rows, amount differences, and status differences to demonstrate reconciliation.
- Reconciliation matching is based on `transaction_id`.
- The dashboard's reconciliation match rate requires a transaction to exist in both files with the same amount and status.
- The merchant high-risk dashboard flag uses a count-based chargeback ratio greater than 1%.

## Next Work

Part 1 analytics and reconciliation outputs are prepared. The next project stage is Part 2 — Credit Risk ML, followed by the Part 3 AI advisory and blockchain/crypto risk components.
