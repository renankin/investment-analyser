from app.models.models import AssetPosition
from app.repositories.assets import (
    delete_asset,
    edit_asset,
    get_all_assets,
    get_asset_by_id,
    insert_asset,
)
from app.services.transaction_service import TransactionService


class AssetService:
    def __init__(self, asset_id: int) -> None:
        self.asset = get_asset_by_id(asset_id)

    @classmethod
    def add_new_asset(
        cls,
        account_id: int,
        asset_symbol: str,
        asset_name: str,
        asset_type: str,
        still_open: bool,
    ) -> None:
        insert_asset(account_id, asset_symbol, asset_name, asset_type, still_open)

    def delete_asset(self) -> bool:
        if TransactionService(self.asset.id).transactions_from_asset:
            return False
        delete_asset(self.asset.id)
        return True

    def edit_asset(self, new_asset: AssetPosition) -> None:
        edit_asset(new_asset)

    @classmethod
    def get_all_assets(cls) -> list[AssetPosition]:
        return get_all_assets()