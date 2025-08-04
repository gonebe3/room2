from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.forms.order_form import OrderForm
from app.services.order_service import (
    get_all_orders,
    get_order_by_id,
    get_orders_by_user,
    create_order,
    update_order_status,
    delete_order,
)
from app.services.cart_service import (
    get_cart_items,
    calculate_cart_totals,
    clear_cart,
    get_cart_summary
)
from app.services.discount_service import validate_discount_code 

order_bp = Blueprint('order', __name__, url_prefix='/orders')

def admin_required(func):
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, "is_admin", False):
            flash("Prieiga tik administratoriams.", "danger")
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return decorated_view

# --- Vartotojo užsakymų sąrašas ---
@order_bp.route('/')
@login_required
def user_orders():
    orders = get_orders_by_user(current_user.id)
    return render_template('order/order.html', orders=orders)

# --- Vieno užsakymo detali peržiūra ---
@order_bp.route('/<int:order_id>')
@login_required
def order_detail(order_id):
    order = get_order_by_id(order_id)
    if not order or (order.user_id != current_user.id and not getattr(current_user, "is_admin", False)):
        flash("Jūs neturite prieigos prie šio užsakymo.", "danger")
        return redirect(url_for('order.user_orders'))
    return render_template('order/order_detail.html', order=order)

# --- Užsakymo sukūrimas (CHECKOUT) ---
@order_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = get_cart_items(current_user.id)
    if not cart_items:
        flash("Jūsų krepšelis tuščias.", "warning")
        return redirect(url_for('cart.view_cart'))

    form = OrderForm()
    # Įvertiname be kodo arba pagal pateiktą kodą, jei jau buvo POST
    if form.is_submitted():
        action = request.form.get('action')
        summary = get_cart_summary(cart_items, form.discount_code.data.strip() or None)
        form.total_price.data = summary['total_final']

        if action == 'apply':
            if summary['error']:
                flash(summary['error'], 'danger')
            # tiesiog persiųstame su atnaujinta suvestine
            return render_template('order/checkout.html',
                                   form=form,
                                   cart_items=cart_items,
                                   summary=summary)

        elif action == 'confirm' and form.validate():
            # patvirtiname užsakymą
            if summary['error']:
                flash(summary['error'], 'danger')
                return render_template('order/checkout.html',
                                       form=form,
                                       cart_items=cart_items,
                                       summary=summary)

            order, error = create_order(
                user_id=current_user.id,
                cart_items=cart_items,
                total_amount=summary['total_final'],
                shipping_address=form.shipping_address.data,
                notes=None,
                created_by=current_user.id,
                discount_id=(summary['discount_obj'].id if summary['discount_obj'] else None)
            )
            if order:
                clear_cart(current_user.id)
                flash("Užsakymas sukurtas!", "success")
                return redirect(url_for('order.user_orders'))
            else:
                flash(error or "Klaida kuriant užsakymą.", "danger")
            # po klaidos – krentu žemyn, render ilgesnės formos

    else:
        # GET metodas
        summary = get_cart_summary(cart_items, None)
        form.total_price.data = summary['total_final']

    return render_template('order/checkout.html',
                           form=form,
                           cart_items=cart_items,
                           summary=summary)
# --- ADMIN ---
@order_bp.route('/all')
@login_required
@admin_required
def all_orders():
    orders = get_all_orders()
    return render_template('admin/orders.html', orders=orders)

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