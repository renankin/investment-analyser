from pandas import Series, to_datetime

from app.fetchers.yfinance import YFetcher
from app.models.models import AdjustedTransaction, AssetPosition, DividendReceived
from app.repositories.assets import (
    delete_asset,
    edit_asset,
    get_all_assets,
    get_asset_by_id,
    insert_asset,
)
from app.repositories.dividends import get_dividends, insert_dividend
from app.repositories.prices import get_market_prices
from app.repositories.stock_splits import get_stock_splits, insert_stock_split
from app.repositories.transactions import get_transactions_from_asset
from app.services.price_service import PriceService
from app.services.transaction_service import TransactionService


class AssetService:
    def __init__(self, asset_id: int) -> None:
        self.asset = get_asset_by_id(asset_id)
        self.price_analyser = PriceService(get_market_prices(self.asset.id))
        self.stock_splits = get_stock_splits(asset_id)
        self.dividends = get_dividends(asset_id)
        self.transactions = get_transactions_from_asset(asset_id)

    @classmethod
    def add_new_asset(
        cls,
        account_id: int,
        asset_symbol: str,
        asset_name: str,
        asset_type: str,
        still_open: bool,
    ) -> None:
        insert_asset(account_id, asset_symbol, asset_name, asset_type, still_open)

    @classmethod
    def get_all_assets(cls) -> list[AssetPosition]:
        return get_all_assets()

    def update_stock_splits(self) -> None:
        splits = Series()
        if self.asset.info.type == "Stock":
            splits = YFetcher(self.asset.info.symbol).get_stock_splits()

        if not splits.empty:
            for date, split in splits.items():
                insert_stock_split(
                    asset_id=self.asset.id,
                    date=to_datetime(str(date)).date(),
                    split_ratio=split,
                )

    def update_dividends(self) -> None:
        dividends = Series()
        if self.asset.info.type == "Stock":
            dividends = YFetcher(self.asset.info.symbol).get_dividends()

        if not dividends.empty:
            for date, div in dividends.items():
                insert_dividend(
                    asset_id=self.asset.id,
                    date=to_datetime(str(date)).date(),
                    dividend_value=div,
                )

    def get_dividends_received(self) -> list[DividendReceived]:

        t = TransactionService().adjust_transactions_for_splits(
            get_transactions_from_asset(self.asset.id), get_stock_splits(self.asset.id)
        )

        divs_received = []
        for div in self.dividends:
            if not self.asset.still_open:
                last_date = max(
                    [transaction.transaction_record.date for transaction in t]
                )
                if div.date >= last_date:
                    continue

            # Find how many shares on that dividend date
            shares = 0
            div_received = False
            for transaction in t:
                if transaction.transaction_record.date <= div.date:
                    div_received = True
                    shares += transaction.shares

            if div_received:
                divs_received.append(
                    DividendReceived(
                        date=div.date,
                        value=shares * div.value,
                        account=self.asset.account,
                    )
                )

        return divs_received

    def delete_asset(self) -> str | None:
        """Attempt to delete the asset. If it can't, return the name of the feature which blocked
        the deletion."""
        if get_transactions_from_asset(self.asset.id):
            return "transactions"
        if get_market_prices(self.asset.id):
            return "prices"
        if get_dividends(self.asset.id):
            return "dividends"
        if get_stock_splits(self.asset.id):
            return "splits"
        delete_asset(self.asset.id)
        return None

    def edit_asset(self, new_asset: AssetPosition) -> None:
        edit_asset(new_asset)

    def get_transactions_from_asset(self) -> list[AdjustedTransaction]:
        transactions = get_transactions_from_asset(self.asset.id)
        splits = get_stock_splits(self.asset.id)
        return TransactionService().adjust_transactions_for_splits(transactions, splits)
