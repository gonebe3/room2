from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.forms.review_form import ReviewForm
from app.services.review_service import (
    get_reviews_by_product,
    get_review_by_id,
    create_review,
    update_review,
    delete_review,
    can_user_review_product,  # ar vartotojas gali palikti review
)
from app.services.product_service import get_product_by_id
from app.services.order_service import get_order_by_id

review_bp = Blueprint('review', __name__, url_prefix='/review')

# 1. Peržiūrėti visus produkto atsiliepimus
@review_bp.route('/product/<int:product_id>')
def product_reviews(product_id):
    product = get_product_by_id(product_id)
    if not product or getattr(product, "is_deleted", False):
        flash('Prekė nerasta.', 'danger')
        return redirect(url_for('product.product_list'))
    reviews = get_reviews_by_product(product_id)
    return render_template('review/review.html', product=product, reviews=reviews)

# 2. Palikti atsiliepimą už užsakytą produktą (naudojamas product_id ir order_id)
@review_bp.route('/product/<int:product_id>/order/<int:order_id>/add', methods=['GET', 'POST'])
@login_required
def create_review_route(product_id, order_id):
    product = get_product_by_id(product_id)
    order = get_order_by_id(order_id)
    can_review, error = can_user_review_product(current_user, product, order)
    if not can_review:
        flash(error, 'danger')
        return redirect(url_for('user.profile'))

    form = ReviewForm()
    if form.validate_on_submit():
        review, error = create_review(current_user.id, product_id, order_id, form)
        if review:
            flash('Atsiliepimas pridėtas.', 'success')
        else:
            flash(error or 'Klaida pridedant atsiliepimą.', 'danger')
        return redirect(url_for('user.profile'))
    return render_template('review/create.html', form=form, product=product, order=order)

# 3. Redaguoti atsiliepimą (tik savo, per servisą)
@review_bp.route('/edit/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    review = get_review_by_id(review_id)
    if not review or review.user_id != current_user.id or review.is_deleted:
        flash('Jūs galite redaguoti tik savo atsiliepimus.', 'danger')
        return redirect(url_for('user.profile'))

    form = ReviewForm(obj=review)
    if form.validate_on_submit():
        updated = update_review(review, form)
        if updated:
            flash('Atsiliepimas atnaujintas.', 'success')
        else:
            flash('Klaida atnaujinant atsiliepimą.', 'danger')
        return redirect(url_for('user.profile'))
    return render_template('review/edit.html', form=form, review=review)

# 4. Ištrinti atsiliepimą (tik savo arba admin)
@review_bp.route('/delete/<int:review_id>', methods=['POST'])
@login_required
def delete_review_route(review_id):
    review = get_review_by_id(review_id)
    if not review or (review.user_id != current_user.id and not getattr(current_user, "is_admin", False)):
        flash('Neturite teisių.', 'danger')
        return redirect(url_for('user.profile'))

    if delete_review(review):
        flash('Atsiliepimas ištrintas.', 'success')
    else:
        flash('Klaida trinant atsiliepimą.', 'danger')
    return redirect(url_for('user.profile'))