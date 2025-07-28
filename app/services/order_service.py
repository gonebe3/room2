from app.models.order import Order
from app.models.order_item import OrderItem
from app.utils.extensions import db
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

def get_all_orders():
    with db.session() as session:
        stmt = select(Order).order_by(Order.created_on.desc())
        return session.execute(stmt).scalars().all()

def get_order_by_id(order_id):
    with db.session() as session:
        stmt = select(Order).where(Order.id == order_id)
        return session.execute(stmt).scalar_one_or_none()

def get_orders_by_user(user_id):
    with db.session() as session:
        stmt = select(Order).where(Order.user_id == user_id).order_by(Order.created_on.desc())
        return session.execute(stmt).scalars().all()

def create_order(user_id, cart_items, total_amount, discount_id=None):
    try:
        with db.session() as session:
            order = Order(
                user_id=user_id,
                total=total_amount,
                discount_id=discount_id
            )
            session.add(order)
            session.flush()  # kad gautume order.id

            # Pridedame kiekvieną krepšelio prekę kaip OrderItem
            for item in cart_items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.product.price
                )
                session.add(order_item)

            session.commit()
            return order
    except SQLAlchemyError as e:
        print(f"Error creating order: {e}")
        return None

def update_order_status(order_id, new_status):
    try:
        with db.session() as session:
            order = session.get(Order, order_id)
            if not order:
                return False
            order.status = new_status
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
    with db.session() as session:
        stmt = select(OrderItem).where(OrderItem.order_id == order_id)
        return session.execute(stmt).scalars().all()

def get_orders_with_details():
    """Sugrąžina visus užsakymus su prekėmis (Order + OrderItem) - naudoti statistikai, dashboardui."""
    with db.session() as session:
        stmt = select(Order).order_by(Order.created_on.desc())
        orders = session.execute(stmt).scalars().all()
        # Galima papildyti, jei norite detalių: order.order_items (jei yra relationship)
        return orders