"""Human-oriented presenter for resolution reports."""

from __future__ import annotations

import typer

from envctl.cli.presenters.common import print_section
from envctl.domain.resolution import ResolutionReport
from envctl.utils.masking import mask_value
from envctl.utils.output import print_kv


def build_resolution_problem_lines(
    report: ResolutionReport,
    *,
    unknown_keys_title: str = "Unknown keys in vault",
) -> list[str]:
    """Build actionable problem lines for one resolution report."""
    lines: list[str] = []

    if report.missing_required:
        lines.extend(("", "Missing required keys"))
        lines.extend(f"  - {key}" for key in report.missing_required)

    if report.invalid_keys:
        lines.extend(("", "Invalid keys"))
        for key in report.invalid_keys:
            item = report.values.get(key)
            if item is not None and item.detail:
                lines.append(f"  - {key}: {item.detail}")
            else:
                lines.append(f"  - {key}")

    if report.unknown_keys:
        lines.extend(("", unknown_keys_title))
        lines.extend(f"  - {key}" for key in report.unknown_keys)

    return lines


def render_resolution_problems(
    report: ResolutionReport,
    *,
    unknown_keys_title: str = "Unknown keys in vault",
) -> None:
    """Render actionable problem sections for one resolution report."""
    for line in build_resolution_problem_lines(
        report,
        unknown_keys_title=unknown_keys_title,
    ):
        typer.echo(line)


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
    render_resolution_problems(report)
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
