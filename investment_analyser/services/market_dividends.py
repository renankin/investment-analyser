from pandas import Series

from investment_analyser.fetchers.yfinance import YFetcher
from investment_analyser.repository.assets import get_asset_by_id
from investment_analyser.repository.dividends import insert_dividend


def insert_dividends(asset_id: int) -> bool:
    """Insert dividends for stock in database and returns True if successful."""

    asset = get_asset_by_id(asset_id)

    dividends = Series()
    if asset.info.type == "Stock":
        dividends = YFetcher(asset.info.symbol).get_dividends()

    if not dividends.empty:
        for date, div in dividends.items():
            insert_dividend(asset_id=asset_id, date=date, dividend_value=div)

        return True

    return False
