## About

`investment_analyser` is a local web app written in Python with Flask for tracking investments across multiple accounts. It supports stocks, ETFs, and Brazilian government bonds.

The app can fetch market data on request: stock and ETF data from `yfinance`, and Brazilian government bond prices from Tesouro Direto. Retrieved data is stored in a local SQLite database under `instance/`; portfolio values are based on the latest prices saved there.

## How to run it

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the requirements:

```bash
python -m pip install -r requirements.txt
```

Initialize the database schema (once for each new database):

```bash
flask --app app init-db
```

Start the Flask development server:

```bash
flask --app app run
```

## Application structure

The application package is organized by architectural layer:

* `app/models/` defines the application data models.
* `app/services/` contains business logic.
* `app/repository/` contains database access and repositories.
* `app/routes/` defines the Flask routes and blueprints.
* `app/templates/` contains the Jinja templates used by the routes.
* `app/db/` contains database connection and schema setup.
* `app/fetchers/` contains integrations for fetching external market data.

The Flask application factory is `create_app()` in `app/__init__.py`. The SQLite database is created in the `instance/` directory.

## Current functionalities

* Create and manage accounts, assets, and buy/sell transactions; transactions can be edited or deleted.
* View a portfolio dashboard with holdings, latest saved prices, valuations, allocation weights, and sector distribution.
* Fetch and save historical prices for stocks, ETFs, and Brazilian government bonds; fetch stock dividends and splits.
* View transaction, price, split, and dividend histories. Stock splits are applied when calculating adjusted holdings.
* Analyze asset returns using absolute ROI and annualized IRR, including sales, dividends, and the current value of open positions.
* Plot portfolio value over time for all accounts, an individual account, or an asset.
* Search for ETFs and compare ETFs in the portfolio using available fund details, historical performance, sector weighting, and top holdings.
