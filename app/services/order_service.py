from app.models.order import Order
from app.models.order_item import OrderItem
from app.utils.extensions import db
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

def get_all_orders():
    """Gražina VISUS užsakymus su jų OrderItem'ais (admin view, statistika)"""
    try:
        with db.session() as session:
            stmt = select(Order).options(joinedload(Order.order_items)).order_by(Order.created_on.desc())
            return session.execute(stmt).scalars().all()
    except SQLAlchemyError as e:
        print(f"Klaida gaunant visus užsakymus: {e}")
        return []

def get_order_by_id(order_id):
    """Gražina vieną užsakymą su jo OrderItem'ais"""
    try:
        with db.session() as session:
            stmt = select(Order).options(joinedload(Order.order_items)).where(Order.id == order_id)
            return session.execute(stmt).scalar_one_or_none()
    except SQLAlchemyError as e:
        print(f"Klaida gaunant užsakymą: {e}")
        return None

def get_orders_by_user(user_id):
    try:
        with db.session() as session:
            stmt = (
                select(Order)
                .options(joinedload(Order.order_items))
                .where(Order.user_id == user_id)
                .where(Order.is_deleted == False)
                .order_by(Order.created_on.desc())
            )
            orders = session.execute(stmt).unique().scalars().all()
            for order in orders:
                order.item_count = sum([oi.quantity for oi in order.order_items])
            return orders
    except SQLAlchemyError as e:
        print(f"Klaida gaunant vartotojo užsakymus: {e}")
        return []

def create_order(
    user_id,
    cart_items,
    total_amount,
    discount_id=None,
    shipping_address=None,
    notes=None,
    created_by=None
):
    try:
        with db.session() as session:
            order = Order(
                user_id=user_id,
                total_amount=total_amount,
                status="pending",
                shipping_address=shipping_address,
                notes=notes,
                created_by=created_by,
                discount_id=discount_id
            )
            session.add(order)
            session.flush()  # order.id jau žinomas

            for item in cart_items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.product.price,
                    created_by=user_id
                )
                session.add(order_item)

            session.commit()
            # Kad grąžintų jau su order_items – užkrauk per session refresh + joinedload
            session.refresh(order)
            order = (
                session.query(Order)
                .options(joinedload(Order.order_items))
                .filter(Order.id == order.id)
                .first()
            )
            return order, None

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Klaida kuriant užsakymą: {e}")
        return None, str(e)

def update_order_status(order_id, new_status, modified_by=None):
    try:
        with db.session() as session:
            order = session.get(Order, order_id)
            if not order:
                return False
            order.status = new_status
            if modified_by:
                order.modified_by = modified_by
            session.commit()
            return True
    except SQLAlchemyError as e:
        print(f"Error updating order status: {e}")
        return False

def delete_order(order_id):
    try:
        with db.session() as session:
            order = session.get(Order, order_id)
            if not order:
                return False
            session.delete(order)
            session.commit()
            return True
    except SQLAlchemyError as e:
        print(f"Error deleting order: {e}")
        return False

def get_order_items(order_id):
    """Sugrąžina VISUS orderio produktus"""
    try:
        with db.session() as session:
            stmt = select(OrderItem).where(OrderItem.order_id == order_id)
            return session.execute(stmt).scalars().all()
    except SQLAlchemyError as e:
        print(f"Klaida gaunant order items: {e}")
        return []

def get_orders_with_details():
    """Sugrąžina visus užsakymus su jų OrderItem'ais – naudoti dashboardui, statistikoms ir pan."""
    return get_all_orders()