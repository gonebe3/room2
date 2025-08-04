from flask_wtf import FlaskForm
from wtforms import DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class BalanceForm(FlaskForm):
    amount = DecimalField('Top-up Amount', validators=[
        DataRequired(), NumberRange(min=0.01)
    ])
    submit = SubmitField('Add Funds')