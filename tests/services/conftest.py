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

    def add_stock_split(self, stock_split: models.StockSplit):
        self.stock_splits.append(stock_split)

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
    return FakeStockSplitRepository()


@fixture
def transaction_service(fake_transaction_repository, fake_stock_split_repository):
    return TransactionService(fake_transaction_repository, fake_stock_split_repository)
