from pandas import Series, to_datetime

from app.fetchers.yfinance import YFetcher
from app.models.models import AssetPosition
from app.repositories.stock_splits import (
    delete_stock_splits,
    get_stock_splits,
    insert_stock_split,
)


class StockSplitService:
    def __init__(self, asset_id: int) -> None:
        self.stock_splits = get_stock_splits(asset_id)

    @classmethod
    def delete_stock_splits(cls, asset: AssetPosition) -> None:
        delete_stock_splits(asset.id)

    @classmethod
    def update_stock_splits(cls, asset: AssetPosition) -> None:
        splits = Series()
        if asset.info.type == "Stock":
            splits = YFetcher(asset.info.symbol).get_stock_splits()

        if not splits.empty:
            for date, split in splits.items():
                insert_stock_split(
                    asset_id=asset.id,
                    date=to_datetime(str(date)).date(),
                    split_ratio=split,
                )
