from flask import Blueprint, flash, render_template, request

from investment_analyser.market_analysis.services.etfs import (
    get_etf_search_result,
    get_etfs_for_comparison,
)

market_analysis_bp = Blueprint("market_analysis", __name__, template_folder="templates")


@market_analysis_bp.route("/market-analysis/compare-etfs")
def compare_etfs():
    """Compares the ETF saved in the watchlist."""

    return render_template("compare_etf.html", all_etfs=get_etfs_for_comparison())


@market_analysis_bp.route("/market-analysis/watchlist/search")
def search_etf():
    """Searches ETF in yfinance and adds them to watchlist."""

    ticker = request.args.get("ticker")
    if ticker:
        result = get_etf_search_result(ticker)
        if result:
            return render_template("search_etf.html", symbol=ticker, rows=result)

        flash("Failed to load fund data.")

    return render_template("search_etf.html")
