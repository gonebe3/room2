from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.services.user_service import (
    get_user_by_id,
    update_user_profile,
    get_user_orders,
    get_user_reviews,
    update_user_balance,
)
from app.forms.profile_form import ProfileForm
from app.forms.balance_form import BalanceForm

user_bp = Blueprint('user', __name__, url_prefix='/user')

# Vartotojo profilis
@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = get_user_by_id(current_user.id)
    form = ProfileForm(obj=user)
    if form.validate_on_submit():
        success = update_user_profile(user, form)
        if success:
            flash("Profilis atnaujintas.", "success")
        else:
            flash("Klaida atnaujinant profilį.", "danger")
        return redirect(url_for("user.profile"))
    return render_template("user/profile.html", form=form, user=user)

# Balanso papildymas
@user_bp.route('/balance', methods=['GET', 'POST'])
@login_required
def balance():
    user = get_user_by_id(current_user.id)
    form = BalanceForm()
    if form.validate_on_submit():
        amount = form.amount.data
        success = update_user_balance(user, amount)
        if success:
            flash("Balansas papildytas.", "success")
        else:
            flash("Klaida pildant balansą.", "danger")
        return redirect(url_for("user.balance"))
    return render_template("user/balance.html", form=form, user=user)

# Vartotojo užsakymai
@user_bp.route('/orders')
@login_required
def orders():
    orders = get_user_orders(current_user.id)
    return render_template("order/order.html", orders=orders)

# Vartotojo atsiliepimai
@user_bp.route('/reviews')
@login_required
def reviews():
    reviews = get_user_reviews(current_user.id)
    return render_template("review/review.html", reviews=reviews, user_mode=True)