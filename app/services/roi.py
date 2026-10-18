from datetime import UTC, datetime
from decimal import Decimal

from scipy import optimize

from app.models.models import (
    AdjustedTransaction,
    CashFlow,
    DividendReceived,
    MarketPrice,
)
from app.repository import prices
from app.repository.assets import get_all_assets, get_asset_by_id
from app.repository.transactions import get_transactions_from_asset
from app.services.dividends import get_dividends_received
from app.services.transactions import get_split_adjusted_transactions


def get_all_return() -> list[dict]:
    """Returns a list of dictionaries containing the return for all assets
    including `asset_name`, `currency`, `still_open`, `total_invested`,
    `total_sold`, `total_dividends`,`irr` and `net_return`"""

    all_assets = get_all_assets()

    all_stats = []

    for asset in all_assets:
        divs = get_dividends_received(asset.id)
        total_divs = sum(div.value for div in divs)

        trans = get_split_adjusted_transactions(
            transactions=get_transactions_from_asset(asset.id)
        )
        total_invested = sum(t.price * t.shares for t in trans if t.shares > 0)
        total_sold = sum(t.price * -t.shares for t in trans if t.shares < 0)

        market_value = 0
        if asset.still_open:
            p = prices.get_most_recent_price(asset.id)
            if p:
                total_shares = sum(t.shares for t in trans)
                market_value = total_shares * p.value

        total_return = market_value + total_sold + total_divs
        if total_invested > 0 and total_return > 0:
            roi = (total_return - total_invested) / total_invested
        else:
            roi = None

        if total_invested > 0:
            stats = {
                "asset_name": asset.info.name,
                "still_open": asset.still_open,
                "currency": asset.account.currency,
                "total_invested": total_invested,
                "total_sold": total_sold,
                "market_value": market_value,
                "total_dividends": total_divs,
                "irr": get_irr(asset.id),
                "roi": roi,
            }

            all_stats.append(stats)

    return all_stats


def get_irr(asset_id: int) -> float | None:
    """Returns the internal rate of return (IRR) for asset by computing transactions,
    dividends and current valuation if position is still open.
    If holding period is less than a year returns `None`."""

    t = get_split_adjusted_transactions(
        transactions=get_transactions_from_asset(asset_id)
    )

    if not t:
        return None

    cashflow = []
    dates = []
    total_shares = 0
    for transaction in t:
        cashflow.append(-1 * transaction.price * transaction.shares)
        dates.append(transaction.transaction_record.date)
        total_shares += transaction.shares

    dividends = get_dividends_received(asset_id)
    if dividends:
        for div in dividends:
            cashflow.append(div.value)
            dates.append(div.date)

    asset = get_asset_by_id(asset_id)
    if asset.still_open:
        p = prices.get_most_recent_price(asset_id)
        if p:
            cashflow.append(p.value * total_shares)
            dates.append(p.date)
        else:
            return None

    elapsed_years = [(date - min(dates)).days / 365 for date in dates]
    holding_period = (datetime.now(tz=UTC).date() - min(dates)).days
    if holding_period < 365:
        return None
    else:
        return compute_irr(cashflow, elapsed_years)


def build_dividend_cashflows(dividends: list[DividendReceived]) -> list[CashFlow]:
    """
    Build cashflow with dividends.
    """

    cashflows: list[CashFlow] = []

    for dividend in dividends:
        cashflows.append(CashFlow(date=dividend.date, value=dividend.value))

    return cashflows


def build_transaction_cashflows(
    transactions: list[AdjustedTransaction],
) -> list[CashFlow]:
    """
    Builds cashflow with transactions.
    """

    cashflows: list[CashFlow] = []

    for transaction in transactions:
        cashflows.append(
            CashFlow(
                date=transaction.transaction_record.date,
                value=-1 * transaction.price * transaction.shares,
            )
        )

    return cashflows


def build_cashflows(
    transactions: list[AdjustedTransaction],
    dividends: list[DividendReceived],
    current_price: MarketPrice,
    open_shares: Decimal,
) -> list[CashFlow]:
    """
    Builds cashflows
    """

    transaction_cashflows: list[CashFlow] = build_transaction_cashflows(transactions)

    dividend_cashflows: list[CashFlow] = build_dividend_cashflows(dividends)

    price_cashflow = CashFlow(
        date=current_price.date, value=current_price.value * open_shares
    )

    return transaction_cashflows + dividend_cashflows + [price_cashflow]


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


def calculate_irr(cashflows: list[CashFlow], initial_guess=0.1) -> float | None:
    """
    Returns the internal rate of return (IRR) by taking a list of Cashflow.
    """

    if not cashflows:
        return None

    transaction_values = [float(cashflow.value) for cashflow in cashflows]
    dates = [cashflow.date for cashflow in cashflows]
    elapsed_time = [(date - min(dates)).days / 365 for date in dates]

    # IRR is found when the sum of net present value equals 0
    solver = optimize.root(
        lambda irr: sum(transaction_values / (1 + irr) ** elapsed_time),
        x0=initial_guess,
    )

    if not solver.success:
        print(solver.message)
        return None

    return float(solver.x[0])
