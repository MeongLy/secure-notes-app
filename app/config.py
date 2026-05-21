# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # Database
    SQLALCHEMY_DATABASE_URI = "sqlite:///notes.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session Security (SR-03: Session timeout 15 menit)
    SESSION_TIMEOUT_MINUTES = int(os.environ.get("SESSION_TIMEOUT_MINUTES", 15))
    PERMANENT_SESSION_LIFETIME = SESSION_TIMEOUT_MINUTES * 60  # Convert to seconds

    # Cookie Security
    SESSION_COOKIE_HTTPONLY = True  # Prevent XSS access to session cookie
    SESSION_COOKIE_SAMESITE = "Lax"  # CSRF protection
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS (SR-09)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_DURATION = 86400  # 1 day for remember me

    # Rate Limiting (SR-02: maksimal 5 percobaan login)
    MAX_LOGIN_ATTEMPTS = int(os.environ.get("MAX_LOGIN_ATTEMPTS", 5))
    LOGIN_ATTEMPT_WINDOW = 300  # 5 minutes window

    # Admin credentials
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

    # Logging
    SECURITY_LOG_FILE = os.environ.get("SECURITY_LOG_FILE", "security.log")

    # Input Validation
    MAX_NOTE_LENGTH = 10000
    MAX_TITLE_LENGTH = 200

    # Environment
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
    DEBUG = FLASK_ENV == "development"

    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "uploads"
    )
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size
    ALLOWED_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "gif",
        "pdf",
        "txt",
        "doc",
        "docx",
        "xlsx",
    }
    ALLOWED_MIMETYPES = {
        "image/png",
        "image/jpeg",
        "image/jpg",
        "image/gif",
        "application/pdf",
        "text/plain",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }
