"""Vault command group."""

from __future__ import annotations

from envctl.cli.typer_theme import create_typer_app

vault_app = create_typer_app(
    help_text="Inspect and maintain the local [bold]vault[/bold] artifact.",
    lazy_subcommands={
        "edit": {
            "import_path": "envctl.cli.commands.vault.commands.edit:vault_edit_command",
            "short_help": (
                "Open the local vault file for the selected profile in the configured editor."
            ),
        },
        "check": {
            "import_path": "envctl.cli.commands.vault.commands.check:vault_check_command",
            "short_help": "Check the local vault file as a physical artifact.",
        },
        "path": {
            "import_path": "envctl.cli.commands.vault.commands.path:vault_path_command",
            "short_help": "Print the current vault file path.",
        },
        "show": {
            "import_path": "envctl.cli.commands.vault.commands.show:vault_show_command",
            "short_help": "Show the current vault file contents, masked by default.",
        },
        "prune": {
            "import_path": "envctl.cli.commands.vault.commands.prune:vault_prune_command",
            "short_help": "Remove vault keys that are not declared in the contract.",
        },
        "encrypt": {
            "import_path": "envctl.cli.commands.vault.commands.encrypt:vault_encrypt_command",
            "short_help": "Encrypt plaintext vault files for the current project or all projects.",
        },
        "decrypt": {
            "import_path": "envctl.cli.commands.vault.commands.decrypt:vault_decrypt_command",
            "short_help": "Decrypt encrypted vault files for the current project or all projects.",
        },
        "audit": {
            "import_path": "envctl.cli.commands.vault.commands.audit:vault_audit_command",
            "short_help": (
                "Audit every persisted vault project for plaintext or inconsistent files."
            ),
        },
    },
)
