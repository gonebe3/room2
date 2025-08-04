from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password: str) -> str:
    """
    Sugeneruoja saugų hash'ą slaptažodžiui.
    Naudoja werkzeug.security .
    """
    return generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)

def verify_password(hash: str, password: str) -> bool:
    """
    Patikrina ar įvestas slaptažodis atitinka saugomą hash'ą.
    """
    return check_password_hash(hash, password)