from datetime import date
from decimal import Decimal

from app.models.models import AssetInfo, MarketPrice
from app.services.market_prices import PriceAnalyser

asset_info = AssetInfo(symbol="APPL", name="Apple", type="Stock")

prices = [
    MarketPrice(
        date=date(year=2025, month=12, day=1),
        asset=asset_info,
        value=Decimal("10.00"),
    ),
    MarketPrice(
        date=date(year=2024, month=12, day=1),
        asset=asset_info,
        value=Decimal("100.00"),
    ),
]


def test_matching_price_dates():

    price_analyser = PriceAnalyser(prices)
    initial_date = date(year=2024, month=12, day=1)
    final_date = date(year=2025, month=12, day=1)
    
    assert price_analyser.calculate_price_change(initial_date, final_date) == Decimal(
        "-0.90"
    )
