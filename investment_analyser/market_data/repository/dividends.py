from datetime import date

from investment_analyser.db import (
    execute_db,
    fetch_multiple_records,
)
from investment_analyser.models.models import AssetInfo, MarketDividend


def get_dividends(asset_id: int) -> list[MarketDividend]:

    query = (
        "SELECT * FROM dividends"
        " JOIN assets ON assets.asset_id = dividends.asset_id"
        " JOIN accounts ON accounts.account_id = assets.account_id"
        " WHERE dividends.asset_id = ?"
        " ORDER BY dividends.date DESC"
    )

    return [
        MarketDividend(
            date=row["date"],
            asset=AssetInfo(
                symbol=row["asset_symbol"],
                name=row["asset_name"],
                type=row["asset_type"],
            ),
            value=row["dividend_value"],
            currency=row["currency"],
        )
        for row in fetch_multiple_records(query, (asset_id,))
    ]


def delete_dividends(asset_id: int) -> None:

    execute_db("DELETE FROM dividends WHERE asset_id = ?", (asset_id,))


def insert_dividend(asset_id: int, date: date, dividend_value: float) -> None:

    execute_db(
        "INSERT INTO dividends (asset_id, date, dividend_value)"
        " VALUES (?, ?, ?)"
        " ON CONFLICT (date, asset_id) DO NOTHING",
        (asset_id, date, dividend_value),
    )
