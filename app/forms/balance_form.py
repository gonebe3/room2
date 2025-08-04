from flask_wtf import FlaskForm
from wtforms import DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class BalanceForm(FlaskForm):
    amount = DecimalField(
        'Suma (€)',
        validators=[
            DataRequired(message="Privaloma nurodyti sumą."),
            NumberRange(min=0.01, message="Suma turi būti didesnė nei 0.")
        ],
        places=2,  # 2 skaičiai po kablelio
        render_kw={"placeholder": "Pvz.: 10.00"}
    )
    submit = SubmitField('Papildyti balansą')