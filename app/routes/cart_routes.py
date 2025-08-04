from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.forms.cart_form import CartAddForm, CartUpdateForm
from app.services.cart_service import (
    get_cart_items,
    add_to_cart,
    update_cart_item,
    remove_from_cart,   # Teisingas funkcijos pavadinimas!
    clear_cart,
)
from app.services.product_service import get_product_by_id

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

@cart_bp.route('/', methods=['GET'])
@login_required
def view_cart():
    cart_items = get_cart_items(current_user.id)
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart/cart.html', cart_items=cart_items, total=total)

@cart_bp.route('/add', methods=['POST'])
@login_required
def add_product_to_cart():
    form = CartAddForm()
    if form.validate_on_submit():
        product = get_product_by_id(form.product_id.data)
        if not product:
            flash('Prekė nerasta.', 'danger')
            return redirect(url_for('product.product_list'))
        add_to_cart(user_id=current_user.id, product_id=product.id, quantity=form.quantity.data)
        flash('Prekė pridėta į krepšelį!', 'success')
        return redirect(url_for('cart.view_cart'))
    flash('Neteisingi duomenys.', 'danger')
    return redirect(url_for('product.product_list'))

@cart_bp.route('/update', methods=['POST'])
@login_required
def update_product_in_cart():
    form = CartUpdateForm()
    if form.validate_on_submit():
        success = update_cart_item(
            user_id=current_user.id,
            cart_item_id=form.cart_item_id.data,
            quantity=form.quantity.data
        )
        if success:
            flash('Kiekis atnaujintas.', 'success')
        else:
            flash('Nepavyko atnaujinti kiekio.', 'danger')
    else:
        flash('Neteisingi duomenys.', 'danger')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/remove', methods=['POST'])
@login_required
def remove_product_from_cart():
    form = CartUpdateForm()
    if form.validate_on_submit():
        success = remove_from_cart(
            user_id=current_user.id,
            cart_item_id=form.cart_item_id.data
        )
        if success:
            flash('Prekė pašalinta iš krepšelio.', 'info')
        else:
            flash('Nepavyko pašalinti prekės.', 'danger')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/clear', methods=['POST'])
@login_required
def clear_user_cart():
    clear_cart(current_user.id)
    flash('Krepšelis išvalytas.', 'info')
    return redirect(url_for('cart.view_cart'))