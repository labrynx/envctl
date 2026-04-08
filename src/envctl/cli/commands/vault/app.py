"""Vault command group."""

from __future__ import annotations

from envctl.cli.commands.vault.commands import (
    vault_audit_command,
    vault_check_command,
    vault_decrypt_command,
    vault_edit_command,
    vault_encrypt_command,
    vault_path_command,
    vault_prune_command,
    vault_show_command,
)
from envctl.cli.typer_theme import create_typer_app

vault_app = create_typer_app(
    help_text="Inspect and maintain the local [bold]vault[/bold] artifact."
)

vault_app.command("edit")(vault_edit_command)
vault_app.command("check")(vault_check_command)
vault_app.command("path")(vault_path_command)
vault_app.command("show")(vault_show_command)
vault_app.command("prune")(vault_prune_command)
vault_app.command("encrypt")(vault_encrypt_command)
vault_app.command("decrypt")(vault_decrypt_command)
vault_app.command("audit")(vault_audit_command)
