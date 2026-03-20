from __future__ import annotations

from pathlib import Path

import pandas as pd

SOURCE_FILES: dict[str, str] = {
    "customers": "customers.csv",
    "accounts": "accounts.csv",
    "merchants": "merchants.csv",
    "transactions": "transactions.csv",
}


def read_source_tables(raw_data_dir: Path) -> dict[str, pd.DataFrame]:
    tables: dict[str, pd.DataFrame] = {}
    for table_name, file_name in SOURCE_FILES.items():
        file_path = raw_data_dir / file_name
        if not file_path.exists():
            msg = f"Expected source file does not exist: {file_path}"
            raise FileNotFoundError(msg)
        tables[table_name] = pd.read_csv(file_path)
    return tables
