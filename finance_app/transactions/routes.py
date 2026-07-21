from flask import Blueprint, flash, redirect, render_template, request, url_for

from finance_app.accounts import accounts as accounts
from finance_app.assets import assets as assets
from finance_app.transactions import transactions as transactions


transactions_bp = Blueprint("transactions", __name__, template_folder="templates")


@transactions_bp.route("/transactions")
def index():
    """List all transactions."""

    asset_search = request.args.get("search")
    if not asset_search:
        asset_search = ""

    all_transactions = []
    for transaction in transactions.get_all_transactions():
        if asset_search.upper() in transaction["asset_name"].upper():
            all_transactions.append(transaction)

    return render_template("show_transactions.html", transactions=all_transactions)


@transactions_bp.route("/transactions/add", methods=["GET", "POST"])
def add():
    """Adds new transaction into database"""

    a = assets.get_all_assets()

    if not a:
        flash("No assets to show. Must add asset first.")
        return redirect(url_for("assets.add"))

    if request.method == "POST":
        asset_id = request.form.get("asset_id", type=int)
        date = request.form.get("date")
        shares = request.form.get("shares", type=float)
        price = request.form.get("price", type=float)

        if not date:
            flash("Must provide date.")
            return redirect(url_for("transactions.add"))

        if not shares:
            flash("Must provide shares")
            return redirect(url_for("transactions.add"))

        if not price:
            flash("Must provide price.")
            return redirect(url_for("transactions.add"))

        transactions.insert_transaction(asset_id, date, shares, price)
        flash("Transaction added.")
        return redirect(url_for("transactions.index"))

    return render_template("add_transaction.html", assets=a)


@transactions_bp.route("/transactions/delete/<int:transaction_id>", methods=["POST"])
def delete(transaction_id):
    """Deletes transaction"""

    t = transactions.get_transaction(transaction_id)

    if t:
        transactions.delete_transaction(transaction_id)
        flash("Transaction deleted.")
    else:
        flash("Transaction not deleted.")

    return redirect(url_for("transactions.index"))


@transactions_bp.route(
    "/transactions/edit/<int:transaction_id>", methods=["GET", "POST"]
)
def edit(transaction_id):
    """Edit transaction"""

    t = transactions.get_transaction(transaction_id)

    asset = assets.get_asset_by_id(t["asset_id"])

    if not t:
        flash("Transaction invalid.")
        return redirect(url_for("transactions.index"))

    if request.method == "POST":
        asset_id = request.form.get("asset_id", type=int)
        date = request.form.get("date")
        shares = request.form.get("shares", type=float)
        price = request.form.get("price", type=float)

        if not date:
            flash("Must provide date.")
            return redirect(url_for("transactions.edit", transaction_id))

        if not shares:
            flash("Must provide shares")
            return redirect(url_for("transactions.edit", transaction_id))

        if not price:
            flash("Must provide price.")
            return redirect(url_for("transactions.edit", transaction_id))

        transactions.update_transaction(transaction_id, asset_id, date, shares, price)
        flash("Transaction updated.")
        return redirect(url_for("transactions.index"))

    return render_template("edit_transaction.html", transaction=t, asset=asset)
