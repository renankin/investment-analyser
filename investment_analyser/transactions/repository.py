from typing import Any

from investment_analyser.db import (
    execute_db,
    fetch_multiple_records,
    fetch_single_record,
)


def delete_transaction(transaction_id: int):
    """Deletes transaction."""

    execute_db("DELETE FROM transactions WHERE transaction_id = ?", (transaction_id,))


def get_all_transactions() -> list[dict[str, Any]]:
    """Fetch all transactions from database and returns a list of dictionaries
    containing `transaction_id`, `account_name`, `asset_symbol`, `date`, `currency`,
    `shares`, `adj_shares`, `price` and `adj_price`."""

    query = (
        "SELECT accounts.account_name, accounts.currency, assets.asset_symbol,"
        " transactions.transaction_id, transactions.date, transactions.shares, "
        " transactions.price"
        " FROM transactions"
        " JOIN assets ON transactions.asset_id = assets.asset_id"
        " JOIN accounts ON assets.account_id = accounts.account_id"
        " ORDER BY transactions.date DESC"
    )

    return [dict(transaction) for transaction in fetch_multiple_records(query)]


def get_transactions_for_open_assets() -> list[dict[str, Any]]:
    """Returns a list of dicts with keys `asset_id`, `asset_name`, `asset_type`,
    `date`, `shares`, `price` and `currency`"""

    query = (
        "SELECT transactions.shares, transactions.price, transactions.date,"
        " assets.asset_id, assets.asset_name, assets.asset_type, assets.asset_symbol,"
        " accounts.currency"
        " FROM transactions"
        " JOIN assets on transactions.asset_id = assets.asset_id"
        " JOIN accounts on assets.account_id = accounts.account_id"
        " WHERE assets.still_open = 1"
    )

    return [dict(row) for row in fetch_multiple_records(query)]


def get_transaction(transaction_id: int) -> dict[str, Any]:
    """Returns a dictionary containing `asset_id`, `transaction_id`,
    `shares`, `price` and `date` keys"""

    query = (
        "SELECT asset_id, transaction_id, shares, price, date"
        " FROM transactions"
        " WHERE transaction_id = ?"
    )

    transaction = fetch_single_record(query, (transaction_id,))

    if transaction:
        return dict(transaction)

    return {}


def get_transactions(asset_id: int) -> list[dict[str, Any]]:
    """Fetch all transactions of an asset and return as list of dictionaries
    with `transaction_id`, `asset_id`, `date`, `price` and `shares`."""

    query = (
        "SELECT transaction_id, asset_id, date, shares, price"
        " FROM transactions"
        " WHERE asset_id = ?"
    )

    return [dict(row) for row in fetch_multiple_records(query, (asset_id,))]


def insert_transaction(asset_id: int, date: str, shares: float, price: float):
    """Inserts transaction in database."""

    query = (
        "INSERT INTO transactions (asset_id, date, price, shares) VALUES (?, ?, ?, ?)"
    )

    execute_db(query, (asset_id, date, price, shares))


def update_transaction(
    transaction_id: int, asset_id: int, date: str, shares: float, price: float
):
    """Updates transaction."""

    query = (
        "UPDATE transactions SET asset_id = ?, date = ?, shares = ?, price = ?"
        " WHERE transaction_id = ?"
    )

    execute_db(query, (asset_id, date, shares, price, transaction_id))
