from app.models.product import Product
from app.utils.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
import os

def get_all_products():
    return Product.query.order_by(Product.created_at.desc()).all()

def get_product_by_id(product_id):
    return Product.query.get(product_id)

def create_product(form, upload_folder):
    try:
        filename = None
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(upload_folder, filename))
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            quantity=form.quantity.data,
            image_filename=filename,
            is_active=form.is_active.data,
        )
        db.session.add(product)
        db.session.commit()
        return product
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Klaida kuriant produktą: {e}")
        return None

def update_product(product, form, upload_folder):
    try:
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(upload_folder, filename))
            product.image_filename = filename
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.quantity = form.quantity.data
        product.is_active = form.is_active.data
        db.session.commit()
        return product
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Klaida atnaujinant produktą: {e}")
        return None

def deactivate_product(product):
    try:
        product.is_active = False
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Klaida deaktyvuojant produktą: {e}")
        return False

def update_product_quantity(product, quantity):
    try:
        product.quantity = quantity
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Klaida atnaujinant kiekį: {e}")
        return False

# Jei reikės ištrynimo visam laikui
def delete_product(product):
    try:
        db.session.delete(product)
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Klaida trinant produktą: {e}")
        return False