from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.review import Review
from app.models.product import Product

review_bp = Blueprint('review', __name__)

@review_bp.route('/product/<int:product_id>/review', methods=['GET', 'POST'])
@login_required
def add_review(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        rating = int(request.form.get('rating', 5))
        comment = request.form.get('comment', '')
        review = Review(
            user_id=current_user.id,
            product_id=product.id,
            rating=rating,
            comment=comment
        )
        db.session.add(review)
        db.session.commit()
        flash('Review submitted.')
        return redirect(url_for('product.detail', product_id=product.id))
    return render_template('review/add_review.html', product=product)