from datetime import date
from decimal import Decimal
from typing import Any, TypedDict

from investment_analyser.assets.repository import get_asset
from investment_analyser.market_data.repository import dividends
from investment_analyser.transactions import transactions


class Dividend(TypedDict):
    """Contains `date` and `value`."""

    date: date
    value: Decimal


def get_dividends_received(asset_id: int) -> list[dict[str, Any]]:
    """Get the dividends received for asset. Returns a list of dictionaries
    containing `date` and `amount_received`."""

    market_divs = dividends.get_dividends(asset_id)
    t = transactions.get_adjusted_transactions(asset_id)

    divs_received = []
    if t:
        for div in market_divs:
            a = get_asset(asset_id)
            if not a["still_open"]:
                last_date = max([transaction["date"] for transaction in t])
                if div["date"] >= last_date:
                    continue

            # Find how many shares on that dividend date
            shares = 0
            div_received = False
            for transaction in t:
                if transaction["date"] <= div["date"]:
                    div_received = True
                    shares += transaction["shares"]

            if div_received:
                value = shares * div["dividend_value"]
                divs_received.append({"date": div["date"], "amount_received": value})

    return divs_received
