# Security Configuration Checklist - Secure Notes App

| **Nama Proyek** | Secure Notes App |
| **Tanggal Verifikasi** | 26 Mei 2026 |
| **Verifikator** | Rusmawatie & Ariel |
| **Status** | ✅ All Pass |

---

## 📋 Checklist Verifikasi

### 1. Authentication & Password Security

| No | Item | Status | Keterangan |
|----|------|--------|-------------|
| 1.1 | Password di-hash dengan bcrypt/pbkdf2 | ✅ Pass | `models/user.py:28` |
| 1.2 | Rate limiting pada endpoint login (5 attempts) | ✅ Pass | `MAX_LOGIN_ATTEMPTS = 5` |
| 1.3 | Account lock setelah 5x percobaan gagal | ✅ Pass | Lock 15 menit |
| 1.4 | Session timeout (15 menit) | ✅ Pass | `SESSION_TIMEOUT_MINUTES = 15` |

### 2. Authorization & Access Control

| No | Item | Status | Keterangan |
|----|------|--------|-------------|
| 2.1 | RBAC untuk admin dan user | ✅ Pass | `@admin_required` decorator |
| 2.2 | Ownership validation (IDOR prevention) | ✅ Pass | `@ownership_required` decorator |
| 2.3 | Endpoint terlindungi `@login_required` | ✅ Pass | Semua endpoint |

### 3. Input Validation & Sanitization

| No | Item | Status | Keterangan |
|----|------|--------|-------------|
| 3.1 | Validasi username (3-20 karakter, alfanumerik) | ✅ Pass | `validate_username()` |
| 3.2 | Validasi email format | ✅ Pass | `validate_email()` |
| 3.3 | Validasi password strength | ✅ Pass | `validate_password()` |
| 3.4 | Sanitasi input (XSS prevention) | ✅ Pass | `sanitize_input()` |
| 3.5 | Parameterized query (SQL injection) | ✅ Pass | SQLAlchemy ORM |

### 4. Session Security

| No | Item | Status | Keterangan |
|----|------|--------|-------------|
| 4.1 | Cookie HTTPOnly flag | ✅ Pass | `SESSION_COOKIE_HTTPONLY = True` |
| 4.2 | Cookie SameSite flag | ✅ Pass | `SESSION_COOKIE_SAMESITE = 'Lax'` |
| 4.3 | Session invalidate setelah logout | ✅ Pass | `session.clear()` |

### 5. Security Headers

| No | Item | Status | Keterangan |
|----|------|--------|-------------|
| 5.1 | X-Content-Type-Options: nosniff | ✅ Pass | `add_security_headers()` |
| 5.2 | X-Frame-Options: DENY | ✅ Pass | `add_security_headers()` |
| 5.3 | X-XSS-Protection: 1; mode=block | ✅ Pass | `add_security_headers()` |
| 5.4 | Referrer-Policy: strict-origin | ✅ Pass | `add_security_headers()` |

### 6. CSRF Protection

| No | Item | Status | Keterangan |
|----|------|--------|-------------|
| 6.1 | CSRF token di semua form POST | ✅ Pass | `{{ csrf_token() }}` |
| 6.2 | CSRF error handler | ✅ Pass | `@app.errorhandler(CSRFError)` |

### 7. File Upload Security

| No | Item | Status | Keterangan |
|----|------|--------|-------------|
| 7.1 | Validasi ekstensi file | ✅ Pass | `ALLOWED_EXTENSIONS` |
| 7.2 | Validasi MIME type | ✅ Pass | `python-magic` |
| 7.3 | Limit file size (5MB) | ✅ Pass | `MAX_CONTENT_LENGTH` |
| 7.4 | Sanitasi nama file | ✅ Pass | `secure_filename()` |

### 8. Security Logging

| No | Item | Status | Keterangan |
|----|------|--------|-------------|
| 8.1 | Log login attempts | ✅ Pass | `log_login_attempt()` |
| 8.2 | Log note operations | ✅ Pass | `log_note_action()` |
| 8.3 | Log unauthorized access | ✅ Pass | `log_unauthorized_access()` |
| 8.4 | Log admin actions | ✅ Pass | `log_admin_action()` |

### 9. Dependency Security

| No | Item | Status | Keterangan |
|----|------|--------|-------------|
| 9.1 | Tidak ada vulnerabilities HIGH | ✅ Pass | pip-audit: 0 HIGH |
| 9.2 | Versi packages up-to-date | ✅ Pass | Flask 3.1.3, Jinja2 3.1.6 |

### 10. Configuration Security

| No | Item | Status | Keterangan |
|----|------|--------|-------------|
| 10.1 | Debug mode OFF | ✅ Pass | `FLASK_ENV=production` |
| 10.2 | Secret key di .env | ✅ Pass | Tidak hardcoded |
| 10.3 | .env tidak di Git | ✅ Pass | `.gitignore` include `.env` |

---

## ✅ Ringkasan Verifikasi

| Kategori | Total | Pass | Fail |
|----------|-------|------|------|
| Authentication | 4 | 4 | 0 |
| Authorization | 3 | 3 | 0 |
| Input Validation | 5 | 5 | 0 |
| Session Security | 3 | 3 | 0 |
| Security Headers | 4 | 4 | 0 |
| CSRF Protection | 2 | 2 | 0 |
| File Upload | 4 | 4 | 0 |
| Security Logging | 4 | 4 | 0 |
| Dependency | 2 | 2 | 0 |
| Configuration | 3 | 3 | 0 |
| **Total** | **34** | **34** | **0** |


---

## 📝 Kesimpulan

Semua item security configuration checklist telah **diverifikasi dan dinyatakan PASS**. Aplikasi Secure Notes App siap untuk deployment.

**Status:** ✅ **READY FOR PRODUCTION**

---

**Dokumen ini dibuat untuk memenuhi tugas mata kuliah Secure Software Engineering (SSE)**

**Universitas Palangka Raya - Teknik Informatika**
