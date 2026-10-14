from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class Account:
    id: int
    name: str
    currency: str


@dataclass
class AssetInfo:
    symbol: str
    name: str
    type: str


@dataclass
class AssetPosition:
    id: int
    info: AssetInfo
    still_open: bool
    account: Account


@dataclass(frozen=True)
class MarketDividend:
    date: date
    asset: AssetInfo
    value: Decimal

@dataclass
class DividendReceived:
    date: date
    value: Decimal
    account: Account


@dataclass(frozen=True)
class MarketPrice:
    date: date
    asset: AssetInfo
    value: Decimal


@dataclass(frozen=True)
class StockSplit:
    date: date
    asset_id: int
    split_ratio: float


@dataclass
class TransactionRecord:
    id: int
    asset: AssetPosition
    date: date
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
