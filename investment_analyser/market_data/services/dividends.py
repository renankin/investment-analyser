from pandas import Series

from investment_analyser.assets.repository import get_asset
from investment_analyser.market_data.fetchers.yfinance import YFetcher
from investment_analyser.market_data.repository.dividends import insert_dividend


def insert_dividends(asset_id: int) -> bool:
    """Insert dividends for stock in database and returns True if successful."""

    asset = get_asset(asset_id)

    dividends = Series()
    if asset["asset_type"] == "Stock":
        dividends = YFetcher(asset["asset_symbol"]).get_dividends()

    if not dividends.empty:
        for date, div in dividends.items():
            insert_dividend(asset_id=asset_id, date=date, dividend_value=div)

        return True

    return False
