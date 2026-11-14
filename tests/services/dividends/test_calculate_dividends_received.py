from datetime import date
from decimal import Decimal

import pytest

from app.models import models
from app.services.dividend_service import calculate_dividends_received


@pytest.fixture
def market_dividends():
    def _make_dividends(div_dates: list[date]) -> list[models.MarketDividend]:
        divs: list[models.MarketDividend] = []
        for div_date in div_dates:
            divs.append(
                models.MarketDividend(
                    asset_id=1,
                    date=div_date,
                    dividend_per_share=Decimal("2.00"),
                    currency="USD",
                )
            )
        return divs

    return _make_dividends


@pytest.fixture
def transaction():
    def _make_transaction(date):
        return models.AdjustedTransaction(
            transaction_record=models.TransactionRecord(
                id=1,
                asset_id=1,
                date=date,
                type=models.TransactionType.PURCHASE,
                shares=Decimal("100.00"),
                price=Decimal("100.00"),
            ),
            shares=Decimal("100.00"),
            price=Decimal("100.00"),
            is_adjusted=False,
        )

    return _make_transaction


def test_dividends_received(market_dividends, transaction):
    market_divs = market_dividends(
        div_dates=[date(2024, 1, 1), date(2025, 1, 1), date(2026, 1, 1)]
    )
    adj_transactions = [transaction(date=date(2024, 1, 1))]
    divs_received = [
        models.DividendReceived(
            asset_id=1,
            date=date(2025, 1, 1),
            received_value=Decimal("200.00"),
            currency="USD",
        ),
        models.DividendReceived(
            asset_id=1,
            date=date(2026, 1, 1),
            received_value=Decimal("200.00"),
            currency="USD",
        ),
    ]
    assert (
        calculate_dividends_received(
            adjusted_transactions=adj_transactions,
            market_dividends=market_divs,
            asset_open=True,
        )
        == divs_received
    )


def test_no_valid_dividends(market_dividends, transaction):
    market_divs = market_dividends(
        div_dates=[date(2024, 1, 1), date(2025, 1, 1), date(2026, 1, 1)]
    )
    adj_transactions = [transaction(date(2026, 1, 1))]

    assert (
        calculate_dividends_received(
            adjusted_transactions=adj_transactions,
            market_dividends=market_divs,
            asset_open=True,
        )
        == []
    )
