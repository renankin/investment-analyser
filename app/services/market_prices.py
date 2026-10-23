from datetime import date
from decimal import Decimal

from pandas import Series

from app.fetchers import tesouro_direto
from app.fetchers.yfinance import YFetcher
from app.models.models import MarketPrice
from app.repositories.assets import get_asset_by_id
from app.repositories.prices import insert_price


class PriceAnalyser:
    def __init__(self, prices: list[MarketPrice]) -> None:
        self.prices = sorted(prices, key=lambda price: price.date)

    def calculate_price_change(self, initial_date: date, final_date: date) -> Decimal:

        initial_matching_price = None
        for price in self.prices:
            if price.date >= initial_date:
                initial_matching_price = price
                break

        final_matching_price = None
        for price in self.prices:
            if price.date <= final_date:
                final_matching_price = price

        if initial_matching_price is None or final_matching_price is None:
            raise ValueError("Selected values are outside price range.")

        return (
            final_matching_price.value - initial_matching_price.value
        ) / initial_matching_price.value


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
