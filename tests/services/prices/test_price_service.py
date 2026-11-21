from datetime import date
from decimal import Decimal

import pytest

from app.models.models import MarketPrice


@pytest.fixture
def prices():
    return [
        MarketPrice(
            date=date(year=2024, month=1, day=1),
            asset_id=1,
            value=Decimal("100.00"),
            currency="USD",
        ),
        MarketPrice(
            date=date(year=2023, month=1, day=1),
            asset_id=1,
            value=Decimal("120.00"),
            currency="USD",
        ),
        MarketPrice(
            date=date(year=2025, month=1, day=1),
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
