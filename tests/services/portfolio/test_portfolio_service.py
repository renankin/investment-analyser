from datetime import date
from decimal import Decimal

import pytest

from app.models import models
from app.services.portfolio_service import PortfolioService


def test_roi_for_asset(
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
    portfolio_service = PortfolioService(
        asset_service, transaction_service, dividend_service, price_service
    )
    assert portfolio_service.get_irr_for_asset(asset) == pytest.approx(1.0)
