"""Config commands."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors, requires_writable_runtime, text_output_only
from envctl.cli.presenters.action_presenter import render_config_init_result
from envctl.cli.typer_theme import create_typer_app

config_app = create_typer_app(help_text="Manage [bold]envctl[/bold] configuration.")


@config_app.command("init")
@handle_errors
@requires_writable_runtime("config init")
@text_output_only("config init")
def config_init() -> None:
    """Create the default envctl config file."""
    from envctl.services.config_service import run_config_init

    config_path = run_config_init()
    render_config_init_result(config_path)
