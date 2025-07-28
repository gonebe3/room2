from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.forms.review_form import ReviewForm
from app.services.review_service import (
    get_reviews_by_product,
    get_review_by_id,
    create_review,
    update_review,
    delete_review
)
from app.services.product_service import get_product_by_id

review_bp = Blueprint('review', __name__, url_prefix='/review')

# Peržiūrėti visus produkto atsiliepimus
@review_bp.route('/product/<int:product_id>')
def product_reviews(product_id):
    product = get_product_by_id(product_id)
    if not product or product.is_deleted:
        flash('Prekė nerasta.', 'danger')
        return redirect(url_for('product.product_list'))
    reviews = get_reviews_by_product(product_id)
    return render_template('review/review.html', product=product, reviews=reviews)

# Parašyti naują atsiliepimą
@review_bp.route('/product/<int:product_id>/add', methods=['GET', 'POST'])
@login_required
def add_review(product_id):
    product = get_product_by_id(product_id)
    if not product or product.is_deleted:
        flash('Prekė nerasta.', 'danger')
        return redirect(url_for('product.product_list'))
    form = ReviewForm()
    if form.validate_on_submit():
        review = create_review(current_user.id, product_id, form)
        if review:
            flash('Atsiliepimas pridėtas.', 'success')
        else:
            flash('Klaida pridedant atsiliepimą.', 'danger')
        return redirect(url_for('review.product_reviews', product_id=product_id))
    return render_template('review/add_review.html', form=form, product=product)

# Redaguoti atsiliepimą (tik savo)
@review_bp.route('/edit/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    review = get_review_by_id(review_id)
    if not review or review.user_id != current_user.id:
        flash('Jūs galite redaguoti tik savo atsiliepimus.', 'danger')
        return redirect(url_for('product.product_list'))
    form = ReviewForm(obj=review)
    if form.validate_on_submit():
        updated = update_review(review, form)
        if updated:
            flash('Atsiliepimas atnaujintas.', 'success')
        else:
            flash('Klaida atnaujinant atsiliepimą.', 'danger')
        return redirect(url_for('review.product_reviews', product_id=review.product_id))
    return render_template('review/edit_review.html', form=form, review=review)

# Ištrinti atsiliepimą (tik savo arba admin)
@review_bp.route('/delete/<int:review_id>', methods=['POST'])
@login_required
def delete_review_route(review_id):
    review = get_review_by_id(review_id)
    if not review or (review.user_id != current_user.id and not getattr(current_user, "is_admin", False)):
        flash('Neturite teisių.', 'danger')
        return redirect(url_for('product.product_list'))
    if delete_review(review):
        flash('Atsiliepimas ištrintas.', 'success')
    else:
        flash('Klaida trinant atsiliepimą.', 'danger')
    return redirect(url_for('review.product_reviews', product_id=review.product_id))