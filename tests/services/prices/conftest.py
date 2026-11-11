from pytest import fixture

from app.models.models import MarketPrice
from app.ports.repository import MarketPriceRepository
from app.services.price_service import PriceService


class FakeMarketRepository(MarketPriceRepository):
    def __init__(self):
        self.prices: list[MarketPrice] = []

    def add_prices(self, prices: list[MarketPrice]) -> None:
        [self.prices.append(price) for price in prices]

    def get_prices_for_asset(self, asset_id: int) -> list[MarketPrice]:
        return [price for price in self.prices if price.asset_id == asset_id]


@fixture
def fake_price_repository():
    return FakeMarketRepository()


@fixture
def price_service(fake_price_repository):
    return PriceService(fake_price_repository)
