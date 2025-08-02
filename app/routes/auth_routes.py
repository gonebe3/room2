from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.forms.login_form import LoginForm
from app.forms.register_form import RegisterForm
from app.services.user_service import authenticate_user, register_new_user
from app.utils.extensions import db
from app.models.user import User
from app.utils.password_hash import check_password_hash

from app.models.login_attempt import LoginAttempt
from datetime import datetime, timedelta, timezone


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data

        # Surask ar yra bandymų įrašas šiam vartotojui
        attempt = LoginAttempt.query.filter_by(username=username).first()
        now = datetime.now(timezone.utc)

        blocked_until = attempt.blocked_until if attempt else None
        # Užtikrinam, kad abu datetimes būtų offset-aware
        if blocked_until is not None and blocked_until.tzinfo is None:
            blocked_until = blocked_until.replace(tzinfo=timezone.utc)

        if attempt and blocked_until and blocked_until > now:
            time_left = int((blocked_until - now).total_seconds())
            minutes, seconds = divmod(time_left, 60)
            flash(f'Per daug neteisingų bandymų. Bandykite po {minutes} min. {seconds} s.', 'danger')
            return render_template('auth/login.html', form=form)

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            # Prisijungimas sėkmingas – ištrinam bandymus
            if attempt:
                db.session.delete(attempt)
                db.session.commit()
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('main.home'))

        # Prisijungimas nesėkmingas
        if not attempt:
            attempt = LoginAttempt(username=username, attempts=1, last_attempt=now, blocked_until=None)
            db.session.add(attempt)
        else:
            attempt.attempts += 1
            attempt.last_attempt = now
            if attempt.attempts == 3:
                attempt.blocked_until = now + timedelta(minutes=5)
            elif attempt.attempts == 4:
                attempt.blocked_until = now + timedelta(hours=1)
            elif attempt.attempts >= 5:
                attempt.blocked_until = now + timedelta(hours=5)
        db.session.commit()
        flash('Neteisingi prisijungimo duomenys.', 'danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Jei jau prisijungęs – iškart peradresuojam į profilį
    if current_user.is_authenticated:
        return redirect(url_for('user.profile'))

    form = RegisterForm()
    if form.validate_on_submit():
        user, error = register_new_user(form)
        if user:
            flash('Registracija sėkminga. Galite prisijungti.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(error or 'Klaida registruojant vartotoją.', 'danger')
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Atsijungėte.', 'info')
    return redirect(url_for('auth.login'))