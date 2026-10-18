from investment_analyser.repository.assets import get_asset_by_id
from investment_analyser.repository import dividends
from investment_analyser.models.models import Account, DividendReceived
from investment_analyser.repository.transactions import get_transactions_from_asset
from investment_analyser.transactions.service import get_split_adjusted_transactions


def get_dividends_received(asset_id: int) -> list[DividendReceived]:

    market_divs = dividends.get_dividends(asset_id)
    t = get_split_adjusted_transactions(
        transactions=get_transactions_from_asset(asset_id)
    )

    divs_received = []
    if t:
        for div in market_divs:
            asset = get_asset_by_id(asset_id)
            if not asset.still_open:
                last_date = max(
                    [transaction.transaction_record.date for transaction in t]
                )
                if div.date >= last_date:
                    continue

            # Find how many shares on that dividend date
            shares = 0
            div_received = False
            for transaction in t:
                if transaction.transaction_record.date <= div.date:
                    div_received = True
                    shares += transaction.shares

            if div_received:
                divs_received.append(
                    DividendReceived(
                        date=div.date,
                        value=shares * div.value,
                        account=Account(
                            id=asset.account.id,
                            name=asset.account.name,
                            currency=asset.account.currency,
                        ),
                    )
                )

    return divs_received
