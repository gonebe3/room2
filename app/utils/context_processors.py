from datetime import datetime

def inject_now():
    return {'now': datetime.now()}

def inject_categories():
    from app.models.category import Category
    categories = Category.query.order_by(Category.name).all()
    return dict(categories=categories)
