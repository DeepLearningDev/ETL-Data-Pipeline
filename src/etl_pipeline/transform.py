from __future__ import annotations

import re
from typing import Any

import pandas as pd

from etl_pipeline.validate import (
    ensure_allowed_values,
    ensure_not_null,
    ensure_numeric,
    ensure_parsed_dates,
    ensure_required_columns,
)

CATEGORY_NORMALIZATION: dict[str, str] = {
    "atm": "Cash Withdrawal",
    "cash": "Cash Withdrawal",
    "coffee shop": "Dining",
    "dining": "Dining",
    "entertainment": "Entertainment",
    "fuel": "Transportation",
    "gas": "Transportation",
    "grocery": "Groceries",
    "groceries": "Groceries",
    "income": "Income",
    "paycheck": "Income",
    "restaurants": "Dining",
    "salary": "Income",
    "shopping": "Shopping",
    "software": "Software",
    "subscription": "Subscriptions",
    "subscriptions": "Subscriptions",
    "travel": "Travel",
    "utilities": "Utilities",
}

ACCOUNT_TYPE_NORMALIZATION: dict[str, str] = {
    "checking": "Checking",
    "credit": "Credit",
    "savings": "Savings",
}

ACCOUNT_STATUS_NORMALIZATION: dict[str, str] = {
    "active": "Open",
    "closed": "Closed",
    "delinquent": "Delinquent",
    "open": "Open",
}

TABLE_ORDER: tuple[str, ...] = ("customers", "accounts", "merchants", "transactions")


