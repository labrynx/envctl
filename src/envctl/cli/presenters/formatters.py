"""Small human-readable formatting helpers for presenters."""

from __future__ import annotations

_STATUS_PREFIXES: dict[str, str] = {
    "ok": "[OK]",
    "warn": "[WARN]",
    "fail": "[FAIL]",
}


def render_action_state(has_issues: bool) -> str:
    """Render one top-level human status."""
    return "action needed" if has_issues else "healthy"


def render_check_prefix(status: str) -> str:
    """Render a standard prefix for inspection-style output."""
    return _STATUS_PREFIXES.get(status, "[INFO]")


def render_present_missing(value: bool) -> str:
    """Render one boolean as present/missing."""
    return "present" if value else "missing"


def render_valid_invalid(value: bool) -> str:
    """Render one boolean as valid/invalid."""
    return "valid" if value else "invalid"
