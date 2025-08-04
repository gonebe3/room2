from app.utils.extensions import db
from sqlalchemy import func

class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Kaina tuo metu, kai buvo perkama

    # Audit fields (sukūrimo ir atnaujinimo sekimas)
    created_on = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    modified_on = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False
    )
    modified_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)

    # Relationship’ai (naudojam back_populates abiejose pusėse!)
    order = db.relationship(
        "Order",
        back_populates="order_items",
        foreign_keys=[order_id]
    )
    product = db.relationship(
        "Product",
        back_populates="order_items",
        foreign_keys=[product_id]
    )
    creator = db.relationship(
        "User",
        foreign_keys=[created_by],
        uselist=False,
        post_update=True
    )
    modifier = db.relationship(
        "User",
        foreign_keys=[modified_by],
        uselist=False,
        post_update=True
    )

    def __repr__(self):
        return (
            f"<OrderItem id={self.id} order_id={self.order_id} "
            f"product_id={self.product_id} qty={self.quantity} price={self.price} is_deleted={self.is_deleted}>"
        )