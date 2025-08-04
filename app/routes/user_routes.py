from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from app.services.user_service import get_user_by_id
from app.forms.balance_form import BalanceForm
from app.services.order_service import get_orders_by_user_with_review_flags
from app.services.review_service import get_reviews_by_user

user_bp = Blueprint('user', __name__, url_prefix='/user')

# Vartotojo PROFILIS su užsakymais (profile.html)
@user_bp.route('/profile')
@login_required
def profile():
    user = current_user
    orders = get_orders_by_user_with_review_flags(user.id)
    return render_template(
        'user/profile.html',
        user=user,
        orders=orders
    )

# BALANSO peržiūra ir forma (tik GET)
@user_bp.route('/balance', methods=['GET'])
@login_required
def balance():
    user = get_user_by_id(current_user.id)
    form = BalanceForm()
    return render_template(
        "user/balance.html",
        form=form,
        user=user,
        stripe_publishable_key=current_app.config.get('STRIPE_PUBLISHABLE_KEY')
    )

# Užsakymai (atskirame puslapyje, jei reikia)
@user_bp.route('/orders')
@login_required
def orders():
    orders = get_orders_by_user_with_review_flags(current_user.id)
    return render_template("order/order.html", orders=orders)

# Atsiliepimai
@user_bp.route('/reviews')
@login_required
def reviews():
    reviews = get_reviews_by_user(current_user.id)
    return render_template("review/review.html", reviews=reviews, user_mode=True)