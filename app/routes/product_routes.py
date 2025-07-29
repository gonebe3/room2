from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.forms.product_form import ProductForm
from app.services.product_service import (
    get_all_products,
    get_product_by_id,
    create_product,
    update_product,
    deactivate_product,
    update_product_quantity,
    delete_product
)
import os


product_bp = Blueprint('product', __name__, url_prefix='/product')

# Produktų sąrašas visiems (pagrindinis katalogas)
@product_bp.route('/')
def product_list():
    products = get_all_products()
    return render_template('product/product_list.html', products=products)

# Vienos prekės detalės (matomas visiems)
@product_bp.route('/<int:product_id>')
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if not product or product.is_deleted or not product.is_active:
        flash('Prekė nerasta.', 'danger')
        return redirect(url_for('product.product_list'))
    return render_template('product/product_detail.html', product=product)

# --- ADMIN VEIKSMAI PER ADMIN BLUEPRINTĄ ---
# Jei reikia, čia galima leisti tik adminams, bet dažniausiai šios funkcijos eina į admin_routes.py

# Produkto pridėjimas (tik adminams)
@product_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if not getattr(current_user, "is_admin", False):
        flash("Prieiga tik administratoriams.", "danger")
        return redirect(url_for('product.product_list'))
    form = ProductForm()
    upload_folder = os.path.join(current_app.root_path, 'static', 'images', 'products')  # <<< PAKEISTA
    if form.validate_on_submit():
        product = create_product(form, upload_folder)  # <<< PAKEISTA
        if product:
            flash('Prekė pridėta sėkmingai.', 'success')
            return redirect(url_for('product.product_list'))
        else:
            flash('Klaida pridedant prekę.', 'danger')
    return render_template('product/add_product.html', form=form)

# Produkto redagavimas (tik adminams)
@product_bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if not getattr(current_user, "is_admin", False):
        flash("Prieiga tik administratoriams.", "danger")
        return redirect(url_for('product.product_list'))
    product = get_product_by_id(product_id)
    if not product:
        flash('Prekė nerasta.', 'danger')
        return redirect(url_for('product.product_list'))
    form = ProductForm(obj=product)
    upload_folder = os.path.join(current_app.root_path, 'static', 'images', 'products')  # <<< PAKEISTA
    if form.validate_on_submit():
        updated = update_product(product, form, upload_folder)  # <<< PAKEISTA
        if updated:
            flash('Prekė atnaujinta.', 'success')
            return redirect(url_for('product.product_list'))
        else:
            flash('Klaida atnaujinant prekę.', 'danger')
    return render_template('product/edit_product.html', form=form, product=product)

# Produkto deaktyvavimas (tik adminams)
@product_bp.route('/deactivate/<int:product_id>', methods=['POST'])
@login_required
def deactivate_product_route(product_id):
    if not getattr(current_user, "is_admin", False):
        flash("Prieiga tik administratoriams.", "danger")
        return redirect(url_for('product.product_list'))
    product = get_product_by_id(product_id)
    if not product:
        flash('Prekė nerasta.', 'danger')
    else:
        if deactivate_product(product):
            flash('Prekė išimta iš prekybos.', 'info')
        else:
            flash('Klaida išimant prekę.', 'danger')
    return redirect(url_for('product.product_list'))

# Produkto kiekio atnaujinimas (tik adminams)
@product_bp.route('/update_quantity/<int:product_id>', methods=['POST'])
@login_required
def update_product_quantity_route(product_id):
    if not getattr(current_user, "is_admin", False):
        flash("Prieiga tik administratoriams.", "danger")
        return redirect(url_for('product.product_list'))
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
    return redirect(url_for('product.product_list'))

# Produkto ištrynimas (tik adminams, jei reikia hard-delete)
@product_bp.route('/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product_route(product_id):
    if not getattr(current_user, "is_admin", False):
        flash("Prieiga tik administratoriams.", "danger")
        return redirect(url_for('product.product_list'))
    product = get_product_by_id(product_id)
    if not product:
        flash('Prekė nerasta.', 'danger')
    else:
        if delete_product(product):
            flash('Prekė ištrinta.', 'success')
        else:
            flash('Klaida trinant prekę.', 'danger')
    return redirect(url_for('product.product_list'))