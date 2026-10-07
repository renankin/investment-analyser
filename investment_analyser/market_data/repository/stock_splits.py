from datetime import date
from typing import Any

from investment_analyser.db import (
    execute_db,
    fetch_multiple_records,
)


def get_stock_splits(asset_id: int) -> list[dict[str, Any]]:
    """Fetch splits from database and returns a list of dictionaries containing `date`
    and `split_ratio`."""

    query = (
        "SELECT date, split_ratio FROM stock_splits"
        " WHERE asset_id = ?"
        " ORDER BY date DESC"
    )

    return [dict(row) for row in fetch_multiple_records(query, (asset_id,))]


def delete_stock_splits(asset_id: int) -> bool:
    """Deletes stock splits from database."""

    splits = get_stock_splits(asset_id)

    if splits:
        execute_db("DELETE FROM stock_splits WHERE asset_id = ?", (asset_id,))
        return True

    return False


def insert_stock_split(asset_id: int, date: date, split_ratio: float) -> None:

    execute_db(
        "INSERT INTO stock_splits (asset_id, date, split_ratio)"
        " VALUES (?, ?, ?)"
        " ON CONFLICT (date, asset_id) DO NOTHING",
        (asset_id, date, split_ratio),
    )
