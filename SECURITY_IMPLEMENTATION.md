# 🔐 Laporan Implementasi Keamanan
# Secure Notes App

| Informasi | Detail |
|---|---|
| **Nama Proyek** | Secure Notes App |
| **Tanggal** | 22 Mei 2026 |
| **Penulis** | Rusmawatie & Ariel |
| **Mata Kuliah** | Secure Software Engineering (SSE) |
| **Framework** | Flask (Python) |
| **Database** | SQLite |
| **Metodologi** | Secure Software Engineering (SSE) |

---

# 📖 Deskripsi Sistem

Secure Notes App adalah aplikasi berbasis web yang digunakan untuk menyimpan dan mengelola catatan pribadi pengguna secara aman. Sistem memungkinkan pengguna melakukan registrasi, login, membuat, mengedit, melihat, dan menghapus catatan pribadi melalui dashboard web.

Aplikasi dirancang menggunakan pendekatan Secure Software Engineering (SSE) dengan fokus pada:
- authentication security
- authorization
- session management
- input validation
- logging
- secure configuration

Sistem juga menerapkan berbagai kontrol keamanan untuk melindungi aplikasi dari ancaman umum seperti:
- SQL Injection
- Cross-Site Scripting (XSS)
- Brute Force Attack
- IDOR
- Unauthorized Access

---

# 📋 Daftar Kontrol Keamanan yang Diimplementasikan

| No | Kontrol Keamanan | Status | Lokasi Kode |
|---|---|---|---|
| 1 | Password Hashing (bcrypt) | ✅ | `app/models/user.py` |
| 2 | Rate Limiting Login (5x) | ✅ | `app/models/user.py` |
| 3 | Account Lock (15 menit) | ✅ | `app/models/user.py` |
| 4 | Session Timeout (15 menit) | ✅ | `app/config.py` |
| 5 | RBAC (Admin/User) | ✅ | `app/utils/auth_middleware.py` |
| 6 | Ownership Validation (IDOR Prevention) | ✅ | `app/utils/auth_middleware.py` |
| 7 | File Upload Validation | ✅ | `app/utils/file_upload.py` |
| 8 | Input Validation (XSS Prevention) | ✅ | `app/utils/security.py` |
| 9 | SQL Injection Prevention | ✅ | `SQLAlchemy ORM` |
| 10 | Security Logging | ✅ | `app/utils/logger.py` |
| 11 | Security Headers | ✅ | `app/utils/cache_control.py` |
| 12 | No-Cache Headers | ✅ | `app/templates/base.html` |

---

# 1️⃣ Password Hashing (bcrypt)

## 📌 Tujuan
Melindungi password pengguna agar tidak disimpan dalam bentuk plaintext di database.

---

## 📍 Lokasi Implementasi

```text
app/models/user.py
```

---

## 💻 Kode Implementasi

```python
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(self, password):
    """Hash password menggunakan pbkdf2:sha256"""
    self.password_hash = generate_password_hash(
        password,
        method='pbkdf2:sha256'
    )

def check_password(self, password):
    return check_password_hash(self.password_hash, password)
```

---

## 🖼️ Screenshot Implementasi

![Password Hashing](screenshots/01_password_hashing.png)

---

## 📝 Penjelasan

Password pengguna di-hash menggunakan algoritma:
```text
pbkdf2:sha256
```

sebelum disimpan ke database.

Teknik hashing ini membantu melindungi password dari:
- pencurian database
- brute force attack
- rainbow table attack

Sistem tidak pernah menyimpan password asli pengguna dalam bentuk plaintext.

---

# 2️⃣ Rate Limiting Login

## 📌 Tujuan
Mencegah brute force attack pada fitur login.

---

## 📍 Lokasi Implementasi

```text
app/models/user.py
```

---

## 💻 Kode Implementasi

```python
MAX_LOGIN_ATTEMPTS = 5

if not user.check_password(password):
    user.login_attempts += 1

    if user.login_attempts >= MAX_LOGIN_ATTEMPTS:
        user.locked_until = datetime.utcnow() + timedelta(minutes=15)

    db.session.commit()
```

---

## 🖼️ Screenshot Implementasi

![Rate Limiting](screenshots/02_rate_limiting.png)

---

## 📝 Penjelasan

Setiap percobaan login gagal akan menambah counter:
```python
login_attempts
```

Jika pengguna gagal login sebanyak:
```text
5 kali
```

maka akun akan dikunci sementara selama:
```text
15 menit
```

melalui field:
```python
locked_until
```

