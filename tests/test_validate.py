from __future__ import annotations

import pandas as pd
import pytest

from etl_pipeline.validate import (
    DataValidationError,
    ensure_allowed_values,
    ensure_required_columns,
)


def test_ensure_required_columns_reports_missing_fields() -> None:
    frame = pd.DataFrame({"customer_id": ["CUST001"]})

    with pytest.raises(DataValidationError, match="Missing columns: first_name"):
        ensure_required_columns(
            frame,
            dataset="customers",
            required_columns=["customer_id", "first_name"],
        )


def test_ensure_allowed_values_rejects_unexpected_direction() -> None:
    frame = pd.DataFrame({"direction": ["refund"]})

    with pytest.raises(DataValidationError, match="unsupported value"):
        ensure_allowed_values(
            frame,
            dataset="transactions",
            column="direction",
            allowed_values=("credit", "debit"),
        )
