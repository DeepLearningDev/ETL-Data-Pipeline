from __future__ import annotations

import pandas as pd
import pytest

from etl_pipeline.transform import transform_all_tables, transform_transactions
from etl_pipeline.validate import DataValidationError


def test_transform_transactions_normalizes_financial_values() -> None:
    raw_transactions = pd.DataFrame(
        {
            "Transaction ID": ["TXN1", "TXN1"],
            "Account ID": ["ACC1", "ACC1"],
            "Customer ID": ["CUST1", "CUST1"],
            "Merchant ID": ["MER1", "MER1"],
            "Transaction Date": ["2026-02-04", "2026-02-04"],
            "Posted Date": ["2026-02-05", "2026-02-05"],
            "Amount": ["$42.75", "$42.75"],
            "Direction": ["debit", "debit"],
            "Category": [" coffee shop ", " coffee shop "],
            "Description": ["", ""],
        }
    )

    transformed = transform_transactions(raw_transactions)

    assert transformed["transaction_id"].tolist() == ["TXN1"]
    assert transformed.loc[0, "amount"] == 42.75
    assert transformed.loc[0, "signed_amount"] == -42.75
    assert transformed.loc[0, "category"] == "Dining"
    assert transformed.loc[0, "description"] == "Not provided"
    assert transformed.loc[0, "transaction_month"] == "2026-02"


def test_transform_transactions_rejects_non_numeric_amount() -> None:
    raw_transactions = pd.DataFrame(
        {
            "Transaction ID": ["TXN9"],
            "Account ID": ["ACC1"],
            "Customer ID": ["CUST1"],
            "Merchant ID": ["MER1"],
            "Transaction Date": ["2026-02-04"],
            "Posted Date": ["2026-02-05"],
            "Amount": ["not-a-number"],
            "Direction": ["debit"],
            "Category": ["groceries"],
            "Description": ["Weekly groceries"],
        }
    )

    with pytest.raises(DataValidationError, match="transactions.not_null: amount"):
        transform_transactions(raw_transactions)


def test_transform_all_tables_rejects_missing_required_table() -> None:
    with pytest.raises(ValueError, match="Missing table\\(s\\) for transform stage: merchants"):
        transform_all_tables(
            {
                "customers": pd.DataFrame(),
                "accounts": pd.DataFrame(),
                "transactions": pd.DataFrame(),
            }
        )
