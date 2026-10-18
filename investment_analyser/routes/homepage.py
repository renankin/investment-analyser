from flask import Blueprint, render_template

from investment_analyser.portfolio_analysis.services.portfolio_distribution import (
    get_asset_allocation,
    get_sector_distribution,
)

homepage_bp = Blueprint("homepage", __name__, template_folder="templates")


@homepage_bp.route("/")
def index():
    """Dashboard for the app."""

    return render_template(
        "dashboard.html",
        portfolio_df=get_asset_allocation(),
        sector_distribution=get_sector_distribution(),
    )
