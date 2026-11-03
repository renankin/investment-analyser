from datetime import date
from decimal import Decimal

from pytest import fixture

from app import create_app
from app.db.connection import get_db
from app.models import models
from app.services.transaction_service import TransactionService


@fixture
def test_app():
    app = create_app()
    app.config["DATABASE"] = ":memory:"
    return app


@fixture
def init_db(test_app):
    with test_app.app_context():
        conn = get_db()
        with test_app.open_resource("db/schema.sql", mode="r") as f:
            conn.executescript(f.read())
        conn.commit()
        yield
        conn.close()


def test_transaction_can_be_added(init_db):

    transaction = models.TransactionRecord(
        id=1,
        asset_id=1,
        date=date(year=2023, month=12, day=1),
        shares=Decimal("100.00"),
        price=Decimal("10.00"),
    )

    TransactionService.add_transaction(transaction)

    assert TransactionService(transaction_id=1).transaction == transaction
