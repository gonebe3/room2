from app.models.order import Order
from app.models.order_item import OrderItem
from app.utils.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from app.models.user import User

def get_all_orders():
    """Gražina VISUS užsakymus su OrderItem'ais (admin view, statistika)"""
    try:
        return (
            Order.query
            .options(joinedload(Order.order_items))
            .order_by(Order.created_on.desc())
            .all()
        )
    except SQLAlchemyError as e:
        print(f"Klaida gaunant visus užsakymus: {e}")
        return []

def get_order_by_id(order_id):
    """Gražina vieną užsakymą su OrderItem'ais"""
    try:
        return (
            Order.query
            .options(joinedload(Order.order_items))
            .filter(Order.id == order_id)
            .first()
        )
    except SQLAlchemyError as e:
        print(f"Klaida gaunant užsakymą: {e}")
        return None

def get_orders_by_user(user_id):
    """Gražina visus nenušalintus (is_deleted=False) vartotojo užsakymus su OrderItem'ais"""
    try:
        orders = (
            Order.query
            .options(joinedload(Order.order_items))
            .filter(Order.user_id == user_id, Order.is_deleted == False)
            .order_by(Order.created_on.desc())
            .all()
        )
        for order in orders:
            order.item_count = sum(oi.quantity for oi in order.order_items)
        return orders
    except SQLAlchemyError as e:
        print(f"Klaida gaunant vartotojo užsakymus: {e}")
        return []

from app.models.user import User
from app.models.order import Order
from app.models.order_item import OrderItem
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from app.utils.extensions import db

def create_order(
    user_id,
    cart_items,
    total_amount,
    discount_id=None,
    shipping_address=None,
    notes=None,
    created_by=None
):
    """
    Sukuria užsakymą su visomis prekėmis, nurašo balansą, grąžina (order, klaida)
    """
    try:
        # 1. Patikrinam vartotoją
        user = db.session.get(User, user_id)
        if not user:
            return None, "Naudotojas nerastas."
        if float(user.balance) < float(total_amount):
            return None, "Nepakanka lėšų sąskaitoje."

        # 2. Nurašom balansą
        user.balance = float(user.balance) - float(total_amount)

        # 3. Sukuriam užsakymą su status="paid" (nes balansas jau nurašytas)
        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            status="paid",   # <- svarbiausia vieta!
            shipping_address=shipping_address,
            notes=notes,
            created_by=created_by,
            discount_id=discount_id
        )
        db.session.add(order)
        db.session.flush()  # Kad gautume order.id

        # 4. Pridedam visas order prekes
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price,
                created_by=user_id
            )
            db.session.add(order_item)

        db.session.commit()

        # 5. Užkraunam orderį su order_items (jei reikia detaliam grąžinimui)
        db.session.refresh(order)
        order = (
            Order.query
            .options(joinedload(Order.order_items))
            .filter(Order.id == order.id)
            .first()
        )
        return order, None
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Klaida kuriant užsakymą: {e}")
        return None, "Įvyko klaida kuriant užsakymą. Bandykite dar kartą."


def update_order_status(order_id, new_status, modified_by=None):
    try:
        order = Order.query.get(order_id)
        if not order:
            return False
        order.status = new_status
        if modified_by:
            order.modified_by = modified_by
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error updating order status: {e}")
        return False

def delete_order(order_id):
    try:
        order = Order.query.get(order_id)
        if not order:
            return False
        db.session.delete(order)
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error deleting order: {e}")
        return False

def get_order_items(order_id):
    """Sugrąžina VISUS orderio produktus"""
    try:
        return (
            OrderItem.query
            .filter(OrderItem.order_id == order_id)
            .all()
        )
    except SQLAlchemyError as e:
        print(f"Klaida gaunant order items: {e}")
        return []

def get_orders_with_details():
    """Sugrąžina visus užsakymus su OrderItem'ais – naudoti dashboardui, statistikoms ir pan."""
    return get_all_orders()