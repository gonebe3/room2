from app.models.cart import Cart
from app.models.product import Product
from app.utils.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, delete

def get_cart_items(user_id: int):
    """Grąžina visus vartotojo krepšelio įrašus (su produktu ryšiu)."""
    try:
        with db.session() as session:
            stmt = select(Cart).where(Cart.user_id == user_id, Cart.is_deleted == False)
            items = session.execute(stmt).scalars().all()
            # Užkrauna produktą lazy='selectin'
            for item in items:
                _ = item.product
            return items
    except SQLAlchemyError:
        return []

def add_to_cart(user_id: int, product_id: int, quantity: int) -> bool:
    """Prideda prekę į vartotojo krepšelį, arba padidina kiekį jei jau yra."""
    try:
        with db.session() as session:
            stmt = select(Cart).where(
                Cart.user_id == user_id,
                Cart.product_id == product_id,
                Cart.is_deleted == False
            )
            cart_item = session.execute(stmt).scalar_one_or_none()
            if cart_item:
                cart_item.quantity += quantity
            else:
                cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
                session.add(cart_item)
            session.commit()
            return True
    except SQLAlchemyError:
        db.session.rollback()
        return False

def update_cart_item(user_id: int, cart_item_id: int, quantity: int) -> bool:
    """Atnaujina prekių kiekį krepšelyje."""
    try:
        with db.session() as session:
            stmt = select(Cart).where(
                Cart.user_id == user_id,
                Cart.id == cart_item_id,
                Cart.is_deleted == False
            )
            cart_item = session.execute(stmt).scalar_one_or_none()
            if cart_item:
                cart_item.quantity = quantity
                session.commit()
                return True
            return False
    except SQLAlchemyError:
        db.session.rollback()
        return False

def remove_from_cart(user_id: int, cart_item_id: int) -> bool:
    """Pašalina prekę iš krepšelio (soft delete)."""
    try:
        with db.session() as session:
            stmt = select(Cart).where(
                Cart.user_id == user_id,
                Cart.id == cart_item_id,
                Cart.is_deleted == False
            )
            cart_item = session.execute(stmt).scalar_one_or_none()
            if cart_item:
                cart_item.is_deleted = True
                session.commit()
                return True
            return False
    except SQLAlchemyError:
        db.session.rollback()
        return False

def clear_cart(user_id: int) -> bool:
    """Išvalo visą vartotojo krepšelį (soft delete)."""
    try:
        with db.session() as session:
            stmt = select(Cart).where(Cart.user_id == user_id, Cart.is_deleted == False)
            items = session.execute(stmt).scalars().all()
            for item in items:
                item.is_deleted = True
            session.commit()
            return True
    except SQLAlchemyError:
        db.session.rollback()
        return False

def calculate_cart_totals(cart_items):
    """
    Suskaičiuoja krepšelio bendrą sumą, nuolaidą, ir galutinę sumą.
    cart_items – sąrašas Cart modelio įrašų su susietu Product.
    """
    total = sum(float(item.product.price) * item.quantity for item in cart_items)
    total_discount = sum(
        (float(item.product.price) - float(getattr(item.product, "discount_price", item.product.price))) * item.quantity
        for item in cart_items if getattr(item.product, "discount_price", None)
    )
    total_final = total - total_discount
    return total, total_discount, total_final