# app/__init__.py
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from datetime import timedelta
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_class=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Load configuration
    if config_class:
        app.config.from_object(config_class)
    else:
        from app.config import Config

        app.config.from_object(Config)

    # Configure session timeout (SR-03: 15 menit)
    @app.before_request
    def make_session_permanent():
        session.permanent = True
        # Ambil nilai dari config
        timeout_value = app.config.get("PERMANENT_SESSION_LIFETIME", 900)

        # Pastikan timeout_value adalah integer (detik)
        if isinstance(timeout_value, timedelta):
            timeout_seconds = int(timeout_value.total_seconds())
        else:
            timeout_seconds = int(timeout_value)

        app.permanent_session_lifetime = timedelta(seconds=timeout_seconds)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)

    # Login configuration
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Silakan login untuk mengakses halaman ini."
    login_manager.login_message_category = "warning"

    # Register blueprints
    from app.routes import auth, notes, admin, main

    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(notes.notes_bp)
    app.register_blueprint(admin.admin_bp)
    app.register_blueprint(main.main_bp)

    # Create database tables
    with app.app_context():
        db.create_all()
        create_default_admin()

    return app


def create_default_admin():
    """Create default admin user if not exists (SR-05: RBAC)"""
    from app.models.user import User

    admin = User.query.filter_by(role="admin").first()
    if not admin:
        admin = User(username="admin", email="admin@securenotes.com", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created: admin / admin123")
