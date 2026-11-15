import pytest

from app.models import models
from app.ports import repository
from app.services.dividend_service import DividendService
from app.services.price_service import PriceService
from app.services.stock_split_service import StockSplitService
from app.services.transaction_service import TransactionService


class FakeMarketDividendRepository(repository.MarketDividendRepository):
    def __init__(self) -> None:
        self.dividends: list[models.MarketDividend] = []

    def add_dividends(self, dividends: list[models.MarketDividend]) -> None:
        [self.dividends.append(dividend) for dividend in dividends]

    def get_dividends_for_asset(self, asset_id: int) -> list[models.MarketDividend]:
        return [
            dividend for dividend in self.dividends if dividend.asset_id == asset_id
        ]


class FakeTransactionRepository(repository.TransactionRepository):
    def __init__(self):
        self.transactions: list[models.TransactionRecord] = []

    def add_transaction(self, transaction: models.TransactionRecord) -> None:
        self.transactions.append(transaction)

    def delete_transaction(self, transaction: models.TransactionRecord) -> None:
        self.transactions.remove(transaction)

    def edit_transaction(self, new_transaction: models.TransactionRecord) -> None:
        [
            new_transaction
            for transaction in self.transactions
            if transaction == self.get_transaction_by_id(new_transaction.id)
        ]

    def get_transaction_by_id(self, transaction_id: int) -> models.TransactionRecord:
        return next(
            transaction
            for transaction in self.transactions
            if transaction.id == transaction_id
        )

    def get_transactions_for_asset(
        self, asset_id: int
    ) -> list[models.TransactionRecord]:
        return [
            transaction
            for transaction in self.transactions
            if transaction.asset_id == asset_id
        ]


class FakeStockSplitRepository(repository.StockSplitRepository):
    def __init__(self):
        self.stock_splits: list[models.StockSplit] = []

    def add_stock_splits(self, stock_splits: list[models.StockSplit]) -> None:
        [self.stock_splits.append(stock) for stock in stock_splits]

    def get_stock_splits_for_asset(self, asset_id: int) -> list[models.StockSplit]:
        return [
            stock_split
            for stock_split in self.stock_splits
            if stock_split.asset_id == asset_id
        ]


class FakeMarketRepository(repository.MarketPriceRepository):
    def __init__(self):
        self.prices: list[models.MarketPrice] = []

    def add_prices(self, prices: list[models.MarketPrice]) -> None:
        [self.prices.append(price) for price in prices]

    def get_prices_for_asset(self, asset_id: int) -> list[models.MarketPrice]:
        return [price for price in self.prices if price.asset_id == asset_id]


@pytest.fixture
def fake_dividend_repository():
    return FakeMarketDividendRepository()


@pytest.fixture
def dividend_service(fake_dividend_repository):
    return DividendService(fake_dividend_repository)


@pytest.fixture
def fake_transaction_repository():
    return FakeTransactionRepository()


@pytest.fixture
def fake_stock_split_repository():
    return FakeStockSplitRepository()


@pytest.fixture
def transaction_service(fake_transaction_repository, fake_stock_split_repository):
    return TransactionService(fake_transaction_repository, fake_stock_split_repository)


@pytest.fixture
def stock_split_service(fake_stock_split_repository):
    return StockSplitService(fake_stock_split_repository)


@pytest.fixture
def fake_price_repository():
    return FakeMarketRepository()


@pytest.fixture
def price_service(fake_price_repository):
    return PriceService(fake_price_repository)
