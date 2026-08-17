from pandas import DataFrame
from yfinance import Ticker

from investment_analyser.assets.assets import get_etf_data
from investment_analyser.market.fetchers.yfinance_fetcher import YFetcher
from investment_analyser.market.repository import get_most_recent_price
from investment_analyser.transactions.repository import get_transactions_for_open_assets
from investment_analyser.transactions.service import get_split_adjusted_transactions


def get_asset_allocation() -> DataFrame:
    """
    Calculates the current porfolio distribution, showing the total shares, current price,
    total value and weight percent for each asset hold.

    Returns a dataframe with following columns:
    - `asset_id`
    - `asset_symbol`
    - `asset_type`
    - `currency`
    - `shares`
    - `price`
    - `total`
    - `weight_percent`
    """

    raw_transactions = get_transactions_for_open_assets()
    adjusted_transactions = DataFrame(get_split_adjusted_transactions(raw_transactions))

    grouped_df = adjusted_transactions.groupby(
        ["asset_id", "asset_symbol", "asset_type", "currency"],
        as_index=False,
    )[["shares"]].sum()
    grouped_df["price"] = grouped_df["asset_id"].apply(get_most_recent_price)
    grouped_df[["price", "currency"]] = grouped_df[["price", "currency"]].apply(
        convert_currency, axis=1
    )
    grouped_df["total"] = grouped_df["price"] * grouped_df["shares"]
    grouped_df["weight_percent"] = grouped_df["total"] / grouped_df["total"].sum(axis=0)

    return grouped_df


def convert_currency(row):

    if row["currency"] == "BRL":
        df = Ticker("GBPBRL=X").history(period="1d")
        row["price"] /= df["Close"].iloc[0]
        row["currency"] = "GBP"

    return row


def get_sector_distribution() -> dict:
    """
    Returns a dictionary containing the sector distribution for the portfolio.
    The returned dictionary contains the sector keys and weight distribution.
    """

    portfolio_df = get_asset_allocation()

    portfolio_sectors = {}
    for _, portfolio_asset in portfolio_df.iterrows():
        asset_symbol = portfolio_asset["asset_symbol"]

        if portfolio_asset["asset_type"] == "ETF":
            etf_data = get_etf_data(portfolio_asset["asset_id"])

            if "underlying_etf_symbol" in etf_data:
                asset_symbol = etf_data["underlying_etf_symbol"]

        asset_sectors = YFetcher(asset_symbol).get_sector_weighting()

        for sector_key in asset_sectors:
            asset_weight = asset_sectors[sector_key] * portfolio_asset["weight_percent"]

            if sector_key in portfolio_sectors:
                portfolio_sectors[sector_key] += asset_weight
            else:
                portfolio_sectors[sector_key] = asset_weight

    return portfolio_sectors
