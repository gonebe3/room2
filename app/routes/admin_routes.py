from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.forms.product_form import ProductForm
from app.forms.admin_user_form import AdminUserForm
from app.forms.category_form import CategoryForm
from app.forms.admin_order_form import AdminOrderForm


# PRIDĖTA – order CRUD forma (jei dar neturi, sukurk kaip admin_order_form.py)

# PRIDĖTA – order servisai
from app.services.order_service import (
    get_all_orders, get_order_by_id, 
    update_order_status, delete_order
)

from app.services.order_service import create_order as order_service_create_order


from app.services.product_service import (
    get_all_products, get_product_by_id, create_product,
    update_product, deactivate_product, update_product_quantity, delete_product
)
from app.services.user_service import (
    get_all_users, get_user_by_id, admin_create_user,
    admin_update_user, delete_user
)
from app.services.category_service import (
    get_all_categories, get_category_by_id, create_category,
    update_category, delete_category
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# --- Universalus admin dekoratorius ---
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
        "categories_count": len(get_all_categories()),  
        "products_count": len(get_all_products()),
        "orders_count": len(get_all_orders()),
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

@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash("Vartotojas nerastas.", "danger")
        return redirect(url_for('admin.user_list'))
    return render_template('admin/users/detail.html', user=user)

# --- PRODUCTS CRUD ---
@admin_bp.route('/products')
@login_required
@admin_required
def product_list():
    products = get_all_products()
    return render_template('admin/products/list.html', products=products)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    form = ProductForm()
    categories = get_all_categories()
    form.category.choices = [(cat.id, cat.name) for cat in categories]
    if form.validate_on_submit():
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
        product = create_product(form, upload_folder)
        if product:
            flash('Prekė pridėta sėkmingai.', 'success')
            return redirect(url_for('admin.product_list'))
        flash('Klaida pridedant prekę.', 'danger')
    return render_template('admin/products/add.html', form=form)

@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash('Prekė nerasta.', 'danger')
        return redirect(url_for('admin.product_list'))
    form = ProductForm(obj=product)
    categories = get_all_categories()
    form.category.choices = [(cat.id, cat.name) for cat in categories]
    if request.method == 'GET':
        form.category.data = product.category_id
    if form.validate_on_submit():
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
        updated = update_product(product, form, upload_folder)
        if updated:
            flash('Prekė atnaujinta.', 'success')
            return redirect(url_for('admin.product_list'))
        flash('Klaida atnaujinant prekę.', 'danger')
    return render_template('admin/products/edit.html', form=form, product=product)

@admin_bp.route('/products/<int:product_id>')
@login_required
@admin_required
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash('Prekė nerasta.', 'danger')
        return redirect(url_for('admin.product_list'))
    return render_template('admin/products/detail.html', product=product)

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

# --- CATEGORIES CRUD ---
@admin_bp.route('/categories')
@login_required
@admin_required
def category_list():
    categories = get_all_categories()
    return render_template('admin/categories/list.html', categories=categories)

@admin_bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category, error = create_category(form)
        if category:
            flash('Kategorija sėkmingai sukurta.', 'success')
            return redirect(url_for('admin.category_list'))
        else:
            flash(error or 'Klaida kuriant kategoriją.', 'danger')
    return render_template('admin/categories/add.html', form=form)

@admin_bp.route('/categories/edit/<int:cat_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(cat_id):
    category = get_category_by_id(cat_id)
    if not category:
        flash('Kategorija nerasta.', 'danger')
        return redirect(url_for('admin.category_list'))
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        updated = update_category(category, form)
        if updated:
            flash('Kategorija atnaujinta.', 'success')
            return redirect(url_for('admin.category_list'))
        else:
            flash('Klaida atnaujinant kategoriją.', 'danger')
    return render_template('admin/categories/edit.html', form=form, category=category)

@admin_bp.route('/categories/delete/<int:cat_id>', methods=['POST'])
@login_required
@admin_required
def delete_category_route(cat_id):
    category = get_category_by_id(cat_id)
    if not category:
        flash('Kategorija nerasta.', 'danger')
    elif delete_category(category):
        flash('Kategorija ištrinta.', 'success')
    else:
        flash('Klaida trinant kategoriją.', 'danger')
    return redirect(url_for('admin.category_list'))

# --- ADMIN ORDERS CRUD (nauji, papildomi maršrutai) ---

# --- ORDERS CRUD (profesionaliai, visi endpoint'ai suderinti) ---

@admin_bp.route('/orders')
@login_required
@admin_required
def order_list():
    """Rodo visų užsakymų sąrašą"""
    orders = get_all_orders()
    return render_template('admin/orders/list.html', orders=orders)


@admin_bp.route('/orders/<int:order_id>')
@login_required
@admin_required
def order_detail(order_id):
    """Rodo užsakymo detales"""
    order = get_order_by_id(order_id)
    if not order:
        flash("Užsakymas nerastas.", "danger")
        return redirect(url_for('admin.order_list'))
    return render_template('admin/orders/detail.html', order=order)

@admin_bp.route('/orders/edit/<int:order_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_order(order_id):
    """Redaguoja užsakymą"""
    order = get_order_by_id(order_id)
    if not order:
        flash("Užsakymas nerastas.", "danger")
        return redirect(url_for('admin.order_list'))
    form = AdminOrderForm(obj=order)
    users = get_all_users()
    form.user_id.choices = [(u.id, f"{u.username} ({u.email})") for u in users]
    if form.validate_on_submit():
        success = update_order_status(order_id, form.status.data, modified_by=current_user.id)
        if success:
            flash("Užsakymo statusas atnaujintas.", "success")
            return redirect(url_for('admin.order_detail', order_id=order_id))
        else:
            flash("Klaida atnaujinant užsakymą.", "danger")
    return render_template('admin/orders/edit.html', form=form, order=order)

@admin_bp.route('/orders/delete/<int:order_id>', methods=['POST'])
@login_required
@admin_required
def delete_order_route(order_id):
    """Ištrina užsakymą"""
    success = delete_order(order_id)
    if success:
        flash('Užsakymas ištrintas.', 'success')
    else:
        flash('Klaida trinant užsakymą.', 'danger')
    return redirect(url_for('admin.order_list'))
# --- SENAS (placeholder) orders route išsaugotas, jeigu reikės redirectų suderinimui ---

@admin_bp.route('/orders')
def orders():
    """
    Rodo visų užsakymų sąrašą administratoriaus panelėje.
    Užsakymai paimami per service sluoksnį.
    """
    try:
        orders = get_all_orders()
    except Exception as e:
        orders = []
        flash("Nepavyko užkrauti užsakymų iš duomenų bazės.", "danger")
    return render_template('admin/orders/list.html', orders=orders)

@admin_bp.route('/discounts')
@login_required
@admin_required
def discounts():
    # Placeholder. Vėliau bus nuolaidų CRUD
    return render_template('admin/discounts.html')