from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.forms.balance_form import BalanceForm
from app.models.user import User

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html', user=current_user)

@user_bp.route('/balance', methods=['GET', 'POST'])
@login_required
def balance():
    form = BalanceForm()
    if form.validate_on_submit():
        current_user.balance += form.amount.data
        db.session.commit()
        flash('Balance updated.')
        return redirect(url_for('user.profile'))
    return render_template('user/balance.html', form=form)