from app.models.models import (
    AdjustedTransaction,
    StockSplit,
    TransactionRecord,
)


class TransactionService:
    def __init__(self) -> None:
        pass

    def adjust_transactions_for_splits(
        self, transactions: list[TransactionRecord], stock_splits: list[StockSplit]
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
