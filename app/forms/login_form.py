from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField(
        'Vartotojo vardas',
        validators=[DataRequired(message="Įveskite vartotojo vardą."), Length(max=64)]
    )
    password = PasswordField(
        'Slaptažodis',
        validators=[DataRequired(message="Įveskite slaptažodį."), Length(min=8, max=128)]
    )
    remember_me = BooleanField('Prisiminti mane')
    submit = SubmitField('Prisijungti')