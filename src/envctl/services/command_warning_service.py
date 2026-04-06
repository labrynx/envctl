"""Helpers for command-level warnings and compatibility checks."""

from __future__ import annotations

from envctl.domain.diagnostics import CommandWarning, InspectResult
from envctl.domain.doctor import DoctorCheck


def build_deprecated_command_warning(
    *,
    command_name: str,
    replacement: str,
    removal_version: str,
) -> CommandWarning:
    """Build one stable deprecated-command warning."""
    return CommandWarning(
        kind="deprecated_command",
        message=(
            f"Warning: `{command_name}` is deprecated and will be removed in {removal_version}.\n"
            f"Use `{replacement}` instead."
        ),
    )


def build_doctor_legacy_checks(result: InspectResult) -> tuple[DoctorCheck, ...]:
    """Build compatibility doctor checks from an inspect result."""
    return (
        DoctorCheck(
            name="project",
            status="ok",
            detail=f"Resolved project: {result.project.display_name}",
        ),
        DoctorCheck(
            name="active_profile",
            status="ok",
            detail=f"Active profile: {result.active_profile}",
        ),
    )
