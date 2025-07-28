from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.forms.product_form import ProductForm
from app.services.product_service import (
    get_all_products, get_product_by_id, create_product,
    update_product, deactivate_product, update_product_quantity, delete_product
)

admin_bp = Blueprint('custom_admin', __name__, url_prefix='/admin')

# Universalus admin dekoratorius – tik adminams
def admin_required(func):
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, "is_admin", False):
            flash("Prieiga tik administratoriams.", "danger")
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return decorated_view

# Visų prekių sąrašas (admino valdymas)
@admin_bp.route('/products')
@login_required
@admin_required
def product_list():
    products = get_all_products()
    return render_template('admin/product_list.html', products=products)

# Naujos prekės pridėjimas
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

# Esamos prekės redagavimas
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

# Prekės deaktyvavimas (minkštas išėmimas iš prekybos)
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

# Kiekio atnaujinimas (formoje quantity laukelis)
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

# Produktas trinamas (hard delete)
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

# (Pavyzdys) Vartotojų sąrašas (jei reikia admino valdymui)
# from app.services.user_service import get_all_users, delete_user
# @admin_bp.route('/users')
# @login_required
# @admin_required
# def user_list():
#     users = get_all_users()
#     return render_template('admin/user_list.html', users=users)
