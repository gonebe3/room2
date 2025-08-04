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

        db_discount = db.session.get(Discount, discount.id)
        if not db_discount:
            return False

        # Paruošiame valid_from su laiko zona
        vf = form.valid_from.data
        if isinstance(vf, date) and not isinstance(vf, datetime):
            valid_from = datetime(vf.year, vf.month, vf.day, tzinfo=timezone.utc)
        else:
            valid_from = vf
        # Paruošiame valid_until su laiko zona
        vu = form.valid_until.data
        if isinstance(vu, date) and not isinstance(vu, datetime):
            valid_until = datetime(vu.year, vu.month, vu.day, tzinfo=timezone.utc)
        else:
            valid_until = vu

        # Nustatymai pagal tipą
        d_type = form.discount_type.data
        if d_type == 'percent':
            value = form.percentage.data
        elif d_type == 'fixed':
            value = form.value.data
        else:
            value = form.value.data or form.percentage.data

        db_discount.code = form.code.data
        db_discount.description = form.description.data
        db_discount.discount_type = d_type
        db_discount.value = value
        db_discount.min_purchase = form.min_purchase.data
        db_discount.loyalty_min_orders = form.loyalty_min_orders.data
        db_discount.loyalty_min_amount = form.loyalty_min_amount.data
        db_discount.loyalty_period_days = form.loyalty_period_days.data
        db_discount.usage_limit = form.usage_limit.data
        db_discount.valid_from = valid_from
        db_discount.valid_until = valid_until
        db_discount.modified_by = modified_by

        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error updating discount: {e}")
        return False

=======
        with db.session() as session:
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


def activate_discount(discount):
    try:
        with db.session() as session:
            db_discount = session.get(Discount, discount.id)
            if db_discount:
                db_discount.is_active = True
                session.commit()
                return True
            return False
    except SQLAlchemyError as e:
        print(f"Error activating discount: {e}")
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
    """
    Patikrina, ar nuolaidos kodas egzistuoja, yra aktyvus ir galioja šiandieną.
    """
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