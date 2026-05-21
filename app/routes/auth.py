# app/routes/auth.py
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    current_app,
)
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from app import db
from app.models.user import User
from app.utils.logger import log_login_attempt, log_logout, log_unauthorized_access
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response
from app.utils.security import (
    validate_email,
    validate_username,
    validate_password,
    sanitize_input,
    is_safe_url,
    get_redirect_target,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ============ REGISTER ============
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """User registration with input validation (SR-04)"""

    # If user already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for("notes.dashboard"))

    if request.method == "POST":
        # Get form data
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # SR-04: Validate all inputs
        errors = []

        # Validate username
        username_valid, username_error = validate_username(username)
        if not username_valid:
            errors.append(username_error)

        # Validate email
        email_valid, email_error = validate_email(email)
        if not email_valid:
            errors.append(email_error)

        # Validate password
        password_valid, password_error = validate_password(password)
        if not password_valid:
            errors.append(password_error)

        # Check if passwords match
        if password != confirm_password:
            errors.append("Password dan konfirmasi password tidak sama.")

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            errors.append("Username sudah terdaftar.")

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            errors.append("Email sudah terdaftar.")

        # If no errors, create user
        if not errors:
            user = User(username=username, email=email)
            user.set_password(password)  # SR-01: bcrypt hashing

            db.session.add(user)
            db.session.commit()

            # Log registration
            log_login_attempt(username, True, reason="Registration successful")

            flash("Registrasi berhasil! Silakan login.", "success")
            return redirect(url_for("auth.login"))

        # If errors, show them
        for error in errors:
            flash(error, "danger")

    return render_template("auth/register.html")


# ============ LOGIN ============
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """User login with rate limiting (SR-02: max 5 attempts)"""

    if current_user.is_authenticated:
        return redirect(url_for("notes.dashboard"))

    if request.method == "POST":
        username = sanitize_input(request.form.get("username", "").strip())
        password = request.form.get("password", "")
        remember = request.form.get("remember", False)  # Remember me checkbox
        ip_address = request.remote_addr

        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        # SR-02: Check if account is locked
        if user and user.is_locked():
            flash(
                "Akun Anda terkunci karena terlalu banyak percobaan login gagal. Silakan coba lagi setelah 15 menit.",
                "danger",
            )
            log_login_attempt(username, False, ip_address, reason="Account locked")
            return render_template("auth/login.html")

        # Validate credentials
        if user and user.check_password(password):
            # SR-02: Reset login attempts on success
            user.reset_login_attempts()
            user.update_last_login()

            # SR-03 & SR-10: Login user dengan remember me
            login_user(user, remember=remember)

            # SR-03: Make session permanent with timeout
            session.permanent = True
            session["_fresh"] = True
            session["user_id"] = user.id
            session["username"] = user.username

            # Set session timeout from config
            timeout_minutes = current_app.config.get("SESSION_TIMEOUT_MINUTES", 15)
            session.permanent_session_lifetime = timedelta(minutes=timeout_minutes)

            # Log successful login
            log_login_attempt(user.username, True, ip_address)

            flash(f"Selamat datang kembali, {user.username}!", "success")

            # SR-09: Redirect ke next page atau dashboard (safe URL check)
            next_page = request.args.get("next")
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            return redirect(url_for("notes.dashboard"))

        else:
            # SR-02: Increment login attempts on failure
            if user:
                user.increment_login_attempts()

                # Lock account if max attempts reached
                if user.login_attempts >= current_app.config.get(
                    "MAX_LOGIN_ATTEMPTS", 5
                ):
                    user.lock_account()
                    flash(
                        "Terlalu banyak percobaan login gagal. Akun Anda dikunci selama 15 menit.",
                        "danger",
                    )
                    log_login_attempt(
                        user.username,
                        False,
                        ip_address,
                        reason="Account locked - max attempts exceeded",
                    )
                else:
                    remaining = (
                        current_app.config.get("MAX_LOGIN_ATTEMPTS", 5)
                        - user.login_attempts
                    )
                    flash(
                        f"Username atau password salah. Sisa percobaan: {remaining}",
                        "danger",
                    )
                    log_login_attempt(
                        user.username, False, ip_address, reason="Invalid credentials"
                    )
            else:
                # User not found - still log to prevent user enumeration
                flash("Username atau password salah.", "danger")
                log_login_attempt(username, False, ip_address, reason="User not found")

    return render_template("auth/login.html")


# ============ LOGOUT ============
@auth_bp.route("/logout")
@login_required
def logout():
    """User logout with session cleanup (SR-10)"""

    username = current_user.username
    ip_address = request.remote_addr

    # Log logout before clearing session
    log_logout(username, ip_address)

    # SR-10: Clear all session data
    logout_user()
    session.clear()

    # Buat response dengan no-cache headers
    response = make_response(redirect(url_for("auth.login")))

    # Hapus cookie
    response.set_cookie("session", "", expires=0)
    response.set_cookie("remember_token", "", expires=0)

    # Tambahkan header untuk mencegah caching halaman setelah logout
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    flash("Anda telah logout.", "info")
    return response


# ============ SESSION CHECK ROUTE ============
@auth_bp.route("/session-status")
@login_required
def session_status():
    """Check current session status (for debugging)"""
    from flask import jsonify

    return jsonify(
        {
            "user_id": session.get("user_id"),
            "username": session.get("username"),
            "session_permanent": session.permanent,
            "session_fresh": session.get("_fresh"),
            "session_lifetime": current_app.config.get("SESSION_TIMEOUT_MINUTES", 15),
            "is_authenticated": current_user.is_authenticated,
            "is_admin": (
                current_user.is_admin() if current_user.is_authenticated else False
            ),
        }
    )


# ============ EXTEND SESSION ============
@auth_bp.route("/extend-session")
@login_required
def extend_session():
    """Extend user session (refresh timeout)"""
    session.permanent = True
    session["_fresh"] = True
    flash("Sesi Anda telah diperpanjang.", "success")
    return redirect(request.referrer or url_for("notes.dashboard"))


# ============ TEMPLATE ROUTES ============
@auth_bp.route("/login-page")
def login_page():
    """Simple login page redirect"""
    return redirect(url_for("auth.login"))


@auth_bp.route("/register-page")
def register_page():
    """Simple register page redirect"""
    return redirect(url_for("auth.register"))
