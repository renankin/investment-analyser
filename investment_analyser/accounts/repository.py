from typing import Any

from investment_analyser.db import (
    execute_db,
    fetch_multiple_records,
    fetch_single_record,
)
from investment_analyser.domain.models import Account


def delete_account(account_id) -> None:

    execute_db("DELETE FROM accounts WHERE account_id = ?", (account_id,))


def get_all_accounts() -> list[Account]:
    query = "SELECT account_id, account_name, currency FROM accounts"

    return [
        Account(
            id=row["account_id"],
            name=row["account_name"],
            currency=row["currency"],
        )
        for row in fetch_multiple_records(query)
    ]


def get_account(account_id: int) -> Account | None:
    query = (
        "SELECT account_id, account_name, currency FROM accounts WHERE account_id = ?"
    )

    result = fetch_single_record(query, (account_id,))

    if result:
        return Account(
            id=result["account_id"],
            name=result["account_name"],
            currency=result["account_currency"],
        )

    return None


def get_assets(account_id: int) -> list[Account]:
    query = "SELECT asset_id, asset_name FROM assets WHERE account_id = ?"

    return [
        Account(
            id=row["account_id"],
            name=row["account_name"],
            currency=row["currency"],
        )
        for row in fetch_multiple_records(query, (account_id,))
    ]


def insert_account(account_name: str, currency: str):
    """Insert account in database."""

    execute_db(
        "INSERT INTO accounts (account_name, currency) VALUES (?, ?)",
        (account_name, currency),
    )


def update_account(account_id: int, account_name: str, currency: str) -> None:
    """Update account."""

    execute_db(
        "UPDATE accounts SET account_name = ?, currency = ? WHERE account_id = ?",
        (account_name, currency, account_id),
    )
