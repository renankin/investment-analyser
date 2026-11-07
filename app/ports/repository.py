from abc import ABC, abstractmethod

from app.models import models


class AccountRepository(ABC):
    @abstractmethod
    def add_new_account(self, account: models.Account): ...

    @abstractmethod
    def delete_account(self, account: models.Account): ...

    @abstractmethod
    def edit_account(self, new_account: models.Account): ...

    @abstractmethod
    def get_account_by_id(self, account_id: int) -> models.Account: ...


class AssetRepository(ABC):
    @abstractmethod
    def add_new_asset(self, asset: models.AssetPosition): ...

    @abstractmethod
    def get_asset_by_id(self, asset_id: int) -> models.AssetPosition: ...


class TransactionRepository(ABC):
    @abstractmethod
    def add_new_transaction(self, transaction: models.TransactionRecord) -> None: ...

    @abstractmethod
    def get_transaction_by_id(
        self, transaction_id: int
    ) -> models.TransactionRecord: ...
