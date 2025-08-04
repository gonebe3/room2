from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, IntegerField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError

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
    discount_type = SelectField(
        'Nuolaidos tipas',
        choices=[
            ('percent', 'Procentinė'),
            ('fixed', 'Fiksuota'),
            ('loyalty', 'Lojalumo')
        ],
        validators=[DataRequired(message="Pasirinkite nuolaidos tipą.")]
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
    loyalty_min_orders = IntegerField(
        'Min. pirkimų skaičius',
        validators=[
            Optional(),
            NumberRange(min=1, message="Minimalių pirkimų skaičius turi būti bent 1.")
        ]
    )
    loyalty_min_amount = DecimalField(
        'Minimali suma lojalumo (€)',
        validators=[
            Optional(),
            NumberRange(min=0, message="Minimali suma negali būti neigiama.")
        ]
    )
    loyalty_period_days = IntegerField(
        'Laikotarpis dienomis',
        validators=[
            Optional(),
            NumberRange(min=1, message="Laikotarpis turi būti bent 1 diena.")
        ]
    )
    valid_from = DateField(
        'Galioja nuo',
        format='%Y-%m-%d',
        validators=[Optional()],
        render_kw={"placeholder": "YYYY-MM-DD"}
    )
    valid_until = DateField(
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

    def validate(self, extra_validators=None):
        rv = super().validate()
        if not rv:
            return False

        dt = self.discount_type.data
        # Tikriname pagal tipą
        if dt == 'percent' and (self.percentage.data is None):
            self.percentage.errors.append('Įveskite procentinę nuolaidą.')
            return False
        if dt == 'fixed' and (self.value.data is None):
            self.value.errors.append('Įveskite fiksuotą nuolaidą.')
            return False
        if dt == 'loyalty':
            if not (self.loyalty_min_orders.data or self.loyalty_min_amount.data):
                msg = 'Nurodykite bent pirkimų skaičių arba sumą lojalumo kriterijui.'
                self.loyalty_min_orders.errors.append(msg)
                self.loyalty_min_amount.errors.append(msg)
                return False
            if self.loyalty_period_days.data is None:
                self.loyalty_period_days.errors.append('Įveskite lojalumo periodo trukmę dienomis.')
                return False
        return True
