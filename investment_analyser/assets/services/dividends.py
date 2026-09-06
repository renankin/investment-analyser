from datetime import date
from decimal import Decimal
from typing import TypedDict


class Dividend(TypedDict):
    """Contains `date` and `value`."""

    date: date
    value: Decimal
