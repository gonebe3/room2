from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DecimalField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange

class AdminUserForm(FlaskForm):
    username = StringField(
        "Vartotojo vardas",
        validators=[
            DataRequired(message="Įveskite vartotojo vardą."),
            Length(min=3, max=64)
        ]
    )
    email = StringField(
        "El. paštas",
        validators=[
            DataRequired(message="Įveskite el. paštą."),
            Email(message="Neteisingas el. pašto formatas.")
        ]
    )
    password = PasswordField(
        "Naujas slaptažodis",
        validators=[
            Optional(),
            Length(min=8, max=128, message="Slaptažodis turi būti bent 8 simbolių.")
        ]
    )
    role = SelectField(
        "Rolė",
        choices=[("user", "Naudotojas"), ("admin", "Administratorius")],
        default="user",
        validators=[DataRequired()]
    )
    balance = DecimalField(
        "Balansas (€)",
        places=2,
        rounding=None,
        validators=[
            DataRequired(message="Įveskite balansą."),
            NumberRange(min=0, message="Balansas negali būti neigiamas.")
        ]
    )
    is_active = BooleanField("Aktyvus naudotojas", default=True)
    submit = SubmitField("Išsaugoti")