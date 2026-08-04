from flask import Blueprint, flash, json, request, render_template

from finance_app.accounts import accounts
from finance_app.assets import assets
from finance_app.analysis import roi, capital_evolution

analysis_bp = Blueprint("analysis", __name__, template_folder="templates")


@analysis_bp.route("/analysis/return")
def show_return():
    """Displays the return on investiment for each asset own."""

    a = roi.get_all_return()

    if not a:
        flash("No data to show.")

    return render_template("show_return.html", assets=a)


@analysis_bp.route("/analysis/evolution")
def portfolio_evolution():
    """Plots the portfolio evolution accross all accounts and assets."""

    account_id = request.args.get("account_id")
    asset_id = request.args.get("asset_id")

    if account_id:
        hist = capital_evolution.get_account_history(account_id)
        title_label = accounts.get_account(account_id)["account_name"]
    elif asset_id:
        hist = capital_evolution.get_asset_history(asset_id)
        title_label = assets.get_asset(asset_id)["asset_name"]
    else:
        hist = capital_evolution.get_all_accounts_history()
        title_label = "All accounts"

    if hist.empty:
        flash("No data to show.")

    index = json.dumps(hist.index.tolist())
    values = json.dumps(hist.values.tolist())
    title = json.dumps(title_label)

    return render_template(
        "plot_evolution.html",
        labels=index,
        data=values,
        title=title,
        accounts=accounts.get_all_accounts(),
        assets=assets.get_all_assets(),
    )
