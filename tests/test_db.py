from datetime import date
from sqlite3 import (
    PARSE_DECLTYPES,
    ProgrammingError,
    Row,
    connect,
    register_adapter,
    register_converter,
)

from flask import g
from pandas import Timestamp
from pytest import fixture, raises

from investment_analyser import create_app, db


@fixture
def test_app():
    app = create_app()
    app.config["DATABASE"] = ":memory:"
    return app


@fixture
def mock_db(monkeypatch):
    database = connect(":memory:", detect_types=PARSE_DECLTYPES)
    database.row_factory = Row
    register_converter("date", db.convert_date)
    register_adapter(date, db.adapt_date_iso)
    register_adapter(Timestamp, db.adapt_date_pandas)

    cursor = database.cursor()
    cursor.execute(
        "CREATE TABLE mock_table (id INTEGER PRIMARY KEY, date DATE, message TEXT)"
    )
    cursor.close()

    monkeypatch.setattr(db, "get_db", lambda: database)
    yield db
    database.close()


def test_connection_lifecycle(test_app):
    with test_app.app_context():
        connection = db.get_db()
        assert g.db is connection
        assert db.get_db() is connection

        db.close_db()
        assert "db" not in g

        with raises(ProgrammingError):
            connection.cursor()


def test_single_record(mock_db):
    mock_db.execute_db("INSERT INTO mock_table (message) VALUES ('Hello')")
    result = mock_db.fetch_single_record(
        "SELECT message FROM mock_table WHERE id = ?",
        (1,),
    )
    assert result["message"] == "Hello"


def test_multiple_records(mock_db):
    mock_db.execute_db("INSERT INTO mock_table (message) VALUES ('Hello')")
    mock_db.execute_db("INSERT INTO mock_table (message) VALUES ('world')")
    res = mock_db.fetch_multiple_records("SELECT message FROM mock_table WHERE id >= 1")
    assert [row["message"] for row in res] == ["Hello", "world"]


def test_single_record_not_found(mock_db):
    res = mock_db.fetch_single_record(
        "SELECT message FROM mock_table WHERE id = ?", (1,)
    )
    assert res is None


def test_multiple_record_not_found(mock_db):
    res = mock_db.fetch_multiple_records(
        "SELECT message FROM mock_table WHERE id = ?",
        (1,),
    )
    assert res == []


def test_single_record_returns_first_matching_row(mock_db):
    mock_db.execute_db("INSERT INTO mock_table (message) VALUES ('Hello')")
    mock_db.execute_db("INSERT INTO mock_table (message) VALUES ('world')")
    res = mock_db.fetch_single_record("SELECT message FROM mock_table WHERE id >= 1")
    assert res["message"] == "Hello"


def test_adapt_iso_date(mock_db):
    test_date = date(2021, 1, 31)
    mock_db.execute_db("INSERT INTO mock_table (date) VALUES (?)", (test_date,))
    res = mock_db.fetch_single_record(
        "SELECT * FROM mock_table WHERE date = ?", (test_date,)
    )
    assert res["date"] == test_date


def test_adapt_pandas_date(mock_db):
    test_date = Timestamp(2021, 1, 31)
    mock_db.execute_db("INSERT INTO mock_table (date) VALUES (?)", (test_date,))
    res = mock_db.fetch_single_record(
        "SELECT * FROM mock_table WHERE date = ?", (test_date,)
    )
    assert res["date"] == date(2021, 1, 31)


def test_multiple_inserts(mock_db):
    mock_db.executemany_db(
        "INSERT INTO mock_table (message) VALUES (?)", [("Hello",), ("world",)]
    )
    res = mock_db.fetch_multiple_records("SELECT message FROM mock_table")
    assert [row["message"] for row in res] == ["Hello", "world"]
