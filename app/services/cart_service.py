from app.models.cart import Cart
from app.models.product import Product
from app.extensions import db
from sqlalchemy import select, delete, update
from sqlalchemy.exc import SQLAlchemyError

def add_to_cart(user_id, product_id, quantity):
    try:
        with db.session() as session:
            stmt = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
            result = session.execute(stmt).scalar_one_or_none()
            if result:
                result.quantity += quantity
            else:
                new_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
                session.add(new_item)
            session.commit()
            return True
    except SQLAlchemyError:
        print(f"Error adding to cart")
        return False
    
def remove_from_cart(user_id, product_id):
    try:
        with db.session() as session:
            stmt = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
            item = session.execute(stmt).scalar_one_or_none()

            if item:
                session.delete(item)
                session.commit()
                return True
            return False
    except SQLAlchemyError:
        print(f"Error removing from cart")
        return False
    
def get_cart(user_id):
    with db.session() as session:
        stmt = select(Cart).where(Cart.user_id == user_id)
        result = session.execute(stmt).scalars().all()

def clear_cart(user_id):
    try:
        with db.session() as session:
            stmt = delete(Cart).where(Cart.user_id == user_id)
            session.execute(stmt)
            session.commit()
            return True
    except SQLAlchemyError:
        print(f"Error clearing cart")
        return False
    
def calculate_cart_total(user_id):
    try:
        with db.session() as session:
            stmt = select(Cart, Product.price).join(Product, Cart.product_id == Product.id).where(Cart.user_id == user_id)
            result = session.execute(stmt).all()
            total = 0
            for item in cart_items:
                product_stmt = select(Product).where(Product.id == item.product_id)
                product = session.execute(product_stmt).scalar_one_or_none()
                if product:
                    total += product.price * product.quantity
            return total
    except SQLAlchemyError:
        print(f"Error calculating cart total")
        return 0
    







    