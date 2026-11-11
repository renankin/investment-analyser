import datetime
from decimal import Decimal

from app.models.models import MarketPrice
from app.ports.repository import MarketPriceRepository


class PriceService:
    def __init__(self, repository: MarketPriceRepository) -> None:
        self._repository = repository

    def calculate_yearly_change(self, asset_id: int, years: int) -> Decimal | None:
        prices = sorted(
            self._repository.get_prices_for_asset(asset_id),
            key=lambda price: price.date,
        )
        if prices:
            most_recent_price = prices[-1].date
            inital_date = most_recent_price - datetime.timedelta(days=365 * years)
            try:
                price_change = self.calculate_price_change(
                    asset_id, initial_date=inital_date, final_date=most_recent_price
                )
            except ValueError:
                return None
            return price_change
        return None

    def calculate_price_change(
        self,
        asset_id: int,
        initial_date: datetime.date,
        final_date: datetime.date,
    ) -> Decimal:
        prices = sorted(
            self._repository.get_prices_for_asset(asset_id),
            key=lambda price: price.date,
        )
        if not prices:
            raise ValueError("Price repository is empty.")
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

    def add_prices(self, prices: list[MarketPrice]) -> None:
        self._repository.add_prices(prices)
