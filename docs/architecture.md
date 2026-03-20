# Architecture Notes

## Pipeline Shape

- Raw structured CSV files land in `data/raw/`.
- The ETL package reads the files, standardizes column names and types, removes duplicates, validates business rules, and writes cleaned outputs to `data/processed/`.
- A full-refresh load writes the final tables into a relational warehouse. SQLite is the default for local execution, and the loader accepts any SQLAlchemy-compatible database URL.

## Data Model

- `customers`: customer master data and signup dates, keyed by `customer_id`
- `accounts`: account ownership, status, type, and current balance, keyed by `account_id` and linked to `customers.customer_id`
- `merchants`: merchant reference data and merchant categories, keyed by `merchant_id`
- `transactions`: cleaned fact table with signed amounts and transaction-month rollups, keyed by `transaction_id` and linked to `account_id`, `customer_id`, and `merchant_id`

## Sample Data Contract

- The raw files intentionally include mixed date formats and one duplicate transaction row so the pipeline demonstrates normalization and deduplication.
- Customer, account, merchant, and transaction identifiers are referentially consistent across the source files.
- The committed sample size is small on purpose so the project runs quickly in interviews and local demos.

## Operational Decisions

- The project uses a deterministic local folder structure rather than environment-heavy orchestration.
- Validation fails fast at transform boundaries so bad raw data never reaches the warehouse.
- SQL analysis lives in `sql/analysis/` so the reporting layer is easy to inspect during interviews.
