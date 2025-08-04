from datetime import datetime, timezone, timedelta
from sqlalchemy import func, desc, or_
from app.utils.extensions import db
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.discount import Discount
from app.models.category import Category

def get_users_count():
    return db.session.query(func.count(User.id)).filter(User.is_deleted == False).scalar()

def get_categories_count():
    return db.session.query(func.count(Category.id)).scalar()

def get_products_count():
    return db.session.query(func.count(Product.id)).scalar()

def get_orders_count():
    return db.session.query(func.count(Order.id)).filter(
        Order.is_deleted == False,
        or_(Order.status == "paid", Order.status == "completed")
    ).scalar()

def get_discounts_count():
    return db.session.query(func.count(Discount.id)).scalar()

def get_today_sales_count():
    now = datetime.now(timezone.utc)
    start_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_today = start_today + timedelta(days=1)
    return db.session.query(func.count(Order.id)).filter(
        Order.created_on >= start_today,
        Order.created_on < end_today,
        Order.is_deleted == False,
        or_(Order.status == "paid", Order.status == "completed")
    ).scalar()

def get_month_revenue():
    now = datetime.now(timezone.utc)
    start_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if start_month.month == 12:
        end_month = start_month.replace(year=start_month.year+1, month=1)
    else:
        end_month = start_month.replace(month=start_month.month+1)
    return float(
        db.session.query(func.coalesce(func.sum(Order.total_amount), 0))
        .filter(
            Order.created_on >= start_month,
            Order.created_on < end_month,
            Order.is_deleted == False,
            or_(Order.status == "paid", Order.status == "completed")
        ).scalar() or 0
    )

def get_top_product_name():
    top_product = db.session.query(
        Product.name,
        func.sum(OrderItem.quantity).label('total_qty')
    ).join(OrderItem, OrderItem.product_id == Product.id) \
     .join(Order, Order.id == OrderItem.order_id) \
     .filter(
        Order.is_deleted == False,
        or_(Order.status == "paid", Order.status == "completed"),
        OrderItem.is_deleted == False,
        Product.is_active == True
     ) \
     .group_by(Product.id, Product.name) \
     .order_by(desc('total_qty')) \
     .first()
    return top_product[0] if top_product else "-"

def get_top_client_name():
    top_client = db.session.query(
        User.username,
        func.sum(Order.total_amount).label('total_spent')
    ).join(Order, User.id == Order.user_id) \
     .filter(
        Order.is_deleted == False,
        User.is_deleted == False,
        or_(Order.status == "paid", Order.status == "completed")
     ) \
     .group_by(User.id, User.username) \
     .order_by(desc('total_spent')) \
     .first()
    return top_client[0] if top_client else "-"

def get_admin_dashboard_stats():
   
    try:
        return {
            "users_count": get_users_count(),
            "categories_count": get_categories_count(),
            "products_count": get_products_count(),
            "orders_count": get_orders_count(),
            "discounts_count": get_discounts_count(),
            "today_sales_count": get_today_sales_count(),
            "month_revenue": get_month_revenue(),
            "top_product_name": get_top_product_name(),
            "top_client_name": get_top_client_name()
        }
    except Exception as e:
        print(f"[DASHBOARD STATS ERROR] {e}")
        # Fallback – grąžina tuščius skaičius
        return {
            "users_count": 0,
            "categories_count": 0,
            "products_count": 0,
            "orders_count": 0,
            "discounts_count": 0,
            "today_sales_count": 0,
            "month_revenue": 0,
            "top_product_name": "-",
            "top_client_name": "-"
        }