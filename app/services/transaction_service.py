from app.models import models
from app.ports import repository


class TransactionService:
    def __init__(
        self,
        transaction_repository: repository.TransactionRepository,
        stock_split_repository: repository.StockSplitRepository,
    ) -> None:
        self._transaction_repository = transaction_repository
        self._stock_split_repository = stock_split_repository

    def adjust_transactions_for_splits(
        self, asset_id: int
    ) -> list[models.AdjustedTransaction]:
        adj_transactions = []
        transactions = self._transaction_repository.get_transactions_for_asset(asset_id)
        stock_splits = self._stock_split_repository.get_stock_splits_for_asset(asset_id)
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

    def add_transaction(self, transaction: models.TransactionRecord) -> None:
        self._transaction_repository.add_transaction(transaction)

    def edit_transaction(self, new_transaction: models.TransactionRecord) -> None:
        self._transaction_repository.edit_transaction(new_transaction)

    def delete_transaction(self, transaction: models.TransactionRecord) -> None:
        self._transaction_repository.delete_transaction(transaction)
