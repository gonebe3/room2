from flask import Blueprint, render_template, request, url_for

promo_bp = Blueprint('promo', __name__)

@promo_bp.route('/promo', methods=['GET', 'POST'])
def promo():
    promo_title = "Super pasiūlymas visiems naujienlaiškio prenumeratoriams!"
    promo_text = "Užsiprenumeruokite mūsų naujienlaiškį ir gaukite 10% nuolaidos kodą pirmam pirkiniui."
    promo_code = None
    logo_url = "/static/logo.png"
    promo_image_url = None
    promo_button_url = url_for('main.index')
    promo_button_text = "Apsipirkti"
    unsubscribe_url = url_for('main.unsubscribe') if 'main.unsubscribe' in [rule.endpoint for rule in request.url_map.iter_rules()] else "#"
    discount_code = None

    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            discount_code = "AKCIJA10"

    return render_template(
        'email/promo.html',
        promo_title=promo_title,
        promo_text=promo_text,
        promo_code=promo_code,
        logo_url=logo_url,
        promo_image_url=promo_image_url,
        promo_button_url=promo_button_url,
        promo_button_text=promo_button_text,
        unsubscribe_url=unsubscribe_url,
        discount_code=discount_code
    )