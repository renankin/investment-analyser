import datetime as dt
from decimal import Decimal

import pandas as pd
from scipy import optimize

from app.models import models
from app.services.account_service import AccountService
from app.services.asset_service import AssetService
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
        account_service: AccountService,
        asset_service: AssetService,
        transaction_service: TransactionService,
        dividend_service: DividendService,
        price_service: PriceService,
    ) -> None:
        self._account_service = account_service
        self._asset_service = asset_service
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

    def calculate_asset_value(self, asset: models.AssetPosition) -> Decimal:
        if asset.still_open:
            shares = self._transaction_service.get_shares_balance(asset.id)
            current_price = self._price_service.get_most_recent_price(asset.id)
            return shares * current_price.value
        return Decimal(0)

    def calculate_portfolio_value(self) -> Decimal:
        open_assets = self._asset_service.get_open_assets()
        portfolio_value = Decimal(0)
        for asset in open_assets:
            portfolio_value += self.calculate_asset_value(asset)
        return portfolio_value

    def calculate_asset_allocation(self, asset: models.AssetPosition) -> Decimal:
        portfolio_value = self.calculate_portfolio_value()
        asset_value = self.calculate_asset_value(asset)
        return asset_value / portfolio_value

    def calculate_asset_value_history(self, asset_id: int) -> pd.Series:
        # Get the cummulative sum of shares
        transactions = self._transaction_service.get_adjusted_transactions(asset_id)
        df1 = (
            pd.DataFrame(
                [
                    {"date": item.transaction_record.date, "shares": item.shares}
                    for item in transactions
                ]
            )
            .set_index("date")
            .sort_values("date")
        )

        # Combine transactions which are ocurring in the same date
        df1 = df1.groupby("date").sum()
        df1["shares_cumsum"] = df1["shares"].cumsum()

        # Get the prices for that asset
        market_prices = self._price_service.get_prices_for_asset(asset_id)
        df2 = (
            pd.DataFrame(
                [
                    {"unit_price": price.value, "date": price.date}
                    for price in market_prices
                ]
            )
            .set_index("date")
            .sort_values("date")
        )

        # Select dates which start from initial transaction
        df2 = df2[df2.index >= df1.first_valid_index()]

        # Include cumsum on the column of df2
        df2 = df2.merge(df1, left_index=True, right_index=True, how="left")

        # Replace NaN values
        df2.ffill(inplace=True)

        # calculate valuation
        df2["asset_history"] = df2["unit_price"] * df2["shares_cumsum"]

        return df2["asset_history"]

    def calculate_account_value_history(self, account_id: int) -> pd.Series:
        all_assets = self._asset_service.get_assets_from_account(account_id)
        df = pd.DataFrame()
        for asset in all_assets:
            ser = self.calculate_asset_value_history(asset.id)
            df = pd.concat([df, ser], axis=1).sort_index()
        return df.sum(axis=1)

    def calculate_portfolio_value_history(self) -> pd.Series:
        all_accounts = self._account_service.get_all_accounts()
        df = pd.DataFrame()
        for account in all_accounts:
            ser = self.calculate_account_value_history(account.id)
            df = pd.concat([df, ser], axis=1).sort_index()
        return df.sum(axis=1)
