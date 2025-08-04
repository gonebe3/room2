from app.models.review import Review
from app.models.product import Product
from app.utils.extensions import db
from sqlalchemy.exc import SQLAlchemyError

def get_reviews_by_product(product_id: int):
    """Grąžina produkto review'us (tik ne ištrintus, naujausi viršuje)."""
    try:
        return (
            Review.query
            .filter_by(product_id=product_id, is_deleted=False)
            .order_by(Review.created_at.desc())
            .all()
        )
    except SQLAlchemyError:
        return []

def get_review_by_id(review_id: int):
    """Grąžina vieną review (jei neištrintas)."""
    try:
        return Review.query.filter_by(id=review_id, is_deleted=False).first()
    except SQLAlchemyError:
        return None

def get_user_review_for_product_and_order(user_id: int, product_id: int, order_id: int):
    """Grąžina review, jei user jau paliko review už šią prekę tame pačiame užsakyme (ne ištrintą), kitu atveju None."""
    try:
        return (
            Review.query
            .filter_by(user_id=user_id, product_id=product_id, order_id=order_id, is_deleted=False)
            .first()
        )
    except SQLAlchemyError:
        return None

def create_review(user_id: int, product_id: int, order_id: int, form):
    """Sukuria naują review, jeigu nėra dublikato už tą patį produktą tame pačiame orderyje."""
    try:
        # Prevencija: ar nėra review už šią prekę ir šį orderį
        existing = get_user_review_for_product_and_order(user_id, product_id, order_id)
        if existing:
            return None, "Jūs jau palikote atsiliepimą už šią prekę šiame užsakyme."
        new_review = Review(
            user_id=user_id,
            product_id=product_id,
            order_id=order_id,
            rating=form.rating.data,
            comment=form.comment.data,
        )
        db.session.add(new_review)
        db.session.commit()
        return new_review, None
    except SQLAlchemyError:
        db.session.rollback()
        return None, "Klaida pridedant atsiliepimą."

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
        return (
            Review.query
            .filter_by(user_id=user_id, is_deleted=False)
            .order_by(Review.created_at.desc())
            .all()
        )
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

def can_user_review_product(user, product, order):
    """
    Tikrina, ar user gali palikti review už nurodytą prekę ir užsakymą.
    - user turi būti order savininkas
    - order.status == 'completed'
    - produktas priklauso orderiui
    - user dar nėra palikęs review už šią prekę šiame orderyje
    """
    if not product or getattr(product, "is_deleted", False):
        return False, "Prekė nerasta."
    if not order or order.user_id != user.id or order.is_deleted:
        return False, "Neturite teisės palikti atsiliepimo už šį užsakymą."
    if order.status != "completed":
        return False, "Atsiliepimą galima palikti tik po pristatymo."
    if not any(item.product_id == product.id for item in order.order_items):
        return False, "Ši prekė nepriklauso šiam užsakymui."
    # Tikslus dublikato tikrinimas pagal product_id ir order_id!
    existing = get_user_review_for_product_and_order(user.id, product.id, order.id)
    if existing:
        return False, "Jūs jau palikote atsiliepimą už šią prekę šiame užsakyme."
    return True, None
