from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.extensions import db, login_manager
from app.models.user import User
from app.forms.login_form import LoginForm
from app.forms.register_form import RegisterForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        now = datetime.utcnow()
        if user:
            if user.locked_until and user.locked_until > now:
                flash('Account locked. Try again later.')
                return redirect(url_for('auth.login'))
            if user.check_password(form.password.data):
                user.login_attempts = 0
                user.locked_until = None
                db.session.commit()
                login_user(user)
                return redirect(url_for('user.profile'))
            else:
                user.login_attempts += 1
                if user.login_attempts >= 5:
                    user.locked_until = now + timedelta(minutes=15)
                db.session.commit()
                flash('Invalid credentials.')
        else:
            flash('Invalid credentials.')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))