# filename: app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_apscheduler import APScheduler
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'
csrf = CSRFProtect()
scheduler = APScheduler()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Initialize Scheduler
    from app.services.notifications import check_upcoming_deadlines
    scheduler.init_app(app)
    
    if not app.config.get('TESTING'):
        scheduler.start()
    
    # Schedule jobs
    if not app.config.get('TESTING'):
        @scheduler.task('interval', id='check_deadlines', hours=24)
        def scheduled_deadline_check():
            check_upcoming_deadlines(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.applications import applications_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(applications_bp, url_prefix='/applications')
    
    # Error handlers
    from app import errors
    app.register_error_handler(404, errors.page_not_found)
    app.register_error_handler(500, errors.internal_server_error)
    
    # Context processors
    @app.context_processor
    def utility_processor():
        from datetime import datetime
        from app.utils import get_status_color, get_days_remaining, get_urgency_class, format_date
        
        return dict(
            datetime=datetime,
            get_status_color=get_status_color,
            get_days_remaining=get_days_remaining,
            get_urgency_class=get_urgency_class,
            format_date=format_date,
            now=datetime.now
        )
    
    return app