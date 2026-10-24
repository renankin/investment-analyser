from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.repositories.accounts import get_account, get_all_accounts
from app.repositories.assets import (
    edit_asset,
    get_all_assets,
    insert_asset,
)
from app.services.asset_deletion import delete_asset_if_unused
from app.services.asset_service import AssetService
from app.services.dividends import get_dividends_received

assets_bp = Blueprint("assets", __name__, template_folder="../templates/asset-page")


@assets_bp.route("/assets")
def index():
    """Show list of assets in account."""

    asset_search = request.args.get("search")
    if not asset_search:
        asset_search = ""

    all_assets = []
    for asset in get_all_assets():
        if asset_search.upper() in asset.info.symbol.upper():
            all_assets.append(asset)

    return render_template("show_assets.html", assets=all_assets)


@assets_bp.route("/assets/add", methods=["POST", "GET"])
def add():
    """Add new asset for account."""

    all_accounts = get_all_accounts()

    if not all_accounts:
        flash("No accounts. Must add account first.")
        return redirect(url_for("accounts.add"))

    if request.method == "POST":
        account_id = request.form.get("account_id", type=int)
        asset_symbol = request.form.get("asset_symbol")
        asset_name = request.form.get("asset_name")
        asset_type = request.form.get("asset_type")
        still_open = request.form.get("still_open", type=bool)

        if not still_open:
            still_open = False

        if account_id and asset_symbol and asset_name and asset_type:
            insert_asset(account_id, asset_symbol, asset_name, asset_type, still_open)
            flash("Asset added.")

        return redirect(url_for("assets.index"))

    return render_template("add_asset.html", accounts=all_accounts)


@assets_bp.route("/assets/<int:asset_id>/edit", methods=["POST", "GET"])
def edit(asset_id):
    """Edit asset."""

    asset_service = AssetService(asset_id)

    if request.method == "POST":
        asset_symbol = request.form.get("asset_symbol")
        asset_name = request.form.get("asset_name")
        asset_type = request.form.get("asset_type")
        still_open = request.form.get("still_open", type=bool)

        if not still_open:
            still_open = False
            asset_service.asset.still_open = still_open

        if asset_symbol and asset_name and asset_type:
            asset_service.asset.info.symbol = asset_symbol
            asset_service.asset.info.name = asset_name
            asset_service.asset.info.type = asset_type

        edit_asset(asset_service.asset)
        flash("Asset updated.")
        return redirect(url_for("assets.index"))

    return render_template("edit_asset.html", asset=asset_service.asset)


@assets_bp.route("/assets/<int:asset_id>/delete", methods=["POST"])
def delete(asset_id):
    deletion_blocker = delete_asset_if_unused(asset_id)
    messages = {
        "transactions": "Must delete transactions first.",
        "prices": "Must delete prices first.",
        "dividends": "Must delete dividends first.",
        "splits": "Must delete splits first.",
    }
    flash(messages[deletion_blocker] if deletion_blocker else "Asset deleted.")

    return redirect(url_for("assets.index"))


@assets_bp.route("/assets/<int:asset_id>/dividends")
def show_dividends(asset_id):
    dividends = get_dividends_received(asset_id)
    asset_service = AssetService(asset_id)
    account = get_account(asset_service.asset.account.id)
    return render_template(
        "show_dividends_received.html",
        dividends=dividends,
        currency=account.currency,
        asset=asset_service.asset,
    )


@assets_bp.route("/assets/<int:asset_id>/price")
def plot_prices(asset_id):
    asset_service = AssetService(asset_id)
    return render_template(
        "asset_price_graph.html",
        dates=asset_service.price_analyser.get_dates(),
        prices=asset_service.price_analyser.get_prices(),
        yearly_change=[
            {
                "year": year,
                "percentage": asset_service.price_analyser.calculate_yearly_change(
                    year
                ),
            }
            for year in [1, 3, 5]
        ],
        asset=asset_service.asset,
    )


@assets_bp.route("/assets/<int:asset_id>/price/update", methods=["POST"])
def update_prices(asset_id):
    asset_service = AssetService(asset_id)
    asset_service.update_prices()
    flash("Prices updated.")
    return redirect(
        url_for(
            "assets.plot_prices",
            asset_id=asset_service.asset.id,
            asset_name=asset_service.asset.info.name,
        )
    )
