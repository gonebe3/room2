import re
from wtforms.validators import ValidationError

password_pattern = re.compile(
    r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
)

def password_regex(form, field):
    if not password_pattern.match(field.data):
        raise ValidationError(
            'Password must be at least 8 characters long, include uppercase, lowercase, number, and special character.'
        )