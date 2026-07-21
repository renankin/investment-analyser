from flask import Blueprint, flash, request, redirect, render_template, url_for

from finance_app.accounts import accounts
from finance_app.assets import assets
from finance_app.market import dividends, prices, stock_splits
from finance_app.transactions import transactions

assets_bp = Blueprint("assets", __name__, template_folder="templates")


@assets_bp.route("/assets")
def index():
    """Show list of assets in account."""

    asset_search = request.args.get("search")
    if not asset_search:
        asset_search = ""

    all_assets = []
    for asset in assets.get_all_assets():
        if asset_search.upper() in asset["asset_name"].upper():
            all_assets.append(asset)

    return render_template("show_assets.html", assets=all_assets)


@assets_bp.route("/assets/add", methods=["POST", "GET"])
def add():
    """Add new asset for account."""

    all_accounts = accounts.get_all_accounts()

    if not all_accounts:
        flash("No accounts. Must add account first.")
        return redirect(url_for("accounts.add"))

    if request.method == "POST":
        account_id = request.form.get("account_id", type=int)
        asset_name = request.form.get("asset_name")
        asset_type = request.form.get("asset_type")
        still_open = request.form.get("still_open", type=bool)

        if not still_open:
            still_open = False

        assets.insert_asset(account_id, asset_name, asset_type, still_open)
        flash("Asset added.")
        return redirect(url_for("assets.index"))

    return render_template("add_asset.html", accounts=all_accounts)


@assets_bp.route("/assets/edit/<int:asset_id>", methods=["POST", "GET"])
def edit(asset_id):
    """Edit asset."""

    a = assets.get_asset_by_id(asset_id)

    if request.method == "POST":
        account_id = request.form.get("account_id", type=int)
        asset_name = request.form.get("asset_name")
        asset_type = request.form.get("asset_type")
        still_open = request.form.get("still_open", type=bool)

        if not still_open:
            still_open = False

        assets.update_asset(
            asset_id, account_id, asset_name, asset_type, still_open
        )
        flash("Asset updated.")
        return redirect(url_for("assets.index"))

    return render_template("edit_asset.html", asset=a)


@assets_bp.route("/assets/<int:asset_id>/delete", methods=["POST"])
def delete(asset_id):
    """Delete asset."""

    if transactions.get_transactions(asset_id):
        flash("Must delete transactions first.")
        return redirect(url_for("assets.index"))

    if prices.get_prices(asset_id):
        flash("Must delete prices first.")
        return redirect(url_for("assets.index"))

    if dividends.get_dividends(asset_id):
        flash("Must delete dividends first.")
        return redirect(url_for("assets.index"))

    if stock_splits.get_stock_splits(asset_id):
        flash("Must delete splits first.")
        return redirect(url_for("assets.index"))

    assets.delete_asset(asset_id)
    flash("Asset deleted.")

    return redirect(url_for("assets.index"))


@assets_bp.route("/assets/<int:asset_id>/dividends")
def show_dividends(asset_id):
    """Show dividends received for asset."""

    dividends = assets.get_dividends_received(asset_id)

    asset = assets.get_asset_by_id(asset_id)

    account = accounts.get_account(asset["account_id"])

    if not dividends:
        flash("No dividends to show.")
        return redirect(url_for("assets.index"))

    return render_template(
        "show_dividends_received.html",
        dividends=dividends,
        currency=account["currency"],
    )
