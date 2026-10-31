from datetime import datetime
from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.services.asset_service import AssetService
from app.services.transaction_service import TransactionService

transactions_bp = Blueprint(
    "transactions", __name__, template_folder="../templates/transactions"
)


@transactions_bp.route("/transactions")
def index():
    asset_search = request.args.get("search")
    if not asset_search:
        asset_search = ""
    all_transactions = []
    for transaction in TransactionService.get_all_transactions():
        if asset_search.upper() in transaction.asset.info.symbol.upper():
            all_transactions.append(transaction)
    return render_template("show_transactions.html", transactions=all_transactions)


@transactions_bp.route("/transactions/add", methods=["GET", "POST"])
@transactions_bp.route(
    "/assets/<int:asset_id>/transactions/add", methods=["POST", "GET"]
)
def add(asset_id=None):
    if request.method == "POST":
        form_asset_id = request.form.get("asset_id", type=int)
        transaction_date = request.form.get("date")
        shares = request.form.get("shares", type=Decimal)
        price = request.form.get("price", type=Decimal)

        if not form_asset_id:
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

        TransactionService(form_asset_id).add_transaction(
            date=datetime.fromisoformat(transaction_date).date(), shares=shares, price=price
        )
        flash("Transaction added.")

        if asset_id:
            return redirect(url_for("assets.show_transactions", asset_id=asset_id))
        return redirect(url_for("transactions.index"))

    return render_template(
        "add_transaction.html",
        assets=[AssetService(asset_id).asset]
        if asset_id
        else AssetService.get_all_assets(),
    )


@transactions_bp.route("/transactions/delete/<int:transaction_id>", methods=["POST"])
def delete(transaction_id):
    TransactionService(transaction_id).delete_transaction()
    flash("Transaction not deleted.")
    return redirect(url_for("transactions.index"))


@transactions_bp.route(
    "/transactions/edit/<int:transaction_id>", methods=["GET", "POST"]
)
def edit(transaction_id):
    transaction = TransactionService(transaction_id).transaction
    if request.method == "POST":
        transaction_date = request.form.get("date")
        shares = request.form.get("shares", type=Decimal)
        price = request.form.get("price", type=Decimal)

        if transaction_date and shares and price:
            transaction.date = datetime.fromisoformat(transaction_date).date()
            transaction.shares = shares
            transaction.price = price

        TransactionService(transaction_id).edit_transaction(transaction)
        flash("Transaction updated.")
        return redirect(url_for("transactions.index"))

    return render_template("edit_transaction.html", transaction=transaction)
