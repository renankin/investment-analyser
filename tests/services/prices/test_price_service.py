import pytest
import datetime
from decimal import Decimal

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


@pytest.fixture
def fake_price_repository():
    return FakeMarketRepository()


@pytest.fixture
def price_service(fake_price_repository):
    return PriceService(fake_price_repository)


@pytest.fixture
def prices():
    return [
        MarketPrice(
            date=datetime.date(year=2024, month=1, day=1),
            asset_id=1,
            value=Decimal("100.00"),
            currency="USD",
        ),
        MarketPrice(
            date=datetime.date(year=2023, month=1, day=1),
            asset_id=1,
            value=Decimal("120.00"),
            currency="USD",
        ),
        MarketPrice(
            date=datetime.date(year=2025, month=1, day=1),
            asset_id=1,
            value=Decimal("90.00"),
            currency="USD",
        ),
    ]


def test_add_prices(price_service, prices, fake_price_repository):
    price_service.add_prices(prices)
    assert prices == fake_price_repository.prices


def test_year_change_calculation(price_service, prices):
    price_service.add_prices(prices)
    assert price_service.calculate_yearly_change(asset_id=1, years=1) == Decimal("-0.1")
