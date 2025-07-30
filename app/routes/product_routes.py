from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.forms.product_form import ProductForm
from app.services.product_service import (
    get_all_products,
    get_product_by_id,
    
)
from app.services.review_service import (
    get_average_rating,
    get_review_count,
)
from app.forms.cart_form import CartAddForm

import os


product_bp = Blueprint('product', __name__, url_prefix='/product')

@product_bp.route('/<int:product_id>')
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if not product or getattr(product, "is_deleted", False) or not product.is_active:
        flash('Prekė nerasta.', 'danger')
        return redirect(url_for('product.product_list'))
    return render_template('product/product_detail.html', product=product)


@product_bp.route('/')
def product_list():
    products = get_all_products()
    avg_ratings = {p.id: get_average_rating(p.id) for p in products}
    reviews_count = {p.id: get_review_count(p.id) for p in products}
    forms = {p.id: CartAddForm(product_id=p.id, quantity=1) for p in products}
    return render_template(
        'product/product_list.html',
        products=products,
        avg_ratings=avg_ratings,
        reviews_count=reviews_count,
        forms=forms
    )