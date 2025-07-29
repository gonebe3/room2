from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.forms.product_form import ProductForm
from app.forms.admin_user_form import AdminUserForm
from app.services.product_service import (
    get_all_products, get_product_by_id, create_product,
    update_product, deactivate_product, update_product_quantity, delete_product
)
from app.services.user_service import (
    get_all_users, get_user_by_id, admin_create_user,
    admin_update_user, delete_user
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# --- ADMIN ONLY DECORATOR ---
def admin_required(func):
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, "is_admin", False):
            flash("Prieiga tik administratoriams.", "danger")
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return decorated_view

# --- DASHBOARD ---
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    stats = {
        "users_count": len(get_all_users()),
        "products_count": len(get_all_products()),
        "orders_count": 0,           # TODO: pridėti užsakymų count
        "discounts_count": 0,        # TODO: pridėti nuolaidų count
        "today_sales_count": 0,      # TODO: parduota šiandien
        "month_revenue": 0,          # TODO: mėnesio apyvarta €
        "top_product_name": "-",     # TODO: populiariausia prekė
        "top_client_name": "-"       # TODO: geriausias klientas
    }
    return render_template('admin/dashboard.html', stats=stats)

# --- USERS CRUD ---

@admin_bp.route('/users')
@login_required
@admin_required
def user_list():
    users = get_all_users()
    return render_template('admin/users/list.html', users=users)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    form = AdminUserForm()
    if form.validate_on_submit():
        user, error = admin_create_user(form)
        if user:
            flash('Vartotojas sukurtas sėkmingai.', 'success')
            return redirect(url_for('admin.user_list'))
        else:
            flash(error or 'Klaida kuriant vartotoją.', 'danger')
    return render_template('admin/users/add.html', form=form)

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash('Vartotojas nerastas.', 'danger')
        return redirect(url_for('admin.user_list'))
    form = AdminUserForm(obj=user)
    if form.validate_on_submit():
        data = form.data.copy()
        if not form.password.data:
            data.pop('password', None)
        else:
            user.set_password(form.password.data)
        data.pop('csrf_token', None)
        data.pop('submit', None)
        success = admin_update_user(user_id, data)
        if success:
            flash("Vartotojo duomenys atnaujinti.", "success")
        else:
            flash("Klaida atnaujinant vartotoją.", "danger")
        return redirect(url_for('admin.user_list'))
    return render_template('admin/users/edit.html', form=form, user=user)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user_route(user_id):
    success = delete_user(user_id)
    if success:
        flash('Vartotojas ištrintas.', 'success')
    else:
        flash('Klaida šalinant vartotoją.', 'danger')
    return redirect(url_for('admin.user_list'))

# --- PRODUCTS LIST ---
@admin_bp.route('/products')
@login_required
@admin_required
def product_list():
    products = get_all_products()
    return render_template('admin/product_list.html', products=products)

# --- ADD PRODUCT ---
@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
        product = create_product(form, upload_folder)
        if product:
            flash('Prekė pridėta sėkmingai.', 'success')
            return redirect(url_for('admin.product_list'))
        flash('Klaida pridedant prekę.', 'danger')
    return render_template('admin/add_product.html', form=form)

# --- EDIT PRODUCT ---
@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash('Prekė nerasta.', 'danger')
        return redirect(url_for('admin.product_list'))
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
        updated = update_product(product, form, upload_folder)
        if updated:
            flash('Prekė atnaujinta.', 'success')
            return redirect(url_for('admin.product_list'))
        flash('Klaida atnaujinant prekę.', 'danger')
    return render_template('admin/edit_product.html', form=form, product=product)

# --- DEACTIVATE PRODUCT (SOFT DELETE) ---
@admin_bp.route('/products/deactivate/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def deactivate_product_route(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash('Prekė nerasta.', 'danger')
    elif deactivate_product(product):
        flash('Prekė išimta iš prekybos.', 'info')
    else:
        flash('Klaida išimant prekę.', 'danger')
    return redirect(url_for('admin.product_list'))

# --- UPDATE QUANTITY ---
@admin_bp.route('/products/update_quantity/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def update_product_quantity_route(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash('Prekė nerasta.', 'danger')
    else:
        try:
            quantity = int(request.form.get('quantity', 0))
            if quantity < 0:
                raise ValueError
            if update_product_quantity(product, quantity):
                flash('Kiekis atnaujintas.', 'success')
            else:
                flash('Klaida atnaujinant kiekį.', 'danger')
        except ValueError:
            flash('Neteisingas kiekis.', 'danger')
    return redirect(url_for('admin.product_list'))

# --- DELETE PRODUCT (HARD DELETE) ---
@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def delete_product_route(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash('Prekė nerasta.', 'danger')
    elif delete_product(product):
        flash('Prekė ištrinta.', 'success')
    else:
        flash('Klaida trinant prekę.', 'danger')
    return redirect(url_for('admin.product_list'))

# --- PRODUCTS STATS PAGE (EXAMPLE) ---
@admin_bp.route('/products/stats')
@login_required
@admin_required
def product_stats():
    # TODO: Implement real statistics
    return render_template('admin/product_stats.html')

# --- ORDERS PAGE (EXAMPLE) ---
@admin_bp.route('/orders')
@login_required
@admin_required
def orders():
    # TODO: Implement real order list
    return render_template('admin/orders.html')

# --- DISCOUNTS PAGE (EXAMPLE) ---
@admin_bp.route('/discounts')
@login_required
@admin_required
def discounts():
    # TODO: Implement real discounts management
    return render_template('admin/discounts.html')

@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash("Vartotojas nerastas.", "danger")
        return redirect(url_for('admin.user_list'))
    return render_template('admin/users/detail.html', user=user)