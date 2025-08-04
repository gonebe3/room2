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

discount_bp = Blueprint('discount', __name__, url_prefix='/discounts')

# Dekoratorius tik admin teisių vartotojui
def admin_required(func):
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, "is_admin", False):
            flash("Prieiga tik administratoriams.", "danger")
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return decorated_view

# Visų nuolaidų sąrašas
@discount_bp.route('/')
@login_required
@admin_required
def list_discounts():
    discounts = get_all_discounts()
    return render_template('admin/discounts.html', discounts=discounts)

# Naujos nuolaidos pridėjimas
@discount_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_discount():
    form = DiscountForm()
    if form.validate_on_submit():
        result, error = create_discount(form)
        if result:
            flash('Nuolaida sukurta.', 'success')
            return redirect(url_for('discount.list_discounts'))
        else:
            flash(error or 'Klaida kuriant nuolaidą.', 'danger')
    return render_template('admin/add_discount.html', form=form)

# Nuolaidos redagavimas
@discount_bp.route('/edit/<int:discount_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_discount(discount_id):
    discount = get_discount_by_id(discount_id)
    if not discount:
        flash('Nuolaida nerasta.', 'danger')
        return redirect(url_for('discount.list_discounts'))
    form = DiscountForm(obj=discount)
    if form.validate_on_submit():
        result, error = update_discount(discount, form)
        if result:
            flash('Nuolaida atnaujinta.', 'success')
            return redirect(url_for('discount.list_discounts'))
        else:
            flash(error or 'Klaida atnaujinant nuolaidą.', 'danger')
    return render_template('admin/edit_discount.html', form=form, discount=discount)

# Nuolaidos aktyvavimas
@discount_bp.route('/activate/<int:discount_id>', methods=['POST'])
@login_required
@admin_required
def activate_discount_route(discount_id):
    discount = get_discount_by_id(discount_id)
    if not discount:
        flash('Nuolaida nerasta.', 'danger')
    else:
        if activate_discount(discount):
            flash('Nuolaida aktyvuota.', 'success')
        else:
            flash('Klaida aktyvuojant nuolaidą.', 'danger')
    return redirect(url_for('discount.list_discounts'))

# Nuolaidos deaktyvavimas
@discount_bp.route('/deactivate/<int:discount_id>', methods=['POST'])
@login_required
@admin_required
def deactivate_discount_route(discount_id):
    discount = get_discount_by_id(discount_id)
    if not discount:
        flash('Nuolaida nerasta.', 'danger')
    else:
        if deactivate_discount(discount):
            flash('Nuolaida išjungta.', 'info')
        else:
            flash('Klaida išjungiant nuolaidą.', 'danger')
    return redirect(url_for('discount.list_discounts'))

# Nuolaidos ištrynimas (hard-delete)
@discount_bp.route('/delete/<int:discount_id>', methods=['POST'])
@login_required
@admin_required
def delete_discount_route(discount_id):
    discount = get_discount_by_id(discount_id)
    if not discount:
        flash('Nuolaida nerasta.', 'danger')
    else:
        if delete_discount(discount):
            flash('Nuolaida ištrinta.', 'success')
        else:
            flash('Klaida trinant nuolaidą.', 'danger')
    return redirect(url_for('discount.list_discounts'))