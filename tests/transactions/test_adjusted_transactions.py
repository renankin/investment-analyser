from datetime import date
from decimal import Decimal

from app.models import models
from app.services.transaction_service import TransactionService

ACCOUNT = models.Account(id=1, name="Account")
ASSET_INFO = models.AssetInfo(symbol="APPL", name="Apple", type="Stock")
ASSET_POS = models.AssetPosition(
    id=1,
    symbol="APPL",
    name="Apple",
    type=models.AssetType.STOCK,
    still_open=True,
    account=ACCOUNT,
)


def test_single_stock_split_adjustment():

    transaction_record = models.TransactionRecord(
        id=1,
        asset_id=1,
        date=date(2024, 1, 31),
        shares=Decimal("10.00"),
        price=Decimal("100.00"),
    )

    stock_split = models.StockSplit(
        asset=ASSET_INFO, date=date(2025, 1, 31), split_ratio=Decimal("2.0")
    )

    adjusted_transaction = models.AdjustedTransaction(
        transaction_record=transaction_record,
        shares=Decimal("20.00"),
        price=Decimal("50.00"),
        is_adjusted=True,
    )

    assert TransactionService.adjust_transactions_for_splits(
        [transaction_record], [stock_split]
    ) == [adjusted_transaction]


def test_sequential_stock_splits_adjustment():

    transaction_record = models.TransactionRecord(
        id=1,
        asset_id=1,
        date=date(2024, 1, 31),
        shares=Decimal("10.00"),
        price=Decimal("100.00"),
    )

    stock_splits = [
        models.StockSplit(
            asset=ASSET_INFO, date=date(2025, 1, 31), split_ratio=Decimal("2.0")
        ),
        models.StockSplit(
            asset=ASSET_INFO, date=date(2026, 1, 31), split_ratio=Decimal("2.0")
        ),
    ]

    adjusted_transaction = models.AdjustedTransaction(
        transaction_record=transaction_record,
        shares=Decimal("40.00"),
        price=Decimal("25.00"),
        is_adjusted=True,
    )

    assert TransactionService.adjust_transactions_for_splits(
        [transaction_record], stock_splits
    ) == [adjusted_transaction]


def test_adjusted_transactions_for_multiple_records():

    transactions = [
        models.TransactionRecord(
            id=1,
            asset_id=1,
            date=date(2026, 1, 31),
            shares=Decimal("10.00"),
            price=Decimal("60.00"),
        ),
        models.TransactionRecord(
            id=2,
            asset_id=1,
            date=date(2023, 1, 31),
            shares=Decimal("5.00"),
            price=Decimal("10.00"),
        ),
    ]

    stock_splits = [
        models.StockSplit(
            asset=ASSET_INFO, date=date(2025, 1, 31), split_ratio=Decimal("2.0")
        ),
        models.StockSplit(
            asset=ASSET_INFO, date=date(2022, 1, 31), split_ratio=Decimal("10.0")
        ),
    ]

    adjusted_transactions = [
        models.AdjustedTransaction(
            transaction_record=transactions[0],
            shares=Decimal("10.00"),
            price=Decimal("60.00"),
            is_adjusted=False,
        ),
        models.AdjustedTransaction(
            transaction_record=transactions[1],
            shares=Decimal("10.00"),
            price=Decimal("5.00"),
            is_adjusted=True,
        ),
    ]

    assert (
        TransactionService.adjust_transactions_for_splits(transactions, stock_splits)
        == adjusted_transactions
    )


def test_split_same_date():

    transactions = [
        models.TransactionRecord(
            id=3,
            asset_id=1,
            date=date(2023, 1, 31),
            shares=Decimal("5.00"),
            price=Decimal("10.00"),
        )
    ]

    stock_splits = [
        models.StockSplit(asset=ASSET_INFO, date=date(2023, 1, 31), split_ratio=Decimal("2.0"))
    ]

    adjusted_transactions = [
        models.AdjustedTransaction(
            transaction_record=transactions[0],
            is_adjusted=False,
            shares=Decimal("5.00"),
            price=Decimal("10.00"),
        )
    ]

    assert (
        TransactionService.adjust_transactions_for_splits(transactions, stock_splits)
        == adjusted_transactions
    )


def test_empty_inputs():

    assert TransactionService.adjust_transactions_for_splits([], []) == []


def test_no_applicable_split():

    transactions = [
        models.TransactionRecord(
            id=4,
            asset_id=1,
            date=date(2024, 1, 31),
            shares=Decimal("10.00"),
            price=Decimal("100.00"),
        )
    ]

    stock_splits = [
        models.StockSplit(
            asset=ASSET_INFO, date=date(2023, 1, 31), split_ratio=Decimal("2.0")
        ),
        models.StockSplit(
            asset=ASSET_INFO, date=date(2022, 1, 31), split_ratio=Decimal("3.0")
        ),
    ]

    adjusted_transactions = [
        models.AdjustedTransaction(
            transaction_record=transactions[0],
            is_adjusted=False,
            shares=Decimal("10.00"),
            price=Decimal("100.00"),
        )
    ]

    assert (
        TransactionService.adjust_transactions_for_splits(transactions, stock_splits)
        == adjusted_transactions
    )


def test_decimal_precision():

    transactions = [
        models.TransactionRecord(
            id=5,
            asset_id=1,
            date=date(2024, 1, 31),
            shares=Decimal("10.53"),
            price=Decimal("10.20"),
        )
    ]

    stock_splits = [
        models.StockSplit(asset=ASSET_INFO, date=date(2025, 1, 31), split_ratio=Decimal("2.5"))
    ]

    adjusted_transactions = [
        models.AdjustedTransaction(
            transaction_record=transactions[0],
            is_adjusted=True,
            shares=Decimal("26.325"),
            price=Decimal("4.08"),
        )
    ]

    assert (
        TransactionService.adjust_transactions_for_splits(transactions, stock_splits)
        == adjusted_transactions
    )
