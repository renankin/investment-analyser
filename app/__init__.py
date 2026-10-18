import os

from flask import Flask

from app import filters
from app.db import connection
from app.routes.accounts import accounts_bp
from app.routes.assets import assets_bp
from app.routes.homepage import homepage_bp
from app.routes.market_analysis import market_analysis_bp
from app.routes.market_data import market_bp
from app.routes.portfolio_analysis import portfolio_analysis_bp
from app.routes.transactions import transactions_bp


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, 'transactions.db'),
    )

    os.makedirs(app.instance_path, exist_ok=True)

    connection.init_app(app)

    app.jinja_env.filters["format_currency"] = filters.format_currency
    app.jinja_env.filters["format_date"] = filters.format_date
    app.jinja_env.filters["format_percent"] = filters.format_percent

    app.register_blueprint(accounts_bp)
    app.register_blueprint(portfolio_analysis_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(homepage_bp)
    app.register_blueprint(market_bp)
    app.register_blueprint(market_analysis_bp)
    app.register_blueprint(transactions_bp)

    return app
