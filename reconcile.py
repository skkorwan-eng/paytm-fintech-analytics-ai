import pandas as pd

def reconcile_payments(ledger_df, gateway_df):
    """
    Compare ledger and gateway payment exports using transaction_id.

    Returns four DataFrames:
      1. transactions missing in gateway
      2. extra transactions in gateway
      3. amount mismatches with computed difference
      4. status mismatches
    """
    ledger_ids = set(ledger_df["transaction_id"])
    gateway_ids = set(gateway_df["transaction_id"])

    missing_ids = ledger_ids - gateway_ids
    extra_ids = gateway_ids - ledger_ids
    common_ids = ledger_ids & gateway_ids

    missing_in_gateway = ledger_df[
        ledger_df["transaction_id"].isin(missing_ids)
    ].copy()

    extra_in_gateway = gateway_df[
        gateway_df["transaction_id"].isin(extra_ids)
    ].copy()

    ledger_common = ledger_df[
        ledger_df["transaction_id"].isin(common_ids)
    ][["transaction_id", "amount_inr", "status"]]

    gateway_common = gateway_df[
        gateway_df["transaction_id"].isin(common_ids)
    ][["transaction_id", "amount_inr", "status"]]

    merged = pd.merge(
        ledger_common,
        gateway_common,
        on="transaction_id",
        how="inner",
        suffixes=("_ledger", "_gateway")
    )

    amount_mismatches = merged[
        merged["amount_inr_ledger"] != merged["amount_inr_gateway"]
    ].copy()

    amount_mismatches["amount_difference"] = (
        amount_mismatches["amount_inr_gateway"]
        - amount_mismatches["amount_inr_ledger"]
    )

    status_mismatches = merged[
        merged["status_ledger"] != merged["status_gateway"]
    ].copy()

    return (
        missing_in_gateway,
        extra_in_gateway,
        amount_mismatches,
        status_mismatches
    )


if __name__ == "__main__":
    ledger_df = pd.read_csv("ledger.csv")
    gateway_df = pd.read_csv("gateway_export.csv")

    (
        missing_in_gateway,
        extra_in_gateway,
        amount_mismatches,
        status_mismatches
    ) = reconcile_payments(ledger_df, gateway_df)

    print("=" * 55)
    print("PAYTM PAYMENT RECONCILIATION")
    print("=" * 55)
    print(f"Ledger transactions       : {len(ledger_df)}")
    print(f"Gateway transactions      : {len(gateway_df)}")
    print(f"Missing in gateway        : {len(missing_in_gateway)}")
    print(f"Extra in gateway          : {len(extra_in_gateway)}")
    print(f"Amount mismatches         : {len(amount_mismatches)}")
    print(f"Status mismatches         : {len(status_mismatches)}")
    print("=" * 55)

    missing_in_gateway.to_csv("missing_in_gateway.csv", index=False)
    extra_in_gateway.to_csv("extra_in_gateway.csv", index=False)
    amount_mismatches.to_csv("amount_mismatches.csv", index=False)
    status_mismatches.to_csv("status_mismatches.csv", index=False)

    print("Four discrepancy CSV files saved successfully.")
