from datetime import date
from decimal import Decimal

from app.db.connection import (
    execute_db,
    fetch_multiple_records,
    fetch_single_record,
)
from app.models import models

ALL_TRANSACTIONS_QUERY = (
    "SELECT accounts.account_id, accounts.account_name, accounts.currency,"
    "assets.asset_id, assets.asset_symbol, assets.asset_name, assets.asset_type, assets.still_open,"
    " transactions.transaction_id, transactions.date, transactions.shares, transactions.price"
    " FROM transactions"
    " JOIN assets ON transactions.asset_id = assets.asset_id"
    " JOIN accounts ON assets.account_id = accounts.account_id"
)


def delete_transaction(transaction_id: int) -> None:

    execute_db("DELETE FROM transactions WHERE transaction_id = ?", (transaction_id,))


def get_all_transactions() -> list[models.TransactionRecord]:

    return [
        models.TransactionRecord(
            id=row["transaction_id"],
            asset_id=row["asset_id"],
            date=row["date"],
            shares=row["shares"],
            price=row["price"],
        )
        for row in fetch_multiple_records(ALL_TRANSACTIONS_QUERY)
    ]


def get_transactions_for_open_assets() -> list[models.TransactionRecord]:

    return [
        models.TransactionRecord(
            id=row["transaction_id"],
            asset_id=row["asset_id"],
            date=row["date"],
            shares=row["shares"],
            price=row["price"],
        )
        for row in fetch_multiple_records(
            ALL_TRANSACTIONS_QUERY
            + " WHERE assets.still_open = 1 ORDER BY transactions.date DESC",
        )
    ]


def get_transaction_by_id(transaction_id: int) -> models.TransactionRecord:

    record = fetch_single_record(
        "SELECT * FROM transactions WHERE transaction_id = ?",
        (transaction_id,),
    )

    return models.TransactionRecord(
        id=record["transaction_id"],
        asset_id=record["asset_id"],
        date=record["date"],
        shares=record["shares"],
        price=record["price"],
    )


def get_transactions_from_asset(asset_id: int) -> list[models.TransactionRecord]:
    return [
        models.TransactionRecord(
            id=row["transaction_id"],
            asset_id=row["asset_id"],
            date=row["date"],
            shares=row["shares"],
            price=row["price"],
        )
        for row in fetch_multiple_records(
            ALL_TRANSACTIONS_QUERY
            + " WHERE assets.asset_id = ? ORDER BY transactions.date DESC",
            (asset_id,),
        )
    ]


def insert_transaction(
    asset_id: int,
    date: date,
    shares: Decimal,
    price: Decimal,
) -> None:

    execute_db(
        "INSERT INTO transactions (asset_id, date, price, shares) VALUES (?, ?, ?, ?)",
        (asset_id, date.isoformat(), price, shares),
    )


def update_transaction(transaction: models.TransactionRecord) -> None:

    execute_db(
        "UPDATE transactions SET asset_id = ?, date = ?, shares = ?, price = ?"
        " WHERE transaction_id = ?",
        (
            transaction.asset_id,
            transaction.date.isoformat(),
            transaction.shares,
            transaction.price,
            transaction.id,
        ),
    )
