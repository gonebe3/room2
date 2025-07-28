from app.models.cart import Cart
from app.models.product import Product
from app.utils.extensions import db
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError

def get_cart_items(user_id: int):
    try:
        with db.session() as session:
            stmt = select(Cart).where(Cart.user_id == user_id)
            return session.execute(stmt).scalars().all()
    except SQLAlchemyError:
        # Čia galima integruoti centralizuotą logging'ą (pvz., Sentry)
        return []

def add_to_cart(user_id: int, product_id: int, quantity: int) -> bool:
    try:
        with db.session() as session:
            stmt = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
            cart_item = session.execute(stmt).scalar_one_or_none()
            if cart_item:
                cart_item.quantity += quantity
            else:
                cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
                session.add(cart_item)
            session.commit()
            return True
    except SQLAlchemyError:
        return False

def update_cart_item(user_id: int, product_id: int, quantity: int) -> bool:
    try:
        with db.session() as session:
            stmt = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
            cart_item = session.execute(stmt).scalar_one_or_none()
            if cart_item:
                cart_item.quantity = quantity
                session.commit()
                return True
            return False
    except SQLAlchemyError:
        return False

def remove_from_cart(user_id: int, product_id: int) -> bool:
    try:
        with db.session() as session:
            stmt = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
            cart_item = session.execute(stmt).scalar_one_or_none()
            if cart_item:
                session.delete(cart_item)
                session.commit()
                return True
            return False
    except SQLAlchemyError:
        return False

def clear_cart(user_id: int) -> bool:
    try:
        with db.session() as session:
            stmt = delete(Cart).where(Cart.user_id == user_id)
            session.execute(stmt)
            session.commit()
            return True
    except SQLAlchemyError:
        return False

def calculate_cart_total(user_id: int) -> float:
    try:
        with db.session() as session:
            stmt = select(Cart, Product).join(Product, Cart.product_id == Product.id).where(Cart.user_id == user_id)
            cart_items = session.execute(stmt).all()
            total = sum(float(product.price) * cart_item.quantity for cart_item, product in cart_items)
            return total
    except SQLAlchemyError:
        return 0.0







    