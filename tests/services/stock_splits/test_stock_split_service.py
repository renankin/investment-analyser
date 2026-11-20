from datetime import date
from decimal import Decimal

import pytest

from app.models import models


@pytest.fixture
def stock_splits():
    return [
        models.StockSplit(
            date=date(2025, 1, 1), asset_id=1, split_ratio=Decimal("2.0")
        ),
        models.StockSplit(
            date=date(2026, 1, 1), asset_id=1, split_ratio=Decimal("5.0")
        ),
        models.StockSplit(
            date=date(2024, 1, 1), asset_id=1, split_ratio=Decimal("1.5")
        ),
    ]


def test_add_stock_split(
    stock_split_service, stock_splits, fake_stock_split_repository
):
    stock_split_service.add_stock_splits(stock_splits)
    assert stock_splits == fake_stock_split_repository.get_stock_splits_for_asset(
        asset_id=1
    )
