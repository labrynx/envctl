"""Human-oriented presenter for project status."""

from __future__ import annotations

import typer

from envctl.cli.presenters.common import (
    print_bullet_list,
    print_kv_line,
    print_section,
    print_title,
    render_action_state,
    render_present_missing,
    render_valid_invalid,
)
from envctl.domain.status import StatusReport
from envctl.utils.output import print_kv


def _has_status_issues(report: StatusReport) -> bool:
    """Return whether the report indicates user-facing issues."""
    return bool(report.issues) or not report.contract_exists or not report.resolved_valid


def _render_header(report: StatusReport) -> None:
    """Render the overall status header."""
    print_title("Status")
    print_kv_line("state", render_action_state(_has_status_issues(report)))


def _render_project(report: StatusReport) -> None:
    """Render project metadata."""
    print_section("Project")
    print_kv_line("name", report.project_slug)
    print_kv_line("id", report.project_id)
    print_kv_line("repository", str(report.repo_root))


def _render_checks(report: StatusReport) -> None:
    """Render high-level checks."""
    print_section("Checks")
    print_kv_line("contract", render_present_missing(report.contract_exists))
    print_kv_line("vault values", render_present_missing(report.vault_exists))
    print_kv_line("resolution", render_valid_invalid(report.resolved_valid))


def _render_summary(report: StatusReport) -> None:
    """Render the human summary text."""
    print_section("Summary")
    typer.echo(f"  {report.summary}")


def _render_issues(report: StatusReport) -> None:
    """Render issue list when present."""
    if not report.issues:
        return

    print_section("Issues")
    print_bullet_list(report.issues)


def _render_next_step(report: StatusReport) -> None:
    """Render suggested next action when present."""
    if not report.suggested_action:
        return

    print_section("Next step")
    typer.echo(f"  {report.suggested_action}")


def render_status(report: StatusReport) -> None:
    """Render one human-oriented project status report."""
    _render_header(report)
    _render_project(report)
    _render_checks(report)
    _render_summary(report)
    _render_issues(report)
    _render_next_step(report)


def render_status_view(
    *,
    profile: str,
    report: StatusReport,
) -> None:
    """Render one human-oriented project status view including the active profile."""
    print_kv("profile", profile)
    render_status(report)
