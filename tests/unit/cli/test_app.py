from __future__ import annotations

import pytest
from typer.testing import CliRunner

import envctl.cli.app as app_module
from envctl.cli.app import app
from envctl.domain.runtime import OutputFormat


def test_root_callback_uses_explicit_profile_over_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = CliRunner()
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        app_module,
        "load_config",
        lambda: type("Config", (), {"default_profile": "local"})(),
    )
    monkeypatch.setattr(
        app_module,
        "set_cli_state",
        lambda ctx, *, output_format, profile: captured.update(
            {
                "output_format": output_format,
                "profile": profile,
            }
        ),
    )

    @app.command("dummy-profile-test")
    def dummy_profile_test() -> None:
        return None

    result = runner.invoke(app, ["--profile", "dev", "dummy-profile-test"])

    assert result.exit_code == 0
    assert captured["output_format"] == OutputFormat.TEXT
    assert captured["profile"] == "dev"
