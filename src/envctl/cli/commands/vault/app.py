"""Vault command group."""

from __future__ import annotations

import typer

from envctl.cli.commands.vault.commands import (
    vault_check_command,
    vault_edit_command,
    vault_path_command,
    vault_prune_command,
    vault_show_command,
)

vault_app = typer.Typer(help="Operate on the local vault artifact.")

vault_app.command("edit")(vault_edit_command)
vault_app.command("check")(vault_check_command)
vault_app.command("path")(vault_path_command)
vault_app.command("show")(vault_show_command)
vault_app.command("prune")(vault_prune_command)
