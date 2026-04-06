"""Presenter for compact check output."""

from __future__ import annotations

import typer

from envctl.domain.diagnostics import CheckResult, DiagnosticProblem
from envctl.utils.output import print_kv, print_section, print_success

_KIND_TITLES = {
    "missing_required": "Missing required keys",
    "invalid_value": "Invalid keys",
    "expansion_reference_error": "Expansion reference error",
    "unknown_key": "Unknown keys",
}


def _render_problem(problem: DiagnosticProblem) -> None:
    if problem.kind == "unknown_key":
        typer.echo(f"  - {problem.key}")
    else:
        typer.echo(f"  - {problem.key}: {problem.message}")
    for action in problem.actions:
        typer.echo(f"    action: {action}")


def render_check_result(result: CheckResult) -> None:
    """Render the compact ``check`` view."""
    print_kv("profile", result.active_profile)
    print_kv("scope", result.selection.describe())

    rendered_kinds: set[str] = set()
    for problem in result.problems:
        title = _KIND_TITLES.get(problem.kind, "Problems")
        if problem.kind not in rendered_kinds:
            print_section(title)
            rendered_kinds.add(problem.kind)
        _render_problem(problem)

    print_section("Summary")
    typer.echo(f"  total: {result.summary.total}")
    typer.echo(f"  valid: {result.summary.valid}")
    typer.echo(f"  invalid: {result.summary.invalid}")
    typer.echo(f"  unknown: {result.summary.unknown}")

    typer.echo()
    if result.ok:
        print_success("Environment contract satisfied")
    else:
        typer.echo("[ERROR] Environment contract is not satisfied")
