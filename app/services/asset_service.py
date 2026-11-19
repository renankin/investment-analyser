from app.models import models
from app.ports.repository import AssetRepository


class AssetService:
    def __init__(self, repository: AssetRepository) -> None:
        self._repository = repository

    def add_asset(self, asset: models.AssetPosition) -> None:
        self._repository.add_asset(asset)

    def delete_asset(self, asset: models.AssetPosition) -> None:
        self._repository.delete_asset(asset)

    def edit_asset(self, new_asset: models.AssetPosition) -> None:
        self._repository.edit_asset(new_asset)

    def get_open_assets(self) -> list[models.AssetPosition]:
        return self._repository.get_open_assets()

    def get_assets_from_account(self, account_id: int) -> list[models.AssetPosition]:
        return self._repository.get_assets_from_account(account_id)
