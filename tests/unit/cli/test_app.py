from __future__ import annotations

import envctl.cli.app as cli_app


def test_help_command_without_argument_invokes_root_help(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_app(argv, standalone_mode):
        captured["argv"] = argv
        captured["standalone_mode"] = standalone_mode

    monkeypatch.setattr(cli_app, "app", fake_app)

    cli_app.help_command(None)

    assert captured == {
        "argv": ["--help"],
        "standalone_mode": False,
    }


def test_help_command_with_argument_invokes_command_help(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_app(argv, standalone_mode):
        captured["argv"] = argv
        captured["standalone_mode"] = standalone_mode

    monkeypatch.setattr(cli_app, "app", fake_app)

    cli_app.help_command("check")

    assert captured == {
        "argv": ["check", "--help"],
        "standalone_mode": False,
    }
