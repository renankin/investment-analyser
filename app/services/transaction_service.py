from decimal import Decimal

from app.models import models
from app.ports import repository


def adjust_transactions_for_splits(
    transactions: list[models.TransactionRecord],
    stock_splits: list[models.StockSplit],
) -> list[models.AdjustedTransaction]:
    adj_transactions = []
    for transaction in transactions:
        adj_transaction = models.AdjustedTransaction(
            transaction_record=transaction,
            is_adjusted=False,
            shares=transaction.shares,
            price=transaction.price,
        )
        for stock_split in stock_splits:
            if transaction.date < stock_split.date:
                adj_transaction.shares *= stock_split.split_ratio
                adj_transaction.price /= stock_split.split_ratio
                adj_transaction.is_adjusted = True
        adj_transactions.append(adj_transaction)
    return adj_transactions


class TransactionService:
    def __init__(
        self,
        transaction_repository: repository.TransactionRepository,
        stock_split_repository: repository.StockSplitRepository,
    ) -> None:
        self._transaction_repository = transaction_repository
        self._stock_split_repository = stock_split_repository

    def get_adjusted_transactions(
        self, asset_id: int
    ) -> list[models.AdjustedTransaction]:
        return adjust_transactions_for_splits(
            transactions=self._transaction_repository.get_transactions_for_asset(
                asset_id
            ),
            stock_splits=self._stock_split_repository.get_stock_splits_for_asset(
                asset_id
            ),
        )

    def get_shares_balance(self, asset_id: int) -> Decimal:
        adjusted_transactions = self.get_adjusted_transactions(asset_id)
        total_shares = Decimal("0.0")
        for transaction in adjusted_transactions:
            total_shares += transaction.shares
        return total_shares

    def add_transaction(self, transaction: models.TransactionRecord) -> None:
        self._transaction_repository.add_transaction(transaction)

    def edit_transaction(self, new_transaction: models.TransactionRecord) -> None:
        self._transaction_repository.edit_transaction(new_transaction)

    def delete_transaction(self, transaction: models.TransactionRecord) -> None:
        self._transaction_repository.delete_transaction(transaction)
