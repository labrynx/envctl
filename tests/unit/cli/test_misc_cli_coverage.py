from __future__ import annotations

from importlib.metadata import PackageNotFoundError

import pytest
import typer

import envctl.cli.callbacks as callbacks_module
from envctl.cli.commands.hook.app import hook_app
from envctl.cli.compat.deprecated_commands import build_deprecated_command_warning


def test_version_callback_uses_unknown_when_package_metadata_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def _raise_package_not_found(package: str) -> str:
        raise PackageNotFoundError(package)

    monkeypatch.setattr(callbacks_module, "version", _raise_package_not_found)

    with pytest.raises(typer.Exit):
        callbacks_module.version_callback(True)

    captured = capsys.readouterr()
    assert captured.out.strip() == "envctl unknown"


def test_hook_app_help_exposes_lazy_run_command() -> None:
    context_settings = hook_app.info.context_settings or {}
    lazy_subcommands = context_settings["lazy_subcommands"]

    assert hook_app.info.help == "Run internal envctl-managed [bold]hook[/bold] policies."
    assert lazy_subcommands["run"]["import_path"] == (
        "envctl.cli.commands.hook.commands.run:hook_run_command"
    )
    assert lazy_subcommands["run"]["short_help"] == "Run one managed hook policy."


def test_build_deprecated_command_warning_returns_stable_payload() -> None:
    warning = build_deprecated_command_warning(
        command_name="envctl doctor",
        replacement="envctl profile list",
        removal_version="3.0.0",
    )

    assert warning.kind == "deprecated_command"
    assert "envctl doctor" in warning.message
    assert "envctl profile list" in warning.message
    assert "3.0.0" in warning.message
