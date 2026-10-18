from datetime import date

from pytest import fixture

from investment_analyser import create_app
from investment_analyser.db import get_db
from investment_analyser.repository.transactions import get_transactions_for_open_assets


@fixture
def test_app():
    app = create_app()
    app.config["DATABASE"] = ":memory:"
    return app


@fixture
def init_db(test_app):
    with test_app.app_context():
        conn = get_db()
        with test_app.open_resource("schema.sql", mode="r") as f:
            conn.executescript(f.read())
        conn.execute(
            "INSERT INTO accounts (account_name, currency) VALUES ('test_account', 'GBP')"
        )
        conn.execute(
            "INSERT INTO assets (asset_symbol, asset_name, asset_type, account_id, still_open)"
            " VALUES ('APPL', 'Apple', 'Stock', 1, 1)"
        )
        conn.execute(
            "INSERT INTO assets (asset_symbol, asset_name, asset_type, account_id, still_open)"
            " VALUES ('MSFT', 'Microsoft', 'Stock', 1, 0)"
        )
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
    assert [transaction.id for transaction in transactions] == [1]
    assert [transaction.asset.info.symbol for transaction in transactions] == ["APPL"]
    assert [transaction.asset.info.name for transaction in transactions] == ["Apple"]
    assert [transaction.asset.info.type for transaction in transactions] == ["Stock"]
    assert [transaction.date for transaction in transactions] == [date(2024, 1, 31)]
    assert [transaction.shares for transaction in transactions] == [100]
    assert [transaction.price for transaction in transactions] == [200]
    assert [transaction.asset.account.currency for transaction in transactions] == [
        "GBP"
    ]
