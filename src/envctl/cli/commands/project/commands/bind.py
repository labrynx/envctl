"""Bind command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime, text_output_only
from envctl.cli.presenters import render_project_bind_result
from envctl.services.bind_service import run_bind


@handle_errors
@requires_writable_runtime("project bind")
@text_output_only("project bind")
def project_bind_command(
    project_id: str = typer.Argument(..., help="Existing canonical project id to bind."),
) -> None:
    """Bind the current repository checkout to an existing vault."""
    context, result = run_bind(project_id)

    render_project_bind_result(
        changed=result.changed,
        display_name=context.display_name,
        project_key=context.project_key,
        project_id=context.project_id,
        binding_source=context.binding_source,
        repo_root=context.repo_root,
        vault_dir=context.vault_project_dir,
        vault_values_path=context.vault_values_path,
    )
