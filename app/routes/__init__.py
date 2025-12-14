from flask import Blueprint

auth_bp = Blueprint('auth', __name__)
dashboard_bp = Blueprint('dashboard', __name__)
applications_bp = Blueprint('applications', __name__)

from app.routes import auth, dashboard, applications