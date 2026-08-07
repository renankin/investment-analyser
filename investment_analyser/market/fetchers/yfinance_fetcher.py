from pandas import DataFrame, Series, merge
from yfinance import Ticker
from yfinance.exceptions import YFException


class YFetcher:
    def __init__(self, symbol: str):

        self.ticker = Ticker(symbol)

        try:
            self.info = self.ticker.info
        except YFException:
            self.ticker = None

    def is_etf(self) -> bool:

        return self.info.get("quoteType") == "ETF"

    def is_stock(self) -> bool:

        return self.info.get("quoteType") == "EQUITY"

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

        return history["Close"].dropna()

    def get_stock_splits(self) -> Series:

        if not self.is_stock():
            return Series()

        splits = self.ticker.splits

        if splits.empty:
            return Series()

        return splits

    def get_top_holdings(self) -> DataFrame:
        """Returns a Dataframe with columns `Name` and `Holding Percent`
        which is indexed with `Symbol`. The DataFrame is sorted by holding percent."""

        if self.is_etf():
            return self.ticker.funds_data.top_holdings.sort_values(
                "Holding Percent", ascending=False
            )

        return None

    def get_sector_weighting(self) -> DataFrame:
        """Returns as DataFrame with columns `Holding Percent` and `Name` for each sector.
        The DataFrame is sorted by holding percent."""

        if self.is_etf():
            sector_map = {
                "realestate": "Real estate",
                "consumer_cyclical": "Consumer",
                "basic_materials": "Basic materials",
                "technology": "Technology",
                "communication_services": "Communication",
                "financial_services": "Financial",
                "utilities": "Utilities",
                "industrials": "Industrials",
                "energy": "Energy",
                "healthcare": "Healthcare",
            }

            df1 = DataFrame(
                data=self.ticker.funds_data.sector_weightings.values(),
                index=self.ticker.funds_data.sector_weightings.keys(),
                columns=["Holding Percent"],
            )

            df2 = DataFrame(
                data=sector_map.values(),
                index=sector_map.keys(),
                columns=["Name"],
            )

            return merge(
                left=df1, right=df2, right_index=True, left_index=True
            ).sort_values("Holding Percent", ascending=False)

        return None

    def get_info(self, key: str):
        """Returns the info requested via the `key` parameter from the `Ticker` class
        from yfinance if found, `None` if not found.

        Some valid keys:

        * `symbol`
        * `currency`
        * `longName`
        * `netAssets`
        * `netExpenseRatio`
        """

        if not self.ticker:
            return {}

        return self.info.get(key)
