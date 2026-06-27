from finance_app.db import execute_db, query_db
from finance_app.assets import assets

from finance_app.market.fetchers.fetcher_registry import FetcherProtocol


def get_all_sources() -> list:
    """Fetch market sources from database and return a list of dictionaries with
    keys containing `display_name`, `source_id`, `supports_prices`, `source_key`,
    `supports_dividends` and `support_stock_splits`."""

    query = (
        "SELECT source_id, display_name, source_key, supports_prices,"
        " supports_dividends, supports_stock_splits"
        " FROM market_sources"
    )

    sources = query_db(query)

    if sources:
        return sources

    return []


def get_assets_from_source(source_id: int) -> list:
    """Returns a list of dictionaries containing `asset_id` and `asset_name`."""

    query = "SELECT asset_id, asset_name FROM assets WHERE market_source_id = ?"

    assets = query_db(query, (source_id,))

    if assets:
        return assets

    return []


def get_source_by_id(source_id: int) -> dict:
    """Fetch source from database and returns a dictionary with `display_name`, `source_key`,
    `supports_prices`, `supports_dividends` and `supports_stock_splits`"""

    query = (
        "SELECT source_id, display_name, source_key, supports_prices,"
        " supports_dividends, supports_stock_splits"
        " FROM market_sources WHERE source_id = ?"
    )

    source = query_db(query, (source_id,), one=True)

    if source:
        return source

    return {}


def update_source(
    source_id: int,
    display_name: str,
    source_key: str,
    supports_prices: bool,
    supports_dividends: bool,
    supports_splits: bool,
) -> bool:
    """Edits source and returns `True` if successful."""

    statement = (
        "UPDATE market_sources SET display_name = ?, source_key = ?,"
        " supports_dividends = ?, supports_prices = ?, supports_stock_splits = ? "
        " WHERE source_id = ?"
    )

    if get_source_by_id(source_id):
        execute_db(
            statement,
            (
                display_name,
                source_key,
                supports_dividends,
                supports_prices,
                supports_splits,
                source_id,
            ),
        )

        return True

    return False


def insert_source(
    display_name: str,
    source_key: str,
    supports_prices: bool,
    supports_dividends: bool,
    supports_stock_splits: bool,
) -> bool:
    """Insert new market source in database and returns `True` if successful."""

    statement = (
        "INSERT INTO market_sources"
        " (display_name, source_key, supports_prices, supports_dividends, supports_stock_splits)"
        " VALUES (?, ?, ?, ?, ?)"
    )

    execute_db(
        statement,
        (
            display_name,
            source_key,
            supports_prices,
            supports_dividends,
            supports_stock_splits,
        ),
    )

    return True


def delete_source(source_id: int) -> bool:
    """Delete source by id and return True if successful."""

    if get_source_by_id(source_id):
        execute_db("DELETE FROM market_sources WHERE source_id = ?", (source_id,))
        return True

    return False


def get_prices(asset_id: int) -> list:
    """Get the prices for asset id and return them as list of dictionaries
    with `date`, `unit_price` and `currency` as keys."""

    query = (
        "SELECT prices.date, prices.unit_price, accounts.currency FROM prices"
        " JOIN accounts ON accounts.account_id = "
        " (SELECT account_id FROM assets WHERE asset_id = ?)"
        " WHERE prices.asset_id = ?"
        " ORDER BY prices.date"
    )

    prices = query_db(query, (asset_id, asset_id))

    if prices:
        return prices

    return []


def get_most_recent_price(asset_id: int) -> dict:
    """Returns the most recent price for asset and returns a dictionary
    containing `price` and `date` key."""

    p = get_prices(asset_id)

    if p:
        price_date = max([price["date"] for price in p])
        price_value = [
            price["unit_price"] for price in p if price["date"] == price_date
        ]

        return {"date": price_date, "price": price_value[0]}

    return {}


def delete_prices(asset_id: int) -> bool:
    """Deletes prices from database and returns True if successful."""

    prices = get_prices(asset_id)

    if prices:
        execute_db("DELETE FROM prices WHERE asset_id = ?", (asset_id,))
        return True

    return False


def insert_prices(asset_id: int) -> bool:
    """Insert prices for asset in database and returns True if successful."""

    asset = assets.get_asset(asset_id)

    market_source = get_source_by_id(asset["market_source_id"])

    fetcher = FetcherProtocol(market_source)

    prices = fetcher.fetch_prices(asset["asset_name"])

    if not prices.empty:
        args = []
        for date, price in prices.items():
            args.append((asset_id, date, price))

        execute_db(
            "INSERT INTO prices (asset_id, date, unit_price) VALUES (?, ?, ?)"
            " ON CONFLICT (date, asset_id) DO NOTHING",
            args,
        )

        return True

    return False


def get_stock_splits(asset_id: int) -> list:
    """Fetch splits from database and returns a list of dictionaries containing `date`
    and `split_ratio`."""

    query = (
        "SELECT date, split_ratio FROM stock_splits"
        " WHERE asset_id = ?"
        " ORDER BY date DESC"
    )

    splits = query_db(query, (asset_id,))

    if splits:
        return splits

    return []


def delete_stock_splits(asset_id: int) -> bool:
    """Deletes stock splits from database."""

    splits = get_stock_splits(asset_id)

    if splits:
        execute_db("DELETE FROM stock_splits WHERE asset_id = ?", (asset_id,))
        return True

    return False


def insert_stock_splits(asset_id: int) -> bool:
    """Insert stock splits in database and returns True if successful."""

    asset = assets.get_asset(asset_id)

    market_source = get_source_by_id(asset["market_source_id"])

    fetcher = FetcherProtocol(market_source)

    splits = fetcher.fetch_stock_splits(asset["asset_name"])

    if not splits.empty:
        args = []
        for date, split in splits.items():
            args.append((asset_id, date, split))

        execute_db(
            "INSERT INTO stock_splits (asset_id, date, split_ratio)"
            " VALUES (?, ?, ?)"
            " ON CONFLICT (date, asset_id) DO NOTHING",
            args,
        )

        return True

    return False


def get_dividends(asset_id: int) -> list:
    """Fetch dividends from database and return them as a list of dictionaries
    containing "date" and "dividend_value" keys."""

    query = (
        "SELECT * FROM dividends"
        " JOIN assets ON assets.asset_id = dividends.asset_id"
        " JOIN accounts ON accounts.account_id = assets.account_id"
        " WHERE dividends.asset_id = ?"
        " ORDER BY dividends.date DESC"
    )

    divs = query_db(query, (asset_id,))

    if divs:
        return divs

    return []


def delete_dividends(asset_id: int) -> bool:
    """Deletes dividends from database and returns True if successful"""

    dividends = get_dividends(asset_id)

    if dividends:
        execute_db("DELETE FROM dividends WHERE asset_id = ?", (asset_id,))
        return True

    return False


def insert_dividends(asset_id: int) -> bool:
    """Insert dividends for stock in database and returns True if successful."""

    asset = assets.get_asset(asset_id)

    market_source = get_source_by_id(asset["market_source_id"])

    fetcher = FetcherProtocol(market_source)

    dividends = fetcher.fetch_dividends(asset["asset_name"])

    if not dividends.empty:
        args = []
        for date, div in dividends.items():
            args.append((asset_id, date, div))

        execute_db(
            "INSERT INTO dividends (asset_id, date, dividend_value)"
            " VALUES (?, ?, ?)"
            " ON CONFLICT (date, asset_id) DO NOTHING",
            args,
        )

        return True

    return False
