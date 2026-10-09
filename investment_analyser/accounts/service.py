from investment_analyser.accounts.repository import (
    delete_account,
    get_assets_from_account,
)


def delete_account_if_empty(account_id: int) -> bool:
    """Delete an account only when it has no assets."""

    if get_assets_from_account(account_id):
        return False

    delete_account(account_id)
    return True
