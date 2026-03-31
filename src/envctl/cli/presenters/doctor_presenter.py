"""Human-oriented presenter for doctor checks."""

from __future__ import annotations

import typer

from envctl.cli.presenters.common import (
    print_kv_line,
    print_section,
    print_title,
    render_check_prefix,
)
from envctl.domain.doctor import DoctorCheck


def _split_checks(
    checks: list[DoctorCheck],
) -> tuple[list[DoctorCheck], list[DoctorCheck], list[DoctorCheck]]:
    """Split checks by severity."""
    failures = [check for check in checks if check.status == "fail"]
    warnings = [check for check in checks if check.status == "warn"]
    healthy = [check for check in checks if check.status == "ok"]
    return failures, warnings, healthy


def _render_summary(
    failures: list[DoctorCheck],
    warnings: list[DoctorCheck],
    healthy: list[DoctorCheck],
) -> None:
    """Render the doctor summary block."""
    print_title("Doctor summary")
    print_kv_line("failures", str(len(failures)))
    print_kv_line("warnings", str(len(warnings)))
    print_kv_line("healthy", str(len(healthy)))
    print_kv_line("checks", str(len(failures) + len(warnings) + len(healthy)))


def _render_group(title: str, checks: list[DoctorCheck]) -> None:
    """Render one grouped doctor section."""
    if not checks:
        return

    print_section(title)
    for check in checks:
        prefix = render_check_prefix(check.status)
        typer.echo(f"  {prefix} {check.name}: {check.detail}")


def render_doctor_checks(checks: list[DoctorCheck]) -> bool:
    """Render doctor checks and return whether failures were found."""
    failures, warnings, healthy = _split_checks(checks)

    _render_summary(failures, warnings, healthy)
    _render_group("Failures", failures)
    _render_group("Warnings", warnings)
    _render_group("Healthy checks", healthy)

    return bool(failures)
