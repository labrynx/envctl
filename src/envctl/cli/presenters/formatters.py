"""Small human-readable formatting helpers for presenters."""

from __future__ import annotations


def render_action_state(has_issues: bool) -> str:
    """Render one top-level human status."""
    return "action needed" if has_issues else "healthy"


def render_present_missing(value: bool) -> str:
    """Render one boolean as present/missing."""
    return "present" if value else "missing"


def render_valid_invalid(value: bool) -> str:
    """Render one boolean as valid/invalid."""
    return "valid" if value else "invalid"
