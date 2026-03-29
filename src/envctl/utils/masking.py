"""Masking helpers for sensitive output."""

from __future__ import annotations


def mask_value(value: str) -> str:
    """Mask a value while preserving only a tiny prefix."""
    if not value:
        return ""
    if len(value) <= 4:
        return "*" * len(value)
    return f"{value[:2]}{'*' * (len(value) - 2)}"
