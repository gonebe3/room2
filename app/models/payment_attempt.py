from app.utils.extensions import db
from datetime import datetime, timezone

class PaymentAttempt(db.Model):
    __tablename__ = "payment_attempts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    session_id = db.Column(db.String(128), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=True)
    status = db.Column(db.String(32), nullable=False)  # e.g. 'success', 'canceled'
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    error_message = db.Column(db.String(256), nullable=True)

    user = db.relationship("User", back_populates="payment_attempts", foreign_keys=[user_id])

    def __repr__(self):
        return f"<PaymentAttempt user={self.user_id} session={self.session_id} status={self.status}>"
