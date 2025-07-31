from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.user_service import (
    get_user_by_id,
    get_user_orders,
    update_user_balance,
)
from app.services.order_service import get_orders_by_user
from app.services.review_service import get_reviews_by_user
from app.forms.balance_form import BalanceForm

user_bp = Blueprint('user', __name__, url_prefix='/user')

# Vartotojo profilis su užsakymais (tinka tavo profile.html)
@user_bp.route('/profile')
@login_required
def profile():
    user = current_user
    orders = get_orders_by_user(user.id)
    orders_for_template = []
    for order in orders:
        orders_for_template.append({
            "id": order.id,
            "date": order.created_on,
            "total_items": sum(item.quantity for item in order.order_items),
            "total_price": float(order.total_amount),
            "status": order.status,
        })
    # Pridėk print debug:
    print("DEBUG: orders_for_template", orders_for_template)
    return render_template(
        'user/profile.html',
        user=user,
        orders=orders_for_template   # <- svarbiausia
    )

# Balanso papildymas
@user_bp.route('/balance', methods=['GET', 'POST'])
@login_required
def balance():
    user = get_user_by_id(current_user.id)
    form = BalanceForm()
    if form.validate_on_submit():
        amount = form.amount.data
        success = update_user_balance(current_user.id, amount)
        if success:
            flash("Balansas papildytas.", "success")
        else:
            flash("Klaida pildant balansą.", "danger")
        return redirect(url_for("user.balance"))
    return render_template("user/balance.html", form=form, user=user)

# Vartotojo užsakymai (jei nori atskiro puslapio)
@user_bp.route('/orders')
@login_required
def orders():
    orders = get_orders_by_user(current_user.id)
    return render_template("order/order.html", orders=orders)

# Vartotojo atsiliepimai
@user_bp.route('/reviews')
@login_required
def reviews():
    reviews = get_reviews_by_user(current_user.id)
    return render_template("review/review.html", reviews=reviews, user_mode=True)