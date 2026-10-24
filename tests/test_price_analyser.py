from datetime import date
from decimal import Decimal

import pytest

from app.models.models import AssetInfo, MarketPrice
from app.services.market_prices import PriceAnalyser

asset_info = AssetInfo(symbol="APPL", name="Apple", type="Stock")

prices = [
    MarketPrice(
        date=date(year=2024, month=1, day=1),
        asset=asset_info,
        value=Decimal("100.00"),
    ),
    MarketPrice(
        date=date(year=2024, month=1, day=10),
        asset=asset_info,
        value=Decimal("120.00"),
    ),
    MarketPrice(
        date=date(year=2024, month=1, day=20),
        asset=asset_info,
        value=Decimal("90.00"),
    ),
]
price_analyser = PriceAnalyser(prices)


def test_price_change_for_complete_period():
    assert price_analyser.calculate_price_change(
        initial_date=date(year=2024, month=1, day=1),
        final_date=date(year=2024, month=1, day=20),
    ) == Decimal("-0.1")


def test_price_change_with_ealier_date():
    with pytest.raises(ValueError):
        price_analyser.calculate_price_change(
            initial_date=date(year=2023, month=12, day=1),
            final_date=date(year=2024, month=1, day=1),
        )


def test_price_change_with_future_date():
    with pytest.raises(ValueError):
        price_analyser.calculate_price_change(
            initial_date=date(year=2024, month=1, day=10),
            final_date=date(year=2026, month=12, day=1),
        )


def test_price_change_within_date_range():
    assert price_analyser.calculate_price_change(
        initial_date=date(year=2024, month=1, day=10),
        final_date=date(year=2024, month=1, day=20),
    ) == Decimal("-0.25")


def test_price_change_non_matching_dates():
    assert price_analyser.calculate_price_change(
        initial_date=date(year=2024, month=1, day=5),
        final_date=date(year=2024, month=1, day=15),
    ) == Decimal("0.2")
