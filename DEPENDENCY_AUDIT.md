# Laporan Dependency Audit - Secure Notes App

| **Nama Proyek** | Secure Notes App |
| **Tanggal Audit** | 26 Mei 2026 |
| **Tool** | pip-audit |
| **Penulis** | Rusmawatie & Ariel |

---

## 📊 Ringkasan Eksekutif

| Metrik | Nilai |
|--------|-------|
| **Total Packages** | 15 |
| **Total Vulnerabilities Found** | 13 |
| **CRITICAL** | 0 |
| **HIGH** | 13 |
| **MEDIUM** | 0 |
| **LOW** | 0 |
| **Status** | ✅ FIXED |

**Kesimpulan:** Ditemukan 13 vulnerabilities pada 4 packages. Semua telah diperbaiki dengan update ke versi terbaru.

---

## 📋 Output pip-audit (Sebelum Perbaikan)

```bash
$ pip-audit --requirement requirements.txt

Found 13 known vulnerabilities in 4 packages

Name          Version ID             Fix Versions
------------- ------- -------------- ------------
flask         2.3.3   CVE-2026-27205 3.1.3
jinja2        3.1.2   CVE-2024-22195 3.1.3
jinja2        3.1.2   CVE-2024-34064 3.1.4
jinja2        3.1.2   CVE-2024-56326 3.1.5
jinja2        3.1.2   CVE-2024-56201 3.1.5
jinja2        3.1.2   CVE-2025-27516 3.1.6
python-dotenv 1.0.0   CVE-2026-28684 1.2.2
werkzeug      2.3.8   CVE-2024-34069 3.0.3
werkzeug      2.3.8   CVE-2024-49766 3.0.6
werkzeug      2.3.8   CVE-2024-49767 3.0.6
werkzeug      2.3.8   CVE-2025-66221 3.1.4
werkzeug      2.3.8   CVE-2026-21860 3.1.5
werkzeug      2.3.8   CVE-2026-27199 3.1.6
