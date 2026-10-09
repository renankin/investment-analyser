from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class Account:
    id: int
    name: str
    currency: str


@dataclass(frozen=True)
class Asset:
    id: int
    symbol: str
    name: str
    type: str
    account_id: int
    still_open: bool


@dataclass(frozen=True)
class MarketDividend:
    date: date
    asset_id: int
    value: Decimal


@dataclass(frozen=True)
class MarketPrice:
    date: date
    asset_id: int
    value: Decimal


@dataclass(frozen=True)
class StockSplit:
    date: date
    asset_id: int
    split_ratio: float


@dataclass(frozen=True)
class Transaction:
    id: int
    account_id: int
    asset_id: int
    date: date
    type: str
    price: Decimal
