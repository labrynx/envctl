"""CLI output formatters."""

from __future__ import annotations

import typer

from envctl.domain.doctor import DoctorCheck
from envctl.domain.resolution import ResolutionReport
from envctl.domain.status import StatusReport
from envctl.utils.masking import mask_value


def render_doctor_checks(checks: list[DoctorCheck]) -> bool:
    """Render doctor checks and return whether failures were found."""
    has_failures = False
    for check in checks:
        prefix = {
            "ok": "[OK]",
            "warn": "[WARN]",
            "fail": "[FAIL]",
        }.get(check.status, "[INFO]")
        typer.echo(f"{prefix} {check.name}: {check.detail}")
        if check.status == "fail":
            has_failures = True
    return has_failures


def render_resolution(report: ResolutionReport) -> None:
    """Render a resolved environment report."""
    if report.values:
        typer.echo("Resolved values:")
        for key in sorted(report.values):
            item = report.values[key]
            shown = mask_value(item.value) if item.masked else item.value
            valid_suffix = "" if item.valid else f" [invalid: {item.detail}]"
            typer.echo(f"  {key} = {shown} ({item.source}){valid_suffix}")
    else:
        typer.echo("No resolved values.")

    if report.missing_required:
        typer.echo()
        typer.echo("Missing required keys:")
        for key in report.missing_required:
            typer.echo(f"  - {key}")

    if report.invalid_keys:
        typer.echo()
        typer.echo("Invalid keys:")
        for key in report.invalid_keys:
            typer.echo(f"  - {key}")

    if report.unknown_keys:
        typer.echo()
        typer.echo("Unknown keys in vault:")
        for key in report.unknown_keys:
            typer.echo(f"  - {key}")


def render_status(report: StatusReport) -> None:
    """Render the status report."""
    typer.echo(f"Project: {report.project_slug} ({report.project_id})")
    typer.echo(f"Repository: {report.repo_root}")
    typer.echo()
    typer.echo(report.summary)
    typer.echo()
    typer.echo(f"Contract present: {'yes' if report.contract_exists else 'no'}")
    typer.echo(f"Vault values present: {'yes' if report.vault_exists else 'no'}")
    typer.echo(f"Resolved valid: {'yes' if report.resolved_valid else 'no'}")

    if report.issues:
        typer.echo()
        typer.echo("Issues:")
        for issue in report.issues:
            typer.echo(f"  - {issue}")

    if report.suggested_action:
        typer.echo()
        typer.echo(f"Suggested action: {report.suggested_action}")