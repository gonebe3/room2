from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from app.utils.extensions import db, login_manager

class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    balance = db.Column(db.Numeric(10, 2), default=0.00)
    role = db.Column(db.String(16), default='user', nullable=False)

    # Email patvirtinimui:
    email_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    email_confirmed_at = db.Column(db.DateTime, nullable=True)
    email_confirmation_token = db.Column(db.String(128), nullable=True)

    # Audito laukai:
    created_on  = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    created_by  = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    modified_on = db.Column(db.DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=False)
    modified_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    is_deleted  = db.Column(db.Boolean, default=False, nullable=False)

    is_active      = db.Column(db.Boolean, default=True)
    login_attempts = db.Column(db.Integer, default=0)
    locked_until   = db.Column(db.DateTime, nullable=True)

    # --------- RYŠIAI ---------
    # Svarbu: Privaloma nurodyti foreign_keys, jei modelyje yra daugiau nei vienas ryšys į tą pačią lentelę!

    cart_items = db.relationship(
        "Cart",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="[Cart.user_id]"
    )
    reviews = db.relationship(
        "Review",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="[Review.user_id]"
    )
    orders = db.relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="[Order.user_id]"
    )
    # Jei reikia – pridėkite ir sekimo (audit) laukų relationship'us:
    # created_cart_items = db.relationship("Cart", foreign_keys="[Cart.created_by]")
    # modified_cart_items = db.relationship("Cart", foreign_keys="[Cart.modified_by]")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        # Galima išplėsti logiką vėliau, jei pridėsite admin lygį
        return getattr(self, 'role', None) == 'admin'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))