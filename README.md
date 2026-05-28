# 🔐 Secure Notes App

HARAP GUNAKAN YANG SUDAH DI DEVELOP DI BRANCH

Aplikasi web untuk menyimpan, mengelola, dan melindungi catatan pribadi pengguna secara aman. Dibangun dengan pendekatan **Secure Software Engineering (SSE)** yang menekankan aspek keamanan sejak tahap perancangan.

---

# 👥 Tema & Anggota Kelompok

| Keterangan | Detail |
|---|---|
| **Tema Project** | Secure Notes App - Aplikasi Catatan Aman |
| **Mata Kuliah** | Secure Software Engineering (SSE) |
| **Dosen** | Septian Geges,S.Kom., M.Kom  |

## Anggota Kelompok

| No | Nama | NIM |
|---|---|---|
| 1 | [Ariel Ebenia Ezeria ] | [213030503140] |
| 2 | [Rusma Watie WN ] | [213030503139] |

---

# 📖 Deskripsi Sistem

Secure Notes App adalah aplikasi berbasis web yang digunakan untuk menyimpan, mengelola, dan melindungi catatan pribadi pengguna secara aman. Sistem memungkinkan pengguna melakukan registrasi, login, serta membuat, mengedit, melihat, dan menghapus catatan pribadi melalui dashboard web.

Aplikasi ini dirancang dengan pendekatan **Secure Software Engineering (SSE)** yang menekankan aspek keamanan sejak tahap perancangan. Sistem menerapkan autentikasi pengguna, pembatasan hak akses, validasi input, hashing password, dan logging aktivitas untuk melindungi data pengguna dari akses tidak sah maupun serangan umum pada aplikasi web.

Selain pengguna biasa, sistem juga memiliki peran admin yang dapat memantau data pengguna dan aktivitas sistem untuk kebutuhan monitoring dan audit keamanan.

---

# 🎯 Fitur Utama

## 👤 Pengguna Biasa

| Fitur | Keamanan |
|---|---|
| Registrasi | Validasi input + bcrypt hashing |
| Login | Pembatasan percobaan login (5x) + session timeout |
| Dashboard | Menampilkan daftar catatan pribadi |
| Buat Catatan | Sanitasi input (XSS prevention) |
| Edit Catatan | Ownership validation |
| Hapus Catatan | Authorization validation |
| Logout | Session invalidation |

---

## 👑 Admin

| Fitur | Keamanan |
|---|---|
| Lihat daftar user | RBAC (Role-Based Access Control) |
| Monitor aktivitas sistem | Security logging |
| Lihat log keamanan | Pembatasan endpoint admin |

---

# 🔒 Fitur Keamanan Utama

- Password hashing menggunakan bcrypt
- Session timeout otomatis
- Rate limiting login
- Input validation & sanitasi
- Role-Based Access Control (RBAC)
- Protection terhadap SQL Injection
- Protection terhadap XSS dasar
- Security logging
- Ownership validation pada catatan
- Session invalidation saat logout

---

# 🛡️ Security Requirements

| ID | Requirement |
|---|---|
| SR-01 | Sistem HARUS menggunakan bcrypt untuk hashing password |
| SR-02 | Sistem HARUS membatasi percobaan login maksimal 5 kali |
| SR-03 | Session HARUS expired setelah 15 menit tidak aktif |
| SR-04 | Seluruh input pengguna HARUS divalidasi |
| SR-05 | Sistem HARUS menerapkan RBAC untuk role user dan admin |
| SR-06 | Sistem HARUS mencatat login gagal ke security log |
| SR-07 | Sistem HARUS memverifikasi ownership sebelum edit catatan |
| SR-08 | Sistem HARUS memverifikasi ownership sebelum hapus catatan |
| SR-09 | Sistem HARUS menggunakan HTTPS |
| SR-10 | Session HARUS dibersihkan saat logout |

---

# 🏗️ Arsitektur Sistem

## Stack Teknologi

