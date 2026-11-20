import pytest

from app.models import models
from app.ports import repository
from app.services.account_service import AccountService
from app.services.asset_service import AssetService
from app.services.dividend_service import DividendService
from app.services.price_service import PriceService
from app.services.stock_split_service import StockSplitService
from app.services.transaction_service import TransactionService


class FakeAccountRepository(repository.AccountRepository):
    def __init__(self):
        self.accounts: list[models.Account] = []

    def add_new_account(self, account: models.Account) -> None:
        self.accounts.append(account)

    def delete_account(self, account: models.Account):
        self.accounts.remove(account)

    def edit_account(self, new_account: models.Account):
        account = self.get_account_by_id(new_account.id)
        account.name = new_account.name

    def get_account_by_id(self, account_id: int) -> models.Account:
        return next(account for account in self.accounts if account.id == account_id)

    def get_all_accounts(self) -> list[models.Account]:
        return self.accounts


class FakeAssetRepository(repository.AssetRepository):
    def __init__(self) -> None:
        self.assets: list[models.AssetPosition] = []

    def add_asset(self, asset: models.AssetPosition) -> None:
        self.assets.append(asset)

    def delete_asset(self, asset: models.AssetPosition) -> None:
        self.assets.remove(asset)

    def edit_asset(self, new_asset: models.AssetPosition) -> None:
        asset_id = new_asset.id
        asset_to_replace = self.get_asset_by_id(asset_id)
        self.assets.remove(asset_to_replace)
        self.assets.append(new_asset)

    def get_asset_by_id(self, asset_id: int) -> models.AssetPosition:
        return next(asset for asset in self.assets if asset.id == asset_id)

    def get_all_assets(self) -> list[models.AssetPosition]:
        return self.assets

    def get_open_assets(self) -> list[models.AssetPosition]:
        return [asset for asset in self.assets if asset.still_open]

    def get_assets_from_account(self, account_id: int) -> list[models.AssetPosition]:
        return [asset for asset in self.assets if asset.account.id == account_id]


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
        transaction_id = new_transaction.id
        transaction_to_replace = self.get_transaction_by_id(transaction_id)
        self.transactions.remove(transaction_to_replace)
        self.transactions.append(new_transaction)

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
def fake_account_repository():
    return FakeAccountRepository()


@pytest.fixture
def account_service(fake_account_repository):
    return AccountService(fake_account_repository)


@pytest.fixture
def fake_asset_repository():
    return FakeAssetRepository()


@pytest.fixture
def asset_service(fake_asset_repository):
    return AssetService(fake_asset_repository)


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
