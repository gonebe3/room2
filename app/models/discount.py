from datetime import datetime, timezone
from app.utils.extensions import db

class Discount(db.Model):
    __tablename__ = "discount"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    # Tipas: percent, fixed arba loyalty
    discount_type = db.Column(db.String(16), nullable=False)
    value = db.Column(db.Numeric(10, 2), nullable=False)

    # Papildomi kriterijai
    min_purchase = db.Column(db.Numeric(10, 2), nullable=True)

    # Loyalty nuolaidos parametrai
    loyalty_min_orders = db.Column(db.Integer, nullable=True)
    loyalty_min_amount = db.Column(db.Numeric(10, 2), nullable=True)
    loyalty_period_days = db.Column(db.Integer, nullable=True)

    # Naudojimo ribojimai
    usage_limit = db.Column(db.Integer, nullable=True)
    used_count = db.Column(db.Integer, default=0, nullable=False)

    # Galiojimo laikas
    valid_from = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    valid_until = db.Column(
        db.DateTime(timezone=True),
        nullable=True
    )

    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Sekimo laukai
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    modified_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    is_deleted = db.Column(db.Boolean, default=False, nullable=False)

    # Santykis su Order
    orders = db.relationship(
        "Order",
        back_populates="discount",
        foreign_keys="Order.discount_id"
    )

    def __repr__(self):
        return f"<Discount code={self.code} type={self.discount_type} value={self.value}>"
