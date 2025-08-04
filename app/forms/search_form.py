from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField

class SearchForm(FlaskForm):
    search_text = StringField('Ieškoti prekių...')
    sort_by = SelectField('Rikiuoti pagal', choices=[
        ('default', 'Rikiuoti pagal'),
        ('price_asc', 'Kaina: nuo mažiausios'),
        ('price_desc', 'Kaina: nuo didžiausios'),
        ('best_rated', 'Geriausiai įvertintos'),
        ('most_popular', 'Populiariausios'),
    ])
    submit = SubmitField('Filtruoti')
    
    