import csv
import pandas as pd
from pathlib import Path
import time
import requests
import os


CSV_FILE = "instance/tesouro_direto.csv"


def save_prices():
    """Access "Tesouro Transparente" portal to fetch bond prices
    and save in a local csv file."""

    url = (
        "https://www.tesourotransparente.gov.br/ckan/dataset/"
        "df56aa42-484a-4a59-8184-7676580c81e3/resource/"
        "796d2059-14e9-44e3-80c9-2d9e30b405c1/download/"
        "precotaxatesourodireto.csv"
    )

    r = requests.get(url)

    r.raise_for_status()

    with open(CSV_FILE, "w") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "bond_name",
                "due_date",
                "base_date",
                "purchase_rate",
                "sell_rate",
                "purchase_price",
                "sell_price",
                "base_price",
            ],
        )

        writer.writeheader()

        i = 0
        for line in r.iter_lines():
            items = line.decode("utf-8").split(";")

            if i > 0:  # Skip header
                writer.writerow(
                    {
                        "bond_name": items[0],
                        "due_date": items[1],
                        "base_date": items[2],
                        "purchase_rate": items[3].replace(",", "."),
                        "sell_rate": items[4].replace(",", "."),
                        "purchase_price": items[5].replace(",", "."),
                        "sell_price": items[6].replace(",", "."),
                        "base_price": items[7].replace(",", "."),
                    }
                )

            i += 1


def get_prices(bond_symbol: str) -> pd.Series:
    """Returns as pandas Series indexed to `date` and named `prices`"""

    if os.path.exists(CSV_FILE):
        # Check if file has been updated today
        if Path(CSV_FILE).stat().st_mtime < time.time() - 86400:
            save_prices()

        df = pd.read_csv(CSV_FILE, parse_dates=[1, 2], date_format="%d/%m/%Y")

        df["bond_symbol"] = df["bond_name"] + " " + df["due_date"].dt.year.astype(str)

        df_filtered = df[df["bond_symbol"] == bond_symbol]

        if df_filtered.empty:
            return pd.Series()

        df_filtered.rename(
            columns={"base_date": "date", "sell_price": "price"}, inplace=True
        )

        df_filtered.set_index("date", inplace=True)

        return df_filtered["price"]
        

    else:
        save_prices()
        get_prices(bond_symbol)
