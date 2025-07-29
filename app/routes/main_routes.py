from flask import Blueprint, render_template, request
from app.services.product_service import get_all_products

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    # Galima pridėti filtravimą, rikiavimą pagal request.args (ateičiai)
    products = get_all_products()
    return render_template('product/product_list.html', products=products)

@main_bp.route('/contacts')
def contacts():
    return render_template('main/contacts.html')

@main_bp.route('/stores')
def stores():
    return render_template('main/stores.html')