from datetime import date
from decimal import Decimal

from pytest import fixture

from app.models import models
from app.ports import repository
from app.services.transaction_service import TransactionService


class FakeTransactionRepository(repository.TransactionRepository):
    def __init__(self):
        self.transactions: list[models.TransactionRecord] = []

    def add_transaction(self, transaction: models.TransactionRecord) -> None:
        self.transactions.append(transaction)

    def delete_transaction(self, transaction: models.TransactionRecord) -> None:
        self.transactions.remove(transaction)

    def edit_transaction(self, new_transaction: models.TransactionRecord) -> None:
        [
            new_transaction
            for transaction in self.transactions
            if transaction == self.get_transaction_by_id(new_transaction.id)
        ]

    def get_transaction_by_id(self, transaction_id: int) -> models.TransactionRecord:
        return next(
            transaction
            for transaction in self.transactions
            if transaction.id == transaction_id
        )

    def get_transactions_for_asset(
        self, asset_id: int
    ) -> list[models.TransactionRecord]:
        return [
            transaction
            for transaction in self.transactions
            if transaction.asset_id == asset_id
        ]


class FakeStockSplitRepository(repository.StockSplitRepository):
    def __init__(self):
        self.stock_splits: list[models.StockSplit] = []

    def add_stock_splits(self, stock_splits: list[models.StockSplit]) -> None:
        [self.stock_splits.append(stock) for stock in stock_splits]

    def get_stock_splits_for_asset(self, asset_id: int) -> list[models.StockSplit]:
        return [
            stock_split
            for stock_split in self.stock_splits
            if stock_split.asset_id == asset_id
        ]


@fixture
def fake_transaction_repository():
    return FakeTransactionRepository()


@fixture
def fake_stock_split_repository():
    repository = FakeStockSplitRepository()
    repository.add_stock_splits(
        [
            models.StockSplit(
                date=date(2025, 1, 31), asset_id=1, split_ratio=Decimal("2.0")
            )
        ]
    )
    return repository


@fixture
def transaction_service(fake_transaction_repository, fake_stock_split_repository):
    return TransactionService(fake_transaction_repository, fake_stock_split_repository)


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


def test_adjusted_transaction_orchestration(transaction_service, transaction):
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
