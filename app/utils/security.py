# app/utils/security.py
import re
from flask import request, session, current_app
from functools import wraps
from urllib.parse import urlparse, urljoin


# ============ INPUT VALIDATION (SR-04) ============


def validate_username(username):
    """
    Validate username:
    - 3-20 characters
    - Only letters, numbers, underscore, dot
    - Cannot start or end with dot/underscore
    """
    if not username:
        return False, "Username tidak boleh kosong."

    if len(username) < 3:
        return False, "Username minimal 3 karakter."

    if len(username) > 20:
        return False, "Username maksimal 20 karakter."

    # Only alphanumeric, underscore, dot
    if not re.match(r"^[a-zA-Z0-9_.]+$", username):
        return (
            False,
            "Username hanya boleh berisi huruf, angka, underscore (_), dan titik (.).",
        )

    # Cannot start or end with dot or underscore
    if username[0] in "_.":
        return (
            False,
            "Username tidak boleh dimulai dengan underscore (_) atau titik (.).",
        )

    if username[-1] in "_.":
        return (
            False,
            "Username tidak boleh diakhiri dengan underscore (_) atau titik (.).",
        )

    return True, ""


def validate_email(email):
    """
    Validate email format
    """
    if not email:
        return False, "Email tidak boleh kosong."

    # Basic email regex
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(email_regex, email):
        return False, "Format email tidak valid."

    if len(email) > 120:
        return False, "Email maksimal 120 karakter."

    return True, ""


def validate_password(password):
    """
    Validate password strength:
    - Minimum 8 characters
    - At least 1 uppercase
    - At least 1 lowercase
    - At least 1 digit
    """
    if not password:
        return False, "Password tidak boleh kosong."

    if len(password) < 8:
        return False, "Password minimal 8 karakter."

    if len(password) > 100:
        return False, "Password maksimal 100 karakter."

    # Check for uppercase
    if not re.search(r"[A-Z]", password):
        return False, "Password harus mengandung setidaknya 1 huruf besar."

    # Check for lowercase
    if not re.search(r"[a-z]", password):
        return False, "Password harus mengandung setidaknya 1 huruf kecil."

    # Check for digit
    if not re.search(r"[0-9]", password):
        return False, "Password harus mengandung setidaknya 1 angka."

    return True, ""


def validate_note_title(title):
    """
    Validate note title:
    - 1-200 characters
    - No XSS payloads
    """
    if not title or not title.strip():
        return False, "Judul catatan tidak boleh kosong."

    if len(title) > 200:
        return False, "Judul catatan maksimal 200 karakter."

    # Basic XSS pattern detection
    dangerous_patterns = [
        r"<script",
        r"javascript:",
        r"onload=",
        r"onclick=",
        r"onerror=",
        r"<iframe",
        r"<object",
        r"<embed",
    ]

    title_lower = title.lower()
    for pattern in dangerous_patterns:
        if pattern in title_lower:
            return False, "Judul mengandung karakter yang tidak diizinkan."

    return True, ""


def validate_note_content(content):
    """
    Validate note content:
    - Max 10000 characters
    """
    if not content:
        return True, ""  # Content can be empty

    if len(content) > 10000:
        return False, "Isi catatan maksimal 10000 karakter."

    return True, ""


# ============ INPUT SANITIZATION ============


def sanitize_input(text):
    """
    Sanitize user input to prevent XSS
    Remove/escape dangerous characters
    """
    if not text:
        return ""

    # Convert to string if not already
    text = str(text)

    # Replace dangerous HTML characters
    sanitized = text.replace("&", "&amp;")
    sanitized = sanitized.replace("<", "&lt;")
    sanitized = sanitized.replace(">", "&gt;")
    sanitized = sanitized.replace('"', "&quot;")
    sanitized = sanitized.replace("'", "&#39;")

    return sanitized


def sanitize_note_content(content):
    """
    Sanitize note content while preserving line breaks
    """
    if not content:
        return ""

    # First sanitize HTML
    sanitized = sanitize_input(content)

    # Convert line breaks to <br> for display
    # But store original with \n in database

    return sanitized


# ============ RATE LIMITING (SR-02) ============


class RateLimiter:
    """
    Simple in-memory rate limiter for login attempts
    """

    def __init__(self):
        self.attempts = {}

    def is_allowed(self, key, max_attempts=5, window_seconds=300):
        """
        Check if request is allowed
        key: identifier (e.g., IP address or username)
        max_attempts: maximum attempts allowed
        window_seconds: time window in seconds
        """
        import time

        now = time.time()

        # Clean old entries
        if key in self.attempts:
            # Remove attempts older than window
            self.attempts[key] = [
                timestamp
                for timestamp in self.attempts[key]
                if now - timestamp < window_seconds
            ]

        # Check if over limit
        if key in self.attempts and len(self.attempts[key]) >= max_attempts:
            return False

        return True

    def add_attempt(self, key):
        """Add an attempt for the key"""
        import time

        now = time.time()

        if key not in self.attempts:
            self.attempts[key] = []

        self.attempts[key].append(now)

    def reset_attempts(self, key):
        """Reset attempts for a key"""
        if key in self.attempts:
            del self.attempts[key]


# Global rate limiter instance
login_rate_limiter = RateLimiter()


# ============ AUTHORIZATION HELPERS ============


def is_safe_url(target):
    """
    Ensure redirect URL is safe (not to external sites)
    """
    if not target:
        return False

    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def get_redirect_target():
    """
    Get safe redirect target from request args or referrer
    """
    target = request.args.get("next")

    if target and is_safe_url(target):
        return target

    return None


# ============ CSRF PROTECTION HELPERS ============


def generate_csrf_token():
    """
    Generate CSRF token for forms
    """
    import secrets

    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)

    return session["_csrf_token"]


def validate_csrf_token(token):
    """
    Validate CSRF token
    """
    if not token:
        return False

    return token == session.get("_csrf_token")


# ============ SQL INJECTION PREVENTION ============


def escape_like_string(string):
    """
    Escape special characters for SQL LIKE queries
    """
    # Escape % and _ characters
    return string.replace("%", "\\%").replace("_", "\\_")


# ============ SECURITY HEADERS ============


def add_security_headers(response):
    """
    Add security headers to HTTP response
    """
    # X-Content-Type-Options: Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # X-Frame-Options: Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"

    # X-XSS-Protection: Enable XSS filtering
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Referrer-Policy: Control referrer info
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    return response
