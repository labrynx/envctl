"""Presenters for run command advisories."""

from __future__ import annotations

from envctl.utils.output import print_warning


def render_run_warnings(warnings: tuple[str, ...]) -> None:
    """Render run command warnings."""
    for warning in warnings:
        print_warning(warning)
