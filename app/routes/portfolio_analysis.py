from flask import Blueprint, flash, json, render_template, request

from app.repository.accounts import get_account, get_all_accounts
from app.repository import assets
from app.services import roi
from app.services import capital_evolution

portfolio_analysis_bp = Blueprint("portfolio_analysis", __name__)


@portfolio_analysis_bp.route("/portfolio-analysis/return")
def show_return():
    """Displays the return on investiment for each asset own."""

    a = roi.get_all_return()

    if not a:
        flash("No data to show.")

    return render_template("show_return.html", assets=a)


@portfolio_analysis_bp.route("/portfolio-analysis/evolution")
def portfolio_evolution():
    """Plots the portfolio evolution accross all accounts and assets."""

    account_id = request.args.get("account_id", type=int)
    asset_id = request.args.get("asset_id", type=int)

    if account_id:
        hist = capital_evolution.get_account_history(account_id)
        title_label = get_account(account_id).name
    elif asset_id:
        hist = capital_evolution.get_asset_history(asset_id)
        title_label = assets.get_asset_by_id(asset_id).info.name
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
        accounts=get_all_accounts(),
        assets=assets.get_all_assets(),
    )
