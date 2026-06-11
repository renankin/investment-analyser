from flask import Blueprint, flash, json, redirect, request, render_template, url_for

from finance_app.accounts import accounts
from finance_app.assets import assets
from finance_app.analysis import roi, capital_evolution
from finance_app.transactions import transactions

analysis_bp = Blueprint("analysis", __name__, template_folder="templates")


@analysis_bp.route("/analysis/return")
def show_return():
    """Displays the return on investiment for each asset own."""

    a = roi.get_all_return()

    if not a:
        flash("No assets to show. Must add asset first.")
        return redirect(url_for("assets.add"))

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

    if not hist.empty:
        index = json.dumps(hist.index.tolist())
        values = json.dumps(hist.values.tolist())
        title = json.dumps(title_label)

        current_value = {"date": hist.index.max(), "value": hist.iloc[-1]}

        return render_template(
            "plot_evolution.html",
            labels=index,
            data=values,
            title=title,
            current_value=current_value,
            accounts=accounts.get_all_accounts(),
            assets=assets.get_all_assets(),
        )
