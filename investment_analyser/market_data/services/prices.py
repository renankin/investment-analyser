from datetime import date
from decimal import Decimal
from typing import TypedDict

from pandas import Series

from investment_analyser.assets.repository import get_asset
from investment_analyser.market_data.fetchers import tesouro_direto
from investment_analyser.market_data.fetchers.yfinance import YFetcher
from investment_analyser.market_data.repository.prices import insert_price


class Price(TypedDict):
    """Contains `date` and `value`."""

    date: date
    value: Decimal


def insert_prices(asset_id: int) -> bool:
    """Insert prices for asset in database and returns True if successful."""

    asset = get_asset(asset_id)

    prices = Series()
    if asset["asset_type"] in ["Stock", "ETF"]:
        prices = YFetcher(asset["asset_symbol"]).get_prices()
    if asset["asset_type"] == "Brazilian bond":
        prices = tesouro_direto.get_prices(asset["asset_symbol"])

    if not prices.empty:
        for date, price in prices.items():
            insert_price(asset_id=asset_id, date=date, unit_price=price)

        return True

    return False
