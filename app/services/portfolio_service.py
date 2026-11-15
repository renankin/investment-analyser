import datetime as dt

from scipy import optimize

from app.models import models
from app.services.dividend_service import DividendService
from app.services.price_service import PriceService
from app.services.transaction_service import TransactionService


def calculate_irr(cashflows: list[models.CashFlow], initial_guess=0.1) -> float | None:
    if not cashflows:
        return None

    transaction_values = [float(cashflow.value) for cashflow in cashflows]
    dates = [cashflow.date for cashflow in cashflows]
    elapsed_time = [(date - min(dates)).days / 365 for date in dates]

    holding_period = (dt.datetime.now(tz=dt.UTC).date() - min(dates)).days
    if holding_period < 365:
        return None

    # IRR is found when the sum of net present value equals 0
    solver = optimize.root(
        lambda irr: sum(transaction_values / (1 + irr) ** elapsed_time),
        x0=initial_guess,
    )

    if not solver.success:
        print(solver.message)
        return None

    return float(solver.x[0])


class PortfolioService:
    def __init__(
        self,
        transaction_service: TransactionService,
        dividend_service: DividendService,
        price_service: PriceService,
    ) -> None:
        self._transaction_service = transaction_service
        self._dividend_service = dividend_service
        self._price_service = price_service

    def _create_cashflows_from_transactions(
        self, asset: models.AssetPosition
    ) -> list[models.CashFlow]:
        cashflows = []
        transactions = self._transaction_service.get_adjusted_transactions(asset.id)
        for transaction in transactions:
            cashflows.append(
                models.CashFlow(
                    date=transaction.transaction_record.date,
                    value=-1 * transaction.price * transaction.shares,
                )
            )
        return cashflows

    def _create_cashflows_from_received_dividends(
        self, asset: models.AssetPosition
    ) -> list[models.CashFlow]:
        cashflows = []
        transactions = self._transaction_service.get_adjusted_transactions(asset.id)
        dividends = self._dividend_service.get_dividends_received(
            asset=asset, adj_transactions=transactions
        )
        for dividend in dividends:
            cashflows.append(
                models.CashFlow(date=dividend.date, value=dividend.received_value)
            )
        return cashflows

    def _create_cashflow_from_available_shares(
        self, asset: models.AssetPosition
    ) -> models.CashFlow:
        shares = self._transaction_service.get_shares_balance(asset.id)
        current_price = self._price_service.get_most_recent_price(asset.id)
        return models.CashFlow(
            date=current_price.date, value=current_price.value * shares
        )

    def _create_cashflows_for_asset(
        self, asset: models.AssetPosition
    ) -> list[models.CashFlow]:
        cashflows = []
        cashflows.extend(self._create_cashflows_from_transactions(asset))

        if asset.type == models.AssetType.STOCK:
            cashflows.extend(self._create_cashflows_from_received_dividends(asset))

        if asset.still_open:
            cashflows.append(self._create_cashflow_from_available_shares(asset))

        return cashflows

    def get_irr_for_asset(self, asset: models.AssetPosition) -> float | None:
        cashflows = self._create_cashflows_for_asset(asset)
        return calculate_irr(cashflows)
