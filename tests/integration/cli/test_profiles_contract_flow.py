from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from envctl.cli.app import app


def test_add_writes_initial_value_to_explicit_profile(
    runner: CliRunner,
    workspace: Path,
) -> None:
    runner.invoke(app, ["config", "init"], catch_exceptions=False)

    result = runner.invoke(
        app,
        ["--profile", "staging", "add", "APP_NAME", "demo-staging"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "profile: staging" in result.stdout
    assert "Added 'APP_NAME' to contract and profile 'staging'" in result.stdout


def test_vault_edit_accepts_profile_override(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "envctl.adapters.editor.open_file",
        lambda path: None,
    )

    result = runner.invoke(
        app,
        ["vault", "edit", "--profile", "dev"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "profile: dev" in result.stdout
