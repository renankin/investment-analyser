from app.models import models
from app.ports.repository import MarketDividendRepository


def calculate_dividends_received(
    adjusted_transactions: list[models.AdjustedTransaction],
    market_dividends: list[models.MarketDividend],
    asset_open: bool = True,
) -> list[models.DividendReceived]:
    divs_received = []
    for div in market_dividends:
        if not asset_open:
            last_date = max(
                [
                    transaction.transaction_record.date
                    for transaction in adjusted_transactions
                ]
            )
            if div.date >= last_date:
                continue

        # Find how many shares on that dividend date
        shares = 0
        div_received = False
        for transaction in adjusted_transactions:
            if transaction.transaction_record.date < div.date:
                div_received = True
                shares += transaction.shares

        if div_received:
            divs_received.append(
                models.DividendReceived(
                    asset_id=div.asset_id,
                    date=div.date,
                    received_value=shares * div.dividend_per_share,
                    currency=div.currency,
                )
            )

    return sorted(divs_received, key=lambda div: div.date)


class DividendService:
    def __init__(self, repository: MarketDividendRepository) -> None:
        self._repository = repository

    def add_market_dividends(self, market_divs: list[models.MarketDividend]) -> None:
        self._repository.add_dividends(market_divs)

    def get_dividends_received(
        self, asset: models.AssetPosition, adj_transactions: list[models.AdjustedTransaction]
    ) -> list[models.DividendReceived]:

        return calculate_dividends_received(
            adjusted_transactions=adj_transactions,
            market_dividends=self._repository.get_dividends_for_asset(asset.id),
            asset_open=asset.still_open,
        )
