# app/__init__.py
from flask import Flask, session, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect, CSRFError
from datetime import timedelta
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_class=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Load configuration
    if config_class:
        app.config.from_object(config_class)
    else:
        from app.config import Config

        app.config.from_object(Config)

    # ============ CSRF PROTECTION ============
    csrf.init_app(app)

    # ============ CSRF ERROR HANDLER ============
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        """Handle CSRF token validation errors"""
        from app.utils.logger import log_security_event

        # Log the CSRF failure
        log_security_event(
            event_type="CSRF_FAILURE",
            details=f"CSRF token validation failed: {str(e)} | Path: {request.path} | IP: {request.remote_addr}",
            ip_address=request.remote_addr,
        )

        # Return error response
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return {"error": "CSRF token validation failed"}, 400
        else:
            return render_template("errors/csrf_error.html"), 400

    # ============ SESSION TIMEOUT (SR-03: 15 menit) ============
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

    # ============ SECURITY HEADERS (VULN-001 fix) ============
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses"""
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Enable XSS filtering
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response

    @app.after_request
    def log_security_events(response):
        """Log security-related events (4xx and 5xx errors)"""
        from app.utils.logger import log_security_event

        # Log untuk status code client error (4xx)
        if 400 <= response.status_code < 500:
            log_security_event(
                event_type="CLIENT_ERROR",
                details=f"Status: {response.status_code} | Path: {request.path} | IP: {request.remote_addr}",
                ip_address=request.remote_addr,
            )
        # Log untuk status code server error (5xx)
        elif response.status_code >= 500:
            log_security_event(
                event_type="SERVER_ERROR",
                details=f"Status: {response.status_code} | Path: {request.path} | IP: {request.remote_addr}",
                ip_address=request.remote_addr,
            )

        return response

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
