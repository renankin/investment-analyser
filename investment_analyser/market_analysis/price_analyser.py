from pandas import Series, Timedelta


def calculate_price_change(prices: Series, years: float) -> float:
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
