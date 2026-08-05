from flask import Blueprint, flash, json, redirect, render_template, url_for

from finance_app.assets import assets
from finance_app.market import dividends, prices, stock_splits

market_bp = Blueprint("market", __name__, template_folder="templates")


@market_bp.route("/market/dividends/add/<int:asset_id>", methods=["POST"])
def add_dividends(asset_id):

    if dividends.insert_dividends(asset_id):
        flash("Dividends added.")

    else:
        flash("Failed to load dividends.")

    return redirect(url_for("assets.index"))


@market_bp.route("/market/dividends/delete/<int:asset_id>", methods=["POST"])
def delete_dividends(asset_id):
    """Delete dividends for asset."""

    if dividends.delete_dividends(asset_id):
        flash("Dividends deleted.")
    else:
        flash("Failed to delete dividends.")

    return redirect(url_for("assets.index"))


@market_bp.route("/market/dividends/<int:asset_id>")
def show_dividends(asset_id):
    """Show dividends for asset."""

    divs = dividends.get_dividends(asset_id)

    if divs:
        return render_template("show_dividends.html", dividends=divs)

    flash("No dividends to show.")
    return redirect(url_for("assets.index"))


@market_bp.route("/market/prices/add/<int:asset_id>", methods=["POST"])
def add_prices(asset_id):
    """Insert prices for asset."""

    if prices.insert_prices(asset_id):
        flash("Prices added.")
    else:
        flash("Failed to add prices.")

    return redirect(url_for("assets.index"))


@market_bp.route("/market/prices/delete/<int:asset_id>", methods=["POST"])
def delete_prices(asset_id):
    """Deletes prices from asset."""

    if prices.delete_prices(asset_id):
        flash("Prices deleted.")
    else:
        flash("Failed to delete prices.")

    return redirect(url_for("assets.index"))


@market_bp.route("/market/prices/<int:asset_id>")
def show_prices(asset_id):
    """Show prices for asset."""

    p = prices.get_prices(asset_id)

    data = json.dumps([price["unit_price"] for price in p])
    labels = json.dumps([price["date"] for price in p])

    a = assets.get_asset(asset_id)

    asset_name = json.dumps(a["asset_name"])

    if p:
        return render_template(
            "show_prices.html", data=data, labels=labels, asset_name=asset_name
        )

    flash("No prices to show.")
    return redirect(url_for("assets.index"))


@market_bp.route("/market/splits/add/<int:asset_id>", methods=["POST"])
def add_splits(asset_id):
    """Insert splits for asset."""

    if stock_splits.insert_stock_splits(asset_id):
        flash("Splits added.")
    else:
        flash("Failed to add splits.")

    return redirect(url_for("assets.index"))


@market_bp.route("/market/splits/<int:asset_id>", methods=["POST"])
def delete_splits(asset_id):
    """Deletes stock splits from asset."""

    if stock_splits.delete_stock_splits(asset_id):
        flash("Splits deleted.")
    else:
        flash("No splits to delete.")

    return redirect(url_for("assets.index"))


@market_bp.route("/market/splits/<int:asset_id>")
def show_splits(asset_id):
    """Show stock splits for asset."""

    s = stock_splits.get_stock_splits(asset_id)

    if s:
        return render_template("show_splits.html", splits=s)

    flash("No splits to show.")
    return redirect(url_for("assets.index"))
