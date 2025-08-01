from app.models.cart import Cart
from app.models.product import Product
from app.utils.extensions import db
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError

def get_cart_items(user_id: int):
    """
    Gražina visus vartotojo krepšelio įrašus (Cart modelio objektus su product ryšiu)
    """
    try:
        return (
            Cart.query
            .options(joinedload(Cart.product))
            .filter_by(user_id=user_id)
            .filter(Cart.is_deleted == False)
            .all()
        )
    except SQLAlchemyError:
        return []

def add_to_cart(user_id: int, product_id: int, quantity: int) -> bool:
    """
    Prideda prekę į krepšelį (jei yra – didina kiekį). True, jei pavyko.
    """
    try:
        cart_item = (
            Cart.query
            .filter_by(user_id=user_id, product_id=product_id, is_deleted=False)
            .first()
        )
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
            db.session.add(cart_item)
        db.session.commit()
        return True
    except SQLAlchemyError:
        db.session.rollback()
        return False

def update_cart_item(user_id: int, cart_item_id: int, quantity: int) -> bool:
    """
    Atnaujina krepšelio įrašo kiekį pagal user ir įrašo ID.
    """
    try:
        cart_item = (
            Cart.query
            .filter_by(user_id=user_id, id=cart_item_id, is_deleted=False)
            .first()
        )
        if cart_item:
            cart_item.quantity = quantity
            db.session.commit()
            return True
        return False
    except SQLAlchemyError:
        db.session.rollback()
        return False

def remove_from_cart(user_id: int, cart_item_id: int) -> bool:
    """
    Pašalina įrašą iš krepšelio pagal user ir įrašo ID.
    """
    try:
        cart_item = (
            Cart.query
            .filter_by(user_id=user_id, id=cart_item_id, is_deleted=False)
            .first()
        )
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
            return True
        return False
    except SQLAlchemyError:
        db.session.rollback()
        return False

def clear_cart(user_id: int) -> bool:
    """
    Išvalo visus vartotojo krepšelio įrašus.
    """
    try:
        items = Cart.query.filter_by(user_id=user_id, is_deleted=False).all()
        for item in items:
            db.session.delete(item)
        db.session.commit()
        return True
    except SQLAlchemyError:
        db.session.rollback()
        return False

def calculate_cart_totals(cart_items):
    """
    Suskaičiuoja visų krepšelio įrašų sumą, nuolaidą ir galutinę sumą.
    Jei discount_price neegzistuoja ar yra None/neskaitomas, nuolaida neskaičiuojama.
    Garantija: grąžins float reikšmes.
    """
    total = 0.0
    total_discount = 0.0
    for item in cart_items:
        price = float(getattr(item.product, "price", 0) or 0)
        # Saugiai gaunam discount_price – jei nėra, bus None
        discount_price = getattr(item.product, "discount_price", None)
        quantity = int(getattr(item, "quantity", 1) or 1)

        # Tikrinam ar discount_price galima paversti į float – jei ne, ignoruojam (nuolaida neskaičiuojama)
        try:
            discount_price = float(discount_price) if discount_price is not None else None
        except (ValueError, TypeError):
            discount_price = None

        if discount_price is not None and discount_price < price:
            total += price * quantity
            total_discount += (price - discount_price) * quantity
        else:
            total += price * quantity

    total_final = total - total_discount

    return float(total), float(total_discount), float(total_final)