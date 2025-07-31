from app.utils.extensions import db
from sqlalchemy.sql import func
 
class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    attempts = db.Column(db.Integer, default=0)
    last_attempt = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    blocked_until = db.Column(db.DateTime, nullable=True)
 