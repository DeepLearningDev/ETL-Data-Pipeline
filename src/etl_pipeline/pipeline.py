from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from etl_pipeline.config import PipelineConfig
from etl_pipeline.extract import read_source_tables
from etl_pipeline.load import load_tables
from etl_pipeline.transform import TABLE_ORDER, transform_all_tables

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class PipelineRunResult:
    row_counts: dict[str, int]
    processed_files: dict[str, Path]
    database_url: str


def run_pipeline(config: PipelineConfig) -> PipelineRunResult:
    _configure_logging(config.log_level)
    config.ensure_directories()

    LOGGER.info("Reading raw CSV files from %s", config.raw_data_dir)
    raw_tables = read_source_tables(config.raw_data_dir)

    LOGGER.info("Transforming and validating source tables")
    processed_tables = transform_all_tables(raw_tables)

    LOGGER.info("Writing analytics-ready CSV outputs to %s", config.processed_data_dir)
    processed_files = write_processed_tables(processed_tables, config.processed_data_dir)

    LOGGER.info("Loading warehouse tables into %s", config.database_url)
    load_tables(processed_tables, config.database_url)

    row_counts = {table_name: len(processed_tables[table_name]) for table_name in TABLE_ORDER}
    LOGGER.info("Pipeline completed successfully with row counts: %s", row_counts)

    return PipelineRunResult(
        row_counts=row_counts,
        processed_files=processed_files,
        database_url=config.database_url,
    )


def write_processed_tables(
    processed_tables: dict[str, pd.DataFrame],
    processed_data_dir: Path,
) -> dict[str, Path]:
    file_paths: dict[str, Path] = {}
    for table_name, frame in processed_tables.items():
        file_path = processed_data_dir / f"{table_name}.csv"
        frame.to_csv(file_path, index=False)
        file_paths[table_name] = file_path
    return file_paths


def _configure_logging(log_level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        force=True,
    )
