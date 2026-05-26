## 📌 Format Log Security Event

```text
[TIMESTAMP] [EVENT_TYPE] IP: [IP_ADDRESS] | User: [USERNAME] | Status: [STATUS] | Details: [DETAILS]
```

---

## 💻 Kode Implementasi

**Lokasi:** `app/utils/logger.py` (line 24–45)

```python
def log_security_event(
    event_type,
    username=None,
    details=None,
    ip_address=None,
    status=None
):
    if ip_address is None:
        ip_address = request.remote_addr if request else "unknown"

    log_entry = f"[{event_type}] IP: {ip_address}"

    if username:
        log_entry += f" | User: {username}"

    if status:
        log_entry += f" | Status: {status}"

    if details:
        log_entry += f" | Details: {details}"

    security_logger.info(log_entry)
```

---

## 📝 Contoh Output Log

```log
[2026-05-26 10:30:15] [LOGIN_SUCCESS]
IP: 127.0.0.1 | User: admin | Status: success

[2026-05-26 10:32:20] [NOTE_CREATED]
IP: 127.0.0.1 | User: admin | Status: success |
Details: Note ID: 1 | Title: Test Note

[2026-05-26 10:35:45] [UNAUTHORIZED_ACCESS]
IP: 192.168.1.100 | User: user1 | Status: failed |
Details: Resource: Note:2
```

---

## 🔐 Jenis Event yang Dicatat

| Event Type | Deskripsi |
|---|---|
| `LOGIN_SUCCESS` | Login berhasil |
| `LOGIN_FAILED` | Login gagal |
| `REGISTER_SUCCESS` | Registrasi berhasil |
| `NOTE_CREATED` | Catatan berhasil dibuat |
| `NOTE_UPDATED` | Catatan berhasil diperbarui |
| `NOTE_DELETED` | Catatan berhasil dihapus |
| `UNAUTHORIZED_ACCESS` | Akses tanpa izin |
| `LOGOUT` | User logout |
| `ACCOUNT_LOCKED` | Akun terkunci akibat login gagal berulang |

---
