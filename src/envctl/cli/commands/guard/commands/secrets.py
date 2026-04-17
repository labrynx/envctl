"""Git secret guard command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters import present
from envctl.cli.presenters.common import merge_outputs
from envctl.cli.presenters.outputs.guard import build_guard_secrets_output
from envctl.cli.presenters.outputs.warnings import build_command_warnings_output


@handle_errors
def guard_secrets_command() -> None:
    """Block staged envctl vault artifacts and master keys."""
    from envctl.cli.runtime import is_json_output
    from envctl.services.context_service import load_project_context
    from envctl.services.git_secret_guard_service import run_git_secret_guard

    _config, context = load_project_context()
    result = run_git_secret_guard(context)

    output = merge_outputs(
        build_command_warnings_output(context.runtime_warnings),
        build_guard_secrets_output(result),
    )

    present(
        output,
        output_format="json" if is_json_output() else "text",
    )

    if not result.ok:
        raise typer.Exit(code=1)
