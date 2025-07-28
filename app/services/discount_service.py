from app.models.discount import Discount
from app.utils.extensions import db
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

def get_all_discounts(active_only=True):
    with db.session() as session:
        stmt = select(Discount)
        if active_only:
            stmt = stmt.where(Discount.is_active == True)
        return session.execute(stmt).scalars().all()

def get_discount_by_id(discount_id):
    with db.session() as session:
        stmt = select(Discount).where(Discount.id == discount_id)
        return session.execute(stmt).scalar_one_or_none()

def create_discount(form):
    try:
        with db.session() as session:
            discount = Discount(
                code=form.code.data,
                description=form.description.data,
                percentage=form.percentage.data,
                valid_from=form.valid_from.data,
                valid_to=form.valid_to.data,
                is_active=form.is_active.data,
            )
            session.add(discount)
            session.commit()
            return discount
    except SQLAlchemyError as e:
        print(f"Error creating discount: {e}")
        return None

def update_discount(discount, form):
    try:
        with db.session() as session:
            # Persist existing instance from db
            db_discount = session.get(Discount, discount.id)
            if not db_discount:
                return False
            db_discount.code = form.code.data
            db_discount.description = form.description.data
            db_discount.percentage = form.percentage.data
            db_discount.valid_from = form.valid_from.data
            db_discount.valid_to = form.valid_to.data
            db_discount.is_active = form.is_active.data
            session.commit()
            return True
    except SQLAlchemyError as e:
        print(f"Error updating discount: {e}")
        return False

def deactivate_discount(discount):
    try:
        with db.session() as session:
            db_discount = session.get(Discount, discount.id)
            if db_discount:
                db_discount.is_active = False
                session.commit()
                return True
            return False
    except SQLAlchemyError as e:
        print(f"Error deactivating discount: {e}")
        return False

def delete_discount(discount):
    try:
        with db.session() as session:
            db_discount = session.get(Discount, discount.id)
            if db_discount:
                session.delete(db_discount)
                session.commit()
                return True
            return False
    except SQLAlchemyError as e:
        print(f"Error deleting discount: {e}")
        return False

def validate_discount_code(code):
    """Tikrinti ar nuolaidos kodas galioja (egzistuoja, aktyvus, galiojimo data)"""
    with db.session() as session:
        stmt = select(Discount).where(
            Discount.code == code,
            Discount.is_active == True
        )
        discount = session.execute(stmt).scalar_one_or_none()
        if not discount:
            return None
        # Patikriname galiojimo datą
        from datetime import date
        today = date.today()
        if (discount.valid_from and discount.valid_from > today) or (discount.valid_to and discount.valid_to < today):
            return None
        return discount