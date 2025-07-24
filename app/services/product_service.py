from app.models.product import Product
from app.extensions import db
from sqlalchemy import select, update, delete, asc, desc
from sqlalchemy.exc import SQLAlchemyError

def get_all_products():
    with db.session() as session:
        stmt = select(Product)
        return session.execute(stmt).scalars().all()

def get_product_by_id(product_id):
    with db.session() as session:
        stmt = select(Product).where(Product.id == product_id)
        return session.execute(stmt).scalar_one_or_none()

def create_product(data):
    try:
        with db.session() as session:
            product = Product(**data)
            session.add(product)
            session.commit()
            return product
    except SQLAlchemyError as e:
        print(f"Error creating product:")
        return None

def update_product(product_id, data):
    try:
        with db.session() as session:
            stmt = select(Product).where(Product.id == product_id)
            product = session.execute(stmt).scalar_one_or_none()
            if not product:
                print("Product not found.")
                return None

            for key, value in data.items():
                setattr(product, key, value)
            session.commit()
            return product
    except SQLAlchemyError:
        print(f"Error updating product:")
        return None

def delete_product(product_id):
    try:
        with db.session() as session:
            stmt = select(Product).where(Product.id == product_id)
            product = session.execute(stmt).scalar_one_or_none()
            if product:
                session.delete(product)
                session.commit()
                return True
            print("Product not found.")
            return False
    except SQLAlchemyError:
        print(f"Error deleting product")
        return False

def filter_products_by_price(order="asc"):
    with db.session() as session:
        stmt = select(Product).order_by(asc(Product.price) if order == "asc" else desc(Product.price))
        return session.execute(stmt).scalars().all()

def filter_products_by_rating(order="desc"):
    with db.session() as session:
        stmt = select(Product).order_by(desc(Product.rating) if order == "desc" else asc(Product.rating))
        return session.execute(stmt).scalars().all()