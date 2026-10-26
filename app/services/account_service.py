from app.repositories.accounts import delete_account, get_account
from app.repositories.assets import get_assets_from_account


class AccountService:
    def __init__(self, account_id: int) -> None:
        self.account = get_account(account_id)
        self.assets = get_assets_from_account(account_id)

    def add_new_account(self) -> None:
        pass

    def delete_account(self) -> bool:
        if self.assets:
            return False
        delete_account(self.account.id)
        return True

    def edit_account(self) -> None:
        pass
