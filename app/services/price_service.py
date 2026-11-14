import datetime
from decimal import Decimal

from app.models.models import MarketPrice
from app.ports.repository import MarketPriceRepository


def calculate_price_change(
    prices: list[MarketPrice],
    initial_date: datetime.date,
    final_date: datetime.date,
) -> Decimal:
    if not prices:
        raise ValueError("Price list is empty.")
    price_date_key = lambda price: price.date
    sorted_prices = sorted(prices, key=price_date_key)
    min_price = min(sorted_prices, key=price_date_key)
    max_price = max(sorted_prices, key=price_date_key)
    if initial_date < min_price.date:
        raise ValueError("Selected initial date is outside price range.")
    if final_date > max_price.date:
        raise ValueError("Selected final date is outside price range.")

    initial_matching_price = min_price
    for price in sorted_prices:
        if initial_date >= price.date:
            initial_matching_price = price

    final_matching_price = max_price
    for price in reversed(sorted_prices):
        if final_date >= price.date:
            final_matching_price = price
            break

    return (
        final_matching_price.value - initial_matching_price.value
    ) / initial_matching_price.value


class PriceService:
    def __init__(self, repository: MarketPriceRepository) -> None:
        self._repository = repository

    def calculate_yearly_change(self, asset_id: int, years: int) -> Decimal | None:
        prices = self._repository.get_prices_for_asset(asset_id)
        if prices:
            most_recent_price = max(prices, key=lambda price: price.date)
            inital_date = most_recent_price.date - datetime.timedelta(days=365 * years)
            try:
                price_change = calculate_price_change(
                    prices=prices,
                    initial_date=inital_date,
                    final_date=most_recent_price.date,
                )
            except ValueError:
                return None
            return price_change
        return None

    def add_prices(self, prices: list[MarketPrice]) -> None:
        self._repository.add_prices(prices)
