import os

from flask import Flask

from investment_analyser import db, filters
from investment_analyser.accounts.routes import accounts_bp
from investment_analyser.assets.routes import assets_bp
from investment_analyser.homepage.routes import homepage_bp
from investment_analyser.market.routes import market_bp
from investment_analyser.market_analysis.routes import market_analysis_bp
from investment_analyser.portfolio_analysis.routes import portfolio_analysis_bp
from investment_analyser.transactions.routes import transactions_bp


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, 'transactions.db'),
    )

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

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
