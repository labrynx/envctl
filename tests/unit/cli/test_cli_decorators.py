from __future__ import annotations

import pytest
import typer

from envctl.cli.decorators import handle_errors
from envctl.errors import EnvctlError


def test_handle_errors_returns_wrapped_result() -> None:
    @handle_errors
    def sample(value: int) -> int:
        return value + 1

    assert sample(4) == 5


def test_handle_errors_converts_envctl_error_to_exit(monkeypatch) -> None:
    captured: dict[str, str] = {}

    @handle_errors
    def sample() -> None:
        raise EnvctlError("boom")

    monkeypatch.setattr(
        "envctl.cli.decorators.print_error",
        lambda message: captured.update({"message": message}),
    )

    with pytest.raises(typer.Exit) as exc_info:
        sample()

    assert exc_info.value.exit_code == 1
    assert captured["message"] == "Error: boom"