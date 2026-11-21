from datetime import date
from decimal import Decimal

from app.models import models


def test_calculate_asset_history(transaction_service, price_service, portfolio_service):
    transaction_service.add_transaction(
        models.TransactionRecord(
            id=1,
            asset_id=1,
            date=date(2024, 1, 1),
            type=models.TransactionType.PURCHASE,
            shares=Decimal("10.00"),
            price=Decimal("100.00"),
        )
    )
    transaction_service.add_transaction(
        models.TransactionRecord(
            id=2,
            asset_id=1,
            date=date(2024, 1, 3),
            type=models.TransactionType.PURCHASE,
            shares=Decimal("5.00"),
            price=Decimal("120.00"),
        )
    )

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

    history = portfolio_service.calculate_asset_value_history(asset_id=1)

    assert history.to_dict() == {
        date(2024, 1, 1): Decimal("1000.00"),
        date(2024, 1, 2): Decimal("1100.00"),
        date(2024, 1, 3): Decimal("1800.00"),
    }


def test_calculate_account_history(
    asset_service, transaction_service, price_service, portfolio_service
):
    account = models.Account(id=1, name="Account 1")
    asset_service.add_asset(
        models.AssetPosition(
            id=1,
            symbol="ASSET1",
            name="Asset 1",
            type=models.AssetType.STOCK,
            still_open=True,
            account=account,
        )
    )
    transaction_service.add_transaction(
        models.TransactionRecord(
            id=1,
            asset_id=1,
            date=date(2024, 1, 1),
            type=models.TransactionType.PURCHASE,
            shares=Decimal("10.00"),
            price=Decimal("100.00"),
        )
    )
    price_service.add_prices(
        [
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
    asset_service.add_asset(
        models.AssetPosition(
            id=2,
            symbol="ASSET2",
            name="Asset 2",
            type=models.AssetType.STOCK,
            still_open=True,
            account=account,
        )
    )
    transaction_service.add_transaction(
        models.TransactionRecord(
            id=2,
            asset_id=2,
            date=date(2024, 1, 2),
            type=models.TransactionType.PURCHASE,
            shares=Decimal("2.00"),
            price=Decimal("50.00"),
        )
    )
    price_service.add_prices(
        [
            models.MarketPrice(
                date=date(2024, 1, 2),
                asset_id=2,
                value=Decimal("50.00"),
                currency="USD",
            ),
            models.MarketPrice(
                date=date(2024, 1, 3),
                asset_id=2,
                value=Decimal("60.00"),
                currency="USD",
            ),
        ]
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
    price_service,
    portfolio_service,
):
    accounts = [
        models.Account(id=1, name="Account 1"),
        models.Account(id=2, name="Account 2"),
    ]
    for account in accounts:
        account_service.add_account(account)

    asset_service.add_asset(
        models.AssetPosition(
            id=1,
            symbol="ASSET1",
            name="Asset 1",
            type=models.AssetType.STOCK,
            still_open=True,
            account=accounts[0],
        )
    )
    transaction_service.add_transaction(
        models.TransactionRecord(
            id=1,
            asset_id=1,
            date=date(2024, 1, 1),
            type=models.TransactionType.PURCHASE,
            shares=Decimal("10.00"),
            price=Decimal("100.00"),
        )
    )
    price_service.add_prices(
        [
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
    asset_service.add_asset(
        models.AssetPosition(
            id=2,
            symbol="ASSET2",
            name="Asset 2",
            type=models.AssetType.STOCK,
            still_open=True,
            account=accounts[1],
        )
    )
    transaction_service.add_transaction(
        models.TransactionRecord(
            id=2,
            asset_id=2,
            date=date(2024, 1, 2),
            type=models.TransactionType.PURCHASE,
            shares=Decimal("2.00"),
            price=Decimal("50.00"),
        )
    )
    price_service.add_prices(
        [
            models.MarketPrice(
                date=date(2024, 1, 2),
                asset_id=2,
                value=Decimal("50.00"),
                currency="USD",
            ),
            models.MarketPrice(
                date=date(2024, 1, 3),
                asset_id=2,
                value=Decimal("60.00"),
                currency="USD",
            ),
        ]
    )

    history = portfolio_service.calculate_portfolio_value_history()

    assert history.to_dict() == {
        date(2024, 1, 1): Decimal("1000.00"),
        date(2024, 1, 2): Decimal("1200.00"),
        date(2024, 1, 3): Decimal("120.00"),
    }
