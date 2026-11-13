from datetime import date
from decimal import Decimal

import pytest

from app.models import models
from app.ports.repository import MarketDividendRepository
from app.services.dividend_service import DividendService


class FakeMarketDividendRepository(MarketDividendRepository):
    def __init__(self) -> None:
        self.dividends: list[models.MarketDividend] = []

    def add_dividends(self, dividends: list[models.MarketDividend]) -> None:
        [self.dividends.append(dividend) for dividend in dividends]

    def get_dividends_for_asset(self, asset_id: int) -> list[models.MarketDividend]:
        return [
            dividend for dividend in self.dividends if dividend.asset_id == asset_id
        ]


@pytest.fixture
def fake_dividend_repository():
    return FakeMarketDividendRepository()


@pytest.fixture
def dividend_service(fake_dividend_repository):
    return DividendService(fake_dividend_repository)


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


def test_dividends_received(asset, market_dividends, transaction, dividend_service):
    market_divs = market_dividends(
        div_dates=[date(2024, 1, 1), date(2025, 1, 1), date(2026, 1, 1)]
    )
    dividend_service.add_market_dividends(market_divs)
    divs_received = dividend_service.calculate_dividends_received(
        asset=asset, adj_transactions=[transaction(date=date(2024, 1, 1))]
    )
    assert divs_received == [
        models.DividendReceived(
            asset=asset,
            date=date(2025, 1, 1),
            received_value=Decimal("200.00"),
            currency="USD",
        ),
        models.DividendReceived(
            asset=asset,
            date=date(2026, 1, 1),
            received_value=Decimal("200.00"),
            currency="USD",
        ),
    ]


def test_no_valid_dividends(asset, market_dividends, transaction, dividend_service):
    market_divs = market_dividends(
        div_dates=[date(2024, 1, 1), date(2025, 1, 1), date(2026, 1, 1)]
    )
    dividend_service.add_market_dividends(market_divs)
    divs = dividend_service.calculate_dividends_received(
        asset=asset, adj_transactions=[transaction(date(2026, 1, 1))]
    )

    assert divs == []
