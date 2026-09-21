import datetime as dt
from sqlite3 import PARSE_DECLTYPES, Row, connect, register_adapter, register_converter
from typing import Any

import click
import pandas as pd
from flask import current_app, g


def adapt_date_iso(val):
    """Adapt datetime.date to ISO 8601 date."""
    return val.isoformat()


def adapt_date_pandas(val):
    """Adapt DateTimeIndex to ISO 8601 date."""
    return val.strftime("%Y-%m-%d")


def convert_date(val):
    """Convert ISO 8601 date to datetime.date object."""
    return dt.date.fromisoformat(val.decode())


register_converter("date", convert_date)
register_adapter(dt.date, adapt_date_iso)
register_adapter(pd.Timestamp, adapt_date_pandas)


def get_db():
    if "db" not in g:
        g.db = connect(current_app.config["DATABASE"], detect_types=PARSE_DECLTYPES)
        g.db.row_factory = Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@click.command("init-db")
def init_db():
    """Instantiate a database from CLI."""
    db = get_db()
    with current_app.open_resource("schema.sql", mode="r") as f:
        db.executescript(f.read())
    db.commit()
    click.echo("Database initialised.")


def execute_db(query: str, args: tuple[Any, ...] = ()):
    """Execute a command in the database with a single argument."""
    db = get_db()
    cursor = db.execute(query, args)
    cursor.close()
    db.commit()


def executemany_db(query: str, args: list[tuple[Any, ...]]):
    """Execute a command with a list of arguments in the database."""
    db = get_db()
    cursor = db.executemany(query, args)
    cursor.close()
    db.commit()


def fetch_single_record(query: str, args: tuple[Any, ...] = ()) -> Row | None:
    database = get_db()
    cursor = database.execute(query, args)
    record = cursor.fetchone()
    cursor.close()

    return record


def fetch_multiple_records(query: str, args: tuple[Any, ...] = ()) -> list[Row]:
    database = get_db()
    cursor = database.execute(query, args)
    records = cursor.fetchall()
    cursor.close()

    return records


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db)
