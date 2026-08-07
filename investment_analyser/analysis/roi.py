import datetime as dt

from scipy import optimize

from investment_analyser.assets import assets
from investment_analyser.market import prices
from investment_analyser.transactions import transactions


def get_all_return() -> list[dict]:
    """Returns a list of dictionaries containing the return for all assets
    including `asset_name`, `currency`, `still_open`, `total_invested`,
    `total_sold`, `total_dividends`,`irr` and `net_return`"""

    all_assets = assets.get_all_assets()

    all_stats = []

    for asset in all_assets:
        divs = assets.get_dividends_received(asset["asset_id"])
        total_divs = sum(div["amount_received"] for div in divs)

        trans = transactions.get_adjusted_transactions(asset["asset_id"])
        total_invested = sum(t["price"] * t["shares"] for t in trans if t["shares"] > 0)
        total_sold = sum(t["price"] * -t["shares"] for t in trans if t["shares"] < 0)

        market_value = 0
        if asset["still_open"]:
            p = prices.get_most_recent_price(asset["asset_id"])
            if p:
                total_shares = sum(t["shares"] for t in trans)
                market_value = total_shares * p["price"]

        total_return = market_value + total_sold + total_divs
        if total_invested > 0 and total_return > 0:
            roi = (total_return - total_invested) / total_invested
        else:
            roi = None

        if total_invested > 0:

            stats = {
                "asset_name": asset["asset_name"],
                "still_open": asset["still_open"],
                "currency": asset["currency"],
                "total_invested": total_invested,
                "total_sold": total_sold,
                "market_value": market_value,
                "total_dividends": total_divs,
                "irr": get_irr(asset["asset_id"]),
                "roi": roi,
            }

            all_stats.append(stats)

    return all_stats


def get_irr(asset_id: int) -> float | None:
    """Returns the internal rate of return (IRR) for asset by computing transactions,
    dividends and current valuation if position is still open.
    If holding period is less than a year returns `None`."""

    t = transactions.get_adjusted_transactions(asset_id)

    if not t:
        return None

    cashflow = []
    dates = []
    total_shares = 0
    for transaction in t:
        cashflow.append(-1 * transaction["price"] * transaction["shares"])
        dates.append(transaction["date"])
        total_shares += transaction["shares"]

    dividends = assets.get_dividends_received(asset_id)
    if dividends:
        for div in dividends:
            cashflow.append(div["amount_received"])
            dates.append(div["date"])

    a = assets.get_asset(asset_id)
    if a["still_open"]:
        p = prices.get_most_recent_price(asset_id)
        if p:
            cashflow.append(p["price"] * total_shares)
            dates.append(p["date"])
        else:
            return None

    elapsed_years = [(date - min(dates)).days / 365 for date in dates]
    holding_period = (dt.datetime.now().date() - min(dates)).days
    if holding_period < 365:
        return None
    else:
        return compute_irr(cashflow, elapsed_years)


def compute_irr(
    transaction_values: list, elapsed_time: list, initial_guess=0
) -> float | None:
    """
    Returns the internal rate of return (IRR).
    `transaction_values` need to be negative for purchases and negative for sales.
    `elapsed_time` is the difference between first purchase and subsequent
    transactions in years.
    """

    # IRR is found when the sum of net present value equals 0
    solver = optimize.root(
        lambda irr: sum(transaction_values / (1 + irr) ** elapsed_time),
        x0=initial_guess,
    )

    if not solver.success:
        print(solver.message)
        return None

    return solver.x[0]
