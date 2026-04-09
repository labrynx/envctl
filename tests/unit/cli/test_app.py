from __future__ import annotations

import pytest
from typer.testing import CliRunner

import envctl.cli.app as app_module
from envctl.domain.runtime import OutputFormat


def test_root_callback_uses_explicit_profile_over_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = CliRunner()
    captured: dict[str, object] = {}

    def fake_load_config() -> object:
        return type("Config", (), {"default_profile": "local"})()

    monkeypatch.setattr(
        app_module,
        "load_config",
        fake_load_config,
    )

    def fake_set_cli_state(
        ctx: object,
        *,
        output_format: OutputFormat,
        profile: str,
        group: str | None = None,
        set_name: str | None = None,
        variable: str | None = None,
    ) -> None:
        captured.update(
            {
                "output_format": output_format,
                "profile": profile,
                "group": group,
                "set_name": set_name,
                "variable": variable,
            }
        )

    monkeypatch.setattr(app_module, "set_cli_state", fake_set_cli_state)

    original_len = len(app_module.app.registered_commands)

    @app_module.app.command("profile-probe")
    def _profile_probe() -> None:
        return None

    try:
        result = runner.invoke(app_module.app, ["--profile", "dev", "profile-probe"])
    finally:
        del app_module.app.registered_commands[original_len:]

    assert result.exit_code == 0
    assert captured["output_format"] == OutputFormat.TEXT
    assert captured["profile"] == "dev"
    assert captured["group"] is None
    assert captured["set_name"] is None
    assert captured["variable"] is None


def test_root_callback_rejects_multiple_scope_selectors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = CliRunner()

    def fake_load_config() -> object:
        return type("Config", (), {"default_profile": "local"})()

    monkeypatch.setattr(
        app_module,
        "load_config",
        fake_load_config,
    )

    original_len = len(app_module.app.registered_commands)

    @app_module.app.command("scope-probe")
    def _scope_probe() -> None:
        return None

    try:
        result = runner.invoke(
            app_module.app,
            ["--group", "Application", "--set", "runtime", "scope-probe"],
        )
    finally:
        del app_module.app.registered_commands[original_len:]

    assert result.exit_code != 0
    assert "mutually exclusive" in result.output
    assert "Next steps" in result.output
    assert "envctl --help" in result.output


def test_root_callback_initializes_observability_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = CliRunner()
    captured: dict[str, str] = {}

    def fake_load_config() -> object:
        return type("Config", (), {"default_profile": "local"})()

    monkeypatch.setattr(app_module, "load_config", fake_load_config)

    def fake_initialize_observability_context(*, command_name: str) -> None:
        captured["command_name"] = command_name

    monkeypatch.setattr(
        app_module,
        "initialize_observability_context",
        fake_initialize_observability_context,
    )

    original_len = len(app_module.app.registered_commands)

    @app_module.app.command("obs-probe")
    def _obs_probe() -> None:
        return None

    try:
        result = runner.invoke(app_module.app, ["obs-probe"])
    finally:
        del app_module.app.registered_commands[original_len:]

    assert result.exit_code == 0
    assert captured["command_name"] == "obs-probe"
