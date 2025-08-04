from app.models.user import User
from app.models.order import Order
from app.utils.extensions import db
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# --- CRUD ir paieškos ---

def get_user_by_id(user_id: int):
    """Gauti vartotoją pagal ID."""
    try:
        with db.session() as session:
            return session.get(User, user_id)
    except SQLAlchemyError as e:
        print(f"Klaida gaunant user pagal ID: {e}")
        return None

def get_user_by_username(username: str):
    """Gauti vartotoją pagal vartotojo vardą."""
    try:
        with db.session() as session:
            stmt = select(User).where(User.username == username)
            return session.execute(stmt).scalar_one_or_none()
    except SQLAlchemyError as e:
        print(f"Klaida gaunant user pagal username: {e}")
        return None

def get_user_by_email(email: str):
    """Gauti vartotoją pagal el. pašto adresą."""
    try:
        with db.session() as session:
            stmt = select(User).where(User.email == email)
            return session.execute(stmt).scalar_one_or_none()
    except SQLAlchemyError as e:
        print(f"Klaida gaunant user pagal email: {e}")
        return None

def get_all_users():
    """Gražina visų vartotojų sąrašą (be ištrintų)."""
    try:
        with db.session() as session:
            stmt = select(User).where(User.is_deleted == False)
            return session.execute(stmt).scalars().all()
    except SQLAlchemyError as e:
        print(f"Klaida gaunant visus users: {e}")
        return []

# --- Registracija / kūrimas ---

def register_new_user(form):
    """
    Registruoja naują vartotoją pagal WTForm objektą.
    Grąžina (user, error) – jei error None, registracija sėkminga.
    """
    try:
        if get_user_by_username(form.username.data):
            return None, "Toks vartotojo vardas jau egzistuoja."
        if get_user_by_email(form.email.data):
            return None, "Toks el. pašto adresas jau naudojamas."
        user = User(
            username=form.username.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        with db.session() as session:
            session.add(user)
            session.commit()
            return user, None
    except IntegrityError:
        db.session.rollback()
        return None, "Unikalumo klaida – vartotojas ar el. paštas jau naudojamas."
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Registracijos klaida: {e}")
        return None, "Įvyko klaida registruojant vartotoją."

def admin_create_user(form):
    """
    Administratoriaus rankinis vartotojo kūrimas (leidžia nurodyti papildomus laukus, pvz., role, is_active).
    """
    try:
        if get_user_by_username(form.username.data):
            return None, "Toks vartotojo vardas jau egzistuoja."
        if get_user_by_email(form.email.data):
            return None, "Toks el. pašto adresas jau naudojamas."
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data if hasattr(form, 'role') else 'user',
            is_active=form.is_active.data if hasattr(form, 'is_active') else True,
            balance=form.balance.data if hasattr(form, 'balance') else 0.00,
        )
        user.set_password(form.password.data)
        with db.session() as session:
            session.add(user)
            session.commit()
            return user, None
    except IntegrityError:
        db.session.rollback()
        return None, "Unikalumo klaida – vartotojas ar el. paštas jau naudojamas."
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Admino vartotojo kūrimo klaida: {e}")
        return None, "Įvyko klaida kuriant vartotoją (admin)."

# --- Autentifikacija ---

def authenticate_user(username: str, password: str):
    """Patikrina vartotojo vardą ir slaptažodį."""
    user = get_user_by_username(username)
    if user and user.check_password(password) and not user.is_deleted:
        return user
    return None

# --- Profilio atnaujinimas (naudotojo) ---

def update_user_profile(user_id: int, data: dict) -> bool:
    """Atnaujina vartotojo profilio laukus pagal žemėlapį (dict) – leidžiama keisti tik username ir email."""
    try:
        with db.session() as session:
            user = session.get(User, user_id)
            if not user or user.is_deleted:
                return False
            for key in ['username', 'email']:
                if key in data:
                    setattr(user, key, data[key])
            session.commit()
            return True
    except SQLAlchemyError as e:
        print(f"Klaida atnaujinant user profilį: {e}")
        return False

def admin_update_user(user_id: int, data: dict) -> bool:
    """
    Leidžia adminui atnaujinti bet kuriuos naudotojo laukus: role, is_active, balance ir t.t.
    """
    try:
        with db.session() as session:
            user = session.get(User, user_id)
            if not user or user.is_deleted:
                return False
            for key, value in data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            session.commit()
            return True
    except SQLAlchemyError as e:
        print(f"Klaida atnaujinant user (admin): {e}")
        return False

# --- Balanso papildymas ---

def update_user_balance(user_id: int, amount: float) -> bool:
    """Atnaujina vartotojo balansą (prideda amount)."""
    try:
        with db.session() as session:
            user = session.get(User, user_id)
            if user and not user.is_deleted:
                user.balance += amount
                session.commit()
                return True
            return False
    except SQLAlchemyError as e:
        print(f"Klaida papildant balansą: {e}")
        return False

def admin_set_user_balance(user_id: int, balance: float) -> bool:
    """Adminas gali nustatyti (ne tik papildyti) vartotojo balansą."""
    try:
        with db.session() as session:
            user = session.get(User, user_id)
            if user and not user.is_deleted:
                user.balance = balance
                session.commit()
                return True
            return False
    except SQLAlchemyError as e:
        print(f"Klaida adminui nustatant balansą: {e}")
        return False

# --- Soft delete (tik admin) ---

def delete_user(user_id: int) -> bool:
    """Soft delete – pažymi vartotoją kaip ištrintą (naudoti TIK admin route!)."""
    try:
        with db.session() as session:
            user = session.get(User, user_id)
            if user and not user.is_deleted:
                user.is_deleted = True
                session.commit()
                return True
            return False
    except SQLAlchemyError as e:
        print(f"Klaida trinant user: {e}")
        return False

# --- Užsakymų gavimas ---

def get_user_orders(user_id: int):
    """Gauti visus vartotojo užsakymus (naudotojo ar admin peržiūrai)."""
    try:
        with db.session() as session:
            stmt = select(Order).where(Order.user_id == user_id)
            return session.execute(stmt).scalars().all()
    except SQLAlchemyError as e:
        print(f"Klaida gaunant user užsakymus: {e}")
        return []
