from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp

class RegisterForm(FlaskForm):
    username = StringField(
        'Vartotojo vardas',
        validators=[
            DataRequired(message="Įveskite vartotojo vardą."),
            Length(min=3, max=64, message="Vartotojo vardas turi būti 3-64 simbolių.")
        ]
    )
    email = StringField(
        'El. paštas',
        validators=[
            DataRequired(message="Įveskite el. paštą."),
            Email(message="Neteisingas el. pašto formatas.")
        ]
    )
    password = PasswordField(
        'Slaptažodis',
        validators=[
            DataRequired(message="Įveskite slaptažodį."),
            Length(min=8, max=128, message="Slaptažodis turi būti bent 8 simbolių."),
            Regexp(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$',
                message="Slaptažodyje turi būti didžiųjų ir mažųjų raidžių, bei bent vienas skaičius."
            )
        ]
    )
    confirm_password = PasswordField(
        'Pakartokite slaptažodį',
        validators=[
            DataRequired(message="Pakartokite slaptažodį."),
            EqualTo('password', message="Slaptažiai nesutampa.")
        ]
    )
    submit = SubmitField('Registruotis')