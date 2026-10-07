from pandas import Series

from investment_analyser.assets.repository import get_asset
from investment_analyser.market_data.fetchers.yfinance import YFetcher
from investment_analyser.market_data.repository.stock_splits import insert_stock_split


def insert_stock_splits(asset_id: int) -> bool:
    """Insert stock splits in database and returns True if successful."""

    asset = get_asset(asset_id)

    splits = Series()
    if asset["asset_type"] == "Stock":
        splits = YFetcher(asset["asset_symbol"]).get_stock_splits()

    if not splits.empty:
        for date, split in splits.items():
            insert_stock_split(asset_id=asset_id, date=date, split_ratio=split)

        return True

    return False
