from app.models.review import Review
from app.utils.extensions import db
from sqlalchemy.exc import SQLAlchemyError


def get_reviews_by_product(product_id: int):
    try:
        return Review.query.filter_by(product_id=product_id, is_deleted=False).order_by(Review.created_at.desc()).all()
    except SQLAlchemyError:
        return []


def get_review_by_id(review_id: int):
    try:
        return Review.query.filter_by(id=review_id, is_deleted=False).first()
    except SQLAlchemyError:
        return None


def create_review(user_id: int, product_id: int, form):
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
    try:
        review.rating = form.rating.data
        review.comment = form.comment.data
        db.session.commit()
        return True
    except SQLAlchemyError:
        db.session.rollback()
        return False


def delete_review(review: Review):
    try:
        review.is_deleted = True
        db.session.commit()
        return True
    except SQLAlchemyError:
        db.session.rollback()
        return False
    
def get_reviews_by_user(user_id: int):
    try:
        return Review.query.filter_by(user_id=user_id, is_deleted=False).order_by(Review.created_at.desc()).all()
    except SQLAlchemyError:
        return []
    

def get_average_rating(product_id):
    avg = db.session.query(db.func.avg(Review.rating)).filter(Review.product_id == product_id).scalar()
    return round(avg, 2) if avg else None

def get_review_count(product_id):
    count = db.session.query(db.func.count(Review.id)).filter(Review.product_id == product_id).scalar()
    return count or 0