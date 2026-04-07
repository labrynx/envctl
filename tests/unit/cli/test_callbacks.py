from __future__ import annotations

from typing import Any

import pytest
import typer

import envctl.cli.callbacks as callbacks_module
from envctl.adapters.input import confirm, prompt_secret, prompt_string


def test_version_callback_does_nothing_when_flag_is_false() -> None:
    callbacks_module.version_callback(False)


def test_version_callback_prints_version_and_exits(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr("envctl.cli.callbacks.__version__", "9.9.9")

    with pytest.raises(typer.Exit):
        callbacks_module.version_callback(True)

    captured = capsys.readouterr()
    assert captured.out.strip() == "envctl 9.9.9"


def test_prompt_secret_uses_getpass_for_secret_with_user_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "envctl.adapters.input.getpass.getpass",
        lambda message: "super-secret",
    )

    result = prompt_secret("API_KEY", default=None)

    assert result == "super-secret"


def test_prompt_secret_uses_default_for_secret_when_input_is_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "envctl.adapters.input.getpass.getpass",
        lambda message: "",
    )

    result = prompt_secret("API_KEY", default="fallback")

    assert result == "fallback"


def test_prompt_secret_uses_empty_string_for_secret_when_no_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "envctl.adapters.input.getpass.getpass",
        lambda message: "",
    )

    result = prompt_secret("API_KEY", default=None)

    assert result == ""


def test_prompt_string_uses_typer_prompt_for_non_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_prompt(message: str, default: str, show_default: bool) -> str:
        captured["message"] = message
        captured["default"] = default
        captured["show_default"] = show_default
        return "3000"

    monkeypatch.setattr("envctl.adapters.input.typer.prompt", fake_prompt)

    result = prompt_string("PORT", default="3000")

    assert result == "3000"
    assert captured == {
        "message": "PORT [3000]",
        "default": "3000",
        "show_default": False,
    }


def test_typer_confirm_passes_correct_arguments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_confirm(message: str, default: bool, show_default: bool) -> bool:
        captured["message"] = message
        captured["default"] = default
        captured["show_default"] = show_default
        return True

    monkeypatch.setattr("envctl.cli.callbacks.typer.confirm", fake_confirm)

    result = confirm(message="Are you sure?", default=True)

    assert result is True
    assert captured == {
        "message": "Are you sure?",
        "default": True,
        "show_default": True,
    }
