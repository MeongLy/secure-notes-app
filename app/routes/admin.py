# app/routes/admin.py
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    make_response,
)
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.note import Note
from app.utils.auth_middleware import admin_required
from app.utils.logger import get_security_logs, log_admin_action, clear_security_logs
from app.utils.cache_control import no_cache, login_required_with_no_cache
from datetime import datetime

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ============ ADMIN DASHBOARD ============
@admin_bp.route("/dashboard")
@login_required_with_no_cache
@admin_required
def dashboard():
    """Admin dashboard with system statistics"""

    # Get statistics
    total_users = User.query.count()
    total_notes = Note.query.count()
    admin_count = User.query.filter_by(role="admin").count()
    user_count = total_users - admin_count

    # Get recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()

    # Get recent notes
    recent_notes = Note.query.order_by(Note.created_at.desc()).limit(10).all()

    # Log admin access
    log_admin_action(
        admin_username=current_user.username,
        action="VIEW_ADMIN_DASHBOARD",
        details="Admin accessed dashboard",
    )

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_notes=total_notes,
        admin_count=admin_count,
        user_count=user_count,
        recent_users=recent_users,
        recent_notes=recent_notes,
    )


# ============ USER MANAGEMENT ============
@admin_bp.route("/users")
@login_required_with_no_cache
@admin_required
def list_users():
    """List all users (admin only)"""

    users = User.query.order_by(User.created_at.desc()).all()

    # Hitung statistik untuk template
    total_notes = Note.query.count()
    admin_count = User.query.filter_by(role="admin").count()
    user_count = User.query.filter_by(role="user").count()

    log_admin_action(
        admin_username=current_user.username,
        action="VIEW_USERS_LIST",
        details="Admin viewed user list",
    )

    return render_template(
        "admin/users.html",
        users=users,
        total_notes=total_notes,
        admin_count=admin_count,
        user_count=user_count,
    )


@admin_bp.route("/user/<int:user_id>")
@login_required_with_no_cache
@admin_required
def view_user(user_id):
    """View user details and their notes"""

    user = User.query.get_or_404(user_id)
    user_notes = (
        Note.query.filter_by(user_id=user.id).order_by(Note.updated_at.desc()).all()
    )

    log_admin_action(
        admin_username=current_user.username,
        action="VIEW_USER_DETAILS",
        target_user=user.username,
        details=f"User ID: {user_id}",
    )

    return render_template("admin/user_detail.html", user=user, notes=user_notes)


@admin_bp.route("/user/<int:user_id>/delete", methods=["POST"])
@login_required_with_no_cache
@admin_required
def delete_user(user_id):
    """Delete a user and all their notes"""

    user = User.query.get_or_404(user_id)

    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        flash("Anda tidak dapat menghapus akun Anda sendiri.", "danger")
        response = make_response(redirect(url_for("admin.list_users")))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response

    username = user.username
    note_count = Note.query.filter_by(user_id=user.id).count()

    # Log before deletion
    log_admin_action(
        admin_username=current_user.username,
        action="DELETE_USER",
        target_user=username,
        details=f"User had {note_count} notes",
    )

    # Delete user (notes will be cascade deleted)
    db.session.delete(user)
    db.session.commit()

    flash(
        f'User "{username}" berhasil dihapus beserta {note_count} catatannya.',
        "success",
    )

    response = make_response(redirect(url_for("admin.list_users")))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


# ============ SECURITY LOGS ============
@admin_bp.route("/logs")
@login_required_with_no_cache
@admin_required
def view_logs():
    """View security logs (SR-06: audit trail)"""

    # Get log count from query parameter
    limit = request.args.get("limit", 100, type=int)
    limit = min(limit, 500)  # Max 500 logs

    logs = get_security_logs(limit)

    log_admin_action(
        admin_username=current_user.username,
        action="VIEW_SECURITY_LOGS",
        details=f"Viewed last {limit} logs",
    )

    return render_template("admin/logs.html", logs=logs, limit=limit)


@admin_bp.route("/logs/clear", methods=["POST"])
@login_required_with_no_cache
@admin_required
def clear_logs():
    """Clear all security logs (admin only)"""

    if clear_security_logs():
        log_admin_action(
            admin_username=current_user.username,
            action="CLEAR_SECURITY_LOGS",
            details="Security logs cleared",
        )
        flash("Log keamanan berhasil dibersihkan.", "success")
    else:
        flash("Gagal membersihkan log keamanan.", "danger")

    response = make_response(redirect(url_for("admin.view_logs")))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


# ============ SYSTEM STATISTICS API ============
@admin_bp.route("/api/stats")
@login_required_with_no_cache
@admin_required
def api_stats():
    """JSON API for system statistics"""

    stats = {
        "total_users": User.query.count(),
        "total_notes": Note.query.count(),
        "admin_count": User.query.filter_by(role="admin").count(),
        "user_count": User.query.filter_by(role="user").count(),
        "notes_per_user": round(Note.query.count() / max(User.query.count(), 1), 2),
        "timestamp": datetime.now().isoformat(),
    }

    return jsonify(stats)
