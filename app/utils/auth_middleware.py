# app/utils/auth_middleware.py
from functools import wraps
from flask import request, flash, redirect, url_for, current_app
from flask_login import current_user
from app.utils.logger import log_unauthorized_access


def role_required(role):
    """
    Decorator for role-based access control (SR-05: RBAC)
    Usage: @role_required('admin')
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                log_unauthorized_access(
                    username=None,
                    resource=request.endpoint,
                    ip_address=request.remote_addr,
                    details="Not authenticated",
                )
                flash("Silakan login terlebih dahulu.", "warning")
                return redirect(url_for("auth.login"))

            if role == "admin" and not current_user.is_admin():
                log_unauthorized_access(
                    username=current_user.username,
                    resource=request.endpoint,
                    ip_address=request.remote_addr,
                    details=f"Required role: {role}, User role: {current_user.role}",
                )
                flash(
                    "Akses ditolak. Anda tidak memiliki izin untuk mengakses halaman ini.",
                    "danger",
                )
                return redirect(url_for("notes.dashboard"))

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f):
    """
    Decorator for admin-only access (shorthand for role_required('admin'))
    """
    return role_required("admin")(f)


def login_rate_limit(f):
    """
    Decorator for rate limiting on login attempts (SR-02: max 5 attempts)
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.utils.security import login_rate_limiter

        # Use IP address + username as key for rate limiting
        username = request.form.get("username", "unknown")
        key = f"{request.remote_addr}:{username}"

        if not login_rate_limiter.is_allowed(key, max_attempts=5, window_seconds=300):
            flash(
                "Terlalu banyak percobaan login. Silakan coba lagi setelah 5 menit.",
                "danger",
            )
            return redirect(url_for("auth.login"))

        response = f(*args, **kwargs)

        # Only track failed attempts in the route
        # This decorator just checks, actual tracking happens in the route

        return response

    return decorated_function


def ownership_required(model, id_param="note_id", user_attr="user_id"):
    """
    Decorator to verify ownership before edit/delete (SR-07, SR-08)

    Usage:
    @ownership_required(Note, 'note_id')
    def edit_note(note_id):
        note = get_note(note_id)  # Will be passed automatically
        ...
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get the ID from kwargs
            item_id = kwargs.get(id_param)

            if not item_id:
                flash("Item tidak ditemukan.", "danger")
                return redirect(url_for("notes.dashboard"))

            # Query the item
            item = model.query.get(item_id)

            if not item:
                flash("Item tidak ditemukan.", "danger")
                return redirect(url_for("notes.dashboard"))

            # Check ownership
            if not current_user.is_authenticated:
                flash("Silakan login terlebih dahulu.", "warning")
                return redirect(url_for("auth.login"))

            # Admin can access everything
            if current_user.is_admin():
                return f(*args, **kwargs, item=item)

            # Check if user owns the item
            if getattr(item, user_attr) != current_user.id:
                log_unauthorized_access(
                    username=current_user.username,
                    resource=f"{model.__name__}:{item_id}",
                    ip_address=request.remote_addr,
                    details=f"User attempted to access {model.__name__} owned by user {getattr(item, user_attr)}",
                )
                flash("Anda tidak memiliki izin untuk mengakses catatan ini.", "danger")
                return redirect(url_for("notes.dashboard"))

            return f(*args, **kwargs, item=item)

        return decorated_function

    return decorator


def session_timeout_check(f):
    """
    Decorator to check session timeout (SR-03)
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session

        if current_user.is_authenticated:
            if not session.get("_fresh", True):
                flash("Sesi Anda telah berakhir. Silakan login kembali.", "warning")
                return redirect(url_for("auth.logout"))

        return f(*args, **kwargs)

    return decorated_function
