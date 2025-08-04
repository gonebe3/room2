from app.utils.extensions import db
from sqlalchemy import func

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(32), default='pending', nullable=False)
    shipping_address = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.String(255), nullable=True)
    discount_id = db.Column(db.Integer, db.ForeignKey("discount.id"), nullable=True)

    created_on = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    modified_on = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    modified_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    user = db.relationship(
        "User",
        back_populates="orders",
        foreign_keys=[user_id]
    )
    order_items = db.relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    discount = db.relationship(
        "Discount",
        back_populates="orders",
        foreign_keys=[discount_id]
    )

    def __repr__(self):
        return f"<Order id={self.id} user_id={self.user_id} total={self.total_amount} status={self.status}>"