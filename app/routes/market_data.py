from flask import Blueprint, flash, redirect, render_template, url_for

from app.repositories import assets
from app.repositories.dividends import (
    delete_dividends,
    get_dividends,
)
from app.repositories.prices import (
    delete_prices,
    get_market_prices,
)
from app.repositories.stock_splits import (
    delete_stock_splits,
    get_stock_splits,
)
from app.services.market_dividends import insert_dividends
from app.services.stock_splits import insert_stock_splits

market_bp = Blueprint("market", __name__)


@market_bp.route("/market/dividends/add/<int:asset_id>", methods=["POST"])
def add_dividends(asset_id):

    if insert_dividends(asset_id):
        flash("Dividends added.")

    else:
        flash("Failed to load dividends.")

    return redirect(url_for("assets.index"))


@market_bp.route("/market/dividends/delete/<int:asset_id>", methods=["POST"])
def del_dividends(asset_id):
    """Delete dividends for asset."""

    if delete_dividends(asset_id):
        flash("Dividends deleted.")
    else:
        flash("Failed to delete dividends.")

    return redirect(url_for("assets.index"))


@market_bp.route("/market/dividends/<int:asset_id>")
def show_dividends(asset_id):
    """Show dividends for asset."""

    divs = get_dividends(asset_id)

    if divs:
        return render_template("show_dividends.html", dividends=divs)

    flash("No dividends to show.")
    return redirect(url_for("assets.index"))


@market_bp.route("/market/prices/delete/<int:asset_id>", methods=["POST"])
def del_prices(asset_id):
    """Deletes prices from asset."""

    if delete_prices(asset_id):
        flash("Prices deleted.")
    else:
        flash("Failed to delete prices.")

    return redirect(url_for("assets.index"))


@market_bp.route("/market/prices/<int:asset_id>")
def show_prices(asset_id):
    """Show prices for asset."""

    p = get_market_prices(asset_id)

    data = [float(price.value) for price in p]
    labels = [price.date.isoformat() for price in p]

    a = assets.get_asset_by_id(asset_id)

    asset_name = a.info.name

    if p:
        return render_template(
            "show_prices.html", data=data, labels=labels, asset_name=asset_name
        )

    flash("No prices to show.")
    return redirect(url_for("assets.index"))


@market_bp.route("/market/splits/add/<int:asset_id>", methods=["POST"])
def add_splits(asset_id):
    """Insert splits for asset."""

    if insert_stock_splits(asset_id):
        flash("Splits added.")
    else:
        flash("Failed to add splits.")

    return redirect(url_for("assets.index"))


@market_bp.route("/market/splits/<int:asset_id>", methods=["POST"])
def delete_splits(asset_id):
    """Deletes stock splits from asset."""

    if delete_stock_splits(asset_id):
        flash("Splits deleted.")
    else:
        flash("No splits to delete.")

    return redirect(url_for("assets.index"))


@market_bp.route("/market/splits/<int:asset_id>")
def show_splits(asset_id):
    """Show stock splits for asset."""

    s = get_stock_splits(asset_id)

    if s:
        return render_template("show_splits.html", splits=s)

    flash("No splits to show.")
    return redirect(url_for("assets.index"))
