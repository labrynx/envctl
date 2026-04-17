"""Config commands."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.presenters import present
from envctl.cli.presenters.outputs.actions import build_config_init_output
from envctl.cli.runtime import is_json_output
from envctl.cli.typer_theme import create_typer_app

config_app = create_typer_app(help_text="Manage [bold]envctl[/bold] configuration.")


@config_app.command("init")
@handle_errors
@requires_writable_runtime("config init")
def config_init() -> None:
    """Create the default envctl config file."""
    from envctl.services.config_service import run_config_init

    config_path = run_config_init()
    present(
        build_config_init_output(config_path),
        output_format="json" if is_json_output() else "text",
    )
