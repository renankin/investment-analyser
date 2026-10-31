from decimal import Decimal

from pandas import Series, to_datetime

from app.fetchers.yfinance import YFetcher
from app.models.models import AdjustedTransaction, AssetPosition, DividendReceived
from app.repositories.dividends import delete_dividends, get_dividends, insert_dividend
from app.services.asset_service import AssetService
from app.services.transaction_service import TransactionService


class DividendService:
    def __init__(self, asset_id: int) -> None:
        self.asset_id = asset_id
        self.dividends = get_dividends(asset_id)

    @property
    def dividends_received(self) -> list[DividendReceived]:
        return self.get_dividends_received(
            asset=AssetService(self.asset_id).asset,
            adj_transactions=TransactionService.get_adjusted_transactions_from_asset(
                self.asset_id
            ),
        )

    @property
    def total_dividends(self) -> Decimal:
        total = Decimal("0.00")
        for dividend in self.dividends_received:
            total += dividend.value
        return total

    def get_dividends_received(
        self, asset: AssetPosition, adj_transactions: list[AdjustedTransaction]
    ) -> list[DividendReceived]:

        divs_received = []
        for div in self.dividends:
            if not asset.still_open:
                last_date = max(
                    [
                        transaction.transaction_record.date
                        for transaction in adj_transactions
                    ]
                )
                if div.date >= last_date:
                    continue

            # Find how many shares on that dividend date
            shares = 0
            div_received = False
            for transaction in adj_transactions:
                if transaction.transaction_record.date <= div.date:
                    div_received = True
                    shares += transaction.shares

            if div_received:
                divs_received.append(
                    DividendReceived(
                        date=div.date,
                        value=Decimal(shares) * div.value,
                        account=asset.account,
                    )
                )

        return divs_received

    @classmethod
    def delete_dividends(cls, asset: AssetPosition) -> None:
        delete_dividends(asset.id)

    @classmethod
    def update_dividends(cls, asset: AssetPosition) -> None:
        dividends = Series()
        if asset.info.type == "Stock":
            dividends = YFetcher(asset.info.symbol).get_dividends()

        if not dividends.empty:
            for date, div in dividends.items():
                insert_dividend(
                    asset_id=asset.id,
                    date=to_datetime(str(date)).date(),
                    dividend_value=div,
                )
