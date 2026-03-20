from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

import pandas as pd

from etl_pipeline.db import build_metadata, create_warehouse_engine

LOAD_ORDER: tuple[str, ...] = ("customers", "accounts", "merchants", "transactions")


def load_tables(processed_tables: dict[str, pd.DataFrame], database_url: str) -> None:
    _ensure_expected_tables(processed_tables, LOAD_ORDER, stage="load")
    engine = create_warehouse_engine(database_url)
    metadata, tables = build_metadata()

    with engine.begin() as connection:
        metadata.drop_all(connection, checkfirst=True)
        metadata.create_all(connection)

        for table_name in LOAD_ORDER:
            records = _prepare_records(processed_tables[table_name])
            if records:
                connection.execute(tables[table_name].insert(), records)


def _prepare_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    raw_records = cast(list[dict[str, Any]], frame.to_dict(orient="records"))
    for raw_record in raw_records:
        record = {column: _normalize_scalar(value) for column, value in raw_record.items()}
        records.append(record)
    return records


def _normalize_scalar(value: Any) -> object:
    if bool(pd.isna(value)):
        return None

    if isinstance(value, float):
        return Decimal(f"{value:.2f}")

    if isinstance(value, int):
        return value

    if hasattr(value, "item"):
        return value.item()

    return value


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
