from pandas import Series, Timedelta

from investment_analyser.assets.repository import (
    get_all_assets,
    get_asset_by_symbol,
    get_etf_data,
)
from investment_analyser.filters import format_currency, format_percent
from investment_analyser.market_data.fetchers.yfinance import YFetcher
from investment_analyser.market_data.repository import prices


def calculate_price_change(prices: Series, years: float) -> float | None:
    """Returns the price change for the asset as specified in `years`."""

    total_days = (prices.index[-1] - prices.index[0]).days
    min_days = years * 365
    while min_days < total_days:
        min_date = prices.index[-1] - Timedelta(days=min_days)
        prices_since = prices[prices.index >= min_date]

        if (prices_since.index[-1] - prices_since.index[0]).days >= min_days:
            price_change = (
                prices_since.iloc[-1] - prices_since.iloc[0]
            ) / prices_since.iloc[0]
            return float(price_change)

        else:
            min_days += 1

    return None

def format_etf_table_for_fetched_assets(symbol: str) -> dict:
    """Format ETF data for display in the comparison and search views."""

    fetcher = YFetcher(symbol)

    basic_info = {}
    basic_info["Symbol"] = fetcher.get_info("symbol")
    basic_info["Name"] = fetcher.get_info("longName")
    net_expense_ratio = fetcher.get_info("netExpenseRatio")
    if net_expense_ratio:
        basic_info["Net expense ratio"] = format_percent(
            net_expense_ratio, in_percent=True
        )
    total_assets = fetcher.get_info("netAssets")
    currency = fetcher.get_info("currency")

    if total_assets and currency:
        basic_info["Total assets"] = format_currency(total_assets, currency)

    performance = {}
    years = [1, 3, 5, 10]
    for year in years:
        price_change = calculate_price_change(fetcher.get_prices(), year)

        if price_change:
            performance[f"{year}-year change"] = format_percent(price_change)

    sector_weighting = {}
    i = 1
    for sector_key, sector_weight in fetcher.get_sector_weighting().items():
        sector_weighting[f"sector_{i}"] = (
            f"{sector_key} ({format_percent(sector_weight)})"
        )
        i += 1

    top_holdings = {}
    i = 1
    for _, row in fetcher.get_top_holdings().iterrows():
        top_holdings[f"holding_{i}"] = (
            f"{row['Name']} ({format_percent(row['Holding Percent'])})"
        )
        i += 1

    return basic_info | performance | sector_weighting | top_holdings


def format_etf_table_for_existing_assets(symbol: str) -> dict:
    """Format ETF data for display in the comparison and search views."""

    fetcher = YFetcher(symbol)
    asset = get_asset_by_symbol(symbol)
    if not fetcher.is_etf():
        underlying_symbol = get_etf_data(asset.id).underlying_etf_symbol
        fetcher = YFetcher(underlying_symbol)

    basic_info = {}
    basic_info["Symbol"] = asset.info.symbol
    basic_info["Name"] = asset.info.name

    performance = {}
    years = [1, 3, 5, 10]
    for year in years:
        if asset:
            asset_prices = prices.get_prices(asset.id)
            prices_ser = Series(
                data=[item["unit_price"] for item in asset_prices],
                index=[item["date"] for item in asset_prices],
            )
            price_change = calculate_price_change(prices_ser, year)
        else:
            price_change = calculate_price_change(fetcher.get_prices(), year)

        if price_change:
            performance[f"{year}-year change"] = format_percent(price_change)

    sector_weighting = {}
    i = 1
    for sector_key, sector_weight in fetcher.get_sector_weighting().items():
        sector_weighting[f"sector_{i}"] = (
            f"{sector_key} ({format_percent(sector_weight)})"
        )
        i += 1

    top_holdings = {}
    i = 1
    for _, row in fetcher.get_top_holdings().iterrows():
        top_holdings[f"holding_{i}"] = (
            f"{row['Name']} ({format_percent(row['Holding Percent'])})"
        )
        i += 1

    return basic_info | performance | sector_weighting | top_holdings


def get_etfs_for_comparison() -> list[dict]:
    """Return formatted data for each ETF in the watchlist."""

    return [
        format_etf_table_for_existing_assets(asset.info.symbol)
        for asset in get_all_assets()
        if asset.info.type == "ETF"
    ]


def get_etf_search_result(ticker: str) -> dict | None:
    """Return the formatted search result if the ticker identifies an ETF."""

    fetcher = YFetcher(ticker)
    if not fetcher.is_etf():
        return None

    return format_etf_table_for_fetched_assets(ticker)
