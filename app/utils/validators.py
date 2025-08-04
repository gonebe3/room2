import re
from wtforms.validators import ValidationError

# Slaptažodžio stiprumo regex: didžioji, mažoji, skaičius, spec. simbolis, min 8 simboliai
password_pattern = re.compile(
    r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
)

def validate_password_strong(form, field):
    """
    Tikrina ar slaptažodis pakankamai stiprus.
    Naudoti RegisterForm ir ChangePasswordForm.
    """
    if not password_pattern.match(field.data):
        raise ValidationError(
            "Slaptažodis turi būti bent 8 simbolių, turėti didžiąją, mažąją, skaičių ir specialų simbolį."
        )