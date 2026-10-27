from app.models.models import Account
from app.repositories.accounts import (
    create_account,
    delete_account,
    get_account,
    get_all_accounts,
    update_account,
)
from app.repositories.assets import get_assets_from_account


class AccountService:
    def __init__(self, account_id: int) -> None:
        self.account = get_account(account_id)
        self.assets = get_assets_from_account(account_id)

    @classmethod
    def add_new_account(cls, account_name: str, currency: str) -> None:
        create_account(account_name, currency)

    @classmethod
    def get_all_accounts(cls) -> list[Account]:
        return get_all_accounts()

    def delete_account(self) -> bool:
        if self.assets:
            return False
        delete_account(self.account.id)
        return True

    def edit_account(self, new_name: str | None, new_currency: str | None) -> None:
        if new_name:
            self.account.name = new_name
        if new_currency:
            self.account.currency = new_currency
        update_account(self.account)
