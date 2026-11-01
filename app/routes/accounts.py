from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.services.account_service import AccountService

accounts_bp = Blueprint("accounts", __name__, template_folder="../templates/accounts")


@accounts_bp.route("/accounts")
def index():
    return render_template(
        "show_accounts.html", accounts=AccountService.get_all_accounts()
    )


@accounts_bp.route("/accounts/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        account_name = request.form.get("account_name")
        currency = request.form.get("currency")

        if account_name and currency:
            AccountService.add_new_account(account_name, currency)
            flash("Account added.")
        else:
            flash("Failed to create account.")
        return redirect(url_for("accounts.index"))

    return render_template("add_account.html")


@accounts_bp.route("/accounts/<int:account_id>/edit", methods=["POST", "GET"])
def edit(account_id):
    account_service = AccountService(account_id)
    if request.method == "POST":
        account_name = request.form.get("account_name")
        currency = request.form.get("currency")
        account_service.edit_account(account_name, currency)
        flash("Account updated")
        return redirect(url_for("accounts.index"))

    return render_template("edit_account.html", account=account_service.account)


@accounts_bp.route("/accounts/<int:account_id>/delete", methods=["POST"])
def delete(account_id):
    if AccountService(account_id).delete_account():
        flash("Account deleted.")
    else:
        flash("Account not deleted. Must delete its transactions first.")
    return redirect(url_for("accounts.index"))
