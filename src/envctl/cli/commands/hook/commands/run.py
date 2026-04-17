"""Internal managed hook runner command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.domain.hooks import HookName
from envctl.errors import ExecutionError

HOOK_ARGUMENT = typer.Argument(...)


@handle_errors
def hook_run_command(
    ctx: typer.Context,
    hook_name: str = HOOK_ARGUMENT,
) -> None:
    """Run one managed hook policy."""
    from envctl.cli.presenters import present
    from envctl.cli.presenters.models import CommandOutput
    from envctl.cli.presenters.outputs.guard import build_guard_secrets_output
    from envctl.cli.runtime import is_json_output
    from envctl.services.hook_service import HookExecutionService

    try:
        resolved_hook_name = HookName(hook_name)
    except ValueError as exc:
        raise ExecutionError(f"Unsupported hook: {hook_name}") from exc

    result = HookExecutionService().run_guarded_hook(resolved_hook_name, ctx.args)
    base_output = build_guard_secrets_output(result.guard_result)

    output = CommandOutput(
        title=base_output.title,
        messages=base_output.messages,
        sections=base_output.sections,
        metadata={
            **base_output.metadata,
            "kind": "hook_run",
            "hook_name": resolved_hook_name.value,
            "exit_code": result.exit_code,
        },
    )

    present(
        output,
        output_format="json" if is_json_output() else "text",
    )

    raise typer.Exit(code=result.exit_code)
