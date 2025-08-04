from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

class OrderForm(FlaskForm):
    shipping_address = TextAreaField(
        'Pristatymo adresas',
        validators=[
            DataRequired(message="Įveskite pristatymo adresą."),
            Length(max=500, message="Adresas per ilgas (maks. 500 simbolių).")
        ]
    )
    recipient_name = StringField(
        'Gavėjo vardas, pavardė',
        validators=[
            DataRequired(message="Įveskite gavėjo vardą ir pavardę."),
            Length(max=128)
        ]
    )
    recipient_phone = StringField(
        'Gavėjo telefonas',
        validators=[
            DataRequired(message="Įveskite telefono numerį."),
            Length(max=30)
        ]
    )
    discount_code = StringField(
        'Nuolaidos kodas',
        validators=[
            Optional(),
            Length(max=32, message="Kodas per ilgas (maks. 32 simboliai).")
        ],
        render_kw={"placeholder": "Įveskite nuolaidos kodą"}
    )
    total_price = DecimalField(
        'Suma (€)',
        places=2,
        render_kw={'readonly': True}  # UI rodo, bet redaguoti negalima
    )
    submit = SubmitField('Patvirtinti užsakymą')
