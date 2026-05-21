# app/routes/main.py
from flask import Blueprint, redirect, url_for, make_response
from flask_login import current_user
from app.utils.cache_control import no_cache

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@no_cache
def index():
    """Halaman utama - redirect ke dashboard atau login"""
    if current_user.is_authenticated:
        response = make_response(redirect(url_for("notes.dashboard")))
        response.headers["Cache-Control"] = (
            "no-cache, no-store, must-revalidate, private"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    response = make_response(redirect(url_for("auth.login")))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
