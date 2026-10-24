from pandas import Series, to_datetime

from app.fetchers.tesouro_direto import get_prices
from app.fetchers.yfinance import YFetcher
from app.repositories.assets import get_asset_by_id
from app.repositories.prices import get_market_prices, insert_price
from app.services.price_analyser import PriceAnalyser


class AssetService:
    def __init__(self, asset_id: int) -> None:
        self.asset = get_asset_by_id(asset_id)
        self.prices = get_market_prices(self.asset.id)
        self.price_analyser = PriceAnalyser(self.prices)

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