Kontrol keamanan ini membantu mencegah:
- brute force attack
- credential stuffing
- automated login attack

---

# 3️⃣ Account Lock Mechanism

## 📌 Tujuan
Mengurangi risiko percobaan login berulang dari attacker.

---

## 📍 Lokasi Implementasi

```text
app/models/user.py
```

---

## 💻 Kode Implementasi

```python
    def lock_account(self):
        from datetime import timedelta

        lock_duration = timedelta(minutes=15)
        self.locked_until = datetime.utcnow() + lock_duration
        db.session.commit()
```

---

## 🖼️ Screenshot Implementasi

![Account Lock](screenshots/03_lock_account.png)

---

## 📝 Penjelasan

Sistem memeriksa apakah akun sedang dalam status terkunci melalui field:
Jika waktu lock masih aktif, pengguna tidak dapat login hingga batas waktu berakhir.

---

# 4️⃣ Session Timeout

## 📌 Tujuan
Mencegah session hijacking dan akses tidak sah akibat session yang terlalu lama aktif.

---

## 📍 Lokasi Implementasi

```text
app/config.py
```

---

## 💻 Kode Implementasi

```python
    # Session Security (SR-03: Session timeout 15 menit)
    SESSION_TIMEOUT_MINUTES = int(os.environ.get("SESSION_TIMEOUT_MINUTES", 15))
    PERMANENT_SESSION_LIFETIME = SESSION_TIMEOUT_MINUTES * 60  # Convert to seconds
```

---

## 🖼️ Screenshot Implementasi

![Session Timeout](screenshots/04_session_timeout.png)

---

## 📝 Penjelasan

Session pengguna otomatis berakhir setelah:
```text
15 menit
```

tidak aktif.

Selain itu:
- `SESSION_COOKIE_HTTPONLY` mencegah akses cookie melalui JavaScript
- `SESSION_COOKIE_SECURE` memastikan cookie hanya dikirim melalui HTTPS

---

# 5️⃣ RBAC (Role-Based Access Control)

## 📌 Tujuan
Membatasi akses berdasarkan role pengguna.

---

## 📍 Lokasi Implementasi

```text
app/utils/auth_middleware.py
```

---

## 💻 Kode Implementasi

```python
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
```

---

## 🖼️ Screenshot Implementasi

![RBAC Middleware](screenshots/05_rbac_middleware.png)

---

## 📝 Penjelasan

Decorator:
```python
@admin_required
```

digunakan untuk memastikan hanya user dengan role:
```text
admin
```

yang dapat mengakses endpoint administrator.

Kontrol keamanan ini membantu mencegah:
- privilege escalation
- unauthorized admin access

---

# 6️⃣ Ownership Validation (IDOR Prevention)

## 📌 Tujuan
Mencegah pengguna mengakses resource milik pengguna lain.

---

## 📍 Lokasi Implementasi

```text
app/utils/auth_middleware.py
```

---

## 💻 Kode Implementasi

```python
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
```

---

## 🖼️ Screenshot Implementasi

![Ownership Validation](screenshots/06_ownership_validation.png)

---

## 📝 Penjelasan

Sistem memverifikasi bahwa:
```text
resource hanya dapat diakses oleh pemiliknya
```

Kontrol ini digunakan untuk mencegah:
```text
IDOR (Insecure Direct Object Reference)
```

---

# 7️⃣ File Upload Validation

## 📌 Tujuan
Mencegah upload file berbahaya ke server.

---

## 📍 Lokasi Implementasi

```text
app/utils/file_upload.py
```

---

## 💻 Kode Implementasi

```python
def allowed_file(filename):
    """Check if file extension is allowed"""
    if not filename:
        return False

    # Get extension
    ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""

    # Check if extension is in allowed list
    return ext in current_app.config["ALLOWED_EXTENSIONS"]
```

---

## 🖼️ Screenshot Implementasi

![File Upload Validation](screenshots/07_file_upload_validation.png)

---

## 📝 Penjelasan

Sistem hanya mengizinkan upload file dengan ekstensi tertentu.

Kontrol ini membantu mencegah:
- malicious file upload
- remote code execution
- upload webshell

---

# 8️⃣ Input Validation & XSS Prevention

## 📌 Tujuan
Mencegah serangan Cross-Site Scripting (XSS).

---

## 📍 Lokasi Implementasi

```text
app/utils/security.py
```

---

## 💻 Kode Implementasi

```python
import bleach

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
```

---

## 🖼️ Screenshot Implementasi

![XSS Prevention](screenshots/08_xss_prevention.png)

