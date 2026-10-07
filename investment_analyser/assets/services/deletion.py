from typing import Literal

from investment_analyser.assets.repository import delete_asset
from investment_analyser.market_data.repository.dividends import get_dividends
from investment_analyser.market_data.repository.prices import get_prices
from investment_analyser.market_data.repository.stock_splits import get_stock_splits
from investment_analyser.transactions.repository import get_transactions

DeletionBlocker = Literal["transactions", "prices", "dividends", "splits"]


def delete_asset_if_unused(asset_id: int) -> DeletionBlocker | None:
    """Delete an asset when it has no associated transactions or market data."""

    if get_transactions(asset_id):
        return "transactions"

    if get_prices(asset_id):
        return "prices"

    if get_dividends(asset_id):
        return "dividends"

    if get_stock_splits(asset_id):
        return "splits"

    delete_asset(asset_id)
    return None
