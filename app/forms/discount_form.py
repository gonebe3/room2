from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class DiscountForm(FlaskForm):
    code = StringField(
        'Nuolaidos kodas',
        validators=[
            DataRequired(message="Įveskite nuolaidos kodą."),
            Length(max=32, message="Kodas per ilgas (maks. 32 simboliai).")
        ]
    )
    description = StringField(
        'Aprašymas',
        validators=[
            Optional(),
            Length(max=200, message="Aprašymas per ilgas (maks. 200 simbolių).")
        ]
    )
    percentage = DecimalField(
        'Nuolaida (%)',
        validators=[
            Optional(),
            NumberRange(min=0, max=100, message="Procentinė nuolaida turi būti tarp 0 ir 100.")
        ]
    )
    value = DecimalField(
        'Fiksuota nuolaida (€)',
        validators=[
            Optional(),
            NumberRange(min=0, message="Fiksuota nuolaida negali būti neigiama.")
        ]
    )
    min_purchase = DecimalField(
        'Minimali pirkimo suma (€)',
        validators=[
            Optional(),
            NumberRange(min=0, message="Minimali suma negali būti neigiama.")
        ]
    )
    expires_on = DateField(
        'Galioja iki',
        format='%Y-%m-%d',
        validators=[Optional()],
        render_kw={"placeholder": "YYYY-MM-DD"}
    )
    usage_limit = IntegerField(
        'Panaudojimų skaičius',
        validators=[Optional(), NumberRange(min=1, message="Mažiausiai 1 kartas.")]
    )
    submit = SubmitField('Išsaugoti nuolaidą')