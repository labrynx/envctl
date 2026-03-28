from __future__ import annotations

import pytest
import typer

from envctl.cli.callbacks import typer_prompt, version_callback


def test_version_callback_does_nothing_when_flag_is_false() -> None:
    assert version_callback(False) is None


def test_version_callback_prints_version_and_exits(monkeypatch, capsys) -> None:
    monkeypatch.setattr("envctl.cli.callbacks.__version__", "9.9.9")

    with pytest.raises(typer.Exit):
        version_callback(True)

    captured = capsys.readouterr()
    assert captured.out.strip() == "envctl 9.9.9"


def test_typer_prompt_uses_getpass_for_secret_with_user_value(monkeypatch) -> None:
    monkeypatch.setattr(
        "envctl.cli.callbacks.getpass.getpass",
        lambda message: "super-secret",
    )

    result = typer_prompt("API_KEY", True, None)

    assert result == "super-secret"


def test_typer_prompt_uses_default_for_secret_when_input_is_empty(monkeypatch) -> None:
    monkeypatch.setattr(
        "envctl.cli.callbacks.getpass.getpass",
        lambda message: "",
    )

    result = typer_prompt("API_KEY", True, "fallback")

    assert result == "fallback"


def test_typer_prompt_uses_empty_string_for_secret_when_no_default(monkeypatch) -> None:
    monkeypatch.setattr(
        "envctl.cli.callbacks.getpass.getpass",
        lambda message: "",
    )

    result = typer_prompt("API_KEY", True, None)

    assert result == ""


def test_typer_prompt_uses_typer_prompt_for_non_secret(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_prompt(message, default, show_default):
        captured["message"] = message
        captured["default"] = default
        captured["show_default"] = show_default
        return "3000"

    monkeypatch.setattr("envctl.cli.callbacks.typer.prompt", fake_prompt)

    result = typer_prompt("PORT", False, "3000")

    assert result == "3000"
    assert captured == {
        "message": "PORT [3000]",
        "default": "3000",
        "show_default": False,
    }
