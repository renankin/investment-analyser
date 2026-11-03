from datetime import date

from pytest import fixture

from app import create_app
from app.db.connection import get_db
from app.repositories.transactions import get_transactions_for_open_assets


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
        conn.execute(
            "INSERT INTO transactions (asset_id, date, shares, price)"
            " VALUES (1, '2024-01-31', 100, 200)"
        )
        conn.execute(
            "INSERT INTO transactions (asset_id, date, shares, price)"
            " VALUES (2, '2024-01-31', 100, 200)"
        )
        conn.commit()
        yield
        conn.close()


def test_transactions_for_open_assets(init_db):
    transactions = get_transactions_for_open_assets()
    assert [transaction.id for transaction in transactions] == []
    assert [transaction.asset_id for transaction in transactions] == []
    assert [transaction.date for transaction in transactions] == []
    assert [transaction.shares for transaction in transactions] == []
    assert [transaction.price for transaction in transactions] == []
