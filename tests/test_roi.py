from datetime import date
from decimal import Decimal

from pytest import approx

from investment_analyser.portfolio_analysis.services.roi import Cashflow, calculate_irr


def test_empty_imputs():

    assert calculate_irr([]) is None


def test_positive_irr():

    cashflows = [
        Cashflow(value=Decimal("-1000.00"), date=date(2024, 1, 31)),
        Cashflow(value=Decimal("1100.00"), date=date(2025, 1, 30)),
    ]

    assert calculate_irr(cashflows) == approx(0.10, abs=1e-4)


def test_negative_irr():

    cashflows = [
        Cashflow(value=Decimal("-1000.00"), date=date(2024, 1, 31)),
        Cashflow(value=Decimal("900.00"), date=date(2025, 1, 30)),
    ]

    assert calculate_irr(cashflows) == approx(-0.1, abs=1e-4)


def test_single_cashflow():

    assert (
        calculate_irr([Cashflow(value=Decimal("1100.00"), date=date(2025, 1, 30))])
        == None
    )


def test_all_positive_cashflows():

    cashflows = [
        Cashflow(value=Decimal("1000.00"), date=date(2024, 1, 31)),
        Cashflow(value=Decimal("1100.00"), date=date(2025, 1, 30)),
    ]

    assert calculate_irr(cashflows) == None


def test_all_negative_cashflows():

    cashflows = [
        Cashflow(value=Decimal("-1000.00"), date=date(2024, 1, 31)),
        Cashflow(value=Decimal("-1100.00"), date=date(2025, 1, 30)),
    ]

    assert calculate_irr(cashflows) == None


def test_irregular_cashflows():

    cashflows = [
        Cashflow(value=Decimal("-1000.00"), date=date(2024, 1, 31)),
        Cashflow(value=Decimal("200.00"), date=date(2024, 7, 15)),
        Cashflow(value=Decimal("-300.00"), date=date(2025, 1, 10)),
        Cashflow(value=Decimal("1400.00"), date=date(2025, 12, 20)),
    ]

    assert calculate_irr(cashflows) == approx(0.15, abs=1e-4)


def test_unsorted_cashflows():

    cashflows = [
        Cashflow(value=Decimal("1400.00"), date=date(2025, 12, 20)),
        Cashflow(value=Decimal("-1000.00"), date=date(2024, 1, 31)),
        Cashflow(value=Decimal("-300.00"), date=date(2025, 1, 10)),
        Cashflow(value=Decimal("200.00"), date=date(2024, 7, 15)),
    ]

    assert calculate_irr(cashflows) == approx(0.15, abs=1e-4)


def test_same_day_cashflows():

    cashflows = [
        Cashflow(value=Decimal("-1200.00"), date=date(2024, 1, 31)),
        Cashflow(value=Decimal("200.00"), date=date(2024, 1, 31)),
        Cashflow(value=Decimal("1100.00"), date=date(2025, 1, 30)),
    ]

    assert calculate_irr(cashflows) == approx(0.10, abs=1e-4)


def test_large_irr():

    cashflows = [
        Cashflow(value=Decimal("-1000.00"), date=date(2024, 1, 31)),
        Cashflow(value=Decimal("2000.00"), date=date(2025, 1, 30)),
    ]

    assert calculate_irr(cashflows) == approx(1.0, abs=1e-4)
