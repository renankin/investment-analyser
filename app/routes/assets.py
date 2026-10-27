from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.services.account_service import AccountService
from app.services.asset_service import AssetService
from app.services.price_service import PriceService

assets_bp = Blueprint("assets", __name__, template_folder="../templates/assets")


@assets_bp.route("/assets")
def index():
    """Show list of assets in account."""

    return render_template("show_assets.html", assets=AssetService.get_all_assets())


@assets_bp.route("/assets/add", methods=["POST", "GET"])
def add():
    if request.method == "POST":
        account_id = request.form.get("account_id", type=int)
        asset_symbol = request.form.get("asset_symbol")
        asset_name = request.form.get("asset_name")
        asset_type = request.form.get("asset_type")
        still_open = request.form.get("still_open", type=bool)

        if not still_open:
            still_open = False

        if account_id and asset_symbol and asset_name and asset_type:
            AssetService.add_new_asset(
                account_id, asset_symbol, asset_name, asset_type, still_open
            )
            flash("Asset added.")
        return redirect(url_for("assets.index"))

    return render_template("add_asset.html", accounts=AccountService.get_all_accounts())


@assets_bp.route("/assets/<int:asset_id>/edit", methods=["POST", "GET"])
def edit(asset_id):
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

        asset_service.edit_asset(asset_service.asset)
        flash("Asset updated.")
        return redirect(url_for("assets.edit", asset_id=asset_service.asset.id))

    return render_template("edit_asset.html", asset=asset_service.asset)


@assets_bp.route("/assets/<int:asset_id>/delete", methods=["POST"])
def delete_asset(asset_id):
    asset_service = AssetService(asset_id)
    deletion_blocker = asset_service.delete_asset()

    if deletion_blocker:
        messages = {
            "transactions": "Must delete transactions first.",
            "prices": "Must delete prices first.",
            "dividends": "Must delete dividends first.",
            "splits": "Must delete splits first.",
        }
        flash(messages[deletion_blocker])
        return redirect(url_for("assets.edit", asset_id=asset_service.asset.id))

    flash("Asset deleted.")
    return redirect(url_for("assets.index"))


@assets_bp.route("/assets/<int:asset_id>/dividends-received")
def show_dividends_received(asset_id):
    asset_service = AssetService(asset_id)
    return render_template(
        "show_dividends_received.html",
        dividends=asset_service.get_dividends_received(),
        asset=asset_service.asset,
    )


@assets_bp.route("/assets/<int:asset_id>/dividends")
def show_dividends(asset_id):
    asset_service = AssetService(asset_id)
    return render_template(
        "show_dividend_history.html",
        dividends=asset_service.dividends,
        asset=asset_service.asset,
    )


@assets_bp.route("/assets/<int:asset_id>/dividends/update", methods=["POST"])
def update_dividends(asset_id):
    asset_service = AssetService(asset_id)
    asset_service.update_dividends()
    flash("Dividends updated.")
    return redirect(url_for("assets.show_dividends", asset_id=asset_service.asset.id))


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
    PriceService.update_prices(asset_service.asset)
    flash("Prices updated.")
    return redirect(
        url_for(
            "assets.plot_prices",
            asset_id=asset_service.asset.id,
            asset_name=asset_service.asset.info.name,
        )
    )


@assets_bp.route("/assets/<int:asset_id>/stock-splits", methods=["GET"])
def show_stock_splits(asset_id):
    asset_service = AssetService(asset_id)
    return render_template(
        "show_splits.html", asset=asset_service.asset, splits=asset_service.stock_splits
    )


@assets_bp.route("/assets/<int:asset_id>/stock-splits/update", methods=["POST"])
def update_stock_splits(asset_id):
    asset_service = AssetService(asset_id)
    asset_service.update_stock_splits()
    flash("Stock split updated.")
    return redirect(
        url_for("assets.show_stock_splits", asset_id=asset_service.asset.id)
    )


@assets_bp.route("/assets/<int:asset_id>/transactions")
def show_transactions(asset_id):
    asset_service = AssetService(asset_id)
    return render_template(
        "show_asset_transactions.html",
        transactions=asset_service.get_transactions_from_asset(),
        asset=asset_service.asset,
    )
