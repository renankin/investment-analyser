from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum


class AssetType(StrEnum):
    STOCK = "Stock"
    BOND = "Bond"
    ETF = "ETF"


class TransactionType(StrEnum):
    SELL = "Sell"
    PURCHASE = "Purchase"
    DIVIDEND = "Dividend"


@dataclass
class Account:
    id: int
    name: str


@dataclass
class AssetInfo:
    symbol: str
    name: str
    type: str


@dataclass
class AssetPosition:
    id: int
    symbol: str
    name: str
    type: AssetType
    still_open: bool
    account: Account


@dataclass
class CashFlow:
    date: date
    value: Decimal


@dataclass(frozen=True)
class MarketDividend:
    date: date
    asset: AssetInfo
    value: Decimal
    currency: str


@dataclass
class DividendReceived:
    date: date
    value: Decimal
    account: Account


@dataclass(frozen=True)
class MarketPrice:
    asset_id: int
    date: date
    value: Decimal
    currency: str


@dataclass(frozen=True)
class StockSplit:
    date: date
    asset_id: int
    split_ratio: Decimal


@dataclass
class TransactionRecord:
    id: int
    asset_id: int
    date: date
    type: TransactionType
    shares: Decimal
    price: Decimal


@dataclass
class AdjustedTransaction:
    transaction_record: TransactionRecord
    is_adjusted: bool
    shares: Decimal
    price: Decimal


@dataclass
class EtfInfo:
    asset_info: AssetInfo
    benchmark_index: str
    expense_ratio: Decimal
    fund_size: Decimal
    underlying_etf_symbol: str
