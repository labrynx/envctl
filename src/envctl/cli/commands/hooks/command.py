"""Managed hooks commands."""

from __future__ import annotations

import typer

from envctl.cli.command_support import build_json_command_payload
from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.presenters import render_hook_operation, render_hooks_status
from envctl.cli.runtime import is_json_output
from envctl.cli.serializers import (
    emit_json,
    serialize_hook_operation_report,
    serialize_hooks_status_report,
)
from envctl.services.context_service import load_project_context
from envctl.services.hook_service import HookService

FORCE_OPTION = typer.Option(
    False,
    "--force",
    help="Overwrite foreign supported hooks in the effective managed hooks path.",
)


@handle_errors
def hooks_status_command() -> None:
    """Show managed hooks status."""
    _config, context = load_project_context()
    report = HookService(context.repo_root).get_status()
    exit_code = 0 if report.is_healthy else 1

    if is_json_output():
        emit_json(
            build_json_command_payload(
                command="hooks status",
                ok=exit_code == 0,
                schema_version=1,
                data=serialize_hooks_status_report(report),
                command_warnings=context.runtime_warnings,
            )
        )
        raise typer.Exit(code=exit_code)

    render_hooks_status(report, repo_root=context.repo_root)
    raise typer.Exit(code=exit_code)


@handle_errors
@requires_writable_runtime("hooks install")
def hooks_install_command(force: bool = FORCE_OPTION) -> None:
    """Install envctl-managed hooks."""
    _config, context = load_project_context()
    report = HookService(context.repo_root).install(force=force)
    exit_code = 0 if report.ok else 1

    if is_json_output():
        emit_json(
            build_json_command_payload(
                command="hooks install",
                ok=exit_code == 0,
                schema_version=1,
                data=serialize_hook_operation_report(report),
                command_warnings=context.runtime_warnings,
            )
        )
        raise typer.Exit(code=exit_code)

    render_hook_operation(report, repo_root=context.repo_root, operation_name="install")
    raise typer.Exit(code=exit_code)


@handle_errors
@requires_writable_runtime("hooks repair")
def hooks_repair_command(force: bool = FORCE_OPTION) -> None:
    """Repair envctl-managed hooks."""
    _config, context = load_project_context()
    report = HookService(context.repo_root).repair(force=force)
    exit_code = 0 if report.ok else 1

    if is_json_output():
        emit_json(
            build_json_command_payload(
                command="hooks repair",
                ok=exit_code == 0,
                schema_version=1,
                data=serialize_hook_operation_report(report),
                command_warnings=context.runtime_warnings,
            )
        )
        raise typer.Exit(code=exit_code)

    render_hook_operation(report, repo_root=context.repo_root, operation_name="repair")
    raise typer.Exit(code=exit_code)


@handle_errors
@requires_writable_runtime("hooks remove")
def hooks_remove_command() -> None:
    """Remove envctl-managed hooks."""
    _config, context = load_project_context()
    report = HookService(context.repo_root).remove()
    exit_code = 0 if report.ok else 1

    if is_json_output():
        emit_json(
            build_json_command_payload(
                command="hooks remove",
                ok=exit_code == 0,
                schema_version=1,
                data=serialize_hook_operation_report(report),
                command_warnings=context.runtime_warnings,
            )
        )
        raise typer.Exit(code=exit_code)

    render_hook_operation(report, repo_root=context.repo_root, operation_name="remove")
    raise typer.Exit(code=exit_code)
