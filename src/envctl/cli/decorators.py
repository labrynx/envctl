"""CLI decorators."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any

import typer

from envctl.domain.runtime import OutputFormat
from envctl.errors import EnvctlError, ExecutionError
from envctl.utils.output import print_error


def emit_handled_error(
    exc: EnvctlError,
    *,
    output_format: OutputFormat,
    command: str | None,
) -> None:
    """Emit one handled application error in text or JSON mode."""
    from envctl.cli.presenters import present
    from envctl.cli.presenters.outputs.errors import (
        build_config_error_output,
        build_contract_error_output,
        build_error_diagnostics_payload,
        build_error_output,
        build_project_binding_error_output,
        build_projection_validation_failure_output,
        build_repository_discovery_error_output,
        build_state_error_output,
    )
    from envctl.domain.error_diagnostics import (
        ConfigDiagnostics,
        ContractDiagnostics,
        ProjectBindingDiagnostics,
        ProjectionValidationDiagnostics,
        RepositoryDiscoveryDiagnostics,
        StateDiagnostics,
    )

    if output_format == OutputFormat.JSON:
        details = (
            build_error_diagnostics_payload(exc.diagnostics)
            if exc.diagnostics is not None
            else None
        )
        present(
            build_error_output(
                error_type=exc.__class__.__name__,
                message=str(exc),
                command=command,
                details=details,
            ),
            output_format="json",
        )
        return

    diagnostics = exc.diagnostics
    if isinstance(diagnostics, ProjectionValidationDiagnostics):
        present(
            build_projection_validation_failure_output(diagnostics, message=str(exc)),
            output_format="text",
        )
        return
    if isinstance(diagnostics, ContractDiagnostics):
        present(
            build_contract_error_output(diagnostics, message=str(exc)),
            output_format="text",
        )
        return
    if isinstance(diagnostics, ConfigDiagnostics):
        present(
            build_config_error_output(diagnostics, message=str(exc)),
            output_format="text",
        )
        return
    if isinstance(diagnostics, StateDiagnostics):
        present(
            build_state_error_output(diagnostics, message=str(exc)),
            output_format="text",
        )
        return
    if isinstance(diagnostics, RepositoryDiscoveryDiagnostics):
        present(
            build_repository_discovery_error_output(diagnostics, message=str(exc)),
            output_format="text",
        )
        return
    if isinstance(diagnostics, ProjectBindingDiagnostics):
        present(
            build_project_binding_error_output(diagnostics, message=str(exc)),
            output_format="text",
        )
        return

    print_error(f"Error: {exc}")


def emit_usage_error(
    message: str,
    *,
    command: str | None,
) -> None:
    """Emit one styled usage error for text-mode CLI validation failures."""
    from envctl.cli.presenters import present
    from envctl.cli.presenters.common import help_hint_section
    from envctl.cli.presenters.models import CommandOutput, OutputMessage

    present(
        CommandOutput(
            messages=[OutputMessage(level="error", text=message, err=True)],
            sections=[help_hint_section(command, err=True)],
        ),
        output_format="text",
    )


def handle_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    """Convert application errors into exit code 1."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        from envctl.cli.runtime import (
            get_command_path,
            get_profile_observability,
            get_trace_enabled,
            get_trace_file,
            get_trace_format,
            get_trace_output,
            is_error_debug_enabled,
            is_json_output,
        )
        from envctl.observability import (
            get_active_observability_context,
            initialize_observability_context,
        )
        from envctl.observability.error_mapping import map_exception_to_error_event
        from envctl.observability.events import ERROR_HANDLED, ERROR_UNHANDLED
        from envctl.observability.recorder import record_event
        from envctl.observability.renderers import render_profile_summary
        from envctl.observability.timing import observe_span

        command = get_command_path() or "envctl"

        initialize_observability_context(
            command_name=command,
            trace_enabled=get_trace_enabled(),
            trace_format=get_trace_format(),
            trace_output=get_trace_output(),
            trace_file=get_trace_file(),
            profile_observability=get_profile_observability(),
        )

        obs_context = get_active_observability_context()
        span_fields: dict[str, Any] = {"command": command}
        result: Any = None

        try:
            with observe_span(
                "command",
                module=__name__,
                operation="handle_errors",
                fields=span_fields,
            ):
                result = func(*args, **kwargs)
        except typer.Exit:
            raise
        except EnvctlError as exc:
            if obs_context is not None:
                mapping = map_exception_to_error_event(exc)
                event_fields = {
                    "command": command,
                    "error_type": exc.__class__.__name__,
                    "error_kind": mapping.event,
                    "handled": True,
                    "message_safe": mapping.message_safe,
                    "phase": "command",
                    "recoverable": mapping.recoverable,
                }
                span_fields.update(event_fields)
                record_event(
                    obs_context,
                    event=mapping.event,
                    status="error",
                    duration_ms=None,
                    module=__name__,
                    operation="handle_errors",
                    fields=event_fields,
                )
                record_event(
                    obs_context,
                    event=ERROR_HANDLED,
                    status="error",
                    duration_ms=None,
                    module=__name__,
                    operation="emit_handled_error",
                    fields=event_fields,
                )

            emit_handled_error(
                exc,
                output_format=OutputFormat.JSON if is_json_output() else OutputFormat.TEXT,
                command=command,
            )
            raise typer.Exit(code=1) from exc
        except Exception as exc:
            if obs_context is not None:
                mapping = map_exception_to_error_event(exc)
                event_fields = {
                    "command": command,
                    "error_type": exc.__class__.__name__,
                    "error_kind": mapping.event,
                    "handled": False,
                    "message_safe": mapping.message_safe,
                    "phase": "command",
                    "recoverable": mapping.recoverable,
                }
                span_fields.update(event_fields)
                record_event(
                    obs_context,
                    event=mapping.event,
                    status="error",
                    duration_ms=None,
                    module=__name__,
                    operation="handle_errors",
                    fields=event_fields,
                )
                record_event(
                    obs_context,
                    event=ERROR_UNHANDLED,
                    status="error",
                    duration_ms=None,
                    module=__name__,
                    operation="emit_unhandled_error",
                    fields=event_fields,
                )

            if is_error_debug_enabled():
                raise

            if is_json_output():
                from envctl.cli.presenters import present
                from envctl.cli.presenters.outputs.errors import build_error_output

                present(
                    build_error_output(
                        error_type=exc.__class__.__name__,
                        message="Unexpected internal error. Re-run with --debug-errors.",
                        command=command,
                    ),
                    output_format="json",
                )
            else:
                print_error("Error: Unexpected internal error. Re-run with --debug-errors.")

            raise typer.Exit(code=1) from exc
        finally:
            if (
                obs_context is not None
                and obs_context.profile_observability
                and obs_context.events is not None
            ):
                typer.echo(render_profile_summary(obs_context.events), err=True)

        return result

    return wrapper


def text_output_only(command_name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Reject JSON mode for commands that do not support structured output yet."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            from envctl.cli.runtime import is_json_output

            if is_json_output():
                raise ExecutionError(f"JSON output is not supported for '{command_name}' yet.")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def requires_writable_runtime(
    command_name: str,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Block mutating commands in CI read-only mode."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            from envctl.cli.runtime import get_config
            from envctl.domain.runtime import RuntimeMode

            config = get_config()
            if config.runtime_mode == RuntimeMode.CI:
                raise ExecutionError(
                    f"Command '{command_name}' is not available in CI read-only mode."
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator
