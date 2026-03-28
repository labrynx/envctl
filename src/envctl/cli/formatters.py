"""CLI output formatters."""

from __future__ import annotations

import typer

from envctl.domain.doctor import DoctorCheck
from envctl.domain.remove import RemoveResult
from envctl.domain.status import StatusReport
from envctl.utils.output import print_success, print_warning


def render_doctor_checks(checks: list[DoctorCheck]) -> bool:
    """Render doctor checks and return whether failures were found."""
    status_prefix = {
        "ok": "[OK]",
        "warn": "[WARN]",
        "fail": "[FAIL]",
    }

    has_failures = False

    for check in checks:
        prefix = status_prefix.get(check.status, "[INFO]")
        typer.echo(f"{prefix} {check.name}: {check.detail}")
        if check.status == "fail":
            has_failures = True

    return has_failures


def render_status_report(report: StatusReport) -> None:
    """Render a status report."""
    if report.project_slug and report.project_id:
        typer.echo(f"On project {report.project_slug} ({report.project_id})")
        typer.echo()
    elif report.project_slug:
        typer.echo(f"On project {report.project_slug}")
        typer.echo()

    typer.echo(f"Status: {report.state}")
    typer.echo()
    typer.echo(report.summary)
    typer.echo()
    typer.echo(f"Repository env: {report.repo_env_status}")
    typer.echo(f"Vault env: {report.vault_env_status}")

    if report.issues:
        typer.echo()
        typer.echo("Issues:")
        for issue in report.issues:
            typer.echo(f"  - {issue}")

    if report.suggested_action:
        typer.echo()
        typer.echo("Suggested action:")
        typer.echo(f"  {report.suggested_action}")


def render_remove_result(result: RemoveResult) -> None:
    """Render a remove result."""
    print_success(f"Removed envctl management for '{result.context.project_slug}'")
    typer.echo()

    if result.restored_repo_env_file:
        print_success("Restored .env.local in the repository")
    elif result.removed_repo_symlink:
        print_success("Removed repository symlink")

    if result.removed_repo_metadata:
        print_success("Removed repository metadata")

    if result.removed_vault_env:
        print_success("Deleted managed vault env file")

    if result.removed_vault_project_dir:
        print_success("Deleted vault project directory")

    if result.left_regular_repo_env_untouched:
        print_warning("A regular .env.local file was left untouched")

    if result.removed_broken_repo_symlink:
        print_warning("Removed a broken symlink without restoration")
