from app.models.review import Review
from app.models.product import Product
from app.utils.extensions import db
from sqlalchemy.exc import SQLAlchemyError

def get_reviews_by_product(product_id: int):
    """Grąžina produkto review'us (tik ne ištrintus, naujausi viršuje)."""
    try:
        product = Product.query.get(product_id)
        if not product:
            return []
        return product.reviews.filter_by(is_deleted=False).order_by(Review.created_at.desc()).all()
    except SQLAlchemyError:
        return []

def get_review_by_id(review_id: int):
    """Grąžina vieną review (jei neištrintas)."""
    try:
        return Review.query.filter_by(id=review_id, is_deleted=False).first()
    except SQLAlchemyError:
        return None

def create_review(user_id: int, product_id: int, form):
    """Sukuria naują review'ą."""
    try:
        new_review = Review(
            user_id=user_id,
            product_id=product_id,
            rating=form.rating.data,
            comment=form.comment.data,
        )
        db.session.add(new_review)
        db.session.commit()
        return new_review
    except SQLAlchemyError:
        db.session.rollback()
        return None

def update_review(review: Review, form):
    """Atnaujina esamą review'ą."""
    try:
        review.rating = form.rating.data
        review.comment = form.comment.data
        db.session.commit()
        return True
    except SQLAlchemyError:
        db.session.rollback()
        return False

def delete_review(review: Review):
    """Soft-delete (žymi kaip ištrintą, nenaikina iš DB)."""
    try:
        review.is_deleted = True
        db.session.commit()
        return True
    except SQLAlchemyError:
        db.session.rollback()
        return False

def get_reviews_by_user(user_id: int):
    """Vartotojo review'ai (tik ne ištrinti)."""
    try:
        return Review.query.filter_by(user_id=user_id, is_deleted=False).order_by(Review.created_at.desc()).all()
    except SQLAlchemyError:
        return []

def get_average_rating(product_id):
    """Produkto atsiliepimų vidurkis (tik ne ištrinti)."""
    try:
        avg = db.session.query(db.func.avg(Review.rating)).filter(
            Review.product_id == product_id,
            Review.is_deleted == False
        ).scalar()
        return round(avg, 2) if avg else None
    except SQLAlchemyError:
        return None

def get_review_count(product_id):
    """Atsiliepimų skaičius (tik ne ištrinti)."""
    try:
        count = db.session.query(db.func.count(Review.id)).filter(
            Review.product_id == product_id,
            Review.is_deleted == False
        ).scalar()
        return count or 0
    except SQLAlchemyError:
        return 0