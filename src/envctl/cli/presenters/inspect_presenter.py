"""Presenter for detailed inspect output."""

from __future__ import annotations

import typer

from envctl.cli.presenters.common import print_kv_line, print_section, print_title
from envctl.domain.diagnostics import InspectKeyResult, InspectResult
from envctl.domain.resolution import ResolvedValue
from envctl.utils.masking import mask_value


def _render_value(item: ResolvedValue) -> str:
    if item.value == "":
        return "[missing]"
    return str(mask_value(item.value) if item.masked else item.value)


def render_inspect_result(result: InspectResult) -> None:
    """Render the detailed ``inspect`` report."""
    print_title("Project")
    print_kv_line("repo_root", str(result.project.repo_root))
    print_kv_line("project_slug", result.project.project_slug)
    print_kv_line("project_id", result.project.project_id)
    print_kv_line("binding", result.project.binding_source)
    print_kv_line("vault_dir", str(result.project.vault_project_dir))

    print_section("Runtime")
    print_kv_line("profile", result.active_profile)
    print_kv_line("scope", result.selection.describe())
    print_kv_line("contract", result.contract_path)
    print_kv_line("values", result.values_path)

    print_section("Summary")
    print_kv_line("total", str(result.summary.total))
    print_kv_line("valid", str(result.summary.valid))
    print_kv_line("invalid", str(result.summary.invalid))
    print_kv_line("unknown", str(result.summary.unknown))

    print_section("Variables")
    if not result.variables:
        typer.echo("  None")
    else:
        for item in result.variables:
            detail_suffix = f" — {item.detail}" if item.detail else ""
            expansion_suffix = ""
            if item.expansion_status == "expanded":
                refs = ", ".join(item.expansion_refs)
                expansion_suffix = f" [expanded{': ' + refs if refs else ''}]"
            elif item.expansion_status == "error" and item.expansion_error is not None:
                expansion_suffix = f" [expansion error: {item.expansion_error.detail}]"
            typer.echo(
                f"  {item.key} = {_render_value(item)} ({item.source})"
                f"{expansion_suffix}{detail_suffix}"
            )

    if result.problems:
        print_section("Problems")
        for problem in result.problems:
            typer.echo(f"  {problem.key}")
            typer.echo(f"    error: {problem.message}")
            for action in problem.actions:
                typer.echo(f"    action: {action}")


def render_inspect_key_result(result: InspectKeyResult) -> None:
    """Render ``inspect KEY`` output."""
    item = result.item
    print_title("Variable")
    print_kv_line("key", item.key)
    print_kv_line("status", "valid" if item.valid else "invalid")
    print_kv_line("source", item.source)
    print_kv_line("sensitive", "yes" if result.sensitive else "no")
    print_kv_line("value", _render_value(item))
    if item.detail:
        print_kv_line("detail", item.detail)

    print_section("Contract")
    print_kv_line("type", result.contract_type)
    print_kv_line("format", result.contract_format or "none")
    print_kv_line("groups", ", ".join(result.groups) if result.groups else "none")
    print_kv_line("default", "none" if result.default is None else str(result.default))

    print_section("Resolution")
    print_kv_line("expanded", "yes" if item.expansion_status == "expanded" else "no")
    if item.expansion_refs:
        print_kv_line("expansion_refs", ", ".join(item.expansion_refs))
    if item.expansion_error is not None:
        print_kv_line("expansion_error", item.expansion_error.detail)
