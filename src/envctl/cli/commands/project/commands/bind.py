"""Bind command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime, text_output_only
from envctl.services.bind_service import run_bind
from envctl.utils.output import print_kv, print_success, print_warning


@handle_errors
@requires_writable_runtime("project bind")
@text_output_only("project bind")
def project_bind_command(
    project_id: str = typer.Argument(..., help="Existing canonical project id to bind."),
) -> None:
    """Bind the current repository checkout to an existing vault."""
    context, result = run_bind(project_id)

    if result.changed:
        print_success(f"Bound repository to {context.display_name}")
    else:
        print_warning(f"Repository already bound to {context.display_name}")

    print_kv("project_key", context.project_key)
    print_kv("project_id", context.project_id)
    print_kv("binding_source", context.binding_source)
    print_kv("repo_root", str(context.repo_root))
    print_kv("vault_dir", str(context.vault_project_dir))
    print_kv("vault_values", str(context.vault_values_path))
