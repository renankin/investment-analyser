from flask import Blueprint, flash, request, redirect, render_template, url_for

from finance_app.accounts import accounts
from finance_app.assets import assets
from finance_app.market import market
from finance_app.transactions import transactions

assets_bp = Blueprint("assets", __name__, template_folder="templates")


@assets_bp.route("/assets")
def index():
    """Show list of assets in account."""

    if not accounts.get_all_accounts():
        return redirect(url_for("accounts.index"))

    a = assets.get_all_assets()

    if a:
        return render_template("show_assets.html", assets=a)

    flash("No assets to show. Must add asset first.")
    return redirect(url_for("assets.add"))


@assets_bp.route("/assets/add", methods=["POST", "GET"])
def add():
    """Add new asset for account."""

    a = accounts.get_all_accounts()

    s = market.get_all_sources()

    if not a:
        flash("No accounts. Must add account first.")
        return redirect(url_for("accounts.add"))

    if request.method == "POST":
        account_id = request.form.get("account_id", type=int)
        asset_name = request.form.get("asset_name")
        market_source_id = request.form.get("market_source_id", type=int)
        still_open = request.form.get("still_open", type=int)

        assets.insert_asset(account_id, asset_name, market_source_id, still_open)
        flash("Asset added.")
        return redirect(url_for("assets.index"))

    return render_template("add_asset.html", accounts=a, sources=s)


@assets_bp.route("/assets/edit/<int:asset_id>", methods=["POST", "GET"])
def edit(asset_id):
    """Edit asset."""

    a = assets.get_asset(asset_id)

    s = market.get_all_sources()

    if request.method == "POST":
        account_id = request.form.get("account_id", type=int)
        asset_name = request.form.get("asset_name")
        market_source_id = request.form.get("market_source_id", type=int)
        still_open = request.form.get("still_open", type=bool)

        if not still_open:
            still_open = False

        assets.update_asset(
            asset_id, account_id, asset_name, market_source_id, still_open
        )
        flash("Asset updated.")
        return redirect(url_for("assets.index"))

    return render_template("edit_asset.html", asset=a, market_sources=s)


@assets_bp.route("/assets/<int:asset_id>/delete", methods=["POST"])
def delete(asset_id):
    """Delete asset."""

    if transactions.get_transactions(asset_id):
        flash("Must delete transactions first.")
        return redirect(url_for("assets.index"))

    if market.get_prices(asset_id):
        flash("Must delete prices first.")
        return redirect(url_for("assets.index"))

    if market.get_dividends(asset_id):
        flash("Must delete dividends first.")
        return redirect(url_for("assets.index"))

    if market.get_stock_splits(asset_id):
        flash("Must delete splits first.")
        return redirect(url_for("assets.index"))

    assets.delete_asset(asset_id)
    flash("Asset deleted.")

    return redirect(url_for("assets.index"))


@assets_bp.route("/assets/<int:asset_id>/dividends")
def show_dividends(asset_id):
    """Show dividends received for asset."""

    dividends = assets.get_dividends_received(asset_id)

    asset = assets.get_asset(asset_id)

    account = accounts.get_account(asset["account_id"])

    if not dividends:
        flash("No dividends to show.")
        return redirect(url_for("assets.index"))

    return render_template(
        "show_dividends_received.html",
        dividends=dividends,
        currency=account["currency"],
    )
