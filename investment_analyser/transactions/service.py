from investment_analyser.market_data.repository.stock_splits import get_stock_splits
from investment_analyser.models.models import (
    AdjustedTransaction,
    StockSplit,
    TransactionRecord,
)


def get_split_adjusted_transactions(
    transactions: list[TransactionRecord],
) -> list[AdjustedTransaction]:

    adj_transactions = []
    for transaction in transactions:
        adj_transaction = AdjustedTransaction(
            transaction_record=transaction,
            is_adjusted=False,
            shares=transaction.shares,
            price=transaction.price,
        )
        for split in get_stock_splits(transaction.id):
            if transaction.date <= split.date:
                adj_transaction = AdjustedTransaction(
                    transaction_record=transaction,
                    is_adjusted=True,
                    shares=transaction.shares * split.split_ratio,
                    price=transaction.price / split.split_ratio,
                )

        adj_transactions.append(adj_transaction)

    return adj_transactions


def adjust_transactions_for_splits(
    transactions: list[TransactionRecord], splits: list[StockSplit]
) -> list[AdjustedTransaction]:
    """Adjust transactions for stock splits occurring after each transaction date."""

    adj_transactions = []
    for transaction in transactions:
        adj_transaction = AdjustedTransaction(
            transaction_record=transaction,
            is_adjusted=False,
            shares=transaction.shares,
            price=transaction.price,
        )
        for split in splits:
            if transaction.date < split.date:
                adj_transaction.shares *= split.split_ratio
                adj_transaction.price /= split.split_ratio
                adj_transaction.is_adjusted = True

        adj_transactions.append(adj_transaction)

    return adj_transactions
