from datetime import date
from decimal import Decimal

import pytest

from app.models import models


@pytest.fixture
def transaction():
    return models.TransactionRecord(
        id=1,
        asset_id=1,
        date=date(2024, 1, 31),
        type=models.TransactionType.PURCHASE,
        shares=Decimal("10.00"),
        price=Decimal("100.00"),
    )


@pytest.fixture
def stock_splits():
    return [
        models.StockSplit(
            date=date(2025, 1, 31), asset_id=1, split_ratio=Decimal("2.0")
        )
    ]


def test_add_transaction(
    fake_transaction_repository,
    transaction,
    transaction_service,
):
    transaction_service.add_transaction(transaction)

    assert transaction in fake_transaction_repository.transactions


def test_delete_transaction(
    fake_transaction_repository,
    transaction,
    transaction_service,
):
    transaction_service.add_transaction(transaction)
    transaction_service.delete_transaction(transaction)
    assert transaction not in fake_transaction_repository.transactions


def test_edit_transaction(
    transaction, fake_transaction_repository, transaction_service
):
    transaction_service.add_transaction(transaction)
    new_transaction = transaction
    new_transaction.price = Decimal(50)
    transaction_service.edit_transaction(new_transaction)
    assert fake_transaction_repository.get_transaction_by_id(
        new_transaction.id
    ).price == Decimal(50)


def test_adjusted_transaction_orchestration(
    stock_splits, stock_split_service, transaction_service, transaction
):
    stock_split_service.add_stock_splits(stock_splits)
    transaction_service.add_transaction(transaction)
    adjusted_transactions = [
        models.AdjustedTransaction(
            transaction_record=transaction,
            is_adjusted=True,
            shares=Decimal("20.00"),
            price=Decimal("50.00"),
        )
    ]
    assert (
        transaction_service.get_adjusted_transactions(asset_id=1)
        == adjusted_transactions
    )
