from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.forms.discount_form import DiscountForm
from app.services.discount_service import (
    get_all_discounts,
    get_discount_by_id,
    create_discount,
    update_discount,
    delete_discount,
    activate_discount,
    deactivate_discount
)

# Sukuriame blueprintą admin nuolaidų valdymui
discount_bp = Blueprint(
    'admin_discounts', __name__, url_prefix='/admin/discounts'
)

# Apribojimas: tik administratoriams
from functools import wraps

def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
            flash('Prieiga tik administratoriams.', 'danger')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return decorated_view

# 1. Nuolaidų sąrašas
@discount_bp.route('/', methods=['GET'])
@login_required
@admin_required
def list_discounts():
    discounts = get_all_discounts(active_only=False)
    return render_template('admin/discounts/list.html', discounts=discounts)

# 2. Pridėti naują nuolaidą
@discount_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_discount():
    form = DiscountForm()
    if form.validate_on_submit():
        discount = create_discount(form, created_by=current_user.id)
        if discount:
            flash('Nuolaida sėkmingai sukurta.', 'success')
            return redirect(url_for('admin_discounts.list_discounts'))
        flash('Įvyko klaida kuriant nuolaidą.', 'danger')
    return render_template('admin/discounts/add.html', form=form, action='add')

# 3. Redaguoti esamą nuolaidą
@discount_bp.route('/<int:discount_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_discount(discount_id):
    discount = get_discount_by_id(discount_id)
    if not discount:
        flash('Nuolaida nerasta.', 'danger')
        return redirect(url_for('admin_discounts.list_discounts'))
    form = DiscountForm(obj=discount)
    if form.validate_on_submit():
        ok = update_discount(discount, form, modified_by=current_user.id)
        if ok:
            flash('Nuolaida atnaujinta.', 'success')
            return redirect(url_for('admin_discounts.list_discounts'))
        flash('Įvyko klaida atnaujinant nuolaidą.', 'danger')
    return render_template('admin/discounts/edit.html', form=form, action='edit', discount=discount)

# 4. Aktyvuoti nuolaidą
@discount_bp.route('/<int:discount_id>/activate', methods=['POST'])
@login_required
@admin_required
def activate_discount_route(discount_id):
    ok = activate_discount(discount_id)
    if ok:
        flash('Nuolaida aktyvuota.', 'success')
    else:
        flash('Klaida aktyvuojant nuolaidą.', 'danger')
    return redirect(url_for('admin_discounts.list_discounts'))

# 5. Deaktyvuoti nuolaidą
@discount_bp.route('/<int:discount_id>/deactivate', methods=['POST'])
@login_required
@admin_required
def deactivate_discount_route(discount_id):
    ok = deactivate_discount(discount_id)
    if ok:
        flash('Nuolaida išjungta.', 'info')
    else:
        flash('Klaida išjungiant nuolaidą.', 'danger')
    return redirect(url_for('admin_discounts.list_discounts'))

# 6. Ištrinti nuolaidą
@discount_bp.route('/<int:discount_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_discount_route(discount_id):
    ok = delete_discount(discount_id)
    if ok:
        flash('Nuolaida ištrinta.', 'success')
    else:
        flash('Klaida trinant nuolaidą.', 'danger')
    return redirect(url_for('admin_discounts.list_discounts'))

# Nuolaidos detalizacijos puslapis
@discount_bp.route('/<int:discount_id>', methods=['GET'])
@login_required
@admin_required
def detail_discount(discount_id):
    discount = get_discount_by_id(discount_id)
    if not discount:
        flash('Nuolaida nerasta.', 'danger')
        return redirect(url_for('admin_discounts.list_discounts'))
    return render_template('admin/discounts/detail.html', discount=discount)