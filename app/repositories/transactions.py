from datetime import date
from decimal import Decimal

from app.db.connection import (
    execute_db,
    fetch_multiple_records,
    fetch_single_record,
)
from app.models.models import (
    Account,
    AssetInfo,
    AssetPosition,
    TransactionRecord,
)

ALL_TRANSACTIONS_QUERY = (
    "SELECT accounts.account_id, accounts.account_name, accounts.currency,"
    "assets.asset_id, assets.asset_symbol, assets.asset_name, assets.asset_type, assets.still_open,"
    " transactions.transaction_id, transactions.date, transactions.shares, transactions.price"
    " FROM transactions"
    " JOIN assets ON transactions.asset_id = assets.asset_id"
    " JOIN accounts ON assets.account_id = accounts.account_id"
)


def delete_transaction(transaction_id: int) -> None:

    execute_db("DELETE FROM transactions WHERE transaction_id = ?", (transaction_id,))


def get_all_transactions() -> list[TransactionRecord]:

    return [
        TransactionRecord(
            id=row["transaction_id"],
            asset=AssetPosition(
                id=row["asset_id"],
                info=AssetInfo(
                    symbol=row["asset_symbol"],
                    name=row["asset_name"],
                    type=row["asset_type"],
                ),
                still_open=row["still_open"],
                account=Account(
                    id=row["account_id"],
                    name=row["account_name"],
                    currency=row["currency"],
                ),
            ),
            date=row["date"],
            shares=row["shares"],
            price=row["price"],
        )
        for row in fetch_multiple_records(ALL_TRANSACTIONS_QUERY)
    ]


def get_transactions_for_open_assets() -> list[TransactionRecord]:

    return [
        TransactionRecord(
            id=row["transaction_id"],
            asset=AssetPosition(
                id=row["asset_id"],
                info=AssetInfo(
                    symbol=row["asset_symbol"],
                    name=row["asset_name"],
                    type=row["asset_type"],
                ),
                still_open=row["still_open"],
                account=Account(
                    id=row["account_id"],
                    name=row["account_name"],
                    currency=row["currency"],
                ),
            ),
            date=row["date"],
            shares=row["shares"],
            price=row["price"],
        )
        for row in fetch_multiple_records(
            ALL_TRANSACTIONS_QUERY
            + " WHERE assets.still_open = 1 ORDER BY transactions.date DESC",
        )
    ]


def get_transaction_by_id(transaction_id: int) -> TransactionRecord:

    record = fetch_single_record(
        ALL_TRANSACTIONS_QUERY
        + " WHERE transactions.transaction_id = ? ORDER BY transactions.date DESC",
        (transaction_id,),
    )

    return TransactionRecord(
        id=record["transaction_id"],
        asset=AssetPosition(
            id=record["asset_id"],
            info=AssetInfo(
                symbol=record["asset_symbol"],
                name=record["asset_name"],
                type=record["asset_type"],
            ),
            still_open=record["still_open"],
            account=Account(
                id=record["account_id"],
                name=record["account_name"],
                currency=record["currency"],
            ),
        ),
        date=record["date"],
        shares=record["shares"],
        price=record["price"],
    )


def get_transactions_from_asset(asset_id: int) -> list[TransactionRecord]:
    return [
        TransactionRecord(
            id=row["transaction_id"],
            asset=AssetPosition(
                id=row["asset_id"],
                info=AssetInfo(
                    symbol=row["asset_symbol"],
                    name=row["asset_name"],
                    type=row["asset_type"],
                ),
                still_open=row["still_open"],
                account=Account(
                    id=row["account_id"],
                    name=row["account_name"],
                    currency=row["currency"],
                ),
            ),
            date=row["date"],
            shares=row["shares"],
            price=row["price"],
        )
        for row in fetch_multiple_records(
            ALL_TRANSACTIONS_QUERY
            + " WHERE assets.asset_id = ? ORDER BY transactions.date DESC",
            (asset_id,),
        )
    ]


def insert_transaction(
    asset_id: int,
    date: date,
    shares: Decimal,
    price: Decimal,
) -> None:

    execute_db(
        "INSERT INTO transactions (asset_id, date, price, shares) VALUES (?, ?, ?, ?)",
        (asset_id, date.isoformat(), price, shares),
    )


def update_transaction(transaction: TransactionRecord) -> None:

    execute_db(
        "UPDATE transactions SET asset_id = ?, date = ?, shares = ?, price = ?"
        " WHERE transaction_id = ?",
        (
            transaction.asset.id,
            transaction.date.isoformat(),
            transaction.shares,
            transaction.price,
            transaction.id,
        ),
    )
