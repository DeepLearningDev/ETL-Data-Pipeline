# Financial ETL Pipeline Showcase

Production-minded ETL showcase for a Data Engineer interview. The project ingests structured banking CSVs, cleans and validates them, writes analytics-ready outputs, loads a relational warehouse, and ships reusable SQL for reporting.

## Resume-Aligned Highlights

- Developed an end-to-end ETL pipeline for ingesting, transforming, and storing structured financial data.
- Automated data cleaning, schema validation, deduplication, and repeatable loading into a relational database.
- Designed SQL queries for reporting on monthly totals, spend by category, high-value transactions, and customer-account performance.

## Business Scenario

The dataset models personal banking activity across customers, accounts, merchants, and transactions. It is synthetic, deterministic, and included in the repository so the project runs out of the box.

## Architecture

```mermaid
flowchart LR
    A["Raw CSVs<br/>data/raw"] --> B["Extract<br/>pandas readers"]
    B --> C["Transform + Validate<br/>clean types, normalize categories, drop duplicates"]
    C --> D["Processed CSVs<br/>data/processed"]
    C --> E["SQLite Warehouse<br/>data/warehouse/financial_warehouse.db"]
    E --> F["SQL Analysis Queries<br/>sql/analysis"]
```

More detail is captured in [docs/architecture.md](C:/Users/Kaleb/Codex%20Projects/DeepLearningDev/ETL-Data-Pipeline/docs/architecture.md).

## Tech Stack

- Python 3.11+
- pandas
- SQLAlchemy
- SQLite by default, with a swappable SQLAlchemy database URL
- pytest
- ruff
- mypy

## Repository Layout

```text
.
|-- data/
|   |-- raw/
|   |-- processed/
|   `-- warehouse/
|-- docs/
|-- sql/analysis/
|-- src/etl_pipeline/
`-- tests/
```

## ETL Flow

1. Extract raw CSV files from `data/raw/`.
2. Standardize column names into snake_case.
3. Clean whitespace, parse dates, coerce numeric fields, normalize category labels, and remove duplicate business keys.
4. Validate required fields, non-null identifiers, numeric amounts, and valid transaction directions.
5. Write analytics-ready CSV outputs to `data/processed/`.
6. Run a full-refresh load into the warehouse database.

## Warehouse Schema

| Table | Purpose | Key fields |
| --- | --- | --- |
| `customers` | Customer master data | `customer_id` |
| `accounts` | Account dimension | `account_id`, `customer_id` |
| `merchants` | Merchant dimension | `merchant_id` |
| `transactions` | Cleaned fact table | `transaction_id`, `account_id`, `customer_id`, `merchant_id`, `signed_amount`, `transaction_month` |

## How To Run Locally

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .[dev]
python -m etl_pipeline run
```

You can swap the warehouse target without changing code:

```powershell
python -m etl_pipeline run --database-url "postgresql+psycopg://user:password@localhost:5432/financial_demo"
```

## Quality Gates

```powershell
python -m ruff format --check .
python -m ruff check .
python -m mypy
python -m pytest
python -m build
```

## SQL Analytics Included

- [monthly_transaction_totals.sql](C:/Users/Kaleb/Codex%20Projects/DeepLearningDev/ETL-Data-Pipeline/sql/analysis/monthly_transaction_totals.sql)
- [spend_by_category.sql](C:/Users/Kaleb/Codex%20Projects/DeepLearningDev/ETL-Data-Pipeline/sql/analysis/spend_by_category.sql)
- [high_value_transactions.sql](C:/Users/Kaleb/Codex%20Projects/DeepLearningDev/ETL-Data-Pipeline/sql/analysis/high_value_transactions.sql)
- [customer_account_summaries.sql](C:/Users/Kaleb/Codex%20Projects/DeepLearningDev/ETL-Data-Pipeline/sql/analysis/customer_account_summaries.sql)
- [merchant_spend_trends.sql](C:/Users/Kaleb/Codex%20Projects/DeepLearningDev/ETL-Data-Pipeline/sql/analysis/merchant_spend_trends.sql)

## Sample Output Snapshot

After a successful run, the pipeline writes four processed CSVs and a warehouse database, with these row counts:

| Table | Rows |
| --- | ---: |
| customers | 5 |
| accounts | 6 |
| merchants | 9 |
| transactions | 25 |

Example result from `sql/analysis/monthly_transaction_totals.sql`:

| Month | Debit Total | Credit Total | Net Amount |
| --- | ---: | ---: | ---: |
| 2026-01 | 696.83 | 3250.00 | 2553.17 |
| 2026-02 | 411.46 | 2800.00 | 2388.54 |
| 2026-03 | 769.26 | 3250.00 | 2480.74 |
| 2026-04 | 173.81 | 2900.00 | 2726.19 |

## Interview Talking Points

- Why SQLite was chosen for the default local demo and how the loader remains PostgreSQL-ready.
- How validation prevents malformed dates, missing IDs, and non-numeric amounts from reaching the warehouse.
- How `signed_amount` and `transaction_month` simplify downstream reporting.
- How the SQL folder separates the reporting layer from the ETL code so reviewers can inspect business logic quickly.
