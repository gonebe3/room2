from flask import Blueprint, render_template, request
from app.services.product_service import get_all_products
from app.services.review_service import get_average_rating, get_review_count
from app.forms.cart_form import CartAddForm
from app.forms.search_form import SearchForm



main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    form = SearchForm(request.args, meta={'csrf': False})
    q = request.args.get('q', '')
    sort_by = request.args.get('sort_by', 'default')
    products = get_all_products()  # arba gali naudoti paiešką/filtrus

    # Sukuriam žemėlapius reitingams, atsiliepimų kiekiui ir formoms:
    avg_ratings = {p.id: get_average_rating(p.id) or 0 for p in products}
    reviews_count = {p.id: get_review_count(p.id) or 0 for p in products}
    forms = {p.id: CartAddForm(product_id=p.id, quantity=1) for p in products}

    return render_template(
        'product/product_list.html',
        form=form,
        products=products,
        avg_ratings=avg_ratings,
        reviews_count=reviews_count,
        forms=forms
    )


@main_bp.route('/contacts')
def contacts():
    return render_template('main/contacts.html')

@main_bp.route('/stores')
def stores():
    return render_template('main/stores.html')

@main_bp.route('/privacy-policy')
def privacy_policy():
    return render_template('main/privacy_policy.html')

@main_bp.route('/terms')
def terms():
    return render_template('main/terms.html')