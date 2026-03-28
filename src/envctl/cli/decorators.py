"""CLI decorators."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any

import typer

from envctl.errors import EnvctlError
from envctl.utils.output import print_error


def handle_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    """Wrap CLI commands and convert domain errors into exit code 1."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except EnvctlError as exc:
            print_error(f"Error: {exc}")
            raise typer.Exit(code=1) from exc

    return wrapper
