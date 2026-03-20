from __future__ import annotations

import shutil
import sqlite3
from pathlib import Path

from etl_pipeline.config import PipelineConfig
from etl_pipeline.pipeline import run_pipeline


def test_pipeline_run_creates_outputs_and_loads_sqlite(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    shutil.copytree(repo_root / "data" / "raw", tmp_path / "data" / "raw")

    config = PipelineConfig.from_project_root(tmp_path)
    result = run_pipeline(config)

    assert result.row_counts == {
        "customers": 5,
        "accounts": 6,
        "merchants": 9,
        "transactions": 25,
    }

    processed_transactions = tmp_path / "data" / "processed" / "transactions.csv"
    assert processed_transactions.exists()

    warehouse_path = tmp_path / "data" / "warehouse" / "financial_warehouse.db"
    assert warehouse_path.exists()

    with sqlite3.connect(warehouse_path) as connection:
        transaction_count = connection.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        dining_category = connection.execute(
            "SELECT category FROM transactions WHERE transaction_id = 'TXN2007'"
        ).fetchone()[0]

    assert transaction_count == 25
    assert dining_category == "Dining"
