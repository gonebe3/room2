from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class CartAddForm(FlaskForm):
    product_id = HiddenField(validators=[DataRequired()])
    quantity = IntegerField('Kiekis', validators=[
        DataRequired(message="Privaloma nurodyti kiekį."),
        NumberRange(min=1, max=100, message="Kiekis turi būti tarp 1 ir 100.")
    ])
    submit = SubmitField('Pridėti į krepšelį')

class CartUpdateForm(FlaskForm):
    cart_item_id = HiddenField(validators=[DataRequired()])
    quantity = IntegerField('Kiekis', validators=[
        DataRequired(message="Privaloma nurodyti kiekį."),
        NumberRange(min=1, max=100, message="Kiekis turi būti tarp 1 ir 100.")
    ])
    submit = SubmitField('Atnaujinti kiekį')