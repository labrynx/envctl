"""Managed hooks repair command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.presenters import present
from envctl.cli.presenters.common import merge_outputs
from envctl.cli.presenters.outputs.hooks import build_hook_operation_output
from envctl.cli.presenters.outputs.warnings import build_command_warnings_output
from envctl.cli.runtime import is_json_output
from envctl.services.context_service import load_project_context
from envctl.services.hook_service import HookService

FORCE_OPTION = typer.Option(
    False,
    "--force",
    help="Overwrite foreign supported hooks in the effective managed hooks path.",
)


@handle_errors
@requires_writable_runtime("hooks repair")
def hooks_repair_command(force: bool = FORCE_OPTION) -> None:
    """Repair envctl-managed hooks."""
    _config, context = load_project_context()
    report = HookService(context.repo_root).repair(force=force)
    exit_code = 0 if report.ok else 1

    output = build_hook_operation_output(
        report,
        repo_root=context.repo_root,
        operation_name="repair",
    )

    if context.runtime_warnings:
        output = merge_outputs(
            build_command_warnings_output(context.runtime_warnings),
            output,
        )

    present(output, output_format="json" if is_json_output() else "text")
    raise typer.Exit(code=exit_code)
