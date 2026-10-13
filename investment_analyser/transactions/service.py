from datetime import date
from decimal import Decimal
from typing import TypedDict

from investment_analyser.market_data.repository.stock_splits import get_stock_splits
from investment_analyser.models.models import AdjustedTransaction, TransactionRecord


class Transaction(TypedDict):
    """Contains `date`, `shares` and `price`."""

    date: date
    shares: Decimal
    price: Decimal


class StockSplit(TypedDict):
    date: date
    split_ratio: Decimal


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
            if transaction.date <= split["date"]:
                adj_transaction = AdjustedTransaction(
                    transaction_record=transaction,
                    is_adjusted=True,
                    shares=transaction.shares * split["split_ratio"],
                    price=transaction.price / split["split_ratio"],
                )

        adj_transactions.append(adj_transaction)

    return adj_transactions


def adjust_transactions_for_splits(
    transactions: list[Transaction], splits: list[StockSplit]
) -> list[Transaction]:
    """Adjust transactions for stock splits occurring after each transaction date."""

    adj_transactions = []
    for transaction in transactions:
        adj_transaction: Transaction = {
            "date": transaction["date"],
            "shares": transaction["shares"],
            "price": transaction["price"],
        }

        for split in splits:
            if transaction["date"] < split["date"]:
                adj_transaction["shares"] *= split["split_ratio"]
                adj_transaction["price"] /= split["split_ratio"]

        adj_transactions.append(adj_transaction)

    return adj_transactions
