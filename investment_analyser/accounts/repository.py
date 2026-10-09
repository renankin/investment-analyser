from investment_analyser.db import (
    execute_db,
    fetch_multiple_records,
    fetch_single_record,
)
from investment_analyser.domain.models import Account, Asset


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


def get_account(account_id: int) -> Account:
    query = (
        "SELECT account_id, account_name, currency FROM accounts WHERE account_id = ?"
    )

    result = fetch_single_record(query, (account_id,))

    return Account(
        id=result["account_id"],
        name=result["account_name"],
        currency=result["currency"],
    )


def get_assets_from_account(account_id: int) -> list[Asset]:

    query = "SELECT * FROM assets WHERE account_id = ?"

    return [
        Asset(
            id=row["asset_id"],
            symbol=row["asset_symbol"],
            name=row["asset_name"],
            type=row["asset_type"],
            account_id=row["account_id"],
            still_open=row["still_open"],
        )
        for row in fetch_multiple_records(query, (account_id,))
    ]


def create_account(account_name: str, account_currency: str) -> None:
    """Insert account in database."""

    execute_db(
        "INSERT INTO accounts (account_name, currency) VALUES (?, ?)",
        (account_name, account_currency),
    )


def update_account(account: Account) -> None:
    """Update account."""

    execute_db(
        "UPDATE accounts SET account_name = ?, currency = ? WHERE account_id = ?",
        (account.name, account.currency, account.id),
    )
