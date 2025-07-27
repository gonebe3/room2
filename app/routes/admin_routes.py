from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.user import User

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/users')
@login_required
def user_list():
    # TODO: add admin role check
    users = User.query.all()
    return render_template('admin/user_list.html', users=users)