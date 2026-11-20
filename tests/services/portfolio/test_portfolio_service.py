from datetime import date
from decimal import Decimal

import pytest

from app.models import models
from app.services.portfolio_service import PortfolioService


def test_roi_for_asset(
    account_service,
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
    portfolio_service = PortfolioService(
        account_service,
        asset_service,
        transaction_service,
        dividend_service,
        price_service,
    )
    assert portfolio_service.get_irr_for_asset(asset) == pytest.approx(1.0)


def test_calculate_asset_history(
    account_service,
    asset_service,
    transaction_service,
    dividend_service,
    price_service,
):
    transactions = [
        models.TransactionRecord(
            id=1,
            asset_id=1,
            date=date(2024, 1, 1),
            type=models.TransactionType.PURCHASE,
            shares=Decimal("10.00"),
            price=Decimal("100.00"),
        ),
        models.TransactionRecord(
            id=2,
            asset_id=1,
            date=date(2024, 1, 3),
            type=models.TransactionType.PURCHASE,
            shares=Decimal("5.00"),
            price=Decimal("120.00"),
        ),
    ]
    transaction_service.add_transaction(transactions[0])
    transaction_service.add_transaction(transactions[1])

    price_service.add_prices(
        [
            models.MarketPrice(
                date=date(2024, 1, 3),
                asset_id=1,
                value=Decimal("120.00"),
                currency="USD",
            ),
            models.MarketPrice(
                date=date(2024, 1, 1),
                asset_id=1,
                value=Decimal("100.00"),
                currency="USD",
            ),
            models.MarketPrice(
                date=date(2024, 1, 2),
                asset_id=1,
                value=Decimal("110.00"),
                currency="USD",
            ),
        ]
    )
    portfolio_service = PortfolioService(
        account_service,
        asset_service,
        transaction_service,
        dividend_service,
        price_service,
    )

    history = portfolio_service.calculate_asset_value_history(asset_id=1)

    assert history.to_dict() == {
        date(2024, 1, 1): Decimal("1000.00"),
        date(2024, 1, 2): Decimal("1100.00"),
        date(2024, 1, 3): Decimal("1800.00"),
    }


def _add_asset_history_data(
    asset_service,
    transaction_service,
    price_service,
    account,
    asset_id,
    shares,
    prices,
):
    asset_service.add_asset(
        models.AssetPosition(
            id=asset_id,
            symbol=f"ASSET{asset_id}",
            name=f"Asset {asset_id}",
            type=models.AssetType.STOCK,
            still_open=True,
            account=account,
        )
    )
    transaction_service.add_transaction(
        models.TransactionRecord(
            id=asset_id,
            asset_id=asset_id,
            date=prices[0][0],
            type=models.TransactionType.PURCHASE,
            shares=shares,
            price=prices[0][1],
        )
    )
    price_service.add_prices(
        [
            models.MarketPrice(
                date=price_date,
                asset_id=asset_id,
                value=price_value,
                currency="USD",
            )
            for price_date, price_value in prices
        ]
    )


def test_calculate_account_history(
    account_service,
    asset_service,
    transaction_service,
    dividend_service,
    price_service,
):
    account = models.Account(id=1, name="Account 1")
    _add_asset_history_data(
        asset_service,
        transaction_service,
        price_service,
        account,
        asset_id=1,
        shares=Decimal("10.00"),
        prices=[
            (date(2024, 1, 1), Decimal("100.00")),
            (date(2024, 1, 2), Decimal("110.00")),
        ],
    )
    _add_asset_history_data(
        asset_service,
        transaction_service,
        price_service,
        account,
        asset_id=2,
        shares=Decimal("2.00"),
        prices=[
            (date(2024, 1, 2), Decimal("50.00")),
            (date(2024, 1, 3), Decimal("60.00")),
        ],
    )
    portfolio_service = PortfolioService(
        account_service,
        asset_service,
        transaction_service,
        dividend_service,
        price_service,
    )

    history = portfolio_service.calculate_account_value_history(account_id=1)

    assert history.to_dict() == {
        date(2024, 1, 1): Decimal("1000.00"),
        date(2024, 1, 2): Decimal("1200.00"),
        date(2024, 1, 3): Decimal("120.00"),
    }


def test_calculate_portfolio_history(
    account_service,
    asset_service,
    transaction_service,
    dividend_service,
    price_service,
):
    accounts = [
        models.Account(id=1, name="Account 1"),
        models.Account(id=2, name="Account 2"),
    ]
    for account in accounts:
        account_service.add_account(account)

    _add_asset_history_data(
        asset_service,
        transaction_service,
        price_service,
        accounts[0],
        asset_id=1,
        shares=Decimal("10.00"),
        prices=[
            (date(2024, 1, 1), Decimal("100.00")),
            (date(2024, 1, 2), Decimal("110.00")),
        ],
    )
    _add_asset_history_data(
        asset_service,
        transaction_service,
        price_service,
        accounts[1],
        asset_id=2,
        shares=Decimal("2.00"),
        prices=[
            (date(2024, 1, 2), Decimal("50.00")),
            (date(2024, 1, 3), Decimal("60.00")),
        ],
    )
    portfolio_service = PortfolioService(
        account_service,
        asset_service,
        transaction_service,
        dividend_service,
        price_service,
    )

    history = portfolio_service.calculate_portfolio_value_history()

    assert history.to_dict() == {
        date(2024, 1, 1): Decimal("1000.00"),
        date(2024, 1, 2): Decimal("1200.00"),
        date(2024, 1, 3): Decimal("120.00"),
    }
