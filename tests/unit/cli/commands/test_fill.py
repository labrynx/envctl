from __future__ import annotations

from types import SimpleNamespace

import pytest
import typer

import envctl.cli.commands.fill.command as fill_command_module
from envctl.domain.operations import FillPlanItem
from envctl.domain.runtime import RuntimeMode


def test_fill_command_outputs_success_when_keys_are_changed(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    context = type("Context", (), {"display_name": "demo-project"})()
    plan = (
        FillPlanItem(
            key="API_KEY",
            description="API key",
            sensitive=True,
            default_value=None,
        ),
        FillPlanItem(
            key="PORT",
            description="Port number",
            sensitive=False,
            default_value="3000",
        ),
    )

    answers = iter(["secret-value", ""])

    monkeypatch.setattr(
        "envctl.services.fill_service.build_fill_plan",
        lambda profile: (context, "staging", plan),
    )
    monkeypatch.setattr(
        "envctl.cli.commands.fill.command.get_active_profile",
        lambda: "staging",
    )
    monkeypatch.setattr(
        "envctl.cli.commands.fill.command.prompt_secret",
        lambda _message, default=None: next(answers),
    )
    monkeypatch.setattr(
        "envctl.cli.commands.fill.command.prompt_string",
        lambda _message, default=None: next(answers),
    )
    monkeypatch.setattr(
        "envctl.services.fill_service.apply_fill",
        lambda values, profile: (context, "staging", "/tmp/staging.env", ["API_KEY", "PORT"]),
    )

    fill_command_module.fill_command()

    output = capsys.readouterr().out
    assert "Filled 2 key(s) for demo-project" in output
    assert "profile: staging" in output
    assert "keys: API_KEY, PORT" in output


def test_fill_command_outputs_warning_when_nothing_to_fill(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    context = type("Context", (), {"display_name": "demo-project"})()

    monkeypatch.setattr(
        "envctl.services.fill_service.build_fill_plan",
        lambda profile: (context, "local", ()),
    )
    monkeypatch.setattr(
        "envctl.cli.commands.fill.command.get_active_profile",
        lambda: "local",
    )

    fill_command_module.fill_command()

    output = capsys.readouterr().out
    assert "No keys were changed" in output
    assert "profile: local" in output


def test_fill_command_outputs_warning_when_apply_fill_changes_nothing(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    context = type("Context", (), {"display_name": "demo-project"})()
    plan = (
        FillPlanItem(
            key="API_KEY",
            description="API key",
            sensitive=True,
            default_value=None,
        ),
    )

    monkeypatch.setattr(
        "envctl.services.fill_service.build_fill_plan",
        lambda profile: (context, "dev", plan),
    )
    monkeypatch.setattr(
        "envctl.cli.commands.fill.command.get_active_profile",
        lambda: "dev",
    )
    monkeypatch.setattr(
        "envctl.cli.commands.fill.command.prompt_secret",
        lambda _message, default=None: "   ",
    )
    monkeypatch.setattr(
        "envctl.services.fill_service.apply_fill",
        lambda values, profile: (context, "dev", "/tmp/dev.env", []),
    )

    fill_command_module.fill_command()

    output = capsys.readouterr().out
    assert "No keys were changed" in output
    assert "profile: dev" in output


def test_fill_command_rejects_ci_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, str] = {}

    monkeypatch.setattr(
        "envctl.config.loader.load_config",
        lambda: SimpleNamespace(runtime_mode=RuntimeMode.CI),
    )
    monkeypatch.setattr(
        "envctl.cli.runtime.is_json_output",
        lambda: False,
    )
    monkeypatch.setattr(
        "envctl.cli.decorators.print_error",
        lambda message: captured.update({"message": message}),
    )

    with pytest.raises(typer.Exit) as exc_info:
        fill_command_module.fill_command()

    assert exc_info.value.exit_code == 1
    assert "CI read-only mode" in captured["message"]
