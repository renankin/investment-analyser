from pandas import DataFrame, Series, Timedelta
from yfinance import Ticker
from yfinance.exceptions import YFException


class Fetcher:
    def __init__(self, symbol: str):

        self.ticker = Ticker(symbol)

        try:
            self.ticker.info
        except YFException:
            self.ticker = None

    def is_etf(self) -> bool:

        if self.ticker.info.get("quoteType") == "ETF":
            return True

        return False

    def is_stock(self) -> bool:

        if self.ticker.info.get("quoteType") == "EQUITY":
            return True

        return False

    def get_dividends(self) -> Series:

        if not self.is_stock():
            return Series()

        divs = self.ticker.dividends

        if divs.empty:
            return Series()

        return divs

    def get_prices(self) -> Series:

        if not self.ticker:
            return Series()

        history = self.ticker.history(period="max", auto_adjust=False)

        if history.empty:
            return Series()

        return history["Close"]

    def get_stock_splits(self) -> Series:

        if not self.is_stock():
            return Series()

        splits = self.ticker.splits

        if splits.empty:
            return Series()

        return splits

    def get_top_holdings(self) -> DataFrame:

        if self.is_etf():
            return self.ticker.funds_data.top_holdings

        return DataFrame()

    def get_sector_weightings(self) -> dict:

        if self.is_etf():
            return self.ticker.funds_data.sector_weightings

        return {}

    def get_info(self) -> dict:

        if not self.ticker:
            return {}

        return self.ticker.info

    def get_performance(self) -> DataFrame:
        """Returns the 1, 3, 5 and 10-year performance for the fund.
        The performance is simply the price change over time."""

        prices = self.get_prices()

        if prices.empty:
            return DataFrame()

        total_days = (prices.index[-1] - prices.index[0]).days

        performance_df = DataFrame(columns=["Years", "Percentage"])
        years = [1, 3, 5, 10]

        for year in years:
            found = False
            min_days = year * 365

            while not found and min_days < total_days:
                min_date = prices.index[-1] - Timedelta(days=min_days)
                prices_since = prices[prices.index >= min_date]

                if (prices_since.index[-1] - prices_since.index[0]).days >= min_days:
                    percent = (
                        100
                        * (prices_since.iloc[-1] - prices_since.iloc[0])
                        / prices_since.iloc[0]
                    )
                    found = True

                else:
                    min_days += 1

            if not found:
                percent = None

            performance_df.loc[len(performance_df)] = [year, percent]

        return performance_df
