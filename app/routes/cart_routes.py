
from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from app.services.cart_service import (
    add_to_cart,
    remove_from_cart,
    get_cart,
    clear_cart,
    calculate_cart_total
)
from app.forms.cart_form import CartForm
from app.models.product import Product
from app.extensions import db
from sqlalchemy import select

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

@cart_bp.route('/')
def view_cart():
    user_id = session.get("user_id")
    if not user_id:
        flash("connect if You want to see Your cart.", "warning")
        return redirect(url_for("auth.login"))

    items = get_cart(user_id)
    total = calculate_cart_total(user_id)
    return render_template('cart/cart.html', items=items, total=total)

@cart_bp.route('/add/<int:product_id>', methods=['GET', 'POST'])
def add_item(product_id):
    user_id = session.get("user_id")
    if not user_id:
        flash("please connect If You would like to add product.", "warning")
        return redirect(url_for("auth.login"))

    form = CartForm()

    if form.validate_on_submit():
        success = add_to_cart(user_id, product_id, form.quantity.data)
        if success:
            flash("The product is add to cart!", "success")
        else:
            flash("Failure - the product is not add.", "danger")
        return redirect(url_for("cart.view_cart"))

    
    with db.session() as session_obj:
        product = session_obj.execute(
            select(Product).where(Product.id == product_id)
        ).scalar_one_or_none()

    return render_template('cart/add_to_cart.html', form=form, product=product)

@cart_bp.route('/remove/<int:product_id>')
def remove_item(product_id):
    user_id = session.get("user_id")
    if not user_id:
        flash("Please connect.", "warning")
        return redirect(url_for("auth.login"))

    success = remove_from_cart(user_id, product_id)
    if success:
        flash("The item is removed from cart.", "success")
    else:
        flash("This item is not exist at Your cart.", "warning")

    return redirect(url_for("cart.view_cart"))

@cart_bp.route('/checkout')
def checkout():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please connect.", "warning")
        return redirect(url_for("auth.login"))

    total = calculate_cart_total(user_id)

    
    clear_cart(user_id)
    flash(f"You bought it! Suma: €{total:.2f}", "success")
    return redirect(url_for("cart.view_cart"))






