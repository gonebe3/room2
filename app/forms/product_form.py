from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, DecimalField, IntegerField,
    BooleanField, FileField, SubmitField, SelectField
)
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from flask_wtf.file import FileAllowed

ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "svg", "webp"]

class ProductForm(FlaskForm):
    name = StringField(
        'Pavadinimas',
        validators=[DataRequired(), Length(max=120, message="Pavadinimas per ilgas.")]
    )
    description = TextAreaField(
        'Aprašymas',
        validators=[Optional(), Length(max=1500, message="Aprašymas per ilgas.")]
    )
    price = DecimalField(
        'Kaina (€)',
        places=2,
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
    
    category = SelectField('Kategorija', coerce=int, validators=[DataRequired(message="Pasirinkite kategoriją.")])
    

    image = FileField(
        'Nuotrauka',
        validators=[
            Optional(),
            FileAllowed(ALLOWED_IMAGE_EXTENSIONS, "Leidžiami tik paveikslėliai: jpg, png, svg ir pan.")
        ]
    )
    is_active = BooleanField('Aktyvus (matomas parduotuvėje)')
    submit = SubmitField('Išsaugoti prekę')