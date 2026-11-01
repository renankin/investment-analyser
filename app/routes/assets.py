from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.services.account_service import AccountService
from app.services.asset_service import AssetService
from app.services.dividend_service import DividendService
from app.services.price_service import PriceService
from app.services.stock_split_service import StockSplitService
from app.services.transaction_service import TransactionService

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
    if AssetService(asset_id).delete_asset():
        flash("Asset deleted.")
    else:
        flash("Asset not deleted. Must delete transactions.")
    return redirect(url_for("assets.index"))


@assets_bp.route("/assets/<int:asset_id>/dividends-received")
def show_dividends_received(asset_id):
    dividend_service = DividendService(asset_id)
    return render_template(
        "show_dividends_received.html",
        dividends=dividend_service.dividends_received,
        total_dividends=dividend_service.total_dividends,
        asset=AssetService(asset_id).asset,
    )


@assets_bp.route("/assets/<int:asset_id>/dividends")
def show_dividends(asset_id):
    return render_template(
        "show_dividend_history.html",
        dividends=DividendService(asset_id).dividends,
        asset=AssetService(asset_id).asset,
    )


@assets_bp.route("/assets/<int:asset_id>/dividends/delete", methods=["POST"])
def delete_dividends(asset_id):
    asset = AssetService(asset_id).asset
    DividendService.delete_dividends(asset)
    flash("Dividends deleted.")
    return redirect(url_for("assets.show_dividends", asset_id=asset_id))


@assets_bp.route("/assets/<int:asset_id>/dividends/update", methods=["POST"])
def update_dividends(asset_id):
    asset = AssetService(asset_id).asset
    DividendService.update_dividends(asset)
    flash("Dividends updated.")
    return redirect(url_for("assets.show_dividends", asset_id=asset_id))


@assets_bp.route("/assets/<int:asset_id>/price")
def plot_prices(asset_id):
    price_service = PriceService(asset_id)

    return render_template(
        "asset_price_graph.html",
        dates=price_service.get_dates(),
        prices=price_service.get_prices(),
        yearly_change=[
            {"year": 1, "percentage": price_service.calculate_yearly_change(1)},
            {"year": 3, "percentage": price_service.calculate_yearly_change(3)},
            {"year": 5, "percentage": price_service.calculate_yearly_change(5)},
        ],
        asset=AssetService(asset_id).asset,
    )


@assets_bp.route("/assets/<int:asset_id>/price/delete", methods=["POST"])
def delete_prices(asset_id):
    asset = AssetService(asset_id).asset
    PriceService.delete_prices(asset)
    flash("Prices deleted.")
    return redirect(
        url_for(
            "assets.plot_prices",
            asset_id=asset.id,
            asset_name=asset.info.name,
        )
    )


@assets_bp.route("/assets/<int:asset_id>/price/update", methods=["POST"])
def update_prices(asset_id):
    asset = AssetService(asset_id).asset
    PriceService.update_prices(asset)
    flash("Prices updated.")
    return redirect(
        url_for(
            "assets.plot_prices",
            asset_id=asset.id,
            asset_name=asset.info.name,
        )
    )


@assets_bp.route("/assets/<int:asset_id>/stock-splits", methods=["GET"])
def show_stock_splits(asset_id):
    return render_template(
        "show_splits.html",
        asset=AssetService(asset_id).asset,
        splits=StockSplitService(asset_id).stock_splits,
    )


@assets_bp.route("/assets/<int:asset_id>/stock-splits/delete", methods=["POST"])
def delete_stock_splits(asset_id):
    asset = AssetService(asset_id).asset
    StockSplitService(asset_id).delete_stock_splits(asset)
    flash("Stock split deleted.")
    return redirect(url_for("assets.show_stock_splits", asset_id=asset_id))


@assets_bp.route("/assets/<int:asset_id>/stock-splits/update", methods=["POST"])
def update_stock_splits(asset_id):
    asset = AssetService(asset_id).asset
    StockSplitService(asset_id).update_stock_splits(asset)
    flash("Stock split updated.")
    return redirect(url_for("assets.show_stock_splits", asset_id=asset_id))


@assets_bp.route("/assets/<int:asset_id>/transactions")
def show_transactions(asset_id):
    asset_service = AssetService(asset_id)
    return render_template(
        "show_asset_transactions.html",
        transactions=TransactionService.get_adjusted_transactions_from_asset(asset_id),
        asset=asset_service.asset,
    )
