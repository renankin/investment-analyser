from datetime import date
from typing import Any

from investment_analyser.db import (
    execute_db,
    fetch_multiple_records,
)


def get_dividends(asset_id: int) -> list[dict[str, Any]]:
    """Fetch dividends from database and return them as a list of dictionaries
    containing "date" and "dividend_value" keys."""

    query = (
        "SELECT * FROM dividends"
        " JOIN assets ON assets.asset_id = dividends.asset_id"
        " JOIN accounts ON accounts.account_id = assets.account_id"
        " WHERE dividends.asset_id = ?"
        " ORDER BY dividends.date DESC"
    )

    return [dict(row) for row in fetch_multiple_records(query, (asset_id,))]


def delete_dividends(asset_id: int) -> bool:
    """Deletes dividends from database and returns True if successful"""

    dividends = get_dividends(asset_id)

    if dividends:
        execute_db("DELETE FROM dividends WHERE asset_id = ?", (asset_id,))
        return True

    return False


def insert_dividend(asset_id: int, date: date, dividend_value: float) -> None:

    execute_db(
        "INSERT INTO dividends (asset_id, date, dividend_value)"
        " VALUES (?, ?, ?)"
        " ON CONFLICT (date, asset_id) DO NOTHING",
        (asset_id, date, dividend_value),
    )
