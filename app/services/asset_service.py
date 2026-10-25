from pandas import Series, to_datetime

from app.fetchers.tesouro_direto import get_prices
from app.fetchers.yfinance import YFetcher
from app.repositories.assets import get_asset_by_id
from app.repositories.dividends import get_dividends, insert_dividend
from app.repositories.prices import get_market_prices, insert_price
from app.repositories.stock_splits import get_stock_splits, insert_stock_split
from app.services.price_analyser import PriceAnalyser


class AssetService:
    def __init__(self, asset_id: int) -> None:
        self.asset = get_asset_by_id(asset_id)
        self.price_analyser = PriceAnalyser(get_market_prices(self.asset.id))
        self.stock_splits = get_stock_splits(asset_id)
        self.dividends = get_dividends(asset_id)

    def update_prices(self) -> None:
        prices = Series()
        if self.asset.info.type in ["Stock", "ETF"]:
            prices = YFetcher(self.asset.info.symbol).get_prices()
        if self.asset.info.type == "Brazilian bond":
            prices = get_prices(self.asset.info.symbol)

        if not prices.empty:
            for date, price in prices.items():
                insert_price(
                    asset_id=self.asset.id,
                    date=to_datetime(str(date)).date(),
                    unit_price=price,
                )

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
