from __future__ import annotations

from typer.testing import CliRunner

from envctl.cli.app import app


def test_add_usage_error_uses_styled_help_hint() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["add", "API_KEY", "secret", "--required", "--optional"],
    )

    assert result.exit_code == 2
    assert "Error: Use either --required or --optional, not both." in result.output
    assert "Next steps" in result.output
    assert "envctl add --help" in result.output
