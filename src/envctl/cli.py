"""CLI entrypoints for envctl."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any

import typer

from envctl.errors import EnvctlError
from envctl.services.config_service import run_config_init
from envctl.services.doctor_service import run_doctor
from envctl.services.init_service import run_init
from envctl.services.remove_service import run_remove
from envctl.services.repair_service import run_repair
from envctl.services.set_service import run_set
from envctl.services.status_service import run_status
from envctl.services.unlink_service import run_unlink
from envctl.utils.output import print_error, print_kv, print_success, print_warning

app = typer.Typer(help="envctl - local environment vault manager")
config_app = typer.Typer(help="Manage envctl configuration.")
app.add_typer(config_app, name="config")


def handle_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    """Wrap CLI commands and convert domain errors into exit code 1."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except EnvctlError as exc:
            print_error(f"Error: {exc}")
            raise typer.Exit(code=1) from exc

    return wrapper


@app.command()
def help(
    command: str | None = typer.Argument(default=None),
) -> None:
    """Show help for envctl or one command."""
    argv = [command, "--help"] if command else ["--help"]
    app(argv, standalone_mode=False)


@app.command()
@handle_errors
def doctor() -> None:
    """Run read-only local environment diagnostics."""
    status_prefix = {
        "ok": "[OK]",
        "warn": "[WARN]",
        "fail": "[FAIL]",
    }

    checks = run_doctor()
    has_failures = False

    for check in checks:
        prefix = status_prefix.get(check.status, "[INFO]")
        typer.echo(f"{prefix} {check.name}: {check.detail}")
        if check.status == "fail":
            has_failures = True

    if has_failures:
        raise typer.Exit(code=1)


@config_app.command("init")
@handle_errors
def config_init() -> None:
    """Create the default envctl config file."""
    config_path = run_config_init()
    print_success("Created envctl config file")
    print_kv("config", str(config_path))


@app.command()
@handle_errors
def init(project: str | None = typer.Argument(default=None)) -> None:
    """Initialize the current Git repository in the vault and link its env file."""
    context = run_init(project_name=project)
    print_success(f"Initialized project '{context.project_slug}'")
    print_kv("project_slug", context.project_slug)
    print_kv("project_id", context.project_id)
    print_kv("repo_root", str(context.repo_root))
    print_kv("metadata", str(context.repo_metadata_path))
    print_kv("vault_dir", str(context.vault_project_dir))
    print_kv("vault_env", str(context.vault_env_path))
    print_kv("repo_env", str(context.repo_env_path))


@app.command()
@handle_errors
def repair(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompts"),
) -> None:
    """Repair the repository env symlink using existing envctl metadata."""
    context = run_repair(force=yes)
    print_success(f"Repaired project '{context.project_slug}'")
    print_kv("project_slug", context.project_slug)
    print_kv("project_id", context.project_id)
    print_kv("repo_env", str(context.repo_env_path))
    print_kv("vault_env", str(context.vault_env_path))


@app.command()
@handle_errors
def unlink() -> None:
    """Remove the repository symlink only."""
    result = run_unlink()

    if result.removed:
        print_success(f"Unlinked repository env file for '{result.context.project_name}'")
    else:
        print_warning(result.message)

    print_kv("repo_env", str(result.context.repo_env_path))
    print_kv("vault_env", str(result.context.vault_env_path))


@app.command()
@handle_errors
def remove(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompts"),
) -> None:
    """Remove envctl management for the current repository."""
    result = run_remove(force=yes)

    print_success(f"Removed envctl management for '{result.context.project_slug}'")
    typer.echo()

    if result.restored_repo_env_file:
        print_success("Restored .env.local in the repository")
    elif result.removed_repo_symlink:
        print_success("Removed repository symlink")

    if result.removed_repo_metadata:
        print_success("Removed repository metadata")

    if result.removed_vault_env:
        print_success("Deleted managed vault env file")

    if result.removed_vault_project_dir:
        print_success("Deleted vault project directory")

    if result.left_regular_repo_env_untouched:
        print_warning("A regular .env.local file was left untouched")

    if result.removed_broken_repo_symlink:
        print_warning("Removed a broken symlink without restoration")


@app.command()
@handle_errors
def status() -> None:
    """Show the current repository envctl status."""
    report = run_status()

    if report.project_slug and report.project_id:
        typer.echo(f"On project {report.project_slug} ({report.project_id})")
        typer.echo()
    elif report.project_slug:
        typer.echo(f"On project {report.project_slug}")
        typer.echo()

    typer.echo(f"Status: {report.state}")
    typer.echo()
    typer.echo(report.summary)
    typer.echo()
    typer.echo(f"Repository env: {report.repo_env_status}")
    typer.echo(f"Vault env: {report.vault_env_status}")

    if report.issues:
        typer.echo()
        typer.echo("Issues:")
        for issue in report.issues:
            typer.echo(f"  - {issue}")

    if report.suggested_action:
        typer.echo()
        typer.echo("Suggested action:")
        typer.echo(f"  {report.suggested_action}")


@app.command()
@handle_errors
def set(
    key: str = typer.Argument(...),
    value: str = typer.Argument(...),
) -> None:
    """Create or update a key in the managed vault env file."""
    context = run_set(key=key, value=value)
    print_success(f"Updated key '{key}' for project '{context.project_name}'")
    print_kv("vault_env", str(context.vault_env_path))
