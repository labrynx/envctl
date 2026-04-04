from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

import pytest
import typer

import envctl.cli.commands.export.command as export_command_module
from envctl.errors import ExecutionError
from tests.support.callables import unwrap_callable


def test_export_command_default_uses_presenter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(export_command_module, "get_active_profile", lambda: "prod")
    monkeypatch.setattr(export_command_module, "get_selected_group", lambda: "Application")
    monkeypatch.setattr(
        export_command_module,
        "run_export",
        lambda active_profile=None, format="shell", group=None: captured.update({"group": group})
        or (
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
        "group": "Application",
        "profile": "prod",
        "rendered": "export APP_NAME='demo'\n",
    }


def test_export_command_shell_uses_presenter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(export_command_module, "get_active_profile", lambda: "prod")
    monkeypatch.setattr(export_command_module, "get_selected_group", lambda: None)
    monkeypatch.setattr(
        export_command_module,
        "run_export",
        lambda active_profile=None, format="shell", group=None: (
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
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(export_command_module, "get_active_profile", lambda: "prod")
    monkeypatch.setattr(export_command_module, "get_selected_group", lambda: "Application")
    monkeypatch.setattr(
        export_command_module,
        "run_export",
        lambda active_profile=None, format="shell", group=None: captured.update(
            {"active_profile": active_profile, "format": format, "group": group}
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
    assert captured["group"] == "Application"
    assert "presenter_called" not in captured


def test_export_command_rejects_json_mode_after_runtime_checks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    monkeypatch.setattr(export_command_module, "is_json_output", lambda: True)
    monkeypatch.setattr("envctl.cli.decorators.is_json_output", lambda: True)
    monkeypatch.setattr(
        "envctl.cli.decorators.get_command_path",
        lambda: "envctl export",
    )
    monkeypatch.setattr(
        "envctl.cli.decorators.emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    with pytest.raises(typer.Exit) as exc_info:
        export_command_module.export_command()

    assert exc_info.value.exit_code == 1
    payload = cast(dict[str, Any], captured["payload"])
    assert payload == {
        "ok": False,
        "command": "envctl export",
        "error": {
            "type": "ExecutionError",
            "message": "JSON output is not supported for 'export' yet.",
        },
    }


def test_export_command_json_mode_does_not_call_export_service(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(export_command_module, "is_json_output", lambda: True)
    monkeypatch.setattr(
        export_command_module,
        "run_export",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("run_export should not be called")
        ),
    )

    wrapped = cast(
        Callable[[], object],
        unwrap_callable(export_command_module.export_command),
    )

    with pytest.raises(
        ExecutionError,
        match="JSON output is not supported for 'export' yet.",
    ):
        wrapped()
