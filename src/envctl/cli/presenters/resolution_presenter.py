"""Human-oriented presenter for resolution reports."""

from __future__ import annotations

import typer

from envctl.cli.presenters.common import print_bullet_list, print_section
from envctl.domain.resolution import ResolutionReport
from envctl.utils.masking import mask_value
from envctl.utils.output import print_kv


def _render_missing_required(report: ResolutionReport) -> None:
    """Render missing required keys."""
    if not report.missing_required:
        return

    print_section("Missing required keys")
    print_bullet_list(report.missing_required)


def _render_invalid_keys(report: ResolutionReport) -> None:
    """Render invalid keys."""
    if not report.invalid_keys:
        return

    print_section("Invalid keys")
    for key in report.invalid_keys:
        item = report.values.get(key)
        if item is not None and item.detail:
            typer.echo(f"  - {key}: {item.detail}")
        else:
            typer.echo(f"  - {key}")


def _render_unknown_keys(report: ResolutionReport) -> None:
    """Render unknown keys found in the vault."""
    if not report.unknown_keys:
        return

    print_section("Unknown keys in vault")
    print_bullet_list(report.unknown_keys)


def _render_resolved_values(report: ResolutionReport) -> None:
    """Render resolved values."""
    print_section("Resolved values")

    if not report.values:
        typer.echo("  None")
        return

    for key in sorted(report.values):
        item = report.values[key]
        shown_value = mask_value(item.value) if item.masked else item.value
        suffix = "" if item.valid else f" — invalid: {item.detail or 'unknown reason'}"
        expansion_suffix = ""
        if item.expansion_status == "expanded":
            refs = ", ".join(item.expansion_refs)
            expansion_suffix = f" [expanded{': ' + refs if refs else ''}]"
        elif item.expansion_status == "error" and item.expansion_error is not None:
            expansion_suffix = f" [expansion error: {item.expansion_error.kind}]"
        typer.echo(f"  {key} = {shown_value} ({item.source}){expansion_suffix}{suffix}")


def render_resolution(report: ResolutionReport) -> None:
    """Render one resolved environment report.

    Order matters here: show actionable problems first, then the full resolved view.
    """
    _render_missing_required(report)
    _render_invalid_keys(report)
    _render_unknown_keys(report)
    _render_resolved_values(report)


def render_resolution_view(
    *,
    profile: str,
    group: str | None,
    report: ResolutionReport,
) -> None:
    """Render one resolved environment view including the active profile."""
    print_kv("profile", profile)
    if group is not None:
        print_kv("group", group)
    render_resolution(report)
