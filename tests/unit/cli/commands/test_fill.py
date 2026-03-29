from __future__ import annotations

from envctl.cli.commands.fill import fill_command
from envctl.domain.operations import FillPlanItem


def test_fill_command_outputs_success_when_keys_are_changed(monkeypatch, capsys) -> None:
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
        "envctl.cli.commands.fill.command.build_fill_plan",
        lambda: (context, plan),
    )
    monkeypatch.setattr(
        "envctl.cli.commands.fill.command.typer_prompt",
        lambda _message, _secret, _default: next(answers),
    )
    monkeypatch.setattr(
        "envctl.cli.commands.fill.command.apply_fill",
        lambda values: (context, ["API_KEY", "PORT"]),
    )

    fill_command()

    output = capsys.readouterr().out
    assert "Filled 2 key(s) for demo-project" in output
    assert "keys: API_KEY, PORT" in output


def test_fill_command_outputs_warning_when_nothing_to_fill(monkeypatch, capsys) -> None:
    context = type("Context", (), {"display_name": "demo-project"})()

    monkeypatch.setattr(
        "envctl.cli.commands.fill.command.build_fill_plan",
        lambda: (context, ()),
    )

    fill_command()

    output = capsys.readouterr().out
    assert "No keys were changed" in output


def test_fill_command_outputs_warning_when_apply_fill_changes_nothing(monkeypatch, capsys) -> None:
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
        "envctl.cli.commands.fill.command.build_fill_plan",
        lambda: (context, plan),
    )
    monkeypatch.setattr(
        "envctl.cli.commands.fill.command.typer_prompt",
        lambda _message, _secret, _default: "   ",
    )
    monkeypatch.setattr(
        "envctl.cli.commands.fill.command.apply_fill",
        lambda values: (context, []),
    )

    fill_command()

    output = capsys.readouterr().out
    assert "No keys were changed" in output
