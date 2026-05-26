# Laporan DAST (Dynamic Application Security Testing)
## Secure Notes App

| **Nama Proyek** | Secure Notes App |
| **Tanggal Pengujian** | 26 Mei 2026 |
| **Penguji** | Rusmawatie & Ariel |
| **Tool** | OWASP ZAP v2.14.0 |
| **Target** | http://127.0.0.1:5000 |

---

## 📊 Ringkasan Hasil Pengujian

| Kategori | Jumlah Temuan |
|----------|---------------|
| HIGH | 0 |
| MEDIUM | X |
| LOW | X |
| INFO | X |

**Kesimpulan:** Tidak ditemukan kerentanan HIGH pada aplikasi. Beberapa temuan LOW/MEDIUM terkait security headers dan rekomendasi perbaikan.

---

---

## 📋 Hasil Pengujian Manual (5 Kategori OWASP Top 10)

### 1. SQL Injection (A03:2021 - Injection)

| **Langkah Reproduksi** | **Hasil** |
|------------------------|-----------|
| 1. Buka halaman login `/auth/login` | ✅ AMAN |
| 2. Masukkan payload `' OR '1'='1` di field username | |
| 3. Password diisi `anything` | |
| 4. Klik Login | |

**Status:** ✅ **Tidak Rentan** - Aplikasi menggunakan SQLAlchemy ORM dengan parameterized query

**Screenshot:** ![SQL Injection Test](screenshots/Minggu3/sql_injection_test.png)

---

### 2. Cross-Site Scripting (XSS) (A03:2021 - Injection)

| **Langkah Reproduksi** | **Hasil** |
|------------------------|-----------|
| 1. Buka halaman `/notes/create` | ✅ AMAN |
| 2. Masukkan `<script>alert('XSS')</script>` di judul | |
| 3. Masukkan `<img src=x onerror=alert('XSS')>` di konten | |
| 4. Simpan dan lihat catatan | |

**Status:** ✅ **Tidak Rentan** - Jinja2 autoescape melakukan escaping otomatis

**Screenshot:** ![XSS Test](screenshots/Minggu3/xss_test.png)

---

### 3. Broken Access Control - IDOR (A01:2021 - Broken Access Control)

| **Langkah Reproduksi** | **Hasil** |
|------------------------|-----------|
| 1. Login sebagai User A, buat catatan (ID=1) | ✅ AMAN |
| 2. Logout, login sebagai User B | |
| 3. Akses `http://127.0.0.1:5000/notes/1` | |

**Status:** ✅ **Tidak Rentan** - Decorator `@ownership_required` memblokir akses

**Screenshot:** ![IDOR Test](screenshots/Minggu3/idor_test.png)

---

### 4. Security Misconfiguration (A05:2021 - Security Misconfiguration)

| **Langkah Reproduksi** | **Hasil** |
|------------------------|-----------|
| 1. Buka DevTools (F12) → Network tab | ⚠️ **Partial** |
| 2. Cek response headers | |
| 3. Apakah security headers terpasang? | |

**Temuan:** Beberapa security headers belum terpasang:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`

**Status:** ⚠️ **Perlu Perbaikan** - Tambahkan header keamanan

**Screenshot:** ![Security Headers](screenshots/Minggu3/security_headers.png)

---

### 5. Cryptographic Failures (A02:2021 - Cryptographic Failures)

| **Langkah Reproduksi** | **Hasil** |
|------------------------|-----------|
| 1. Lihat database, cek kolom password | ✅ AMAN |
| 2. Apakah password di-hash? | |

**Status:** ✅ **Aman** - Password di-hash dengan pbkdf2:sha256

**Screenshot:** ![Password Hash](screenshots/Minggu3/password_hash.png)

---

## 📋 Tabel Ringkasan Pengujian Manual

| No | Kategori | Status | Severity |
|----|----------|--------|----------|
| 1 | SQL Injection | ✅ Aman | - |
| 2 | XSS | ✅ Aman | - |
| 3 | IDOR | ✅ Aman | - |
| 4 | Security Misconfiguration | ⚠️ Partial | LOW |
| 5 | Cryptographic Failures | ✅ Aman | - |

---

## 📎 Lampiran

- [Laporan ZAP HTML](screenshots/Minggu3/zap_report.html)
- [Laporan ZAP PDF](screenshots/Minggu3/zap_report.pdf)
- [Screenshot Pengujian](screenshots/Minggu3/)
