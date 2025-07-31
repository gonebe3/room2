from sqlalchemy import Integer, ForeignKey, DateTime, Boolean, func
from app.utils.extensions import db

class Cart(db.Model):
    __tablename__ = "cart"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    added_on = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Sekimo laukai:
    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    modified_on = db.Column(db.DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now(), nullable=False)
    modified_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)

    # Ryšiai
    user = db.relationship(
        "User",
        back_populates="cart_items",
        foreign_keys=[user_id]
    )
    product = db.relationship(
        "Product",
        back_populates="cart_items",
        lazy="selectin"
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
            f"<Cart id={self.id} user_id={self.user_id} "
            f"product_id={self.product_id} qty={self.quantity} is_deleted={self.is_deleted}>"
        )