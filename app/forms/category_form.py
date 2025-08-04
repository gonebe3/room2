from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class CategoryForm(FlaskForm):
    name = StringField(
        'Kategorijos pavadinimas',
        validators=[
            DataRequired(message="Įveskite kategorijos pavadinimą."),
            Length(max=100, message="Pavadinimas per ilgas.")
        ]
    )
    description = TextAreaField(
        'Aprašymas',
        validators=[
            Optional(),
            Length(max=1000, message="Aprašymas per ilgas.")
        ]
    )
    submit = SubmitField('Išsaugoti')