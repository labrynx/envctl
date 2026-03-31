"""Presenters for vault commands."""

from __future__ import annotations

from pathlib import Path

import typer

from envctl.utils.output import print_kv, print_success, print_warning


def render_vault_check_result(
    *,
    profile: str,
    path: Path,
    exists: bool,
    parseable: bool,
    private_permissions: bool,
    key_count: int,
) -> None:
    """Render vault check output."""
    if not exists:
        print_warning("Vault file does not exist")
        print_kv("profile", profile)
        print_kv("vault_values", str(path))
        return

    if not parseable:
        print_warning("Vault file is not parseable")
        print_kv("profile", profile)
        print_kv("vault_values", str(path))
        return

    if private_permissions:
        print_success("Vault file looks valid")
    else:
        print_warning("Vault file is parseable but permissions are not private enough")

    print_kv("profile", profile)
    print_kv("vault_values", str(path))
    print_kv("parseable", "yes" if parseable else "no")
    print_kv("private_permissions", "yes" if private_permissions else "no")
    print_kv("keys", str(key_count))


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
) -> None:
    """Render vault values listing."""
    print_kv("profile", profile)
    print_kv("vault_values", str(path))

    typer.echo("Values:")
    for key in sorted(values):
        typer.echo(f"  {key}={values[key]}")
