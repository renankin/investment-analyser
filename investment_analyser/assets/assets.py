from investment_analyser.db import execute_db, query_db
from investment_analyser.market_data.repository import dividends
from investment_analyser.transactions import transactions


def delete_asset(asset_id: int):
    """Delete asset."""

    execute_db("DELETE FROM assets WHERE asset_id = ?", (asset_id,))


def get_all_assets() -> list:
    """Returns a list of dictionaries containing
    `asset_id`, `asset_symbol`, `asset_name`, `account_name`, `benchmark_index, `total_assets`
    `asset_type`, `still_open`, `currency`."""

    query = (
        "SELECT assets.asset_id, assets.asset_symbol, assets.asset_name, assets.asset_type,"
        " assets.still_open, assets.benchmark_index, assets.total_assets, assets.expense_ratio,"
        " accounts.account_name, accounts.currency"
        " FROM assets"
        " JOIN accounts ON assets.account_id = accounts.account_id"
    )

    return query_db(query)


def get_asset(asset_id: int | None = None, asset_symbol: str | None = None) -> dict:
    """Returns a dictionary containing `account_id`, `asset_id`, `asset_symbol`, `asset_name`,
    `asset_type`, `still_open`, `benchmark_index`, `expense_ratio` and `total_assets`."""

    query = (
        "SELECT account_id, asset_id, asset_symbol, asset_name, asset_type, still_open,"
        " benchmark_index, expense_ratio, total_assets"
        " FROM assets"
    )

    if asset_id:
        query += " WHERE asset_id = ?"
        param = asset_id

    if asset_symbol:
        query += " WHERE asset_symbol = ?"
        param = asset_symbol

    return query_db(query, (param,), one=True)


def get_dividends_received(asset_id: int) -> list[dict]:
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


def get_etf_data(asset_id: int) -> dict:
    """Get the data from the ETF for an asset and return as a dictionary with keys 
    `benchmark_index`, `expense_ratio`, `fund_size` and `underlying_etf_symbol`"""

    query = (
        "SELECT benchmark_index, expense_ratio, fund_size, underlying_etf_symbol"
        " FROM etf_metadata"
        " WHERE asset_id = ?"
    )

    return query_db(query, (asset_id,), one=True)


def insert_asset(
    account_id: int,
    asset_symbol: str,
    asset_name: str,
    benchmark_index: str,
    expense_ratio: float,
    total_assets: float,
    asset_type: str,
    still_open: int,
):
    """Insert into assets table."""

    query = (
        "INSERT INTO assets"
        " (account_id, asset_symbol, asset_name, asset_type, still_open,"
        " benchmark_index, expense_ratio, total_assets )"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    )

    execute_db(
        query,
        (
            account_id,
            asset_symbol,
            asset_name,
            asset_type,
            still_open,
            benchmark_index,
            expense_ratio,
            total_assets,
        ),
    )


def edit_asset(
    asset_id: int,
    asset_symbol: str,
    asset_name: str,
    benchmark_index: str,
    expense_ratio: float,
    total_assets: float,
    asset_type: str,
    still_open: int,
):
    """Update asset."""

    query = (
        "UPDATE assets"
        " SET asset_symbol = ?, asset_name = ?, asset_type = ?, still_open = ?,"
        " benchmark_index = ?, expense_ratio = ?, total_assets = ?"
        " WHERE asset_id = ?"
    )

    execute_db(
        query,
        (
            asset_symbol,
            asset_name,
            asset_type,
            still_open,
            benchmark_index,
            expense_ratio,
            total_assets,
            asset_id,
        ),
    )
