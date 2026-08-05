from pandas import Series

from finance_app.assets import assets
from finance_app.db import execute_db, query_db
from finance_app.market.fetchers.yfinance_fetcher import YFetcher


def get_stock_splits(asset_id: int) -> list:
    """Fetch splits from database and returns a list of dictionaries containing `date`
    and `split_ratio`."""

    query = (
        "SELECT date, split_ratio FROM stock_splits"
        " WHERE asset_id = ?"
        " ORDER BY date DESC"
    )

    return query_db(query, (asset_id,))



def delete_stock_splits(asset_id: int) -> bool:
    """Deletes stock splits from database."""

    splits = get_stock_splits(asset_id)

    if splits:
        execute_db("DELETE FROM stock_splits WHERE asset_id = ?", (asset_id,))
        return True

    return False


def insert_stock_splits(asset_id: int) -> bool:
    """Insert stock splits in database and returns True if successful."""

    asset = assets.get_asset(asset_id)

    splits = Series()
    if asset["asset_type"] == "Stock":
        splits = YFetcher(asset["asset_symbol"]).get_stock_splits()

    if not splits.empty:
        args = []
        for date, split in splits.items():
            args.append((asset_id, date, split))

        execute_db(
            "INSERT INTO stock_splits (asset_id, date, split_ratio)"
            " VALUES (?, ?, ?)"
            " ON CONFLICT (date, asset_id) DO NOTHING",
            args,
        )

        return True

    return False
