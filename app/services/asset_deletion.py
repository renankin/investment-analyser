from typing import Literal

from app.repository.assets import delete_asset
from app.repository.dividends import get_dividends
from app.repository.prices import get_market_prices
from app.repository.stock_splits import get_stock_splits
from app.repository.transactions import get_transactions_from_asset

DeletionBlocker = Literal["transactions", "prices", "dividends", "splits"]


def delete_asset_if_unused(asset_id: int) -> DeletionBlocker | None:
    """Delete an asset when it has no associated transactions or market data."""

    if get_transactions_from_asset(asset_id):
        return "transactions"

    if get_market_prices(asset_id):
        return "prices"

    if get_dividends(asset_id):
        return "dividends"

    if get_stock_splits(asset_id):
        return "splits"

    delete_asset(asset_id)
    return None
