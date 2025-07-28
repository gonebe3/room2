from app.models.user import User
from app.utils.extensions import db
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

def get_user_by_username(username: str):
    try:
        with db.session() as session:
            stmt = select(User).where(User.username == username)
            return session.execute(stmt).scalar_one_or_none()
    except SQLAlchemyError:
        return None

def get_user_by_email(email: str):
    try:
        with db.session() as session:
            stmt = select(User).where(User.email == email)
            return session.execute(stmt).scalar_one_or_none()
    except SQLAlchemyError:
        return None

def authenticate_user(username: str, password: str):
    user = get_user_by_username(username)
    if user and user.check_password(password):
        return user
    return None

def register_new_user(username: str, email: str, password: str):
    try:
        user = User(username=username, email=email)
        user.set_password(password)
        with db.session() as session:
            session.add(user)
            session.commit()
            return user
    except SQLAlchemyError:
        return None

def update_user_balance(user_id: int, amount: float) -> bool:
    try:
        with db.session() as session:
            stmt = select(User).where(User.id == user_id)
            user = session.execute(stmt).scalar_one_or_none()
            if user:
                user.balance += amount
                session.commit()
                return True
            return False
    except SQLAlchemyError:
        return False