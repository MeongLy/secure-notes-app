# app/routes/notes.py
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
    make_response,
    send_file,
)
from flask_login import login_required, current_user
from app import db
from app.models.note import Note, NoteAttachment
from app.utils.security import (
    validate_note_title,
    validate_note_content,
    sanitize_input,
)
from app.utils.auth_middleware import ownership_required
from app.utils.logger import log_note_action, log_unauthorized_access
from app.utils.cache_control import no_cache, login_required_with_no_cache
from app.utils.file_upload import save_uploaded_file, validate_file
import os

notes_bp = Blueprint("notes", __name__, url_prefix="/notes")


# ============ DASHBOARD ============
@notes_bp.route("/dashboard")
@login_required_with_no_cache
def dashboard():
    """Display user's notes dashboard"""
    # Get user's notes only (SR-07, SR-08 enforced at query level)
    user_notes = (
        Note.query.filter_by(user_id=current_user.id)
        .order_by(Note.updated_at.desc())
        .all()
    )

    return render_template("dashboard.html", notes=user_notes)


# ============ CREATE NOTE ============
@notes_bp.route("/create", methods=["GET", "POST"])
@login_required_with_no_cache
def create_note():
    """Create a new note with input validation"""

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        # SR-04: Validate input
        title_valid, title_error = validate_note_title(title)
        content_valid, content_error = validate_note_content(content)

        errors = []
        if not title_valid:
            errors.append(title_error)
        if not content_valid:
            errors.append(content_error)

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("notes/create.html", title=title, content=content)

        # Create new note
        note = Note(
            title=sanitize_input(title),  # Sanitize title
            content=content,  # Content stored as-is, sanitized on display
            user_id=current_user.id,
        )

        db.session.add(note)
        db.session.commit()

        # Log note creation
        log_note_action("created", current_user.username, note.id, note.title)

        flash("Catatan berhasil dibuat!", "success")

        response = make_response(redirect(url_for("notes.dashboard")))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response

    return render_template("notes/create.html")


# ============ VIEW NOTE ============
@notes_bp.route("/<int:note_id>")
@login_required_with_no_cache
@ownership_required(Note, "note_id")
def view_note(note_id, item=None):
    """View a single note (with ownership check)"""
    note = item or Note.query.get_or_404(note_id)

    # Log note view
    log_note_action("viewed", current_user.username, note.id, note.title)

    return render_template("notes/view.html", note=note)


