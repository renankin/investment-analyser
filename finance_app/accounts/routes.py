from flask import Blueprint, flash, redirect, render_template, request, url_for

from finance_app.accounts import accounts

accounts_bp = Blueprint("accounts", __name__, template_folder="templates")


@accounts_bp.route("/accounts")
def index():
    """Show all accounts."""

    account_search = request.args.get("search")
    if not account_search:
        account_search = ""

    all_accounts = []
    for account in accounts.get_all_accounts():
        if account_search.upper() in account["account_name"].upper():
            all_accounts.append(account)

    return render_template("show_accounts.html", accounts=all_accounts)


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

    a = accounts.get_assets(account_id)

    if a:
        flash("Account not deleted. Must delete its transactions first.")
    else:
        accounts.delete_account(account_id)
        flash("Account deleted.")

    return redirect(url_for("accounts.index"))
