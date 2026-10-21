from pandas import Series

from app.fetchers import tesouro_direto
from app.fetchers.yfinance import YFetcher
from app.repositories.assets import get_asset_by_id
from app.repositories.prices import insert_price


def insert_prices(asset_id: int) -> bool:
    """Insert prices for asset in database and returns True if successful."""

    asset = get_asset_by_id(asset_id)

    prices = Series()
    if asset.info.type in ["Stock", "ETF"]:
        prices = YFetcher(asset.info.symbol).get_prices()
    if asset.info.type == "Brazilian bond":
        prices = tesouro_direto.get_prices(asset.info.symbol)

    if not prices.empty:
        for date, price in prices.items():
            insert_price(asset_id=asset_id, date=date, unit_price=price)

        return True

    return False
