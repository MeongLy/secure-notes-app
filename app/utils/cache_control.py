# app/utils/cache_control.py
from functools import wraps
from flask import make_response, session, redirect, url_for
from flask_login import current_user


def no_cache(view):
    """Decorator to add no-cache headers to responses"""

    @wraps(view)
    def decorated_function(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = (
            "no-cache, no-store, must-revalidate, private"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    return decorated_function


def login_required_with_no_cache(view):
    """Combined decorator: login required + no cache"""
    from flask_login import login_required

    return login_required(no_cache(view))
