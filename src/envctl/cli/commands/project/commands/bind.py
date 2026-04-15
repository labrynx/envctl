"""Bind command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.presenters import present
from envctl.cli.presenters.outputs.actions import build_project_bind_output
from envctl.cli.runtime import is_json_output


@handle_errors
@requires_writable_runtime("project bind")
def project_bind_command(
    project_id: str = typer.Argument(..., help="Existing canonical project id to bind."),
) -> None:
    """Bind the current repository checkout to an existing vault."""
    from envctl.services.bind_service import run_bind

    context, result = run_bind(project_id)

    present(
        build_project_bind_output(
            changed=result.changed,
            display_name=context.display_name,
            project_key=context.project_key,
            project_id=context.project_id,
            binding_source=context.binding_source,
            repo_root=context.repo_root,
            vault_dir=context.vault_project_dir,
            vault_values_path=context.vault_values_path,
        ),
        output_format="json" if is_json_output() else "text",
    )
