import datetime as dt
import sqlite3

import click
from flask import current_app, g


def adapt_date_iso(val):
    """Adapt datetime.date to ISO 8601 date."""
    return val.isoformat()


def convert_date(val):
    """Convert ISO 8601 date to datetime.date object."""
    return dt.date.fromisoformat(val.decode())


sqlite3.register_converter("date", convert_date)
sqlite3.register_adapter(dt.date, adapt_date_iso)


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = dict_factory

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


def execute_db(query: str, args=()):
    """Insert a command in the database. If args is a list it will insert all entries
    into database."""

    db = get_db()

    if isinstance(args, list):
        cur = db.executemany(query, args)
    else:
        cur = db.execute(query, args)

    cur.close()
    db.commit()


def query_db(query: str, args=(), one=False):
    """Returns a dictionary with queried database if `One` is True. Otherwise, returns a list of dictionaries if `One` is False."""

    cur = get_db().execute(query, args)
    res = cur.fetchall()
    cur.close()

    if res:
        if one:
            return res[0]
        return res

    return None


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db)
