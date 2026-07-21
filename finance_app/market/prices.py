from pandas import Series

from finance_app.db import execute_db, query_db
from finance_app.assets import assets
from finance_app.market.fetchers.yfinance_fetcher import Fetcher
from finance_app.market.fetchers import tesouro_fetcher


def get_prices(asset_id: int) -> list:
    """Get the prices for asset id and return them as list of dictionaries
    with `date`, `unit_price` and `currency` as keys."""

    query = (
        "SELECT prices.date, prices.unit_price, accounts.currency FROM prices"
        " JOIN accounts ON accounts.account_id = "
        " (SELECT account_id FROM assets WHERE asset_id = ?)"
        " WHERE prices.asset_id = ?"
        " ORDER BY prices.date"
    )

    return query_db(query, (asset_id, asset_id))



def get_most_recent_price(asset_id: int) -> dict:
    """Returns the most recent price for asset and returns a dictionary
    containing `price` and `date` key."""

    p = get_prices(asset_id)

    if p:
        price_date = max([price["date"] for price in p])
        price_value = [
            price["unit_price"] for price in p if price["date"] == price_date
        ]

        return {"date": price_date, "price": price_value[0]}

    return {}


def delete_prices(asset_id: int) -> bool:
    """Deletes prices from database and returns True if successful."""

    prices = get_prices(asset_id)

    if prices:
        execute_db("DELETE FROM prices WHERE asset_id = ?", (asset_id,))
        return True

    return False


def insert_prices(asset_id: int) -> bool:
    """Insert prices for asset in database and returns True if successful."""

    asset = assets.get_asset_by_id(asset_id)
    
    prices = Series()
    if asset["asset_type"] == ("Stock" or "ETF"):
        prices = Fetcher(asset["asset_name"]).get_prices()
    if asset["asset_type"] == "Brazilian bond":
        prices = tesouro_fetcher.get_prices(asset["asset_name"])
 
    if not prices.empty:
        args = []
        for date, price in prices.items():
            args.append((asset_id, date, price))

        execute_db(
            "INSERT INTO prices (asset_id, date, unit_price) VALUES (?, ?, ?)"
            " ON CONFLICT (date, asset_id) DO NOTHING",
            args,
        )

        return True

    return False