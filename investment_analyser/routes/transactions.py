from datetime import datetime
from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, url_for

from investment_analyser.repository.assets import get_all_assets
from investment_analyser.repository.transactions import (
    delete_transaction,
    get_all_transactions,
    get_transaction_by_id,
    insert_transaction,
    update_transaction,
)

transactions_bp = Blueprint("transactions", __name__)


@transactions_bp.route("/transactions")
def index():
    """List all transactions."""

    asset_search = request.args.get("search")
    if not asset_search:
        asset_search = ""

    all_transactions = []
    for transaction in get_all_transactions():
        if asset_search.upper() in transaction.asset.info.symbol.upper():
            all_transactions.append(transaction)

    return render_template("show_transactions.html", transactions=all_transactions)


@transactions_bp.route("/transactions/add", methods=["GET", "POST"])
def add():
    """Adds new transaction into database"""

    available_assets = get_all_assets()

    if not available_assets:
        flash("No assets to show. Must add asset first.")
        return redirect(url_for("assets.add"))

    if request.method == "POST":
        asset_id = request.form.get("asset_id", type=int)
        transaction_date = request.form.get("date")
        shares = request.form.get("shares", type=Decimal)
        price = request.form.get("price", type=Decimal)

        if not asset_id:
            flash("Invalid asset.")
            return redirect(url_for("transactions.add"))

        if not transaction_date:
            flash("Must provide date.")
            return redirect(url_for("transactions.add"))
        else:
            transaction_date = datetime.fromisoformat(transaction_date)

        if not shares:
            flash("Must provide shares")
            return redirect(url_for("transactions.add"))

        if not price:
            flash("Must provide price.")
            return redirect(url_for("transactions.add"))

        insert_transaction(asset_id, transaction_date, shares, price)
        flash("Transaction added.")
        return redirect(url_for("transactions.index"))

    return render_template("add_transaction.html", assets=available_assets)


@transactions_bp.route("/transactions/delete/<int:transaction_id>", methods=["POST"])
def delete(transaction_id):
    """Deletes transaction"""

    t = get_transaction_by_id(transaction_id)

    if t:
        delete_transaction(transaction_id)
        flash("Transaction deleted.")
    else:
        flash("Transaction not deleted.")

    return redirect(url_for("transactions.index"))


@transactions_bp.route(
    "/transactions/edit/<int:transaction_id>", methods=["GET", "POST"]
)
def edit(transaction_id):
    """Edit transaction"""

    transaction = get_transaction_by_id(transaction_id)

    if not transaction:
        flash("Transaction invalid.")
        return redirect(url_for("transactions.index"))

    if request.method == "POST":
        asset_id = request.form.get("asset_id", type=int)
        transaction_date = request.form.get("date")
        shares = request.form.get("shares", type=Decimal)
        price = request.form.get("price", type=Decimal)

        if not asset_id:
            flash("Invalid asset.")
            return redirect(url_for("transactions.add"))

        if not transaction_date:
            flash("Must provide date.")
            return redirect(url_for("transactions.add"))

        if not shares:
            flash("Must provide shares")
            return redirect(url_for("transactions.add"))

        if not price:
            flash("Must provide price.")
            return redirect(url_for("transactions.add"))

        update_transaction(transaction_id, asset_id, transaction_date, shares, price)
        flash("Transaction updated.")
        return redirect(url_for("transactions.index"))

    return render_template("edit_transaction.html", transaction=transaction)
