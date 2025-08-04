from datetime import datetime, timezone
from app.utils.extensions import db

class Discount(db.Model):
    __tablename__ = "discount"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), unique=True, nullable=False)  # Kupono kodas
    description = db.Column(db.String(255), nullable=True)
    discount_type = db.Column(db.String(16), nullable=False)  # 'percent' arba 'fixed'
    value = db.Column(db.Numeric(10, 2), nullable=False)      # Nuolaidos dydis (pvz., 10 arba 10.00)
    usage_limit = db.Column(db.Integer, nullable=True)        # Kiek kartų galima panaudoti (None - neribota)
    used_count = db.Column(db.Integer, default=0, nullable=False)
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

    def __repr__(self):
        return f"<Discount {self.code} type={self.discount_type} value={self.value}>"