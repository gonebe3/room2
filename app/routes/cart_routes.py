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

    # Apskaičiuojam suvestines (jei nenaudoji serviso – calculate_cart_total, skaičiuok tiesiai)
    total = sum(item.product.price * item.quantity for item in cart_items)
    total_discount = sum(
        (item.product.price - item.product.discount_price) * item.quantity
        for item in cart_items
        if getattr(item.product, "discount_price", None)
    )
    total_final = total - total_discount

    cart = {
        "items": cart_items,
        "total": total,
        "total_discount": total_discount,
        "total_final": total_final,
    }

    return render_template('cart/cart.html', cart=cart)

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

@cart_bp.route('/add/<int:product_id>', methods=['POST'], endpoint='add_to_cart')
@login_required
def add_to_cart_route(product_id):
    form = CartAddForm()
    if form.validate_on_submit():
        success = add_to_cart(current_user.id, product_id, form.quantity.data)
        if success:
            flash("Prekė pridėta į krepšelį.", "success")
        else:
            flash("Nepavyko pridėti prekės į krepšelį.", "danger")
    else:
        flash("Neteisingi duomenys.", "danger")
    return redirect(url_for('cart.view_cart'))