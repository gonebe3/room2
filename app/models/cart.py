# from sqlalchemy import Integer, ForeignKey, DateTime, func
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from app.utils.extensions import db

# class Cart(db.Model):
#     __tablename__ = "cart"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
#     product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), nullable=False)
#     quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
#     added_on: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

#     user = relationship("User", back_populates="cart_items")
#     product = relationship("Product", back_populates="cart_items")

#     def __repr__(self):
#         return f"<Cart id={self.id} user_id={self.user_id} product_id={self.product_id} qty={self.quantity}>"

# # Papildomai User ir Product modeliuose:
# # User:
# # cart_items = relationship("Cart", back_populates="user", cascade="all, delete-orphan")

# # Product:
# # cart_items = relationship("Cart", back_populates="product", cascade="all, delete-orphan")