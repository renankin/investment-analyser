from datetime import date
from decimal import Decimal

import pytest

from app.models import models


@pytest.fixture
def asset():
    return models.AssetPosition(
        id=1,
        symbol="APPL",
        name="Apple",
        type=models.AssetType.STOCK,
        still_open=True,
        account=models.Account(id=1, name="Test Account"),
    )


@pytest.fixture
def market_dividends():
    return [
        models.MarketDividend(
            asset_id=1,
            date=date(2024, 1, 1),
            dividend_per_share=Decimal("10.0"),
            currency="USD",
        ),
        models.MarketDividend(
            asset_id=1,
            date=date(2025, 1, 1),
            dividend_per_share=Decimal("10.0"),
            currency="USD",
        ),
    ]


def test_add_dividends(dividend_service, market_dividends, fake_dividend_repository):
    dividend_service.add_market_dividends(market_dividends)
    assert market_dividends == fake_dividend_repository.dividends


def test_dividends_received_orchestration(asset, dividend_service, market_dividends):
    dividend_service.add_market_dividends(market_dividends)
    adjusted_transactions = [
        models.AdjustedTransaction(
            transaction_record=models.TransactionRecord(
                id=1,
                asset_id=1,
                date=date(2024, 1, 1),
                type=models.TransactionType.PURCHASE,
                shares=Decimal("100.00"),
                price=Decimal("100.00"),
            ),
            shares=Decimal("100.00"),
            price=Decimal("100.00"),
            is_adjusted=False,
        )
    ]
    divs_received = [
        models.DividendReceived(
            asset_id=1,
            date=date(2025, 1, 1),
            received_value=Decimal("1000.00"),
            currency="USD",
        ),
    ]
    assert (
        dividend_service.get_dividends_received(
            asset=asset, adj_transactions=adjusted_transactions
        )
        == divs_received
    )
