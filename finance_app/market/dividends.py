from pandas import Series

from finance_app.assets import assets
from finance_app.db import execute_db, query_db
from finance_app.market.fetchers.yfinance_fetcher import YFetcher


def get_dividends(asset_id: int) -> list:
    """Fetch dividends from database and return them as a list of dictionaries
    containing "date" and "dividend_value" keys."""

    query = (
        "SELECT * FROM dividends"
        " JOIN assets ON assets.asset_id = dividends.asset_id"
        " JOIN accounts ON accounts.account_id = assets.account_id"
        " WHERE dividends.asset_id = ?"
        " ORDER BY dividends.date DESC"
    )

    return query_db(query, (asset_id,))



def delete_dividends(asset_id: int) -> bool:
    """Deletes dividends from database and returns True if successful"""

    dividends = get_dividends(asset_id)

    if dividends:
        execute_db("DELETE FROM dividends WHERE asset_id = ?", (asset_id,))
        return True

    return False


def insert_dividends(asset_id: int) -> bool:
    """Insert dividends for stock in database and returns True if successful."""

    asset = assets.get_asset(asset_id)

    dividends = Series()
    if asset["asset_type"] == "Stock":
        dividends = YFetcher(asset["asset_name"]).get_dividends()

    if not dividends.empty:
        args = []
        for date, div in dividends.items():
            args.append((asset_id, date, div))

        execute_db(
            "INSERT INTO dividends (asset_id, date, dividend_value)"
            " VALUES (?, ?, ?)"
            " ON CONFLICT (date, asset_id) DO NOTHING",
            args,
        )

        return True

    return False