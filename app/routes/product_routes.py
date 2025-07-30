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
    get_reviews_by_product,
)
from app.forms.cart_form import CartAddForm
from app.forms.search_form import SearchForm
from app.services.search_service import search_products

product_bp = Blueprint('product', __name__, url_prefix='/product')

@product_bp.route('/<int:product_id>', methods=["GET", "POST"])
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if not product or getattr(product, "is_deleted", False) or not product.is_active:
        flash('Prekė nerasta.', 'danger')
        return redirect(url_for('product.product_list'))

    # Atsiliepimai ir reitingai
    avg_rating = get_average_rating(product.id)
    reviews_count = get_review_count(product.id)
    reviews = get_reviews_by_product(product.id)

    # Pridėti į krepšelį forma
    form = CartAddForm(product_id=product.id, quantity=1)
    if request.method == "POST" and form.validate_on_submit():
        # Logika dėl pridėjimo į krepšelį galėtų būti čia, jei reikia.
        # Dabar formą tiesiog perduodame į šabloną.
        pass

    return render_template(
        'product/product_detail.html',
        product=product,
        avg_rating=avg_rating or 0,
        reviews_count=reviews_count or 0,
        reviews=reviews,
        form=form
    )

@product_bp.route('/', methods=["GET"])
def product_list():
    products = get_all_products()
    avg_ratings = {p.id: get_average_rating(p.id) or 0 for p in products}
    reviews_count = {p.id: get_review_count(p.id) or 0 for p in products}
    forms = {p.id: CartAddForm(product_id=p.id, quantity=1) for p in products}
    return render_template(
        'product/product_list.html',
        products=products,
        avg_ratings=avg_ratings,
        reviews_count=reviews_count,
        forms=forms
    )


@product_bp.route('/product')
def product_list():
    form = SearchForm(request.args,meta={'csrf': False})
    q = request.args.get('q', '')
    sort_by = request.args.get('sort_by', 'default')
    return render_template('product/product_list.html', form=form, products=products)