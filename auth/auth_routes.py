# Insert a route to users.html here

from flask import Blueprint, render_template
from auth.users_model import User

auth_bp = Blueprint('auth', __name__, template_folder='.')

@auth_bp.route('/users')
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('auth/users.html', users=users)