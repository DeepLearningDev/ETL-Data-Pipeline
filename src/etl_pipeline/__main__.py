from __future__ import annotations

import argparse
from pathlib import Path

from etl_pipeline.config import PipelineConfig
from etl_pipeline.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the financial ETL showcase pipeline against local CSV inputs."
    )
    parser.add_argument("command", nargs="?", default="run", choices=["run"])
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root that contains the data/, src/, and sql/ folders.",
    )
    parser.add_argument("--raw-data-dir", type=Path, default=None)
    parser.add_argument("--processed-data-dir", type=Path, default=None)
    parser.add_argument("--warehouse-dir", type=Path, default=None)
    parser.add_argument("--database-url", default=None)
    parser.add_argument("--log-level", default="INFO")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    config = PipelineConfig.from_project_root(
        project_root=args.project_root,
        raw_data_dir=args.raw_data_dir,
        processed_data_dir=args.processed_data_dir,
        warehouse_dir=args.warehouse_dir,
        database_url=args.database_url,
        log_level=args.log_level,
    )

    result = run_pipeline(config)
    print("Pipeline complete.")
    for table_name, row_count in result.row_counts.items():
        print(f" - {table_name}: {row_count} rows")
    print(f" - database: {result.database_url}")


if __name__ == "__main__":
    main()