| Layer | Teknologi | Justifikasi Keamanan |
|---|---|---|
| Frontend | HTML, CSS, Bootstrap | Sanitasi output via Jinja2 |
| Backend | Flask (Python) | Framework ringan dengan middleware keamanan |
| Database | SQLite / MySQL | Mendukung prepared statement |
| Authentication | Flask-Login + Session | Session timeout + invalidation |
| Password Security | bcrypt | Salted hashing tahan brute force |
| Logging | File-based security log | Audit trail aktivitas |

---

# 🧩 Threat Modeling

Metodologi keamanan yang digunakan:

- STRIDE
- Data Flow Diagram (DFD)
- Attack Tree

Dokumentasi lengkap tersedia pada folder:

```text
/docs
```

---

# 📁 Struktur Direktori

```text
secure-notes-app/
│
├── .venv/
│
├── app/
│   ├── __init__.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   └── note.py
│   │
│   ├── routes/
│   │   ├── auth.py
│   │   ├── notes.py
│   │   └── admin.py
│   │
│   ├── templates/
│   ├── static/
│   │
│   ├── utils/
│   │   ├── security.py
│   │   ├── auth_middleware.py
│   │   └── logger.py
│   │
│   └── config.py
│
├── logs/
│   └── security.log
│
├── instance/
│   └── notes.db
│
├── docs/
│
├── tests/
│
├── .env
├── .gitignore
├── requirements.txt
├── run.py
├── README.md
└── SECURITY.md
```

---

# 🚀 Cara Install & Jalankan

## 1. Clone Repository

```bash
git clone https://github.com/MeongLy/secure-notes-app.git
cd secure-notes-app
```

---

## 2. Buat Virtual Environment

```bash
python -m venv .venv
```

### Aktivasi Virtual Environment

#### Windows

```bash
.venv\Scripts\activate
```

#### Linux/macOS

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Buat File `.env`

```env
SECRET_KEY=rahasia_yang_sangat_aman_dan_panjang
FLASK_ENV=development
SESSION_TIMEOUT_MINUTES=15
MAX_LOGIN_ATTEMPTS=5
```

⚠️ Jangan pernah commit file `.env` ke repository publik.

---

## 5. Jalankan Aplikasi

```bash
python run.py
```

Aplikasi akan berjalan di:

```text
http://127.0.0.1:5000
```

---

# 🚫 File yang Tidak Di-commit

File sensitif dimasukkan ke `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.db
logs/
```

---

# 📌 Status Project

| Minggu | Status |
|---|---|
| Minggu 1 — Threat Modeling | ✅ Done |
| Minggu 2 — Secure Coding | ✅ Done |
| Minggu 3 — Security Testing | ✅ Done |
| Minggu 4 — Hardening | ✅ Done |

---

# 🔐 Secure Notes App

Aplikasi catatan pribadi berbasis web yang menerapkan prinsip **Secure Software Engineering (SSE)** dengan berbagai kontrol keamanan.

---

## 📋 Deskripsi Proyek

Secure Notes App adalah aplikasi web untuk menyimpan dan mengelola catatan pribadi secara aman. Aplikasi ini dibangun menggunakan **Flask (Python)** dengan database **SQLite** dan menerapkan berbagai kontrol keamanan sesuai standar OWASP.

### Fitur Utama
- Registrasi dan Login pengguna
- CRUD catatan pribadi
- Panel Admin (kelola user, lihat log keamanan)
- Upload file attachment

### Kontrol Keamanan
- ✅ Password hashing (pbkdf2:sha256)
- ✅ Rate limiting (5 percobaan login)
- ✅ Account lock (15 menit)
- ✅ Session timeout (15 menit)
- ✅ CSRF protection pada semua form
- ✅ Security headers (X-Frame-Options, X-Content-Type-Options)
- ✅ Input validation dan sanitasi (XSS prevention)
- ✅ SQL Injection prevention (SQLAlchemy ORM)
- ✅ IDOR prevention (ownership validation)
- ✅ Security logging
- ✅ Dependency audit (pip-audit)

---

## 🚀 Cara Install

### 1. Clone Repository
```bash
git clone https://github.com/MeongLy/secure-notes-app.git
cd secure-notes-app


# 📄 License

Project ini dibuat untuk keperluan akademik mata kuliah Secure Software Engineering (SSE).

---
