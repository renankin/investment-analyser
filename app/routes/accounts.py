from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.repositories.accounts import (
    create_account,
    get_account,
    get_all_accounts,
    update_account,
)
from app.services.account_service import AccountService

accounts_bp = Blueprint("accounts", __name__, template_folder="../templates/accounts")


@accounts_bp.route("/accounts")
def index():
    """Show all accounts."""

    account_search = request.args.get("search")
    if not account_search:
        account_search = ""

    all_accounts = []
    for account in get_all_accounts():
        if account_search.upper() in account.name.upper():
            all_accounts.append(account)

    return render_template("show_accounts.html", accounts=all_accounts)


@accounts_bp.route("/accounts/add", methods=["GET", "POST"])
def add():
    """Add new account."""

    if request.method == "POST":
        account_name = request.form.get("account_name")
        currency = request.form.get("currency")

        if account_name and currency:
            create_account(account_name, currency)
            flash("Account added.")
        else:
            flash("Failed to create account.")
        return redirect(url_for("accounts.index"))

    return render_template("add_account.html")


@accounts_bp.route("/accounts/<int:account_id>/edit", methods=["POST", "GET"])
def edit(account_id):
    """Edit account."""

    account = get_account(account_id)

    if request.method == "POST":
        account_name = request.form.get("account_name")
        currency = request.form.get("currency")

        if account_name and currency:
            account.name = account_name
            account.currency = currency
            update_account(account)
            flash("Account updated")

        return redirect(url_for("accounts.index"))

    return render_template("edit_account.html", account=account)


@accounts_bp.route("/accounts/<int:account_id>/delete", methods=["POST"])
def delete(account_id):
    account_service = AccountService(account_id)
    if account_service.delete_account():
        flash("Account deleted.")
    else:
        flash("Account not deleted. Must delete its transactions first.")
    return redirect(url_for("accounts.index"))
