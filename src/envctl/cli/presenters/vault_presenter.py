"""Presenters for vault commands."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import typer

from envctl.utils.output import print_kv, print_success, print_warning

if TYPE_CHECKING:
    from envctl.domain.operations import VaultAuditProjectResult


def render_vault_check_result(
    *,
    profile: str,
    path: Path,
    exists: bool,
    parseable: bool,
    private_permissions: bool,
    key_count: int,
    state: str,
    detail: str | None = None,
) -> None:
    """Render vault check output."""
    if not exists:
        print_warning("Vault file does not exist")
        print_kv("profile", profile)
        print_kv("vault_values", str(path))
        return

    if state == "plaintext":
        print_warning("Vault file is plaintext")
    elif state == "encrypted":
        print_success("Vault file is encrypted and readable")
    elif state == "wrong_key":
        print_warning("Vault file is encrypted with a different key")
    elif state == "corrupt":
        print_warning("Vault file is corrupted")

    print_kv("profile", profile)
    print_kv("vault_values", str(path))
    print_kv("state", state)
    print_kv("parseable", "yes" if parseable else "no")
    print_kv("private_permissions", "yes" if private_permissions else "no")
    print_kv("keys", str(key_count))
    if detail:
        print_kv("detail", detail)


def render_vault_edit_result(*, profile: str, path: Path, created: bool) -> None:
    """Render vault edit output."""
    if created:
        print_success(f"Created and opened profile '{profile}' vault file")
    else:
        print_success(f"Opened profile '{profile}' vault file")

    print_kv("profile", profile)
    print_kv("vault_values", str(path))


def render_vault_path_result(*, profile: str, path: Path) -> None:
    """Render vault path output."""
    print_kv("profile", profile)
    print_kv("vault_values", str(path))


def render_vault_prune_no_changes(*, profile: str, path: Path) -> None:
    """Render vault prune output when nothing changes."""
    print_kv("profile", profile)
    print_kv("vault_values", str(path))
    print_warning("No unknown keys were removed")


def render_vault_prune_cancelled(*, profile: str, path: Path) -> None:
    """Render vault prune output when user cancels."""
    print_kv("profile", profile)
    print_kv("vault_values", str(path))
    print_warning("No unknown keys were removed")
    print_kv("kept_keys", "unchanged")


def render_vault_prune_result(
    *,
    profile: str,
    path: Path,
    removed_keys: tuple[str, ...],
    kept_keys: int,
) -> None:
    """Render vault prune output."""
    print_kv("profile", profile)
    print_kv("vault_values", str(path))
    print_success(f"Removed {len(removed_keys)} unknown key(s) from profile '{profile}'")
    print_kv("removed_keys", ", ".join(removed_keys))
    print_kv("kept_keys", str(kept_keys))


def render_vault_show_missing(*, profile: str, path: Path) -> None:
    """Render vault show output when file is missing."""
    print_warning("Vault file does not exist")
    print_kv("profile", profile)
    print_kv("vault_values", str(path))


def render_vault_show_empty(*, profile: str, path: Path) -> None:
    """Render vault show output when file is empty."""
    print_kv("profile", profile)
    print_kv("vault_values", str(path))
    print_warning("Vault file is empty")


def render_vault_show_cancelled(*, profile: str, path: Path) -> None:
    """Render vault show output when raw display is cancelled."""
    print_kv("profile", profile)
    print_kv("vault_values", str(path))
    print_warning("Nothing was shown.")


def render_vault_show_values(
    *,
    profile: str,
    path: Path,
    values: dict[str, str],
    state: str,
    detail: str | None = None,
) -> None:
    """Render vault values listing."""
    print_kv("profile", profile)
    print_kv("vault_values", str(path))
    print_kv("state", state)
    if detail:
        print_kv("detail", detail)

    typer.echo("Values:")
    for key in sorted(values):
        typer.echo(f"  {key}={values[key]}")


def render_vault_encrypt_result(result: object) -> None:
    """Render vault encrypt output."""
    from envctl.domain.operations import VaultEncryptResult

    if not isinstance(result, VaultEncryptResult):  # pragma: no cover
        return

    if result.encrypted_files:
        print_success(f"Encrypted {len(result.encrypted_files)} file(s)")
        for path in result.encrypted_files:
            print_kv("encrypted", str(path))
    else:
        print_warning("No plaintext vault files found to encrypt")

    for path in result.skipped_files:
        print_kv("skipped", str(path))


def render_vault_decrypt_result(result: object) -> None:
    """Render vault decrypt output."""
    from envctl.domain.operations import VaultDecryptResult

    if not isinstance(result, VaultDecryptResult):  # pragma: no cover
        return

    if result.decrypted_files:
        print_success(f"Decrypted {len(result.decrypted_files)} file(s)")
        for path in result.decrypted_files:
            print_kv("decrypted", str(path))
    else:
        print_warning("No encrypted vault files found to decrypt")

    for path in result.skipped_files:
        print_kv("skipped", str(path))


def render_vault_audit_result(projects: tuple[VaultAuditProjectResult, ...]) -> None:
    """Render one full vault audit report."""
    if not projects:
        print_warning("No persisted vault projects were found")
        return

    for project in projects:
        typer.echo(f"{project.project_slug} ({project.project_id})")
        print_kv("key_path", str(project.key_path))
        print_kv("key_exists", "yes" if project.key_exists else "no")

        if not project.files:
            print_warning("No vault files found for this project")
            typer.echo("")
            continue

        for item in project.files:
            print_kv("file", str(item.path))
            print_kv("state", item.state)
            print_kv("private_permissions", "yes" if item.private_permissions else "no")
            print_kv("detail", item.detail)

        typer.echo("")
