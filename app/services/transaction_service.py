from datetime import date
from decimal import Decimal

from app.models.models import (
    AdjustedTransaction,
    StockSplit,
    TransactionRecord,
)
from app.repositories.transactions import (
    delete_transaction,
    get_all_transactions,
    get_transaction_by_id,
    get_transactions_from_asset,
    insert_transaction,
    update_transaction,
)
from app.services.stock_split_service import StockSplitService


class TransactionService:
    def __init__(self, transaction_id: int) -> None:
        self.transaction = get_transaction_by_id(transaction_id)

    @classmethod
    def transactions_from_asset(cls, asset_id: int):
        return get_transactions_from_asset(asset_id)

    @classmethod
    def get_adjusted_transactions_from_asset(cls, asset_id: int):
        return TransactionService.adjust_transactions_for_splits(
            TransactionService.transactions_from_asset(asset_id),
            StockSplitService(asset_id).stock_splits,
        )

    @classmethod
    def get_all_transactions(cls) -> list[TransactionRecord]:
        return get_all_transactions()


    @classmethod
    def adjust_transactions_for_splits(
        cls, transactions: list[TransactionRecord], stock_splits: list[StockSplit]
    ) -> list[AdjustedTransaction]:
        adj_transactions = []
        for transaction in transactions:
            adj_transaction = AdjustedTransaction(
                transaction_record=transaction,
                is_adjusted=False,
                shares=transaction.shares,
                price=transaction.price,
            )
            for split in stock_splits:
                if transaction.date < split.date:
                    adj_transaction.shares *= split.split_ratio
                    adj_transaction.price /= split.split_ratio
                    adj_transaction.is_adjusted = True
            adj_transactions.append(adj_transaction)
        return adj_transactions

    def add_transaction(self, date: date, shares: Decimal, price: Decimal) -> None:
        insert_transaction(
            asset_id=self.transaction.asset.id,
            date=date,
            shares=shares,
            price=price,
        )

    def edit_transaction(self, new_transaction: TransactionRecord) -> None:
        update_transaction(new_transaction)

    def delete_transaction(self) -> None:
        delete_transaction(self.transaction.id)
