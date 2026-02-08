"""
Datetime helpers.
"""

from datetime import datetime, timezone


def utcnow_aware() -> datetime:
    """Return current UTC time with tzinfo for DB fields."""
    return datetime.now(timezone.utc)
