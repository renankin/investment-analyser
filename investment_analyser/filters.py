import datetime as dt


def format_currency(value: float, currency: str) -> str:
    """Takes currency input and returns formatted price value"""

    if value is None:
        return "-"

    map = {
        "GBP": "£",
        "BRL": "R$",
        "USD": "$",
    }

    if currency.upper() in map:
        million = 1000000
        billion = 1000000000
        if value < million:
            return f"{map[currency.upper()]}{value:,.2f}"
        elif value > billion:
            return f"{map[currency.upper()]}{round(value / billion)}B"
        else:
            return f"{map[currency.upper()]}{round(value / million)}M"
    else:
        return "-"


def format_date(date):
    """Takes format and format string"""

    return dt.date.strftime(date, "%d/%m/%Y")


def format_percent(fraction: float, in_percent=False) -> str:
    """Returns formated fraction as a string e.g. 0.1%.
    If float is NaN it will return `-` instead"""

    if fraction is None:
        return "-"

    percent = 100
    if in_percent:
        percent = 1

    return f"{round(percent * fraction, 2)}%"
