from datetime import date
from decimal import Decimal

import pytest

from app.models import models
from app.models.models import CashFlow
from app.services.portfolio_service import calculate_irr


def test_roi_for_asset(
    portfolio_service,
    asset_service,
    transaction_service,
    dividend_service,
    price_service,
):
    asset = models.AssetPosition(
        id=1,
        symbol="APPL",
        name="Apple",
        type=models.AssetType.STOCK,
        still_open=True,
        account=models.Account(id=1, name="Test Account"),
    )
    asset_service.add_asset(asset)
    transaction_service.add_transaction(
        models.TransactionRecord(
            id=1,
            asset_id=1,
            date=date(2024, 1, 31),
            type=models.TransactionType.PURCHASE,
            shares=Decimal("10.00"),
            price=Decimal("100.00"),
        )
    )
    dividend_service.add_market_dividends(
        [
            models.MarketDividend(
                asset_id=1,
                date=date(2025, 1, 30),
                dividend_per_share=Decimal("10.0"),
                currency="USD",
            )
        ]
    )
    price_service.add_prices(
        [
            models.MarketPrice(
                date=date(year=2025, month=1, day=30),
                asset_id=1,
                value=Decimal("190.00"),
                currency="USD",
            ),
        ]
    )
    assert portfolio_service.get_irr_for_asset(asset) == pytest.approx(1.0)

def test_empty_imputs():

    assert calculate_irr([]) is None


def test_positive_irr():

    cashflows = [
        CashFlow(value=Decimal("-1000.00"), date=date(2024, 1, 31)),
        CashFlow(value=Decimal("1100.00"), date=date(2025, 1, 30)),
    ]

    assert calculate_irr(cashflows) == pytest.approx(0.10, abs=1e-4)


def test_negative_irr():

    cashflows = [
        CashFlow(value=Decimal("-1000.00"), date=date(2024, 1, 31)),
        CashFlow(value=Decimal("900.00"), date=date(2025, 1, 30)),
    ]

    assert calculate_irr(cashflows) == pytest.approx(-0.1, abs=1e-4)


def test_single_cashflow():

    assert (
        calculate_irr([CashFlow(value=Decimal("1100.00"), date=date(2025, 1, 30))])
        == None
    )


def test_all_positive_cashflows():

    cashflows = [
        CashFlow(value=Decimal("1000.00"), date=date(2024, 1, 31)),
        CashFlow(value=Decimal("1100.00"), date=date(2025, 1, 30)),
    ]

    assert calculate_irr(cashflows) == None


def test_all_negative_cashflows():

    cashflows = [
        CashFlow(value=Decimal("-1000.00"), date=date(2024, 1, 31)),
        CashFlow(value=Decimal("-1100.00"), date=date(2025, 1, 30)),
    ]

    assert calculate_irr(cashflows) == None


def test_irregular_cashflows():

    cashflows = [
        CashFlow(value=Decimal("-1000.00"), date=date(2024, 1, 31)),
        CashFlow(value=Decimal("200.00"), date=date(2024, 7, 15)),
        CashFlow(value=Decimal("-300.00"), date=date(2025, 1, 10)),
        CashFlow(value=Decimal("1400.00"), date=date(2025, 12, 20)),
    ]

    assert calculate_irr(cashflows) == pytest.approx(0.15, abs=1e-4)


def test_unsorted_cashflows():

    cashflows = [
        CashFlow(value=Decimal("1400.00"), date=date(2025, 12, 20)),
        CashFlow(value=Decimal("-1000.00"), date=date(2024, 1, 31)),
        CashFlow(value=Decimal("-300.00"), date=date(2025, 1, 10)),
        CashFlow(value=Decimal("200.00"), date=date(2024, 7, 15)),
    ]

    assert calculate_irr(cashflows) == pytest.approx(0.15, abs=1e-4)


def test_same_day_cashflows():

    cashflows = [
        CashFlow(value=Decimal("-1200.00"), date=date(2024, 1, 31)),
        CashFlow(value=Decimal("200.00"), date=date(2024, 1, 31)),
        CashFlow(value=Decimal("1100.00"), date=date(2025, 1, 30)),
    ]

    assert calculate_irr(cashflows) == pytest.approx(0.10, abs=1e-4)


def test_large_irr():

    cashflows = [
        CashFlow(value=Decimal("-1000.00"), date=date(2024, 1, 31)),
        CashFlow(value=Decimal("2000.00"), date=date(2025, 1, 30)),
    ]

    assert calculate_irr(cashflows) == pytest.approx(1.0, abs=1e-4)
