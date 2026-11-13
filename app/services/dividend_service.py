
from app.models import models
from app.models.models import AdjustedTransaction, AssetPosition, DividendReceived
from app.ports.repository import MarketDividendRepository


class DividendService:
    def __init__(self, repository: MarketDividendRepository) -> None:
        self._repository = repository

    def add_market_dividends(self, market_divs: list[models.MarketDividend]) -> None:
        self._repository.add_dividends(market_divs)

    def calculate_dividends_received(
        self, asset: AssetPosition, adj_transactions: list[AdjustedTransaction]
    ) -> list[DividendReceived]:

        divs_received = []
        market_divs = self._repository.get_dividends_for_asset(asset.id)
        for div in market_divs:
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
                if transaction.transaction_record.date < div.date:
                    div_received = True
                    shares += transaction.shares

            if div_received:
                divs_received.append(
                    DividendReceived(
                        asset=asset,
                        date=div.date,
                        received_value=shares * div.dividend_per_share,
                        currency=div.currency,
                    )
                )

        return sorted(divs_received, key=lambda div: div.date)
