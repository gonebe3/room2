from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SelectField, DecimalField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

class AdminOrderForm(FlaskForm):
    user_id = IntegerField('Vartotojo ID', validators=[DataRequired()])
    status = SelectField(
        'Būsena',
        choices=[
            ('pending', 'Laukia apmokėjimo'),
            ('paid', 'Apmokėtas'),
            ('shipped', 'Išsiųstas'),
            ('completed', 'Įvykdytas'),
            ('canceled', 'Atšauktas'),
        ],
        validators=[DataRequired()]
    )
    total_amount = DecimalField('Suma', validators=[DataRequired(), NumberRange(min=0)])
    shipping_address = StringField('Pristatymo adresas', validators=[Optional()])
    notes = TextAreaField('Pastabos', validators=[Optional()])
    discount_id = IntegerField('Nuolaidos ID', validators=[Optional()])
    submit = SubmitField('Išsaugoti')