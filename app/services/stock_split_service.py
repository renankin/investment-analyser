from app.models.models import StockSplit
from app.ports.repository import StockSplitRepository


class StockSplitService:
    def __init__(self, repository: StockSplitRepository) -> None:
        self._repository = repository

    def add_stock_splits(self, stock_splits: list[StockSplit]) -> None:
        self._repository.add_stock_splits(stock_splits)
