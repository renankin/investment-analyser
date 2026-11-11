import pytest

from app.models import models
from app.ports import repository
from app.services.asset_service import AssetService


class FakeAssetRepository(repository.AssetRepository):
    def __init__(self):
        self.assets: list[models.AssetPosition] = []

    def add_asset(self, asset: models.AssetPosition) -> None:
        self.assets.append(asset)

    def delete_asset(self, asset: models.AssetPosition):
        self.assets.remove(asset)

    def edit_asset(self, new_asset: models.AssetPosition):
        [
            new_asset
            for asset in self.assets
            if asset == self.get_asset_by_id(new_asset.id)
        ]

    def get_asset_by_id(self, asset_id: int) -> models.AssetPosition:
        return next(asset for asset in self.assets if asset.id == asset_id)


@pytest.fixture
def asset():
    return models.AssetPosition(
        id=1,
        name="Apple",
        symbol="APPL",
        still_open=True,
        type=models.AssetType.STOCK,
        account=models.Account(id=1, name="Test account"),
    )


@pytest.fixture
def fake_repository():
    return FakeAssetRepository()


@pytest.fixture
def asset_service(fake_repository):
    return AssetService(fake_repository)


def test_add_asset(asset, fake_repository, asset_service):
    asset_service.add_asset(asset)
    assert asset in fake_repository.assets


def test_delete_asset(asset, fake_repository, asset_service):
    asset_service.add_asset(asset)
    asset_service.delete_asset(asset)
    assert asset not in fake_repository.assets


def test_edit_asset(asset, fake_repository, asset_service):
    asset_service.add_asset(asset)
    editted_asset = asset
    editted_asset.still_open = False
    asset_service.edit_asset(editted_asset)
    assert fake_repository.get_asset_by_id(editted_asset.id).still_open == False
