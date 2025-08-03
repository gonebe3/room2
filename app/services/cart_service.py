from app.models.cart import Cart
from app.models.product import Product
from app.utils.extensions import db
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from app.services.discount_service import validate_discount_code

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
    Jei prekė turi savybę `discount_price` ir ji mažesnė už `price`, skaičiuojame
    tiek nuolaidą, tiek galutinę kainą. Grąžina tris float reikšmes:
      total – be nuolaidų, 
      total_discount – sutaupymas,
      total_final – mokėtina suma.
    """
    total = 0.0
    total_discount = 0.0

    for item in cart_items:
        # Originali prekės kaina
        price = float(getattr(item.product, 'price', 0) or 0)
        # Galima nuolaidos kaina
        raw_dp = getattr(item.product, 'discount_price', None)
        try:
            discount_price = float(raw_dp) if raw_dp is not None else None
        except (TypeError, ValueError):
            discount_price = None

        # Kiekis (saugiai paverčiame int)
        try:
            quantity = int(item.quantity or 1)
        except (TypeError, ValueError):
            quantity = 1

        # Apskaičiuojame
        if discount_price is not None and discount_price < price:
            total += price * quantity
            total_discount += (price - discount_price) * quantity
        else:
            total += price * quantity

    total_final = total - total_discount
    return float(total), float(total_discount), float(total_final)

def get_cart_summary(cart_items, discount_code=None):
    """
    Apskaičiuoja visą krepšelio suvestinę kartu su nuolaidos kodo patikrinimu.
    Grąžina dict su:
      - total: suma be jokių nuolaidų
      - discount_items: sutaupymas prekėms su discount_price
      - code_discount: papildoma nuolaida pagal kodą
      - total_discount: bendras sutaupymas (prekės + kodas)
      - total_final: galutinė mokėtina suma
      - discount_obj: Discount objektas, jei kodas galioja, kitu atveju None
      - error: klaidos tekstas, jei kodas neteisingas arba netinka
    """
    total, discount_items, after_items = calculate_cart_totals(cart_items)
    code_discount = 0.0
    discount_obj = None
    error = None

    if discount_code:
        discount_obj = validate_discount_code(discount_code)
        if not discount_obj:
            error = "Klaidingas arba nebegaliojantis nuolaidos kodas."
        else:
            # procentinė arba fiksuota
            if discount_obj.discount_type == 'percent':
                code_discount = float(discount_obj.value) / 100.0 * after_items
            else:
                code_discount = float(discount_obj.value)
            # minimalios sumos tikrinimas
            if discount_obj.min_purchase and after_items < float(discount_obj.min_purchase):
                error = f"Ši nuolaida galioja nuo {discount_obj.min_purchase} € pirkimų sumos."

    total_discount = discount_items + (code_discount if not error else 0)
    total_final = after_items - (code_discount if not error else 0)

    return {
        'total': total,
        'discount_items': discount_items,
        'code_discount': code_discount,
        'total_discount': total_discount,
        'total_final': total_final,
        'discount_obj': discount_obj,
        'error': error
    }