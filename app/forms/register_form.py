from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from sqlalchemy import select
from app.extensions import db
from app.models.user import User
from app.utils.validators import password_regex

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(), password_regex
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password')
    ])
    submit = SubmitField('Register')

    def validate_username(self, username):
        stmt = select(User).where(User.username == username.data)
        user = db.session.scalars(stmt).first()
        if user:
            raise ValidationError('Username already taken.')

    def validate_email(self, email):
        stmt = select(User).where(User.email == email.data)
        user = db.session.scalars(stmt).first()
        if user:
            raise ValidationError('Email already registered.')
