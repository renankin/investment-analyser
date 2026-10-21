from datetime import date

from app.db.connection import (
    execute_db,
    fetch_multiple_records,
    fetch_single_record,
)
from app.models.models import AssetInfo, MarketPrice


def get_market_prices(asset_id: int) -> list[MarketPrice]:
    return [
        MarketPrice(
            date=row["date"],
            asset=AssetInfo(
                symbol=row["asset_symbol"],
                name=row["asset_name"],
                type=row["asset_type"],
            ),
            value=row["unit_price"],
        )
        for row in fetch_multiple_records(
            (
                "SELECT * FROM prices"
                " JOIN assets ON assets.asset_id = prices.asset_id"
                " JOIN accounts ON accounts.account_id = assets.account_id"
                " WHERE prices.asset_id = ?"
            ),
            (asset_id,),
        )
    ]


def get_most_recent_price(asset_id: int) -> MarketPrice:
    record = fetch_single_record(
        (
            "SELECT * FROM prices"
            " JOIN assets ON assets.asset_id = prices.asset_id"
            " JOIN accounts ON accounts.account_id = assets.account_id"
            " WHERE prices.asset_id = ?"
            " ORDER BY prices.date DESC LIMIT 1"
        ),
        (asset_id,),
    )
    return MarketPrice(
        date=record["date"],
        asset=AssetInfo(
            symbol=record["asset_symbol"],
            name=record["asset_name"],
            type=record["asset_type"],
        ),
        value=record["unit_price"],
    )


def delete_prices(asset_id: int) -> None:
    execute_db("DELETE FROM prices WHERE asset_id = ?", (asset_id,))


def insert_price(asset_id: int, date: date, unit_price: float) -> None:
    execute_db(
        "INSERT INTO prices (asset_id, date, unit_price) VALUES (?, ?, ?)"
        " ON CONFLICT (date, asset_id) DO NOTHING",
        (asset_id, date, unit_price),
    )
