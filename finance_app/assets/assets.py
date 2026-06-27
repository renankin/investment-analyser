from finance_app.db import execute_db, query_db

from finance_app.market import market
from finance_app.transactions import transactions


def delete_asset(asset_id: int):
    """Delete asset."""

    execute_db("DELETE FROM assets WHERE asset_id = ?", (asset_id,))


def get_all_assets() -> list:
    """Fetch assets from all accounts and returns a list of dictionaries containing
    `asset_id`, `asset_name`, `account_name`, `currency`, `source_display_name` and `still_open`."""

    query = (
        "SELECT assets.asset_id, assets.asset_name, "
        " market_sources.display_name AS source_display_name,"
        " assets.still_open, accounts.account_name, accounts.currency"
        " FROM assets"
        " JOIN accounts ON assets.account_id = accounts.account_id"
        " JOIN market_sources ON assets.market_source_id = market_sources.source_id"
    )

    assets = query_db(query)

    if assets:
        return assets

    return []


def get_asset(asset_id: int) -> dict:
    """Returns a dictionary containing `account_id`, `asset_id`, `asset_name`,
     `market_source_id` and `still_open`."""

    query = (
        "SELECT account_id, asset_id, asset_name, market_source_id, still_open"
        " FROM assets"
        " WHERE asset_id = ?"
    )

    asset = query_db(query, (asset_id,), one=True)

    if asset:
        return asset

    return []


def get_dividends_received(asset_id: int) -> list[dict]:
    """Get the dividends received for asset. Returns a list of dictionaries
    containing `date` and `amount_received`."""

    market_divs = market.get_dividends(asset_id)
    t = transactions.get_adjusted_transactions(asset_id)

    divs_received = []
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
            divs_received.append(
                {"date": div["date"], "amount_received": value}
            )

    return divs_received


def insert_asset(
    account_id: int, asset_name: str, market_source_id: int, still_open: int
):
    """Insert into assets."""

    query = (
        "INSERT INTO assets (account_id, asset_name, market_source_id, still_open)"
        " VALUES (?, ?, ?, ?)"
    )

    execute_db(query, (account_id, asset_name, market_source_id, still_open))


def update_asset(
    asset_id: int,
    account_id: int,
    asset_name: str,
    market_source_id: int,
    still_open: bool,
):
    """Update asset."""

    query = (
        "UPDATE assets"
        " SET asset_name = ?, account_id = ?, market_source_id = ?, still_open = ?"
        " WHERE asset_id = ?"
    )

    execute_db(query, (asset_name, account_id, market_source_id, still_open, asset_id))
