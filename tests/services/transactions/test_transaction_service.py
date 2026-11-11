from datetime import date
from decimal import Decimal

from pytest import fixture

from app.models import models


@fixture
def transaction():
    return models.TransactionRecord(
        id=1,
        asset_id=1,
        date=date(2024, 1, 31),
        type=models.TransactionType.PURCHASE,
        shares=Decimal("10.00"),
        price=Decimal("100.00"),
    )


def test_add_transaction(transaction, fake_transaction_repository, transaction_service):
    transaction_service.add_transaction(transaction)
    assert transaction in fake_transaction_repository.transactions


def test_delete_transaction(
    transaction, fake_transaction_repository, transaction_service
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


