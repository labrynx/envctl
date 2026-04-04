"""Presenters for structured repository detection errors."""

from __future__ import annotations

import typer

from envctl.services.error_diagnostics import (
    ProjectBindingDiagnostics,
    RepositoryDiscoveryDiagnostics,
)


def render_repository_discovery_error(
    diagnostics: RepositoryDiscoveryDiagnostics,
    *,
    message: str,
) -> None:
    """Render a structured repository discovery error to stderr."""
    typer.echo(f"Error: {message}", err=True)

    if (
        diagnostics.repo_root is not None
        or diagnostics.cwd is not None
        or diagnostics.git_args
        or diagnostics.git_stdout is not None
        or diagnostics.git_stderr is not None
    ):
        typer.echo(err=True)

    if diagnostics.repo_root is not None:
        typer.echo(f"repo_root: {diagnostics.repo_root}", err=True)
    if diagnostics.cwd is not None:
        typer.echo(f"cwd: {diagnostics.cwd}", err=True)
    if diagnostics.git_args:
        typer.echo(f"git_args: {' '.join(diagnostics.git_args)}", err=True)
    if diagnostics.git_stdout is not None:
        typer.echo(f"git_stdout: {diagnostics.git_stdout}", err=True)
    if diagnostics.git_stderr is not None:
        typer.echo(f"git_stderr: {diagnostics.git_stderr}", err=True)

    if diagnostics.suggested_actions:
        typer.echo(err=True)
        typer.echo("Next steps", err=True)
        for action in diagnostics.suggested_actions:
            typer.echo(f"  - Run `{action}`", err=True)


def render_project_binding_error(
    diagnostics: ProjectBindingDiagnostics,
    *,
    message: str,
) -> None:
    """Render a structured project binding error to stderr."""
    typer.echo(f"Error: {message}", err=True)
    if diagnostics.repo_root is not None:
        typer.echo(err=True)
        typer.echo(f"repo_root: {diagnostics.repo_root}", err=True)
    if diagnostics.project_id is not None:
        typer.echo(f"project_id: {diagnostics.project_id}", err=True)
    if diagnostics.matching_ids:
        typer.echo(f"matching_ids: {', '.join(diagnostics.matching_ids)}", err=True)
    if diagnostics.matching_directories:
        typer.echo("matching_directories:", err=True)
        for path in diagnostics.matching_directories:
            typer.echo(f"  - {path}", err=True)

    if diagnostics.suggested_actions:
        typer.echo(err=True)
        typer.echo("Next steps", err=True)
        for action in diagnostics.suggested_actions:
            typer.echo(f"  - Run `{action}`", err=True)
