"""Timing helpers for observability."""

from __future__ import annotations

from datetime import datetime, timezone


def utcnow() -> datetime:
    """Return timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)
