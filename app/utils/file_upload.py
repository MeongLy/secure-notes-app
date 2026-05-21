# app/utils/file_upload.py
import os
import hashlib
from werkzeug.utils import secure_filename
from flask import current_app
from datetime import datetime

# Coba import magic, jika gagal fallback ke mimetypes
try:
    import magic

    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    import mimetypes


def allowed_file(filename):
    """Check if file extension is allowed"""
    if not filename:
        return False

    # Get extension
    ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""

    # Check if extension is in allowed list
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def allowed_mimetype(file_stream):
    """Check if file MIME type is allowed"""
    try:
        # Baca file untuk deteksi
        file_content = file_stream.read(1024)
        file_stream.seek(0)  # Reset stream position

        # Jika file kosong
        if len(file_content) == 0:
            return False

        if MAGIC_AVAILABLE:
            # Gunakan python-magic jika tersedia
            mime = magic.Magic(mime=True)
            mime_type = mime.from_buffer(file_content)
        else:
            # Fallback ke mimetypes berdasarkan ekstensi
            # Ambil nama file dari request (perlu passing filename)
            return True  # Sementara izinkan, akan dicek extension

        return mime_type in current_app.config["ALLOWED_MIMETYPES"]

    except Exception as e:
        print(f"MIME detection error: {e}")
        # Jika gagal, fallback ke validasi ekstensi saja
        return True


def validate_file(file):
    """
    Validate uploaded file:
    - Check if file exists
    - Check file size
    - Check extension
    - Check MIME type (if available)
    """
    errors = []

    # Check if file is present
    if not file or file.filename == "":
        errors.append("Tidak ada file yang dipilih.")
        return False, errors

    # Check file size
    file.seek(0, 2)  # Go to end of file
    file_size = file.tell()
    file.seek(0)  # Reset to beginning

    max_size = current_app.config.get("MAX_CONTENT_LENGTH", 5 * 1024 * 1024)
    if file_size > max_size:
        errors.append(
            f"Ukuran file terlalu besar. Maksimal {max_size // (1024*1024)}MB."
        )
        return False, errors

    # Check if file is empty
    if file_size == 0:
        errors.append("File kosong. Silakan pilih file yang valid.")
        return False, errors

    # Check extension
    if not allowed_file(file.filename):
        allowed = ", ".join(current_app.config["ALLOWED_EXTENSIONS"])
        errors.append(
            f"Tipe file tidak diizinkan. Ekstensi yang diperbolehkan: {allowed}"
        )
        return False, errors

    # Check MIME type (optional, jika gagal tidak blocking)
    try:
        if not allowed_mimetype(file):
            # Jangan langsung error, karena magic mungkin tidak berfungsi
            print(f"Warning: MIME type check failed for {file.filename}")
            # errors.append('Tipe file tidak valid atau file mungkin corrupted.')
            # return False, errors
    except Exception as e:
        print(f"MIME check error: {e}")
        # Continue anyway

    return True, errors


def generate_secure_filename(original_filename):
    """Generate secure unique filename"""
    # Sanitize original filename
    safe_filename = secure_filename(original_filename)
    if not safe_filename:
        # Jika secure_filename menghasilkan string kosong, buat dari hash
        safe_filename = "file"

    # Generate unique name with timestamp and hash
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(safe_filename)
    if not ext:
        # Jika tidak ada ekstensi, ambil dari original
        ext = (
            original_filename.rsplit(".", 1)[1].lower()
            if "." in original_filename
            else ""
        )
        ext = f".{ext}" if ext else ""

    hash_part = hashlib.md5(f"{timestamp}{name}".encode()).hexdigest()[:8]

    return f"{timestamp}_{hash_part}{ext}"


def save_uploaded_file(file, note_id):
    """
    Save uploaded file and return attachment object
    """
    # Validate file first
    is_valid, errors = validate_file(file)
    if not is_valid:
        return None, errors

    # Create upload folder if not exists
    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Create note-specific subfolder
    note_folder = os.path.join(upload_folder, str(note_id))
    if not os.path.exists(note_folder):
        os.makedirs(note_folder)

    # Generate secure filename
    original_filename = file.filename
    secure_filename_generated = generate_secure_filename(original_filename)

    # Get file extension
    ext = (
        original_filename.rsplit(".", 1)[1].lower() if "." in original_filename else ""
    )

    # Get MIME type
    mime_type = "application/octet-stream"  # Default
    try:
        file.seek(0)
        file_content = file.read(1024)
        file.seek(0)

        if MAGIC_AVAILABLE:
            mime = magic.Magic(mime=True)
            mime_type = mime.from_buffer(file_content)
        else:
            # Fallback ke mimetypes
            mime_type = mimetypes.guess_type(original_filename)[0] or mime_type
    except Exception as e:
        print(f"MIME detection error: {e}")

    # Get file size
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)

    # Save file
    file_path = os.path.join(note_folder, secure_filename_generated)
    file.save(file_path)

    return {
        "filename": secure_filename_generated,
        "original_filename": original_filename,
        "file_path": file_path,
        "file_size": file_size,
        "mime_type": mime_type,
        "file_extension": ext,
    }, None
