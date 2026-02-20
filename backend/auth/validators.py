"""
Input validators for authentication fields.
All validation runs on the backend – never rely solely on frontend checks.
"""

import re
from typing import Optional


# Pre-compiled regex for a reasonable email format check (RFC 5322 simplified).
_EMAIL_RE = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)


def validate_email_format(email: str) -> Optional[str]:
    """Validate basic email format.

    Returns:
        ``None`` if valid, or an error message string if invalid.
    """
    if not email or not email.strip():
        return "Email is required."
    if not _EMAIL_RE.match(email.strip()):
        return "Invalid email format."
    return None


def validate_password_strength(password: str) -> Optional[str]:
    """Validate password against strength requirements.

    Requirements:
        - Minimum 8 characters
        - At least 1 uppercase letter
        - At least 1 lowercase letter
        - At least 1 digit
        - At least 1 special character

    Returns:
        ``None`` if strong enough, or an error message string describing the
        first failing requirement.
    """
    if not password:
        return "Password is required."
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?`~]", password):
        return "Password must contain at least one special character."
    return None
