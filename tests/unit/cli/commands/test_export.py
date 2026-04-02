from __future__ import annotations

import envctl.cli.commands.export.command as export_command_module


def test_export_command_default_uses_presenter(
    monkeypatch,
) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(export_command_module, "get_active_profile", lambda: "prod")
    monkeypatch.setattr(
        export_command_module,
        "run_export",
        lambda active_profile=None, format="shell": (
            "context",
            "prod",
            "export APP_NAME='demo'\n",
        ),
    )
    monkeypatch.setattr(
        export_command_module,
        "render_export_output",
        lambda *, profile, rendered: captured.update({"profile": profile, "rendered": rendered}),
    )

    export_command_module.export_command()

    assert captured == {
        "profile": "prod",
        "rendered": "export APP_NAME='demo'\n",
    }


def test_export_command_shell_uses_presenter(
    monkeypatch,
) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(export_command_module, "get_active_profile", lambda: "prod")
    monkeypatch.setattr(
        export_command_module,
        "run_export",
        lambda active_profile=None, format="shell": (
            "context",
            "prod",
            "export APP_NAME='demo'\n",
        ),
    )
    monkeypatch.setattr(
        export_command_module,
        "render_export_output",
        lambda *, profile, rendered: captured.update({"profile": profile, "rendered": rendered}),
    )

    export_command_module.export_command(format="shell")

    assert captured == {
        "profile": "prod",
        "rendered": "export APP_NAME='demo'\n",
    }


def test_export_command_dotenv_prints_raw_output(
    monkeypatch,
    capsys,
) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(export_command_module, "get_active_profile", lambda: "prod")
    monkeypatch.setattr(
        export_command_module,
        "run_export",
        lambda active_profile=None, format="shell": captured.update(
            {"active_profile": active_profile, "format": format}
        )
        or ("context", "prod", "APP_NAME=demo\n"),
    )
    monkeypatch.setattr(
        export_command_module,
        "render_export_output",
        lambda *, profile, rendered: captured.update({"presenter_called": True}),
    )

    export_command_module.export_command(format="dotenv")

    assert capsys.readouterr().out == "APP_NAME=demo\n"
    assert captured["active_profile"] == "prod"
    assert captured["format"] == "dotenv"
    assert "presenter_called" not in captured
