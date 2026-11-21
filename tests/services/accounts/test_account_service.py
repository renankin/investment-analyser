import pytest

from app.models import models


@pytest.fixture
def account():
    return models.Account(id=1, name="Test account")


def test_add_account(account, fake_account_repository, account_service):
    account_service.add_account(account)
    assert account in fake_account_repository.accounts


def test_delete_account(account, fake_account_repository, account_service):
    account_service.add_account(account)
    account_service.delete_account(account)
    assert account not in fake_account_repository.accounts


def test_account_name_is_editable(account, fake_account_repository, account_service):
    account_service.add_account(account)
    renamed_account = models.Account(id=1, name="New test account")
    account_service.edit_account(renamed_account)
    assert fake_account_repository.accounts[0].name == "New test account"
