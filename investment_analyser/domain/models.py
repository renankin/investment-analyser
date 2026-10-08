from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class Asset: ...


@dataclass
class Transaction:
    id: int
    asset_id: int
    date: date
    type: str
    price: Decimal

@dataclass
class Account: ...

@dataclass
class Dividend: ...