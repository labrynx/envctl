"""CLI decorators."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any

import typer

from envctl.cli.presenters import (
    render_config_error,
    render_contract_error,
    render_project_binding_error,
    render_projection_validation_failure,
    render_repository_discovery_error,
    render_state_error,
)
from envctl.cli.presenters.common import print_error_title, print_help_hint
from envctl.cli.runtime import get_command_path, is_json_output
from envctl.cli.serializers import (
    emit_json,
    serialize_error,
    serialize_error_diagnostics,
)
from envctl.config.loader import load_config
from envctl.domain.error_diagnostics import (
    ConfigDiagnostics,
    ContractDiagnostics,
    ProjectBindingDiagnostics,
    ProjectionValidationDiagnostics,
    RepositoryDiscoveryDiagnostics,
    StateDiagnostics,
)
from envctl.domain.runtime import RuntimeMode
from envctl.errors import EnvctlError, ExecutionError
from envctl.observability import get_active_observability_context
from envctl.observability.events import (
    COMMAND_ERROR,
    COMMAND_FINISH,
    COMMAND_START,
    ERROR_HANDLED,
)
from envctl.observability.recorder import duration_ms, record_event
from envctl.observability.timing import utcnow
from envctl.utils.output import print_error


def emit_handled_error(
    exc: EnvctlError,
    *,
    json_output: bool,
    command: str | None,
) -> None:
    """Emit one handled application error in text or JSON mode."""
    if json_output:
        details = (
            serialize_error_diagnostics(exc.diagnostics) if exc.diagnostics is not None else None
        )
        emit_json(
            serialize_error(
                error_type=exc.__class__.__name__,
                message=str(exc),
                command=command,
                details=details,
            )
        )
        return

    diagnostics = exc.diagnostics
    if isinstance(diagnostics, ProjectionValidationDiagnostics):
        render_projection_validation_failure(diagnostics, message=str(exc))
        return
    if isinstance(diagnostics, ContractDiagnostics):
        render_contract_error(diagnostics, message=str(exc))
        return
    if isinstance(diagnostics, ConfigDiagnostics):
        render_config_error(diagnostics, message=str(exc))
        return
    if isinstance(diagnostics, StateDiagnostics):
        render_state_error(diagnostics, message=str(exc))
        return
    if isinstance(diagnostics, RepositoryDiscoveryDiagnostics):
        render_repository_discovery_error(diagnostics, message=str(exc))
        return
    if isinstance(diagnostics, ProjectBindingDiagnostics):
        render_project_binding_error(diagnostics, message=str(exc))
        return

    print_error(f"Error: {exc}")


def emit_usage_error(
    message: str,
    *,
    command: str | None,
) -> None:
    """Emit one styled usage error for text-mode CLI validation failures."""
    print_error_title(message)
    print_help_hint(command, err=True)


def handle_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    """Convert application errors into exit code 1."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        started_at = utcnow()
        obs_context = get_active_observability_context()
        command = get_command_path()
        if obs_context is not None:
            record_event(
                obs_context,
                event=COMMAND_START,
                status="start",
                module=__name__,
                operation="handle_errors",
                fields={"command": command},
            )
        try:
            result = func(*args, **kwargs)
        except EnvctlError as exc:
            if obs_context is not None:
                event_fields = {
                    "command": command,
                    "error_type": exc.__class__.__name__,
                }
                record_event(
                    obs_context,
                    event=COMMAND_ERROR,
                    status="error",
                    duration_ms=duration_ms(started_at),
                    module=__name__,
                    operation="handle_errors",
                    fields=event_fields,
                )
                record_event(
                    obs_context,
                    event=ERROR_HANDLED,
                    status="error",
                    duration_ms=duration_ms(started_at),
                    module=__name__,
                    operation="emit_handled_error",
                    fields=event_fields,
                )
            emit_handled_error(
                exc,
                json_output=is_json_output(),
                command=get_command_path(),
            )
            raise typer.Exit(code=1) from exc
        if obs_context is not None:
            record_event(
                obs_context,
                event=COMMAND_FINISH,
                status="finish",
                duration_ms=duration_ms(started_at),
                module=__name__,
                operation="handle_errors",
                fields={"command": command},
            )
        return result

    return wrapper


def text_output_only(command_name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Reject JSON mode for commands that do not support structured output yet."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
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
            config = load_config()
            if config.runtime_mode == RuntimeMode.CI:
                raise ExecutionError(
                    f"Command '{command_name}' is not available in CI read-only mode."
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator
