from __future__ import annotations

from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Index,
    MetaData,
    Numeric,
    String,
    Table,
    create_engine,
)
from sqlalchemy.engine import Engine


def create_warehouse_engine(database_url: str) -> Engine:
    return create_engine(database_url, future=True)


def build_metadata() -> tuple[MetaData, dict[str, Table]]:
    metadata = MetaData()

    customers = Table(
        "customers",
        metadata,
        Column("customer_id", String(20), primary_key=True),
        Column("first_name", String(80), nullable=False),
        Column("last_name", String(80), nullable=False),
        Column("segment", String(40), nullable=False),
        Column("city", String(80), nullable=False),
        Column("state", String(2), nullable=False),
        Column("signup_date", Date(), nullable=False),
    )

    accounts = Table(
        "accounts",
        metadata,
        Column("account_id", String(20), primary_key=True),
        Column("customer_id", String(20), ForeignKey("customers.customer_id"), nullable=False),
        Column("account_type", String(20), nullable=False),
        Column("opened_date", Date(), nullable=False),
        Column("status", String(20), nullable=False),
        Column("current_balance", Numeric(12, 2), nullable=False),
    )

    merchants = Table(
        "merchants",
        metadata,
        Column("merchant_id", String(20), primary_key=True),
        Column("merchant_name", String(120), nullable=False),
        Column("merchant_category", String(40), nullable=False),
        Column("city", String(80), nullable=False),
        Column("state", String(2), nullable=False),
    )

    transactions = Table(
        "transactions",
        metadata,
        Column("transaction_id", String(20), primary_key=True),
        Column("account_id", String(20), ForeignKey("accounts.account_id"), nullable=False),
        Column("customer_id", String(20), ForeignKey("customers.customer_id"), nullable=False),
        Column("merchant_id", String(20), ForeignKey("merchants.merchant_id"), nullable=False),
        Column("transaction_date", Date(), nullable=False),
        Column("posted_date", Date(), nullable=False),
        Column("amount", Numeric(12, 2), nullable=False),
        Column("direction", String(10), nullable=False),
        Column("category", String(40), nullable=False),
        Column("description", String(200), nullable=False),
        Column("signed_amount", Numeric(12, 2), nullable=False),
        Column("transaction_month", String(7), nullable=False),
    )

    Index("ix_transactions_transaction_date", transactions.c.transaction_date)
    Index("ix_transactions_category", transactions.c.category)
    Index("ix_transactions_merchant_id", transactions.c.merchant_id)

    return metadata, {
        "customers": customers,
        "accounts": accounts,
        "merchants": merchants,
        "transactions": transactions,
    }
