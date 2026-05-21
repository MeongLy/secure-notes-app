# app/models/note.py
from app import db
from datetime import datetime


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Foreign key to User (ownership)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Relationship with attachments (cascade delete)
    attachments = db.relationship(
        "NoteAttachment", backref="note", lazy=True, cascade="all, delete-orphan"
    )

    def belongs_to(self, user_id):
        """SR-07 & SR-08: Check ownership before edit/delete"""
        return self.user_id == user_id

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "attachments_count": len(self.attachments) if self.attachments else 0,
        }

    def __repr__(self):
        return f"<Note {self.title}>"


class NoteAttachment(db.Model):
    """Model untuk file attachment pada catatan"""

    __tablename__ = "note_attachments"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)  # Nama file tersimpan
    original_filename = db.Column(db.String(255), nullable=False)  # Nama asli file
    file_path = db.Column(db.String(500), nullable=False)  # Path lengkap file
    file_size = db.Column(db.Integer, nullable=False)  # Ukuran file dalam bytes
    mime_type = db.Column(db.String(100), nullable=False)  # MIME type file
    file_extension = db.Column(db.String(20), nullable=False)  # Ekstensi file
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key to Note
    note_id = db.Column(db.Integer, db.ForeignKey("notes.id"), nullable=False)

    def to_dict(self):
        """Convert attachment to dictionary"""
        return {
            "id": self.id,
            "filename": self.original_filename,
            "file_size": self.file_size,
            "file_size_kb": round(self.file_size / 1024, 2),
            "mime_type": self.mime_type,
            "file_extension": self.file_extension,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def get_file_size_mb(self):
        """Get file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)

    def __repr__(self):
        return f"<Attachment {self.original_filename}>"