---

## 📝 Penjelasan

Semua input pengguna dibersihkan menggunakan:
```python
bleach.clean()
```

untuk menghapus script berbahaya sebelum ditampilkan kembali ke browser.

Sistem juga memanfaatkan escaping bawaan Jinja2 untuk mengurangi risiko:
- reflected XSS
- stored XSS

---

# 9️⃣ SQL Injection Prevention

## 📌 Tujuan
Mencegah manipulasi query database oleh attacker.

---

## 📍 Lokasi Implementasi

```text
SQLAlchemy ORM
```

---

## 💻 Kode Implementasi

```python
user = User.query.filter_by(email=email).first()
```

---

## 🖼️ Screenshot Implementasi

![SQL Injection Prevention](screenshots/09_sql_injection_prevention.png)

---

## 📝 Penjelasan

Aplikasi menggunakan SQLAlchemy ORM sehingga query database dilakukan menggunakan parameterized query.

Pendekatan ini membantu mencegah:
- SQL Injection
- manipulasi query manual
- unauthorized database access

---

# 🔟 Security Logging

## 📌 Tujuan
Menyediakan audit trail aktivitas keamanan sistem.

---

## 📍 Lokasi Implementasi

```text
app/utils/logger.py
```

---

## 💻 Kode Implementasi

```python
def log_note_action(
    action, username, note_id, note_title=None, ip_address=None, status="success"
):
    """
    Log note-related actions (create, edit, delete)

    Actions: NOTE_CREATED, NOTE_EDITED, NOTE_DELETED, NOTE_VIEWED
    """
    details = f"Note ID: {note_id}"
    if note_title:
        details += f" | Title: {note_title[:50]}"  # Truncate long titles

    log_security_event(
        f"NOTE_{action.upper()}",
        username=username,
        ip_address=ip_address,
        status=status,
        details=details,
    )
```

---

## 🖼️ Screenshot Implementasi

![Security Logging](screenshots/10_security_logging.png)

---

## 📝 Aktivitas yang Dicatat

- Login berhasil
- Login gagal
- Logout pengguna
- Akses endpoint admin
- Penghapusan catatan
- Percobaan akses tidak sah

---

# 1️⃣1️⃣ Security Headers

## 📌 Tujuan
Meningkatkan keamanan browser dan mengurangi risiko browser-based attack.

---

## 📍 Lokasi Implementasi

```text
app/utils/cache_control.py
```

---

## 💻 Kode Implementasi

```python
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
```

---

## 🖼️ Screenshot Implementasi

![Security Headers](screenshots/11_security_headers.png)

---

## 📝 Penjelasan

Header keamanan ditambahkan untuk membantu mencegah:
- clickjacking
- MIME sniffing
- browser exploitation

---

# 1️⃣2️⃣ No-Cache Headers

## 📌 Tujuan
Mencegah browser menyimpan data sensitif di cache.

---

## 📍 Lokasi Implementasi

```text
app/templates/base.html
```

---

## 💻 Kode Implementasi

```html
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
```

---

## 🖼️ Screenshot Implementasi

![No Cache Headers](screenshots/12_no_cache_headers.png)

---

## 📝 Penjelasan

Header no-cache membantu mencegah:
- penyimpanan session sensitif
- caching halaman login
- akses data melalui browser history

---

# 📊 Ringkasan Kontrol Keamanan

| Kategori | Implementasi |
|---|---|
| Authentication Security | Password hashing, rate limiting, account lock |
| Authorization | RBAC, ownership validation |
| Session Security | Session timeout, logout invalidation |
| Input Security | XSS prevention, validation |
| Database Security | SQL Injection prevention |
| Browser Security | Security headers, no-cache |
| Monitoring | Security logging |
| File Security | File upload validation |

---

# ✅ Kesimpulan

Secure Notes App telah mengimplementasikan berbagai kontrol keamanan dasar sesuai prinsip Secure Software Engineering (SSE).

Kontrol keamanan yang diterapkan mencakup:
- authentication security
- authorization
- session management
- input validation
- logging
- access control
- brute force protection
- secure configuration

Implementasi ini membantu meningkatkan keamanan aplikasi terhadap ancaman umum pada aplikasi web modern seperti:
- SQL Injection
- Cross-Site Scripting (XSS)
- Brute Force Attack
- IDOR
- Unauthorized Access

Dengan penerapan kontrol keamanan tersebut, aplikasi menjadi lebih aman, terstruktur, dan sesuai dengan prinsip secure software development lifecycle.

---
