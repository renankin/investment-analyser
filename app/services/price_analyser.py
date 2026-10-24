import datetime
from decimal import Decimal

from app.models.models import MarketPrice
from app.repositories.prices import get_market_prices


class PriceAnalyser:
    def __init__(self, prices: list[MarketPrice]) -> None:
        self.prices = sorted(prices, key=lambda price: price.date)

    def calculate_price_change(
        self, initial_date: datetime.date, final_date: datetime.date
    ) -> Decimal:
        if initial_date < self.prices[0].date:
            raise ValueError("Selected initial date is outside price range.")
        if final_date > self.prices[-1].date:
            raise ValueError("Selected final date is outside price range.")

        initial_matching_price = self.prices[0]
        for price in self.prices:
            if initial_date >= price.date:
                initial_matching_price = price

        final_matching_price = self.prices[-1]
        for price in reversed(self.prices):
            if final_date >= price.date:
                final_matching_price = price
                break

        return (
            final_matching_price.value - initial_matching_price.value
        ) / initial_matching_price.value

    def get_dates(self) -> list[datetime.date]:
        return [price.date for price in self.prices]

    def get_prices(self) -> list[Decimal]:
        return [price.value for price in self.prices]

    def calculate_yearly_change(self, years: int) -> Decimal:
        most_recent_price = self.prices[-1].date
        inital_date = most_recent_price - datetime.timedelta(days=365 * years)
        return self.calculate_price_change(
            initial_date=inital_date, final_date=most_recent_price
        )


def fetch_price_analyser_for_asset(asset_id: int) -> PriceAnalyser:
    prices = get_market_prices(asset_id)
    return PriceAnalyser(prices)
