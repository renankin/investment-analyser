from app.models.models import (
    AdjustedTransaction,
    StockSplit,
    TransactionRecord,
)
from app.repositories.transactions import get_transactions_from_asset
from app.services.stock_split_service import StockSplitService


class TransactionService:
    def __init__(self, asset_id: int) -> None:
        self.transactions = get_transactions_from_asset(asset_id)
        self.adj_transactions = self.adjust_transactions_for_splits(
            transactions=self.transactions,
            stock_splits=StockSplitService(asset_id).stock_splits,
        )

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
