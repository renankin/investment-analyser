import pytest

from app.models import models


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


def test_add_asset(asset, fake_asset_repository, asset_service):
    asset_service.add_asset(asset)
    assert asset in fake_asset_repository.assets


def test_delete_asset(asset, fake_asset_repository, asset_service):
    asset_service.add_asset(asset)
    asset_service.delete_asset(asset)
    assert asset not in fake_asset_repository.assets


def test_edit_asset(asset, fake_asset_repository, asset_service):
    asset_service.add_asset(asset)
    editted_asset = asset
    editted_asset.still_open = False
    asset_service.edit_asset(editted_asset)
    assert fake_asset_repository.get_asset_by_id(editted_asset.id).still_open == False
