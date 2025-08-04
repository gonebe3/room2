from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.forms.cart_form import CartAddForm, CartUpdateForm, CartClearForm
from app.services.cart_service import (
    get_cart_items,
    add_to_cart,
    update_cart_item,
    remove_from_cart,
    clear_cart,
    calculate_cart_totals,
)
from app.services.product_service import get_product_by_id
from sqlalchemy.exc import SQLAlchemyError

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

@cart_bp.route('/', methods=['GET'])
@login_required
def view_cart():
    try:
        cart_items = get_cart_items(current_user.id)
        total, total_discount, total_final = calculate_cart_totals(cart_items)
        clear_form = CartClearForm()  # <-- Sukuriam formos instanciją
        return render_template(
            'cart/cart.html',
            cart_items=cart_items,
            total=total,
            total_discount=total_discount,
            total_final=total_final,
            clear_form=clear_form,   # <-- Perduodam į template
        )
    except SQLAlchemyError:
        flash('Įvyko klaida atvaizduojant krepšelį.', 'danger')
        return redirect(url_for('product.product_list'))

@cart_bp.route('/add/<int:product_id>', methods=['POST'], endpoint='add_to_cart')
@login_required
def add_to_cart_route(product_id):
    form = CartAddForm()
    if form.validate_on_submit():
        try:
            success = add_to_cart(current_user.id, product_id, form.quantity.data)
            if success:
                flash("Prekė pridėta į krepšelį.", "success")
            else:
                flash("Nepavyko pridėti prekės į krepšelį.", "danger")
        except SQLAlchemyError:
            flash("Klaida pridedant prekę į krepšelį.", "danger")
    else:
        flash("Neteisingi duomenys.", "danger")
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/update', methods=['POST'])
@login_required
def update_product_in_cart():
    form = CartUpdateForm()
    if form.validate_on_submit():
        try:
            success = update_cart_item(
                user_id=current_user.id,
                cart_item_id=form.cart_item_id.data,
                quantity=form.quantity.data
            )
            if success:
                flash('Kiekis atnaujintas.', 'success')
            else:
                flash('Nepavyko atnaujinti kiekio.', 'danger')
        except SQLAlchemyError:
            flash('Įvyko klaida atnaujinant kiekį.', 'danger')
    else:
        flash('Neteisingi duomenys.', 'danger')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/remove', methods=['POST'])
@login_required
def remove_product_from_cart():
    form = CartUpdateForm()
    if form.validate_on_submit():
        try:
            success = remove_from_cart(
                user_id=current_user.id,
                cart_item_id=form.cart_item_id.data
            )
            if success:
                flash('Prekė pašalinta iš krepšelio.', 'info')
            else:
                flash('Nepavyko pašalinti prekės.', 'danger')
        except SQLAlchemyError:
            flash('Įvyko klaida šalinant prekę.', 'danger')
    else:
        flash('Neteisingi duomenys.', 'danger')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/clear', methods=['POST'])
@login_required
def clear_user_cart():
    try:
        clear_cart(current_user.id)
        flash('Krepšelis išvalytas.', 'info')
    except SQLAlchemyError:
        flash('Įvyko klaida valant krepšelį.', 'danger')
    return redirect(url_for('cart.view_cart'))