def transform_all_tables(raw_tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    _ensure_expected_tables(raw_tables, TABLE_ORDER, stage="transform")
    return {
        "customers": transform_customers(raw_tables["customers"]),
        "accounts": transform_accounts(raw_tables["accounts"]),
        "merchants": transform_merchants(raw_tables["merchants"]),
        "transactions": transform_transactions(raw_tables["transactions"]),
    }


def transform_customers(frame: pd.DataFrame) -> pd.DataFrame:
    dataset = "customers"
    required_columns = [
        "customer_id",
        "first_name",
        "last_name",
        "segment",
        "city",
        "state",
        "signup_date",
    ]

    transformed = _prepare_frame(frame)
    ensure_required_columns(transformed, dataset=dataset, required_columns=required_columns)

    transformed = transformed[required_columns].copy()
    transformed["signup_date"] = pd.to_datetime(
        transformed["signup_date"], errors="coerce", format="mixed"
    )
    transformed["segment"] = transformed["segment"].map(_title_case_series)
    transformed["city"] = transformed["city"].map(_title_case_series)
    transformed["state"] = transformed["state"].astype("string").str.upper()
    transformed = _deduplicate(transformed, ["customer_id"])

    ensure_not_null(transformed, dataset=dataset, columns=required_columns)
    ensure_parsed_dates(transformed, dataset=dataset, columns=["signup_date"])

    transformed["signup_date"] = transformed["signup_date"].dt.date
    return transformed.sort_values("customer_id").reset_index(drop=True)


def transform_accounts(frame: pd.DataFrame) -> pd.DataFrame:
    dataset = "accounts"
    required_columns = [
        "account_id",
        "customer_id",
        "account_type",
        "opened_date",
        "status",
        "current_balance",
    ]

    transformed = _prepare_frame(frame)
    ensure_required_columns(transformed, dataset=dataset, required_columns=required_columns)

    transformed = transformed[required_columns].copy()
    transformed["account_type"] = transformed["account_type"].map(
        lambda value: _normalize_from_mapping(value, ACCOUNT_TYPE_NORMALIZATION)
    )
    transformed["status"] = transformed["status"].map(
        lambda value: _normalize_from_mapping(value, ACCOUNT_STATUS_NORMALIZATION)
    )
    transformed["opened_date"] = pd.to_datetime(
        transformed["opened_date"], errors="coerce", format="mixed"
    )
    transformed["current_balance"] = _coerce_numeric(transformed["current_balance"])
    transformed = _deduplicate(transformed, ["account_id"])

    ensure_not_null(
        transformed,
        dataset=dataset,
        columns=["account_id", "customer_id", "account_type", "opened_date", "status"],
    )
    ensure_parsed_dates(transformed, dataset=dataset, columns=["opened_date"])
    ensure_numeric(transformed, dataset=dataset, columns=["current_balance"])
    ensure_allowed_values(
        transformed,
        dataset=dataset,
        column="account_type",
        allowed_values=ACCOUNT_TYPE_NORMALIZATION.values(),
    )
    ensure_allowed_values(
        transformed,
        dataset=dataset,
        column="status",
        allowed_values=ACCOUNT_STATUS_NORMALIZATION.values(),
    )

    transformed["opened_date"] = transformed["opened_date"].dt.date
    transformed["current_balance"] = transformed["current_balance"].round(2)
    return transformed.sort_values("account_id").reset_index(drop=True)


def transform_merchants(frame: pd.DataFrame) -> pd.DataFrame:
    dataset = "merchants"
    required_columns = ["merchant_id", "merchant_name", "merchant_category", "city", "state"]

    transformed = _prepare_frame(frame)
    ensure_required_columns(transformed, dataset=dataset, required_columns=required_columns)

    transformed = transformed[required_columns].copy()
    transformed["merchant_name"] = transformed["merchant_name"].map(_title_case_series)
    transformed["merchant_category"] = transformed["merchant_category"].map(_normalize_category)
    transformed["city"] = transformed["city"].map(_title_case_series)
    transformed["state"] = transformed["state"].astype("string").str.upper()
    transformed = _deduplicate(transformed, ["merchant_id"])

    ensure_not_null(transformed, dataset=dataset, columns=required_columns)
    return transformed.sort_values("merchant_id").reset_index(drop=True)


def transform_transactions(frame: pd.DataFrame) -> pd.DataFrame:
    dataset = "transactions"
    required_columns = [
        "transaction_id",
        "account_id",
        "customer_id",
        "merchant_id",
        "transaction_date",
        "posted_date",
        "amount",
        "direction",
        "category",
        "description",
    ]

    transformed = _prepare_frame(frame)
    ensure_required_columns(transformed, dataset=dataset, required_columns=required_columns)

    transformed = transformed[required_columns].copy()
    transformed["transaction_date"] = pd.to_datetime(
        transformed["transaction_date"], errors="coerce", format="mixed"
    )
    transformed["posted_date"] = pd.to_datetime(
        transformed["posted_date"], errors="coerce", format="mixed"
    )
    transformed["amount"] = _coerce_numeric(transformed["amount"])
    transformed["direction"] = transformed["direction"].astype("string").str.lower()
    transformed["category"] = transformed["category"].map(_normalize_category)
    transformed["description"] = transformed["description"].fillna("Not provided")
    transformed = _deduplicate(transformed, ["transaction_id"])

    ensure_not_null(
        transformed,
        dataset=dataset,
        columns=[
            "transaction_id",
            "account_id",
            "customer_id",
            "merchant_id",
            "transaction_date",
            "posted_date",
            "amount",
            "direction",
            "category",
        ],
    )
    ensure_parsed_dates(
        transformed,
        dataset=dataset,
        columns=["transaction_date", "posted_date"],
    )
    ensure_numeric(transformed, dataset=dataset, columns=["amount"])
    ensure_allowed_values(
        transformed,
        dataset=dataset,
        column="direction",
        allowed_values=("credit", "debit"),
    )

    transformed["amount"] = transformed["amount"].round(2)
    transformed["signed_amount"] = transformed["amount"].where(
        transformed["direction"].eq("credit"),
        -transformed["amount"],
    )
    transformed["transaction_month"] = transformed["transaction_date"].dt.strftime("%Y-%m")
    transformed["transaction_date"] = transformed["transaction_date"].dt.date
    transformed["posted_date"] = transformed["posted_date"].dt.date
    transformed["signed_amount"] = transformed["signed_amount"].round(2)

    ordered_columns = required_columns + ["signed_amount", "transaction_month"]
    return (
        transformed[ordered_columns]
        .sort_values(["transaction_date", "transaction_id"])
        .reset_index(drop=True)
    )


def _prepare_frame(frame: pd.DataFrame) -> pd.DataFrame:
    transformed = frame.rename(columns=lambda column: _to_snake_case(str(column))).copy()
    for column in transformed.select_dtypes(include=["object", "string"]).columns:
        series = transformed[column].astype("string").str.strip()
        transformed[column] = series.mask(series.eq(""), pd.NA)
    return transformed


def _deduplicate(frame: pd.DataFrame, subset: list[str]) -> pd.DataFrame:
    return frame.drop_duplicates(subset=subset, keep="first").copy()


def _to_snake_case(value: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-z]+", "_", value.strip())
    return re.sub(r"_+", "_", cleaned).strip("_").lower()


def _coerce_numeric(series: pd.Series) -> pd.Series:
    cleaned = series.astype("string").str.replace(r"[^0-9.\-]", "", regex=True)
    return pd.to_numeric(cleaned, errors="coerce")


def _normalize_category(value: Any) -> object:
    return _normalize_from_mapping(value, CATEGORY_NORMALIZATION, fallback="title")


def _normalize_from_mapping(
    value: Any,
    mapping: dict[str, str],
    *,
    fallback: str = "preserve",
) -> object:
    if bool(pd.isna(value)):
        return pd.NA

    normalized_key = str(value).strip().lower()
    if normalized_key in mapping:
        return mapping[normalized_key]

    if fallback == "title":
        return normalized_key.title()

    return value


def _title_case_series(value: Any) -> object:
    if bool(pd.isna(value)):
        return pd.NA
    return str(value).strip().title()


def _ensure_expected_tables(
    tables: dict[str, pd.DataFrame],
    expected_tables: tuple[str, ...],
    *,
    stage: str,
) -> None:
    missing_tables = [table_name for table_name in expected_tables if table_name not in tables]
    if missing_tables:
        missing = ", ".join(missing_tables)
        msg = f"Missing table(s) for {stage} stage: {missing}"
        raise ValueError(msg)
