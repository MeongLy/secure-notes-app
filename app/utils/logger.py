# app/utils/logger.py
import logging
import os
from datetime import datetime
from flask import request, session
from functools import wraps

# Create logs directory if not exists
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure security logger
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)

# File handler for security logs
security_log_file = os.path.join(LOG_DIR, "security.log")
file_handler = logging.FileHandler(security_log_file)
file_handler.setLevel(logging.INFO)

# Formatter for security logs
formatter = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(formatter)

security_logger.addHandler(file_handler)

# Prevent propagation to root logger
security_logger.propagate = False


def log_security_event(
    event_type, username=None, details=None, ip_address=None, status=None
):
    """
    Log security events (SR-06: Security logging)

    Args:
        event_type: Type of event (login_success, login_failed, note_created, etc.)
        username: Username of the user
        details: Additional details about the event
        ip_address: Client IP address
        status: Status of the event (success/failure)
    """
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


def log_login_attempt(username, success, ip_address=None, reason=None):
    """SR-06: Log login attempts (success/failure)"""
    event = "LOGIN_SUCCESS" if success else "LOGIN_FAILED"
    details = reason if reason else None
    log_security_event(
        event,
        username=username,
        ip_address=ip_address,
        status="success" if success else "failed",
        details=details,
    )


def log_logout(username, ip_address=None):
    """Log logout events (SR-10: Session cleanup)"""
    log_security_event(
        "LOGOUT", username=username, ip_address=ip_address, status="success"
    )


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


def log_unauthorized_access(username, resource, ip_address=None, details=None):
    """Log unauthorized access attempts (for monitoring)"""
    log_security_event(
        "UNAUTHORIZED_ACCESS",
        username=username,
        ip_address=ip_address,
        status="failed",
        details=f"Resource: {resource} | {details if details else ''}",
    )


def log_admin_action(
    admin_username, action, target_user=None, details=None, ip_address=None
):
    """Log admin actions for audit (SR-06)"""
    log_details = f"Action: {action}"
    if target_user:
        log_details += f" | Target User: {target_user}"
    if details:
        log_details += f" | {details}"

    log_security_event(
        "ADMIN_ACTION",
        username=admin_username,
        ip_address=ip_address,
        status="success",
        details=log_details,
    )


def log_database_error(error_type, details=None, username=None, ip_address=None):
    """Log database errors that might indicate attacks (SQL injection attempts)"""
    log_security_event(
        "DATABASE_ERROR",
        username=username,
        ip_address=ip_address,
        status="failed",
        details=f"Error: {error_type} | {details if details else ''}",
    )


def get_security_logs(limit=100):
    """Read recent security logs (for admin panel)"""
    logs = []
    try:
        if os.path.exists(security_log_file):
            with open(security_log_file, "r") as f:
                lines = f.readlines()
                # Get last 'limit' lines
                for line in lines[-limit:]:
                    logs.append(line.strip())
    except Exception as e:
        logs.append(f"Error reading logs: {str(e)}")

    return logs


def clear_security_logs():
    """Clear security logs (admin only)"""
    try:
        if os.path.exists(security_log_file):
            with open(security_log_file, "w") as f:
                f.write("")
            return True
    except Exception:
        return False
    return False
