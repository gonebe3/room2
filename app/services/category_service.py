from app.models.category import Category
from app.utils.extensions import db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

def get_all_categories():
    try:
        return Category.query.order_by(Category.name).all()
    except SQLAlchemyError as e:
        print(f"Klaida gaunant kategorijas: {e}")
        return []

def get_category_by_id(cat_id):
    try:
        return Category.query.get(cat_id)
    except SQLAlchemyError as e:
        print(f"Klaida gaunant kategoriją: {e}")
        return None

def create_category(form):
    try:
        category = Category(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(category)
        db.session.commit()
        return category, None
    except IntegrityError:
        db.session.rollback()
        return None, "Tokia kategorija jau egzistuoja."
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Klaida kuriant kategoriją: {e}")
        return None, "Klaida kuriant kategoriją."

def update_category(category, form):
    try:
        category.name = form.name.data
        category.description = form.description.data
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Klaida atnaujinant kategoriją: {e}")
        return False

def delete_category(category):
    try:
        db.session.delete(category)
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Klaida trinant kategoriją: {e}")
        return False