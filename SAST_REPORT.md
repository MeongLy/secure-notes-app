# Laporan SAST (Static Application Security Testing)
## Secure Notes App

| **Nama Proyek** | Secure Notes App |
| **Tanggal Scan** | 26 Mei 2026 |
| **Tool** | Bandit v1.7.8 |
| **Penulis** | Rusmawatie & Ariel |

---

## 📊 Ringkasan Eksekutif

| Parameter | Nilai |
|-----------|-------|
| **Total Files Scanned** | 25 files |
| **Total Lines of Code** | 1,381 lines |
| **Total Issues Found** | 1 |
| **CRITICAL** | 0 |
| **HIGH** | 1 |
| **MEDIUM** | 0 |
| **LOW** | 0 |

**Kesimpulan:** Ditemukan 1 isu HIGH severity terkait penggunaan algoritma hash MD5 yang lemah. Isu telah diperbaiki dengan mengganti MD5 menjadi Blake2b.

---

## 🖼️ Screenshot Hasil Scan

### Terminal Output (Sebelum Perbaikan)

![Bandit Scan - Before Fix](screenshots/Minggu3/Temuan_Risk_High_Sebelum.png)

---

## 📋 Tabel Temuan SAST

| No | Severity | CWE | Kategori | Lokasi Kode | Status | Mitigasi |
|----|----------|-----|----------|-------------|--------|----------|
| 1 | HIGH | CWE-327 | Use of Broken or Risky Cryptographic Algorithm | `app/utils/file_upload.py:132` | ✅ Fixed | Ganti MD5 dengan Blake2b |

---

## 📝 Temuan Detail dengan Bukti Perbaikan

### Temuan 1: Penggunaan algoritma hash MD5 yang lemah (HIGH)

**Severity:** HIGH
**CWE:** CWE-327 (Use of a Broken or Risky Cryptographic Algorithm)
**Lokasi:** `app/utils/file_upload.py` line 132

#### Kode Sebelum Perbaikan dan sesudah perbaikan

```python
# app/utils/file_upload.py - line 132
hash_part = hashlib.md5(f"{timestamp}{name}".encode()).hexdigest()[:8]

# app/utils/file_upload.py - line 132
hash_part = hashlib.blake2b(
    f"{timestamp}{name}".encode(), digest_size=8
).hexdigest()
