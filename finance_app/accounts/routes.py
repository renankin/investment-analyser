from flask import Blueprint, flash, redirect, request, render_template, url_for

from finance_app.accounts import accounts as accounts
from finance_app.assets import assets as assets

accounts_bp = Blueprint("accounts", __name__, template_folder="templates")


@accounts_bp.route("/accounts")
def index():
    """Show all accounts."""

    a = accounts.get_all_accounts()

    if a:
        return render_template("accounts.html", accounts=a)

    flash("No accounts to show. Must add account first.")
    return redirect(url_for("accounts.add"))


@accounts_bp.route("/accounts/add", methods=["GET", "POST"])
def add():
    """Add new account."""

    if request.method == "POST":
        account_name = request.form.get("account_name")
        currency = request.form.get("currency")

        accounts.insert_account(account_name, currency)
        flash("Account added")
        return redirect(url_for("accounts.index"))

    return render_template("add_account.html")


@accounts_bp.route("/accounts/<int:account_id>/edit", methods=["POST", "GET"])
def edit(account_id):
    """Edit account."""

    account = accounts.get_account(account_id)

    if request.method == "POST":
        account_name = request.form.get("account_name")
        currency = request.form.get("currency")

        accounts.update_account(account_id, account_name, currency)
        flash("Account updated")
        return redirect(url_for("accounts.index"))

    return render_template("edit_account.html", account=account)


@accounts_bp.route("/accounts/<int:account_id>/delete", methods=["POST"])
def delete(account_id):
    """Delete account."""

    a = assets.get_assets(account_id)

    if a:
        flash("Account not deleted. Must delete its transactions first.")
    else:
        accounts.delete_account(account_id)
        flash("Account deleted.")

    return redirect(url_for("accounts.index"))
