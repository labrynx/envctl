"""Internal managed hook runner command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, text_output_only
from envctl.domain.hooks import HookName
from envctl.errors import ExecutionError
from envctl.utils.output import print_error, print_kv, print_success

HOOK_ARGUMENT = typer.Argument(...)


@handle_errors
@text_output_only("hook-run")
def hook_run_command(
    ctx: typer.Context,
    hook_name: str = HOOK_ARGUMENT,
) -> None:
    """Run one managed hook policy."""
    try:
        resolved_hook_name = HookName(hook_name)
    except ValueError as exc:
        raise ExecutionError(f"Unsupported hook: {hook_name}") from exc

    from envctl.services.hook_service import HookExecutionService

    result = HookExecutionService().run_guarded_hook(resolved_hook_name, ctx.args)
    if result.guard_result.ok:
        print_success("No staged envctl secrets detected")
        print_kv("scanned_paths", str(len(result.guard_result.scanned_paths)))
        raise typer.Exit(code=0)

    for finding in result.guard_result.findings:
        print_error(f"{finding.path}: {finding.message}")
        for action in finding.actions:
            print_kv("action", action)
    raise typer.Exit(code=result.exit_code)
