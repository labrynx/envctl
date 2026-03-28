from __future__ import annotations

from envctl.cli.commands.fill import fill_command


def test_fill_command_outputs_success_when_keys_are_changed(monkeypatch, capsys) -> None:
    context = type("Context", (), {"display_name": "demo-project"})()

    monkeypatch.setattr(
        "envctl.cli.commands.fill.run_fill",
        lambda prompt: (context, ["API_KEY", "PORT"]),
    )

    fill_command()

    captured = capsys.readouterr()
    output = captured.out

    assert "Filled 2 key(s) for demo-project" in output
    assert "keys: API_KEY, PORT" in output


def test_fill_command_outputs_warning_when_nothing_changed(monkeypatch, capsys) -> None:
    context = type("Context", (), {"display_name": "demo-project"})()

    monkeypatch.setattr(
        "envctl.cli.commands.fill.run_fill",
        lambda prompt: (context, []),
    )

    fill_command()

    captured = capsys.readouterr()
    assert "No keys were changed" in captured.out
