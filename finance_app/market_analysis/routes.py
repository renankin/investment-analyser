from flask import Blueprint, flash, redirect, render_template, request, url_for

from finance_app.assets import assets
from finance_app.market.fetchers.yfinance_fetcher import YFetcher
from finance_app.market_analysis import table_formatter

market_analysis_bp = Blueprint("market_analysis", __name__, template_folder="templates")


@market_analysis_bp.route("/market-analysis/compare-etfs")
def compare_etfs():
    """Compares the ETF saved in the watchlist."""

    all_etfs = []
    for asset in assets.get_all_assets():
        if asset["asset_type"] == "ETF":
            all_etfs.append(table_formatter.format_etf_table(asset["asset_symbol"]))

    return render_template("compare_etf.html", all_etfs=all_etfs)


@market_analysis_bp.route("/market-analysis/watchlist/search")
def search_etf():
    """Searches ETF in yfinance and adds them to watchlist."""

    ticker = request.args.get("ticker")
    if ticker:
        fetcher = YFetcher(ticker)
        if fetcher.is_etf():
            rows = table_formatter.format_etf_table(fetcher.get_info("symbol"))

            return render_template(
                "search_etf.html", symbol=fetcher.get_info("symbol"), rows=rows
            )

        flash("Failed to load fund data.")

    return render_template("search_etf.html")
