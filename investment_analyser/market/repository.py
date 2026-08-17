from investment_analyser.db import query_db


def get_most_recent_price(asset_id: int) -> float:
    """Returns the most recent price for asset."""

    query = (
        "SELECT unit_price FROM prices WHERE asset_id = ? ORDER BY date DESC LIMIT 1"
    )

    data = query_db(query, (asset_id,), one=True)

    return data["unit_price"]
