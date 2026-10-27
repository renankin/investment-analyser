import datetime
from decimal import Decimal

from pandas import Series, to_datetime

from app.fetchers.tesouro_direto import get_prices
from app.fetchers.yfinance import YFetcher
from app.models.models import AssetPosition, MarketPrice
from app.repositories.prices import get_market_prices, insert_price


class PriceService:
    def __init__(self, asset_id: int) -> None:
        self.prices = sorted(get_market_prices(asset_id), key=lambda price: price.date)

    def get_dates(self) -> list[datetime.date]:
        return [price.date for price in self.prices]

    def get_prices(self) -> list[Decimal]:
        return [price.value for price in self.prices]

    def calculate_yearly_change(self, years: int) -> Decimal:
        most_recent_price = self.prices[-1].date
        inital_date = most_recent_price - datetime.timedelta(days=365 * years)
        return self.calculate_price_change(
            self.prices, initial_date=inital_date, final_date=most_recent_price
        )

    @classmethod
    def calculate_price_change(
        cls,
        prices: list[MarketPrice],
        initial_date: datetime.date,
        final_date: datetime.date,
    ) -> Decimal:
        if initial_date < prices[0].date:
            raise ValueError("Selected initial date is outside price range.")
        if final_date > prices[-1].date:
            raise ValueError("Selected final date is outside price range.")

        initial_matching_price = prices[0]
        for price in prices:
            if initial_date >= price.date:
                initial_matching_price = price

        final_matching_price = prices[-1]
        for price in reversed(prices):
            if final_date >= price.date:
                final_matching_price = price
                break

        return (
            final_matching_price.value - initial_matching_price.value
        ) / initial_matching_price.value

    @classmethod
    def update_prices(cls, asset: AssetPosition) -> None:
        prices = Series()
        if asset.info.type in ["Stock", "ETF"]:
            prices = YFetcher(asset.info.symbol).get_prices()
        if asset.info.type == "Brazilian bond":
            prices = get_prices(asset.info.symbol)

        if not prices.empty:
            for date, price in prices.items():
                insert_price(
                    asset_id=asset.id,
                    date=to_datetime(str(date)).date(),
                    unit_price=price,
                )
