from flask import Blueprint, flash, json, redirect, request, render_template, url_for

from finance_app.assets import assets
from finance_app.market import market

market_bp = Blueprint("market", __name__, template_folder="templates")


@market_bp.route("/market/sources")
def show_sources():
    """Get market sources and display them in a table."""

    s = market.get_all_sources()

    return render_template("show_sources.html", market_sources=s)


@market_bp.route("/market/sources/add", methods=["GET", "POST"])
def add_source():
    """Add new source."""

    if request.method == "POST":
        display_name = request.form.get("source_name")
        source_key = request.form.get("source_key")
        p = request.form.get("supports_prices", type=bool)
        d = request.form.get("supports_dividends", type=bool)
        s = request.form.get("supports_splits", type=bool)

        if not p:
            p = False
        if not d:
            d = False
        if not s:
            s = False

        if market.insert_source(display_name, source_key, p, d, s):
            flash("Source added.")
            return redirect(url_for("market.show_sources"))

        flash("Failed to add source.")

    return render_template("add_source.html")


@market_bp.route("/market/sources/<int:source_id>/delete", methods=["POST"])
def delete_source(source_id):
    """Deletes source from database."""

    a = assets.get_assets_from_source(source_id)

    if a:
        flash("Must delete assets first.")
        return redirect(url_for("market.show_sources"))

    if market.delete_source(source_id):
        flash("Source deleted.")
    else:
        flash("Failed to delete source.")

    return redirect(url_for("market.show_sources"))


@market_bp.route("/market/sources/<int:source_id>/edit", methods=["GET", "POST"])
def edit_source(source_id):
    """Edits source."""

    s = market.get_source_by_id(source_id)

    if request.method == "POST":
        display_name = request.form.get("source_name")
        source_key = request.form.get("source_key")
        p = request.form.get("supports_prices", type=bool)
        d = request.form.get("supports_dividends", type=bool)
        s = request.form.get("supports_splits", type=bool)

        if not p:
            p = False
        if not d:
            d = False
        if not s:
            s = False

        if market.update_source(source_id, display_name, source_key, p, d, s):
            flash("Source updated.")
        else:
            flash("Failed to update source.")

        return redirect(url_for("market.show_sources"))

    return render_template("update_source.html", source=s)


@market_bp.route("/market/sources/<int:source_id>/update", methods=["POST"])
def update_source(source_id):
    """Updates all entries in the source."""

    all_assets = market.get_assets_from_source(source_id)

    source = market.get_source_by_id(source_id)

    flash("Database updated.")

    for asset in all_assets:
        asset_id = asset["asset_id"]

        if source["supports_prices"]:
            if not market.insert_prices(asset_id):
                flash(f"No prices for {asset["asset_name"]}.")

        if source["supports_dividends"]:
            if not market.insert_dividends(asset_id):
                flash(f"No dividends for {asset["asset_name"]}.")

        if source["supports_stock_splits"]:
            if not market.insert_stock_splits(asset_id):
                flash(f"No stock splits for {asset["asset_name"]}.")

    return redirect(url_for("market.show_sources"))


@market_bp.route("/market/dividends/add/<int:asset_id>", methods=["POST"])
def add_dividends(asset_id):

    if market.insert_dividends(asset_id):
        flash("Dividends added.")

    else:
        flash("Failed to load dividends.")

    return redirect(url_for("market.get_dividends"))


@market_bp.route("/market/dividends")
def get_dividends():
    """Get dividends for assets."""

    a = assets.get_all_assets()

    if not a:
        flash("Must add asset first.")
        return redirect(url_for("assets.add"))

    return render_template("get_dividends.html", assets=a)


@market_bp.route("/market/dividends/delete/<int:asset_id>", methods=["POST"])
def delete_dividends(asset_id):
    """Delete dividends for asset."""

    if market.delete_dividends(asset_id):
        flash("Dividends deleted.")
    else:
        flash("Failed to delete dividends.")

    return redirect(url_for("market.get_dividends"))


@market_bp.route("/market/dividends/<int:asset_id>")
def show_dividends(asset_id):
    """Show dividends for asset."""

    divs = market.get_dividends(asset_id)

    if divs:
        return render_template("show_dividends.html", dividends=divs)

    flash("No dividends to show.")
    return redirect(url_for("market.get_dividends"))


@market_bp.route("/market/prices/add/<int:asset_id>", methods=["POST"])
def add_prices(asset_id):
    """Insert prices for asset."""

    if market.insert_prices(asset_id):
        flash("Prices added.")
    else:
        flash("Failed to add prices.")

    return redirect(url_for("market.get_prices"))


@market_bp.route("/market/prices/delete/<int:asset_id>", methods=["POST"])
def delete_prices(asset_id):
    """Deletes prices from asset."""

    if market.delete_prices(asset_id):
        flash("Prices deleted.")
    else:
        flash("Failed to delete prices.")

    return redirect(url_for("market.get_prices"))


@market_bp.route("/market/prices")
def get_prices():
    """Get prices for assets."""

    a = assets.get_all_assets()

    if not a:
        flash("Must add asset first.")
        return redirect(url_for("assets.add"))

    return render_template("get_prices.html", assets=a)


@market_bp.route("/market/prices/<int:asset_id>")
def show_prices(asset_id):
    """Show prices for asset."""

    p = market.get_prices(asset_id)

    data = json.dumps([price["unit_price"] for price in p])
    labels = json.dumps([price["date"] for price in p])

    a = assets.get_asset(asset_id)

    asset_name = json.dumps(a["asset_name"])

    if p:
        return render_template(
            "show_prices.html", data=data, labels=labels, asset_name=asset_name
        )

    flash("No prices to show.")
    return redirect(url_for("market.get_prices"))


####### Stock splits routes #######


@market_bp.route("/market/splits/add/<int:asset_id>", methods=["POST"])
def add_splits(asset_id):
    """Insert splits for asset."""

    if market.insert_stock_splits(asset_id):
        flash("Splits added.")
    else:
        flash("Failed to add splits.")

    return redirect(url_for("market.get_splits"))


@market_bp.route("/market/splits/<int:asset_id>", methods=["POST"])
def delete_splits(asset_id):
    """Deletes stock splits from asset."""

    if market.delete_stock_splits(asset_id):
        flash("Splits deleted.")
    else:
        flash("No splits to delete.")

    return redirect(url_for("market.get_splits"))


@market_bp.route("/market/splits")
def get_splits():
    """Get splits for assets."""

    a = assets.get_all_assets()

    if not a:
        flash("Must add asset first.")
        return redirect(url_for("assets.add"))

    return render_template("get_splits.html", assets=a)


@market_bp.route("/market/splits/<int:asset_id>")
def show_splits(asset_id):
    """Show stock splits for asset."""

    s = market.get_stock_splits(asset_id)

    if s:
        return render_template("show_splits.html", splits=s)

    flash("No splits to show.")
    return redirect(url_for("market.get_splits"))
