from __future__ import annotations

from typer.testing import CliRunner

from envctl.cli.app import app
from envctl.cli.typer_theme import create_typer_app


def test_create_typer_app_applies_shared_cli_defaults() -> None:
    themed = create_typer_app(help_text="Demo help")

    assert getattr(themed.info, "add_completion", False) is False
    assert themed.info.no_args_is_help is True
    assert themed.rich_markup_mode == "rich"
    assert themed.info.context_settings == {"help_option_names": ["-h", "--help"]}


def test_root_help_includes_core_flow_copy() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Core flows" in result.output
    assert "run" in result.output
    assert "sync" in result.output
    assert "export" in result.output
