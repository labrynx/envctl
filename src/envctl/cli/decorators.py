"""CLI decorators."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any

import typer

from envctl.cli.runtime import get_command_path, is_json_output
from envctl.cli.serializers import emit_json, serialize_error
from envctl.config.loader import load_config
from envctl.domain.runtime import RuntimeMode
from envctl.errors import EnvctlError, ExecutionError
from envctl.utils.output import print_error


def handle_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    """Convert application errors into exit code 1."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except EnvctlError as exc:
            if is_json_output():
                emit_json(
                    serialize_error(
                        error_type=exc.__class__.__name__,
                        message=str(exc),
                        command=get_command_path(),
                    )
                )
            else:
                print_error(f"Error: {exc}")
            raise typer.Exit(code=1) from exc

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
