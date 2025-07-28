from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/contacts')
def contacts():
    return render_template('main/contacts.html')

@main_bp.route('/stores')
def stores():
    return render_template('main/stores.html')