from typing import Any

from investment_analyser.db import (
    execute_db,
    fetch_multiple_records,
    fetch_single_record,
)
from investment_analyser.models.models import Account, AssetInfo, AssetPosition, EtfInfo

ALL_ASSETS_QUERY = (
    "SELECT assets.account_id, assets.asset_id, assets.asset_symbol, assets.asset_name,"
    " assets.asset_type, assets.still_open, accounts.account_name, accounts.currency"
    " FROM assets"
    " JOIN accounts ON assets.account_id = accounts.account_id"
)


def delete_asset(asset_id: int) -> None:
    """Delete asset."""

    execute_db("DELETE FROM assets WHERE asset_id = ?", (asset_id,))


def get_all_assets() -> list[AssetPosition]:

    return [
        AssetPosition(
            id=row["asset_id"],
            info=AssetInfo(
                symbol=row["asset_symbol"],
                name=row["asset_name"],
                type=row["asset_type"],
            ),
            still_open=row["still_open"],
            account=Account(
                id=row["account_id"], name=row["account_name"], currency=row["currency"]
            ),
        )
        for row in fetch_multiple_records(ALL_ASSETS_QUERY)
    ]


def get_asset_by_id(asset_id: int) -> AssetPosition:

    record = fetch_single_record(
        ALL_ASSETS_QUERY + " WHERE assets.asset_id = ?",
        (asset_id,),
    )

    return AssetPosition(
        id=record["asset_id"],
        info=AssetInfo(
            symbol=record["asset_symbol"],
            name=record["asset_name"],
            type=record["asset_type"],
        ),
        still_open=record["still_open"],
        account=Account(
            id=record["account_id"],
            name=record["account_name"],
            currency=record["currency"],
        ),
    )


def get_asset_by_symbol(symbol: str) -> AssetPosition:

    record = fetch_single_record(
        ALL_ASSETS_QUERY + " WHERE assets.asset_symbol = ?",
        (symbol,),
    )

    return AssetPosition(
        id=record["asset_id"],
        info=AssetInfo(
            symbol=record["asset_symbol"],
            name=record["asset_name"],
            type=record["asset_type"],
        ),
        still_open=record["still_open"],
        account=Account(
            id=record["account_id"],
            name=record["account_name"],
            currency=record["currency"],
        ),
    )


def get_assets_from_account(account_id: int) -> list[AssetPosition]:

    return [
        AssetPosition(
            id=row["asset_id"],
            info=AssetInfo(
                symbol=row["asset_symbol"],
                name=row["asset_name"],
                type=row["asset_type"],
            ),
            still_open=row["still_open"],
            account=Account(
                id=row["account_id"], name=row["account_name"], currency=row["currency"]
            ),
        )
        for row in fetch_multiple_records(
            ALL_ASSETS_QUERY + " WHERE accounts.account_id = ?", (account_id,)
        )
    ]


def get_etf_data(asset_id: int) -> EtfInfo:

    record = fetch_single_record(
        "SELECT etf_metadata.benchmark_index, etf_metadata.expense_ratio, etf_metadata.fund_size,"
        " etf_metadata.underlying_etf_symbol, assets.asset_name, assets.asset_symbol,"
        " assets.asset_type"
        " FROM etf_metadata"
        " JOIN assets ON assets.asset_id = etf_metadata.asset_id"
        " WHERE etf_metadata.asset_id = ?",
        (asset_id,),
    )

    return EtfInfo(
        asset_info=AssetInfo(
            symbol=record["asset_symbol"],
            name=record["asset_name"],
            type=record["asset_type"],
        ),
        benchmark_index=record["benchmark_index"],
        expense_ratio=record["expense_ratio"],
        fund_size=record["fund_size"],
        underlying_etf_symbol=record["underlying_etf_symbol"],
    )


def insert_asset(
    account_id: int,
    asset_symbol: str,
    asset_name: str,
    asset_type: str,
    still_open: bool,
) -> None:

    query = (
        "INSERT INTO assets"
        " (account_id, asset_symbol, asset_name, asset_type, still_open)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    )

    execute_db(
        query,
        (account_id, asset_symbol, asset_name, asset_type, still_open),
    )


def edit_asset(asset_pos: AssetPosition) -> None:

    query = (
        "UPDATE assets"
        " SET asset_symbol = ?, asset_name = ?, asset_type = ?, still_open = ?"
        " WHERE asset_id = ?"
    )

    execute_db(
        query,
        (
            asset_pos.info.symbol,
            asset_pos.info.name,
            asset_pos.info.type,
            asset_pos.still_open,
            asset_pos.id,
        ),
    )
