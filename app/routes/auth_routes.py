from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.forms.login_form import LoginForm
from app.forms.register_form import RegisterForm
from app.services.user_service import authenticate_user, register_new_user
from app.utils.extensions import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Jei jau prisijungęs – iškart peradresuojam į profilį
    if current_user.is_authenticated:
        return redirect(url_for('user.profile'))

    form = LoginForm()
    if form.validate_on_submit():
        user = authenticate_user(form.username.data, form.password.data)
        if user:
            login_user(user, remember=form.remember_me.data)
            flash('Sėkmingai prisijungėte.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('user.profile'))
        else:
            flash('Neteisingas vartotojo vardas arba slaptažodis.', 'danger')
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