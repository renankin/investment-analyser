from datetime import date
from decimal import Decimal

from investment_analyser.db import (
    execute_db,
    fetch_multiple_records,
)
from investment_analyser.models.models import AssetInfo, StockSplit


def get_stock_splits(asset_id: int) -> list[StockSplit]:

    query = (
        "SELECT * FROM stock_splits"
        " JOIN assets ON stock_splits.asset_id = assets.asset_id"
        " WHERE stock_splits.asset_id = ?"
        " ORDER BY stock_splits.date DESC"
    )
    records = fetch_multiple_records(query, (asset_id,))

    return [
        StockSplit(
            date=row["date"],
            asset=AssetInfo(
                symbol=row["asset_symbol"],
                name=row["asset_name"],
                type=row["asset_type"],
            ),
            split_ratio=row["split_ratio"],
        )
        for row in records
    ]


def delete_stock_splits(asset_id: int) -> None:
    execute_db("DELETE FROM stock_splits WHERE asset_id = ?", (asset_id,))


def insert_stock_split(asset_id: int, date: date, split_ratio: Decimal) -> None:
    execute_db(
        "INSERT INTO stock_splits (asset_id, date, split_ratio)"
        " VALUES (?, ?, ?)"
        " ON CONFLICT (date, asset_id) DO NOTHING",
        (asset_id, date, split_ratio),
    )
