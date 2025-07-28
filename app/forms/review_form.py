from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length

class ReviewForm(FlaskForm):
    rating = IntegerField(
        'Įvertinimas (1-5)',
        validators=[
            DataRequired(message="Nurodykite įvertinimą."),
            NumberRange(min=1, max=5, message="Įvertinimas turi būti nuo 1 iki 5.")
        ]
    )
    comment = TextAreaField(
        'Komentaras',
        validators=[
            Length(max=1000, message="Komentaras per ilgas (maks. 1000 simbolių).")
        ]
    )
    submit = SubmitField('Pateikti atsiliepimą')