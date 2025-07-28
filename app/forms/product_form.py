from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, DecimalField, IntegerField,
    BooleanField, FileField, SubmitField
)
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from flask_wtf.file import FileAllowed

ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "svg", "webp"]

class ProductForm(FlaskForm):
    name = StringField(
        'Pavadinimas',
        validators=[DataRequired(), Length(max=100, message="Pavadinimas per ilgas.")]
    )
    description = TextAreaField(
        'Aprašymas',
        validators=[Optional(), Length(max=1500, message="Aprašymas per ilgas.")]
    )
    price = DecimalField(
        'Kaina (€)',
        places=2,
        rounding=None,
        validators=[
            DataRequired(message="Nurodykite kainą."),
            NumberRange(min=0, message="Kaina turi būti teigiama.")
        ]
    )
    quantity = IntegerField(
        'Kiekis',
        validators=[
            DataRequired(message="Nurodykite kiekį."),
            NumberRange(min=0, message="Kiekis turi būti neneigiamas.")
        ]
    )
    image = FileField(
        'Nuotrauka',
        validators=[
            Optional(),
            FileAllowed(ALLOWED_IMAGE_EXTENSIONS, "Leidžiami tik paveikslėlių formatai: jpg, png, svg ir pan.")
        ]
    )
    is_active = BooleanField('Aktyvus (matomas parduotuvėje)')
    submit = SubmitField('Išsaugoti prekę')