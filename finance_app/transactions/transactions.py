from finance_app.db import query_db, execute_db
from finance_app.market import stock_splits


def delete_transaction(transaction_id: int):
    """Deletes transaction."""

    execute_db("DELETE FROM transactions WHERE transaction_id = ?", (transaction_id,))


def get_all_transactions() -> list:
    """Fetch all transactions from database and returns a list of dictionaries
    containing `transaction_id`, `account_name`, `asset_name`, `date`, `currency`,
    `shares`, `adj_shares`, `price` and `adj_price`."""

    query = (
        "SELECT accounts.account_name, accounts.currency, assets.asset_name,"
        " transactions.transaction_id, transactions.date, transactions.shares, "
        " transactions.price"
        " FROM transactions"
        " JOIN assets ON transactions.asset_id = assets.asset_id"
        " JOIN accounts ON assets.account_id = accounts.account_id"
        " ORDER BY transactions.date DESC"
    )

    transactions = query_db(query)

    if transactions:
        for t in transactions:
            adj_t = get_adjusted_transaction(t["transaction_id"])
            t["adj_shares"] = adj_t["shares"]
            t["adj_price"] = adj_t["price"]
            t["is_adjusted"] = adj_t["is_adjusted"]

        return transactions

    return []


def get_adjusted_transactions(asset_id: int) -> list:
    """Adjust cashflow for assets when there are stock splits and returns a list of
    dictionaries containing `date`, `shares`, `price` and `adjusted`."""

    transactions = get_transactions(asset_id)

    new_t = []

    for t in transactions:
        new_t.append(get_adjusted_transaction(t["transaction_id"]))

    return new_t


def get_adjusted_transaction(transaction_id: int) -> dict:
    """Adjust transaction when there is a stock split and returns a dictionary containing
    `asset_id`, `transaction_id`, `shares`, `price`, `date` and `is_adjusted`"""

    t = get_transaction(transaction_id)

    s = stock_splits.get_stock_splits(t["asset_id"])

    new_t = t
    t["is_adjusted"] = False

    for split in s:
        if t["date"] <= split["date"]:
            new_t["shares"] *= split["split_ratio"]
            new_t["price"] /= split["split_ratio"]
            new_t["is_adjusted"] = True

    return new_t


def get_transaction(transaction_id: int) -> dict:
    """Returns a dictionary containing `asset_id`, `transaction_id`,
    `shares`, `price` and `date` keys"""

    query = (
        "SELECT asset_id, transaction_id, shares, price, date"
        " FROM transactions"
        " WHERE transaction_id = ?"
    )

    transaction = query_db(query, (transaction_id,), one=True)

    if transaction:
        return transaction

    return {}


def get_transactions(asset_id: int) -> list:
    """Fetch all transactions of an asset and return as list of dictionaries
    with `transaction_id`, `asset_id`, `date`, `price` and `shares`."""

    query = (
        "SELECT transaction_id, asset_id, date, shares, price"
        " FROM transactions"
        " WHERE asset_id = ?"
    )

    transactions = query_db(query, (asset_id,))

    if transactions:
        return transactions

    return []


def insert_transaction(asset_id: int, date: str, shares: float, price: float):
    """Inserts transaction in database."""

    query = (
        "INSERT INTO transactions (asset_id, date, price, shares) VALUES (?, ?, ?, ?)"
    )

    execute_db(query, (asset_id, date, price, shares))


def update_transaction(
    transaction_id: int, asset_id: int, date: str, shares: float, price: float
):
    """Updates transaction."""

    query = (
        "UPDATE transactions SET asset_id = ?, date = ?, shares = ?, price = ?"
        " WHERE transaction_id = ?"
    )

    execute_db(query, (asset_id, date, shares, price, transaction_id))
