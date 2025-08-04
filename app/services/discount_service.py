from datetime import datetime, date, timedelta, timezone
from sqlalchemy import select, and_, func, or_
from sqlalchemy.exc import SQLAlchemyError
from app.models.discount import Discount
from app.models.order import Order
from app.utils.extensions import db


def get_all_discounts(active_only=True):
    """
    Grąžina visas nuolaidas. Jei active_only=True, tik aktyvias.
    """
    try:
        stmt = select(Discount)
        if active_only:
            stmt = stmt.where(Discount.is_active == True)
        return db.session.execute(stmt).scalars().all()
    except SQLAlchemyError as e:
        print(f"Error fetching discounts: {e}")
        return []


def get_discount_by_id(discount_id):
    """
    Grąžina nuolaidą pagal ID arba None.
    """
    try:
        return db.session.get(Discount, discount_id)
    except SQLAlchemyError as e:
        print(f"Error fetching discount by id: {e}")
        return None


def create_discount(form, created_by=None):
    """
    Sukuria naują Discount objektą pagal formos duomenis.
    """
    try:
        # Paruošiame valid_from su laiko zona
        vf = form.valid_from.data
        if isinstance(vf, date) and not isinstance(vf, datetime):
            valid_from = datetime(vf.year, vf.month, vf.day, tzinfo=timezone.utc)
        else:
            valid_from = vf or datetime.now(timezone.utc)
        # Paruošiame valid_until su laiko zona
        vu = form.valid_until.data
        if isinstance(vu, date) and not isinstance(vu, datetime):
            valid_until = datetime(vu.year, vu.month, vu.day, tzinfo=timezone.utc)
        else:
            valid_until = vu

        # Nustatome reikšmes pagal tipą
        d_type = form.discount_type.data
        if d_type == 'percent':
            value = form.percentage.data
        elif d_type == 'fixed':
            value = form.value.data
        else:  # loyalty
            value = form.value.data or form.percentage.data

        discount = Discount(
            code=form.code.data,
            description=form.description.data,
            discount_type=d_type,
            value=value,
            min_purchase=form.min_purchase.data,
            loyalty_min_orders=form.loyalty_min_orders.data,
            loyalty_min_amount=form.loyalty_min_amount.data,
            loyalty_period_days=form.loyalty_period_days.data,
            usage_limit=form.usage_limit.data,
            valid_from=valid_from,
            valid_until=valid_until,
            is_active=True,
            created_by=created_by
        )
        db.session.add(discount)
        db.session.commit()
        return discount
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error creating discount: {e}")
        return None
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error creating discount: {e}")
        return None


def update_discount(discount, form, modified_by=None):
    """
    Atnaujina esamą nuolaidą pagal formą.
    """
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
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error updating discount: {e}")
        return False


def activate_discount(discount_id):
    """
    Aktyvuoja nuolaidą pagal ID.
    """
    try:
        d = db.session.get(Discount, discount_id)
        if not d:
            return False
        d.is_active = True
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error activating discount: {e}")
        return False


def deactivate_discount(discount_id):
    """
    Deaktyvuoja nuolaidą pagal ID.
    """
    try:
        d = db.session.get(Discount, discount_id)
        if not d:
            return False
        d.is_active = False
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error deactivating discount: {e}")
        return False


def delete_discount(discount_id):
    """
    Ištrina nuolaidą pagal ID.
    """
    try:
        d = db.session.get(Discount, discount_id)
        if not d:
            return False
        db.session.delete(d)
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error deleting discount: {e}")
        return False


def validate_discount_code(code):
    """
    Patikrina, ar duotas kodas egzistuoja, yra aktyvus ir galioja šiandien.
    Grąžina Discount arba None.
    """
    try:
        today = date.today()
        stmt = select(Discount).where(
            Discount.code == code,
            Discount.discount_type != 'loyalty',
            Discount.is_active == True
        )
        d = db.session.execute(stmt).scalar_one_or_none()
        if not d:
            return None
        if d.valid_from and d.valid_from.date() > today:
            return None
        if d.valid_until and d.valid_until.date() < today:
            return None
        if d.usage_limit and d.used_count >= d.usage_limit:
            return None
        return d
    except SQLAlchemyError as e:
        print(f"Error validating discount code: {e}")
        return None


def get_loyalty_discounts_for_user(user_id):
    """
    Gražina lojalumo nuolaidas, kurias atitinka vartotojas:
    - per paskutines loyalty_period_days dienas pirko >= loyalty_min_orders
      arba išleido >= loyalty_min_amount.
    """
    try:
        now = datetime.now(timezone.utc)
        stmt = select(Discount).where(
            Discount.discount_type == 'loyalty',
            Discount.is_active == True,
            or_(Discount.valid_from <= now, Discount.valid_from.is_(None)),
            or_(Discount.valid_until >= now, Discount.valid_until.is_(None))
        )
        discounts = db.session.execute(stmt).scalars().all()
        result = []
        for d in discounts:
            start_period = now - timedelta(days=d.loyalty_period_days)
            order_count = db.session.execute(
                select(func.count(Order.id)).where(
                    Order.user_id == user_id,
                    Order.created_at >= start_period,
                    Order.created_at <= now
                )
            ).scalar() or 0
            total_spent = db.session.execute(
                select(func.coalesce(func.sum(Order.total_amount), 0)).where(
                    Order.user_id == user_id,
                    Order.created_at >= start_period,
                    Order.created_at <= now
                )
            ).scalar() or 0
            ok_orders = d.loyalty_min_orders and order_count >= d.loyalty_min_orders
            ok_amount = d.loyalty_min_amount and total_spent >= d.loyalty_min_amount
            if ok_orders or ok_amount:
                result.append(d)
        return result
    except SQLAlchemyError as e:
        print(f"Error fetching loyalty discounts: {e}")
        return []