# ============ EDIT NOTE ============
@notes_bp.route("/<int:note_id>/edit", methods=["GET", "POST"])
@login_required_with_no_cache
@ownership_required(Note, "note_id")
def edit_note(note_id, item=None):
    """Edit a note (SR-07: ownership validation)"""
    note = item or Note.query.get_or_404(note_id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        # SR-04: Validate input
        title_valid, title_error = validate_note_title(title)
        content_valid, content_error = validate_note_content(content)

        errors = []
        if not title_valid:
            errors.append(title_error)
        if not content_valid:
            errors.append(content_error)

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("notes/edit.html", note=note)

        # Update note
        note.title = sanitize_input(title)
        note.content = content

        db.session.commit()

        # Log note edit
        log_note_action("edited", current_user.username, note.id, note.title)

        flash("Catatan berhasil diperbarui!", "success")

        response = make_response(redirect(url_for("notes.view_note", note_id=note.id)))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response

    return render_template("notes/edit.html", note=note)


# ============ DELETE NOTE ============
@notes_bp.route("/<int:note_id>/delete", methods=["POST"])
@login_required_with_no_cache
@ownership_required(Note, "note_id")
def delete_note(note_id, item=None):
    """Delete a note (SR-08: ownership validation)"""
    note = item or Note.query.get_or_404(note_id)

    # Log before deletion
    log_note_action("deleted", current_user.username, note.id, note.title)

    # Delete note (attachments will be cascade deleted)
    db.session.delete(note)
    db.session.commit()

    flash("Catatan berhasil dihapus!", "success")

    response = make_response(redirect(url_for("notes.dashboard")))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


# ============ SEARCH NOTES ============
@notes_bp.route("/search")
@login_required_with_no_cache
def search_notes():
    """Search user's notes"""
    query = request.args.get("q", "").strip()

    if not query:
        return redirect(url_for("notes.dashboard"))

    # Search in user's notes only (SR-07)
    notes = (
        Note.query.filter(
            Note.user_id == current_user.id,
            (Note.title.contains(query) | Note.content.contains(query)),
        )
        .order_by(Note.updated_at.desc())
        .all()
    )

    return render_template("dashboard.html", notes=notes, search_query=query)


# ============ UPLOAD FILE ATTACHMENT ============
@notes_bp.route("/<int:note_id>/upload", methods=["POST"])
@login_required_with_no_cache
@ownership_required(Note, "note_id")
def upload_attachment(note_id, item=None):
    """Upload file attachment for a note"""
    note = item or Note.query.get_or_404(note_id)

    # Check if file is present
    if "file" not in request.files:
        flash("Tidak ada file yang dipilih.", "danger")
        return redirect(url_for("notes.edit_note", note_id=note.id))

    file = request.files["file"]

    # Check if filename is not empty
    if file.filename == "":
        flash("Tidak ada file yang dipilih.", "danger")
        return redirect(url_for("notes.edit_note", note_id=note.id))

    # Save file using helper function
    attachment_data, error = save_uploaded_file(file, note.id)

    if error:
        for err in error:
            flash(err, "danger")
        return redirect(url_for("notes.edit_note", note_id=note.id))

    # Create attachment record in database
    attachment = NoteAttachment(
        filename=attachment_data["filename"],
        original_filename=attachment_data["original_filename"],
        file_path=attachment_data["file_path"],
        file_size=attachment_data["file_size"],
        mime_type=attachment_data["mime_type"],
        file_extension=attachment_data["file_extension"],
        note_id=note.id,
    )

    db.session.add(attachment)
    db.session.commit()

    # Log attachment upload
    log_note_action(
        "attachment_uploaded",
        current_user.username,
        note.id,
        f"File: {attachment.original_filename} ({attachment.file_size} bytes)",
    )

    flash(f'File "{attachment.original_filename}" berhasil diupload!', "success")
    return redirect(url_for("notes.edit_note", note_id=note.id))


# ============ DELETE FILE ATTACHMENT ============
@notes_bp.route("/attachment/<int:attachment_id>/delete", methods=["POST"])
@login_required_with_no_cache
def delete_attachment(attachment_id):
    """Delete file attachment (with ownership check)"""
    attachment = NoteAttachment.query.get_or_404(attachment_id)
    note = Note.query.get_or_404(attachment.note_id)

    # Check ownership (user must own the note or be admin)
    if note.user_id != current_user.id and not current_user.is_admin():
        log_unauthorized_access(
            username=current_user.username,
            resource=f"Attachment:{attachment_id}",
            ip_address=request.remote_addr,
            details=f"User attempted to delete attachment of note {note.id}",
        )
        flash("Anda tidak memiliki izin untuk menghapus file ini.", "danger")
        return redirect(url_for("notes.dashboard"))

    # Delete file from filesystem
    if os.path.exists(attachment.file_path):
        try:
            os.remove(attachment.file_path)
        except OSError as e:
            flash(f"Gagal menghapus file: {e}", "danger")
            return redirect(url_for("notes.edit_note", note_id=note.id))

    # Log deletion
    log_note_action(
        "attachment_deleted",
        current_user.username,
        note.id,
        f"File: {attachment.original_filename}",
    )

    # Delete database record
    db.session.delete(attachment)
    db.session.commit()

    flash(f'File "{attachment.original_filename}" berhasil dihapus!', "success")
    return redirect(url_for("notes.edit_note", note_id=note.id))


# ============ DOWNLOAD FILE ATTACHMENT ============
@notes_bp.route("/attachment/<int:attachment_id>/download")
@login_required_with_no_cache
def download_attachment(attachment_id):
    """Download file attachment"""
    attachment = NoteAttachment.query.get_or_404(attachment_id)
    note = Note.query.get_or_404(attachment.note_id)

    # Check ownership
    if note.user_id != current_user.id and not current_user.is_admin():
        log_unauthorized_access(
            username=current_user.username,
            resource=f"Attachment:{attachment_id}",
            ip_address=request.remote_addr,
            details=f"User attempted to download attachment of note {note.id}",
        )
        flash("Anda tidak memiliki izin untuk mendownload file ini.", "danger")
        return redirect(url_for("notes.dashboard"))

    # Check if file exists on filesystem
    if not os.path.exists(attachment.file_path):
        flash("File tidak ditemukan di server.", "danger")
        return redirect(url_for("notes.edit_note", note_id=note.id))

    # Log download
    log_note_action(
        "attachment_downloaded",
        current_user.username,
        note.id,
        f"File: {attachment.original_filename}",
    )

    # Send file to client
    return send_file(
        attachment.file_path,
        as_attachment=True,
        download_name=attachment.original_filename,
        mimetype=attachment.mime_type,
    )
