from datetime import date
from typing import Any

from investment_analyser.db import (
    execute_db,
    fetch_multiple_records,
    fetch_single_record,
)


def get_prices(asset_id: int) -> list[dict[str, Any]]:
    """Get the prices for asset id and return them as list of dictionaries
    with `date`, `unit_price` and `currency` as keys."""

    query = (
        "SELECT prices.date, prices.unit_price, accounts.currency FROM prices"
        " JOIN accounts ON accounts.account_id = "
        " (SELECT account_id FROM assets WHERE asset_id = ?)"
        " WHERE prices.asset_id = ?"
        " ORDER BY prices.date"
    )

    return [dict(row) for row in fetch_multiple_records(query, (asset_id, asset_id))]


def get_most_recent_price(asset_id: int) -> dict[str, Any] | None:
    """Returns the most recent price for asset as dictionary with keys `unit_price` and `date`."""

    query = "SELECT unit_price, date FROM prices WHERE asset_id = ? ORDER BY date DESC LIMIT 1"

    result = fetch_single_record(query, (asset_id,))

    if result:
        return dict(result)

    return None


def delete_prices(asset_id: int) -> bool:
    """Deletes prices from database and returns True if successful."""

    prices = get_prices(asset_id)

    if prices:
        execute_db("DELETE FROM prices WHERE asset_id = ?", (asset_id,))
        return True

    return False


def insert_price(asset_id: int, date: date, unit_price: float) -> None:

    execute_db(
        "INSERT INTO prices (asset_id, date, unit_price) VALUES (?, ?, ?)"
        " ON CONFLICT (date, asset_id) DO NOTHING",
        (asset_id, date, unit_price),
    )
