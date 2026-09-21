from typing import Any

from investment_analyser.db import fetch_multiple_records


def get_transactions_for_open_assets() -> list[dict[str, Any]]:
    """Returns a list of dicts with keys `asset_id`, `asset_name`, `asset_type`,
    `date`, `shares`, `price` and `currency`"""

    query = (
        "SELECT transactions.shares, transactions.price, transactions.date,"
        " assets.asset_id, assets.asset_name, assets.asset_type, assets.asset_symbol,"
        " accounts.currency"
        " FROM transactions"
        " JOIN assets on transactions.asset_id = assets.asset_id"
        " JOIN accounts on assets.account_id = accounts.account_id"
        " WHERE assets.still_open = 1"
    )

    return [dict(row) for row in fetch_multiple_records(query)]
