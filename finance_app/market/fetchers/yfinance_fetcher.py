import pandas as pd
import yfinance as yf


def get_prices(symbol: str) -> pd.Series:

    history = yf.Ticker(symbol).history(period="max", auto_adjust=False)

    if history.empty:
        return pd.Series()

    return history["Close"]


def get_dividends(symbol: str) -> pd.Series:

    divs = yf.Ticker(symbol).dividends

    if divs.empty:
        return pd.Series()

    return divs


def get_stock_splits(symbol: str) -> pd.Series:

    splits = yf.Ticker(symbol).splits

    if splits.empty:
        return pd.Series()

    return splits
