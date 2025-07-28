from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.forms.order_form import OrderForm
from app.services.order_service import (
    get_all_orders,
    get_order_by_id,
    get_orders_by_user,     # <-- teisingas pavadinimas!
    create_order,
    update_order_status,
    delete_order
)

order_bp = Blueprint('order', __name__, url_prefix='/orders')

# Tik adminams (jei norite atskirti, naudokite admin blueprint)
def admin_required(func):
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, "is_admin", False):
            flash("Prieiga tik administratoriams.", "danger")
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return decorated_view

# Vartotojo užsakymų sąrašas
@order_bp.route('/')
@login_required
def user_orders():
    orders = get_orders_by_user(current_user.id)   # <-- PATAISYTA!
    return render_template('order/order.html', orders=orders)

# Vieno užsakymo detali peržiūra (vartotojui)
@order_bp.route('/<int:order_id>')
@login_required
def order_detail(order_id):
    order = get_order_by_id(order_id)
    if not order or (order.user_id != current_user.id and not getattr(current_user, "is_admin", False)):
        flash("Jūs neturite prieigos prie šio užsakymo.", "danger")
        return redirect(url_for('order.user_orders'))
    return render_template('order/order_detail.html', order=order)

# Užsakymo sukūrimas (checkout)
@order_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_new_order():
    form = OrderForm()
    if form.validate_on_submit():
        success, error = create_order(current_user.id, form)
        if success:
            flash("Užsakymas sukurtas!", "success")
            return redirect(url_for('order.user_orders'))
        else:
            flash(error or "Klaida kuriant užsakymą.", "danger")
    return render_template('order/checkout.html', form=form)

# --- ADMIN ROUTES ---

# Visų užsakymų sąrašas (ADMIN)
@order_bp.route('/all')
@login_required
@admin_required
def all_orders():
    orders = get_all_orders()
    return render_template('admin/orders.html', orders=orders)

# Užsakymo statuso keitimas (ADMIN)
@order_bp.route('/update_status/<int:order_id>', methods=['POST'])
@login_required
@admin_required
def update_order_status_route(order_id):
    status = request.form.get('status')
    success = update_order_status(order_id, status)
    if success:
        flash('Užsakymo statusas atnaujintas.', 'success')
    else:
        flash('Klaida atnaujinant statusą.', 'danger')
    return redirect(url_for('order.all_orders'))

# Užsakymo ištrynimas (ADMIN)
@order_bp.route('/delete/<int:order_id>', methods=['POST'])
@login_required
@admin_required
def delete_order_route(order_id):
    success = delete_order(order_id)
    if success:
        flash('Užsakymas ištrintas.', 'success')
    else:
        flash('Klaida trinant užsakymą.', 'danger')
    return redirect(url_for('order.all_orders'))