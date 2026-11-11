import pytest

from app.models import models
from app.ports import repository
from app.services.account_service import AccountService


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

@pytest.fixture
def account():
    return models.Account(id=1, name="Test account")

@pytest.fixture
def fake_repository():
    return FakeAccountRepository()

@pytest.fixture
def account_service(fake_repository):
    return AccountService(fake_repository)


def test_add_account(account, fake_repository, account_service):
    account_service.add_account(account)
    assert account in fake_repository.accounts

def test_delete_account(account, fake_repository, account_service):
    account_service.add_account(account)
    account_service.delete_account(account)
    assert account not in fake_repository.accounts

def test_account_name_is_editable(account, fake_repository, account_service):
    account_service.add_account(account)
    renamed_account = models.Account(id=1, name="New test account")
    account_service.edit_account(renamed_account)
    assert fake_repository.accounts[0].name == "New test account"


