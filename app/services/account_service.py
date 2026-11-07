from app.models import models
from app.ports import repository


class AccountService:
    def __init__(self, repository: repository.AccountRepository) -> None:
        self._repository = repository

    def add_account(self, account: models.Account) -> None:
        self._repository.add_new_account(account)

    def delete_account(self, account: models.Account) -> None:
        self._repository.delete_account(account)

    def edit_account(self, new_account: models.Account) -> None:
        self._repository.edit_account(new_account)
