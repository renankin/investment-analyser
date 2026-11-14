from datetime import date
from decimal import Decimal

import pytest

from app.models.models import MarketPrice
from app.services.price_service import calculate_price_change


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
            date=date(year=2024, month=1, day=10),
            asset_id=1,
            value=Decimal("120.00"),
            currency="USD",
        ),
        MarketPrice(
            date=date(year=2024, month=1, day=20),
            asset_id=1,
            value=Decimal("90.00"),
            currency="USD",
        ),
    ]


def test_price_change_for_complete_period(prices):
    assert calculate_price_change(
        prices=prices,
        initial_date=date(year=2024, month=1, day=1),
        final_date=date(year=2024, month=1, day=20),
    ) == Decimal("-0.1")


def test_price_change_with_ealier_date(prices):
    with pytest.raises(ValueError):
        calculate_price_change(
            prices=prices,
            initial_date=date(year=2023, month=12, day=1),
            final_date=date(year=2024, month=1, day=1),
        )


def test_price_change_with_future_date(prices):
    with pytest.raises(ValueError):
        calculate_price_change(
            prices=prices,
            initial_date=date(year=2024, month=1, day=10),
            final_date=date(year=2026, month=12, day=1),
        )


def test_empty_prices():
    with pytest.raises(ValueError):
        calculate_price_change(
            prices=[],
            initial_date=date(year=2024, month=1, day=10),
            final_date=date(year=2026, month=12, day=1),
        )


def test_price_change_within_date_range(prices):
    assert calculate_price_change(
        prices=prices,
        initial_date=date(year=2024, month=1, day=10),
        final_date=date(year=2024, month=1, day=20),
    ) == Decimal("-0.25")


def test_price_change_non_matching_dates(prices):
    assert calculate_price_change(
        prices=prices,
        initial_date=date(year=2024, month=1, day=5),
        final_date=date(year=2024, month=1, day=15),
    ) == Decimal("0.2")
