from datetime import datetime, timezone
from app.utils.extensions import db

class Review(db.Model):
    __tablename__ = "review"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=True)
    rating = db.Column(db.Integer, nullable=False)  # 1–5
    comment = db.Column(db.Text, nullable=True)
    

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)

    # Ryšiai
    user = db.relationship(
        "User",
        back_populates="reviews",
        foreign_keys=[user_id]
    )
    product = db.relationship(
        "Product",
        back_populates="reviews",
        foreign_keys=[product_id]
    )
    order = db.relationship(
        "Order", backref="reviews",
          foreign_keys=[order_id]
    )

    def __repr__(self):
        return f"<Review {self.id} | User: {self.user_id} | Product: {self.product_id} | Rating: {self.rating}>"
