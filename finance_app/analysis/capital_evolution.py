import pandas as pd

from finance_app.accounts import accounts
from finance_app.transactions import transactions
from finance_app.market import prices


def get_all_accounts_history() -> pd.Series:
    """Returns Series"""

    all_accounts = accounts.get_all_accounts()

    df = pd.DataFrame()

    for account in all_accounts:
        ser = get_account_history(account["account_id"])

        df = pd.concat([df, ser], axis=1).sort_index()

    return df.sum(axis=1)


def get_account_history(account_id: int) -> pd.Series:
    """Returns a Series with `values` for the account history."""

    all_assets = accounts.get_assets(account_id)

    df = pd.DataFrame()

    for asset in all_assets:
        ser = get_asset_history(asset["asset_id"])

        df = pd.concat([df, ser], axis=1).sort_index()

    return df.sum(axis=1)


def get_asset_history(asset_id: int) -> pd.Series:
    """Returns a Series with `values` for the asset history."""

    # Get the cummulative sum of shares
    t = transactions.get_adjusted_transactions(asset_id)
    df1 = pd.DataFrame(t)[["date", "shares"]]

    # Combine transactions which are ocurring in the same date
    df1 = df1.groupby("date").sum()
    df1["shares_cumsum"] = df1["shares"].cumsum()

    # Get the prices for that asset
    p = prices.get_prices(asset_id)
    if not p:
        return pd.Series()

    df2 = pd.DataFrame(p).set_index("date")

    # Select dates which start from initial transaction
    df2 = df2[df2.index >= df1.first_valid_index()]

    # Include cumsum on the column of df2
    df2 = df2.merge(df1, on="date", how="left")

    # Replace NaN values
    df2.ffill(inplace=True)

    # calculate valuation
    df2["asset_history"] = df2["unit_price"] * df2["shares_cumsum"]

    return df2["asset_history"]
