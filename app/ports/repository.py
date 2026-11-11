from abc import ABC, abstractmethod

from app.models import models


class AccountRepository(ABC):
    @abstractmethod
    def add_new_account(self, account: models.Account) -> None: ...

    @abstractmethod
    def delete_account(self, account: models.Account) -> None: ...

    @abstractmethod
    def edit_account(self, new_account: models.Account) -> None: ...

    @abstractmethod
    def get_account_by_id(self, account_id: int) -> models.Account: ...


class AssetRepository(ABC):
    @abstractmethod
    def add_asset(self, asset: models.AssetPosition) -> None: ...

    @abstractmethod
    def delete_asset(self, asset: models.AssetPosition) -> None: ...

    @abstractmethod
    def edit_asset(self, new_asset: models.AssetPosition) -> None: ...

    @abstractmethod
    def get_asset_by_id(self, asset_id: int) -> models.AssetPosition: ...


class MarketPriceRepository(ABC):
    @abstractmethod
    def add_prices(self, prices: list[models.MarketPrice]) -> None: ...

    @abstractmethod
    def get_prices_for_asset(self, asset_id: int) -> list[models.MarketPrice]: ...


class StockSplitRepository(ABC):
    @abstractmethod
    def add_stock_split(self, stock_split: models.StockSplit): ...

    @abstractmethod
    def get_stock_splits_for_asset(self, asset_id: int) -> list[models.StockSplit]: ...


class TransactionRepository(ABC):
    @abstractmethod
    def add_transaction(self, transaction: models.TransactionRecord) -> None: ...

    @abstractmethod
    def delete_transaction(self, transaction: models.TransactionRecord) -> None: ...

    @abstractmethod
    def edit_transaction(self, new_transaction: models.TransactionRecord) -> None: ...

    @abstractmethod
    def get_transaction_by_id(
        self, transaction_id: int
    ) -> models.TransactionRecord: ...

    @abstractmethod
    def get_transactions_for_asset(
        self, asset_id: int
    ) -> list[models.TransactionRecord]: ...
