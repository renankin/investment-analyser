from typing import Any

from pandas import Series

from investment_analyser.assets import assets
from investment_analyser.db import (
    execute_db,
    executemany_db,
    fetch_multiple_records,
    fetch_single_record,
)
from investment_analyser.market_data.fetchers import tesouro_direto
from investment_analyser.market_data.fetchers.yfinance import YFetcher


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


def insert_prices(asset_id: int) -> bool:
    """Insert prices for asset in database and returns True if successful."""

    asset = assets.get_asset(asset_id)

    prices = Series()
    if asset["asset_type"] in ["Stock", "ETF"]:
        prices = YFetcher(asset["asset_symbol"]).get_prices()
    if asset["asset_type"] == "Brazilian bond":
        prices = tesouro_direto.get_prices(asset["asset_symbol"])

    if not prices.empty:
        args = []
        for date, price in prices.items():
            args.append((asset_id, date, price))

        executemany_db(
            "INSERT INTO prices (asset_id, date, unit_price) VALUES (?, ?, ?)"
            " ON CONFLICT (date, asset_id) DO NOTHING",
            args,
        )

        return True

    return False
